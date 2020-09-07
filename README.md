# ParadoxMediaWikiWorker
用于P社维基搬页面

## 安装
1. 安装python
2. 安装python环境
    `pip install -r requirements.txt`
3. 填写同步脚本中的登录名与密码  
    打开`scripts.py`文件，找到 `cn_username="用户名",
        cn_password="密码"`代码位置，将用户名和密码替换为自己的账户用户名密码
4. 运行 `python scripts.py`