from AndroidTikApis import AndroidTikApis
from utilities import Utils

json_data_list = Utils().random_device_(1)
for device in json_data_list:
    account = {
        "account": {
            "mobile": "+1",
        }
    }
    device.update(account)
    tik_api = AndroidTikApis(**device)
    sms_send_code = tik_api.sms_send_code()
    if sms_send_code.get("message", "") == 'success':
        print("Code sent successfully!")
        code = input("Please enter the received code: ")
        device["account"].update({"code": code})
        sms_login_only = tik_api.sms_login_only()
        print(sms_login_only)
    else:
        print(sms_send_code)
