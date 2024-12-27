import json

from anonymize_data import get_data_folder
from igdb_databases import get_igdb_file_name_suffix


def get_file_name_for_whitelisted_igdb_ids(release_year=None):
    suffix = get_igdb_file_name_suffix(release_year)

    file_name = get_data_folder() + "whitelisted_igdb_ids" + suffix + ".json"

    return file_name


def load_whitelisted_igdb_ids(release_year=None):
    file_name = get_file_name_for_whitelisted_igdb_ids(release_year=release_year)

    try:
        with open(file_name, encoding="utf-8") as f:
            whitelisted_igdb_ids = json.load(f)
    except FileNotFoundError:
        print(f"File {file_name} not found.")
        whitelisted_igdb_ids = {}

    return whitelisted_igdb_ids


def main():
    release_year = "2018"

    whitelisted_igdb_ids = load_whitelisted_igdb_ids(release_year=release_year)

    return True


if __name__ == "__main__":
    main()
