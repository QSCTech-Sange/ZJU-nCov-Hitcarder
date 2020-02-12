# ZJU-nCov-Hitcarder

浙大 nCov 肺炎健康打卡定时自动脚本

 - 可定时，默认为每天 6 点 5 分
 - 默认每次提交上次所提交的内容（只有时间部分更新）

 项目用于学习交流，仅用于各项无异常时打卡，如有身体不适等情况还请自行如实打卡~

<img src="https://github.com/Tishacy/ZJU-nCov-Hitcarder/raw/master/demo.png" width="500px"/>

> 感谢[conv1d](https://github.com/conv1d)同学，已使用 requests 直接登录浙大统一认证平台，不再依赖phantomjs
>
> ~~增加了各操作系统的phantomjs和自动选driver的功能，结果导致库变得较大，如果想自行下载对应版本的phantomjs，可以切换到`neat`分支（只保留了windows系统的phantomjs）下载本项目。~~

## Usage

1. clone 本项目（为了加快 clone 速度，可以指定 clone 深度`--depth 1`，只克隆最近一次 commit），并 cd 到本目录
    ```bash
    $ git clone https://github.com/Tishacy/ZJU-nCov-Hitcarder.git --depth 1
    $ cd ZJU-nCov-Hitcarder
    ```
    
2. 安装依赖

    ```bash
    $ pip3 install -r requirements.txt
    ```

3. 将 config.json.templ 模板文件重命名为 config.json 文件，并修改 config.json 中的配置。如果需要更多用户的话可以继续添加。请注意，用户与用户之间的大括号之间应该留有**空格**，而结尾不应该留有空格。如果只需要给一个人打开，可以删除第二个用户。
  
    ```javascript
    {   "username":"你的浙大统一认证平台用户名" , 
        "password":"你的浙大统一认证平台密码",
        "schedule": {
            "hour": "6",
            "minute": "5"
        } 
    },
    {   "username":"你对象的浙大统一认证平台用户名" , 
        "password":"你对象的浙大统一认证平台密码",
        "schedule": {
            "hour": "6",
            "minute": "5"
        } 
    }
    ```

4. 启动定时自动打卡脚本

   ```bash
   $ python3 daka.py
   ```


## Tips

- 为了防止电脑休眠或关机时程序不运行，推荐把这个部署到 VPS 上
- 测试程序是否正常运行：可以先把定的时间放在最近的一个时间（比如下一分钟）看下到时间是否可以正常打卡


## Thanks

感谢贡献者

<a href="https://github.com/conv1d"><img src="https://avatars2.githubusercontent.com/u/24759956" width="100px" height="100px"></a>


## LICENSE

Copyright (c) 2020 tishacy.

Licensed under the [MIT License](https://github.com/Tishacy/ZJU-nCov-Hitcarder/blob/master/LICENSE)



