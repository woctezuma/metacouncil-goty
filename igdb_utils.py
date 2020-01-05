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


def get_pc_platform_range():
    pc_platform_range = []

    pc_platform_range.append(get_pc_platform_no())

    return pc_platform_range


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


def get_steam_service_no():
    # name 	                value
    # ====================  =====
    # steam 	            1
    # gog 	                5
    # youtube 	            10
    # microsoft 	        11
    # apple 	            13
    # twitch 	            14
    # android 	            15

    steam_service_no = 1

    return steam_service_no


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


def get_igdb_fields_for_games(must_be_available_on_pc=True,
                              must_be_a_game=True,
                              enforced_platform=None,
                              enforced_game_category=None,
                              enforced_year=None):
    # Reference: https://api-docs.igdb.com/?kotlin#game

    field_separator = ', '

    igdb_fields_for_games = field_separator.join([
        'name',
        'slug',
        'platforms',
        'category',
        'release_dates.y',
        'release_dates.platform',
        'release_dates.human',
        'external_games.category',
        'external_games.name',
        'external_games.uid',
        'external_games.url',
        'external_games.year',
        'alternative_names.comment',
        'alternative_names.name',
    ])

    if must_be_available_on_pc or enforced_platform is not None:

        if enforced_platform is None:
            enforced_platform = get_pc_platform_no()

        igdb_fields_for_games = append_filter_for_igdb_fields(igdb_fields_for_games,
                                                              'platforms',
                                                              enforced_platform,
                                                              use_parenthesis=True,
                                                              )

    if must_be_a_game or enforced_game_category is not None:

        if enforced_game_category is None:
            enforced_game_category = get_game_category_no()

        igdb_fields_for_games = append_filter_for_igdb_fields(igdb_fields_for_games,
                                                              'category',
                                                              enforced_game_category,
                                                              )

    if enforced_year is not None:
        igdb_fields_for_games = append_filter_for_igdb_fields(igdb_fields_for_games,
                                                              'release_dates.y',
                                                              enforced_year,
                                                              )

    return igdb_fields_for_games


def get_igdb_fields_for_release_dates(must_be_available_on_pc=True,
                                      enforced_platform=None,
                                      enforced_year=None):
    # Reference: https://api-docs.igdb.com/?kotlin#release-date

    field_separator = ', '

    igdb_fields_for_release_dates = field_separator.join([
        'game.name',
        'game.slug',
        'game.platforms',
        'game.category',
        'platform',
        'human',
        'y',
    ])

    if must_be_available_on_pc or enforced_platform is not None:

        if enforced_platform is None:
            enforced_platform = get_pc_platform_no()

        igdb_fields_for_release_dates = append_filter_for_igdb_fields(igdb_fields_for_release_dates,
                                                                      'platform',
                                                                      enforced_platform,
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
                      must_be_available_on_pc=True,
                      must_be_a_game=True,
                      enforced_platform=None,
                      enforced_game_category=None,
                      verbose=True):
    if verbose:
        print('[query] Game name: {} ; Year: {} ; PC: {} ; Game: {} ; Platform: {} ; Category: {}'.format(
            game_name,
            enforced_year,
            must_be_available_on_pc,
            must_be_a_game,
            enforced_platform,
            enforced_game_category,
        ))

    url = get_igdb_api_url_for_games()
    headers = get_igdb_request_headers()

    fields_str = get_igdb_fields_for_games(must_be_available_on_pc=must_be_available_on_pc,
                                           must_be_a_game=must_be_a_game,
                                           enforced_platform=enforced_platform,
                                           enforced_game_category=enforced_game_category,
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
        print('Response (#games={}): {}\n'.format(
            len(data),
            data
        ))

    return data


def look_up_game_id(game_id,
                    enforced_year=None,
                    must_be_available_on_pc=True,
                    must_be_a_game=True,
                    enforced_platform=None,
                    enforced_game_category=None,
                    verbose=True):
    if verbose:
        print('[query] Game id: {} ; Year: {} ; PC: {} ; Game: {} ; Platform: {} ; Category: {}'.format(
            game_id,
            enforced_year,
            must_be_available_on_pc,
            must_be_a_game,
            enforced_platform,
            enforced_game_category,
        ))

    url = get_igdb_api_url_for_games()
    headers = get_igdb_request_headers()

    fields_str = get_igdb_fields_for_games(must_be_available_on_pc=must_be_available_on_pc,
                                           must_be_a_game=must_be_a_game,
                                           enforced_platform=enforced_platform,
                                           enforced_game_category=enforced_game_category,
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
        print('Response (#games={}): {}\n'.format(
            len(data),
            data
        ))

    return data


def look_up_games_released_in_given_year(enforced_year,
                                         must_be_available_on_pc=True,
                                         enforced_platform=None,
                                         verbose=True):
    if verbose:
        print('[query] Year: {} ; PC: {} ; Platform: {}'.format(
            enforced_year,
            must_be_available_on_pc,
            enforced_platform,
        ))

    url = get_igdb_api_url_for_release_dates()
    headers = get_igdb_request_headers()

    fields_str = get_igdb_fields_for_release_dates(must_be_available_on_pc=must_be_available_on_pc,
                                                   enforced_platform=enforced_platform,
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
        print('Response (#games={}): {}\n'.format(
            len(data),
            data
        ))

    return data


def download_list_of_platforms(verbose=True):
    url = get_igdb_api_url(end_point='platforms')
    headers = get_igdb_request_headers()

    fields_str = 'abbreviation, alternative_name, category, name, slug, summary, url'

    params = get_igdb_request_params()
    params['fields'] = fields_str
    params['limit'] = 500

    response = requests.post(
        url=url,
        headers=headers,
        params=params,
    )

    data = response.json()

    if verbose:
        print('Response (#platforms={}): {}\n'.format(
            len(data),
            data
        ))

    return data


def format_list_of_platforms(raw_data_platforms,
                             verbose=True):
    formatted_data_platforms = dict()

    sorted_data_platforms = sorted(raw_data_platforms,
                                   key=lambda x: x['id'])

    for e in sorted_data_platforms:
        id = e['id']

        formatted_data_platforms[id] = dict()
        formatted_data_platforms[id]['slug'] = e['slug']
        formatted_data_platforms[id]['slug'] = e['name']

        try:
            formatted_data_platforms[id]['category'] = e['category']
        except KeyError:
            formatted_data_platforms[id]['category'] = None

    if verbose:
        for id in formatted_data_platforms:
            category = formatted_data_platforms[id]['category']

            if category == get_pc_platform_no():
                slug = formatted_data_platforms[id]['slug']

                print('Category: {} ; ID: {} ; Slug: {}'.format(category,
                                                                id,
                                                                slug,
                                                                ))

    return formatted_data_platforms


def main():
    enforced_year = 2019
    must_be_available_on_pc = True
    must_be_a_game = True
    verbose = True

    game_name = 'Red Dead'

    data = look_up_game_name(game_name=game_name,
                             enforced_year=enforced_year,
                             must_be_available_on_pc=must_be_available_on_pc,
                             must_be_a_game=must_be_a_game,
                             verbose=verbose)

    game_id = 113391

    data = look_up_game_id(game_id=game_id,
                           enforced_year=enforced_year,
                           must_be_available_on_pc=must_be_available_on_pc,
                           must_be_a_game=must_be_a_game,
                           verbose=verbose)

    data = look_up_games_released_in_given_year(enforced_year=enforced_year,
                                                must_be_available_on_pc=must_be_available_on_pc,
                                                verbose=verbose)

    raw_data_platforms = download_list_of_platforms(verbose=verbose)
    formatted_data_platforms = format_list_of_platforms(raw_data_platforms,
                                                        verbose=verbose)

    return True


if __name__ == '__main__':
    main()
