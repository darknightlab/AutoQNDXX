import json
from ddddocr import DdddOcr
import re
import requests
import yaml
import argparse
import onnxruntime
import time


class QNDXX_NEW_COURSE():
    def __init__(self) -> None:
        self.id = 0
        self.title = ""
        self.url = ""
        self.end_img_url = ""
        self.study_url = ""
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
            print(f"[INFO] NEW COURSE id={self.id}, title={self.title}")
            self.url = index["newCourse"]["url"]
            # self.org_id = index["rank"][0]["data"][1]["org_id"]
            i = self.url.find("/m.html")
            self.end_img_url = self.url[:i] + "/images/end.jpg"
            self.study_url = f"https://m.bjyouth.net/dxx/check?id={self.id}&org_id=%s"
            print("[INFO] Class updated success")
            return 1
        except:
            print("[ERROR] Class update failed")
            return 0


class Youth():
    def __init__(self) -> None:
        self.cookies = ""
        self.username = ""
        self.password = ""
        self.get_cookies_turn = 6
        self.course = QNDXX_NEW_COURSE()
        self.ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Safari/605.1.15"
        self.headers = {
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "Host": "m.bjyouth.net",
            "User-Agent": self.ua,
            "Cookie": "",
            "Referer": "https://m.bjyouth.net/qndxx/index.html",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
        self.org_id = ""  # Does not matter, change config instead
        self.send_message_org_id = ""
        self.email = ""

    def get_cookie(self):
        for i in range(self.get_cookies_turn):
            # cookies = self.get_login_cookie_with_selenium()
            print(f"[INFO] Try to get cookie ... {i}/{self.get_cookies_turn}")
            cookies, cookiem = self.get_cookie_with_requests()
            print(cookies, cookiem)
            if cookies:
                self.cookies = "HttpOnly=true; _csrf_mobile="+cookiem + \
                    "; HttpOnly=true; PHPSESSID=" + cookies + "; schedule=not; summary=month"
                self.headers["Cookie"] = self.cookies
                print("[INFO] Get cookie success")
                return 1
        print("[ERROR] Get cookie error! please check your password.")
        return 0

    def get_cookie_with_requests(self):
        try:
            S = requests.Session()
            headers = {"Host": "m.bjyouth.net", "User-Agent": self.ua,
                       "Referer": "https://m.bjyouth.net/qndxx/index.html"}
            r = S.get(url="https://m.bjyouth.net/site/login",
                      headers=headers,
                      timeout=5)
            r.status_code
            cap_url = "https://m.bjyouth.net" + re.findall(
                r"src=\"/site/captcha.+\" alt=", r.text)[0][5:-6]
            headers["Referer"] = "https://m.bjyouth.net/site/login"
            cap = S.get(url=cap_url, headers=headers, timeout=5)
            cap.status_code
            onnxruntime.set_default_logger_severity(3)
            ocr = DdddOcr()
            cap_text = ocr.classification(cap.content)
            print(f"[INFO] Captcha OCR: {cap_text}")
            _csrf_mobile = S.cookies.get_dict()["_csrf_mobile"]
            headers["Origin"] = "https://m.bjyouth.net"
            login_username = self.username
            login_password = self.password
            login_r = S.post("https://m.bjyouth.net/site/login",
                             headers=headers,
                             data={
                                 "_csrf_mobile": _csrf_mobile,
                                 "Login[username]": login_username,
                                 "Login[password]": login_password,
                                 "Login[verifyCode]": cap_text
                             },
                             timeout=5)
            # import ipdb;ipdb.set_trace()
            return [login_r.cookies.get_dict()["PHPSESSID"], login_r.cookies.get_dict()["_csrf_mobile"]]
        except:
            return [None, None]

    def read_config(self, config):
        self.username = config["username"]
        self.password = config["password"]
        if not (self.username and self.password):
            raise "username and password cannot be blank!!!"
        self.org_id = config["org_id"] or self.org_id
        self.send_message_org_id = config["send_message_org_id"] or self.org_id

    def study(self, course_id=None):
        try:
            if course_id is None:  # Use default (newest)
                course_id = self.course.id
            study_url = f"https://m.bjyouth.net/dxx/check?id={course_id}&org_id={self.org_id}"
            requests.get(
                url=f"https://m.bjyouth.net/qndxx/index.html#/pages/home/detail?id={course_id}", headers=self.headers, timeout=5)
            for i in range(2):
                print(f"[INFO] Studying {course_id}...{i}/2")
                r = requests.get(
                    url=study_url, headers=self.headers, timeout=5)
                r3 = requests.get(
                    url="https://m.bjyouth.net/dxx/is-league", headers=self.headers, timeout=5)
                time.sleep(1)
                r2 = requests.get(
                    url=f"https://m.bjyouth.net/dxx/course-detail?id={course_id}", headers=self.headers, timeout=5)
                if r.text and r2.text and r3.text:
                    print(
                        f"[ERROR] The url {study_url} maybe not correct or the website changed")
                    return 0

            print(f"[INFO] Study completed!")
            return 1
        except:
            print("[ERROR] Study failed!")
            return 0


def main():
    youth = Youth()
    course = youth.course
    print("[INFO] Read config from config.yaml")
    with open("config.yaml", "r") as f:
        config_dict = yaml.safe_load(f)
    for single_config in config_dict["youth"]:
        print(single_config["username"], "Start")
        youth.read_config(single_config)
        if not youth.get_cookie():
            continue
        if (course.need_update):
            if not course.update(youth.headers):
                continue
            course.need_update = False
        # youth.study(51) # learn by course_ID (id=51 as an example)

        # for i in range(1,62): # iterative learn a lot of courses!
        #     youth.study(i)
        #     time.sleep(6)

        if not youth.study():  # learn the newest!
            continue
    return 1


def main_cli(args):
    print("[INFO] Read config from command line parameters")
    print("[INFO] Start")
    youth = Youth()
    course = youth.course
    youth.username = args.username
    youth.password = args.password
    youth.org_id = args.org_id
    if not youth.get_cookie():
        return 0
    if not course.update(youth.headers):
        return 0
    if not youth.study():
        return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", type=str)
    parser.add_argument("--password", type=str)
    parser.add_argument("--org_id", type=str)
    args = parser.parse_args()
    if (args.username and args.password and args.org_id):
        main_cli(args)
    else:
        main()
