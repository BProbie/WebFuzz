# 原创开源脚本



## ⭐基本信息

软件名称：WebFuzz（网安Web应用高并发模糊测试脚本）**（无需字典直接上手）**

软件版本：v1.2.0（稳定版）

开发语言：Python（Python-3.13.0）

开发时间：2026年05月11日 ~ 至今持续更新！

开源地址（Github）：https://github.com/BProbie/WebFuzz/

开源协议（MIT）：https://github.com/BProbie/WebFuzz/raw/refs/heads/master/LICENSE/

下载地址（Github）：https://github.com/BProbie/WebFuzz/releases/tag/1.2.0/

依赖工具：

- pip

依赖技术：

- yarl~=1.23.0

- aiohttp~=3.13.5

- fake-useragent~=2.2.0



## ⭐快速开始

### GIT

#### 克隆项目

```shell
git clone https://github.com/BProbie/WebFuzz.git
```

#### 安装依赖

```shell
cd WebFuzz
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

#### 构建工具

```shell
cd scripts
build
```

#### 运行测试

```shell
cd ..
cd dist
main -u http://www.baidu.com -f POST -p {'key':'value'} -w ['waf']
```



## ⭐简单介绍

**基于payload而非字典**，用于网络空间安全学习以及测试的，Web应用**高并发**模糊测试脚本



## ⭐诞生背景

阳光明媚的一天，一个不知名的网安人正躲在宿舍打CTF，这是一道关于Web-SSTI的题目：So Easy！哎？不对，这是什么，Waf！

坐在电脑前的网安人陷入了沉默：**我拿不到这道题目的源码，那我怎么知道它拦截了哪些字符？**

问问AI吧：Fuzz？Fuzz是什么啊？模糊测试？模糊测试是什么呀？

在对AI追问不舍下我终于下了我人生中第一个Yakit：这怎么用啊？好困难啊！WebFuzz应该是这个吧...哎？怎么还要字典啊？**字典在哪弄啊？字典又大又重不仅会污染我的存储空间导入还好慢呀！**

怎么办？怎么办！坐在电脑前的网安人再一次陷入了沉思...

于是，WebFuzz（网安Web应用模糊测试脚本），诞生了！



## ⭐核心场景

利用**payload**对Web应用进行**高并发**模糊测试，进而获得其**WAF**



## ⭐使用教程

### 帮助文档

```shell
WebFuzz -h
```

```shell
usage: 命令行参数 [-h] [-uri URI] [-fuzz FUZZ] [-get GET] [-post POST] [-userAgent USERAGENT] [-cookie COOKIE] [-waf WAF]
             [-delay DELAY] [-concurrency CONCURRENCY] [-timeout TIMEOUT] [-attempts ATTEMPTS]

options:
  -h, --help            show this help message and exit
  -uri, -url, -u URI    请求网址 https://www.baidu.com/
  -fuzz, -fz, -f FUZZ   测试类型 GET|POST|UserAgent|Cookie
  -get, -gt, -g GET     GET数据 {'key':'value'}
  -post, -pt, -p POST   POST数据 {'key':'value'}
  -userAgent, -ua USERAGENT
                        UserAgent数据 UserAgent
  -cookie, -ck, -c COOKIE
                        Cookie数据 {'key':'value'}
  -waf, -wf, -w WAF     拦截标志 waf|['waf']
  -delay, -dl, -d DELAY
                        请求间隔(秒) 0
  -concurrency, -cc CONCURRENCY
                        并发数量(个) 100
  -timeout, -to, -t TIMEOUT
                        请求超时(秒) 60
  -attempts, -attempt, -at, -a ATTEMPTS
                        请求重试(次) 10
```

|     名称      |     参数     | 简化 |         作用          |             规范             |   必要   | 默认 |               备注                |
| :-----------: | :----------: | :--: | :-------------------: | :--------------------------: | :------: | :--: | :-------------------------------: |
|   查看帮助    |    -help     |  -h  |       查看帮助        |              /               |    /     |  /   |                 /                 |
|   请求网址    |     -uri     |  -u  |     设置请求网址      |    https://www.baidu.com     |    是    |  /   |                 /                 |
|   测试类型    |    -fuzz     |  -f  |     设置测试类型      | GET\|POST\|UserAgent\|Cookie |    是    |  /   |                 /                 |
|    GET数据    |     -get     |  -g  |    设置GET请求参数    |       {'key':'value'}        | 依据Fuzz |  {}  |    默认以第一对键值为Fuzz对象     |
|   POST数据    |    -post     |  -p  |   设置POST请求参数    |       {'key':'value'}        | 依据Fuzz |  {}  |    默认以第一对键值为Fuzz对象     |
| UserAgent数据 |  -userAgent  | -ua  | 设置UserAgent请求参数 |          UserAgent           | 依据Fuzz | 随机 |                 /                 |
|  Cookie数据   |   -cookie    |  -c  |  设置Cookie请求参数   |       {'key':'value'}        | 依据Fuzz |  {}  |    默认以第一对键值为Fuzz对象     |
|   拦截标志    |     -waf     |  -w  |     设置拦截标志      |         waf\|['waf']         |    是    |  /   | ['waf','block']两个标志是或的关系 |
|   请求间隔    |    -delay    |  -d  |   设置请求间隔(秒)    |              0               |    否    |  0   |  当delay>=1时concurrency固定为1   |
|   并发数量    | -concurrency | -cc  |   设置请求间隔(个)    |             100              |    否    | 100  |      范围在[1,(CPU核数*10)²]      |
|   请求超时    |   -timeout   |  -t  | 设置请求超时限制(秒)  |              60              |    否    |  60  |                 /                 |
|   请求重试    |  -attempts   |  -a  | 设置请求重试次数(次)  |              10              |    否    |  10  |                 /                 |

### 使用示例

#### 通用示例

```shell
WebFuzz -u http://challenge.imxbt.cn:31952/ -f POST -g {} -p {'user_input':'{{().__class__.__bases__[0].__subclasses__()}}'} -c {} -w ['waf'] -d 0 -cc 100 -t 60 -a 10
```

```shell
====================================================================================================

Thanks For Using WebFuzz-1.2.0 (https://github.com/BProbie/WebFuzz)

Uri: http://challenge.imxbt.cn:31952/
Fuzz: POST
GET: {}
POST: {'user_input': '{{().__class__.__bases__[0].__subclasses__()}}'}
UserAgent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36
Cookie: {}
Waf: ['waf']
Delay: 0
Concurrency: 100
Timeout: 60
Attempts: 10

The Script Start At The Time Of 2026-05-15 20:35:25

[##################################################] 1081/1081

The Script Stop At The Time Of 2026-05-15 20:35:55

====================================================================================================

The Result of WebFuzz: ['_', '[']
```

#### 小攻击载荷情况示例

```shell
WebFuzz -u http://challenge.imxbt.cn:31952/ -f POST -p {'user_input':'{{().__class__.__bases__[0].__subclasses__()}}'} -w ['waf'] -d 0 -cc 100
```

#### 大攻击载荷情况示例

```shell
WebFuzz -u http://challenge.imxbt.cn:31952/ -f POST -p {'user_input':'{{().__class__.__bases__[0].__subclasses__()}}'} -w ['waf'] -d 0 -cc 100000 -t 3600 -a 100
```

#### 访问冷却限制情况示例

```shell
WebFuzz -u http://challenge.imxbt.cn:31952/ -f POST -p {'user_input':'{{().__class__.__bases__[0].__subclasses__()}}'} -w ['waf'] -d 1
```



## ⭐项目结构

```markdown
WebFuzz/
├── .github/
│   └── workflows/
│       └── build.yml
├── .git/ # 已在仓库中删除
├── .idea/ # 已在仓库中删除
├── build/ # 已在仓库中删除
├── dist/ # 已在仓库中删除
├── scripts/
│   ├── build.bat
│   ├── build.sh
│   ├── main.spec # 已在仓库中删除
├── src/
│   └── webfuzz/
│       └── main.py
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```



## ⭐技术原理

获取输入参数 -> 引导矫正输入参数 -> 规范全部输入参数 -> 显示所有参数信息 -> 根据参数切割攻击载荷 -> 根据攻击载荷创建任务线程 -> 根据任务线程创建工作协程 -> 利用工作协程向目标网址发起异步网络请求 -> 获取网络请求的响应数据 -> 分析响应数据并做出异常处理 -> 将响应数据与拦截标志做出比较判断 -> 将拦截字节搜集整合起来 -> 同步模糊测试任务进度 -> 将搜集起来的拦截字节做共有字符颗粒度最小化处理(回溯法) -> 输出工作过程细节信息 -> 告知模糊测试结果



## ⭐技术细节

### 多终端

脚本做了多终端的适配，适配终端包括CMD、PowerShell、Shell等



### 跨平台

脚本做了跨平台的适配，适配平台包括Windows32、Windows64、Linux、Mac等



### 鲁棒性

脚本做了鲁棒性的优化，不仅支持使用命令行工具执行指令使用，而且支持鼠标左键双击打开脚本根据引导提示使用，并且脚本还会自动检查不合规范的参数值并且主动提出修正或者自动使用默认值作为替代



### 进程+线程+协程

脚本采用进程+线程+协程模式，会自动匹配最优并发配比，并发量最高可达[(CPU * 10)²] ≈ 10w+（其中并发效率在Linux或Mac操作系统中最为显著）



## ⭐技术创新

① 不同于其他大多数Web应用模糊测试脚本基于冗余的字典进行模糊测试的，这个脚本是基于更轻量的Payload攻击载荷切割进行模糊测试。

② 不同于其他大多数Web应用模糊测试脚本只基于线程或只基于协程执行模糊测试并发量有限，这个脚本是结合了线程和协程自动匹配最优配比执行模糊测试，在没有TCP和端口限制的情况下并发数可以达到恐怖的10w+且性能稳定。

③ 不同于其他大多数Web应用模糊测试脚本要么鲁棒性差要么注入点少，这个脚本很好地结合了鲁棒性和注入点，在提供了数个注入点的同时，对于不熟悉本脚本的使用者还提供了傻瓜模式和参数自检，对于要求较高的使用者还提供了多个参数用于自行修改。



## ⭐作者介绍

作者：**BProbie**

贡献：

- **BProbie**



## ⭐疑问交流联系

如有疑问请通过提交**Issue**阐述，作者能看到且会经常查看！



## ⭐附录

贡献指南：https://github.com/BProbie/WebFuzz?tab=contributing-ov-file

社区准则：https://github.com/BProbie/WebFuzz?tab=coc-ov-file

安全策略：https://github.com/BProbie/WebFuzz?tab=security-ov-file

更新内容：https://github.com/BProbie/WebFuzz/blob/master/CHANGELOG.md

作者详情：https://github.com/BProbie/WebFuzz/blob/master/AUTHORS.md

贡献者页：https://github.com/BProbie/WebFuzz/blob/master/CONTRIBUTORS.md

依赖仓库：https://github.com/BProbie/WebFuzz/blob/master/requirements.txt



# **❤❤❤**