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


def count_optional_ballots(optional_ballots):
    optional_counts = dict()

    for element in optional_ballots:
        try:
            optional_counts[element] += 1
        except KeyError:
            optional_counts[element] = 1

    return optional_counts


def compute_ranking_based_on_optional_ballots(optional_ballots, filter_noise=False):
    if filter_noise:
        optional_ballots = filter_optional_ballots(optional_ballots)

    optional_counts = count_optional_ballots(optional_ballots)

    # Reference: https://stackoverflow.com/a/37693603
    ranking = sorted(optional_counts.items(), key=lambda x: (- x[1], x[0]), reverse=False)

    return ranking


def pretty_display(ranking):
    print()

    for (rank, element) in enumerate(ranking):
        game_name = element[0]
        num_votes = element[1]

        if num_votes > 1:
            my_str = ' (#votes = '
        else:
            my_str = ' (#vote = '

        print('{0:2} | '.format(rank + 1)
              + game_name.strip()
              + my_str + str(num_votes) + ')'
              )

    return


def display_optional_ballots(input_filename):
    from load_ballots import load_ballots

    ballots = load_ballots(input_filename)

    for category_name in get_optional_categories():
        print('\nCategory: ' + category_name)

        optional_ballots = get_optional_ballots(ballots, category_name)

        ranking = compute_ranking_based_on_optional_ballots(optional_ballots, filter_noise=False)
        pretty_display(ranking)

        ranking = compute_ranking_based_on_optional_ballots(optional_ballots, filter_noise=True)
        pretty_display(ranking)

    return True


if __name__ == '__main__':
    ballot_year = '2018'
    input_filename = 'pc_gaming_metacouncil_goty_awards_' + ballot_year + '.csv'
    display_optional_ballots(input_filename)
