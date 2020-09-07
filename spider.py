import datetime

import requests


class Spider(object):
    def __init__(self, url, username=None, password=None):
        self.url = url
        self.username = username
        self.password = password

        self.login_status = False
        self.session = requests.Session()

    def get_token(self, type="csrf"):
        params = {
            "action": "query",
            "format": "json",
            "meta": "tokens",
            "type": type,
        }
        content = self._get(params=params)
        token = list(content["query"]["tokens"].values())[0]
        return token

    def login(self):
        if not self.username or not self.password:
            raise Exception("未定义用户名和密码")
        token = self.get_token("login")
        body = {
            "action": "login",
            "format": "json",
            "lgname": self.username,
            "lgpassword": self.password,
            "lgtoken": token,
        }
        content = self._post(body=body)
        if content.get("login", {}).get("result", "") == "Success":
            print("登陆成功")
            self.login_status = True
            return content
        else:
            print(content)
            raise Exception("登录失败")

    def logout(self):
        body = {
            "action": "logout",
            "format": "json",
        }
        content = self._post(body=body)
        return content

    def edit(self, title, text, summary=None, createonly=False):
        try:
            token = self.get_token("csrf")
            params = {
                "action": "edit",
                "format": "json",
                "title": title,
                "text": text,
                "bot": "1",
                "basetimestamp": datetime.datetime.utcnow().isoformat(),
                "token": token,
            }
            if summary:
                params["summary"] = summary
            if createonly:
                params["createonly"] = 1
            content = self._post(body=params, timeout=5)
            if content.get("edit", {}).get("result", "").lower() == "success":
                print("{}页面编辑成功".format(title))
                return content
            elif content.get("error", {}).get("code", "").lower() == "permissiondenied":
                print("请求过快，暂停30秒")
                raise Exception("编辑失败")
            else:
                print("编辑 {} 失败, ret: {}".format(title, content))
                raise Exception("编辑失败")
        except Exception:
            return None

    def check_page_exist(self, name_list):
        if not isinstance(name_list, list):
            name_list = [name_list]
        params = {"action": "query", "format": "json", "titles": "|".join(name_list)}
        content = self._get(params)
        result = {}
        data = content["query"]["pages"]
        for page_id, value in data.items():
            if not page_id.isdigit() or int(page_id) < 0:
                result[value["title"]] = False
            else:
                result[value["title"]] = True
        return result

    def get_page_list(self, keyword=None, limit=10, option=None):
        params = {
            "action": "query",
            "format": "json",
            "list": "allpages",
            "apfilterredir": "all",
            "aplimit": limit,
        }
        if keyword:
            params["apprefix"] = keyword
        if option:
            params.update(option)
        content = self._get(params)
        continue_key = None
        if content.get("continue"):
            continue_key = content["continue"]["apcontinue"]
        return content["query"]["allpages"], continue_key

    def get_page_text(self, name, option=None):
        params = {
            "action": "parse",
            "format": "json",
            "page": name,
            "prop": "wikitext",
        }
        if option:
            params.update(option)
        content = self._get(params)
        return content["parse"]["wikitext"]["*"]

    def _post(self, body=None, **kwargs):
        if "timeout" not in kwargs:
            kwargs["timeout"] = 5
        r = self.session.post(url=self.url, data=body, **kwargs)
        content = r.json()
        return content

    def _get(self, params=None, **kwargs):
        r = self.session.get(url=self.url, params=params, **kwargs)
        content = r.json()
        return content
