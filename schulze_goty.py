import steampi.calendar

from disqualify_vote import filter_out_votes_for_hard_coded_reasons
from extend_steamspy import load_extended_steamspy_database
from load_ballots import load_ballots, print_reviews
from match_names import standardize_ballots
from steam_store_utils import get_link_to_store


def filter_out_votes_for_wrong_release_years(standardized_ballots, target_release_year):
    # Objective: remove appID which gathered votes but were not released during the target release year

    print()

    release_years = dict()
    removed_app_ids = []

    for voter in standardized_ballots.keys():
        current_ballots = standardized_ballots[voter]['ballots']

        current_ballots_list = []
        for position in sorted(current_ballots.keys()):
            app_id = current_ballots[position]
            if app_id is not None:
                if app_id not in release_years.keys():
                    release_years[app_id] = steampi.calendar.get_release_year(app_id)
                if release_years[app_id] == int(target_release_year):
                    current_ballots_list.append(app_id)
                elif release_years[app_id] == -1:
                    print('AppID ' + app_id + ' not found on Steam (either a console game, or from another PC store)')
                    current_ballots_list.append(app_id)
                else:
                    if app_id not in removed_app_ids:
                        print('AppID ' + app_id + ' removed because it was released in ' + str(release_years[app_id]))
                        removed_app_ids.append(app_id)

        for (i, current_ballot) in enumerate(current_ballots_list):
            position = i + 1
            standardized_ballots[voter]['ballots'][position] = current_ballot
        for i in range(len(current_ballots_list), len(current_ballots.keys())):
            position = i + 1
            standardized_ballots[voter]['ballots'][position] = None

    return standardized_ballots


def adapt_votes_format_for_schulze_computations(standardized_ballots):
    candidate_names = set()

    for voter in standardized_ballots.keys():
        current_ballots = standardized_ballots[voter]['ballots']
        for position in sorted(current_ballots.keys()):
            app_id = current_ballots[position]
            if app_id is not None:
                candidate_names.add(app_id)

    weighted_ranks = []

    for voter in standardized_ballots.keys():
        current_ballots = standardized_ballots[voter]['ballots']
        current_ranking = []
        currently_seen_candidates = set()
        for position in sorted(current_ballots.keys()):
            app_id = current_ballots[position]
            if app_id is not None:
                current_ranking.append([app_id])
                currently_seen_candidates.add(app_id)

        remaining_app_ids = candidate_names.difference(currently_seen_candidates)
        current_ranking.append(remaining_app_ids)

        current_weight = 1
        weighted_ranks.append((current_ranking, current_weight))

    candidate_names = list(candidate_names)

    return candidate_names, weighted_ranks


def compute_schulze_ranking(standardized_ballots):
    # Reference: https://github.com/mgp/schulze-method

    import schulze

    (candidate_names, weighted_ranks) = adapt_votes_format_for_schulze_computations(standardized_ballots)

    schulze_ranking = schulze.compute_ranks(candidate_names, weighted_ranks)

    return schulze_ranking


def print_schulze_ranking(schulze_ranking):
    steamspy_database = load_extended_steamspy_database()

    print()

    def get_game_name(app_id):
        return steamspy_database[app_id]['name']

    offset = 0

    for (rank, appID_group) in enumerate(schulze_ranking):

        for appID in sorted(appID_group, key=get_game_name):
            game_name = get_game_name(appID)

            app_id_release_date = steampi.calendar.get_release_date_as_str(appID)
            if app_id_release_date is None:
                app_id_release_date = 'an unknown date'

            print('{0:2} | '.format(rank + offset + 1)
                  + game_name.strip()
                  + ' (appID: ' + get_link_to_store(appID)
                  + ', released on ' + app_id_release_date + ')'
                  )

        offset += len(appID_group) - 1

    return


def try_to_break_ties_in_app_id_group(app_id_group, standardized_ballots):
    standardized_ballots_for_tied_app_id_group = dict()

    for voter_name in standardized_ballots:
        current_ballots = standardized_ballots[voter_name]['ballots']
        positions = sorted(current_ballots.keys())
        current_app_ids = [current_ballots[position] for position in positions]

        has_voted_for_at_least_one_tied_app_id = sum([bool(app_id in current_app_ids) for app_id in app_id_group]) > 0

        if has_voted_for_at_least_one_tied_app_id:
            standardized_ballots_for_tied_app_id_group[voter_name] = dict()
            standardized_ballots_for_tied_app_id_group[voter_name]['ballots'] = dict()

            new_ballots = [current_ballots[position] for position in positions
                           if current_ballots[position] in app_id_group]

            for (i, app_id) in enumerate(new_ballots):
                position = i + 1
                standardized_ballots_for_tied_app_id_group[voter_name]['ballots'][position] = app_id
            for i in range(len(new_ballots), len(current_ballots)):
                position = i + 1
                standardized_ballots_for_tied_app_id_group[voter_name]['ballots'][position] = None

    if len(standardized_ballots_for_tied_app_id_group) == 0:
        schulze_ranking_for_tied_app_id_group = [app_id_group]
    else:
        schulze_ranking_for_tied_app_id_group = compute_schulze_ranking(standardized_ballots_for_tied_app_id_group)

    return schulze_ranking_for_tied_app_id_group


def try_to_break_ties_in_schulze_ranking(schulze_ranking, standardized_ballots):
    untied_schulze_ranking = list()

    for (group_no, appID_group) in enumerate(schulze_ranking):
        if len(appID_group) > 1:
            schulze_ranking_for_tied_app_id_group = try_to_break_ties_in_app_id_group(appID_group, standardized_ballots)

            if len(schulze_ranking_for_tied_app_id_group) > 1:
                print('\nAt least one tie has been broken for group n°{}'.format(group_no))

            for untied_app_id_group in schulze_ranking_for_tied_app_id_group:
                untied_schulze_ranking.append(untied_app_id_group)
        else:
            untied_schulze_ranking.append(appID_group)

    return untied_schulze_ranking


def print_ballot_distribution_for_given_appid(app_id_group, standardized_ballots):
    for appID in app_id_group:

        ballot_distribution = None

        for voter_name in standardized_ballots.keys():
            current_ballots = standardized_ballots[voter_name]['ballots']

            if ballot_distribution is None:
                ballot_distribution = [0 for _ in range(len(current_ballots))]

            positions = sorted(current_ballots.keys())

            for (index, position) in enumerate(positions):
                if current_ballots[position] == appID:
                    ballot_distribution[index] += 1

        print('\nappID:' + appID, end='\t')
        print('counts of ballots with rank 1, 2, ..., 5:\t', ballot_distribution)

    return


def print_ballot_distribution_for_top_ranked_games(schulze_ranking, standardized_ballots,
                                                   num_app_id_groups_to_display=3):
    for appID_group in schulze_ranking[0:num_app_id_groups_to_display]:
        print_ballot_distribution_for_given_appid(appID_group, standardized_ballots)

    return


def print_reviews_for_top_ranked_games(schulze_ranking, ballots, matches,
                                       num_app_id_groups_to_display=3):
    for app_id_group in schulze_ranking[0:num_app_id_groups_to_display]:
        for app_id in app_id_group:
            print_reviews(ballots, matches, app_id)

    return


def apply_pipeline(input_filename, release_year='2018', fake_author_name=True, try_to_break_ties=False):
    ballots = load_ballots(input_filename, fake_author_name=fake_author_name)

    # Standardize ballots

    (standardized_ballots, matches) = standardize_ballots(ballots, release_year, print_after_sort=False)

    standardized_ballots = filter_out_votes_for_wrong_release_years(standardized_ballots, release_year)

    standardized_ballots = filter_out_votes_for_hard_coded_reasons(standardized_ballots)

    # Apply Schulze method

    schulze_ranking = compute_schulze_ranking(standardized_ballots)

    if try_to_break_ties:
        schulze_ranking = try_to_break_ties_in_schulze_ranking(schulze_ranking, standardized_ballots)

    print_schulze_ranking(schulze_ranking)

    print_ballot_distribution_for_top_ranked_games(schulze_ranking, standardized_ballots,
                                                   num_app_id_groups_to_display=7)

    print_reviews_for_top_ranked_games(schulze_ranking, ballots, matches,
                                       num_app_id_groups_to_display=7)

    return True


if __name__ == '__main__':
    ballot_year = '2018'
    input_filename = 'pc_gaming_metacouncil_goty_awards_' + ballot_year + '.csv'
    apply_pipeline(input_filename, release_year=ballot_year, fake_author_name=False, try_to_break_ties=True)
