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
    # name 	                value
    # ====================  =====
    # console 	            1
    # arcade 	            2
    # platform 	            3
    # operating_system 	    4
    # portable_console 	    5
    # computer 	            6

    pc_platform_no = 6

    return pc_platform_no


def get_game_category_no():
    # name 	                value
    # ====================  =====
    # main_game 	        0
    # dlc_addon 	        1
    # expansion 	        2
    # bundle 	            3
    # standalone_expansion 	4

    game_category_no = 0

    return game_category_no


def get_released_status_no():
    # name 	                value
    # ====================  =====
    # released 	            0
    # alpha 	            2
    # beta 	                3
    # early_access 	        4
    # offline 	            5
    # cancelled 	        6

    # Caveat: the release status is often missing from IGDB. Avoid using it for now, or you will get empty responses!

    released_status_no = 0

    return released_status_no


def append_filter_for_igdb_fields(igdb_fields,
                                  filter_name,
                                  filter_value,
                                  use_parenthesis=False):
    where_statement = ' ; where '
    conjunction_statement = ' & '

    if filter_name.startswith('platform'):
        # The filter name can be singular or plural:
        # - 'platforms' when used for games,
        # - 'platform' when used for release dates.
        use_parenthesis = True

    if use_parenthesis:
        # Use parenthesis, e.g. (6), to look for games released on platform n°6, without discarding multi-platform games
        # Reference: https://medium.com/igdb/its-here-the-new-igdb-api-f6ad745b53fe
        statement_to_append = '{} = ({})'.format(
            filter_name,
            filter_value,
        )
    else:
        statement_to_append = '{} = {}'.format(
            filter_name,
            filter_value,
        )

    if where_statement in igdb_fields:
        igdb_fields += conjunction_statement + statement_to_append
    else:
        igdb_fields += where_statement + statement_to_append

    return igdb_fields


def get_igdb_fields_for_games(is_available_on_pc=True,
                              is_a_game=True,
                              enforced_year=None):
    # Reference: https://api-docs.igdb.com/?kotlin#game

    field_separator = ', '

    igdb_fields_for_games = field_separator.join([
        'name',
        'slug',
        'alternative_names',
        'platforms',
        'category',
        'status',
        'first_release_date',
        'release_dates.y',
        'release_dates.human',
    ])  # TODO

    if is_available_on_pc:
        igdb_fields_for_games = append_filter_for_igdb_fields(igdb_fields_for_games,
                                                              'platforms',
                                                              get_pc_platform_no(),
                                                              use_parenthesis=True,
                                                              )

    if is_a_game:
        igdb_fields_for_games = append_filter_for_igdb_fields(igdb_fields_for_games,
                                                              'category',
                                                              get_game_category_no(),
                                                              )

    if enforced_year is not None:
        igdb_fields_for_games = append_filter_for_igdb_fields(igdb_fields_for_games,
                                                              'release_dates.y',
                                                              enforced_year,
                                                              )

    return igdb_fields_for_games


def get_igdb_fields_for_release_dates(is_available_on_pc=True,
                                      enforced_year=None):
    # Reference: https://api-docs.igdb.com/?kotlin#release-date

    field_separator = ', '

    igdb_fields_for_release_dates = field_separator.join([
        'game',
        'platform',
        'date',
        'human',
        'category',
    ])  # TODO

    if is_available_on_pc:
        igdb_fields_for_release_dates = append_filter_for_igdb_fields(igdb_fields_for_release_dates,
                                                                      'platform',
                                                                      get_pc_platform_no(),
                                                                      use_parenthesis=True,
                                                                      )

    if enforced_year is not None:
        igdb_fields_for_release_dates = append_filter_for_igdb_fields(igdb_fields_for_release_dates,
                                                                      'y',
                                                                      enforced_year,
                                                                      )

    return igdb_fields_for_release_dates


def look_up_game_name(game_name,
                      enforced_year=None,
                      is_available_on_pc=True,
                      is_a_game=True,
                      verbose=True):
    if verbose:
        print('[query] Game name: {} ; Year: {} ; PC: {} ; Game: {}'.format(game_name,
                                                                            enforced_year,
                                                                            is_available_on_pc,
                                                                            is_a_game,
                                                                            ))

    url = get_igdb_api_url_for_games()
    headers = get_igdb_request_headers()

    fields_str = get_igdb_fields_for_games(is_available_on_pc=is_available_on_pc,
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
                    is_available_on_pc=True,
                    is_a_game=True,
                    verbose=True):
    if verbose:
        print('[query] Game id: {} ; Year: {} ; PC: {} ; Game: {}'.format(game_id,
                                                                          enforced_year,
                                                                          is_available_on_pc,
                                                                          is_a_game,
                                                                          ))

    url = get_igdb_api_url_for_games()
    headers = get_igdb_request_headers()

    fields_str = get_igdb_fields_for_games(is_available_on_pc=is_available_on_pc,
                                           is_a_game=is_a_game,
                                           enforced_year=enforced_year)

    fields_str = append_filter_for_igdb_fields(fields_str,
                                               'id',
                                               game_id,
                                               )

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
                                         is_available_on_pc=True,
                                         verbose=True):
    if verbose:
        print('[query] Year: {} ; PC: {}'.format(enforced_year,
                                                 is_available_on_pc))

    url = get_igdb_api_url_for_release_dates()
    headers = get_igdb_request_headers()

    fields_str = get_igdb_fields_for_release_dates(is_available_on_pc=is_available_on_pc,
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
    is_available_on_pc = True
    verbose = True

    game_name = 'Red Dead'

    data = look_up_game_name(game_name=game_name,
                             enforced_year=enforced_year,
                             is_available_on_pc=is_available_on_pc,
                             verbose=verbose)

    game_id = 113391

    data = look_up_game_id(game_id=game_id,
                           enforced_year=enforced_year,
                           is_available_on_pc=is_available_on_pc,
                           verbose=verbose)

    data = look_up_games_released_in_given_year(enforced_year=enforced_year,
                                                is_available_on_pc=is_available_on_pc,
                                                verbose=verbose)

    return True


if __name__ == '__main__':
    main()
