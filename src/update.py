#!/usr/bin/python3

import os
import requests
import shutil


def download_from_core(resource: str):
    if resource == 'secret':
        url = 'https://core.telegram.org/getProxySecret/proxy-secret'
    elif resource == 'proxy.conf':
        url = 'https://core.telegram.org/getProxyConfig/proxy-multi.conf'
    else:
        assert False

    working_dir = '/server/objs/bin'
    os.makedirs(os.path.dirname(working_dir), exist_ok=True)
    download_request = requests.get(url, stream=True)
    if download_request.status_code == 200:
        with open(working_dir + '/' + resource, 'wb') as output_file:
            download_request.raw.decode_content = True
            shutil.copyfileobj(download_request.raw, output_file)


# This file will be evaluated as script from cron, in that case it should only update configuration.
if __name__ == "__main__":
    download_from_core('proxy.conf')
