"""
导入依赖库
"""
import os
import sys
import ast
import math
import time
import asyncio
import aiohttp # requirement
import textwrap
import argparse
import itertools
import threading
from yarl import URL # requirement
import fake_useragent # requirement
from collections import defaultdict
from aiohttp import ClientTimeout, ClientError, TCPConnector

"""
脚本信息
"""
NAME = "WebFuzz"
VERSION = "1.2.0"
GITHUB = "https://github.com/BProbie/WebFuzz"

"""
请求参数
"""
uri = ""

fuzz = ""

get = {}
post = {}

userAgent = fake_useragent.UserAgent().random
cookie = {}

waf = []

delay = "0" # [0, 3600]
concurrency = "100" # [1, math.pow(cpu * 10, 2)]

timeout = 60 # [1, 600]
attempts = 10 # [0, 100]

"""
拦截元素集合
"""
wafElementList = []
payloadElementList = []

"""
模糊测试进度条
"""
currentProgress = itertools.count(0)
totalProgress = 0

"""
异步 GET 网络请求
@param uri: 请求网址
@param session: 请求会话对象
@param params: 请求 GET 参数
@param userAgent: 请求 UserAgent 参数
@param cookie: 请求 Cookie 参数
@param timeout: 请求超时时间
@param attempts: 请求重试次数
@return: 请求响应文本
"""
async def async_get(uri: str, params: dict, session: aiohttp.ClientSession, userAgent: str = None, cookie: dict = None, timeout: int = timeout, attempts: int = attempts) -> str:
    for attempt in range(attempts):
        try:
            async with session.get(
                    url=uri,
                    params=params,
                    headers={"User-Agent": dict(session.headers)["User-Agent"] if userAgent is None else userAgent},
                    cookies=session.cookie_jar.filter_cookies(URL(uri)) if cookie is None else cookie,
                    timeout=ClientTimeout(total=timeout)
            ) as response:
                return await response.text()
        except ClientError as clientError:
            if attempt + 1 == attempts:
                print(f"\nError> {clientError}")
    return ""


"""
异步 POST 网络请求
@param uri: 请求网址
@param session: 请求会话对象
@param params: 请求 GET 参数
@param data: 请求 POST 参数
@param userAgent: 请求 UserAgent 参数
@param cookie: 请求 Cookie 参数
@param timeout: 请求超时时间
@param attempts: 请求重试次数
@return: 请求响应文本
"""
async def async_post(uri: str, params: dict, data: dict, session: aiohttp.ClientSession, userAgent: str = None, cookie: dict = None, timeout: int = 60, attempts: int = 10) -> str:
    for attempt in range(attempts):
        try:
            async with session.post(
                    url=uri,
                    params=params,
                    data=data,
                    headers={"User-Agent": dict(session.headers)["User-Agent"] if userAgent is None else userAgent},
                    cookies=session.cookie_jar.filter_cookies(URL(uri)) if cookie is None else cookie,
                    timeout=ClientTimeout(total=timeout)
            ) as response:
                return await response.text()
        except ClientError as clientError:
            if attempt + 1 == attempts:
                print(f"\nError> {clientError}")
    return ""

"""
切割 payload 为元素集合
@param payload 攻击载荷
@return: 元素集合
"""
def turnPayloadToElements(payload: str) -> list[str]:
    elementList = []
    stringLength = len(payload)
    for length in range(1, stringLength + 1):
        for index in range(stringLength - length + 1):
            elementList.append(payload[index: index+length])
    return elementList

"""
均分元素集合
@param element: 元素集合
@param count: 均分个数
@return: 均分的元素集合
"""
def turnElementsToElementsList(elements: list[str], count: int) -> list[list[str]]:
    size = len(elements) // count
    rest = len(elements) % count
    return [elements[i * size + min(i, rest):(i + 1) * size + min(i + 1, rest)] for i in range(count)]

"""
最小化元素集合中的共有元素(回溯法)
@param element: 元素集合
@return: 最小共有元素集合
"""
def turnElementsToMinElements(elements: list[str]) -> list[str]:
    str_count = len(elements)
    if str_count == 0:
        return []

    if str_count == 1:
        s = elements[0]
        return [min(s, key=len)] if s else []

    substr_cover = defaultdict(set)
    for idx, s in enumerate(elements):
        n = len(s)
        seen = set()
        for i in range(n):
            for j in range(i + 1, n + 1):
                substr = s[i:j]
                if substr not in seen:
                    seen.add(substr)
                    substr_cover[substr].add(idx)

    substr_cover = {k: v for k, v in substr_cover.items() if v}

    candidates = sorted(
        substr_cover.items(),
        key=lambda x: (-len(x[1]), len(x[0]))
    )
    filtered = []
    for substr, cover in candidates:
        dominated = False
        for s, c in filtered:
            if cover.issubset(c) and len(s) <= len(substr):
                dominated = True
                break
        if not dominated:
            filtered.append((substr, cover))

    unique_cover = {}
    for substr, cover in filtered:
        cover_frozen = frozenset(cover)
        if cover_frozen not in unique_cover or len(substr) < len(unique_cover[cover_frozen][0]):
            unique_cover[cover_frozen] = (substr, cover)
    candidates = list(unique_cover.values())

    candidates.sort(key=lambda x: (len(x[0]), -len(x[1])))
    substrs = [x[0] for x in candidates]
    covers = [x[1] for x in candidates]
    m = len(candidates)

    if m == 0:
        return elements.copy()

    best_size = float('inf')
    best_res = []
    best_total_len = float('inf')

    max_cover_after = [0] * (m + 1)
    for i in range(m - 1, -1, -1):
        max_cover_after[i] = max(len(covers[i]), max_cover_after[i + 1])

    def backtrack(start, current_set, covered_indices):
        nonlocal best_size, best_res, best_total_len

        current_len = len(current_set)
        remaining = str_count - len(covered_indices)

        if current_len >= best_size:
            return

        if remaining == 0:
            current_total = sum(len(s) for s in current_set)
            if current_len < best_size or (current_len == best_size and current_total < best_total_len):
                best_size = current_len
                best_res = current_set.copy()
                best_total_len = current_total
            return

        if start >= m:
            return

        max_possible_cover = max_cover_after[start]
        if max_possible_cover == 0:
            return

        lower_bound = (remaining + max_possible_cover - 1) // max_possible_cover
        if current_len + lower_bound >= best_size:
            return

        if best_size == 1:
            return

        for i in range(start, m):
            substr = substrs[i]
            cover = covers[i]

            new_covered = cover - covered_indices
            if not new_covered:
                continue

            current_set.append(substr)
            backtrack(i + 1, current_set, covered_indices | new_covered)
            current_set.pop()

    backtrack(0, [], set())

    return best_res if best_res else elements.copy()

"""
异步 WebFuzzAsync 协程
@param fuzz: 模糊测试类型
@param element: 模糊测试元素
@param session: 模糊测试会话
@param semaphore: 模糊测试并发数
"""
async def webFuzzAsync(fuzz: str, element: str, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore):
    async with semaphore:
        try:
            response = ""

            match fuzz.lower():

                case "get":
                    copyGet = get.copy()
                    copyGet[next(iter(copyGet.keys()))] = element
                    response = await async_get(uri=uri,params=copyGet, session=session)

                case "post":
                    copyPost = post.copy()
                    copyPost[next(iter(copyPost.keys()))] = element
                    response = await async_post(uri=uri, params=get, data=copyPost, session=session)

                case "useragent":
                    response = await async_post(uri=uri, params=get, data=post, session=session, userAgent=element)

                case "cookie":
                    copyCookie = cookie.copy()
                    copyCookie[next(iter(copyCookie.keys()))] = element
                    response = await async_post(uri=uri, params=get, data=post, session=session, cookie=copyCookie)

            for w in waf:
                if response.lower().__contains__(str(w).lower()):
                    wafElementList.append(element)

        except Exception:
            pass

        finally:
            global currentProgress, totalProgress
            cp = next(currentProgress)

            sys.stdout.write(f"\r[{'#' * int((cp / totalProgress) * 50)}{' ' * (50 - int((cp / totalProgress) * 50))}] {cp}/{totalProgress}")
            sys.stdout.flush()

            if int(delay) > 0:
                await asyncio.sleep(int(delay))

"""
异步 WebFuzzThread 线程
@param elements: 模糊测试元素集合
"""
async def webFuzzThread(elements: list[str]):
    connector = TCPConnector(
        limit_per_host=int(len(elements) + 0),
        limit=int(len(elements) + 0),
        force_close=False,
        ssl=False
    )
    semaphore = asyncio.Semaphore(int(concurrency))

    async with aiohttp.ClientSession(
            headers={"User-Agent": userAgent},
            cookies=cookie,
            connector=connector
    ) as session:
        tasks = [webFuzzAsync(fuzz, element, session, semaphore) for element in elements]

        await asyncio.gather(*tasks, return_exceptions=True)

"""
WebFuzzTask 任务
@param func: 函数方法
@param args: 参数变量
"""
def webFuzzTask(func, *args):
    try:
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except:
        pass

    try:
        import resource
        resource.setrlimit(resource.RLIMIT_NOFILE, (65535, 65535))
    except:
        pass

    asyncio.run(func(*args))

"""
WebFuzz 主函数
"""
def webFuzz():
    taskCount = int(math.ceil(int(concurrency) / (os.cpu_count() * 10)))
    elementsList = turnElementsToElementsList(payloadElementList, taskCount)

    tasks = []
    for index in range(taskCount):
        task = threading.Thread(target=webFuzzTask, args=(webFuzzThread, elementsList[index]))
        tasks.append(task)
        task.start()
    for task in tasks:
        task.join()

    sys.stdout.write(f"\r[{'#' * 50}] {totalProgress}/{totalProgress}")
    sys.stdout.flush()

    print(textwrap.dedent(f"""
    
    The Script Stop At The Time Of {time.strftime('%Y-%m-%d %H:%M:%S')}
    
    {"=" * 100}
    """))

    time.sleep(0)

    print(f"The Result of WebFuzz: {turnElementsToMinElements(wafElementList)}")

"""
展示信息
"""
def showInformation():
    print(textwrap.dedent(f"""
    {"=" * 100}
    
    Thanks For Using {NAME}-{VERSION} ({GITHUB})
    
    Uri: {uri}
    Fuzz: {fuzz}
    GET: {get}
    POST: {post}
    UserAgent: {userAgent}
    Cookie: {cookie}
    Waf: {waf}
    Delay: {delay}
    Concurrency: {concurrency}
    Timeout: {timeout}
    Attempts: {attempts}
    
    The Script Start At The Time Of {time.strftime("%Y-%m-%d %H:%M:%S")}
    """))

    time.sleep(0)

"""
程序主函数
@param args: 命令行参数集合
"""
def main(args):
    global uri, fuzz, get, post, userAgent, cookie, waf, delay, concurrency, timeout, attempts
    global payloadElementList, totalProgress, wafElementList, currentProgress

    uri = args.uri
    fuzz = args.fuzz
    get = args.get
    post = args.post
    userAgent = args.userAgent
    cookie = args.cookie
    waf = args.waf
    delay = args.delay
    concurrency = args.concurrency
    timeout = args.timeout
    attempts = args.attempts

    wafElementList = []
    payloadElementList = []
    currentProgress = itertools.count(0)
    totalProgress = 0

    match fuzz.lower():

        case "get":
            payloadElementList = turnPayloadToElements(str(list(get.values())[0]))
            totalProgress = len(payloadElementList)

        case "post":
            payloadElementList = turnPayloadToElements(str(list(post.values())[0]))
            totalProgress = len(payloadElementList)

        case "useragent":
            payloadElementList = turnPayloadToElements(userAgent)
            totalProgress = len(payloadElementList)

        case "cookie":
            payloadElementList = turnPayloadToElements(str(list(cookie.values())[0]))
            totalProgress = len(payloadElementList)

    concurrency = str(totalProgress) if int(concurrency) > totalProgress else concurrency

    showInformation()

    webFuzz()

"""
获取命令行参数集合
@return: 命令行参数集合
"""
def getArgs() -> argparse.Namespace:
    parser = argparse.ArgumentParser("命令行参数")

    parser.add_argument("-uri", "-url", "-u", type=str, required=False, help="请求网址" + " " + "https://www.baidu.com/")
    parser.add_argument("-fuzz", "-fz", "-f", type=str, required=False, help="测试类型" + " " + "GET|POST|UserAgent|Cookie")
    parser.add_argument("-get", "-gt", "-g", type=str, required=False, help="GET数据" + " " + "{'key':'value'}")
    parser.add_argument("-post", "-pt", "-p", type=str, required=False, help="POST数据" + " " + "{'key':'value'}")
    parser.add_argument("-userAgent", "-ua", type=str, required=False, help="UserAgent数据" + " " + "UserAgent")
    parser.add_argument("-cookie", "-ck", "-c", type=str, required=False, help="Cookie数据" + " " + "{'key':'value'}")
    parser.add_argument("-waf", "-wf", "-w", type=str, required=False, help="拦截标志" + " " + "waf|['waf']")
    parser.add_argument("-delay", "-dl", "-d", type=str, required=False, help="请求间隔(秒)" + " " + "0")
    parser.add_argument("-concurrency", "-cc", type=str, required=False, help="并发数量(个)" + " " + "100")
    parser.add_argument("-timeout", "-to", "-t", type=str, required=False, help="请求超时(秒)" + " " + "60")
    parser.add_argument("-attempts", "-attempt", "-at", "-a", type=str, required=False, help="请求重试(次)" + " " + "10")

    args = parser.parse_args()

    while args.uri is None or args.uri.strip() == "":
        args.uri = input("Uri = ")

    while args.fuzz is None or not ["get", "post", "useragent", "cookie"].__contains__(str(args.fuzz).lower()):
        args.fuzz = input("Fuzz(GET|POST|UserAgent|Cookie) = ")

    match str(args.fuzz).lower():
        case "get":
            while True:
                try:
                    args.get = ast.literal_eval(str(args.get))
                    if isinstance(args.get, dict) and args.get and str(list(args.get.values())[0]).strip() != "":
                        break
                    raise Exception
                except Exception:
                    args.get = input("GET = ")

        case "post":
            while True:
                try:
                    args.post = ast.literal_eval(str(args.post))
                    if isinstance(args.post, dict) and args.post and str(list(args.post.values())[0]).strip() != "":
                        break
                    raise Exception
                except Exception:
                    args.post = input("POST = ")

        case "useragent":
            while args.userAgent is None or args.userAgent.strip() == "":
                args.userAgent = input("UserAgent = ")

        case "cookie":
            while True:
                try:
                    args.cookie = ast.literal_eval(str(args.cookie))
                    if isinstance(args.cookie, dict) and args.cookie and str(list(args.cookie.values())[0]).strip() != "":
                        break
                    raise Exception
                except Exception:
                    args.cookie = input("Cookie = ")

    global get
    if args.get is not None:
        while True:
            try:
                args.get = ast.literal_eval(str(args.get))
                if isinstance(args.get, dict):
                    break
                raise Exception
            except Exception:
                args.get = input("GET = ")
                # args.get = get
                # break
    else:
        args.get = get

    global post
    if args.post is not None:
        while True:
            try:
                args.post = ast.literal_eval(str(args.post))
                if isinstance(args.post, dict):
                    break
                raise Exception
            except Exception:
                args.post = input("POST = ")
                # args.post = post
                # break
    else:
        args.post = post

    global userAgent
    if args.userAgent is None:
        args.userAgent = userAgent

    global cookie
    if args.cookie is not None:
        while True:
            try:
                args.cookie = ast.literal_eval(str(args.cookie))
                if isinstance(args.cookie, dict):
                    break
                raise Exception
            except Exception:
                args.cookie = input("Cookie = ")
                # args.cookie = cookie
                # break
    else:
        args.cookie = cookie

    while True:
        try:
            if args.waf is not None and str(args.waf).strip() != "":
                try:
                    args.waf = ast.literal_eval(str(args.waf))
                    if isinstance(args.waf, list) and args.waf and str(args.waf[0]).strip() != "":
                        break
                except Exception:
                    args.waf = [args.waf]
                    break
            raise Exception
        except Exception:
            args.waf = input("Waf = ")

    global delay
    while True:
        try:
            args.delay = delay if args.delay is None else (
                "0" if int(args.delay) < 0 else (
                    "3600" if int(args.delay) > 3600 else (
                        str(int(args.delay))
                    )
                )
            )
            break
        except Exception:
            # args.delay = input("Delay = ")
            args.delay = delay
            break

    global concurrency
    while True:
        try:
            args.concurrency = str(1) if int(delay) > 0 else (
                str(1) if int(args.concurrency) < 1 else (
                    str(math.pow(os.cpu_count() * 10, 2)) if int(args.concurrency) > math.pow(os.cpu_count() * 10, 2) else (
                        concurrency if args.concurrency is None else (
                            args.concurrency
                        )
                    )
                )
            )
            break
        except Exception:
            # args.concurrency = input("Concurrency = ")
            args.concurrency = concurrency
            break

    global timeout
    while True:
        try:
            args.timeout = timeout if args.timeout is None else (
                "1" if int(args.timeout) < 1 else (
                    "600" if int(args.timeout) > 600 else (
                        str(int(args.timeout))
                    )
                )
            )
            break
        except Exception:
            # args.timeout = input("Timeout = ")
            args.timeout = timeout
            break

    global attempts
    while True:
        try:
            args.attempts = attempts if args.attempts is None else (
                "0" if int(args.attempts) < 0 else (
                    "100" if int(args.attempts) > 100 else (
                        str(int(args.attempts))
                    )
                )
            )
            break
        except Exception:
            # args.attempts = input("Attempts = ")
            args.attempts = attempts
            break

    return args

"""
程序主函数入口
"""
if __name__ == "__main__":
    main(getArgs())

"""

单元测试脚本

python main.py -u http://challenge.imxbt.cn:31952/ -f POST -g {} -p {'user_input':'{{().__class__.__bases__[0].__subclasses__()}}'} -c {} -w ['waf'] -d 0 -cc 100 -t 60 -a 10

main -u http://challenge.imxbt.cn:31952/ -f POST -g {} -p {'user_input':'{{().__class__.__bases__[0].__subclasses__()}}'} -c {} -w ['waf'] -d 0 -cc 100 -t 60 -a 10

webfuzz -u http://challenge.imxbt.cn:31952/ -f POST -g {} -p {'user_input':'{{().__class__.__bases__[0].__subclasses__()}}'} -c {} -w ['waf'] -d 0 -cc 100 -t 60 -a 10

WebFuzz -u http://challenge.imxbt.cn:31952/ -f POST -g {} -p {'user_input':'{{().__class__.__bases__[0].__subclasses__()}}'} -c {} -w ['waf'] -d 0 -cc 100 -t 60 -a 10

WebFuzz -u http://challenge.imxbt.cn:31952/ -f POST -g {} -p {'user_input':'{{().__class__.__bases__[0].__subclasses__()}}'} -c {} -w ['waf'] -d 0 -cc 100 -t 60 -a 10

"""