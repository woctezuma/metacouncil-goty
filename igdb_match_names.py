from disqualify_vote import get_hard_coded_noisy_votes
from extend_steamspy import load_extended_steamspy_database
from igdb_databases import load_igdb_local_database_file_name, load_igdb_match_database_file_name
from igdb_databases import save_igdb_local_database_file_name, save_igdb_match_database_file_name
from igdb_utils import look_up_game_name, get_pc_platform_range
from load_ballots import load_ballots
from match_names import precompute_matches, display_matches


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
                    #         matches returned by precompute_matches(). TODO
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

            release_years = set(
                date['y']
                for date in igdb_data['release_dates']
                if 'y' in date and (date['platform'] in get_pc_platform_range())
            )

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

            print('\t{} ---> {} ({})'.format(raw_name,
                                             igdb_data['name'],
                                             displayed_release_years,
                                             ))
        else:
            print('[X]\t{}'.format(raw_name))

    return


def download_igdb_local_databases(ballots,
                                  release_year=None):
    igdb_match_database, igdb_local_database = match_names_with_igdb(ballots,
                                                                     release_year=release_year)

    save_igdb_match_database_file_name(data=igdb_match_database,
                                       release_year=release_year)

    save_igdb_local_database_file_name(data=igdb_local_database,
                                       release_year=release_year)

    return igdb_match_database, igdb_local_database


def load_igdb_local_databases(ballots,
                              release_year=None):
    try:
        igdb_match_database = load_igdb_match_database_file_name(release_year=release_year)

        igdb_local_database = load_igdb_local_database_file_name(release_year=release_year)

    except FileNotFoundError:
        igdb_match_database, igdb_local_database = download_igdb_local_databases(ballots,
                                                                                 release_year=release_year)

    return igdb_match_database, igdb_local_database


def main():
    ballot_year = '2018'
    input_filename = 'anonymized_pc_gaming_metacouncil_goty_awards_' + ballot_year + '.csv'

    ballots = load_ballots(input_filename)

    release_year = ballot_year

    use_igdb = True

    # If SteamSpy is used instead of IGDB, choose between Levenshtein distance and difflib:
    use_levenshtein_distance = True

    if use_igdb:
        # Using IGDB

        igdb_match_database, igdb_local_database = load_igdb_local_databases(ballots,
                                                                             release_year=release_year)

        print_igdb_matches(igdb_match_database,
                           igdb_local_database,
                           constrained_release_year=release_year)

    else:
        # Using SteamSpy

        matches = precompute_matches(ballots,
                                     release_year=release_year,
                                     num_closest_neighbors=3,
                                     max_num_tries_for_year=2,
                                     use_levenshtein_distance=use_levenshtein_distance)

        display_matches(matches, print_after_sort=False)

    return True


if __name__ == '__main__':
    main()
