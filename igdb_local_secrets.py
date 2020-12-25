import json


def get_igdb_user_key_file_name():
    igdb_user_key_file_name = "igdb_user_key.json"

    return igdb_user_key_file_name


def load_igdb_user_key():
    file_name = get_igdb_user_key_file_name()

    try:
        with open(file_name, "r") as f:
            igdb_user_key = json.load(f)
    except FileNotFoundError:
        print("IGDB user secret key {} not found.".format(file_name))
        igdb_user_key = {
            # For version 3 of IGDB API:
            "user-key": None,
            # For version 4 of IGDB API:
            "client_id": None,
            "client_secret": None,
        }

    return igdb_user_key
