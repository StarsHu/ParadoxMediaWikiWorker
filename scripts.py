from spider import Spider


class PageSync(object):
    def __init__(self, cn_url, cn_username, cn_password, eu_url, eu_username=None, eu_password=None):
        self.spider_cn = Spider(url=cn_url, username=cn_username, password=cn_password)
        self.spider_cn.login()
        self.spider_eu = Spider(url=eu_url, username=eu_username, password=eu_password)

    @staticmethod
    def get_page_title_by_prefix(spider: Spider, keyword, option=None):
        if option is None:
            option = {}
        page_list, continue_key = spider.get_page_list(keyword=keyword, limit=500, option=option)
        title_list = [each_page["title"] for each_page in page_list]
        while continue_key:
            page_list, continue_key = spider.get_page_list(
                keyword=keyword, limit=500, option={**option, "apcontinue": continue_key}
            )
            title_list.extend([each_page["title"] for each_page in page_list])
        return title_list

    def run(self, namespace=None):
        dig_list = "0123456789"
        str_list = "abcdefghijklmnopqrstuvwxyz"
        merged_list = []
        passed_list = []
        error_list = []
        option = {"apnamespace": namespace} if namespace else {}
        for letter in dig_list + str_list:
            origin_titles = self.get_page_title_by_prefix(self.spider_eu, letter, option=option)
            current_titles = self.get_page_title_by_prefix(self.spider_cn, letter, option=option)
            for title in origin_titles:
                if title in current_titles:
                    passed_list.append(title)
                    print('page "%s" passed' % title)
                else:
                    content = self.spider_eu.get_page_text(title)
                    try:
                        self.spider_cn.edit(title=title, text=content, summary="merge from offical wiki")
                        merged_list.append(title)
                        print('page "%s" merged successful' % title)
                    except:
                        error_list.append(title)
            print("letter %s checked, %i pages." % (letter, len(origin_titles)))
        print("merged number:", len(merged_list))
        print("passed number:", len(passed_list))
        print("ERROR:", error_list)


if __name__ == "__main__":
    p = PageSync(
        cn_url="https://ck3.parawikis.com/api.php",
        cn_username="用户名",
        cn_password="密码",
        eu_url="https://ck3.paradoxwikis.com/api.php",
    )
    p.run()
    p.run(namespace=6)
    p.run(namespace=10)
    p.run(namespace=14)
