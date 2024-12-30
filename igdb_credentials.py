# Reference: https://api-docs.igdb.com/#breaking-changes

import json
import time
from pathlib import Path

import requests

from igdb_local_secrets import get_igdb_user_key_file_name, load_igdb_user_key

TIMEOUT_IN_SECONDS = 5


def get_igdb_oauth_url() -> str:
    return "https://id.twitch.tv/oauth2/token"


def load_client_params(*, verbose: bool = False) -> dict[str, str | None]:
    igdb_user_key = load_igdb_user_key()

    params = {
        "client_id": igdb_user_key["client_id"],
        "client_secret": igdb_user_key["client_secret"],
        "grant_type": "client_credentials",
    }

    if verbose:
        print(f"Params (#fields={len(params)}): {params}\n")

    return params


def get_default_headers() -> dict[str, str]:
    return {
        "Accept": "application/json",
    }


def get_default_credentials() -> dict[str, str | int]:
    return {
        "access_token": "",
        "expires_in": 0,
        "token_type": "",
    }


def load_credential_headers(*, verbose: bool = False) -> dict[str, str | None]:
    igdb_user_key = load_igdb_user_key()

    headers = get_default_headers()

    headers["Client-ID"] = igdb_user_key["client_id"]

    headers["Authorization"] = "{} {}".format(
        igdb_user_key["token_type"].capitalize(),
        igdb_user_key["access_token"],
    )

    if verbose:
        print(f"Headers (#fields={len(headers)}): {headers}\n")

    return headers


def get_unix_time_stamp() -> int:
    # Reference: https://stackoverflow.com/a/49362936

    unix_time_stamp = time.time()

    return int(unix_time_stamp)


def save_credentials_to_disk(credentials: dict) -> None:
    igdb_user_key: dict[str, int | str | None] = load_igdb_user_key()
    igdb_user_key.update(credentials)

    time_dict: dict[str, int] = {"save_timestamp": get_unix_time_stamp()}
    igdb_user_key.update(time_dict)

    with Path(get_igdb_user_key_file_name()).open("w", encoding="utf-8") as f:
        json.dump(igdb_user_key, f)


def download_latest_credentials(*, verbose: bool = True) -> dict:
    if verbose:
        print("[query] credentials")

    response = requests.post(
        url=get_igdb_oauth_url(),
        headers=get_default_headers(),
        params=load_client_params(),
        timeout=TIMEOUT_IN_SECONDS,
    )

    if response.ok:
        data = response.json()
        save_credentials_to_disk(data)
    else:
        data = get_default_credentials()

    if verbose:
        print(f"Response (#fields={len(data)}): {data}\n")

    return data


if __name__ == "__main__":
    data = download_latest_credentials(verbose=True)
    client_params = load_client_params(verbose=True)
    credential_params = load_credential_headers(verbose=True)
