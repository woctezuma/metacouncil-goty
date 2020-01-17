import steampi.calendar

from disqualify_vote import filter_out_votes_for_hard_coded_reasons
from extend_igdb import extend_both_igdb_databases
from extend_steamspy import load_extended_steamspy_database
from igdb_match_names import get_igdb_release_years, get_link_to_igdb_website, get_igdb_human_release_dates
from load_ballots import load_ballots, print_reviews
from match_names import standardize_ballots
from steam_store_utils import get_link_to_store, get_early_access_status
from whitelist_vote import load_whitelisted_ids


def filter_out_votes_for_early_access_titles(standardized_ballots,
                                             whitelisted_ids=None):
    # Objective: remove appID which gathered votes but are tagged as 'Early Access' titles

    if whitelisted_ids is None:
        # Caveat: Early Access status is only retrieved when using SteamSpy, hence why 'release_year' and 'use_igdb'
        # are not function parameters of filter_out_votes_for_early_access_titles()
        release_year = None
        use_igdb = False

        whitelisted_ids = load_whitelisted_ids(release_year=release_year,
                                               use_igdb=use_igdb)

    for voter in standardized_ballots.keys():
        current_ballots = standardized_ballots[voter]['ballots']

        current_ballots_list = []
        for position in sorted(current_ballots.keys()):
            app_id = current_ballots[position]
            if app_id is not None:
                is_early_access = get_early_access_status(app_id)

                if not is_early_access:
                    current_ballots_list.append(app_id)
                elif app_id in whitelisted_ids:
                    print('AppID ' + app_id + ' whitelisted because ' + whitelisted_ids[app_id]["reason"])
                    current_ballots_list.append(app_id)
                else:
                    print('AppID ' + app_id + ' removed because it is tagged as an Early Access title')

        for (i, current_ballot) in enumerate(current_ballots_list):
            position = i + 1
            standardized_ballots[voter]['ballots'][position] = current_ballot
        for i in range(len(current_ballots_list), len(current_ballots.keys())):
            position = i + 1
            standardized_ballots[voter]['ballots'][position] = None

    return standardized_ballots


def get_local_database(target_release_year=None,
                       use_igdb=False,
                       verbose=False):
    if use_igdb:
        _, extended_igdb_local_database = extend_both_igdb_databases(release_year=target_release_year,
                                                                     verbose=verbose)
        steamspy_database = None

        local_database = extended_igdb_local_database
    else:
        extended_igdb_local_database = None
        steamspy_database = load_extended_steamspy_database()

        local_database = steamspy_database

    return local_database


def filter_out_votes_for_wrong_release_years(standardized_ballots,
                                             target_release_year,
                                             use_igdb=False,
                                             whitelisted_ids=None):
    # Objective: remove appID which gathered votes but were not released during the target release year

    if whitelisted_ids is None:
        whitelisted_ids = load_whitelisted_ids(release_year=target_release_year,
                                               use_igdb=use_igdb)

    local_database = get_local_database(target_release_year=target_release_year,
                                        use_igdb=use_igdb)

    print()

    release_years = dict()
    removed_app_ids = []

    for voter in standardized_ballots.keys():
        current_ballots = standardized_ballots[voter]['ballots']

        current_ballots_list = []
        for position in sorted(current_ballots.keys()):
            app_id = current_ballots[position]
            if app_id is not None:
                app_id_as_str = str(app_id)
                app_data = local_database[app_id_as_str]
                app_name = app_data['name']

                if app_id not in release_years.keys():
                    if use_igdb:
                        possible_release_years, year_to_remember = get_igdb_release_years(app_data,
                                                                                          target_release_year=target_release_year)
                        release_years[app_id] = year_to_remember
                    else:
                        release_years[app_id] = steampi.calendar.get_release_year(app_id)
                if release_years[app_id] == int(target_release_year):
                    current_ballots_list.append(app_id)
                elif release_years[app_id] == -1:
                    print('AppID {} ({}) not found on Steam (either a console game, or from another PC store)'.format(
                        app_id,
                        app_name,
                    ))
                    current_ballots_list.append(app_id)
                elif app_id in whitelisted_ids:
                    print('AppID ' + app_id + ' whitelisted because ' + whitelisted_ids[app_id]["reason"])
                    current_ballots_list.append(app_id)
                else:
                    if app_id not in removed_app_ids:
                        print('AppID {} ({}) removed because it was released in {}'.format(
                            app_id,
                            app_name,
                            release_years[app_id],
                        ))
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


def print_schulze_ranking(schulze_ranking,
                          target_release_year=None,
                          use_igdb=False):
    local_database = get_local_database(target_release_year=target_release_year,
                                        use_igdb=use_igdb)

    print()

    def get_game_name(app_id):
        return local_database[app_id]['name']

    offset = 0

    for (rank, appID_group) in enumerate(schulze_ranking):

        for appID in sorted(appID_group, key=get_game_name):
            game_name = get_game_name(appID)

            if use_igdb:

                _, app_id_release_date = get_igdb_human_release_dates(appID,
                                                                      local_database)
                app_url = get_link_to_igdb_website(appID,
                                                   local_database)
            else:
                app_id_release_date = steampi.calendar.get_release_date_as_str(appID)
                app_url = get_link_to_store(appID)

            if app_id_release_date is None:
                app_id_release_date = 'an unknown date'

            print('{0:2} | '.format(rank + offset + 1)
                  + game_name.strip()
                  + ' (appID: ' + app_url
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


def print_voter_stats(schulze_ranking, standardized_ballots, num_app_id_groups_to_display=7, verbose=True):
    # Check how many people voted for N games which ended up in the top 10 of the GOTY ranking
    # Reference:
    # https://metacouncil.com/threads/metacouncils-pc-games-of-the-year-awards-2018-results.525/page-2

    goty = []
    for app_id_group in schulze_ranking[0:num_app_id_groups_to_display]:
        for app_id in app_id_group:
            goty.append(int(app_id))

    print('\nVoter stats are displayed based on the top {} games'.format(len(goty)))

    max_num_ballots_per_person = 0

    counter = dict()
    for voter in standardized_ballots:
        current_ballots = standardized_ballots[voter]['ballots'].values()
        max_num_ballots_per_person = max(max_num_ballots_per_person, len(current_ballots))

        vote = [int(i) for i in current_ballots if i is not None]
        counter[voter] = sum(i in goty for i in vote)

    for num_votes in reversed(range(max_num_ballots_per_person + 1)):
        l = []
        for (v, c) in counter.items():
            if c == num_votes:
                l.append(v)
        print('\n{} ballots included {} games present in the top {}.'.format(len(l), num_votes, len(goty)))
        if verbose:
            print(l)

    return


def apply_pipeline(input_filename,
                   release_year='2018',
                   fake_author_name=True,
                   try_to_break_ties=False,
                   use_igdb=False,
                   retrieve_igdb_data_from_scratch=True,
                   apply_hard_coded_extension_and_fixes=True,
                   use_levenshtein_distance=True,
                   goty_field='goty_preferences',
                   year_constraint='equality'):
    ballots = load_ballots(input_filename, fake_author_name=fake_author_name)

    # Standardize ballots

    (standardized_ballots, matches) = standardize_ballots(ballots,
                                                          release_year,
                                                          print_after_sort=False,
                                                          use_igdb=use_igdb,
                                                          retrieve_igdb_data_from_scratch=retrieve_igdb_data_from_scratch,
                                                          apply_hard_coded_extension_and_fixes=apply_hard_coded_extension_and_fixes,
                                                          use_levenshtein_distance=use_levenshtein_distance,
                                                          goty_field=goty_field,
                                                          year_constraint=year_constraint)

    whitelisted_ids = load_whitelisted_ids(release_year=release_year,
                                           use_igdb=use_igdb)

    standardized_ballots = filter_out_votes_for_wrong_release_years(standardized_ballots,
                                                                    release_year,
                                                                    use_igdb=use_igdb,
                                                                    whitelisted_ids=whitelisted_ids)

    if not use_igdb:
        standardized_ballots = filter_out_votes_for_early_access_titles(standardized_ballots,
                                                                        whitelisted_ids=whitelisted_ids)

    standardized_ballots = filter_out_votes_for_hard_coded_reasons(standardized_ballots,
                                                                   release_year=release_year,
                                                                   use_igdb=use_igdb)

    # Apply Schulze method

    schulze_ranking = compute_schulze_ranking(standardized_ballots)

    if try_to_break_ties:
        schulze_ranking = try_to_break_ties_in_schulze_ranking(schulze_ranking, standardized_ballots)

    print_schulze_ranking(schulze_ranking,
                          target_release_year=release_year,
                          use_igdb=use_igdb)

    print_ballot_distribution_for_top_ranked_games(schulze_ranking, standardized_ballots,
                                                   num_app_id_groups_to_display=7)

    print_voter_stats(schulze_ranking, standardized_ballots,
                      num_app_id_groups_to_display=7)

    print_reviews_for_top_ranked_games(schulze_ranking, ballots, matches,
                                       num_app_id_groups_to_display=7)

    return True


if __name__ == '__main__':
    ballot_year = '2018'
    input_filename = 'pc_gaming_metacouncil_goty_awards_' + ballot_year + '.csv'
    use_igdb = True
    retrieve_igdb_data_from_scratch = False
    apply_hard_coded_extension_and_fixes = True
    use_levenshtein_distance = True
    goty_field = 'goty_preferences'
    apply_pipeline(input_filename,
                   release_year=ballot_year,
                   fake_author_name=False,
                   try_to_break_ties=False,
                   use_igdb=use_igdb,
                   retrieve_igdb_data_from_scratch=retrieve_igdb_data_from_scratch,
                   apply_hard_coded_extension_and_fixes=apply_hard_coded_extension_and_fixes,
                   use_levenshtein_distance=use_levenshtein_distance,
                   goty_field=goty_field,
                   year_constraint='equality')
