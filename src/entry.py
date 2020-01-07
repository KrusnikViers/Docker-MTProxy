#!/usr/bin/env python3

import binascii
import datetime
import json
import os
import shutil
import socket
import subprocess
import time

import requests

CONFIGURATION_FILEPATH = '/configuration.json'
PROXY_LIST_FILEPATH = '/server/proxy.conf'
SECRET_FILEPATH = '/server/secret'


def download(path: str, source_url: str) -> bool:
    download_request = requests.get(source_url, stream=True)
    if download_request.status_code == 200:
        with open(path, 'wb') as output_file:
            download_request.raw.decode_content = True
            shutil.copyfileobj(download_request.raw, output_file)
        print('Download to {}: {}b'.format(path, os.path.getsize(path)))
        return True
    else:
        print('Download to {} failed: {}'.format(path, download_request.text))
        return False


def update_remote_configurations(retry_minutes: int) -> bool:
    print('Downloading remote configuration...')
    while True:
        updates_downloaded = False
        try:
            updates_downloaded = \
                download(SECRET_FILEPATH, 'https://core.telegram.org/getProxySecret') and \
                download(PROXY_LIST_FILEPATH, 'https://core.telegram.org/getProxyConfig')
        except Exception as e:
            print('Download failed with an exception: {}'.format(e))

        if updates_downloaded:
            return True

        print('Retrying download in {} minutes.'.format(retry_minutes))
        time.sleep(60 * retry_minutes)


# Read configuration, if any.
try:
    with open(CONFIGURATION_FILEPATH) as configuration_file:
        configuration = json.load(configuration_file)
except FileNotFoundError:
    print("Configuration file was not found. Please, check the documentation on how to mount the file.")
    exit(1)

# Define proxy server parameters.
keys = configuration.get('keys', [])
new_keys = configuration.get('new_keys', 1)
update_hours = configuration.get('update_hours', 12)
ip = configuration.get('ip', '')
url = configuration.get('url', ip)
port = configuration.get('port', 4000)
fake_tls_domain = configuration.get('fake_tls_domain', '')
port_stats = configuration.get('port_stats', 80)
tag = configuration.get('tag', '')

# Base command for mtproxy binary, with system user, stat and proxy ports.
command = '/server/mtproto-proxy -u nobody'
command += ' -H {}'.format(port)
if port_stats:
    print('Serving HTTP stats on {} port. Accessible only via loopback'.format(port_stats))
    command += ' -p {} --http-stats'.format(port_stats)

if tag:
    print('Advertising tag configured: {}'.format(tag))
    command += ' -P {}'.format(tag)

# Add Fake-TLS Domain, if configured.
fake_tls_hex = None
if fake_tls_domain:
    print('Using {} for FakeTLS'.format(fake_tls_domain))
    command += ' -D {}'.format(fake_tls_domain)
    fake_tls_hex = binascii.b2a_hex(fake_tls_domain.encode('UTF-8')).decode('UTF-8')

# If external ip is configured and server is behind the NAT, add NAT information.
if ip:
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    test_socket.connect(("8.8.8.8", 80))  # Use Google DNS as a remote node.
    local_ip = test_socket.getsockname()[0]
    test_socket.close()
    if local_ip != ip:
        print('Configuring server to work behind the NAT: local {} vs global {}'.format(local_ip, ip))
        command += ' --nat-info {}:{}'.format(local_ip, ip)

# Generate and print client keys.
for i in range(0, new_keys):
    keys.append(binascii.b2a_hex(os.urandom(16)).decode('UTF-8'))

# Print client keys with invite keys.
if not url:
    print('No server url or ip has been provided. Invite links will not be generated.')
print('----------')
for key in keys:
    print('Key: {}'.format(key))
    if url:
        if fake_tls_hex:
            print('tg://proxy?server={}&port={}&secret=ee{}{}'.format(url, port, key, fake_tls_hex))
        else:
            print('tg://proxy?server={}&port={}&secret=dd{}'.format(url, port, key))
    print('----------')
    command += ' -S ' + key

# Configuration files.
command += ' --aes-pwd {} {}'.format(SECRET_FILEPATH, PROXY_LIST_FILEPATH)

# Write actual configuration values into local configuration.
configuration['keys'] = keys
configuration['new_keys'] = 0
configuration['update_hours'] = update_hours
configuration['ip'] = ip
configuration['url'] = url
configuration['port_stats'] = port_stats
configuration['port'] = port
configuration['fake_tls_domain'] = fake_tls_domain
configuration['tag'] = tag
with open(CONFIGURATION_FILEPATH, 'w') as configuration_file:
    json.dump(configuration, configuration_file, indent='  ')
print('Configuration file updated: {}b'.format(os.path.getsize(CONFIGURATION_FILEPATH)))

# On first update, we should get configurations as fast, as possible.
update_remote_configurations(retry_minutes=1)

# Outer loop: each iteration updates remote configuration and run server for |update_hours|
while True:
    start_time = time.time()
    # Inner loop: running and restarting the server, if it has crashed until the update time.
    while True:
        try:
            time_left = int(update_hours * 3600 - (time.time() - start_time))
            print('Launching at {}:\n{}'.format(datetime.datetime.now(), command))
            print('Server will be interrupted after {}'.format(datetime.timedelta(seconds=time_left)))
            print('------------------------------------------------------')
            server_process = subprocess.Popen(command.split())
            server_process.wait(timeout=time_left)
            # If we hit this, process has been terminated earlier than necessary. We should restart waiting cycle.
            print('------------------------------------------------------')
            print('Warning! Server exited unexpectedly with code {}'.format(server_process.returncode))
            continue
        except subprocess.TimeoutExpired:
            print('Requesting new configuration')
            update_remote_configurations(retry_minutes=30)
            print('Restarting service process...')
            server_process.terminate()
            try:
                server_process.wait(timeout=20)
            except subprocess.TimeoutExpired:
                print('Warning! Server termination failed. Attempting to kill')
                server_process.kill()
                server_process.wait()
            print('------------------------------------------------------')
            break
