import json
import os
from pathlib import Path


def get_environment() -> dict:
    return os.environ.copy()


def get_igdb_user_key_file_name() -> str:
    return "igdb_user_key.json"


def load_igdb_user_key() -> dict:
    file_name = get_igdb_user_key_file_name()

    environment = get_environment()

    try:
        with Path(file_name).open(encoding="utf-8") as f:
            igdb_user_key = json.load(f)
    except FileNotFoundError:
        print(f"IGDB user secret key {file_name} not found.")
        igdb_user_key = {
            # For version 3 of IGDB API:
            "user-key": environment.get("IGDB_USER_KEY", ""),
            # For version 4 of IGDB API:
            "client_id": environment.get("IGDB_CLIENT_ID", ""),
            "client_secret": environment.get("IGDB_CLIENT_SECRET", ""),
            # The following are temporary credentials which should be obtained with the pair (id, secret) above:
            "token_type": "",
            "access_token": "",
        }

    return igdb_user_key
