import random
import time
import json
import hashlib
import os
from datetime import datetime as dt
from urllib.parse import urlencode
URL_RFC_3986 = {
    "!": "%21", "#": "%23", "$": "%24", "&": "%26", "'": "%27", "(": "%28", ")": "%29", "*": "%2A", "+": "%2B",
    ",": "%2C", "/": "%2F", ":": "%3A", ";": "%3B", "=": "%3D", "?": "%3F", "@": "%40", "[": "%5B", "]": "%5D",
}
class Utils:
    @staticmethod
    def parse_set_cookie_headers(set_cookie_headers):
        cookies = {}
        if set_cookie_headers:
            cookie_headers = set_cookie_headers.split(", ")
            for cookie_header in cookie_headers:
                parts = cookie_header.split(";")
                if parts:
                    cookie = parts[0]
                    cookie_key_value = cookie.split("=")
                    if len(cookie_key_value) == 2:
                        key = cookie_key_value[0].strip()
                        value = cookie_key_value[1].strip()
                        if value:
                            cookies[key] = value
        return cookies
    @staticmethod
    def random_device_(file_limit):
        folder_path = "./device/"
        json_files = [os.path.join(folder_path, file) for file in os.listdir(
            folder_path) if file.endswith('.json')]
        file_limit = min(file_limit, len(json_files))
        random_files = random.sample(json_files, file_limit)
        loaded_json_data = []
        for file_path in random_files:
            with open(file_path, 'r') as file:
                json_data = json.load(file)
                loaded_json_data.append(json_data)
        return loaded_json_data
    @staticmethod
    def check_matching(data):
        keys = ["api21", "api22", "api31"]
        for prefix in keys:
            if prefix in data:
                parts = data.split('-')
                parts[0] = parts[0].replace(prefix, "api16")
                return '-'.join(parts)
        return data
    @staticmethod
    def random_mail():
        return random.choice(["@yahoo.com", "@outlook.com", "@zoho.com", "@icloud.com",])
    @staticmethod
    def rand_str(length):
        rand = ''
        random_str = '0123456789abcdef'
        for _ in range(length):
            rand += random.choice(random_str)
        return rand
    @staticmethod
    def url_encoder(b):
        if type(b) == bytes:
            b = b.decode(encoding="utf-8")
        result = bytearray()
        for i in b:
            if i in URL_RFC_3986:
                for j in URL_RFC_3986[i]:
                    result.append(ord(j))
                continue
            i = bytes(i, encoding="utf-8")
            if len(i) == 1:
                result.append(ord(i))
            else:
                for c in i:
                    c = hex(c)[2:].upper()
                    result.append(ord("%"))
                    result.append(ord(c[0:1]))
                    result.append(ord(c[1:2]))
        result = result.decode(encoding="ascii")
        return result
    @staticmethod
    def url_decoder(b):
        if type(b) == bytes:
            b = b.decode("utf-8")
        result = bytearray()
        enter_hex_unicode_mode = 0
        hex_tmp = ""
        now_index = 0
        for i in b:
            if i == '%':
                enter_hex_unicode_mode = 1
                continue
            if enter_hex_unicode_mode:
                hex_tmp += i
                now_index += 1
                if now_index == 2:
                    result.append(int(hex_tmp, 16))
                    hex_tmp = ""
                    now_index = 0
                    enter_hex_unicode_mode = 0
                continue
            result.append(ord(i))
        result = result.decode(encoding="utf-8")
        return result
    @staticmethod
    def create_payload(username, password, action_type):
        if (action_type == "register"):
            payload = f"password={Utils._xor_tiktok(password)}&fixed_mix_mode=1&rules_version=v2&mix_mode=1&multi_login=1&email={Utils._xor_tiktok(username)}&account_sdk_source=app&birthday={Utils.generate_random_birthdate()}&multi_signup=0"
        else:
            if '@' in username:
                payload = f"password={Utils._xor_tiktok(password)}&account_sdk_source=app&multi_login=1&mix_mode=1&email={Utils._xor_tiktok(username)}"
            else:
                payload = f"password={Utils._xor_tiktok(password)}&account_sdk_source=app&multi_login=1&mix_mode=1&username={Utils._xor_tiktok(username)}"
        return payload
    @staticmethod
    def get_follow_endpoint(aid):
        if int(aid) == 1340:
            return "lite/v2/relation/follow/"
        else:
            return "aweme/v1/commit/follow/user/"
    @staticmethod
    def get_like_endpoint(aid):
        if int(aid) == 1340:
            return "lite/v2/item/digg/"
        else:
            return "aweme/v1/commit/item/digg/"
    @staticmethod
    def generate_random_password():
        length = random.randint(8, 14)
        special_chars = "@+"
        uppercase_chars = "ABCOPSXYZ"
        lowercase_chars = "abcdefmnopqrsvwxz"
        digits = "0123456789"
        password_chars = [random.choice(special_chars)]
        password_chars += [random.choice(uppercase_chars)
                           for _ in range(random.randint(1, 3))]
        remaining_length = length - len(password_chars)
        password_chars += [random.choice(lowercase_chars + digits)
                           for _ in range(remaining_length)]
        random.shuffle(password_chars)
        password = ''.join(password_chars)
        return password
    @staticmethod
    def domain_chose(cookie: str = None):
        domains = {
            "maliva": [
                "api16-normal-c-alisg.tiktokv.com",
                "api19-normal-c-alisg.tiktokv.com",
                "api21-normal-c-alisg.tiktokv.com",
                "api22-normal-c-alisg.tiktokv.com",
            ],
            "useast1a": [
                "api16-normal-c-useast1a.tiktokv.com",
                "api19-normal-c-useast1a.tiktokv.com",
                "api22-normal-c-useast1a.tiktokv.com"
            ],
            "useast2a": [
                "api16-normal-c-useast2a.tiktokv.com",
                "api19-normal-c-useast2a.tiktokv.com",
                "api21-normal-c-useast2a.tiktokv.com",
                "api22-normal-c-useast2a.tiktokv.com"
            ],
            "us": [
                "api16-normal-useast5.us.tiktokv.com",
                "api19-normal-useast5.us.tiktokv.com"
            ]
        }
        captcha_urls = [
            "verify-sg.tiktokv.com",
            "verification-va.byteoversea.com"
        ]
        if cookie:
            cookie_dict = Utils.parse_cookies(cookie)
            tt_target_idc = cookie_dict.get('tt-target-idc', None)
            if tt_target_idc and tt_target_idc in domains:
                domain_choices = domains[tt_target_idc]
            else:
                domain_choices = [domain for sublist in domains.values()
                                  for domain in sublist]
        else:
            domain_choices = [domain for sublist in domains.values()
                              for domain in sublist]
        login_url = random.choice(domain_choices)
        captcha_url = random.choice(captcha_urls)
        return {"domain": login_url, "captcha_domain": captcha_url}
    @staticmethod
    def parse_cookies(cookie_str):
        cookie_dict = {}
        items = cookie_str.split(';')
        for item in items:
            parts = item.strip().split('=')
            if len(parts) == 2:
                key, value = parts
                key = key.strip()
                value = value.strip()
                if key in cookie_dict:
                    if isinstance(cookie_dict[key], list):
                        cookie_dict[key].append(value)
                    else:
                        cookie_dict[key] = [cookie_dict[key], value]
                else:
                    cookie_dict[key] = value
        cookie_dict = {k: v for k, v in cookie_dict.items()
                       if v is not None and v != ''}
        return cookie_dict
    @staticmethod
    def _xor_tiktok(string):
        encrypted = [hex(ord(c) ^ 5)[2:] for c in string]
        return "".join(encrypted)
    @staticmethod
    def _unxor_tiktok(encrypted_string):
        hex_chars = [encrypted_string[i:i+2]
                     for i in range(0, len(encrypted_string), 2)]
        decrypted_chars = [chr(int(hx, 16) ^ 5) for hx in hex_chars]
        return ''.join(decrypted_chars)
    @staticmethod
    def hashed_id(value):
        if "+" in value:
            type_value = "1"
        elif "@" in value:
            type_value = "2"
        else:
            type_value = "3"
        hashed_id = value + "aDy0TUhtql92P7hScCs97YWMT-jub2q9"
        hashed_value = hashlib.sha256(hashed_id.encode()).hexdigest()
        return f"hashed_id={hashed_value}&type={type_value}"
    @staticmethod
    def channel_select(device_brand):
        if device_brand.lower() == "huawei":
            return ("huaweiadsglobal_int")
        else:
            return ("googleplay")
    @staticmethod
    def userAgent_new(config):
        app_info = config.get("app_info", {})
        dev_info = config.get("device", {})
        country_location = config.get("country_location", {})
        device_model_or_type = dev_info['device_model'] if 'device_model' in dev_info else dev_info.get(
            'device_type', 'Unknown')
        build_id_part = f"; Build/{dev_info['build_id']}" if 'build_id' in dev_info and dev_info['build_id'] else ""
        return f"{app_info['package_name']}/{app_info['update_version_code']} (Linux; U; Android {dev_info['os_version']}; {country_location['lang_k']}_{country_location['lang_b']}; {dev_info['os_version']}; {device_model_or_type}{build_id_part})"
    @staticmethod
    def android_generate_query_new(config, extra=None):
        if extra is None:
            extra = {}
        app_info = config.get("app_info", {})
        dev_info = config.get("device", {})
        country_location = config.get("country_location", {})
        time_ts = int(time.time())
        url_params = {
            "manifest_version_code": app_info.get("manifest_version_code"),
            "_rticket": str(int(round(time_ts * 1000))),
            "current_region": country_location.get("lang_b", ""),
            "app_language": country_location.get("lang_k", ""),
            "app_type": dev_info.get("app_type", "normal"),
            "iid": dev_info.get("install_id", ""),
            "channel": Utils.channel_select(dev_info.get("device_brand", "").lower()),
            "device_type": dev_info.get("device_model", ""),
            "language": country_location.get("lang_k", ""),
            "locale": f'{country_location.get("lang_k", "")}-{country_location.get("lang_b", "")}',
            "resolution": dev_info.get("resolution", "").replace("x", "*"),
            "openudid": dev_info.get("openudid", ""),
            "update_version_code": app_info.get("update_version_code"),
            "ac2": "wifi5g",
            "cdid": dev_info.get("cdid", ""),
            "sys_region": country_location.get("lang_b", ""),
            "os_api": dev_info.get("os_api", ""),
            "timezone_name": country_location.get("tz_name", "").replace("/", "%2F"),
            "dpi": dev_info.get("dpi", ""),
            "carrier_region": country_location.get("lang_b", ""),
            "ac": "wifi",
            "device_id": dev_info.get("device_id", ""),
            "mcc_mnc": dev_info.get("mcc_mnc", ""),
            "os_version": str(dev_info.get("os_version", "")),
            "timezone_offset": country_location.get("tz_offset", ""),
            "version_code": app_info.get("version_code", ""),
            "app_name": app_info.get("app_name", ""),
            "version_name": app_info.get("app_version", ""),
            "device_brand": dev_info.get("device_brand", ""),
            "op_region": country_location.get("lang_b", ""),
            "ssmix": "a",
            "device_platform": "android",
            "build_number": app_info.get("app_version", ""),
            "region": country_location.get("lang_b", ""),
            "aid": app_info.get("aid", ""),
            "ts": str(time_ts),
        }
        if not url_params["iid"]:
            del url_params["iid"], url_params["device_id"]
        url_params.update(extra)
        query = Utils.url_decoder(Utils.url_encoder(
            urlencode(url_params)))
        return query.replace("/", "%2F").replace("+", "%20").replace("+", "%20").replace("+", "%20").replace("+", "%20")
    @staticmethod
    def generate_random_birthdate():
        current_year = dt.now().year
        birth_year = random.randint(current_year - 50, current_year - 18)
        birth_month = random.randint(1, 12)
        if birth_month == 2:
            if (birth_year % 4 == 0 and birth_year % 100 != 0) or (birth_year % 400 == 0):
                max_day = 29
            else:
                max_day = 28
        elif birth_month in [4, 6, 9, 11]:
            max_day = 30
        else:
            max_day = 31
        birth_day = random.randint(1, max_day)
        return f"{birth_year}-{birth_month:02d}-{birth_day:02d}"
    @staticmethod
    def payload_data(data):
        if isinstance(data, bytes):
            payload = data.decode()
            return data if payload.startswith(('b\'', 'b"')) and payload.endswith(('\'', '"')) else data.hex()
        try:
            return json.dumps(json.loads(data))
        except (ValueError, TypeError):
            return data
    @staticmethod
    def check_and_convert(payload):
        try:
            return bytes.fromhex(payload) if isinstance(payload, str) else payload
        except ValueError:
            return payload
    @staticmethod
    def extract_ids(data):
        decoded_data = data.decode('utf-8')
        json_data = json.loads(decoded_data)
        return {
            "new_user": json_data.get("new_user"),
            "device_id": json_data.get("device_id_str"),
            "install_id": json_data.get("install_id_str"),
        }
