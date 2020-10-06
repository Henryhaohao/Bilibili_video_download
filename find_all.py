#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import os

path = r"F:\2019go"

lt = []
for i,_,k in os.walk(path):
    for file in k:
        name = file.split(" ", 1)[0].split("P")[1]
        lt.append(int(name))

lt.sort()
# print(lt)
for i in range(153):
    if i not in lt:
        print(i)

