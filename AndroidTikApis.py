import requests
import json
import random
import time
import traceback
from utilities import Utils
from HTTPRequester import HTTPRequester
from captcha import Captcha


class AndroidTikApis:
    def __init__(self, **kwargs):
        self.API_KEY = ''
        self.API_URL = "https://tikapis.com/private/android/v1/"
        self.config = kwargs
        self.SOLVER_API = f"{self.API_URL}/captcha/solver"
        self.DOMAIN_NORMAL = random.choice(["api-boot.tiktokv.com"])
        self.headers = {'api-key': self.API_KEY,'x-api-key': self.API_KEY, 'Content-Type': 'application/json'}
        self.proxy = kwargs.get("proxy", "")
        self.setup_proxy()
        self.user = {}
        self.http_requester = HTTPRequester(
            proxies=self.proxy, app=self.config, API_URL=self.API_URL, API_HEADERS=self.headers)

    def device_save(self):
        device_id = f'./device/{self.config.get("device", {}).get("device_id","0")}.json'
        with open(device_id, 'w') as file:
            json.dump(self.config, file)
        print(f"Data successfully saved to {device_id} in JSON format.")

    def build_headers(self):
        return {
            "passport-sdk-version": self.config.get("passport-sdk-version", "19"),
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "sdk-version": "2",
            "cookie": self.config.get("cookie", ""),
            "x-tt-token": self.config.get("x_token", ""),
            "x-bd-client-key": self.config.get("x_bd_lanusk", ""),
            'user-agent': Utils.userAgent_new(self.config)
        }

    def error_check(self, response):
        return response.get('error') if isinstance(response, dict) else None

    def setup_proxy(self):
        if self.proxy:
            proxy_type = "SOCKS5" if "socks5" in self.proxy.lower() else "HTTP"
            print(f"Using {proxy_type} proxy: {self.proxy}")
        else:
            print("No proxy provided. Using local network.")
        if not all(key in self.config for key in ("tz_name", "lang_k", "lang_b")):
            self.fetch_additional_data()

    def fetch_additional_data(self):
        try:
            proxies = {'http': f'http://{self.proxy}',
                       'https': f'http://{self.proxy}'} if self.proxy else None
            response = requests.get(
                "https://ipinfo.io/json", proxies=proxies, timeout=10)
            response.raise_for_status()
            response_data = response.json()
            print(response_data)
            country_code = response_data.get("country", "US")
            self.config['country_location'].update(tz_name=response_data.get(
                "timezone", "America/New_York"), lang_b=country_code, lang_k="en" if country_code == "us" else country_code.lower())
        except Exception as e:
            traceback.print_exc()
            self.config['country_location'].update(tz_name=random.choice(
                ["America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles"]), lang_b="US", lang_k="en")

    def session_cookie(self, response):
        if hasattr(response, 'headers') and "set-cookie" in response.headers:
            set_cookie_header = response.headers.get("set-cookie", "")
            if set_cookie_header:
                cookies = Utils.parse_set_cookie_headers(set_cookie_header)
                existing_cookies = {key.strip(): value.strip() for key, value in [cookie.split(
                    "=") for cookie in self.config.get("cookie", "").split("; ") if "=" in cookie]}
                existing_cookies.update(
                    {key: value for key, value in cookies.items() if value})
                self.config["cookie"] = "; ".join(
                    [f"{key}={value}" for key, value in existing_cookies.items()])
                for key, value in cookies.items():
                    setattr(self, key, value)

    def device_template(self):
        response = requests.post(
            f"{self.API_URL}/service/template", headers=self.headers, json=self.config)
        try:
            response_data = response.json()
            if response_data.get('app_info'):
                self.config.update(**response_data)
            else:
                print(response.content)
                exit()
        except ValueError:
            print(response.content)
            exit()
                
    def device_register(self):
        response = requests.post(
            f"{self.API_URL}/service/register", headers=self.headers, data=json.dumps(self.config))
        if response.status_code == 200:
            try:
                response_data = response.json()
                if 'method' in response_data:
                    self.config['device'].update(Utils.extract_ids(
                        self.tiktok_auto_request(response_data)))
                else:
                    return response.content
            except ValueError:
                return response.content
        return response.content

    def get_token(self):
        return self.request_and_process("mssdk/token", "token", "mssdk/token_decode", ["sdk_token"])

    def get_seed(self):
        return self.request_and_process("mssdk/get_seed", "seed", "mssdk/seed_decode", ["sdk_dyn_seed"])

    def api_request(self, endpoint, payload={}):
        return requests.post(f"{self.API_URL}/{endpoint}", headers=self.headers, json={**payload, **self.config}).json()

    def request_and_process(self, endpoint, key, process_key, success_keys):
        try:
            response = requests.post(
                f"{self.API_URL}/{endpoint}", headers=self.headers, data=json.dumps(self.config))
            if response.status_code == 200:
                response_data = response.json()
                if 'method' in response_data:
                    token = self.tiktok_auto_request(response_data)
                    processed_response = self.api_request(
                        process_key, {f"{key}_hex": token.hex()})
                    if all(key in processed_response for key in success_keys):
                        return self.config['mssdk_parameters'].update(**processed_response)
        except Exception as e:
            return "An error occurred or the conditions were not met."

    def get_sign(self, url, data=None, extra_headers=None):
        if data is None:
            data = ""
        extra_headers = extra_headers or {}
        payload = {
            "url": url,
            "data": Utils.payload_data(data),
            "headers": json.dumps(extra_headers)
        }
        response = requests.post(
            f"{self.API_URL}/sign/create", headers=self.headers, json={**self.config, **payload})
        if response.status_code == 200 and 'X-Argus' in response.json():
            response_data = response.json()
        else:
            print(response.content)
            exit()
        return response_data

    def tiktok_auto_request(self, load):
        try:
            method = load.get("method", "GET")
            response = self.http_requester.post(load["url"], headers=load["headers"], data=Utils.check_and_convert(load.get(
                "payload", {}))) if method == "POST" else self.http_requester.get(load["url"], headers=load["headers"]) if method == "GET" else None
            self.session_cookie(response) if response else None
            return self.error_check(response) or (response.content if response else json.dumps(load))
        except Exception as e:
            print({"error": str(e), "traceback": traceback.format_exc()})
            return json.dumps(load)

    def app_region(self):
        try:
            query = Utils.android_generate_query_new(self.config, {})
            payload = Utils.hashed_id(
                self.config.get("account", {}).get("email"))
            url = f"https://{self.DOMAIN_NORMAL}/passport/app/region/?{query}"
            headers = self.build_headers()
            headers.update(self.get_sign(
                url, data=payload, extra_headers=headers))
            json_response = self.http_requester.post(
                url, headers=headers, data=payload)
            if 'data' in json_response and 'domain' in json_response:
                self.session_cookie(json_response)
                return json_response.json()
            else:
                return {}
        except Exception as e:
            traceback.print_exc()

    def user_save(self):
        user_id_str = self.config.get("user", {}).get("user_id_str")
        if user_id_str is not None:
            user_file_path = f'./user/{user_id_str}.json'
            with open(user_file_path, 'w') as file:
                json.dump(self.config, file)
            print(
                f"Data successfully saved to {user_file_path} in JSON format.")
        else:
            exit()

    def get_domain_info(self, app_region):
        if app_region and "data" in app_region:
            data = app_region["data"]
            if "domain" in data and data["domain"]:
                return data
        return Utils.domain_chose(self.config.get("cookie", ""))

    def user_login(self, r, callback=None, retry_after_captcha=False):
        if isinstance(r, dict) and "error" in r:
            return r
        try:
            if hasattr(r, "headers") and "x-tt-token" in r.headers:
                token = r.headers.get("x-tt-token")
                if token:
                    response_json = r.json()
                    set_cookie_headers = r.headers.get("x-tt-token")
                    if set_cookie_headers:
                        self.session_cookie(r)
                        user = {}
                        user["proxy"] = self.config.get("proxy", "")
                        user["domain"] = self.DOMAIN_NORMAL
                        user["account"] = self.config.get("account", {})
                        user["app_info"] = self.config.get("app_info", {})
                        user["mssdk_parameters"] = self.config.get(
                            "mssdk_parameters", {})
                        user["country_location"] = self.config.get(
                            "country_location", {})
                        user["device"] = self.config.get("device", {})
                        user["user"] = response_json.get("data")
                        user["x_token"] = r.headers.get("x-tt-token")
                        user["x_bd_lanusk"] = r.headers.get("x-bd-lanusk", "")
                        user["cookie"] = self.config.get("cookie", "")
                        self.config.update(**user)
                        self.user_save()
                        return json.dumps(user)
            else:
                is_json = r.json()
                error_code = is_json.get("data", {}).get("error_code", None)
                if error_code in [1107, 1105, 1108] and not retry_after_captcha:
                    captcha_solution = Captcha(
                        self.config,
                        self.captcha_domain,
                        error_code,
                        self.SOLVER_API,
                        self.API_KEY
                    ).solve_captcha()
                    print(f"Captcha solved: {captcha_solution}")
                    if callback:
                        return callback()
                print(is_json)
                exit()
        except Exception as e:
            print(r.content)
            exit()

    def account_register(self, retry_after_captcha=False):
        app_region = self.app_region().decode(
            'utf-8') if isinstance(self.app_region(), bytes) else self.app_region()
        domain_info = self.get_domain_info(app_region)
        self.captcha_domain = domain_info["captcha_domain"]
        self.DOMAIN_NORMAL = domain_info["domain"]
        extra = {
            "passport-sdk-version": self.config.get("passport-sdk-version", "5030190"),
            "uoo": "0",
            "cronet_version": self.config.get("cronet_version", ""),
            "ttnet_version": self.config.get("ttnet_version", ""),
            "use_store_region_cookie": "1"
        }
        query = Utils.android_generate_query_new(self.config, extra)
        payload = Utils.create_payload(self.config.get("account", {}).get(
            "email"), self.config.get("account", {}).get("password"), "register")
        url = f"https://{self.DOMAIN_NORMAL}/passport/email/register/v2/?{query}"
        headers = self.build_headers()
        headers.update(self.get_sign(
            url=url, data=payload, extra_headers=headers))
        response = self.http_requester.post(url, headers=headers, data=payload)
        return self.user_login(
            response,
            lambda: self.account_register(retry_after_captcha=True),
            retry_after_captcha,
        )

    def signature(self):
        response = requests.post(
            f"{self.API_URL}/commit/user/profile/signature", headers=self.headers, json=self.config)
        try:
            response_data = response.json()
            return response_data
        except ValueError:
            return response.content

    def bio_url(self):
        response = requests.post(
            f"{self.API_URL}/commit/user/bio_url", headers=self.headers, json=self.config)
        try:
            response_data = response.json()
            return response_data
        except ValueError:
            return response.content

    def nickname(self):
        response = requests.post(
            f"{self.API_URL}/commit/user/profile/nickname", headers=self.headers, json=self.config)
        try:
            response_data = response.json()
            return response_data
        except ValueError:
            return response.content

    def login_name(self):
        response = requests.post(
            f"{self.API_URL}/commit/user/login_name", headers=self.headers, json=self.config)
        try:
            response_data = response.json()
            return response_data
        except ValueError:
            return response.content

    def uniqueid_check(self):
        response = requests.post(
            f"{self.API_URL}/commit/user/uniqueid_check", headers=self.headers, json=self.config)
        try:
            response_data = response.json()
            return response_data
        except ValueError:
            return response.content

    def user_image_add(self):
        response = requests.post(
            f"{self.API_URL}/commit/user/profile/user_image_add", headers=self.headers, json=self.config)
        try:
            response_data = response.json()
            return response_data
        except ValueError:
            return response.content

    def user_image_upload(self):
        r = requests.post(
            f"{self.API_URL}/commit/user/profile/user_image_upload", headers=self.headers, json=self.config)
        try:
            is_json = r.json()
            uri = is_json.get("data", {}).get("uri", "")
            self.config.update({"avatar_uri": uri})
            return self.user_image_add()
        except ValueError:
            return r.content

    def conversation_create(self):
        self.config["conversation"].update(
            {"from_user_id": self.config.get("user", {}).get("old_user_id_str", "")})
        r = requests.post(
            f"{self.API_URL}/message/conversation/create", headers=self.headers, json=self.config)
        try:
            is_json = r.json()
            conversation = is_json.get("body", {}).get(
                "conversation", {}).get("conversation_id", {})
            self.config["conversation"].update(
                {
                    "conversation_id": conversation.get("conversation_id"),
                    "conversation_short_id": conversation.get("conversation_short_id")
                })
            return True
        except ValueError:
            return r.content

    def text_send(self):
        response = requests.post(
            f"{self.API_URL}/message/text_send", headers=self.headers, json=self.config)
        try:
            response_data = response.json()
            return response_data
        except ValueError:
            return response.content

    def video_send(self):
        response = requests.post(
            f"{self.API_URL}/message/video_send", headers=self.headers, json=self.config)
        try:
            response_data = response.json()
            return response_data
        except ValueError:
            return response.content

    def comment(self):
        response = requests.post(
            f"{self.API_URL}/commit/publish/comment", headers=self.headers, json=self.config)
        try:
            response_data = response.json()
            return response_data
        except ValueError:
            return response.content
        
    def service_account_register(self):
        response = requests.post(
            f"{self.API_URL}/passport/email/register", headers=self.headers, data=json.dumps(self.config))
        if response.status_code == 200:
            try:
                response_data = response.json()
                user_id_str = response_data.get("user", {}).get("user_id_str")
                if user_id_str is not None:
                    self.config.update(**response_data)
                    self.user_save()
                    return response_data
                else:
                    print(response.content)
                    exit()
            except ValueError:
                return response.content
        return response.content

    def login(self):
        response = requests.post(
            f"{self.API_URL}/passport/user/login", headers=self.headers, data=json.dumps(self.config))
        if response.status_code == 200:
            try:
                response_data = response.json()
                user_id_str = response_data.get("user", {}).get("user_id_str")
                if user_id_str is not None:
                    self.config.update(**response_data)
                    self.user_save()
                    return response_data
                else:
                    print(response.content)
                    exit()
            except ValueError:
                return response.content
        return response.content

    def sms_send_code(self):
        response = requests.post(
            f"{self.API_URL}/passport/mobile/sms_send_code", headers=self.headers, json=self.config)
        try:
            response_data = response.json()
            return response_data
        except ValueError:
            return response.content

    def sms_login_only(self):
        response = requests.post(
            f"{self.API_URL}/passport/mobile/sms_login_only", headers=self.headers, data=json.dumps(self.config))
        if response.status_code == 200:
            try:
                response_data = response.json()
                user_id_str = response_data.get("user", {}).get("user_id_str")
                if user_id_str is not None:
                    self.config.update(**response_data)
                    self.user_save()
                    return response_data
                else:
                    print(response.content)
                    exit()
            except ValueError:
                return response.content
        return response.content

    def perform_action(self, action_type, extra):
        domain = Utils().check_matching(self.config.get(
            "domain", self.DOMAIN_NORMAL).replace("c-", ""))
        end_point = Utils.get_follow_endpoint(self.config.get("aid", -1)) if action_type == "follow" \
            else Utils.get_like_endpoint(self.config.get("aid", -1))
        url = f"https://{domain}/{end_point}?{Utils.android_generate_query_new(self.config, extra)}"
        headers = self.build_headers()
        headers.update(self.get_sign(url, extra_headers=headers))
        response = self.http_requester.get(url, headers)
        error = self.error_check(response)
        return error if error else response.content

    def follow(self):
        extra = {"user_id": "107955",
                 "sec_user_id": "", "type": "1"}
        return self.perform_action("follow", extra)

    def digg(self):
        extra = {"aweme_id": "107955", "type": "1"}
        return self.perform_action("digg", extra)
