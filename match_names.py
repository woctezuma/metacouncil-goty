import steampi.calendar
import steampi.text_distances
import steamspypi.api


def get_hard_coded_app_id_dict():
    # Hard-coded list of game names which are wrongly matched with Levenshtein distance

    hard_coded_dict = {
        "PUBG": "578080",
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


def apply_hard_coded_fixes_to_app_id_search(game_name_input, filtered_sorted_app_ids, num_closest_neighbors):
    closest_app_id = [find_hard_coded_app_id(game_name_input)]
    if num_closest_neighbors > 1:
        closest_app_id.extend(filtered_sorted_app_ids[0:(num_closest_neighbors - 1)])

    return closest_app_id


def constrain_app_id_search_by_year(dist, sorted_app_ids, release_year, max_num_tries_for_year):
    filtered_sorted_app_ids = sorted_app_ids.copy()

    if release_year is not None:
        first_match = filtered_sorted_app_ids[0]
        dist_reference = dist[first_match]

        if dist_reference > 0:
            # Check release year to remove possible mismatches. For instance, with input Warhammer 2 and two choices:
            # Warhammer & Warhammer II, we would only keep the game released in the target year (2017), i.e. the sequel.
            is_the_first_match_released_in_a_wrong_year = True
            iter_count = 0
            while is_the_first_match_released_in_a_wrong_year and (iter_count < max_num_tries_for_year):
                first_match = filtered_sorted_app_ids[0]
                matched_release_year = steampi.calendar.get_release_year(first_match)

                is_the_first_match_released_in_a_wrong_year = bool(matched_release_year != int(release_year))
                if is_the_first_match_released_in_a_wrong_year:
                    filtered_sorted_app_ids.pop(0)

                iter_count += 1
            # Reset if we could not find a match released in the target year
            if is_the_first_match_released_in_a_wrong_year:
                filtered_sorted_app_ids = sorted_app_ids

    return filtered_sorted_app_ids


def find_closest_app_id(game_name_input, steamspy_database, num_closest_neighbors=1,
                        release_year=None, max_num_tries_for_year=2):
    (sorted_app_ids, dist) = steampi.text_distances.find_most_similar_game_names(game_name_input, steamspy_database)

    filtered_sorted_app_ids = sorted_app_ids

    if release_year is not None:
        filtered_sorted_app_ids = constrain_app_id_search_by_year(dist, sorted_app_ids, release_year,
                                                                  max_num_tries_for_year)

    closest_app_id = filtered_sorted_app_ids[0:num_closest_neighbors]

    if check_database_of_problematic_game_names(game_name_input):
        closest_app_id = apply_hard_coded_fixes_to_app_id_search(game_name_input, filtered_sorted_app_ids,
                                                                 num_closest_neighbors)

    closest_distance = [dist[app_id] for app_id in closest_app_id]

    return closest_app_id, closest_distance


def precompute_matches(raw_votes, num_closest_neighbors=1,
                       release_year=None, max_num_tries_for_year=2):
    seen_game_names = set()
    matches = dict()

    steamspy_database = steamspypi.api.load()

    for voter in raw_votes.keys():
        for (position, raw_name) in raw_votes[voter]['goty_preferences'].items():
            if raw_name not in seen_game_names:
                seen_game_names.add(raw_name)

                if raw_name != '':
                    (closest_appID, closest_distance) = find_closest_app_id(raw_name, steamspy_database,
                                                                            num_closest_neighbors,
                                                                            release_year, max_num_tries_for_year)

                    element = dict()
                    element['input_name'] = raw_name
                    element['matched_appID'] = closest_appID
                    element['matched_name'] = [steamspy_database[appID]['name'] for appID in closest_appID]
                    element['match_distance'] = closest_distance

                    matches[raw_name] = element

    return matches


def display_matches(matches):
    # Index of the neighbor used to sort keys of the matches dictionary
    neighbor_reference_index = 0

    sorted_keys = sorted(matches.keys(),
                         key=lambda x: matches[x]['match_distance'][neighbor_reference_index] / (
                                 1 + len(matches[x]['input_name'])))

    for game in sorted_keys:
        element = matches[game]

        dist_reference = element['match_distance'][neighbor_reference_index]
        game_name = element['input_name']

        if dist_reference > 0 or check_database_of_problematic_game_names(game_name):

            print('\n' + game_name
                  + ' (' + 'length:' + str(len(game_name)) + ')'
                  + ' ---> ', end='')
            for neighbor_index in range(len(element['match_distance'])):
                dist = element['match_distance'][neighbor_index]
                print(element['matched_name'][neighbor_index]
                      + ' (appID: ' + element['matched_appID'][neighbor_index]
                      + ' ; ' + 'distance:' + str(dist) + ')', end='\t')

    print()

    return


def get_matches(ballots, release_year='2018', num_closest_neighbors=3):
    # The following parameter can only have an effect if it is strictly greater than 1.
    max_num_tries_for_year = 2

    matches = precompute_matches(ballots, num_closest_neighbors,
                                 release_year, max_num_tries_for_year)

    display_matches(matches)

    return matches


def normalize_votes(raw_votes, matches):
    # Index of the first neighbor
    neighbor_reference_index = 0

    normalized_votes = dict()

    for voter_name in raw_votes.keys():
        normalized_votes[voter_name] = dict()
        normalized_votes[voter_name]['ballots'] = dict()
        normalized_votes[voter_name]['distances'] = dict()
        for (position, game_name) in raw_votes[voter_name]['goty_preferences'].items():

            if game_name in matches.keys():

                normalized_votes[voter_name]['ballots'][position] = matches[game_name]['matched_appID'][
                    neighbor_reference_index]
                normalized_votes[voter_name]['distances'][position] = matches[game_name]['match_distance'][
                    neighbor_reference_index]
            else:
                normalized_votes[voter_name]['ballots'][position] = None
                normalized_votes[voter_name]['distances'][position] = None

    return normalized_votes


def standardize_ballots(ballots, release_year):
    matches = get_matches(ballots, release_year=release_year)

    standardized_ballots = normalize_votes(ballots, matches)

    return standardized_ballots


if __name__ == '__main__':
    from load_ballots import load_ballots

    ballot_year = '2018'
    input_filename = 'pc_gaming_metacouncil_goty_awards_' + ballot_year + '.csv'

    ballots = load_ballots(input_filename)
    standardized_ballots = standardize_ballots(ballots, release_year=ballot_year)
