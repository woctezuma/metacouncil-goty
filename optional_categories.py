def get_optional_categories():
    optional_categories = [
        'best_dlc',
        'best_early_access',
        'best_turd',
    ]

    return optional_categories


def get_hard_coded_noisy_votes():
    noisy_votes = [
        '-',
        'None played',
    ]

    return noisy_votes


def get_optional_ballots(ballots, category_name):
    optional_ballots = [ballots[voter_name][category_name] for voter_name in ballots
                        if len(ballots[voter_name][category_name]) > 0]

    return optional_ballots


def filter_optional_ballots(optional_ballots):
    filtered_optional_ballots = []

    for element in optional_ballots:
        if element not in get_hard_coded_noisy_votes():
            filtered_optional_ballots.append(element)

    return filtered_optional_ballots


def match_optional_ballots(optional_ballots):
    import steampi.calendar

    from hard_coded_matches import load_extended_steamspy_database
    from match_names import find_closest_app_id

    seen_game_names = set()
    matches = dict()
    matched_optional_ballots = []

    steamspy_database = load_extended_steamspy_database()

    print()

    for raw_name in optional_ballots:
        if raw_name not in seen_game_names:
            seen_game_names.add(raw_name)

            (closest_appID, closest_distance) = find_closest_app_id(raw_name, steamspy_database)

            appID = closest_appID[0]

            app_id_release_date = steampi.calendar.get_release_date_as_str(appID)
            if app_id_release_date is None:
                app_id_release_date = 'an unknown date'

            matches[raw_name] = dict()
            matches[raw_name]['matched_appID'] = appID
            matches[raw_name]['matched_name'] = steamspy_database[appID]['name']
            matches[raw_name]['matched_release_date'] = app_id_release_date

            print(raw_name + ' -> ' + matches[raw_name]['matched_name'])

        my_str = matches[raw_name]['matched_name'] + \
                 ' (appID: ' + matches[raw_name]['matched_appID'] + \
                 ', released on ' + matches[raw_name]['matched_release_date'] + ')'

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

    for element in ranking:
        game_name = element[0]
        num_votes = element[1]

        if num_votes != current_num_votes:
            current_num_votes = num_votes
            rank += 1

        if num_votes > 1:
            my_str = ' with #votes = '
        else:
            my_str = ' with #vote = '

        print('{0:2} | '.format(rank)
              + game_name.strip()
              + my_str + str(num_votes)
              )

    return


def display_optional_ballots(input_filename, filter_noise=True):
    from load_ballots import load_ballots

    ballots = load_ballots(input_filename)

    for category_name in get_optional_categories():
        print('\nCategory: ' + category_name)

        optional_ballots = get_optional_ballots(ballots, category_name)

        if filter_noise:
            optional_ballots = filter_optional_ballots(optional_ballots)

        optional_ballots = match_optional_ballots(optional_ballots)

        ranking = compute_ranking_based_on_optional_ballots(optional_ballots)
        pretty_display(ranking)

    return True


if __name__ == '__main__':
    ballot_year = '2018'
    input_filename = 'pc_gaming_metacouncil_goty_awards_' + ballot_year + '.csv'
    display_optional_ballots(input_filename)
