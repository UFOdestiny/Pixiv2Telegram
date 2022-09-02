#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# @Name     : Pixiv.py
# @Date     : 2022/9/2 10:19
# @Auth     : UFOdestiny
# @Desc     : get pixiv favorite images (latest 90) and send them to telegram favorite.

import json
import time

from pixivpy3 import AppPixivAPI
from pixivpy3.utils import PixivError

from Telegram import Telegram
from config import PixivAccount
from Logger import Logger


class AuthError(Exception):
    def __str__(self):
        return "连接失败"


class PixivFavorite(PixivAccount):
    def __init__(self):
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
