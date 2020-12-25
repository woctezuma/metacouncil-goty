import requests

from igdb_utils import (
    get_igdb_api_url_for_games,
    get_igdb_request_headers,
    get_igdb_fields_for_games,
    get_igdb_request_params,
    append_filter_for_igdb_fields,
    get_igdb_api_url,
    get_igdb_api_url_for_release_dates,
    get_igdb_fields_for_release_dates,
    format_release_dates_for_manual_display,
    format_list_of_platforms,
)


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
            )
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
        print("Response (#games={}): {}\n".format(len(data), data))

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
            )
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
        print("Response (#games={}): {}\n".format(len(data), data))

    return data


def look_up_games_released_in_given_year(
    enforced_year, must_be_available_on_pc=True, enforced_platform=None, verbose=True
):
    if verbose:
        print(
            "[query] Year: {} ; PC: {} ; Platform: {}".format(
                enforced_year,
                must_be_available_on_pc,
                enforced_platform,
            )
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
        print("Response (#games={}): {}\n".format(len(data), data))

    return data


def download_list_of_platforms(verbose=True):
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
        print("Response (#platforms={}): {}\n".format(len(data), data))

    return data


def manual_look_up(
    input, must_be_a_game=False, must_be_available_on_pc=False, verbose=True
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
                )
            )

    return data


def main():
    enforced_year = 2019
    must_be_available_on_pc = True
    must_be_a_game = True
    verbose = True

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
        raw_data_platforms, verbose=verbose
    )

    return True


if __name__ == "__main__":
    main()
