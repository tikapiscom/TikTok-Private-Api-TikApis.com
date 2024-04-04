import requests
import base64
import time
import random
import json
from urllib.parse import urlencode


class Captcha:
    def __init__(self, config, host, error_code, API_URL, API_KEY):
        self.host = host
        self.API_URL = API_URL
        self.API_KEY = API_KEY
        self.app_info = config.get("app_info", {})
        self.device = config.get("device", {})
        self.country_location = config.get("country_location", {})
        self.account = config.get("account", {})
        self.subtype = {1105: "slide", 1107: "3d",
                        1108: "whirl"}.get(error_code, "")
        self.client = requests.Session()

    def get_challenge(self):
        params = self.__params()
        req = self.client.get(url=(
            "https://" + self.host + "/captcha/get?" + params), headers=self.__headers())
        return req.json()

    def find_parameters(self, parsed_json, parameters):
        found_parameters = {}

        def search_in_json(json_obj):
            if isinstance(json_obj, dict):
                for key, value in json_obj.items():
                    if key in parameters:
                        found_parameters[key] = value
                    if isinstance(value, (dict, list)):
                        search_in_json(value)
            elif isinstance(json_obj, list):
                for item in json_obj:
                    search_in_json(item)
        search_in_json(parsed_json)
        return found_parameters

    def post_captcha(self, body):
        params = self.__params()
        headers = self.__headers()
        url = "https://" + self.host + "/captcha/verify?" + params
        req = self.client.post(url=url, headers=headers.update(
            {"content-type": "application/json"}), json=body)
        return req.json()

    def api_captcha_solver(self, data):
        payload = json.dumps(
            {**data, "app_info": {"aid": self.device.get("aid", "1233")}})
        response = self.client.post(self.API_URL, headers={
                                    'Content-Type': 'application/json', "api-key": self.API_KEY, "x-api-key": self.API_KEY}, data=payload)
        if response.json().get("mode"):
            time.sleep(random.randint(2, 3))
            return self.post_captcha(response.json())
        else:
            print("api_captcha_solver", response.content)
            exit()

    def solve_captcha(self, max_retries=3):
        retries = 2
        while retries < max_retries:
            try:
                captcha_challenge = self.get_challenge()
                break
            except Exception as e:
                retries += 1
                if retries >= max_retries:
                    raise Exception(
                        "Max retries reached while trying to get captcha challenge.") from e
        try:
            keys = ["mode", "url1", "url2", "url_1",
                    "url_2", "tip_y", "id", "verify_id", "host"]
            data = self.find_parameters(captcha_challenge, keys)
            if data:
                return self.api_captcha_solver(data)
            else:
                print("Data key not found.", captcha_challenge)
        except Exception as e:
            print("The incoming data is not in JSON format.", e)

    def __params(self):
        params = {
            "lang": self.device.get("lang_k", self.device.get("lang_b", "")),
            "app_name": self.app_info.get("app_name", ""),
            "h5_sdk_version": "2.21.2",
            "sdk_version": "2.2.1.i18n",
            "iid": self.device.get("install_id", self.device.get("iid", "")),
            "did": self.device.get("device_id", self.device.get("did", "")),
            "device_id": self.device.get("device_id", self.device.get("did", "")),
            "ch": "googleplay",
            "aid": self.device.get("aid", "1233"),
            "os_type": "0",
            "mode": self.subtype,
            "tmp": f"{int(time.time())}{random.randint(111, 999)}",
            "platform": "app",
            "webdriver": "undefined",
            "verify_host": f"https://{self.host}/",
            "locale": self.device.get("lang_k", self.device.get("lang_b", "")),
            "channel": "googleplay",
            "app_key": "",
            "vc": self.app_info.get("app_version"),
            "app_verison": self.app_info.get("app_version"),
            "session_id": "",
            "region": "",
            "use_native_report": "0",
            "use_jsb_request": "0",
            "orientation": "2",
            "resolution": self.device.get("resolution", ""),
            "os_version": self.device.get("os_version", ""),
            "device_brand": "Android",
            "device_model": self.device.get("device_model", "Android"),
            "os_name": "Android",
            "version_code": self.app_info.get("version_code"),
            "device_type": self.device.get("device_model", "Android"),
            "device_platform": "Android",
            "app_version": self.app_info.get("app_version"),
            "type": "verify",
            "challenge_code": "99999",
            "subtype": self.subtype,
        }
        return urlencode(params)

    def __headers(self):
        headers = {
            "Fastly-Client-IP": "{}.{}.{}.{}".format(*random.sample(range(0, 255), 4)),
        }
        return headers
