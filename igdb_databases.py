import json

from anonymize_data import get_data_folder


def get_igdb_file_name_suffix(release_year=None):
    suffix = '' if release_year is None else '_' + str(release_year)

    return suffix


def get_igdb_match_database_file_name(release_year=None):
    # Dict: query string ---> igdb ID

    suffix = get_igdb_file_name_suffix(release_year)

    file_name = get_data_folder() + 'igdb_match_database' + suffix + '.json'

    return file_name


def get_igdb_local_database_file_name(release_year=None):
    # Dict: igdb ID ---> igdb data

    suffix = get_igdb_file_name_suffix(release_year)

    file_name = get_data_folder() + 'igdb_local_database' + suffix + '.json'

    return file_name


def load_igdb_match_database(release_year=None, file_name=None):
    if file_name is None:
        file_name = get_igdb_match_database_file_name(release_year=release_year)

    with open(file_name, encoding='utf-8') as f:
        data = json.load(f)

    return data


def save_igdb_match_database(data, release_year=None, file_name=None):
    if file_name is None:
        file_name = get_igdb_match_database_file_name(release_year=release_year)

    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f)

    return


def load_igdb_local_database(release_year=None, file_name=None):
    if file_name is None:
        file_name = get_igdb_local_database_file_name(release_year=release_year)

    with open(file_name, encoding='utf-8') as f:
        data = json.load(f)

    return data


def save_igdb_local_database(data, release_year=None, file_name=None):
    if file_name is None:
        file_name = get_igdb_local_database_file_name(release_year=release_year)

    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f)

    return


def main():
    release_year = '2018'

    igdb_match_database = load_igdb_match_database(release_year)

    igdb_local_database = load_igdb_local_database(release_year)

    return True


if __name__ == '__main__':
    main()
