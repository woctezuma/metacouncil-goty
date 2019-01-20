def get_hard_coded_app_id_dict():
    # Matches, manually added, from game names to Steam appIDs

    hard_coded_dict = {
        # Manually fix matches for which the automatic name matching (based on Levenshtein distance) is wrong:
        "The Missing": "842910",
        "Pillars of Eternity 2": "560130",
        "Dragon Quest XI": "742120",
        "DRAGON QUEST XI: Echoes of an Elusive Age": "742120",
        "Dragon Quest XI: Echoes of an Elusive Age": "742120",
        "Dragon Quest XI: Shadows of an Elusive Age": "742120",
        "Atelier Rorona ~The Alchemist of Arland~ DX": "936160",
        "Megaman 11": "742300",
        "Mega Man 11": "742300",
        "Ys VIII: Lacrimosa of DANA": "579180",
        "The Curse of the Pharaohs (Assassin's Creed Origins)": "662351",
        "ATOM RPG": "552620",
        "Spider-Man": "-1",
        "F76": "-2",
        "Deltarune": "-4",
        "DELTARUNE": "-4",
        "The Orb Vallis (Warframe Expansion)": "-101",
        "CSGO: Danger Zone": "-102",
        "Epic Game Launcher": "-201",
    }

    return hard_coded_dict


def check_database_of_problematic_game_names(game_name):
    hard_coded_dict = get_hard_coded_app_id_dict()

    is_a_problematic_game_name = bool(game_name in hard_coded_dict.keys())

    return is_a_problematic_game_name


def find_hard_coded_app_id(game_name_input):
    hard_coded_dict = get_hard_coded_app_id_dict()

    hard_coded_app_id = hard_coded_dict[game_name_input]

    return hard_coded_app_id


if __name__ == '__main__':
    hard_coded_dict = get_hard_coded_app_id_dict()
