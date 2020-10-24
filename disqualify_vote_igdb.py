import json

from anonymize_data import get_data_folder
from igdb_databases import get_igdb_file_name_suffix


def get_file_name_for_disqualified_igdb_ids(release_year=None):
    suffix = get_igdb_file_name_suffix(release_year)

    return get_data_folder() + 'disqualified_igdb_ids' + suffix + '.json'


def load_disqualified_igdb_ids(release_year=None):
    file_name = get_file_name_for_disqualified_igdb_ids(release_year=release_year)

    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            disqualified_igdb_ids = json.load(f)
    except FileNotFoundError:
        print('File {} not found.'.format(file_name))
        disqualified_igdb_ids = {}

    return disqualified_igdb_ids


def main():
    release_year = '2018'

    disqualified_igdb_ids = load_disqualified_igdb_ids(release_year=release_year)

    return True


if __name__ == '__main__':
    main()
