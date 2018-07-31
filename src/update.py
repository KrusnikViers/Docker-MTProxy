#!/usr/bin/env python3

import os
import requests
import shutil

secret_name = 'secret'
servers_conf_name = 'proxy.conf'
server_dir = '/server/'


def download(resource: str):
    url = None
    if resource == secret_name:
        url = 'https://core.telegram.org/getProxySecret/proxy-secret'
    elif resource == servers_conf_name:
        url = 'https://core.telegram.org/getProxyConfig/proxy-multi.conf'

    download_request = requests.get(url, stream=True)
    file_path = server_dir + resource
    if download_request.status_code == 200:
        with open(file_path, 'wb') as output_file:
            download_request.raw.decode_content = True
            shutil.copyfileobj(download_request.raw, output_file)
        print('{} downloaded: {}b'.format(file_path, os.path.getsize(file_path)))
    else:
        print('{} download failed: {}'.format(file_path, download_request.text))


# This file might be evaluated as script from cron, in that case we should only update configuration.
# Also this is a reason, why this code lives in a separate file.
if __name__ == "__main__":
    download(servers_conf_name)
