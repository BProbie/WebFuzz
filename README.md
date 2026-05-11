# ⭐原创开源脚本

### 软件名称：WebFuzz（网安Web应用模糊测试脚本）

### 软件版本：v1.0.0（稳定版）

### 开发语言：Python（Python-3.13.0）

### 开发时间：2026年05月11日 ~ 至今持续更新！

### 开源地址（Github）：https://github.com/BProbie/WebFuzz/

### 开源协议（MIT）：https://github.com/BProbie/WebFuzz/raw/refs/heads/master/LICENSE/

### 下载地址（Github）：https://github.com/BProbie/WebFuzz/releases/tag/1.0.0/

### 依赖工具：pip

### 依赖技术：

- ##### PyInstaller~=6.15.0

- ##### requests~=2.32.5

- ##### fake-useragent~=2.2.0



# ⭐脚本背景

### 阳光明媚的一天，一个不知名的网安人正躲在宿舍打CTF，这是一道关于Web-SSTI的题目：So Easy！哎？不对，这是什么，Waf！

### 坐在电脑前的网安人陷入了沉默：我拿不到这道题目的源码，那我怎么知道它拦截了哪些字符？

### 问问AI吧：Fuzz？Fuzz是什么啊？模糊测试？模糊测试是什么呀？

### 在对AI追问不舍下我终于下了我人生中第一个Yakit：这怎么用啊？好困难啊！WebFuzz应该是这个吧...哎？怎么还要字典啊？字典在哪弄啊？字典又大又重不仅会污染我的存储空间导入还好慢呀！

### 怎么办？怎么办！坐在电脑前的网安人再一次陷入了沉思...

### 于是，WebFuzz（网安Web应用模糊测试脚本），诞生了！



# ⭐脚本简介

### 基于payload而非字典，用于网络空间安全学习以及测试的，Web应用模糊测试脚本



# ⭐快速开始

### GIT

##### 克隆项目

```shell
git clone https://github.com/BProbie/WebFuzz.git
```

##### 安装依赖

```shell
cd WebFuzz
python.exe -m pip install --upgrade pip
python.exe -m pip install -r requirements.txt
```

##### 构建工具

```shell
cd scripts
build
```

##### 运行测试

```shell
cd ..
cd dist
main -u http://www.baidu.com -dt {'key':'value'} -w ['waf']
```



# ⭐使用教程

### 帮助教程

```shell
WebFuzz -h
```

```shell
usage: 命令行参数 [-h] [-uri URI] [-type TYPE] [-data DATA] [-waf WAF] [-delay DELAY] [-thread THREAD]

options:
  -h, --help           show this help message and exit
  -uri, -u URI         请求网址 https://www.baidu.com/
  -type, -tp TYPE      请求类型 POST/GET
  -data, -dt DATA      请求数据 {'key':'value'}
  -waf, -w WAF         拦截标志 waf
  -delay, -dl DELAY    间隔秒数 0
  -thread, -tr THREAD  线程数量 1
```

|   名称   |  参数   | 简化 |     作用     |         规范          |                   示例                    | 必要 | 默认 |              备注              |
| :------: | :-----: | :--: | :----------: | :-------------------: | :---------------------------------------: | :--: | :--: | :----------------------------: |
| 查看帮助 |  -help  |  -h  |   查看帮助   |           /           |                WebFuzz -h                 |  /   |  /   |               /                |
| 请求网址 |  -url   |  -u  | 设置请求网址 | https://www.baidu.com |     WebFuzz -u https://www.baidu.com      |  是  |  /   |     可在网址中带上GET参数      |
| 请求类型 |  -type  |  -t  | 设置请求类型 |       POST/GET        |              WebFuzz -t POST              |  否  | POST |               /                |
| 请求参数 |  -data  | -dt  | 设置请求参数 |    {'key':'value'}    |        WebFuzz -dt {'key':'value'}        |  是  |  /   |   默认以第一对键值为Fuzz对象   |
| 拦截标志 |  -waf   |  -w  | 设置拦截标志 |      waf/['waf']      | WebFuzz -w waf \| WebFuzz -w ['waf','no'] |  是  |  /   | ['waf','no']两个标志是或的关系 |
| 请求间隔 | -delay  | -dl  | 设置请求间隔 |           0           |               WebFuzz -dl 0               |  否  |  0   |   当delay>=1时thread固定为1    |
| 请求线程 | -thread | -tr  | 设置请求线程 |           1           |               WebFuzz -tr 1               |  否  |  1   |      范围在[1,CPU核数*10]      |

### 使用示例

```shell
WebFuzz -u http://challenge.imxbt.cn:32542/ -ty POST -dt {'user_input':'{{().__class__.__base__.__subclasses__()}}'} -w ['waf'] -dl 0 -tr 100
```

```shell
Thanks For Using WebFuzz-v1.0.0 (https://github.com/BProbie/WebFuzz)
Uri: http://challenge.imxbt.cn:32542/
Type: POST
Data: {'user_input': '().__class__.__base__.__subclasses__()}'}
Waf: ['waf']
Delay: 0
Thread: 100
The Script Start At The Time Of 2026-05-11 21:29:39

[#########################] 780/780 (The Script End At The Time Of 2026-05-11 21:30:04)

The Result of WebFuzz: ['_']
```



# ⭐项目结构

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
├── src/
│   └── webfuzz/
│       └── main.py
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```



# ⭐技术细节

### ① 脚本做了多终端的适配

### ② 脚本做了跨平台的适配

### ③ 脚本做了鲁棒性的适配



# ⭐作者介绍

### 作者：probie

### 贡献：\[probie, probie, probie]



# ⭐疑问交流联系

### 如有疑问请通过提交Issue阐述，作者能看到且会经常查看！



# ❤❤❤