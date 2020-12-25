# Reference: https://api-docs.igdb.com/#breaking-changes

import json

import requests

from igdb_utils import (
    load_igdb_user_key,
    get_igdb_user_key_file_name,
)


def get_igdb_oauth_url():
    igdb_oauth_url = "https://id.twitch.tv/oauth2/token"

    return igdb_oauth_url


def load_client_params(verbose=False):
    igdb_user_key = load_igdb_user_key()

    params = {
        "client_id": igdb_user_key["client_id"],
        "client_secret": igdb_user_key["client_secret"],
        "grant_type": "client_credentials",
    }

    if verbose:
        print("Params (#fields={}): {}\n".format(len(params), params))

    return params


def get_default_headers():
    headers = {
        "Accept": "application/json",
    }

    return headers


def get_default_credentials():
    data = {
        "access_token": "",
        "expires_in": 0,
        "token_type": "",
    }

    return data


def load_credential_headers(verbose=False):
    igdb_user_key = load_igdb_user_key()

    headers = get_default_headers()

    headers["Client-ID"] = igdb_user_key["client_id"]

    headers["Authorization"] = "{} {}".format(
        igdb_user_key["token_type"].capitalize(), igdb_user_key["access_token"]
    )

    if verbose:
        print("Headers (#fields={}): {}\n".format(len(headers), headers))

    return headers


def save_credentials_to_disk(credentials):
    igdb_user_key = load_igdb_user_key()
    igdb_user_key.update(credentials)

    with open(get_igdb_user_key_file_name(), "w") as f:
        json.dump(igdb_user_key, f)

    return


def download_latest_credentials(verbose=True):
    response = requests.post(
        url=get_igdb_oauth_url(),
        headers=get_default_headers(),
        params=load_client_params(),
    )

    if response.ok:
        data = response.json()
        save_credentials_to_disk(data)
    else:
        data = get_default_credentials()

    if verbose:
        print("Response (#fields={}): {}\n".format(len(data), data))

    return data


if __name__ == "__main__":
    # data = download_latest_credentials(verbose=True)
    client_params = load_client_params(verbose=True)
    credential_params = load_credential_headers(verbose=True)
