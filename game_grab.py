# coding:utf-8
# game factory scraper
# env:python 3.6 + lxml
# license:MIT
# author:winxos
# since:2017-02-19
# Notes:changeXuan

import urllib.request
import urllib.error
import itertools
from lxml import etree
import json
from multiprocessing import Pool
from time import clock
from functools import partial

POOLS_SIZE = 20
TRY_TIMES = 100
SINGLE_THREAD_DEBUG = False
# SINGLE_THREAD_DEBUG = True
CONFIG = None
SELFPAGE = 3

# 读取grab_config.json文件中的数据
try:
    with open('grab_config.json', 'r', encoding='utf8') as fg:
        # 使用json格式去加载fg
        # CONFIG是一个json数据
        CONFIG = json.load(fg)
        # print("[debug] config loaded.")
except IOError as e:
    print("[error] %s" % e)
    exit()


# 取得网页的内容(xpath)
def get_content(url, charset):
    global TRY_TIMES
    try:
        # 请求url
        fc = urllib.request.urlopen(url)
        # 请求失败后重新请求的次数
        TRY_TIMES = 100 # todo 用类进行封装
        # 使用utf8编码读取fc网页的内容
        # 使用html接续网页的内容，之后就可以使用xpath来解析了
        # XPath基于XML的树状结构，提供在数据结构树中找寻节点的能力
        return etree.HTML(fc.read().decode(charset))
    except UnicodeDecodeError as ude:
        print("[error] decode error %s" % url)
        print("[debug] info %s" % ude)
    except urllib.error.URLError or TimeoutError:  # 捕捉访问异常，一般为timeout，信息在e中
        # print("[retry %d] %s" % (TRY_TIMES, url))
        # print(traceback.format_exc())
        TRY_TIMES -= 1
        if TRY_TIMES > 0:
            return get_content(url, charset)
        return None

# 解析xpath
def get_items(selector, xpath):
    return selector.xpath(xpath)

# 取得总页数
def get_pages(rule_id):
    # 传入json文件中的 "http://wanga.me/page/"并加上1 所以传入的url为"http://wanga.me/page/1"
    # 第二各参数是json数据中的utf8字符串
    # s是一个可以使用xpath的数据集合
    s = get_content(CONFIG["rules"][rule_id]["games_page_url"] + "1", CONFIG["rules"][rule_id]["charset"])
    if s is None:
        return
    # 第二个参数是"//div[@id="nav-below"]/a[3]/text()"
    # 这是一个xpath的解析路径
    # 在div中寻找id为nav-below的东西
    # 在这个div中的第三个a标签中取得标签内的值：431
    #page_max = int(get_items(s, CONFIG["rules"][rule_id]["games_page_max"])[0])
    page_max = SELFPAGE
    # for循环1～431
    # 返回一个数组，每一项为每一页的地址
    return [CONFIG["rules"][rule_id]["games_page_url"] + str(i) for i in range(1, page_max + 1)]


# 取得每一页的游戏集合
def get_page_games(rule_id, url):
    # 取得url中的xpath
    s = get_content(url, CONFIG["rules"][rule_id]["charset"])
    if s is None:
        return []
    # "//div[@class="game-info"]/a[1]/@href"
    # 取得div中class为game-info的a标签的href内容
    # games_href是一个游戏集合
    games_href = get_items(s, CONFIG["rules"][rule_id]["games_href"])
    return games_href

# 取得游戏的详细信息
def get_game_info(rule_id, url):
    s = get_content(url, CONFIG["rules"][rule_id]["charset"])
    if s is None:
        return
    # 使用xpath解析出name，detail，src(这个是一个swf文件链接，可下载)
    game_name = "".join(get_items(s, CONFIG["rules"][rule_id]["game_name"]))
    game_detail = "".join([x.strip() for x in get_items(s, CONFIG["rules"][rule_id]["game_detail"])])
    game_src = "".join(get_items(s, CONFIG["rules"][rule_id]["game_src"]))
    return game_name, game_detail, url, game_src

# 保存文件
def save_txt(name, data, mode='a'):
    # data为游戏信息map后的字符串
    with open(name, mode, encoding='utf8') as f:
        f.write(data)


# 主函数调用下载
def download(rule_id):
    st = clock()#开始计时
    # 创建一个线程池，大小为20(具体数据在json文件中配置 CONFIG["rules"][rule_id]["pool_size"]为20)
    pool = Pool(processes=int(CONFIG["rules"][rule_id]["pool_size"]))
    print("[debug] downloading game pages list.")
    # 取得游戏页码的地址的数组集合
    page_urls = get_pages(rule_id)
    # 偏函数
    # 因为get_page_games这个函数被放进偏函数中
    # 所以在补齐参数后在调用get_page_games函数
    # 但是id已经压入get_page_games的函数栈中
    func = partial(get_page_games, rule_id)
    game_list = []
    # 返回一个迭代器
    # 就算子线程没有完成，依旧可以使用next来获取下一个
    # 多线程操作，不用等待子线程返回
    # 偏函数添加地址数组，满足参数需求
    pi = pool.imap(func, page_urls)  # iterator for progress
    for i in range(len(page_urls)):
        # 使用next来驱动获取下一个数据
        # 使用迭代器来访问func，和每一个url
        game_list.append(pi.next())
        if i % POOLS_SIZE == 0:
            print("[debug] downloaded pages [%d/%d]" % (i, len(page_urls)))
    # 把多维数组链接成一个长list
    # list中的每个链接为游戏的相信信息
    game_list = list(itertools.chain(*game_list))
    print('[debug] downloaded %d game urls. used:%f s' %
          (len(game_list), clock() - st))
    print('[debug] downloading game details, waiting.')
    # 构建一个get_game_info的偏函数
    func = partial(get_game_info, 0)
    if not SINGLE_THREAD_DEBUG:
        games_info = []
        gi = pool.imap(func, game_list)
        for i in range(len(game_list)):
            games_info.append(gi.next())
            if i % POOLS_SIZE == 0:
                print("[debug] downloading progress %.2f%%" %
                      (i * 100 / len(game_list)))
    else:
        games_info = []
        for gl in game_list[:10]:
            games_info.append(func(gl))
    print('[debug] downloaded %d game details. total used:%f s' %
          (len(games_info), clock() - st))
    # for扫描games_info数组
    # 把内容存入文件夹
    for gi in games_info:
        #print(gi)
        # 每个gi是包含名字等信息的数组
        # map(str,gi)是吧gi的每一个元素转成str，并在每个item面前添加$(第一个元素除外)
        save_txt(str(rule_id) + ".txt", '$'.join(map(str, gi)) + "\n")


'''
usage:
download(index of grab_config_game_lib)
'''
if __name__ == '__main__':
    #testUrl = "http://wanga.me/page/1"
    download(0)
    #print(CONFIG)
    #print(urllib.request.urlopen("http://wanga.me/page/1"))
    pass
