#coding=utf-8
from urllib import request
import os
import time
import random
import datetime
from bs4 import BeautifulSoup
import re
import requests
import urllib.request
from lxml import etree



firefoxHead = ''
headersList = [{'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'},
            {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'},
            {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0"}
               ]

IPRegular = r"(([1-9]?\d|1\d{2}|2[0-4]\d|25[0-5]).){3}([1-9]?\d|1\d{2}|2[0-4]\d|25[0-5])"
userCsdn = "博客主URL"


def get_html(url, pageNum, filepwd, num_retries=2):
    print("begin get url")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
    items = []
    for page in range(1, pageNum):
        try:
            time.sleep(5)  # xicidaili 会封杀IP 如果访问过快
            response = request.Request(url=url % page, headers=headers)
            html = request.urlopen(response).read().decode('utf-8')
            soup = BeautifulSoup(html, 'html.parser')
            trs = soup.find_all('tr')
            for i in range(1, len(trs)):
                try:
                    tds = trs[i].find_all("td")
                    tds0, tds6, tds7 = '', '', ''
                    if len(tds) == 10:
                        if tds[0].img: tds0 = tds[0].img["alt"]
                        if tds[6].div: tds6 = tds[6].div["title"]
                        if tds[7].div: tds7 = tds[7].div["title"]
                        item = (tds0, tds[1].get_text(), tds[2].get_text(),
                                tds[3].get_text().strip(), tds[4].get_text(),
                                tds[5].get_text(), tds6, tds7, tds[8].get_text(),
                                tds[9].get_text())
                        items.append(item)
                except TypeError as e:
                    print('get_html_td TypeError:' + e.__str__())
                    continue
            print(url % page)
        except request.URLError as e:
            print('get_html Error:' + e.reason)
            html = None
            if num_retries > 0:
                if hasattr(e, 'code') and 500 <= e.code < 600:
                    # recursively retry 5xx HTTP errors
                    return get_html(url, pageNum, filepwd, num_retries - 1)

        write_excel(items, filepwd)
        items = []
        print("---finish " + page.__str__() + " pages---")


def write_excel(items, filepwd):
    with open(filepwd, 'a+', encoding='utf-8') as fw:
        for item in items:
            fw.write('\t'.join(item) + '\n')


def readIPs(filepwd):
    Ips = []
    with open(filepwd, 'r', encoding='utf-8') as fr:
        src = fr.readlines()
        for line in src[1:]:
            item = line.strip().split('\t')[1]
            Ips.append(item)
    return Ips


def getCodes(pageNum):
    urlList = []
    req_headers = random.choice(headersList)
    resp = requests.get(userCsdn, headers=req_headers)
    if resp.status_code == requests.codes.ok:
        # 构建所有页面的链接
        base_page_link = userCsdn + 'article/list/'
        for i in range(pageNum):
            real_page_link = base_page_link + str(i) + '?'

            # 提取本页所有文章链接
            resp = requests.get(real_page_link, headers=req_headers)
            if resp.status_code == requests.codes.ok:
                html = etree.HTML(resp.text)
                article_links = html.xpath('//div[@class="article-list"]//h4/a/@href')

                # 访问每一篇文章，模拟点击
                for article_link in article_links:
                    urlList.append(article_link)
    print("总共文章数：" + str(len(urlList)))
    return urlList

'''
利用代理IP 实现页面访问
'''
def PV(itemUrl,j):
    s = requests.Session()
    print("开始")
    s.headers = firefoxHead
    for i in range(1):
        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),end='\t')
        print("正在进行第{}次访问\t".format(j), end="\t")
        try:
            s.proxies = {"http": "{}:8080".format(IPs[j])}
            print("IP:" + s.proxies['http'],end='\t')
            r = s.get(itemUrl,timeout=3) # 3秒以内
            print(itemUrl, end='\t')
        except Exception as e:
            print("访问失败", end='\t')
        finally:
            print("访问成功", end='\t')
            time.sleep(random.randint(10,15)) #  访问时间自设定 尽量随机真实些


def getUrls(filename):
    urlList = []
    with open(filename) as fr:
        src = fr.readlines()
        for line in src:
            urlList.append(line.strip())
    return urlList

if __name__ == '__main__':
    while True:
        now = datetime.datetime.now()
        Url = 'http://www.xicidaili.com/nn/%s'
        filepwd = 'IPs'
        Num = 2
        # get_html(Url, Num, filepwd)  # 笔者自己测试 差不多在61次时候会报错
        IPs = readIPs(filepwd)
        print("读取IP池成功")
        '''
        if(now.hour == 23) and (now.minute == 59):

            if os.path.exists(filepwd):
                os.remove(filepwd)

            with open(filepwd, 'a+', encoding='utf-8') as fw:
                head = ['国家', 'IP地址', '端口', '服务器地址', '是否匿名', '类型',
                        '速度', '连接时间', '存活时间', '验证时间']
                headStr = '\t'.join(head) + '\n'
            get_html(Url, Num, filepwd)  # 笔者自己测试 差不多在61次时候会报错
            Ips = readIPs(filepwd)
        '''
        # 接下来 循环执行
        # urlList = getCodes(20)  # 要遍历多少页文章 获取这些页文章的 URL 也可以自己制定想要的文章列表
        urlList = getUrls('urls.txt')
        print("指定URL")
        urlList = ['写具体的URL也可以']
        for j in range(len(IPs)):
            for itemUrl in urlList:
                firefoxHead = random.choice(headersList)
                PV(itemUrl, j)