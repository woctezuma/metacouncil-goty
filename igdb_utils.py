# Objective: look-up games and release dates on IGDB:
#
# Reference: https://api-docs.igdb.com/?kotlin#endpoints

import datetime
import json

import requests


def get_igdb_api_url(end_point=None):
    igdb_api_url = 'https://api-v3.igdb.com'

    if end_point is not None:
        url_separator = '/'

        if not end_point.startswith(url_separator):
            end_point = url_separator + end_point

        if not end_point.endswith(url_separator):
            end_point += url_separator

        # NB: the end-point should look like '/games/' or '/release_dates/'

        igdb_api_url += end_point

    return igdb_api_url


def get_igdb_api_url_for_games():
    end_point = '/games/'
    igdb_api_url_for_games = get_igdb_api_url(end_point=end_point)

    return igdb_api_url_for_games


def get_igdb_api_url_for_release_dates():
    end_point = '/release_dates/'
    igdb_api_url_for_release_dates = get_igdb_api_url(end_point=end_point)

    return igdb_api_url_for_release_dates


def get_time_stamp_for_year_start(year):
    time_stamp_for_year_start = datetime.datetime(year, 1, 1).timestamp()

    return time_stamp_for_year_start


def get_time_stamp_for_year_end(year):
    time_stamp_for_year_end = get_time_stamp_for_year_start(year=year + 1)

    return time_stamp_for_year_end


def get_igdb_user_key_file_name():
    igdb_user_key_file_name = 'igdb_user_key.json'

    return igdb_user_key_file_name


def load_igdb_user_key():
    with open(get_igdb_user_key_file_name(), 'r') as f:
        igdb_user_key = json.load(f)

    return igdb_user_key


def get_igdb_request_headers():
    igdb_user_key = load_igdb_user_key()

    headers = {
        'user-key': igdb_user_key['user-key'],
        'Accept': 'application/json',
    }

    return headers


def get_igdb_request_params():
    params = {
        'fields': '*',  # It would be better if the fields were explicitly stated (and narrowed down to what is needed)!
        'limit': 10,  # max value is 500
    }

    return params


def get_pc_platform_no():
    pc_platform_no = 6

    return pc_platform_no


def get_game_category_no():
    game_category_no = 0

    return game_category_no


def get_igdb_fields_for_games(enforce_pc_games=True,
                              is_a_game=True,
                              enforced_year=None):
    # Reference: https://api-docs.igdb.com/?kotlin#game

    igdb_fields_for_games = 'name, slug, alternative_names, platforms, category, status, first_release_date, release_dates.y, release_dates.human'  # TODO

    if enforce_pc_games:
        # Use parenthesis, e.g. (6), to look for games released on platform n°6, without discarding multi-platform games
        # Reference: https://medium.com/igdb/its-here-the-new-igdb-api-f6ad745b53fe
        igdb_fields_for_games += ' ; where platforms = ({})'.format(
            get_pc_platform_no(),
        )

    if is_a_game:
        if ' ; where ' in igdb_fields_for_games:
            igdb_fields_for_games += ' & category = {}'.format(
                get_game_category_no(),
            )
        else:
            igdb_fields_for_games += ' ; where category = {}'.format(
                get_game_category_no(),
            )

    if enforced_year is not None:
        if ' ; where ' in igdb_fields_for_games:
            igdb_fields_for_games += ' & release_dates.y = {}'.format(
                enforced_year,
            )
        else:
            igdb_fields_for_games += ' ; where release_dates.y = {}'.format(
                enforced_year,
            )

    return igdb_fields_for_games


def get_igdb_fields_for_release_dates(enforce_pc_games=True,
                                      enforced_year=None):
    # Reference: https://api-docs.igdb.com/?kotlin#release-date

    igdb_fields_for_release_dates = 'game, platform, date, human'  # TODO

    if enforce_pc_games:
        igdb_fields_for_release_dates += ' ; where platform = ({})'.format(
            get_pc_platform_no(),
        )

    if enforced_year is not None:
        if ' ; where ' in igdb_fields_for_release_dates:
            igdb_fields_for_release_dates += ' & y = {}'.format(
                enforced_year,
            )
        else:
            igdb_fields_for_release_dates += ' ; where y = {}'.format(
                enforced_year,
            )

    return igdb_fields_for_release_dates


def look_up_game_name(game_name,
                      enforced_year=None,
                      enforce_pc_games=True,
                      is_a_game=True,
                      verbose=True):
    if verbose:
        print('[query] Game name: {} ; Year: {} ; PC: {} ; Game: {}'.format(game_name,
                                                                            enforced_year,
                                                                            enforce_pc_games,
                                                                            is_a_game,
                                                                            ))

    url = get_igdb_api_url_for_games()
    headers = get_igdb_request_headers()

    fields_str = get_igdb_fields_for_games(enforce_pc_games=enforce_pc_games,
                                           is_a_game=is_a_game,
                                           enforced_year=enforced_year)

    params = get_igdb_request_params()
    params['fields'] = fields_str

    params['search'] = game_name

    response = requests.post(
        url=url,
        headers=headers,
        params=params,
    )

    data = response.json()

    if verbose:
        print('Response: {}\n'.format(data))

    return data


def look_up_game_id(game_id,
                    enforced_year=None,
                    enforce_pc_games=True,
                    is_a_game=True,
                    verbose=True):
    if verbose:
        print('[query] Game id: {} ; Year: {} ; PC: {} ; Game: {}'.format(game_id,
                                                                          enforced_year,
                                                                          enforce_pc_games,
                                                                          is_a_game,
                                                                          ))

    url = get_igdb_api_url_for_games()
    headers = get_igdb_request_headers()

    fields_str = get_igdb_fields_for_games(enforce_pc_games=enforce_pc_games,
                                           is_a_game=is_a_game,
                                           enforced_year=enforced_year)

    if ' ; where ' in fields_str:
        fields_str += ' & id = ({})'.format(game_id)
    else:
        fields_str += ' ; where id = ({})'.format(game_id)

    params = get_igdb_request_params()
    params['fields'] = fields_str

    response = requests.post(
        url=url,
        headers=headers,
        params=params,
    )

    data = response.json()

    if verbose:
        print('Response: {}\n'.format(data))

    return data


def look_up_games_released_in_given_year(enforced_year,
                                         enforce_pc_games=True,
                                         verbose=True):
    if verbose:
        print('[query] Year: {} ; PC: {}'.format(enforced_year,
                                                 enforce_pc_games))

    url = get_igdb_api_url_for_release_dates()
    headers = get_igdb_request_headers()

    fields_str = get_igdb_fields_for_release_dates(enforce_pc_games=enforce_pc_games,
                                                   enforced_year=enforced_year)

    params = get_igdb_request_params()
    params['fields'] = fields_str

    response = requests.post(
        url=url,
        headers=headers,
        params=params,
    )

    data = response.json()

    if verbose:
        print('Response: {}\n'.format(data))

    return data


def main():
    enforced_year = 2019
    enforce_pc_games = True
    verbose = True

    game_name = 'Red Dead'

    data = look_up_game_name(game_name=game_name,
                             enforced_year=enforced_year,
                             enforce_pc_games=enforce_pc_games,
                             verbose=verbose)

    game_id = 113391

    data = look_up_game_id(game_id=game_id,
                           enforced_year=enforced_year,
                           enforce_pc_games=enforce_pc_games,
                           verbose=verbose)

    data = look_up_games_released_in_given_year(enforced_year=enforced_year,
                                                enforce_pc_games=enforce_pc_games,
                                                verbose=verbose)

    return True


if __name__ == '__main__':
    main()
