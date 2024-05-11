# 安装使用教程

## 1, Metrix注册使用教程

**基础介绍** : https://www.neboer.site/nerchat/docs/introduction/

### 1.1 注册账号
由于当前国内网络限制,所以我们使用一个其他人部署在香港的matrix服务器,请访问 **https://chat.neboer.site/**
`完成账号的注册后,请牢记你的账号密码`


### 1.2 登录
登陆可以使用客户端或者网页端进行登陆,登陆的过程中请将你的服务器指向 `chat.neboer.site`
推荐登陆工具:
- https://element.io/
- 网页登陆


### 1.3 创建房间
- 创建房间可以选择公共房间或者私人房间
- 创建房间过程中不需要选择端到端加密(此功能会影响机器人,等待后续解决)
![创建房间.png]

### 1.4 加入房间
- 如果是私人房间,则需要房主发邀请给用户然后才能加入房间
- 如果是公共房间,则可以直接搜索加入
  ![加入公共房间](./attachment/加入公共房间.png "加入房间")

### 1.5 图片帮助
如果你不是特别清楚如何注册等,可以参考doc下面的deploy/attachment文件夹下面的图片帮助,如果还是有问题,请访问 **https://www.neboer.site/nerchat/docs/introduction/** 从而获得更详细的帮助


## 2, 项目安装使用教程
- git clone 此项目
- 切换你的环境,保证你的环境是python3.10.12的版本
    - 如果出现环境版本不对称,请使用conda重新安装此环境  
  ```shell
     conda create -n  py310 python=3.10.12 -y 
- 安装依赖
```shell
pip3 install -r requirements.txt && pip3 install -e . 
```

## 3，项目配置说明

项目配置文件在 `configs` 目录下,配置文件的说明如下:
- **ai/api.yaml** : 包含openai的api访问地址和请求地址,chatgpt没有vpn所以没有试验gpt连接是否正常
- **metrix/user.yaml** : 包含metrix的用户信息,包括用户名,密码,服务器地址等,如果你需要添加机器人的话,那么直接在上面添加即可,如果你不需要`prompt`的提示词,那么直接写明为null即可

## 4.启动项目
### 4.1 启动matrix项目
启动文件在aiverse/main.py中,直接使用 `rm -rf *.session && python3 run_matrix.py` 启动

### 4.2 启动matrix项目
启动文件在aiverse/main.py中,直接使用 `rm -rf *.secret && python3 run_mastodon.py ` 启动


## 5. 项目结构说明
- aiverse 为主入口
- aiverse/chatgpt:  为调用openai接口的封装
- aiverse/config: Hydra加载配置文件的类,用于加载配置文件
- aiverse/data_class : 为了验证传递过来的数据是否正常,所以定义了一个数据类模块
- aiverse/distribute : 分布式函数模块
- aiverse/metrix : 用于metrix-bot底层实现的逻辑模块
- aiverse/metrix_robot : 用于metrix-bot底层实现的逻辑模块
- aiverse/util : 通用的工具类模块



## 6. 当前小问题

### 6.1 如果你发现程序启动了  但是日志中没有发现用户登陆的信息,那么请检查你的本地文件是否存在一个 `session.txt`的文件,如果出现这个文件,那么把这个文件删除,后续我会做一个自动判断删除的逻辑



## 7， Docker环境安装和部署
docker pull jasoncky96/miniconda-ubuntu

