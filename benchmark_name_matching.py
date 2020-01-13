# Objective: compare the different options for name matching with data from the GotY vote in 2018:
#   i) SteamSpy database with Levenshtein distance,
#  ii) SteamSpy database with difflib,
# iii) IGDB database.

from igdb_databases import load_igdb_local_database_file_name, load_igdb_match_database_file_name
from igdb_match_names import download_igdb_local_databases, print_igdb_matches
from load_ballots import load_ballots
from match_names import precompute_matches, display_matches


def main():
    ballot_year = '2018'
    input_filename = 'anonymized_pc_gaming_metacouncil_goty_awards_' + ballot_year + '.csv'

    ballots = load_ballots(input_filename)

    release_year = ballot_year

    print('\n\ti) SteamSpy database with Levenshtein distance\n')

    # TODO do not use the extended database

    matches = precompute_matches(ballots,
                                 release_year=release_year,
                                 num_closest_neighbors=3,
                                 max_num_tries_for_year=2,
                                 use_levenshtein_distance=True)

    display_matches(matches, print_after_sort=False)

    print('\n\tii) SteamSpy database with difflib\n')

    # TODO do not use the extended database

    matches = precompute_matches(ballots,
                                 release_year=release_year,
                                 num_closest_neighbors=3,
                                 max_num_tries_for_year=2,
                                 use_levenshtein_distance=False)

    display_matches(matches, print_after_sort=False)

    print('\n\tiii) IGDB database\n')

    try:
        igdb_match_database = load_igdb_match_database_file_name(release_year=release_year)

        igdb_local_database = load_igdb_local_database_file_name(release_year=release_year)

    except FileNotFoundError:
        igdb_match_database, igdb_local_database = download_igdb_local_databases(ballots,
                                                                                 release_year=release_year)

    print_igdb_matches(igdb_match_database,
                       igdb_local_database,
                       constrained_release_year=release_year)

    return True


if __name__ == '__main__':
    main()
