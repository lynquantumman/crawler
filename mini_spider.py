#coding=utf-8
#!/usr/bin/python

# 从html文档中提取出url，经过检验后加入待抓去队列，应该是producer
#       url是否重复
#       url是否符合模式
# 从待抓去队列中get url，然后去抓去,consumer
# -*- coding: utf-8 -*-

import threading
import time
import sys
import urllib.request
import chardet
import html.parser
import urllib.parse
import re

class MyHtmlParser(html.parser.HTMLParser):
    def __init__(self,data):
        html.parser.HTMLParser.__init__(self)
        self.data = data



class Html2url(threading.Thread):
    def __init__(self, name, url_queue, html_queue):
        threading.Thread.__init__(self)
        self.name = name
        self.url_queue = url_queue
        self.html_queue = html_queue

    def run(self):

        html_str, depth = self.html_queue.get()
        if depth<1:
            p = r'"[^"]*html"'
            real_p = re.compile(p)

            for url_str in real_p.findall(html_str):
                print("============="+str(type(url_str)))
                if not url_str.startswith('http'):
                    self.url_queue.put(url_str[2:], depth + 1)
                else:
                    self.url_queue.put(url_str, depth + 1)



class Url2html(threading.Thread):

    def __init__(self, name, url_queue, html_queue):
        threading.Thread.__init__(self)
        self.name = name
        self.url_queue = url_queue
        self.html_queue = html_queue
        self.headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language':'zh-CN,zh;q=0.8',
                        'Connection':'keep-alive',
                        'Upgrade-Insecure-Requests':'1',
                        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0'}
    def run(self):
        # 抓取网页不能太频繁
        # 这里应该有循环
        time.sleep(1)
        url,depth = self.url_queue.get()
        self.headers['host'] = urllib.parse.urlparse(url).netloc
        req = urllib.request.Request(url,headers=self.headers)


        with urllib.request.urlopen(req) as f:
            html_str = f.read().decode('utf-8')
            # lang_info_temp = chardet.detect(f.read())
            # print(lang_info_temp)
            # print(list(f.getheaders()))
        self.html_queue.put((html_str,depth))
        # lang_info = chardet.detect(data)
        # print()
        # lang_info['encoding']
        # print(data.decode('utf-8'))

        with open(r'./'+str(self.headers['host']),'w',encoding='utf-8') as output:
            output.write(html_str)






def main():
    import queue
    url_queue = queue.Queue()
    url_queue.put(('http://www.cma.gov.cn/',0))
    url_queue.put(('http://www.sina.com.cn/',0))
    url_queue.put(('https://www.baidu.com/',0))

    html_queue = queue.Queue()
    html2url = Html2url('xiaomachaoshou', url_queue,html_queue)
    url2html = Url2html('wo', url_queue, html_queue)
    html2url.start()
    url2html.start()





if __name__=='__main__':


    main()

    try:
        sys.exit(0)
    except SystemExit:
        print('The mini_spider has exited gracefully')