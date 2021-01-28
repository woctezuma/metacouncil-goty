# Objective: compare the different options for name matching with data from the GotY vote in 2018:
#   i) SteamSpy database with Levenshtein distance,
#  ii) SteamSpy database with difflib,
# iii) IGDB database.

import steampi.calendar
import steampi.text_distances
import steamspypi.api

from disqualify_vote import is_a_noisy_vote
from igdb_match_names import load_igdb_local_databases, print_igdb_matches
from load_ballots import load_ballots
from match_names import precompute_matches, display_matches, constrain_app_id_search_by_year


def run_benchmark_for_steam_spy(raw_votes,
                                release_year=None,
                                num_closest_neighbors=1,
                                max_num_tries_for_year=0,
                                use_levenshtein_distance=True,
                                goty_field='goty_preferences'):
    seen_game_names = set()
    matches = dict()

    # Caveat: do not use the extended SteamSpy database for a fair benchmark!
    steamspy_database = steamspypi.load()

    for voter in raw_votes.keys():
        for raw_name in raw_votes[voter][goty_field].values():
            if raw_name not in seen_game_names:
                seen_game_names.add(raw_name)

                if not is_a_noisy_vote(raw_name):
                    (sorted_app_ids, dist) = steampi.text_distances.find_most_similar_game_names(raw_name,
                                                                                                 steamspy_database,
                                                                                                 use_levenshtein_distance=use_levenshtein_distance,
                                                                                                 n=num_closest_neighbors)

                    if release_year is not None:
                        sorted_app_ids = constrain_app_id_search_by_year(dist,
                                                                         sorted_app_ids,
                                                                         release_year,
                                                                         max_num_tries_for_year)

                    closest_app_id = sorted_app_ids[0:num_closest_neighbors]
                    closest_distance = [dist[app_id] for app_id in closest_app_id]

                    element = dict()
                    element['input_name'] = raw_name
                    element['matched_appID'] = closest_app_id
                    element['matched_name'] = [steamspy_database[appID]['name'] for appID in closest_app_id]
                    element['match_distance'] = closest_distance

                    matches[raw_name] = element

    return matches


def main():
    from load_ballots import get_ballot_file_name

    ballot_year = '2018'
    input_filename = get_ballot_file_name(ballot_year, is_anonymized=True)
    ballots = load_ballots(input_filename)

    release_year = ballot_year

    num_closest_neighbors = 3
    max_num_tries_for_year = 2

    apply_hard_coded_extension_and_fixes = False

    print('\n\ti) Vanilla SteamSpy database with Levenshtein distance (without using the release year)\n')

    matches = run_benchmark_for_steam_spy(ballots,
                                          num_closest_neighbors=num_closest_neighbors,
                                          use_levenshtein_distance=True)

    display_matches(matches, print_after_sort=False)

    print('\n\tii) Vanilla SteamSpy database with difflib (without using the release year)\n')

    matches = run_benchmark_for_steam_spy(ballots,
                                          num_closest_neighbors=num_closest_neighbors,
                                          use_levenshtein_distance=False)

    display_matches(matches, print_after_sort=False)

    print('\n\tiii) Vanilla IGDB database (without using the release year)\n')

    igdb_match_database, igdb_local_database = load_igdb_local_databases(ballots,
                                                                         release_year=None,
                                                                         apply_hard_coded_extension_and_fixes=apply_hard_coded_extension_and_fixes)

    print_igdb_matches(igdb_match_database,
                       igdb_local_database,
                       constrained_release_year=None)

    print('\n\tiv) Vanilla IGDB database (plus release year)\n')

    igdb_match_database, igdb_local_database = load_igdb_local_databases(ballots,
                                                                         release_year=release_year,
                                                                         apply_hard_coded_extension_and_fixes=apply_hard_coded_extension_and_fixes)

    print_igdb_matches(igdb_match_database,
                       igdb_local_database,
                       constrained_release_year=release_year)

    print('\n\tv) Extended SteamSpy database with Levenshtein distance (plus hard-coded matches and release year)\n')

    matches = precompute_matches(ballots,
                                 release_year=release_year,
                                 num_closest_neighbors=num_closest_neighbors,
                                 max_num_tries_for_year=max_num_tries_for_year,
                                 use_levenshtein_distance=True)

    display_matches(matches, print_after_sort=False)

    print('\n\tvi) Extended SteamSpy database with difflib (plus hard-coded matches and release year)\n')

    matches = precompute_matches(ballots,
                                 release_year=release_year,
                                 num_closest_neighbors=num_closest_neighbors,
                                 max_num_tries_for_year=max_num_tries_for_year,
                                 use_levenshtein_distance=False)

    display_matches(matches, print_after_sort=False)

    print('\n\tvii) Vanilla SteamSpy database with Levenshtein distance (plus release year)\n')

    matches = run_benchmark_for_steam_spy(ballots,
                                          release_year=release_year,
                                          num_closest_neighbors=num_closest_neighbors,
                                          max_num_tries_for_year=max_num_tries_for_year,
                                          use_levenshtein_distance=True)

    display_matches(matches, print_after_sort=False)

    print('\n\tviii) Vanilla SteamSpy database with difflib (plus release year)\n')

    matches = run_benchmark_for_steam_spy(ballots,
                                          release_year=release_year,
                                          num_closest_neighbors=num_closest_neighbors,
                                          max_num_tries_for_year=max_num_tries_for_year,
                                          use_levenshtein_distance=False)

    display_matches(matches, print_after_sort=False)

    return True


if __name__ == '__main__':
    main()
