import json
from pathlib import Path

from anonymize_data import get_data_folder


def get_igdb_file_name_suffix(release_year: str | None = None) -> str:
    return "" if release_year is None else "_" + str(release_year)


def get_igdb_match_database_file_name(release_year: str | None = None) -> str:
    # Dict: query string ---> igdb ID

    suffix = get_igdb_file_name_suffix(release_year)

    return get_data_folder() + "igdb_match_database" + suffix + ".json"


def get_igdb_local_database_file_name(release_year: str | None = None) -> str:
    # Dict: igdb ID ---> igdb data

    suffix = get_igdb_file_name_suffix(release_year)

    return get_data_folder() + "igdb_local_database" + suffix + ".json"


def load_igdb_match_database(
    release_year: str | None = None,
    file_name: str | None = None,
) -> dict:
    if file_name is None:
        file_name = get_igdb_match_database_file_name(release_year=release_year)

    with Path(file_name).open(encoding="utf-8") as f:
        return json.load(f)


def save_igdb_match_database(
    data: dict,
    release_year: str | None = None,
    file_name: str | None = None,
) -> None:
    if file_name is None:
        file_name = get_igdb_match_database_file_name(release_year=release_year)

    with Path(file_name).open("w", encoding="utf-8") as f:
        json.dump(data, f)


def load_igdb_local_database(
    release_year: str | None = None,
    file_name: str | None = None,
) -> dict:
    if file_name is None:
        file_name = get_igdb_local_database_file_name(release_year=release_year)

    with Path(file_name).open(encoding="utf-8") as f:
        return json.load(f)


def save_igdb_local_database(
    data: dict,
    release_year: str | None = None,
    file_name: str | None = None,
) -> None:
    if file_name is None:
        file_name = get_igdb_local_database_file_name(release_year=release_year)

    with Path(file_name).open("w", encoding="utf-8") as f:
        json.dump(data, f)


def main() -> bool:
    release_year = "2018"

    load_igdb_match_database(release_year)

    load_igdb_local_database(release_year)

    return True


if __name__ == "__main__":
    main()
