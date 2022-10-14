import json
from ddddocr import DdddOcr
import re
import os
import random
import requests
import yaml
import time


class QNDXX_NEW_COURSE():
    def __init__(self) -> None:
        self.id = 0
        self.title = ""
        self.url = ""
        # self.org_id =
        self.study_url = f"https://m.bjyouth.net/dxx/check?id={self.id}"
        self.need_update = True

    def update(self, headers):
        try:
            r = requests.get("https://m.bjyouth.net/dxx/index",
                             headers=headers,
                             timeout=5)
            r.status_code
            index = json.loads(r.text)
            self.id = index["newCourse"]["id"]
            self.title = index["newCourse"]["title"]
            self.url = index["newCourse"]["url"]
            # self.org_id = index["rank"][0]["data"][1]['org_id']
            i = self.url.find("/m.html")
            self.url = self.url[:i]
            self.study_url = f"https://m.bjyouth.net/dxx/check?id={self.id}"
            print('[INFO] Class updated success')
            return True
        except:
            print('[ERROR] Class update failed')
            return False


class Youth():
    def __init__(self) -> None:
        self.cookies = ""
        self.username = ""
        self.password = ""
        self.get_cookies_turn = 5
        self.course = QNDXX_NEW_COURSE()
        self.ua = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x6307062c)"
        self.headers = {
            "Host": "m.bjyouth.net",
            "User-Agent": self.ua,
            "Cookie": "",
            "Referer": "https://m.bjyouth.net/qndxx/index.html"
        }
        self.org_id = ""
        # self.email = ""

    def get_cookie(self):
        for i in range(self.get_cookies_turn):
            # cookies = self.get_login_cookie_with_selenium()
            print(f'[INFO] Try to get cookie ... {i}/{self.get_cookies_turn}')
            cookies = self.get_cookie_with_requests()
            if cookies:
                self.cookies = 'PHPSESSID=' + cookies
                self.headers["Cookie"] = self.cookies
                print('[INFO] Get cookie successfully.')
                return True
        print('[ERROR] Get cookie error! please check your password.')
        return False

    def get_cookie_with_requests(self):
        try:
            S = requests.Session()
            headers = {"Host": "m.bjyouth.net", "User-Agent": self.ua}
            r = S.get(url="https://m.bjyouth.net/site/login",
                      headers=headers,
                      timeout=5)
            r.status_code
            cap_url = "https://m.bjyouth.net" + re.findall(
                r'src="/site/captcha.+" alt=', r.text)[0][5:-6]
            headers["Referer"] = "https://m.bjyouth.net/site/login"
            cap = S.get(url=cap_url, headers=headers, timeout=5)
            cap.status_code
            ocr = DdddOcr()
            cap_text = ocr.classification(cap.content)

            print(f'[INFO] Captcha OCR: {cap_text}')
            # print(S.cookies.get_dict())
            _csrf_mobile = S.cookies.get_dict()['_csrf_mobile']
            headers["Origin"] = "https://m.bjyouth.net"
            login_username = self.username
            login_password = self.password
            login_r = S.post('https://m.bjyouth.net/site/login',
                             headers=headers,
                             data={
                                 '_csrf_mobile': _csrf_mobile,
                                 'Login[username]': login_username,
                                 'Login[password]': login_password,
                                 'Login[verifyCode]': cap_text
                             },
                             timeout=5)
            return login_r.cookies.get_dict()["PHPSESSID"]
        except:
            return ""

    def read_config(self, config):
        self.username = config["username"]
        self.password = config["password"]
        if not (self.username and self.password):
            raise "username and password cannot be blank!!!"
        self.org_id = config['org_id'] or self.org_id
        # self.email = config["email"] or ""

    def study(self):
        try:
            study_url = f"{self.course.study_url}&org_id={self.org_id}"
            # r = requests.get(url=study_url, headers=self.headers, timeout=5)
            data = {"id": self.course.id, "org_id": self.org_id}
            r = requests.post(url="https://m.bjyouth.net/dxx/check",
                              headers=self.headers, timeout=5, json=data)
            r.status_code
            if r.text:
                print(
                    f'[ERROR] The url{study_url} maybe not correct or the website changed'
                )
                return True
            print(f'[INFO] Study complete')
            return True
        except:
            print('[ERROR] Study fail')
            return False


def main():
    youth = Youth()
    course = youth.course
    print("[INFO] Read config from config.yaml")
    with open("config.yaml", "r") as f:
        config_dict = yaml.safe_load(f)

    user_i = 0
    for single_config in config_dict["youth"]:
        print("[INFO] User ", user_i, " Start")
        user_i += 1
        youth.read_config(single_config)
        if not youth.get_cookie():
            continue
        if course.need_update:
            if not course.update(youth.headers):
                continue
            course.need_update = False
        if not youth.study():
            continue
        sleep_time = 2 + random.random()
        print(f"[INFO] Sleep {sleep_time} s")
        time.sleep(sleep_time)
    return True


def main_cli(args):
    print("[INFO] Read config from command line parameters")
    print("[INFO] Start")
    youth = Youth()
    youth.username = args["USERNAME"]
    youth.password = args["PASSWORD"]
    youth.org_id = args["ORG_ID"]
    if not youth.get_cookie():
        return False
    if not youth.course.update(youth.headers):
        return False
    if not youth.study():
        return False


if __name__ == "__main__":
    ENV = {
        _i: os.getenv(_i) for _i in ["PASSWORD", "USERNAME", "ORG_ID", "REMOTE_CONFIG"]
    }
    if ENV["REMOTE_CONFIG"]:
        main(ENV["REMOTE_CONFIG"])
    elif ENV["USERNAME"] and ENV["PASSWORD"] and ENV["ORG_ID"]:
        main_cli(ENV)
    else:
        main()
