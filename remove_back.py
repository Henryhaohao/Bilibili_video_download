
# -*- coding:utf-8 -*-
import os, sys, shutil, random

endlist = (".flv", ".mp4", ".mkv", ".avi", ".mov")


def run(start_path, result_file):
    path_list = os.listdir(start_path)
    for i in path_list:
        file = os.path.join(start_path, i)
        if os.path.isfile(file):
            if file == os.path.join(result_file, i):
                continue
            elif i.lower().endswith(endlist):
                print(file)
                try:
                    shutil.move(file, result_file)
                except shutil.Error:
                    name = i.rsplit(".")[0]
                    type = i.rsplit(".")[-1]
                    new_name = f"{name}-{random.randint(0, 99)}.{type}"
                    print("rename", new_name)
                    new_file = os.path.join(start_path, new_name)
                    os.rename(file, new_file)
                    shutil.move(new_file, result_file)
        else:
            run(file, result_file)


start_path = r"C:\Users\MOKE\Desktop"
result_file = start_path

run(start_path, result_file)