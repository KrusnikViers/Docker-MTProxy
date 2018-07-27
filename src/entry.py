#!/usr/bin/env python3

import binascii
import crontab
import json
import os
import subprocess

from update import download_from_core


# Read configuration
with open('/configuration.json') as configuration_file:
    configuration = json.load(configuration_file)

    keys = configuration.get('existing_keys', [])
    keys_to_generate = configuration.get('keys_to_generate', 1)
    update_period_hours = configuration.get('update_period_hours', 24)
    server_url = configuration['server_url']
    server_port = configuration.get('server_port', 443)
    tag = configuration.get('proxy_tag', None)

# Generate and print client keys.
for i in range(0, keys_to_generate):
    key_string = binascii.b2a_hex(os.urandom(16)).decode('UTF-8')
    keys.append(key_string)

keys_string = ''
template_url = 'tg://proxy?server={}&port={}&secret={{}}'.format(server_url, server_port)
for key in keys:
    print('Key to be used: {}'.format(key))
    print('Usual invite link: ' + template_url.format(key))
    print('Random padding invite link: ' + template_url.format('dd' + key))
    print('---------------------------')
    keys_string += ' -S ' + key

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
command = '/server/mtproto-proxy -u nobody -p 80 -H {} {} {} --aes-pwd /server/secret /server/proxy.conf -M 1'.format(
    server_port, keys_string, tag if tag else '')
print('launching:\n' + command)
subprocess.run(command, shell=True)
