import steamspypi.api


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

        # Legitimate Steam appIDs for adult Steam games, which are not provided by SteamSpy as they are tagged as adult.
        "885940": {
            "name": "Meritocracy of the Oni & Blade", "developer": "ONEONE1", "publisher": "DLsite"
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


if __name__ == '__main__':
    steamspy_database = load_extended_steamspy_database()
