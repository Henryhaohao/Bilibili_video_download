#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import json
import requests


def BidToAid(Bid):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36'
                      ' (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
    }
    url = "https://api.bilibili.com/x/web-interface/view?bvid=" + Bid
    r = requests.get(url,headers=headers)
    aid = json.loads(r.text)["data"]["aid"]
    return aid

import re

start = "https://www.bilibili.com/video/BV19W411s72F"
res = 'https://api.bilibili.com/x/web-interface/view?bvid=' + re.search(r'/BV(\S+)\?', start).group(1)

print(res)
