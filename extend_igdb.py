import json
import time
from pathlib import Path

from anonymize_data import get_data_folder
from igdb_databases import (
    get_igdb_file_name_suffix,
    load_igdb_local_database,
    load_igdb_match_database,
    save_igdb_local_database,
)
from igdb_look_up import look_up_game_id, wait_for_cooldown


def get_file_name_for_fixes_to_igdb_database(
    release_year: str | int | None = None,
    database_type: str | None = None,
) -> str:
    if database_type is None:
        database_type = "local"  # either 'local' or 'match'

    prefix = "fixes_to_"

    suffix = get_igdb_file_name_suffix(release_year)

    return (
        get_data_folder()
        + prefix
        + "igdb_"
        + database_type
        + "_database"
        + suffix
        + ".json"
    )


def load_fixes_to_igdb_database(
    release_year: str | int | None = None,
    database_type: str | None = None,
) -> dict:
    if database_type is None:
        database_type = "local"  # either 'local' or 'match'

    file_name = get_file_name_for_fixes_to_igdb_database(
        release_year=release_year,
        database_type=database_type,
    )

    try:
        with Path(file_name).open(encoding="utf-8") as f:
            fixes_to_igdb_database = json.load(f)
    except FileNotFoundError:
        print(f"File {file_name} not found.")
        fixes_to_igdb_database = {}

    return fixes_to_igdb_database


def load_fixes_to_igdb_local_database(release_year: str | int | None = None) -> dict:
    return load_fixes_to_igdb_database(
        release_year=release_year,
        database_type="local",
    )


def load_fixes_to_igdb_match_database(release_year: str | int | None = None) -> dict:
    return load_fixes_to_igdb_database(
        release_year=release_year,
        database_type="match",
    )


def extend_igdb_local_database(
    release_year: str | int | None = None,
    igdb_local_database: dict | None = None,
) -> dict:
    if igdb_local_database is None:
        igdb_local_database = load_igdb_local_database(release_year=release_year)

    fixes_to_igdb_local_database = load_fixes_to_igdb_local_database(
        release_year=release_year,
    )

    extended_igdb_local_database = igdb_local_database
    for igdb_id in fixes_to_igdb_local_database:
        if igdb_id in igdb_local_database:
            print(
                f"IGDB ID {igdb_id} already exists in IGDB local database. Data will be overwritten.",
            )
        extended_igdb_local_database[igdb_id] = fixes_to_igdb_local_database[igdb_id]

    return extended_igdb_local_database


def extend_igdb_match_database(
    release_year: str | int | None = None,
    igdb_match_database: dict | None = None,
    *,
    verbose: bool = True,
) -> dict:
    if igdb_match_database is None:
        igdb_match_database = load_igdb_match_database(release_year=release_year)

    fixes_to_igdb_match_database = load_fixes_to_igdb_match_database(
        release_year=release_year,
    )

    extended_igdb_match_database = igdb_match_database
    for app_name in fixes_to_igdb_match_database:
        if app_name in igdb_match_database and verbose:
            print(
                f"Query name {app_name} already exists in IGDB match database. Match will be overwritten.",
            )
        extended_igdb_match_database[app_name] = fixes_to_igdb_match_database[app_name]

    return extended_igdb_match_database


def fill_in_blanks_in_the_local_database(
    release_year: str | int | None = None,
    igdb_local_database: dict | None = None,
    igdb_match_database: dict | None = None,
    *,
    save_to_disk: bool = True,
) -> dict:
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

        if is_a_real_igdb_id and igdb_id_as_str not in augmented_igdb_local_database:
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
    release_year: str | int | None = None,
    igdb_match_database: dict | None = None,
    igdb_local_database: dict | None = None,
    *,
    verbose: bool = True,
) -> tuple[dict, dict]:
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


def main() -> bool:
    release_year = "2018"

    (
        _extended_igdb_match_database,
        _extended_igdb_local_database,
    ) = extend_both_igdb_databases(release_year=release_year)

    return True


if __name__ == "__main__":
    main()
