#!/bin/python3
"""
network module of scraper library
"""
import os
import requests
import json
import hashlib

import config as config
import common as common

CONFIG = common.read_json(config.CONFIG_FILE)

def __download_with_headers(url, data):
    """
    """
    headers = {}
    output = None
    r = requests.get(url, json=data, headers=headers, verify=False)


    output = r.json()
    url_storage = output["data"]["url"]
    headers = output["data"]["headers"]

    print(output)

    r2 = requests.get(url_storage, headers=headers, verify=False)
    with open(CONFIG["OUTPUT_PDF"], "wb") as binary_file:
        binary_file.write(r2.content)

    return r2.status_code

def __send_get_request(url, data):
    """
    """
    headers = {}
    r = requests.get(url, json=data, headers=headers, verify=False)
    with open(CONFIG["OUTPUT_HTML"], "wb") as binary_file:
        binary_file.write(r.content)

    return r.status_code


def __send_file(url, data, token):
    """
    """
    r, files = None, None

    headers = {'Authorization': 'Bearer {}'.format(token)}
    if 'fpath' in data.keys():
        fpath = data['fpath']
        files = {'file': open(fpath, 'rb')}

    if files is not None:
        r = requests.post(url, headers=headers, files=files, params=data, verify=False)
    else:
        r = requests.post(url, headers=headers, params=data, verify=False)

    return r.status_code

def __send_post_request(url, data, token):
    """
    """
    headers = {'Authorization': 'Bearer {}'.format(token)}
    r = requests.post(url, json=data, headers=headers, verify=False)

    try:
        output = r.json()
        common.write_json(CONFIG["OUTPUT_JSON"], output)
    except:
        with open(CONFIG["ERROR_TXT"], "wb") as binary_file:
            binary_file.write(r.content)
    return r.status_code

def dispatch_request(rtype, url, data, token=None):
    """
    """
    if rtype == 'GET':
        return __send_get_request(url, data)
    if rtype == 'POST':
        return __send_post_request(url, data, token)
    elif rtype == 'DOWNLOAD':
        return __download_with_headers(url, data)
    else:
        return -1
