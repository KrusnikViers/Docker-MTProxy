#!/usr/bin/env python3

import os
import requests
import shutil


def download_from_core(resource: str):
    url = None
    if resource == 'secret':
        url = 'https://core.telegram.org/getProxySecret/proxy-secret'
    elif resource == 'proxy.conf':
        url = 'https://core.telegram.org/getProxyConfig/proxy-multi.conf'

    download_request = requests.get(url, stream=True)
    file_path = '/server/' + resource
    if download_request.status_code == 200:
        with open(file_path, 'wb') as output_file:
            download_request.raw.decode_content = True
            shutil.copyfileobj(download_request.raw, output_file)
        print('{} downloaded: {}b'.format(resource, os.path.getsize(file_path)))
    else:
        print('{} download failed: {}'.format(resource, download_request.text))


# This file might be evaluated as script from cron, in that case we should only update configuration.
if __name__ == "__main__":
    download_from_core('proxy.conf')
