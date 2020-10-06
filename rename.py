#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import json
import os
import shutil
import requests


def getpage(Bid):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
    }

    url = f"https://api.bilibili.com/x/player/pagelist?bvid={Bid}&jsonp=jsonp"
    r = requests.get(url,headers=headers)
    j = json.loads(r.text)
    return j["data"]

rest = getpage("BV1B4411w7vv")
dt = {}
for i in rest:
    page = i["page"]
    part = i["part"]
    name = f"P{page} {part}.flv"
    # print(name)
    dt[part+".flv"] = name

# print(dt)

path = r"C:\Users\MOKE\Desktop\Bilibili_video_download-master\bilibili_video"
for i,_,k in os.walk(path):
    for file in k:
        file_path = os.path.join(i, file)
        # print(file_path)
        # print(file)
        if file in dt:
            new_file = os.path.join(i, dt[file])
            print(new_file)
            os.rename(file_path, new_file)

