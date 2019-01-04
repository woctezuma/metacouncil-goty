import steamspypi.api


def get_hard_coded_app_id_dict():
    # Hard-coded list of game names which are wrongly matched with Levenshtein distance

    hard_coded_dict = {
        "The Missing": "842910",
        "Pillars of Eternity 2": "560130",
        "Dragon Quest XI: Shadows of an Elusive Age": "742120",
        "Atelier Rorona ~The Alchemist of Arland~ DX": "936160",

        # Add an entry for a game which we could not manually find on Steam. We start with -1, and decrement from there.
        "Spider-Man": "-1",
    }

    return hard_coded_dict


def get_hard_coded_steamspy_database_extension():
    database_extension = {
        "-1": {
            "name": "Marvel's Spider-Man", "developer": "Insomniac Games", "publisher": "Sony Interactive Entertainment"
        },
    }

    return database_extension


def load_extended_steamspy_database():
    steamspy_database = steamspypi.api.load()

    hard_coded_steamspy_database_extension = get_hard_coded_steamspy_database_extension()

    extended_steamspy_database = steamspy_database
    for app_id in hard_coded_steamspy_database_extension.keys():
        extended_steamspy_database[app_id] = hard_coded_steamspy_database_extension[app_id]
        extended_steamspy_database[app_id]["appid"] = int(app_id)

    return extended_steamspy_database


def check_database_of_problematic_game_names(game_name):
    hard_coded_dict = get_hard_coded_app_id_dict()

    is_a_problematic_game_name = bool(game_name in hard_coded_dict.keys())

    return is_a_problematic_game_name


def find_hard_coded_app_id(game_name_input):
    hard_coded_dict = get_hard_coded_app_id_dict()

    hard_coded_app_id = hard_coded_dict[game_name_input]

    return hard_coded_app_id


if __name__ == '__main__':
    steamspy_database = load_extended_steamspy_database()
