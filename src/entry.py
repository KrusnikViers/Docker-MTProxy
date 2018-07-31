#!/usr/bin/env python3

import binascii
import crontab
import json
import os
import socket
import subprocess

import update


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

# Download necessary data from telegram core.
update.download(update.secret_name)
update.download(update.servers_conf_name)

# Create cron job, if necessary.
cron = crontab.CronTab(user=True)
existing_jobs = list(cron.find_comment('mtproxy'))
if not existing_jobs:
    job = cron.new(command='python /src/update.py &> /server/last_update_log.txt', comment='mtproxy')
    job.hour.every(update_hours)
    cron.write()
else:
    print('Cron job has already been planned.')
print('Current cron setup:')
for job in cron:
    print(job)

# Generate command for mtproxy binary, set system user, stat and proxy ports:
command = update.server_dir + 'mtproto-proxy -u nobody -p 80 -H 443'
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
command += ' --aes-pwd {} {} -M 1'.format(update.server_dir + update.secret_name,
                                          update.server_dir + update.servers_conf_name)
print('Launching:\n{}\n\n'.format(command))

subprocess.run(command, shell=True)
