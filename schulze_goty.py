import steampi.calendar
import steamspypi.api


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


def adapt_votes_format_for_schulze_computations(normalized_votes):
    candidate_names = set()

    for voter in normalized_votes.keys():
        current_ballots = normalized_votes[voter]['ballots']
        for position in sorted(current_ballots.keys()):
            app_id = current_ballots[position]
            if app_id is not None:
                candidate_names.add(app_id)

    weighted_ranks = []

    for voter in normalized_votes.keys():
        current_ballots = normalized_votes[voter]['ballots']
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


def compute_schulze_ranking(normalized_votes):
    # Reference: https://github.com/mgp/schulze-method

    import schulze

    (candidate_names, weighted_ranks) = adapt_votes_format_for_schulze_computations(normalized_votes)

    schulze_ranking = schulze.compute_ranks(candidate_names, weighted_ranks)

    print_schulze_ranking(schulze_ranking)

    return schulze_ranking


def print_schulze_ranking(schulze_ranking):
    steamspy_database = steamspypi.api.load()

    print()

    for (rank, appID_group) in enumerate(schulze_ranking):

        def get_game_name(app_id):
            return steamspy_database[app_id]['name']

        for appID in sorted(appID_group, key=get_game_name):
            game_name = get_game_name(appID)

            app_id_release_date = steampi.calendar.get_release_date_as_str(appID)
            if app_id_release_date is None:
                app_id_release_date = 'an unknown date'

            print('{0:2} | '.format(rank + 1)
                  + game_name.strip()
                  + ' (appID: ' + appID
                  + ', released on ' + app_id_release_date + ')'
                  )

    return


def print_ballot_distribution_for_given_appid(app_id_group, normalized_votes):
    for appID in app_id_group:

        ballot_distribution = None

        for voter_name in normalized_votes.keys():
            current_ballots = normalized_votes[voter_name]['ballots']

            if ballot_distribution is None:
                ballot_distribution = [0 for _ in range(len(current_ballots))]

            positions = sorted(current_ballots.keys())

            for index in range(len(ballot_distribution)):
                if current_ballots[positions[index]] == appID:
                    ballot_distribution[index] += 1

        print('\nappID:' + appID, end='\t')
        print('counts of ballots with rank 1, 2, ..., 5:\t', ballot_distribution)

    return


def filter_out_votes_for_wrong_release_years(normalized_votes, target_release_year):
    # Objective: remove appID which gathered votes but were not released during the target release year

    print()

    release_years = dict()
    removed_app_ids = []

    for voter in normalized_votes.keys():
        current_ballots = normalized_votes[voter]['ballots']

        current_ballots_list = []
        for position in sorted(current_ballots.keys()):
            app_id = current_ballots[position]
            if app_id is not None:
                if app_id not in release_years.keys():
                    release_years[app_id] = steampi.calendar.get_release_year(app_id)
                if release_years[app_id] == int(target_release_year):
                    current_ballots_list.append(app_id)
                else:
                    if app_id not in removed_app_ids:
                        print('AppID ' + app_id + ' was removed because it was released in '
                              + str(release_years[app_id]))
                        removed_app_ids.append(app_id)

        for i in range(len(current_ballots_list)):
            position = i + 1
            normalized_votes[voter]['ballots'][position] = current_ballots_list[i]
        for i in range(len(current_ballots_list), len(current_ballots.keys())):
            position = i + 1
            normalized_votes[voter]['ballots'][position] = None

    return normalized_votes


def compute_ranking(ballots, release_year='2018'):
    from match_names import get_matches

    matches = get_matches(ballots, release_year=release_year)

    normalized_votes = normalize_votes(ballots, matches)

    normalized_votes = filter_out_votes_for_wrong_release_years(normalized_votes, release_year)

    schulze_ranking = compute_schulze_ranking(normalized_votes)

    num_app_id_groups_to_display = 3
    for appID_group in schulze_ranking[0:num_app_id_groups_to_display]:
        print_ballot_distribution_for_given_appid(appID_group, normalized_votes)


def apply_pipeline(input_filename, release_year):
    from load_ballots import load_ballots

    ballots = load_ballots(input_filename)

    compute_ranking(ballots, release_year=release_year)

    return True


if __name__ == '__main__':
    ballot_year = '2018'
    input_filename = 'pc_gaming_metacouncil_goty_awards_' + ballot_year + '.csv'
    apply_pipeline(input_filename, release_year=ballot_year)
