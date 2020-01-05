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

                        try:
                            igdb_best_match = igdb_matches[0]
                        except IndexError:
                            igdb_best_match = None

                    # (closest_appID, closest_distance) = find_closest_app_id(raw_name, steamspy_database,
                    #                                                         release_year,
                    #                                                         num_closest_neighbors,
                    #                                                         max_num_tries_for_year)

                    element = dict()
                    element['input_name'] = raw_name

                    if igdb_best_match is not None:
                        element['matched_name'] = igdb_best_match['name']
                        element['igdb_id'] = igdb_best_match['id']
                        element['release_dates'] = set(
                            date['y']
                            for date in igdb_best_match['release_dates']
                            if 'y' in date and date['platform'] == get_pc_platform_no()
                        )

                    # element['matched_appID'] = closest_appID
                    # element['matched_name'] = [steamspy_database[appID]['name'] for appID in closest_appID]
                    # element['match_distance'] = closest_distance

                    matches[raw_name] = element

    return matches


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

        print(matches)

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
