"""
导入依赖库
"""
import os
import sys
import ast
import json
import time
import textwrap
import argparse
import requests
import itertools
import threading
import fake_useragent

"""
脚本信息
"""
NAME = "WebFuzz"
VERSION = "v1.0.0"
GITHUB = "https://github.com/BProbie/WebFuzz"

"""
请求参数
"""
uri = ""
type = ""
data = {}
waf = []
delay = ""
thread = ""

"""
线程安全锁
"""
waf_lock = threading.Lock()

"""
拦截元素集合
"""
wafElement = []

"""
进度条
"""
currentProgress = itertools.count(0)
totalProgress = 0

"""
GET 网络请求
@param uri: 请求网址
@param param: 请求数据
@param data: 请求数据
@return: 请求响应
"""
def get(uri: str, params: dict = None, data: dict = None) -> bytes:
    return requests.get(url = uri, headers = {"User-Agent": fake_useragent.UserAgent().random}, params = params, data = data).content

"""
POST 网络请求
@param uri: 请求网址
@param data: 请求数据
@param param: 请求数据
@return: 请求响应
"""
def post(uri: str, data: dict = None, params: dict = None) -> bytes:
    return requests.post(url = uri, headers = {"User-Agent": fake_useragent.UserAgent().random}, params = params, data = data).content

"""
切割 payload 为元素
@param string payload
@return: 元素集合
"""
def splitElement(string: str) -> list[str]:
    elementList = []
    stringLength = len(string)
    for length in range(1, stringLength + 1):
        for index in range(stringLength - length + 1):
            elementList.append(string[index: index+length])
    return elementList

"""
均分元素集合
@param elementsList: 元素集合
@param count: 均分个数
@return: 均分的元素集合
"""
def splitElements(elementsList: list[str], count: int) -> list[list[str]]:
    size = len(elementsList) // count
    rest = len(elementsList) % count
    return [elementsList[i * size + min(i, rest):(i + 1) * size + min(i + 1, rest)] for i in range(count)]

"""
最小化元素集合中的共有元素(回溯法)
@param elementList: 元素集合
@return: 最小共有元素集合
"""
def minElement(elementList: list[str]) -> list[str]:
    from collections import defaultdict
    str_count = len(elementList)
    substr_cover = defaultdict(set)

    for idx, s in enumerate(elementList):
        n = len(s)
        unique_subst = set()
        for i in range(n):
            for j in range(i + 1, n + 1):
                substr = s[i:j]
                unique_subst.add(substr)
        for substr in unique_subst:
            substr_cover[substr].add(idx)

    best_size = float('inf')
    best_res = []
    all_subst = list(substr_cover.keys())
    all_subst.sort(key=lambda x: (len(x), -len(substr_cover[x])))

    def backtrack(start, current_set, covered_indices):
        nonlocal best_size, best_res
        if len(current_set) > best_size:
            return
        if len(covered_indices) == str_count:
            current_len = len(current_set)
            current_total_length = sum(len(s) for s in current_set)
            best_total_length = sum(len(s) for s in best_res) if best_res else float('inf')
            if current_len < best_size or (current_len == best_size and current_total_length < best_total_length):
                best_size = current_len
                best_res = current_set.copy()
            return
        for i in range(start, len(all_subst)):
            substr = all_subst[i]
            new_covered = substr_cover[substr]
            if new_covered.issubset(covered_indices):
                continue
            current_set.append(substr)
            backtrack(i + 1, current_set, covered_indices.union(new_covered))
            current_set.pop()

    backtrack(0, [], set())
    return best_res

"""
WebFuzz 最小线程任务单元
@param elements 元素集合
"""
def webFuzzTask(elements: list[str]):
    for element in elements:
        copyData = data.copy()
        copyData[next(iter(data.keys()))] = element
        response = get(uri=uri, params=copyData) if type.lower().__contains__("get") else post(uri=uri, data=copyData)

        for w in waf:
            if response.decode().lower().__contains__(w.lower()):
                wafElement.append(element)

        global currentProgress, totalProgress
        cp = next(currentProgress)

        sys.stdout.write(f"\r[{'#' * (int((cp / totalProgress) * 25))}{' ' * (25 - (int((cp / totalProgress) * 25)))}] {cp}/{totalProgress}")
        sys.stdout.flush()

        time.sleep(int(delay))

"""
WebFuzz
"""
def webFuzz():
    elements = splitElement(next(iter(data.values())))
    elementsList = splitElements(elements, int(thread))

    global totalProgress
    totalProgress = len(elements)

    threads = []
    for i in range(int(thread) if int(thread) < totalProgress else totalProgress):
        task = threading.Thread(target=webFuzzTask, args=(elementsList[i],))
        threads.append(task)
        task.start()
    for task in threads:
        task.join()

    sys.stdout.write(f"\r[{'#' * (int((totalProgress / totalProgress) * 25))}{' ' * (25 - (int((totalProgress / totalProgress) * 25)))}] {totalProgress}/{totalProgress} (The Script End At The Time Of {time.strftime("%Y-%m-%d %H:%M:%S")})")
    sys.stdout.flush()

    print()
    time.sleep(0)
    print(f"\nThe Result of WebFuzz: {minElement(wafElement)}")

"""
展示脚本信息
"""
def show():
    print(textwrap.dedent(f"""
    Thanks For Using {NAME}-{VERSION} ({GITHUB})
    Uri: {uri}
    Type: {type}
    Data: {data}
    Waf: {waf}
    Delay: {delay}
    Thread: {thread}
    The Script Start At The Time Of {time.strftime("%Y-%m-%d %H:%M:%S")}
    """))

    time.sleep(0)

"""
主函数
@param args: 命令行参数集合
"""
def main(args):
    global uri, type, data, waf, delay, thread

    while uri is None or uri == "":
        uri = input("Uri: ") if args.uri is None else (
            args.uri
        )

    type = "POST" if args.type is None else (
        str(args.type).upper() if str(args.type).lower().__contains__("post") or str(args.type).lower().__contains__("get") else (
            "POST"
        )
    )

    while data is None or data == {}:
        try:
            data = input("Data: ") if args.data is None else (
                json.loads(args.data)
            )
        except json.decoder.JSONDecodeError:
            data = ast.literal_eval(args.data)

    while waf is None or waf == []:
        waf = input("Waf: ") if args.waf is None else (
            args.waf
        )
        if str(waf).__contains__('[') and str(waf).__contains__(']'):
            try:
                waf = json.loads(waf)
            except json.decoder.JSONDecodeError:
                waf = ast.literal_eval(waf)
        else:
            waf = [waf]

    delay = "0" if args.delay is None else (
        str(int(args.delay)) if int(args.delay) >= 0 else (
            "0"
        )
    )

    thread = "1" if int(delay) > 0 or args.thread is None else (
        "1" if int(args.thread) < 1 else (
            str(os.cpu_count() * 10) if int(args.thread) > os.cpu_count() * 10 else (
                str(int(args.thread))
            )
        )
    )

    show()

    webFuzz()

"""
获取命令行参数集合
@return: 命令行参数集合
"""
def getArgs():
    parser = argparse.ArgumentParser("命令行参数")
    parser.add_argument("-uri", "-u", type=str, required=False, help="请求网址" + " " + "https://www.baidu.com/")
    parser.add_argument("-type", "-tp", type=str, required=False, help="请求类型" + " " + "POST/GET")
    parser.add_argument("-data", "-dt", type=str, required=False, help="请求数据" + " " + "{'key':'value'}")
    parser.add_argument("-waf", "-w", type=str, required=False, help="拦截标志" + " " + "waf")
    parser.add_argument("-delay", "-dl", type=str, required=False, help="间隔秒数" + " " + "0")
    parser.add_argument("-thread", "-tr", type=str, required=False, help="线程数量" + " " + "1")
    return parser.parse_args()

"""
主函数入口
"""
if __name__ == "__main__":
    main(getArgs())

"""

单元测试脚本

python main.py -u http://challenge.imxbt.cn:32542/ -ty POST -dt {'user_input':'{{().__class__.__base__.__subclasses__()}}'} -w ['waf'] -dl 0 -tr 10

main -u http://challenge.imxbt.cn:32542/ -ty POST -dt {'user_input':'{{().__class__.__base__.__subclasses__()}}'} -w ['waf'] -dl 0 -tr 10

webfuzz -u http://challenge.imxbt.cn:32542/ -ty POST -dt {'user_input':'{{().__class__.__base__.__subclasses__()}}'} -w ['waf'] -dl 0 -tr 10

WebFuzz -u http://challenge.imxbt.cn:32542/ -ty POST -dt {'user_input':'{{().__class__.__base__.__subclasses__()}}'} -w ['waf'] -dl 0 -tr 10

"""