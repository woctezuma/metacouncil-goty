import json

from anonymize_data import get_data_folder
from disqualify_vote import get_hard_coded_noisy_votes
from extend_steamspy import load_extended_steamspy_database
from igdb_utils import look_up_game_name, get_pc_platform_no
from load_ballots import load_ballots
from match_names import precompute_matches, display_matches


def match_names_with_igdb(raw_votes,
                          release_year=None):
    seen_game_names = set()
    matches = dict()

    steamspy_database = load_extended_steamspy_database()
    noisy_votes = get_hard_coded_noisy_votes()

    for voter in raw_votes.keys():
        for raw_name in raw_votes[voter]['goty_preferences'].values():
            if raw_name not in seen_game_names:
                seen_game_names.add(raw_name)

                if raw_name != '' and (raw_name not in noisy_votes):
                    igdb_matches = look_up_game_name(game_name=raw_name,
                                                     enforced_year=release_year)

                    try:
                        igdb_best_match = igdb_matches[0]
                    except IndexError:
                        print('Relaxing the year constraint for {}'.format(raw_name))

                        igdb_matches = look_up_game_name(game_name=raw_name,
                                                         enforced_year=None)

                    # Caveat: For now, matches returned by match_names_with_igdb() does not have the same structure as
                    #         matches returned by precompute_matches(). TODO
                    matches[raw_name] = igdb_matches

    return matches


def print_igdb_matches(matches):
    sorted_input_names = sorted(matches.keys())

    for raw_name in sorted_input_names:
        igdb_matches = matches[raw_name]

        try:
            igdb_best_match = igdb_matches[0]
        except IndexError:
            igdb_best_match = None

        if igdb_best_match is not None:

            release_years = set(
                date['y']
                for date in igdb_best_match['release_dates']
                if 'y' in date and date['platform'] == get_pc_platform_no()
            )

            if len(release_years) > 1:
                displayed_release_years = sorted(release_years)
                print('[!]\tSeveral release years are found for {}.'.format(raw_name))
            else:
                displayed_release_years = list(release_years)[0]

            print('\t{} ---> {} ({})'.format(raw_name,
                                             igdb_best_match['name'],
                                             displayed_release_years,
                                             ))
        else:
            print('[X]\t{}'.format(raw_name))

    return


def get_igdb_local_database_file_name(release_year=None):
    if release_year is None:
        suffix = ''
    else:
        suffix = '_' + str(release_year)

    file_name = get_data_folder() + 'igdb_database' + suffix + '.json'

    return file_name


def load_igdb_local_database_file_name(release_year=None,
                                       file_name=None):
    if file_name is None:
        file_name = get_igdb_local_database_file_name(release_year=release_year)

    with open(file_name, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data


def save_igdb_local_database_file_name(data,
                                       release_year=None,
                                       file_name=None):
    if file_name is None:
        file_name = get_igdb_local_database_file_name(release_year=release_year)

    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f)

    return


def download_igdb_local_database_file_name(ballots,
                                           release_year=None,
                                           file_name=None):
    matches = match_names_with_igdb(ballots,
                                    release_year=release_year)

    save_igdb_local_database_file_name(data=matches,
                                       release_year=release_year,
                                       file_name=file_name)

    return matches


def main():
    ballot_year = '2018'
    input_filename = 'anonymized_pc_gaming_metacouncil_goty_awards_' + ballot_year + '.csv'

    ballots = load_ballots(input_filename)

    release_year = ballot_year

    use_igdb = True

    if use_igdb:
        # Using IGDB

        try:
            matches = load_igdb_local_database_file_name(release_year=release_year)
        except FileNotFoundError:
            matches = download_igdb_local_database_file_name(ballots,
                                                             release_year=release_year)

        print_igdb_matches(matches)

    else:
        # Using SteamSpy

        matches = precompute_matches(ballots,
                                     release_year=release_year,
                                     num_closest_neighbors=3,
                                     max_num_tries_for_year=2)

        display_matches(matches, print_after_sort=False)

    return True


if __name__ == '__main__':
    main()
