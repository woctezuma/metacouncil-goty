import steamspypi.api


def get_hard_coded_app_id_dict():
    # Hard-coded list of game names which are wrongly matched with Levenshtein distance

    hard_coded_dict = {
        # Manually fix matches for which the automatic name matching is wrong:
        "The Missing": "842910",
        "Pillars of Eternity 2": "560130",
        "Dragon Quest XI: Shadows of an Elusive Age": "742120",
        "Atelier Rorona ~The Alchemist of Arland~ DX": "936160",
        "Mega Man 11": "742300",
        "Ys VIII: Lacrimosa of DANA": "579180",
        "Spider-Man": "-1",
    }

    return hard_coded_dict


def get_hard_coded_steamspy_database_extension():
    # Entries manually added to SteamSpy's database

    database_extension = {
        # Dummy (negative) Steam appIDs for games absent from Steam, e.g. console games or PC games from other stores.
        "-1": {
            "name": "Marvel's Spider-Man", "developer": "Insomniac Games", "publisher": "Sony Interactive Entertainment"
        },
        "-2": {
            "name": "Fallout 76", "developer": "Bethesda Game Studios", "publisher": " Bethesda Softworks"
        },

        # Legitimate Steam appIDs for Steam DLC, which are not provided by SteamSpy because they are not games.
        "624621": {"name": "Wolfenstein II: The Freedom Chronicles - Episode 2", },
        "744840": {"name": "Rainbow Six Siege - Year 3 Pass", },
        "865670": {"name": "Prey - Mooncrash", },
        "911930": {"name": "BATTLETECH Flashpoint", },
        "947950": {"name": "Faeria - Puzzle Pack Elements", },
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
