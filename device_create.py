from AndroidTikApis import AndroidTikApis
import json

device = {
    # "proxy": f"username:password@ip:port",
    "app_info": {
        "aid": 1233,
        "app_version": "34.0.2",
        "version_code": "340002",
        "manifest_version_code": "2023400020",
        "update_version_code": "2023400020",
    },
    "country_location": {},
    "mssdk_parameters": {
        "lc_sdk_version": 134252544,
    }
}
for i in range(0, 1):
    tik_api = AndroidTikApis(**device)
    tik_api.device_template()
    tik_api.device_register()
    tik_api.get_token()
    tik_api.get_seed()
    print(json.dumps(tik_api.config))
    tik_api.device_save()
    active_device = {
        "1": 'service/app_alert_check',
        "2": 'mssdk/ri/report',
         "3": 'mssdk/ri/did-iid-update',
         "4": "mssdk/common_setting",
         "5": "mssdk/common_config",
         "6": "mssdk/ri/image",
    }
    for key, value in active_device.items():
        if isinstance(value, dict):
            print(f"Response: {key} -> value")
            print(value)
        else:
            api = tik_api.api_request(value)
            tiktok_auto_request = tik_api.tiktok_auto_request(api)
            print(f"Response: {value} -> value {tiktok_auto_request}")
        print("\n")
    print("\n")
    print(json.dumps(tik_api.config))
