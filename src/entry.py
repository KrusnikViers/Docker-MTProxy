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

secret_path = '/server/secret'
proxy_list_path = '/server/proxy.conf'


def download(path: str, url: str):
    print('Request for {} at {}...'.format(url, datetime.datetime.now()))
    download_request = requests.get(url, stream=True)
    if download_request.status_code == 200:
        with open(path, 'wb') as output_file:
            download_request.raw.decode_content = True
            shutil.copyfileobj(download_request.raw, output_file)
        print('{} downloaded: {}b'.format(path, os.path.getsize(path)))
    else:
        print('{} download failed: {}'.format(path, download_request.text))


# Read configuration, if any.
configuration = {}
configuration_path = '/configuration.json'
if os.path.isfile(configuration_path):
    with open('/configuration.json') as configuration_file:
        configuration = json.load(configuration_file)
else:
    print('Warning! No configuration file has been provided. Server will run with default options.')

# Define proxy server parameters
keys = configuration.get('keys', [])
new_keys = configuration.get('new_keys', 1)
update_hours = configuration.get('update_hours', 12)
ip = configuration.get('ip', None)
url = configuration.get('url', ip)
port = configuration.get('port', 443)
tag = configuration.get('tag', None)

# Generate and print client keys.
for i in range(0, new_keys):
    key_string = binascii.b2a_hex(os.urandom(16)).decode('UTF-8')
    keys.append(key_string)

invite_url = 'tg://proxy?server={}&port={}&secret={}'
print('----- Client Keys Data -----')
if not url:
    print('Warning! No server url or ip has been provided. Invite links will not be generated.')
print('----------------------------')
for key in keys:
    print('Key: {}'.format(key))
    if url:
        print('Invite link: ' + invite_url.format(url, port, key))
    print('----------------------------')

# Download secret token from telegram core.
download(secret_path, 'https://core.telegram.org/getProxySecret/proxy-secret')

# Generate command for mtproxy binary, set system user, stat and proxy ports:
command = '/server/mtproto-proxy -u nobody -p 80 -H 443'
# Client keys:
command += ' ' + ' '.join(['-S {}'.format(key) for key in keys])
# Proxy server tag:
if tag:
    command += ' -T {}'.format(tag)
# NAT information:
if ip:
    # Find local IP with internet access.
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    test_socket.connect(("8.8.8.8", 80))
    local_ip = test_socket.getsockname()[0]
    test_socket.close()
    print('Local IP defined as {}'.format(local_ip))
    if local_ip != ip:
        command += ' --nat-info {}:{}'.format(local_ip, ip)
# Telegram configuration files and workers count:
command += ' --aes-pwd {} {} -M 1'.format(secret_path, proxy_list_path)
print('Launching:\n{}\n\n'.format(command))

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
            print('Running server process for {} seconds...'.format(seconds_to_wait))
            server_process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            server_process.wait(timeout=time_left)
            # If we hit this, process has been terminated earlier than necessary. We should restart waiting cycle.
            print('Early wake up!')
            continue
        except subprocess.TimeoutExpired:
            print('Killing server process for update')
            server_process.kill()
            server_process.wait()
            break
