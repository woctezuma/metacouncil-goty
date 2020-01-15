from disqualify_vote import get_hard_coded_noisy_votes
from extend_igdb import extend_both_igdb_databases
from extend_steamspy import load_extended_steamspy_database
from igdb_databases import load_igdb_local_database, load_igdb_match_database
from igdb_databases import save_igdb_local_database, save_igdb_match_database
from igdb_utils import get_steam_service_no, get_pc_platform_no
from igdb_utils import look_up_game_name, get_pc_platform_range
from load_ballots import load_ballots


def get_link_to_igdb_website(igdb_id,
                             igdb_local_database,
                             hide_dummy_app_id=True):
    igdb_base_url = 'https://www.igdb.com/games/'

    igdb_data = igdb_local_database[igdb_id]
    slug = igdb_data['slug']

    if int(igdb_id) > 0:
        link_to_store = '[URL=' + igdb_base_url + slug + '/]' + igdb_id + '[/URL]'
    else:
        if hide_dummy_app_id:
            link_to_store = 'n/a'
        else:
            link_to_store = igdb_id
    return link_to_store


def get_igdb_human_release_dates(igdb_id,
                                 igdb_local_database):
    igdb_data = igdb_local_database[igdb_id]

    try:
        human_release_dates = set(
            date['human']
            for date in igdb_data['release_dates']
            if 'human' in date and (date['platform'] in get_pc_platform_range())
        )
    except KeyError:
        # Unknown release date
        human_release_dates = [None]

    if len(human_release_dates) > 0:
        human_release_date_to_remember = max(human_release_dates)
    else:
        human_release_date_to_remember = None

    return human_release_dates, human_release_date_to_remember


def get_igdb_release_years(igdb_data,
                           target_release_year=None):
    try:
        release_years = set(
            date['y']
            for date in igdb_data['release_dates']
            if 'y' in date and (date['platform'] in get_pc_platform_range())
        )
    except KeyError:
        # Unknown release date
        release_years = [None]

    year_to_remember = -1

    if target_release_year is not None:
        target_release_year_as_int = int(target_release_year)

        if len(release_years) > 0:
            if target_release_year_as_int in release_years:
                year_to_remember = target_release_year_as_int
            else:
                the_most_recent_date = max(release_years)
                year_to_remember = the_most_recent_date

                if year_to_remember is None:
                    year_to_remember = -1

    return release_years, year_to_remember


def format_game_name_for_igdb(raw_name):
    formatted_game_name_for_igdb = raw_name
    formatted_game_name_for_igdb = formatted_game_name_for_igdb.replace('®', ' ')
    formatted_game_name_for_igdb = formatted_game_name_for_igdb.replace('~', ' ')

    return formatted_game_name_for_igdb


def match_names_with_igdb(raw_votes,
                          release_year=None):
    seen_game_names = set()
    igdb_match_database = dict()
    igdb_local_database = dict()

    steamspy_database = load_extended_steamspy_database()
    noisy_votes = get_hard_coded_noisy_votes()

    for voter in raw_votes.keys():
        for raw_name in raw_votes[voter]['goty_preferences'].values():
            if raw_name not in seen_game_names:
                seen_game_names.add(raw_name)

                if raw_name != '' and (raw_name not in noisy_votes):
                    formatted_game_name_for_igdb = format_game_name_for_igdb(raw_name)

                    igdb_matches = look_up_game_name(game_name=formatted_game_name_for_igdb,
                                                     enforced_year=release_year)

                    try:
                        igdb_best_match = igdb_matches[0]
                    except IndexError:
                        print('Relaxing the year constraint for {}'.format(raw_name))

                        igdb_matches = look_up_game_name(game_name=raw_name,
                                                         enforced_year=None)

                    igdb_matched_ids = []

                    for element in igdb_matches:
                        igdb_id = element['id']
                        igdb_data = element

                        igdb_matched_ids.append(igdb_id)

                        igdb_local_database[igdb_id] = igdb_data

                    # Caveat: For now, matches returned by match_names_with_igdb() does not have the same structure as
                    #         matches returned by precompute_matches(). cf. transform_structure_of_matches()
                    igdb_match_database[raw_name] = igdb_matched_ids

    return igdb_match_database, igdb_local_database


def print_igdb_matches(igdb_match_database,
                       igdb_local_database,
                       constrained_release_year=None):
    sorted_input_names = sorted(igdb_match_database.keys())

    for raw_name in sorted_input_names:
        igdb_matched_ids = igdb_match_database[raw_name]

        try:
            igdb_best_matched_id = igdb_matched_ids[0]
        except IndexError:
            igdb_best_matched_id = None

        if igdb_best_matched_id is not None:
            igdb_data = igdb_local_database[str(igdb_best_matched_id)]

            release_years, year_to_remember = get_igdb_release_years(igdb_data,
                                                                     target_release_year=constrained_release_year)

            if len(release_years) > 1:
                displayed_release_years = sorted(release_years)
                print('[!]\tSeveral release years are found for {}.'.format(raw_name))
            else:
                displayed_release_years = list(release_years)[0]

            if constrained_release_year is not None:
                if all(year != int(constrained_release_year) for year in release_years):
                    print('[!]\tRelease year(s) ({}) do not match the ballot year ({}) for {}.'.format(
                        displayed_release_years,
                        constrained_release_year,
                        raw_name,
                    ))

            print('\t{} ---> IGDB id: {}\t;\t{} ({})'.format(raw_name,
                                                             igdb_data['id'],
                                                             igdb_data['name'],
                                                             displayed_release_years,
                                                             ))
        else:
            print('[X]\t{}'.format(raw_name))

    return


def download_igdb_local_databases(ballots,
                                  release_year=None,
                                  apply_hard_coded_extension_and_fixes=True):
    igdb_match_database, igdb_local_database = match_names_with_igdb(ballots,
                                                                     release_year=release_year)

    # Save data before applying any hard-coded change

    save_igdb_match_database(data=igdb_match_database,
                             release_year=release_year)

    save_igdb_local_database(data=igdb_local_database,
                             release_year=release_year)

    # Apply hard-coded changes: i) database extension and ii) fixes to name matching

    if apply_hard_coded_extension_and_fixes:
        igdb_match_database, igdb_local_database = extend_both_igdb_databases(release_year=release_year,
                                                                              igdb_match_database=igdb_match_database,
                                                                              igdb_local_database=igdb_local_database)

    return igdb_match_database, igdb_local_database


def load_igdb_local_databases(ballots,
                              release_year=None,
                              apply_hard_coded_extension_and_fixes=True,
                              verbose=False):
    try:
        igdb_match_database = load_igdb_match_database(release_year=release_year)

        igdb_local_database = load_igdb_local_database(release_year=release_year)

    except FileNotFoundError:
        igdb_match_database, igdb_local_database = download_igdb_local_databases(ballots,
                                                                                 release_year=release_year,
                                                                                 apply_hard_coded_extension_and_fixes=apply_hard_coded_extension_and_fixes)

    # Apply hard-coded changes: i) database extension and ii) fixes to name matching

    if apply_hard_coded_extension_and_fixes:
        igdb_match_database, igdb_local_database = extend_both_igdb_databases(release_year=release_year,
                                                                              igdb_match_database=igdb_match_database,
                                                                              igdb_local_database=igdb_local_database)

    if verbose:
        print_igdb_matches(igdb_match_database,
                           igdb_local_database,
                           constrained_release_year=release_year)

    return igdb_match_database, igdb_local_database


def transform_structure_of_matches(igdb_match_database,
                                   igdb_local_database):
    # Retro-compatibility with code written for SteamSpy

    matches = dict()

    for raw_name in igdb_match_database.keys():
        igdb_matched_ids = [
            str(igdb_id)
            for igdb_id in igdb_match_database[raw_name]
        ]

        igdb_matched_pc_release_dates = []
        for igdb_id_as_str in igdb_matched_ids:
            try:
                release_dates = igdb_local_database[igdb_id_as_str]['release_dates']
            except KeyError:
                continue
            for element in release_dates:
                if element['platform'] == get_pc_platform_no():
                    release_date = element['human']
                    igdb_matched_pc_release_dates.append(release_date)

        steam_matched_ids = []
        for igdb_id_as_str in igdb_matched_ids:
            try:
                external_games = igdb_local_database[igdb_id_as_str]['external_games']
            except KeyError:
                continue
            for element in external_games:
                if element['category'] == get_steam_service_no():
                    steam_app_id = element['uid']
                    steam_matched_ids.append(steam_app_id)

        igdb_matched_slugs = [
            igdb_local_database[igdb_id_as_str]['slug']
            for igdb_id_as_str in igdb_matched_ids
        ]

        igdb_matched_names = [
            igdb_local_database[igdb_id_as_str]['name']
            for igdb_id_as_str in igdb_matched_ids
        ]

        dummy_distances = [
            None
            for _ in igdb_matched_ids
        ]

        element = dict()
        element['input_name'] = raw_name
        element['matched_appID'] = igdb_matched_ids  # For IGDB, this is IGDB ID. For SteamSpy, this is Steam appID.
        element['matched_pc_release_date'] = igdb_matched_pc_release_dates
        element['matched_steam_appID'] = steam_matched_ids  # Steam urls use an appID, which is the game ID on the store
        element['matched_slug'] = igdb_matched_slugs  # IGDB urls rely on the slug, which is an url-friendly game name.
        element['matched_name'] = igdb_matched_names
        element['match_distance'] = dummy_distances

        matches[raw_name] = element

    return matches


def main():
    ballot_year = '2018'
    input_filename = 'anonymized_pc_gaming_metacouncil_goty_awards_' + ballot_year + '.csv'

    ballots = load_ballots(input_filename)

    release_year = ballot_year

    # Before manual fixes

    igdb_match_database, igdb_local_database = load_igdb_local_databases(ballots,
                                                                         release_year=release_year,
                                                                         apply_hard_coded_extension_and_fixes=False)

    print_igdb_matches(igdb_match_database,
                       igdb_local_database,
                       constrained_release_year=release_year)

    # After manual fixes

    igdb_match_database, igdb_local_database = load_igdb_local_databases(ballots,
                                                                         release_year=release_year,
                                                                         apply_hard_coded_extension_and_fixes=True)

    print_igdb_matches(igdb_match_database,
                       igdb_local_database,
                       constrained_release_year=release_year)

    return True


if __name__ == '__main__':
    main()
