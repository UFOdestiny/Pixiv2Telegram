#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# @Name     : pixiv.py
# @Date     : 2022/9/2 10:19
# @Auth     : UFOdestiny
# @Desc     : get pixiv favorite images (latest 90) and send them to telegram favorite.

import json

import time

from pixivpy3 import AppPixivAPI
from pixivpy3.utils import PixivError
from pyrogram import Client
from pyrogram.errors.exceptions.bad_request_400 import WebpageCurlFailed, ExternalUrlInvalid, MediaEmpty

from logger import Logger

from config import TelegramAccount, PixivAccount


class AuthError(Exception):
    def __str__(self):
        return "连接失败"


class Telegram(TelegramAccount):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # self.api_id = TelegramAccount.api_id
        # self.api_hash = TelegramAccount.api_hash
        # self.proxy = TelegramAccount.proxy

        self.app = Client("TG", api_id=self.api_id, api_hash=self.api_hash, proxy=self.proxy)

        self.logger = Logger(file_name="telegram", mode="file")

    async def send_one_picture(self, url, id_=None):
        try:
            await self.app.send_photo("me", url, caption=id_)
        except WebpageCurlFailed:
            self.logger.error(f"{id_} : {url}")
        except ExternalUrlInvalid:
            self.logger.error(f"{id_} : {url}")

    async def pic_pixiv(self, dic):
        async with self.app:
            for t in list(dic.items()):
                id_, urls = t[0], t[1]
                for url in urls:
                    await self.send_one_picture(url, id_)

    def send_pixiv(self, d):
        self.app.run(self.pic_pixiv(d))


class PixivFavorite(PixivAccount):
    def __init__(self):
        # self.token = PixivAccount.token
        # self.proxy = PixivAccount.proxy
        # self.userid = PixivAccount.userid
        # self.json_name = PixivAccount.json_name

        self.api = AppPixivAPI(proxies=self.proxy)
        self.logger = Logger(file_name="pixiv", mode="file")

        self.auth(1)

        self.favorite = None
        self.new = None

    def auth(self, retry=5):
        if retry == 0:
            self.logger.error(AuthError())
            raise AuthError
        else:
            try:
                self.api.auth(refresh_token=self.token)
            except PixivError:
                time.sleep(0)
                self.auth(retry - 1)

    def save_json(self, data, file_name=None):
        if not file_name:
            file_name = self.json_name
        f = open(file_name, "w+", encoding="utf-8")
        if type(data) == list:
            data = {"id": data}
        json.dump(data, f)
        f.close()

    def load_json(self, file_name=None):
        if not file_name:
            file_name = self.json_name
        f = open(file_name, encoding="utf-8")
        data = json.load(f)
        f.close()
        return data["id"]

    def get_favorite_list(self, pages=3):
        res_dic = dict()
        content = [self.api.user_bookmarks_illust(self.userid)]

        for _ in range(pages - 1):
            next_qs = self.api.parse_qs(content[-1].next_url)
            json_result = self.api.user_bookmarks_illust(**next_qs)
            content.append(json_result)

        for page in content:
            for i in page.illusts:
                id_ = i["id"]
                msp = i['meta_single_page']
                if msp != {}:
                    res = [msp["original_image_url"]]
                else:
                    res = [j['image_urls']["original"] for j in i['meta_pages']]
                res_dic[id_] = res

        self.favorite = res_dic

    def check_update(self):
        cache_ids = self.load_json()
        favorite_ids = list(self.favorite.keys())
        self.save_json(favorite_ids)

        new_ids = [i for i in favorite_ids if i not in cache_ids]
        self.new = {k: self.favorite[k] for k in new_ids}

    def send(self, send=True):
        if self.new:
            # print('\r' + f"正在更新{len(self.new)}张收藏到telegram", end='', flush=True)
            if send:
                self.logger.info(f"正在更新{len(self.new)}张收藏到telegram")
                telegram = Telegram()
                telegram.send_pixiv(self.new)
                self.logger.info(f"更新完毕")

        else:
            # print('\r' + "收藏没更新", end='', flush=True)
            self.logger.info("收藏没更新")

    def run(self):
        self.get_favorite_list()
        self.check_update()
        self.send()


if __name__ == '__main__':
    p = PixivFavorite()
    p.run()
    # tg = Telegram()
    # tg.send_pixiv({12314: ["https://i.pximg.net/img-original/img/2022/08/13/08/06/04/100444623_p1.png "]})
