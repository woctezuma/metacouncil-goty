from disqualify_vote import get_hard_coded_noisy_votes
from igdb_match_names import download_igdb_local_databases, load_igdb_local_databases
from igdb_match_names import get_link_to_igdb_website, get_igdb_human_release_dates
from steam_store_utils import get_link_to_store


def get_optional_categories():
    optional_categories = [
        'best_dlc',
        'best_early_access',
        'best_vr',
        'best_turd',
    ]

    return optional_categories


def get_optional_ballots(ballots, category_name):
    optional_ballots = [ballots[voter_name][category_name] for voter_name in ballots
                        if category_name in ballots[voter_name]
                        and len(ballots[voter_name][category_name]) > 0]

    return optional_ballots


def filter_noise_from_optional_ballots(optional_ballots):
    filtered_optional_ballots = []

    for element in optional_ballots:
        if element not in get_hard_coded_noisy_votes():
            filtered_optional_ballots.append(element)

    return filtered_optional_ballots


def get_dummy_field():
    dummy_field = 'dummy_preferences'

    return dummy_field


def format_optional_ballots_for_igdb_matching(optional_ballots,
                                              dummy_field=None):
    if dummy_field is None:
        dummy_field = get_dummy_field()

    dummy_voter = 'dummy_voter'

    formatted_optional_ballots = dict()
    formatted_optional_ballots[dummy_voter] = dict()
    formatted_optional_ballots[dummy_voter][dummy_field] = dict(enumerate(optional_ballots))

    return formatted_optional_ballots


def match_optional_ballots(optional_ballots,
                           release_year=None,
                           use_igdb=False,
                           retrieve_igdb_data_from_scratch=True,
                           apply_hard_coded_extension_and_fixes=True,
                           must_be_available_on_pc=False,
                           must_be_a_game=False,
                           use_levenshtein_distance=True):
    import steampi.calendar

    from extend_steamspy import load_extended_steamspy_database
    from match_names import find_closest_app_id

    seen_game_names = set()
    matches = dict()
    matched_optional_ballots = []

    dummy_field = get_dummy_field()

    formatted_optional_ballots = format_optional_ballots_for_igdb_matching(optional_ballots,
                                                                           dummy_field=dummy_field)

    if use_igdb:
        # Code inspired from standardize_ballots() in match_names.py

        if retrieve_igdb_data_from_scratch:
            # Caveat: it is mandatory to set 'extend_previous_databases' to True, because:
            # i) databases are shared between GotY and optional categories, and we want to KEEP the data for GotY,
            # ii) databases are shared between optional categories, and there is a loop over the optional categories.
            extend_previous_databases = True

            igdb_match_database, local_database = download_igdb_local_databases(formatted_optional_ballots,
                                                                                release_year=release_year,
                                                                                apply_hard_coded_extension_and_fixes=apply_hard_coded_extension_and_fixes,
                                                                                extend_previous_databases=extend_previous_databases,
                                                                                must_be_available_on_pc=must_be_available_on_pc,
                                                                                must_be_a_game=must_be_a_game,
                                                                                goty_field=dummy_field)
        else:
            igdb_match_database, local_database = load_igdb_local_databases(formatted_optional_ballots,
                                                                            release_year=release_year,
                                                                            apply_hard_coded_extension_and_fixes=apply_hard_coded_extension_and_fixes,
                                                                            must_be_available_on_pc=must_be_available_on_pc,
                                                                            must_be_a_game=must_be_a_game,
                                                                            goty_field=dummy_field)
    else:
        igdb_match_database = None
        local_database = load_extended_steamspy_database()

    print()

    for raw_name in optional_ballots:
        if raw_name not in seen_game_names:
            seen_game_names.add(raw_name)

            if use_igdb:
                # Using IGDB
                # Code inspired from print_schulze_ranking() in schulze_goty.py

                try:
                    igdb_matched_ids = igdb_match_database[raw_name]
                except KeyError:
                    igdb_matched_ids = [None]

                try:
                    igdb_best_matched_id = igdb_matched_ids[0]
                except IndexError:
                    igdb_best_matched_id = None

                if igdb_best_matched_id is not None:
                    appID = str(igdb_best_matched_id)

                    app_name = local_database[appID]['name']

                    _, app_id_release_date = get_igdb_human_release_dates(appID,
                                                                          local_database)
                    app_url = get_link_to_igdb_website(appID,
                                                       local_database)
                else:
                    appID = None
                    app_name = None
                    app_id_release_date = None
                    app_url = None

            else:
                # Using SteamSpy

                (closest_appID, _) = find_closest_app_id(raw_name,
                                                         steamspy_database=local_database,
                                                         use_levenshtein_distance=use_levenshtein_distance)

                appID = closest_appID[0]

                app_name = local_database[appID]['name']

                app_id_release_date = steampi.calendar.get_release_date_as_str(appID)

                app_url = get_link_to_store(appID)

            if app_id_release_date is None:
                app_id_release_date = 'an unknown date'

            matches[raw_name] = dict()
            matches[raw_name]['matched_appID'] = appID
            matches[raw_name]['matched_name'] = app_name
            matches[raw_name]['matched_release_date'] = app_id_release_date
            matches[raw_name]['matched_url'] = app_url

            print('\t{} ---> IGDB id: {}\t;\t{} ({})'.format(raw_name,
                                                             matches[raw_name]['matched_appID'],
                                                             matches[raw_name]['matched_name'],
                                                             matches[raw_name]['matched_release_date'],
                                                             ))

        my_str = '{} (appID: {}, released on {})'.format(
            matches[raw_name]['matched_name'],
            matches[raw_name]['matched_url'],
            matches[raw_name]['matched_release_date'],
        )

        matched_optional_ballots.append(my_str)

    return matched_optional_ballots


def count_optional_ballots(optional_ballots):
    optional_counts = dict()

    for element in optional_ballots:
        try:
            optional_counts[element] += 1
        except KeyError:
            optional_counts[element] = 1

    return optional_counts


def compute_ranking_based_on_optional_ballots(optional_ballots):
    optional_counts = count_optional_ballots(optional_ballots)

    # Reference: https://stackoverflow.com/a/37693603
    ranking = sorted(optional_counts.items(), key=lambda x: (- x[1], x[0]), reverse=False)

    return ranking


def pretty_display(ranking):
    print()

    current_num_votes = 0
    rank = 0
    increment = 1

    for element in ranking:
        game_name = element[0]
        num_votes = element[1]

        if num_votes != current_num_votes:
            current_num_votes = num_votes
            rank += increment
            increment = 1
        else:
            increment += 1

        if num_votes > 1:
            my_str = ' with #votes = '
        else:
            my_str = ' with #vote = '

        print('{0:2} | '.format(rank)
              + game_name.strip()
              + my_str + str(num_votes)
              )

    return


def display_optional_ballots(input_filename,
                             filter_noise=True,
                             release_year=None,
                             use_igdb=False,
                             retrieve_igdb_data_from_scratch=True,
                             apply_hard_coded_extension_and_fixes=True,
                             use_levenshtein_distance=True):
    from load_ballots import load_ballots

    ballots = load_ballots(input_filename)

    for category_name in get_optional_categories():
        print('\nCategory: ' + category_name)

        optional_ballots = get_optional_ballots(ballots, category_name)

        if filter_noise:
            optional_ballots = filter_noise_from_optional_ballots(optional_ballots)

        optional_ballots = match_optional_ballots(optional_ballots,
                                                  release_year=release_year,
                                                  use_igdb=use_igdb,
                                                  retrieve_igdb_data_from_scratch=retrieve_igdb_data_from_scratch,
                                                  apply_hard_coded_extension_and_fixes=apply_hard_coded_extension_and_fixes,
                                                  use_levenshtein_distance=use_levenshtein_distance)

        ranking = compute_ranking_based_on_optional_ballots(optional_ballots)
        pretty_display(ranking)

    return True


if __name__ == '__main__':
    ballot_year = '2018'
    input_filename = 'pc_gaming_metacouncil_goty_awards_' + ballot_year + '.csv'
    use_igdb = True
    retrieve_igdb_data_from_scratch = False
    apply_hard_coded_extension_and_fixes = True
    use_levenshtein_distance = True
    display_optional_ballots(input_filename,
                             release_year=ballot_year,
                             use_igdb=use_igdb,
                             retrieve_igdb_data_from_scratch=retrieve_igdb_data_from_scratch,
                             apply_hard_coded_extension_and_fixes=apply_hard_coded_extension_and_fixes,
                             use_levenshtein_distance=use_levenshtein_distance)
