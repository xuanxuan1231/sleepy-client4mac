#!/usr/bin/python3
# coding:utf-8

"""
一个 python 命令行示例
依赖: requests
by @wyf9
"""

import requests
import json
import config as cf


# 请求重试次数
RETRY = 3


def get(url):
    for t1 in range(RETRY):
        t = t1 + 1
        try:
            x = requests.get(url, proxies={'http': None, 'https': None})
            return x.text
        except:
            print(f'Retrying... {t}/{RETRY}')
            if t >= RETRY:
                print('Max retry limit!')
                raise
            continue


def loadjson(url):
    raw = get(url)
    try:
        return json.loads(raw)
    except json.decoder.JSONDecodeError:
        print('Error decoding json!\nRaw data:\n"""')
        print(raw)
        print('"""')
        raise
    except Exception as e:
        print('Error:', e)
        raise


def main():

    print('\n---\nStatus now:')
    stnow = loadjson(f'{cf.server}/query')
    try:
        print(f'success: [{stnow["success"]}], status: [{stnow["status"]}], info_name: [{stnow["info"]["name"]}],'
              f' info_desc: [{stnow["info"]["desc"]}], info_color: [{stnow["info"]["color"]}]')
    except KeyError:
        print(f'RawData: {stnow}')

    print('\n---\nSelect status:')

    stlst = loadjson(f'{cf.server}/status_list')
    for n in stlst:
        print(f'{n["id"]} - {n["name"]} - {n["desc"]}')

    st = input('\n> ')
    ret = loadjson(f'{cf.server}/set/{cf.secret}/{st}')
    try:
        print(f'success: [{ret["success"]}], code: [{ret["code"]}], set_to: [{ret["set_to"]}]')
    except:
        print(f'RawData: {ret}')
    input('\n---\nPress Enter to exit.')
    return 0


if __name__ == "__main__":
    main()
