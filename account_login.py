from AndroidTikApis import AndroidTikApis
from utilities import Utils




json_data_list = Utils().random_device_(1)
for device in json_data_list:
    account = {
        "account": {
            # "email" : "example@gmail.com",
            "username": "asdsaddassad",
            "password": "@password@",
        },
        "conversation": {
            "to_user_id": "107955",
            "message": "how are you",
            "video_id": ""
        },
    }
    device.update(account)
    tik_api = AndroidTikApis(**device)
    login = tik_api.login()
    print(login)
