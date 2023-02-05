import time

import requests

from igdb_credentials import download_latest_credentials, load_credential_headers
from igdb_local_secrets import load_igdb_user_key
from igdb_utils import (
    append_filter_for_igdb_fields,
    format_list_of_platforms,
    format_release_dates_for_manual_display,
    get_igdb_api_url,
    get_igdb_api_url_for_games,
    get_igdb_api_url_for_release_dates,
    get_igdb_fields_for_games,
    get_igdb_fields_for_release_dates,
    get_igdb_request_params,
)


def get_igdb_rate_limits():
    # Reference: https://api-docs.igdb.com/

    igdb_rate_limits = {
        # There is a rate limit of 4 requests per second.
        # If you go over this limit you will receive a response with status code 429 Too Many Requests.
        "num_requests_per_second": 4,
        # Alternatively, encode this piece of information as such:
        "num_requests": 4,
        "num_seconds": 1,
        # You are able to have up to 8 open requests at any moment in time.
        # This can occur if requests take longer than 1 second to respond when multiple requests are being made.
        "max_num_open_requests": 8,
    }

    return igdb_rate_limits


def wait_for_cooldown(num_requests, start_time, igdb_rate_limits=None):
    if igdb_rate_limits is None:
        igdb_rate_limits = get_igdb_rate_limits()

    if num_requests % igdb_rate_limits["num_requests"] == 0:
        elapsed_time = time.time() - start_time

        cooldown_duration = igdb_rate_limits["num_seconds"] - elapsed_time
        if cooldown_duration > 0:
            time.sleep(cooldown_duration)
        new_start_time = time.time()
    else:
        new_start_time = start_time

    return new_start_time


def get_igdb_request_headers():
    igdb_user_key = load_igdb_user_key()

    # For IGDB API version 3:
    headers = {
        "user-key": igdb_user_key["user-key"],
        "Accept": "application/json",
    }

    # For IGDB API version 4:
    headers_for_igdb_v4 = load_credential_headers()
    headers.update(headers_for_igdb_v4)

    return headers


def look_up_game_name(
    game_name,
    enforced_year=None,
    must_be_available_on_pc=True,
    must_be_a_game=True,
    enforced_platform=None,
    enforced_game_category=None,
    year_constraint="equality",
    verbose=True,
):
    if verbose:
        print(
            "[query] Game name: {} ; Year: {} ({}) ; PC: {} ; Game: {} ; Platform: {} ; Category: {}".format(
                game_name,
                enforced_year,
                year_constraint,
                must_be_available_on_pc,
                must_be_a_game,
                enforced_platform,
                enforced_game_category,
            ),
        )

    url = get_igdb_api_url_for_games()
    headers = get_igdb_request_headers()

    fields_str = get_igdb_fields_for_games(
        must_be_available_on_pc=must_be_available_on_pc,
        must_be_a_game=must_be_a_game,
        enforced_platform=enforced_platform,
        enforced_game_category=enforced_game_category,
        enforced_year=enforced_year,
        year_constraint=year_constraint,
    )

    params = get_igdb_request_params()
    params["fields"] = fields_str

    params["search"] = game_name

    response = requests.post(
        url=url,
        headers=headers,
        params=params,
    )

    data = response.json()

    if verbose:
        print(f"Response (#games={len(data)}): {data}\n")

    return data


def look_up_game_id(
    game_id,
    enforced_year=None,
    must_be_available_on_pc=True,
    must_be_a_game=True,
    enforced_platform=None,
    enforced_game_category=None,
    year_constraint="equality",
    verbose=True,
):
    if verbose:
        print(
            "[query] Game id: {} ; Year: {} ; PC: {} ; Game: {} ; Platform: {} ; Category: {}".format(
                game_id,
                enforced_year,
                must_be_available_on_pc,
                must_be_a_game,
                enforced_platform,
                enforced_game_category,
            ),
        )

    url = get_igdb_api_url_for_games()
    headers = get_igdb_request_headers()

    fields_str = get_igdb_fields_for_games(
        must_be_available_on_pc=must_be_available_on_pc,
        must_be_a_game=must_be_a_game,
        enforced_platform=enforced_platform,
        enforced_game_category=enforced_game_category,
        enforced_year=enforced_year,
        year_constraint=year_constraint,
    )

    fields_str = append_filter_for_igdb_fields(
        fields_str,
        "id",
        game_id,
    )

    params = get_igdb_request_params()
    params["fields"] = fields_str

    response = requests.post(
        url=url,
        headers=headers,
        params=params,
    )

    data = response.json()

    if verbose:
        print(f"Response (#games={len(data)}): {data}\n")

    return data


def look_up_games_released_in_given_year(
    enforced_year,
    must_be_available_on_pc=True,
    enforced_platform=None,
    verbose=True,
):
    if verbose:
        print(
            "[query] Year: {} ; PC: {} ; Platform: {}".format(
                enforced_year,
                must_be_available_on_pc,
                enforced_platform,
            ),
        )

    url = get_igdb_api_url_for_release_dates()
    headers = get_igdb_request_headers()

    fields_str = get_igdb_fields_for_release_dates(
        must_be_available_on_pc=must_be_available_on_pc,
        enforced_platform=enforced_platform,
        enforced_year=enforced_year,
    )

    params = get_igdb_request_params()
    params["fields"] = fields_str

    response = requests.post(
        url=url,
        headers=headers,
        params=params,
    )

    data = response.json()

    if verbose:
        print(f"Response (#games={len(data)}): {data}\n")

    return data


def download_list_of_platforms(verbose=True):
    if verbose:
        print("[query] all possible platforms")

    url = get_igdb_api_url(end_point="platforms")
    headers = get_igdb_request_headers()

    fields_str = "abbreviation, alternative_name, category, name, slug, summary, url"

    params = get_igdb_request_params()
    params["fields"] = fields_str
    params["limit"] = 500

    response = requests.post(
        url=url,
        headers=headers,
        params=params,
    )

    data = response.json()

    if verbose:
        print(f"Response (#platforms={len(data)}): {data}\n")

    return data


def manual_look_up(
    input,
    must_be_a_game=False,
    must_be_available_on_pc=False,
    verbose=True,
):
    # Input can be:
    # - either a query game name,
    # - or an IGDB id.
    #
    # NB: This is a quality-of-lie utility function to manually query IGDB, in order to figure out:
    # - fixes to name matching,
    # - and database extensions.

    try:
        input = int(input)

        data = look_up_game_id(
            input,
            must_be_a_game=must_be_a_game,
            must_be_available_on_pc=must_be_available_on_pc,
        )
    except ValueError:
        data = look_up_game_name(
            input,
            must_be_a_game=must_be_a_game,
            must_be_available_on_pc=must_be_available_on_pc,
        )

    if verbose:
        for element in data:
            release_years_as_str = format_release_dates_for_manual_display(element)

            print(
                "{}\t{}\t({})".format(
                    element["id"],
                    element["name"],
                    release_years_as_str,
                ),
            )

    return data


def main():
    enforced_year = 2019
    must_be_available_on_pc = True
    must_be_a_game = True
    verbose = True

    # Ensure credentials are up-to-date
    download_latest_credentials(verbose=verbose)

    game_name = "Red Dead"

    data = look_up_game_name(
        game_name=game_name,
        enforced_year=enforced_year,
        must_be_available_on_pc=must_be_available_on_pc,
        must_be_a_game=must_be_a_game,
        verbose=verbose,
    )

    game_id = 113391

    data = look_up_game_id(
        game_id=game_id,
        enforced_year=enforced_year,
        must_be_available_on_pc=must_be_available_on_pc,
        must_be_a_game=must_be_a_game,
        verbose=verbose,
    )

    data = look_up_games_released_in_given_year(
        enforced_year=enforced_year,
        must_be_available_on_pc=must_be_available_on_pc,
        verbose=verbose,
    )

    raw_data_platforms = download_list_of_platforms(verbose=verbose)
    formatted_data_platforms = format_list_of_platforms(
        raw_data_platforms,
        verbose=verbose,
    )

    return True


if __name__ == "__main__":
    main()
