#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# @Name     : Pixiv.py
# @Date     : 2022/9/2 13:26
# @Auth     : UFOdestiny
# @Desc     : config

import platform


class TelegramAccount:
    api_id = 1234455
    api_hash = 'abcde'

    plat = platform.system().lower()
    if plat == 'windows':
        proxy = dict(scheme="http", hostname="127.0.0.1", port=7890)
    elif plat == 'linux':
        proxy = dict(hostname="127.0.0.1", port=7891)


class PixivAccount:
    token = "abcde"
    proxy = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890', }
    userid = 12345

    json_name = "cache.json"


class LogSetting:
    path = "log"


if __name__ == "__main__":
    print(TelegramAccount.proxy)
