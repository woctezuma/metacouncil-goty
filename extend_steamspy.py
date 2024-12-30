import steampi.calendar
import steamspypi.api


def get_hard_coded_steamspy_database_extension() -> dict[str, dict[str, str]]:
    # Entries manually added to SteamSpy's database

    return {
        # Dummy (negative) Steam appIDs for games absent from Steam, e.g. console games or PC games from other stores.
        "-1": {
            "name": "Marvel's Spider-Man",
            "developer": "Insomniac Games",
            "publisher": "Sony Interactive Entertainment",
        },
        "-2": {
            "name": "Fallout 76",
            "developer": "Bethesda Game Studios",
            "publisher": "Bethesda Softworks",
        },
        "-3": {
            "name": "Ashen",
            "developer": "New Zealand studio A44",
            "publisher": "Annapurna Interactive",
        },
        "-4": {
            "name": "Deltarune - Chapter 1",
            "developer": "Toby Fox",
            "publisher": "Toby Fox",
        },
        "-5": {
            "name": "Hades",
            "developer": "Supergiant Games",
            "publisher": "Supergiant Games",
        },
        "-6": {
            "name": "Un Pueblo De Nada",
            "developer": "Cardboard Computer",
            "publisher": "Cardboard Computer",
        },
        "-7": {
            "name": "Phoenix Point",
            "developer": "Snapshot Games",
            "publisher": "Snapshot Games",
        },
        # Dummy (negative) Steam appIDs for DLC/major updates absent from Steam.
        "-101": {
            "name": "Warframe: Fortuna - Orb Vallis map",
            "developer": "Digital Extremes",
            "publisher": "Digital Extremes",
        },
        "-102": {
            "name": "Counter-Strike: Global Offensive (Danger Zone)",
            "developer": "Valve, Hidden Path Entertainment",
            "publisher": "Valve",
        },
        "-103": {
            "name": "Path of Exile: Betrayal",
            "developer": "Grinding Gear Games",
            "publisher": "Grinding Gear Games",
        },
        # Dummy (negative) Steam appIDs for softwares absent from Steam.
        "-201": {
            "name": "Epic Games Launcher (software)",
            "developer": "Epic Games",
            "publisher": "Epic Games",
        },
        # Legitimate Steam appIDs for adult Steam games, which are not provided by SteamSpy as they are tagged as adult.
        "885940": {
            "name": "Meritocracy of the Oni & Blade",
            "developer": "ONEONE1",
            "publisher": "DLsite",
        },
        "955560": {
            "name": "Evenicle",
            "developer": "Alicesoft",
            "publisher": "MangaGamer",
        },
        # Legitimate Steam appIDs for Steam games, which are not provided by SteamSpy due to being temporarily removed
        "271260": {
            "name": "Star Control®: Origins",
            "developer": "Stardock Entertainment",
            "publisher": "Stardock Entertainment",
        },
        # Legitimate Steam appIDs for Steam DLC, which are not provided by SteamSpy because they are not games.
        "624621": {
            "name": "Wolfenstein II: The Freedom Chronicles - Episode 2",
        },
        "662351": {
            "name": "Assassin's Creed® Origins - The Curse Of The Pharaohs",
        },
        "744840": {
            "name": "Rainbow Six Siege - Year 3 Pass",
        },
        "785300": {
            "name": "XCOM 2: War of the Chosen - Tactical Legacy Pack",
        },
        "792331": {
            "name": "Valkyria Chronicles 4 - Squad E, to the Beach!",
        },
        "865670": {
            "name": "Prey - Mooncrash",
        },
        "874344": {
            "name": "SOULCALIBUR VI - 2B",
        },
        "896680": {
            "name": "WORLD OF FINAL FANTASY® MAXIMA Upgrade",
        },
        "911930": {
            "name": "BATTLETECH Flashpoint",
        },
        "947950": {
            "name": "Faeria - Puzzle Pack Elements",
        },
        "984180": {
            "name": "Pinball FX3 - Williams™ Pinball: Volume 2",
        },
    }


def load_extended_steamspy_database(steamspy_database: dict | None = None) -> dict:
    if steamspy_database is None:
        steamspy_database = steamspypi.load()

    hard_coded_steamspy_database_extension = (
        get_hard_coded_steamspy_database_extension()
    )

    extended_steamspy_database = steamspy_database
    for app_id in hard_coded_steamspy_database_extension:
        if app_id in steamspy_database:
            print(
                f"AppID {app_id} already exists in SteamSpy database. The entry will be overwritten.",
            )
        extended_steamspy_database[app_id] = hard_coded_steamspy_database_extension[
            app_id
        ]
        extended_steamspy_database[app_id]["appid"] = int(app_id)

    return extended_steamspy_database


def get_app_name_for_problematic_app_id(app_id: str | None = None) -> str:
    return "[Not Available]" if app_id is None else f"app_{app_id}"


def get_release_year_for_problematic_app_id(app_id: str) -> int:
    # As of December 2020, SteamSpy returns release_date_as_str = "29 янв. 2015" for appID = "319630".
    release_date_as_str = steampi.calendar.get_release_date_as_str(app_id=app_id)
    matched_release_year = release_date_as_str.split(" ")[-1]
    try:
        matched_release_year_as_int = int(matched_release_year)
    except ValueError:
        matched_release_year = release_date_as_str.split(" ")[0]
        matched_release_year_as_int = int(matched_release_year)

    return matched_release_year_as_int


if __name__ == "__main__":
    steamspy_database = load_extended_steamspy_database()
