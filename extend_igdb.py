import json
import time

from anonymize_data import get_data_folder
from igdb_databases import (
    get_igdb_file_name_suffix,
    load_igdb_local_database,
    load_igdb_match_database,
)
from igdb_databases import save_igdb_local_database
from igdb_look_up import look_up_game_id, wait_for_cooldown


def get_file_name_for_fixes_to_igdb_database(release_year=None, database_type=None):
    if database_type is None:
        database_type = 'local'  # either 'local' or 'match'

    prefix = 'fixes_to_'

    suffix = get_igdb_file_name_suffix(release_year)

    file_name = (
        get_data_folder()
        + prefix
        + 'igdb_'
        + database_type
        + '_database'
        + suffix
        + '.json'
    )

    return file_name


def load_fixes_to_igdb_database(release_year=None, database_type=None):
    if database_type is None:
        database_type = 'local'  # either 'local' or 'match'

    file_name = get_file_name_for_fixes_to_igdb_database(
        release_year=release_year,
        database_type=database_type,
    )

    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            fixes_to_igdb_database = json.load(f)
    except FileNotFoundError:
        print('File {} not found.'.format(file_name))
        fixes_to_igdb_database = dict()

    return fixes_to_igdb_database


def load_fixes_to_igdb_local_database(release_year=None):
    fixes_to_igdb_database = load_fixes_to_igdb_database(
        release_year=release_year,
        database_type='local',
    )

    return fixes_to_igdb_database


def load_fixes_to_igdb_match_database(release_year=None):
    fixes_to_igdb_database = load_fixes_to_igdb_database(
        release_year=release_year,
        database_type='match',
    )

    return fixes_to_igdb_database


def extend_igdb_local_database(release_year=None, igdb_local_database=None):
    if igdb_local_database is None:
        igdb_local_database = load_igdb_local_database(release_year=release_year)

    fixes_to_igdb_local_database = load_fixes_to_igdb_local_database(
        release_year=release_year,
    )

    extended_igdb_local_database = igdb_local_database
    for igdb_id in fixes_to_igdb_local_database.keys():
        if igdb_id in igdb_local_database.keys():
            print(
                'IGDB ID {} already exists in IGDB local database. Data will be overwritten.'.format(
                    igdb_id,
                ),
            )
        extended_igdb_local_database[igdb_id] = fixes_to_igdb_local_database[igdb_id]

    return extended_igdb_local_database


def extend_igdb_match_database(
    release_year=None,
    igdb_match_database=None,
    verbose=True,
):
    if igdb_match_database is None:
        igdb_match_database = load_igdb_match_database(release_year=release_year)

    fixes_to_igdb_match_database = load_fixes_to_igdb_match_database(
        release_year=release_year,
    )

    extended_igdb_match_database = igdb_match_database
    for app_name in fixes_to_igdb_match_database.keys():
        if app_name in igdb_match_database.keys():
            if verbose:
                print(
                    'Query name {} already exists in IGDB match database. Match will be overwritten.'.format(
                        app_name,
                    ),
                )
        extended_igdb_match_database[app_name] = fixes_to_igdb_match_database[app_name]

    return extended_igdb_match_database


def fill_in_blanks_in_the_local_database(
    release_year=None,
    igdb_local_database=None,
    igdb_match_database=None,
    save_to_disk=True,
):
    if igdb_local_database is None:
        igdb_local_database = load_igdb_local_database(release_year=release_year)

    if igdb_match_database is None:
        igdb_match_database = load_igdb_match_database(release_year=release_year)

    fixes_to_igdb_match_database = load_fixes_to_igdb_match_database(
        release_year=release_year,
    )

    required_igdb_ids = []
    for igdb_ids in fixes_to_igdb_match_database.values():
        required_igdb_ids += igdb_ids
    for igdb_ids in igdb_match_database.values():
        required_igdb_ids += igdb_ids

    augmented_igdb_local_database = igdb_local_database
    num_additional_entries = 0
    start_time = time.time()

    for igdb_id in required_igdb_ids:
        igdb_id_as_str = str(igdb_id)

        is_a_real_igdb_id = bool(igdb_id > 0)

        if (
            is_a_real_igdb_id
            and igdb_id_as_str not in augmented_igdb_local_database.keys()
        ):
            # Give as much freedom as possible: we **know** the IGDB ID (and it is a real IGDB ID since it is positive),
            # but we ignore the reason why the matching previously failed. It is likely due a combination of missing
            # information about the PC release on IGDB, and our parameters constraining the search to PC games.
            encapsulated_data = look_up_game_id(
                igdb_id,
                must_be_available_on_pc=False,
                must_be_a_game=False,
            )

            data = encapsulated_data[0]

            augmented_igdb_local_database[igdb_id_as_str] = data
            num_additional_entries += 1
            start_time = wait_for_cooldown(
                num_requests=num_additional_entries,
                start_time=start_time,
            )

    if save_to_disk and num_additional_entries > 0:
        save_igdb_local_database(
            augmented_igdb_local_database,
            release_year=release_year,
        )

    return augmented_igdb_local_database


def extend_both_igdb_databases(
    release_year=None,
    igdb_match_database=None,
    igdb_local_database=None,
    verbose=True,
):
    # Manual extension of the match database

    extended_igdb_match_database = extend_igdb_match_database(
        release_year=release_year,
        igdb_match_database=igdb_match_database,
        verbose=verbose,
    )

    # Automatic extension of the local database after the manual extension of the match database

    augmented_igdb_local_database = fill_in_blanks_in_the_local_database(
        release_year=release_year,
        igdb_local_database=igdb_local_database,
        igdb_match_database=extended_igdb_match_database,
    )

    # Manual extension of the local database

    extended_igdb_local_database = extend_igdb_local_database(
        release_year=release_year,
        igdb_local_database=augmented_igdb_local_database,
    )

    return extended_igdb_match_database, extended_igdb_local_database


def main():
    release_year = '2018'

    (
        extended_igdb_match_database,
        extended_igdb_local_database,
    ) = extend_both_igdb_databases(release_year=release_year)

    return True


if __name__ == '__main__':
    main()
