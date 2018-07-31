#!/usr/bin/env python3

import binascii
import crontab
import json
import os
import socket
import subprocess

from update import download_from_core


# Read configuration
with open('/configuration.json') as configuration_file:
    configuration = json.load(configuration_file)

    keys = configuration.get('existing_keys', [])
    keys_to_generate = configuration.get('keys_to_generate', 1)
    update_period_hours = configuration.get('update_period_hours', 24)
    server_ip = configuration['server_ip']
    server_port = configuration.get('server_port', 443)
    tag = configuration.get('proxy_tag', '')
    tag = (' -P ' + tag) if tag else ''

# Generate and print client keys.
for i in range(0, keys_to_generate):
    key_string = binascii.b2a_hex(os.urandom(16)).decode('UTF-8')
    keys.append(key_string)

keys_string = ''
template_url = 'tg://proxy?server={}&port={}&secret={{}}'.format(server_ip, server_port)
print('---------------------------')
for key in keys:
    print('Key to be used: {}'.format(key))
    print('Invite link: ' + template_url.format(key))
    print('---------------------------')
    keys_string += ' -S ' + key

# Find out local IP with internet access.
test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
test_socket.connect(("8.8.8.8", 80))
local_ip = test_socket.getsockname()[0]
test_socket.close()

# Download configuration data from telegram core.
download_from_core('secret')
download_from_core('proxy.conf')

# Create cron job, if necessary
cron = crontab.CronTab(user=True)
existing_jobs = list(cron.find_comment('mtp'))
if not existing_jobs:
    job = cron.new(command='python /src/update.py &> /last_log.txt', comment='mtp')
    job.hour.every(update_period_hours)
    cron.write()

# Launch server.
stat_port = 80
secret_file = '/server/secret'
proxy_configuration_file = '/server/proxy.conf'
workers_count = 1

command = '/server/mtproto-proxy -u nobody -p {} -H {} {} {} --nat-info {}:{} --aes-pwd {} {} -M {}'.format(
    stat_port, server_port, keys_string, tag, local_ip, server_ip, secret_file, proxy_configuration_file, workers_count)
print('launching:\n' + command)
subprocess.run(command, shell=True)
