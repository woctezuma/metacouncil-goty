import json

from anonymize_data import get_data_folder
from igdb_databases import get_igdb_file_name_suffix, load_igdb_local_database, load_igdb_match_database


def get_file_name_for_fixes_to_igdb_database(release_year=None,
                                             database_type=None):
    if database_type is None:
        database_type = 'local'  # either 'local' or 'match'

    prefix = 'fixes_to_'

    suffix = get_igdb_file_name_suffix(release_year)

    file_name = get_data_folder() + prefix + 'igdb_' + database_type + '_database' + suffix + '.json'

    return file_name


def load_fixes_to_igdb_database(release_year=None,
                                database_type=None):
    if database_type is None:
        database_type = 'local'  # either 'local' or 'match'

    file_name = get_file_name_for_fixes_to_igdb_database(release_year=release_year,
                                                         database_type=database_type)

    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            fixes_to_igdb_database = json.load(f)
    except FileNotFoundError:
        print('File {} not found.'.format(file_name))
        fixes_to_igdb_database = dict()

    return fixes_to_igdb_database


def load_fixes_to_igdb_local_database(release_year=None):
    fixes_to_igdb_database = load_fixes_to_igdb_database(release_year=release_year,
                                                         database_type='local')

    return fixes_to_igdb_database


def load_fixes_to_igdb_match_database(release_year=None):
    fixes_to_igdb_database = load_fixes_to_igdb_database(release_year=release_year,
                                                         database_type='match')

    return fixes_to_igdb_database


def extend_igdb_local_database(release_year=None,
                               igdb_local_database=None):
    if igdb_local_database is None:
        igdb_local_database = load_igdb_local_database(release_year=release_year)

    fixes_to_igdb_local_database = load_fixes_to_igdb_local_database(release_year=release_year)

    extended_igdb_local_database = igdb_local_database
    for igdb_id in fixes_to_igdb_local_database.keys():
        if igdb_id in igdb_local_database.keys():
            print('IGDB ID {} already exists in IGDB local database. Data will be overwritten.'.format(igdb_id))
        extended_igdb_local_database[igdb_id] = fixes_to_igdb_local_database[igdb_id]

    return extended_igdb_local_database


def extend_igdb_match_database(release_year=None,
                               igdb_match_database=None):
    if igdb_match_database is None:
        igdb_match_database = load_igdb_match_database(release_year=release_year)

    fixes_to_igdb_match_database = load_fixes_to_igdb_match_database(release_year=release_year)

    extended_igdb_match_database = igdb_match_database
    for app_name in fixes_to_igdb_match_database.keys():
        if app_name in igdb_match_database.keys():
            print('Query name {} already exists in IGDB match database. Match will be overwritten.'.format(app_name))
        extended_igdb_match_database[app_name] = fixes_to_igdb_match_database[app_name]

    return extended_igdb_match_database


def extend_both_igdb_databases(release_year=None,
                               igdb_match_database=None,
                               igdb_local_database=None):
    extended_igdb_match_database = extend_igdb_match_database(release_year=release_year,
                                                              igdb_match_database=igdb_match_database)

    extended_igdb_local_database = extend_igdb_local_database(release_year=release_year,
                                                              igdb_local_database=igdb_local_database)

    return extended_igdb_match_database, extended_igdb_local_database


def main():
    release_year = '2018'

    extended_igdb_match_database, extended_igdb_local_database = extend_both_igdb_databases(release_year=release_year)

    return True


if __name__ == '__main__':
    main()
