import json


def get_igdb_user_key_file_name() -> str:
    return "igdb_user_key.json"


def load_igdb_user_key():
    file_name = get_igdb_user_key_file_name()

    try:
        with open(file_name, encoding="utf-8") as f:
            igdb_user_key = json.load(f)
    except FileNotFoundError:
        print(f"IGDB user secret key {file_name} not found.")
        igdb_user_key = {
            # For version 3 of IGDB API:
            "user-key": None,
            # For version 4 of IGDB API:
            "client_id": None,
            "client_secret": None,
            # The following are temporary credentials which should be obtained with the pair (id, secret) above:
            "token_type": "",
            "access_token": "",
        }

    return igdb_user_key
