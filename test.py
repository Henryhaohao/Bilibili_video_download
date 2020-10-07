#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import requests,json,re

start = "https://www.bilibili.com/video/BV20218473?p=1"

res = re.search(r'/BV(\S+)\?', start).group(1)
print(res)
