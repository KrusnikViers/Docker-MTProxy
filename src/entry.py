#!/usr/bin/env python3

import binascii
import datetime
import json
import os
import requests
import shutil
import socket
import subprocess
import time


def download(path: str, source_url: str):
    download_request = requests.get(source_url, stream=True)
    if download_request.status_code == 200:
        with open(path, 'wb') as output_file:
            download_request.raw.decode_content = True
            shutil.copyfileobj(download_request.raw, output_file)
        print('Download to {}: {}b'.format(path, os.path.getsize(path)))
    else:
        print('Download to {} failed: {}'.format(path, download_request.text))


# Read configuration, if any.
configuration = {}
configuration_path = '/configuration.json'
if os.path.isfile(configuration_path):
    with open('/configuration.json') as configuration_file:
        configuration = json.load(configuration_file)
else:
    print('Warning! No configuration file has been provided. Server will run with default options')

# Define proxy server parameters.
keys = configuration.get('keys', [])
new_keys = configuration.get('new_keys', 1)
update_hours = configuration.get('update_hours', 12)
ip = configuration.get('ip', None)
url = configuration.get('url', ip)
port = configuration.get('port', 443)
tag = configuration.get('tag', None)

# Base command for mtproxy binary, with system user, stat and proxy ports.
command = '/server/mtproto-proxy -u nobody -p 80 -H 443'
if tag:
    command += ' -T {}'.format(tag)

# Generate and print client keys.
for i in range(0, new_keys):
    keys.append(binascii.b2a_hex(os.urandom(16)).decode('UTF-8'))

# Print client keys with invite keys.
if not url:
    print('Warning! No server url or ip has been provided. Invite links will not be generated.')
for key in keys:
    print('----------------------------')
    print('Key: {}'.format(key))
    if url:
        print('Link: tg://proxy?server={}&port={}&secret={}'.format(url, port, key))
    print('----------------------------')
    command += ' -S ' + key

# Check if server is behind NAT (external ip should be provided).
if ip:
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    test_socket.connect(("8.8.8.8", 80))  # Use Google DNS as remote node.
    local_ip = test_socket.getsockname()[0]
    test_socket.close()
    if local_ip != ip:
        print('Server local and external IP mismatch: {} vs {}'.format(local_ip, ip))
        command += ' --nat-info {}:{}'.format(local_ip, ip)

# Configuration files.
secret_path = '/server/secret'
proxy_list_path = '/server/proxy.conf'
download(secret_path, 'https://core.telegram.org/getProxySecret/proxy-secret')
command += ' --aes-pwd {} {} -M 1'.format(secret_path, proxy_list_path)

seconds_to_wait = update_hours * 3600
server_process = None

# Outer loop: download a proxy servers list, and run the server for |update_hours|.
while True:
    download(proxy_list_path, 'https://core.telegram.org/getProxyConfig/proxy-multi.conf')
    start_time = time.time()

    # Inner loop: running and restarting the server, if it has crashed until the update time.
    while True:
        try:
            time_left = seconds_to_wait - (time.time() - start_time)
            print('Launching at {}:\n{}'.format(datetime.datetime.now(), command))
            print('Server will be interrupted after {} seconds'.format(time_left))
            print('------------------------------------------------------')
            server_process = subprocess.Popen(command.split())
            server_process.wait(timeout=time_left)
            # If we hit this, process has been terminated earlier than necessary. We should restart waiting cycle.
            print('------------------------------------------------------')
            print('Warning! Server exited unexpectedly with code {}'.format(server_process.returncode))
            continue
        except subprocess.TimeoutExpired:
            print('Stopping server process for update')
            server_process.terminate()
            try:
                server_process.wait(timeout=20)
            except subprocess.TimeoutExpired:
                print('Warning! Server termination failed. Attempting to kill')
                server_process.kill()
                server_process.wait()
            print('------------------------------------------------------')
            break
