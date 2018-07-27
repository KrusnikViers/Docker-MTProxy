#!/usr/bin/python3

import requests
import shutil


def download_from_core(resource: str):
    url = None
    if resource == 'secret':
        url = 'https://core.telegram.org/getProxySecret/proxy-secret'
    elif resource == 'proxy.conf':
        url = 'https://core.telegram.org/getProxyConfig/proxy-multi.conf'

    working_dir = '/server/objs/bin'
    download_request = requests.get(url, stream=True)
    if download_request.status_code == 200:
        with open(working_dir + '/' + resource, 'wb') as output_file:
            download_request.raw.decode_content = True
            shutil.copyfileobj(download_request.raw, output_file)


# This file might be evaluated as script from cron, in that case we should only update configuration.
if __name__ == "__main__":
    download_from_core('proxy.conf')
