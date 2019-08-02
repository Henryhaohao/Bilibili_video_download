# !/usr/bin/python
# -*- coding:utf-8 -*-
# time: 2019/07/21--20:12
__author__ = 'Henry'


'''
项目: B站动漫番剧(bangumi)下载

版本2: 无加密API版,但是需要加入登录后cookie中的SESSDATA字段,才可下载720p及以上视频

API:
1.获取cid的api为 https://api.bilibili.com/x/web-interface/view?aid=47476691 aid后面为av号
2.下载链接api为 https://api.bilibili.com/x/player/playurl?avid=44743619&cid=78328965&qn=32 cid为上面获取到的 avid为输入的av号 qn为视频质量

注意:
但是此接口headers需要加上登录后'Cookie': 'SESSDATA=3c5d20cf%2C1556704080%2C7dcd8c41' (30天的有效期)(因为现在只有登录后才能看到720P以上视频了)
不然下载之后都是最低清晰度,哪怕选择了80也是只有480p的分辨率!!
'''

import requests, time, urllib.request, re
from moviepy.editor import *
import os, sys, threading, json

import imageio
imageio.plugins.ffmpeg.download()

# 访问API地址
def get_play_list(aid, cid, quality):
    url_api = 'https://api.bilibili.com/x/player/playurl?cid={}&avid={}&qn={}'.format(cid, aid, quality)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Cookie': 'SESSDATA=75a75cf2%2C1564669876%2Cb7c7b171', # 登录B站后复制一下cookie中的SESSDATA字段,有效期1个月
        'Host': 'api.bilibili.com'
    }
    html = requests.get(url_api, headers=headers).json()
    # print(html)
    # 当下载会员视频时,如果cookie中传入的不是大会员的SESSDATA时就会返回: {'code': -404, 'message': '啥都木有', 'ttl': 1, 'data': None}
    if html['code'] != 0:
        print('注意!当前集数为B站大会员专享,若想下载,Cookie中请传入大会员的SESSDATA')
        return 'NoVIP'
    video_list = []
    for i in html['data']['durl']:
        video_list.append(i['url'])
    print(video_list)
    return video_list


# 下载视频
'''
 urllib.urlretrieve 的回调函数：
def callbackfunc(blocknum, blocksize, totalsize):
    @blocknum:  已经下载的数据块
    @blocksize: 数据块的大小
    @totalsize: 远程文件的大小
'''


def Schedule_cmd(blocknum, blocksize, totalsize):
    speed = (blocknum * blocksize) / (time.time() - start_time)
    # speed_str = " Speed: %.2f" % speed
    speed_str = " Speed: %s" % format_size(speed)
    recv_size = blocknum * blocksize

    # 设置下载进度条
    f = sys.stdout
    pervent = recv_size / totalsize
    percent_str = "%.2f%%" % (pervent * 100)
    n = round(pervent * 50)
    s = ('#' * n).ljust(50, '-')
    f.write(percent_str.ljust(8, ' ') + '[' + s + ']' + speed_str)
    f.flush()
    # time.sleep(0.1)
    f.write('\r')


def Schedule(blocknum, blocksize, totalsize):
    speed = (blocknum * blocksize) / (time.time() - start_time)
    # speed_str = " Speed: %.2f" % speed
    speed_str = " Speed: %s" % format_size(speed)
    recv_size = blocknum * blocksize

    # 设置下载进度条
    f = sys.stdout
    pervent = recv_size / totalsize
    percent_str = "%.2f%%" % (pervent * 100)
    n = round(pervent * 50)
    s = ('#' * n).ljust(50, '-')
    print(percent_str.ljust(6, ' ') + '-' + speed_str)
    f.flush()
    time.sleep(2)
    # print('\r')


# 字节bytes转化K\M\G
def format_size(bytes):
    try:
        bytes = float(bytes)
        kb = bytes / 1024
    except:
        print("传入的字节格式不对")
        return "Error"
    if kb >= 1024:
        M = kb / 1024
        if M >= 1024:
            G = M / 1024
            return "%.3fG" % (G)
        else:
            return "%.3fM" % (M)
    else:
        return "%.3fK" % (kb)


#  下载视频
def down_video(video_list, title, start_url, page):
    num = 1
    print('[正在下载第{}话视频,请稍等...]:'.format(page) + title)
    currentVideoPath = os.path.join(sys.path[0], 'bilibili_video', title)  # 当前目录作为下载目录
    for i in video_list:
        opener = urllib.request.build_opener()
        # 请求头
        opener.addheaders = [
            # ('Host', 'upos-hz-mirrorks3.acgvideo.com'),  #注意修改host,不用也行
            ('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:56.0) Gecko/20100101 Firefox/56.0'),
            ('Accept', '*/*'),
            ('Accept-Language', 'en-US,en;q=0.5'),
            ('Accept-Encoding', 'gzip, deflate, br'),
            ('Range', 'bytes=0-'),  # Range 的值要为 bytes=0- 才能下载完整视频
            ('Referer', start_url),  # 注意修改referer,必须要加的!
            ('Origin', 'https://www.bilibili.com'),
            ('Connection', 'keep-alive'),

        ]
        urllib.request.install_opener(opener)
        # 创建文件夹存放下载的视频
        if not os.path.exists(currentVideoPath):
            os.makedirs(currentVideoPath)
        # 开始下载
        if len(video_list) > 1:
            urllib.request.urlretrieve(url=i, filename=os.path.join(currentVideoPath, r'{}-{}.flv'.format(title, num)),
                                       reporthook=Schedule_cmd)  # 写成mp4也行  title + '-' + num + '.flv'
        else:
            urllib.request.urlretrieve(url=i, filename=os.path.join(currentVideoPath, r'{}.flv'.format(title)),
                                       reporthook=Schedule_cmd)  # 写成mp4也行  title + '-' + num + '.flv'
        num += 1


# 合并视频(20190802新版)
def combine_video(title_list):
    video_path = os.path.join(sys.path[0], 'bilibili_video')  # 下载目录
    for title in title_list:
        current_video_path = os.path.join(video_path ,title)
        if len(os.listdir(current_video_path)) >= 2:
            # 视频大于一段才要合并
            print('[下载完成,正在合并视频...]:' + title)
            # 定义一个数组
            L = []
            # 遍历所有文件
            for file in sorted(os.listdir(current_video_path), key=lambda x: int(x[x.rindex("-") + 1:x.rindex(".")])):
                # 如果后缀名为 .mp4/.flv
                if os.path.splitext(file)[1] == '.flv':
                    # 拼接成完整路径
                    filePath = os.path.join(current_video_path, file)
                    # 载入视频
                    video = VideoFileClip(filePath)
                    # 添加到数组
                    L.append(video)
            # 拼接视频
            final_clip = concatenate_videoclips(L)
            # 生成目标视频文件
            final_clip.to_videofile(os.path.join(current_video_path, r'{}.mp4'.format(title)), fps=24, remove_temp=False)
            print('[视频合并完成]' + title)
        else:
            # 视频只有一段则直接打印下载完成
            print('[视频合并完成]:' + title)


if __name__ == '__main__':
    start_time = time.time()
    # 用户输入番剧完整链接地址
    # 1. https://www.bilibili.com/bangumi/play/ep267692 (用带ep链接)
    # 2. https://www.bilibili.com/bangumi/play/ss26878  (不要用这个ss链接,epinfo的aid会变成'-1')
    print('*' * 30 + 'B站番剧视频下载小助手' + '*' * 30)
    print('[提示]: 1.如果您想下载720P60,1080p+,1080p60质量的视频,请将35行代码中的SESSDATA改成你登录大会员后得到的SESSDATA,普通用户的SESSDATA最多只能下载1080p的视频')
    print('       2.若发现下载的视频质量在720p以下,请将35行代码中的SESSDATA改成你登录后得到的SESSDATA(有效期一个月),而失效的SESSDATA就只能下载480p的视频')

    start = input('请输入您要下载的B站番剧的完整链接地址(例如:https://www.bilibili.com/bangumi/play/ep267692):')
    ep_url = start
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
    }
    html = requests.get(ep_url,headers=headers).text
    ep_info = re.search(r'INITIAL_STATE__=(.*?"]});', html).group(1)
    # print(ep_info)
    ep_info = json.loads(ep_info)
    # print('您将要下载的番剧名为:' + ep_info['mediaInfo']['title']) # 字段格式太不统一了
    y = input('请输入1或2 - 1.只下载当前一集 2.下载此番剧的全集:')
    # 1.如果只下载当前ep
    id_list = []
    if y == '1':
        try:
            id_list.append([ep_info['epInfo']['aid'], ep_info['epInfo']['cid'],
                            ep_info['epInfo']['titleFormat'] + ' ' + ep_info['epInfo']['longTitle']])
        except:
            id_list.append([ep_info['epInfo']['aid'], ep_info['epInfo']['cid'],
                            '第' + str(ep_info['epInfo']['index']) + '话 ' + ep_info['epInfo']['index_title']])
    # 2.下载此番剧全部ep
    else:
        for i in ep_info['epList']:
            # if i['badge'] == '': # 当badge字段为'会员'时,接口返回404
            try:
                id_list.append([i['aid'], i['cid'],
                                i['titleFormat'] + ' ' + i['longTitle']])
            except:
                id_list.append([i['aid'], i['cid'],'第' + str(i['index']) + '话 ' + i['index_title']])

    # qn参数就是视频清晰度
    # 可选值：
    # 116: 高清1080P60 (需要带入大会员的cookie中的SESSDATA才行,普通用户的SESSDATA最多只能下载1080p的视频,不带入SESSDATA就只能下载480p的)
    # 112: 高清1080P+ (hdflv2) (需要大会员)
    # 80: 高清1080P (flv)
    # 74: 高清720P60 (需要大会员)
    # 64: 高清720P (flv720)
    # 32: 清晰480P (flv480)
    # 16: 流畅360P (flv360)
    print('请输入您要下载视频的清晰度(1080p60:116;1080p+:112;1080p:80;720p60:74;720p:64;480p:32;360p:16; **注意:1080p+,1080p60,720p60都需要带入大会员的cookie中的SESSDATA才行,普通用户的SESSDATA最多只能下载1080p的视频):')
    quality = input('请输入116或112或80或74或64或32或16:')
    threadpool = []
    title_list = []
    page = 1
    print(id_list)
    for item in id_list:
        aid = str(item[0])
        cid = str(item[1])
        title = item[2]
        title = re.sub(r'[\/\\:*?"<>|]', '', title)  # 替换为空的
        print('[下载番剧标题]:' + title)
        title_list.append(title)
        start_url = ep_url
        video_list = get_play_list(aid, cid, quality)
        start_time = time.time()
        # down_video(video_list, title, start_url, page)
        # 定义线程
        if video_list != 'NoVIP':
            th = threading.Thread(target=down_video, args=(video_list, title, start_url, page))
            # 将线程加入线程池
            threadpool.append(th)
        page += 1

    # 开始线程
    for th in threadpool:
        th.start()
    # 等待所有线程运行完毕
    for th in threadpool:
        th.join()
    
    # 最后合并视频
    print(title_list)
    combine_video(title_list)
    
    end_time = time.time()  # 结束时间
    print('下载总耗时%.2f秒,约%.2f分钟' % (end_time - start_time, int(end_time - start_time) / 60))
    # 如果是windows系统，下载完成后打开下载目录
    currentVideoPath = os.path.join(sys.path[0], 'bilibili_video')  # 当前目录作为下载目录
    if (sys.platform.startswith('win')):
        os.startfile(currentVideoPath)


# 番剧视频下载测试: https://www.bilibili.com/bangumi/play/ep269828
