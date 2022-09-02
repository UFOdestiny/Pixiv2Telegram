#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# @Name     : Pixiv.py
# @Date     : 2022/9/2 10:19
# @Auth     : UFOdestiny
# @Desc     : Telegram

from pyrogram import Client
from pyrogram.errors.exceptions.bad_request_400 import WebpageCurlFailed, ExternalUrlInvalid, MediaEmpty

from config import TelegramAccount
from Logger import Logger


class Telegram(TelegramAccount):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.app = Client("TG", api_id=self.api_id, api_hash=self.api_hash, proxy=self.proxy)
        self.logger = Logger(file_name="telegram", mode="file")

    async def send_one_picture(self, url, id_=None):
        try:
            await self.app.send_photo("me", url, caption=id_)
        except WebpageCurlFailed:
            self.logger.error(f"{id_} : {url}")
        except ExternalUrlInvalid:
            self.logger.error(f"{id_} : {url}")
        except MediaEmpty:
            self.logger.error(f"{id_} : {url}")

    async def pic_pixiv(self, dic):
        async with self.app:
            for t in list(dic.items()):
                id_, urls = t[0], t[1]
                for url in urls:
                    await self.send_one_picture(url, id_)

    def send_pixiv(self, d):
        self.app.run(self.pic_pixiv(d))


if __name__ == '__main__':
    tg = Telegram()
    tg.send_pixiv({12314: ["https://i.pximg.net/img-original/img/2022/08/13/08/06/04/100444623_p1.png "]})
