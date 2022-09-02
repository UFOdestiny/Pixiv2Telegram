#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# @Name     : pixiv.py
# @Date     : 2022/9/2 13:26
# @Auth     : UFOdestiny
# @Desc     : config

import platform


class TelegramAccount:
    api_id = 18733780
    api_hash = 'dc3607b8cf6585cc6911cda8fc33b6e8'

    plat = platform.system().lower()
    if plat == 'windows':
        proxy = dict(scheme="http", hostname="127.0.0.1", port=7890)
    elif plat == 'linux':
        proxy = dict(hostname="127.0.0.1", port=7891)


class PixivAccount:
    token = "UlXZC7-72tWNIc73Awnk1ir-Glr9MjCy4Q-06NuO_yw"
    proxy = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890', }
    userid = 10344870

    json_name = "cache.json"


class LogSetting:
    path = "log"


if __name__ == "__main__":
    print(TelegramAccount.proxy)
