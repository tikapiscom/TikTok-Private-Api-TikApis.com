import random
import json
from AndroidTikApis import AndroidTikApis
from utilities import Utils


def generate_random_email():
    return f"{Utils.rand_str(random.randint(10, 18))}{Utils.random_mail()}"


def generate_random_device(email):
    return {
        "imagel_url": "https://fastly.picsum.photos/id/130/536/354.jpg?hmac=a3CMMZgFMD60VsyMXoXbMllYckSrfgS3Dr5pUzkoZqs",
        "signature": f"hey ! {Utils.rand_str(random.randint(10, 18))}",
        "bio_url": "tdsadsa",
        "nickname": f"hey!! {Utils.rand_str(random.randint(10, 18))}",
        "login_name": Utils.rand_str(random.randint(10, 18)),
        "unique_id": Utils.rand_str(random.randint(10, 18)),
        "account": {
            "email": email,
            "password": Utils.generate_random_password(),
            "mobile": "",
            "code": ""
        },
        "conversation": {
            "to_user_id": "107955",
            "message": "how are you",
            "video_id": "7353002700935679278"
        },
        "comment": {
            "video_id": "7353002700935679278",
            "text": f"hey {random.randint(5,888)}"
        },
    }


def process_device(method_mapping):
    for method_name, method in method_mapping.items():
        print(f"{method_name}: {method()}")

# The service_account_register function creates accounts over the service with a 99% success rate. The account_register, on the other hand, creates an account locally using a proxy address.


def main():
    api_methods = [
        ("account_register", "account_register"),
        # ("service_account_register", "service_account_register"),
        ("uniqueid_check", "uniqueid_check"),
        ("signature", "signature"),
        ("bio_url", "bio_url"),
        ("comment", "comment"),
        ("nickname", "nickname"),
        ("login_name", "login_name"),
        ("user_image_upload", "user_image_upload"),
        ("conversation_create", "conversation_create"),
        ("text_send", "text_send"),
        ("video_send", "video_send"),
        ("follow", "follow"),
        ("like", "digg")
    ]

    json_data_list = Utils().random_device_(1)
    email = generate_random_email()

    for device in json_data_list:
        device.update(generate_random_device(email))
        tik_api = AndroidTikApis(**device)
        method_mapping = {method_name: getattr(
            tik_api, method_name) for method_name, method_name in api_methods}
        process_device(method_mapping)


if __name__ == "__main__":
    main()
