from collections import Counter

import steampi.calendar

from disqualify_vote import filter_out_votes_for_hard_coded_reasons
from extend_igdb import extend_both_igdb_databases
from extend_steamspy import (
    get_app_name_for_problematic_app_id,
    get_release_year_for_problematic_app_id,
    load_extended_steamspy_database,
)
from igdb_credentials import download_latest_credentials
from igdb_match_names import (
    get_igdb_human_release_dates,
    get_igdb_release_years,
    get_link_to_igdb_website,
)
from load_ballots import load_ballots, print_reviews
from match_names import standardize_ballots
from steam_store_utils import get_early_access_status, get_link_to_store
from whitelist_vote import load_whitelisted_ids


def filter_out_votes_for_early_access_titles(
    standardized_ballots: dict,
    whitelisted_ids: dict | None = None,
) -> dict:
    # Objective: remove appID which gathered votes but are tagged as 'Early Access' titles

    if whitelisted_ids is None:
        # Caveat: Early Access status is only retrieved when using SteamSpy, hence why 'release_year' and 'use_igdb'
        # are not function parameters of filter_out_votes_for_early_access_titles()
        release_year = None
        use_igdb = False

        whitelisted_ids = load_whitelisted_ids(
            release_year=release_year,
            use_igdb=use_igdb,
        )

    for voter in standardized_ballots:
        current_ballots = standardized_ballots[voter]["ballots"]

        current_ballots_list = []
        for position in sorted(current_ballots.keys()):
            app_id = current_ballots[position]
            if app_id is not None:
                is_early_access = get_early_access_status(app_id)

                if not is_early_access:
                    current_ballots_list.append(app_id)
                elif app_id in whitelisted_ids:
                    print(
                        "AppID "
                        + app_id
                        + " whitelisted because "
                        + whitelisted_ids[app_id]["reason"],
                    )
                    current_ballots_list.append(app_id)
                else:
                    print(
                        "AppID "
                        + app_id
                        + " removed because it is tagged as an Early Access title",
                    )

        for i, current_ballot in enumerate(current_ballots_list):
            position = i + 1
            standardized_ballots[voter]["ballots"][position] = current_ballot
        for i in range(len(current_ballots_list), len(current_ballots.keys())):
            position = i + 1
            standardized_ballots[voter]["ballots"][position] = None

    return standardized_ballots


def get_local_database(
    target_release_year: int | str | None = None,
    *,
    use_igdb: bool = False,
    verbose: bool = False,
) -> dict:
    if use_igdb:
        _, extended_igdb_local_database = extend_both_igdb_databases(
            release_year=target_release_year,
            verbose=verbose,
        )
        steamspy_database = None

        local_database = extended_igdb_local_database
    else:
        extended_igdb_local_database = None
        steamspy_database = load_extended_steamspy_database()

        local_database = steamspy_database

    return local_database


def filter_out_votes_for_wrong_release_years(
    standardized_ballots: dict,
    target_release_year: int | str,
    *,
    use_igdb: bool = False,
    year_constraint: str = "equality",
    whitelisted_ids: dict | None = None,
    is_steamspy_api_paginated: bool = True,
) -> dict:
    # Objective: remove appID which gathered votes but were not released during the target release year

    if whitelisted_ids is None:
        whitelisted_ids = load_whitelisted_ids(
            release_year=target_release_year,
            use_igdb=use_igdb,
        )

    local_database = get_local_database(
        target_release_year=target_release_year,
        use_igdb=use_igdb,
    )

    print()

    release_years = {}
    removed_app_ids = []

    for voter in standardized_ballots:
        current_ballots = standardized_ballots[voter]["ballots"]

        current_ballots_list = []
        for position in sorted(current_ballots.keys()):
            app_id = current_ballots[position]
            if app_id is not None:
                app_id_as_str = str(app_id)

                # Due to the pagination recently adopted by SteamSpy API, local_database can miss many entries nowadays.
                if (
                    not use_igdb
                    and is_steamspy_api_paginated
                    and app_id_as_str not in local_database
                ):
                    local_database[app_id_as_str] = {}
                    local_database[app_id_as_str]["name"] = (
                        get_app_name_for_problematic_app_id(app_id_as_str)
                    )

                app_data = local_database[app_id_as_str]
                app_name = app_data["name"]

                if app_id not in release_years:
                    if use_igdb:
                        (
                            _possible_release_years,
                            year_to_remember,
                        ) = get_igdb_release_years(
                            app_data,
                            target_release_year=target_release_year,
                        )
                        release_years[app_id] = year_to_remember
                    else:
                        try:
                            release_years[app_id] = steampi.calendar.get_release_year(
                                app_id,
                            )
                        except ValueError:
                            release_years[app_id] = (
                                get_release_year_for_problematic_app_id(app_id=app_id)
                            )
                if release_years[app_id] == int(target_release_year):
                    # Always keep the game, whichever the value of 'year_constraint' ('equality', 'minimum', 'maximum').
                    current_ballots_list.append(app_id)
                elif release_years[app_id] == -1:
                    print(
                        f"AppID {app_id} ({app_name}) not found on Steam (either a console game, or from another PC store)",
                    )
                    current_ballots_list.append(app_id)
                elif (
                    year_constraint == "minimum"
                    and release_years[app_id]
                    >= int(
                        target_release_year,
                    )
                ) or (
                    year_constraint == "maximum"
                    and release_years[app_id]
                    <= int(
                        target_release_year,
                    )
                ):
                    current_ballots_list.append(app_id)
                elif app_id in whitelisted_ids:
                    print(
                        "AppID "
                        + app_id
                        + " whitelisted because "
                        + whitelisted_ids[app_id]["reason"],
                    )
                    current_ballots_list.append(app_id)
                elif app_id not in removed_app_ids:
                    print(
                        f"AppID {app_id} ({app_name}) removed because it was released in {release_years[app_id]}",
                    )
                    removed_app_ids.append(app_id)

        for i, current_ballot in enumerate(current_ballots_list):
            position = i + 1
            standardized_ballots[voter]["ballots"][position] = current_ballot
        for i in range(len(current_ballots_list), len(current_ballots.keys())):
            position = i + 1
            standardized_ballots[voter]["ballots"][position] = None

    return standardized_ballots


def adapt_votes_format_for_schulze_computations(
    standardized_ballots: dict,
) -> tuple[list[str], list[tuple[list[list[str]], int]]]:
    candidate_names = set()

    for voter in standardized_ballots:
        current_ballots = standardized_ballots[voter]["ballots"]
        for position in sorted(current_ballots.keys()):
            app_id = current_ballots[position]
            if app_id is not None:
                candidate_names.add(app_id)

    weighted_ranks = []

    for voter in standardized_ballots:
        current_ballots = standardized_ballots[voter]["ballots"]
        current_ranking = []
        currently_seen_candidates = set()
        for position in sorted(current_ballots.keys()):
            app_id = current_ballots[position]
            if app_id is not None:
                current_ranking.append([app_id])
                currently_seen_candidates.add(app_id)

        remaining_app_ids = list(candidate_names.difference(currently_seen_candidates))
        if remaining_app_ids:
            current_ranking.append(remaining_app_ids)

        current_weight = 1
        weighted_ranks.append((current_ranking, current_weight))

    candidate_names = list(candidate_names)

    return candidate_names, weighted_ranks


def compute_schulze_ranking(standardized_ballots: dict) -> list[list[str]]:
    # Reference: https://github.com/mgp/schulze-method

    import schulze

    (candidate_names, weighted_ranks) = adapt_votes_format_for_schulze_computations(
        standardized_ballots,
    )

    return schulze.compute_ranks(candidate_names, weighted_ranks)


def print_schulze_ranking(
    schulze_ranking: list[list[str]],
    target_release_year: int | str | None = None,
    *,
    use_igdb: bool = False,
) -> None:
    local_database = get_local_database(
        target_release_year=target_release_year,
        use_igdb=use_igdb,
    )

    print()

    def get_game_name(app_id: str) -> str:
        try:
            output_game_name = local_database[app_id]["name"]
        except KeyError:
            output_game_name = get_app_name_for_problematic_app_id(app_id)
        return output_game_name

    offset = 0

    for rank, app_id_group in enumerate(schulze_ranking):
        for app_id in sorted(app_id_group, key=get_game_name):
            game_name = get_game_name(app_id)

            if use_igdb:
                _, app_id_release_date = get_igdb_human_release_dates(
                    app_id,
                    local_database,
                )
                app_url = get_link_to_igdb_website(app_id, local_database)
            else:
                app_id_release_date = steampi.calendar.get_release_date_as_str(app_id)
                app_url = get_link_to_store(app_id)

            if app_id_release_date is None:
                app_id_release_date = "an unknown date"

            print(
                f"{rank + offset + 1:2} | "
                + game_name.strip()
                + " (appID: "
                + app_url
                + ", released on "
                + app_id_release_date
                + ")",
            )

        offset += len(app_id_group) - 1


def get_positions_for_single_voter(ballots: dict) -> list[str]:
    return sorted(ballots.keys())


def get_positions_for_every_voter(ballots_for_every_voter: dict) -> list[str]:
    positions_for_every_voter = set()

    for voter_name in ballots_for_every_voter:
        ballots = ballots_for_every_voter[voter_name]["ballots"]
        positions = get_positions_for_single_voter(ballots)

        positions_for_every_voter.update(positions)

    return sorted(positions_for_every_voter)


def build_standardized_ballots_for_tie(
    app_id_group: list[str],
    standardized_ballots: dict,
    threshold_n: int | None = None,
) -> dict:
    if threshold_n is None:
        threshold_n = 1

    standardized_ballots_for_tied_app_id_group: dict = {}

    for voter_name in standardized_ballots:
        current_ballots = standardized_ballots[voter_name]["ballots"]
        positions = get_positions_for_single_voter(ballots=current_ballots)
        current_app_ids = [current_ballots[position] for position in positions]

        current_num_votes_for_tied_app_ids = sum(
            bool(app_id in current_app_ids) for app_id in app_id_group
        )
        has_voted_for_at_least_n_tied_app_ids = bool(
            current_num_votes_for_tied_app_ids >= threshold_n,
        )

        if has_voted_for_at_least_n_tied_app_ids:
            standardized_ballots_for_tied_app_id_group[voter_name] = {}
            standardized_ballots_for_tied_app_id_group[voter_name]["ballots"] = {}

            new_ballots = [
                current_ballots[position]
                for position in positions
                if current_ballots[position] in app_id_group
            ]

            for i, app_id in enumerate(new_ballots):
                position = i + 1
                standardized_ballots_for_tied_app_id_group[voter_name]["ballots"][
                    position
                ] = app_id
            for i in range(len(new_ballots), len(current_ballots)):
                position = i + 1
                standardized_ballots_for_tied_app_id_group[voter_name]["ballots"][
                    position
                ] = None

    return standardized_ballots_for_tied_app_id_group


def try_to_break_ties_in_app_id_group(
    app_id_group: list[str],
    standardized_ballots: dict,
    threshold_n: int | None = None,
) -> list[list[str]]:
    len(app_id_group)

    if threshold_n is None:
        threshold_n = 1

    standardized_ballots_for_tied_app_id_group = build_standardized_ballots_for_tie(
        app_id_group,
        standardized_ballots,
        threshold_n=threshold_n,
    )

    if not standardized_ballots_for_tied_app_id_group:
        print("Cannot break the tie.")
        schulze_ranking_for_tied_app_id_group = [app_id_group]
    else:
        display_info_about_tie(
            app_id_group,
            standardized_ballots_for_tied_app_id_group,
            threshold_n,
        )
        schulze_ranking_for_tied_app_id_group = compute_schulze_ranking(
            standardized_ballots_for_tied_app_id_group,
        )
        schulze_ranking_for_tied_app_id_group = unwind_ranking(
            input_ranking=schulze_ranking_for_tied_app_id_group,
            app_id_group=app_id_group,
            standardized_ballots=standardized_ballots,
            threshold_n=threshold_n,
        )

    return schulze_ranking_for_tied_app_id_group


def unwind_ranking(
    input_ranking: list[list[str]],
    app_id_group: list[str],
    standardized_ballots: dict,
    threshold_n: int,
) -> list[list[str]]:
    if len(input_ranking) == 1:
        print("Tie still there. Trying again with a higher threshold.")
        output_ranking = try_to_break_ties_in_app_id_group(
            app_id_group,
            standardized_ballots,
            threshold_n=threshold_n + 1,
        )
    else:
        print(f"Tie has been partially broken: {input_ranking}")
        output_ranking = dissect_ranking(
            input_ranking=input_ranking,
            standardized_ballots=standardized_ballots,
        )

    return output_ranking


def dissect_ranking(
    input_ranking: list[list[str]],
    standardized_ballots: dict,
) -> list[list[str]]:
    output_ranking = []

    for small_app_id_group in input_ranking:
        if len(small_app_id_group) == 1:
            output_ranking.append(small_app_id_group)
        else:
            print(
                f"Looking more closely at a **strictly** smaller tie: {small_app_id_group}",
            )
            untied_ranking = try_to_break_ties_in_app_id_group(
                small_app_id_group,
                standardized_ballots,
                threshold_n=None,
            )
            output_ranking += untied_ranking

    return output_ranking


def display_info_about_tie(
    app_id_group: list[str],
    standardized_ballots_for_tied_app_id_group: dict,
    threshold_n: int,
) -> None:
    positions = get_positions_for_every_voter(
        standardized_ballots_for_tied_app_id_group,
    )

    print(
        f"\nInfo regarding tie with appIDs in {app_id_group} with threshold = {threshold_n}",
    )

    for position in positions:
        ballots_at_position = [
            current_vote["ballots"][position]
            for current_vote in standardized_ballots_for_tied_app_id_group.values()
        ]
        count_at_position = Counter(ballots_at_position)
        if any(k is not None for k in count_at_position):
            print(f"Position n°{position} ; {count_at_position}")


def try_to_break_ties_in_schulze_ranking(
    schulze_ranking: list[list[str]],
    standardized_ballots: dict,
) -> list[list[str]]:
    untied_schulze_ranking = []

    for group_no, app_id_group in enumerate(schulze_ranking):
        if len(app_id_group) > 1:
            schulze_ranking_for_tied_app_id_group = try_to_break_ties_in_app_id_group(
                app_id_group,
                standardized_ballots,
                threshold_n=None,
            )

            if len(schulze_ranking_for_tied_app_id_group) > 1:
                print(
                    f"\nAt least one tie has been broken for group n°{group_no + 1}",
                )

            untied_schulze_ranking.extend(schulze_ranking_for_tied_app_id_group)
        else:
            untied_schulze_ranking.append(app_id_group)

    return untied_schulze_ranking


def print_ballot_distribution_for_given_appid(
    app_id_group: list[str],
    standardized_ballots: dict,
) -> None:
    for app_id in app_id_group:
        ballot_distribution = None

        for voter_name in standardized_ballots:
            current_ballots = standardized_ballots[voter_name]["ballots"]

            if ballot_distribution is None:
                ballot_distribution = [0 for _ in range(len(current_ballots))]

            positions = sorted(current_ballots.keys())

            for index, position in enumerate(positions):
                if current_ballots[position] == app_id:
                    ballot_distribution[index] += 1

        print("\nappID:" + app_id, end="\t")
        print("counts of ballots with rank 1, 2, ..., 5:\t", ballot_distribution)


def print_ballot_distribution_for_top_ranked_games(
    schulze_ranking: list[list[str]],
    standardized_ballots: dict,
    num_app_id_groups_to_display: int = 3,
) -> None:
    for app_id_group in schulze_ranking[0:num_app_id_groups_to_display]:
        print_ballot_distribution_for_given_appid(app_id_group, standardized_ballots)


def print_reviews_for_top_ranked_games(
    schulze_ranking: list[list[str]],
    ballots: dict,
    matches: dict,
    goty_field: str = "goty_preferences",
    num_app_id_groups_to_display: int = 3,
) -> None:
    for app_id_group in schulze_ranking[0:num_app_id_groups_to_display]:
        for app_id in app_id_group:
            print_reviews(ballots, matches, app_id, goty_field=goty_field)


def print_voter_stats(
    schulze_ranking: list[list[str]],
    standardized_ballots: dict,
    num_app_id_groups_to_display: int = 7,
    *,
    verbose: bool = True,
) -> None:
    # Check how many people voted for N games which ended up in the top 10 of the GOTY ranking
    # Reference:
    # https://metacouncil.com/threads/metacouncils-pc-games-of-the-year-awards-2018-results.525/page-2

    goty = []
    for app_id_group in schulze_ranking[0:num_app_id_groups_to_display]:
        goty.extend([int(app_id) for app_id in app_id_group])

    print(f"\nVoter stats are displayed based on the top {len(goty)} games")

    max_num_ballots_per_person = 0

    counter = {}
    for voter in standardized_ballots:
        current_ballots = standardized_ballots[voter]["ballots"].values()
        max_num_ballots_per_person = max(
            max_num_ballots_per_person,
            len(current_ballots),
        )

        vote = [int(i) for i in current_ballots if i is not None]
        counter[voter] = sum(i in goty for i in vote)

    for num_votes in reversed(range(max_num_ballots_per_person + 1)):
        ballots = [v for v, c in counter.items() if c == num_votes]
        print(
            f"\n{len(ballots)} ballots included {num_votes} games present in the top {len(goty)}.",
        )
        if verbose:
            print(ballots)


def apply_pipeline(
    input_filename: str,
    release_year: str = "2018",
    *,
    try_to_break_ties: bool = False,
    use_igdb: bool = False,
    retrieve_igdb_data_from_scratch: bool = True,
    apply_hard_coded_extension_and_fixes: bool = True,
    use_levenshtein_distance: bool = True,
    goty_field: str = "goty_preferences",
    year_constraint: str = "equality",
    print_matches: bool = True,
    num_app_id_groups_to_display: int = 7,
) -> bool:
    ballots = load_ballots(input_filename)

    # Standardize ballots

    (standardized_ballots, matches) = standardize_ballots(
        ballots,
        release_year,
        print_after_sort=False,
        use_igdb=use_igdb,
        retrieve_igdb_data_from_scratch=retrieve_igdb_data_from_scratch,
        apply_hard_coded_extension_and_fixes=apply_hard_coded_extension_and_fixes,
        use_levenshtein_distance=use_levenshtein_distance,
        goty_field=goty_field,
        year_constraint=year_constraint,
        print_matches=print_matches,
    )

    whitelisted_ids = load_whitelisted_ids(release_year=release_year, use_igdb=use_igdb)

    standardized_ballots = filter_out_votes_for_wrong_release_years(
        standardized_ballots,
        release_year,
        use_igdb=use_igdb,
        year_constraint=year_constraint,
        whitelisted_ids=whitelisted_ids,
    )

    if not use_igdb:
        standardized_ballots = filter_out_votes_for_early_access_titles(
            standardized_ballots,
            whitelisted_ids=whitelisted_ids,
        )

    standardized_ballots = filter_out_votes_for_hard_coded_reasons(
        standardized_ballots,
        release_year=release_year,
        use_igdb=use_igdb,
    )

    # Apply Schulze method

    schulze_ranking = compute_schulze_ranking(standardized_ballots)

    if try_to_break_ties:
        schulze_ranking = try_to_break_ties_in_schulze_ranking(
            schulze_ranking,
            standardized_ballots,
        )

    print_schulze_ranking(
        schulze_ranking,
        target_release_year=release_year,
        use_igdb=use_igdb,
    )

    print_ballot_distribution_for_top_ranked_games(
        schulze_ranking,
        standardized_ballots,
        num_app_id_groups_to_display=num_app_id_groups_to_display,
    )

    print_voter_stats(
        schulze_ranking,
        standardized_ballots,
        num_app_id_groups_to_display=num_app_id_groups_to_display,
    )

    print_reviews_for_top_ranked_games(
        schulze_ranking,
        ballots,
        matches,
        goty_field=goty_field,
        num_app_id_groups_to_display=num_app_id_groups_to_display,
    )

    return True


if __name__ == "__main__":
    from load_ballots import get_ballot_file_name

    ballot_year = "2020"
    input_filename = get_ballot_file_name(ballot_year, is_anonymized=True)
    use_igdb = True
    retrieve_igdb_data_from_scratch = False
    apply_hard_coded_extension_and_fixes = True
    use_levenshtein_distance = True
    update_credentials = False

    if update_credentials:
        download_latest_credentials(verbose=False)

    # Game of the Year
    goty_field = "goty_preferences"
    release_year = ballot_year
    year_constraint = "equality"

    apply_pipeline(
        input_filename,
        release_year=release_year,
        try_to_break_ties=True,
        use_igdb=use_igdb,
        retrieve_igdb_data_from_scratch=retrieve_igdb_data_from_scratch,
        apply_hard_coded_extension_and_fixes=apply_hard_coded_extension_and_fixes,
        use_levenshtein_distance=use_levenshtein_distance,
        goty_field=goty_field,
        year_constraint=year_constraint,
        num_app_id_groups_to_display=9,
    )
