import steampi.calendar
import steampi.text_distances

from disqualify_vote import is_a_noisy_vote
from extend_steamspy import (
    get_app_name_for_problematic_app_id,
    get_release_year_for_problematic_app_id,
    load_extended_steamspy_database,
)
from hard_coded_matches import (
    check_database_of_problematic_game_names,
    find_hard_coded_app_id,
)
from igdb_match_names import (
    download_igdb_local_databases,
    load_igdb_local_databases,
    print_igdb_matches,
    transform_structure_of_matches,
)


def constrain_app_id_search_by_year(
    dist: dict[str, float],
    sorted_app_ids: list[str],
    release_year: str | None,
    max_num_tries_for_year: int,
    year_constraint: str | None = "equality",
) -> list[str]:
    filtered_sorted_app_ids = sorted_app_ids.copy()

    if release_year is not None and year_constraint is not None:
        first_match = filtered_sorted_app_ids[0]
        dist_reference = dist[first_match]

        if dist_reference > 0:
            # Check release year to remove possible mismatches. For instance, with input Warhammer 2 and two choices:
            # Warhammer & Warhammer II, we would only keep the game released in the target year (2017), i.e. the sequel.
            is_the_first_match_released_in_a_wrong_year = True
            iter_count = 0
            while (
                is_the_first_match_released_in_a_wrong_year
                and (iter_count < max_num_tries_for_year)
                and filtered_sorted_app_ids
            ):
                first_match = filtered_sorted_app_ids[0]
                try:
                    matched_release_year = steampi.calendar.get_release_year(
                        first_match,
                    )
                except ValueError:
                    matched_release_year = get_release_year_for_problematic_app_id(
                        app_id=first_match,
                    )

                if year_constraint == "equality":
                    # We want the matched release year to be equal to the target release year.
                    # NB: this is useful to compute the Game of the Year.
                    is_the_first_match_released_in_a_wrong_year = bool(
                        matched_release_year != int(release_year),
                    )
                elif year_constraint == "minimum":
                    # We want the matched release year to be greater than or equal to the target release year.
                    # NB: this should be useful to compute the Game of the last Decade.
                    is_the_first_match_released_in_a_wrong_year = bool(
                        matched_release_year < int(release_year),
                    )
                elif year_constraint == "maximum":
                    # We want the matched release year to be less than or equal to the target release year.
                    is_the_first_match_released_in_a_wrong_year = bool(
                        matched_release_year > int(release_year),
                    )
                else:
                    # We do not want to apply any constraint.
                    is_the_first_match_released_in_a_wrong_year = False

                if is_the_first_match_released_in_a_wrong_year:
                    filtered_sorted_app_ids.pop(0)

                iter_count += 1
            # Reset if we could not find a match released in the target year
            if is_the_first_match_released_in_a_wrong_year:
                filtered_sorted_app_ids = sorted_app_ids

    return filtered_sorted_app_ids


def apply_hard_coded_fixes_to_app_id_search(
    game_name_input: str,
    filtered_sorted_app_ids: list[str],
    num_closest_neighbors: int,
) -> str:
    closest_app_id = [find_hard_coded_app_id(game_name_input)]
    if num_closest_neighbors > 1:
        closest_app_id.extend(filtered_sorted_app_ids[0 : (num_closest_neighbors - 1)])

    return closest_app_id


def get_default_distance_cut_off_for_difflib() -> float:
    # Reference: https://docs.python.org/3/library/difflib.html

    similarity_cut_off = 0.6

    return 1 - similarity_cut_off


def find_closest_app_id(
    game_name_input: str,
    steamspy_database: dict,
    release_year: int | str | None = None,
    num_closest_neighbors: int = 1,
    max_num_tries_for_year: int = 2,
    *,
    use_levenshtein_distance: bool = True,
    year_constraint: str = "equality",
    is_steamspy_api_paginated: bool = True,
) -> tuple[list[str], list[int]]:
    if use_levenshtein_distance:
        # n is not used by Levenshtein distance.
        n = None
    else:
        # n is only used by difflib.
        # NB: difflib may not return as many neighbors as requested, because difflib relies on a similarity cut-off.
        n = num_closest_neighbors + max_num_tries_for_year

    (sorted_app_ids, dist) = steampi.text_distances.find_most_similar_game_names(
        game_name_input,
        steamspy_database,
        use_levenshtein_distance=use_levenshtein_distance,
        n=n,
    )

    filtered_sorted_app_ids = sorted_app_ids

    if release_year is not None and year_constraint is not None:
        filtered_sorted_app_ids = constrain_app_id_search_by_year(
            dist,
            sorted_app_ids,
            release_year,
            max_num_tries_for_year,
            year_constraint=year_constraint,
        )

    closest_app_id = filtered_sorted_app_ids[0:num_closest_neighbors]

    if check_database_of_problematic_game_names(game_name_input):
        closest_app_id = apply_hard_coded_fixes_to_app_id_search(
            game_name_input,
            filtered_sorted_app_ids,
            num_closest_neighbors,
        )

        if not use_levenshtein_distance or is_steamspy_api_paginated:
            # With difflib, computations are more expensive than with Levenshtein distance, therefore dist only contains
            # distances for a few entries. So, we set the distance to 0.4 (default cut-off) for all the other entries.
            #
            # Edit: moreover, due to the pagination recently adopted by SteamSpy API, dist misses many entries nowadays.
            for app_id in closest_app_id:
                if app_id not in dist:
                    dist[app_id] = get_default_distance_cut_off_for_difflib()

    closest_distance = [dist[app_id] for app_id in closest_app_id]

    return closest_app_id, closest_distance


def precompute_matches(
    raw_votes: dict,
    release_year: int | None = None,
    num_closest_neighbors: int = 3,
    max_num_tries_for_year: int = 2,
    *,
    use_levenshtein_distance: bool = True,
    year_constraint: str = "equality",
    goty_field: str = "goty_preferences",
    is_steamspy_api_paginated: bool = True,
) -> dict:
    seen_game_names = set()
    matches = {}

    steamspy_database = load_extended_steamspy_database()

    for voter in raw_votes:
        for raw_name in raw_votes[voter][goty_field].values():
            if raw_name not in seen_game_names:
                seen_game_names.add(raw_name)

                if not is_a_noisy_vote(raw_name):
                    (closest_app_id, closest_distance) = find_closest_app_id(
                        raw_name,
                        steamspy_database,
                        release_year,
                        num_closest_neighbors,
                        max_num_tries_for_year,
                        use_levenshtein_distance=use_levenshtein_distance,
                        year_constraint=year_constraint,
                        is_steamspy_api_paginated=is_steamspy_api_paginated,
                    )

                    # Due to the pagination recently adopted by SteamSpy API, dist misses many entries nowadays.
                    if is_steamspy_api_paginated:
                        for app_id in closest_app_id:
                            if app_id not in steamspy_database:
                                steamspy_database[app_id] = {}
                                steamspy_database[app_id]["name"] = (
                                    get_app_name_for_problematic_app_id(app_id)
                                )

                    element = {}
                    element["input_name"] = raw_name
                    element["matched_appID"] = closest_app_id
                    element["matched_name"] = [
                        steamspy_database[appID]["name"] for appID in closest_app_id
                    ]
                    element["match_distance"] = closest_distance

                    matches[raw_name] = element

    return matches


def display_matches(matches: dict, *, print_after_sort: bool = True) -> None:
    # Index of the neighbor used to sort keys of the matches dictionary
    neighbor_reference_index = 0

    if print_after_sort:
        sorted_keys = sorted(
            matches.keys(),
            key=lambda x: matches[x]["match_distance"][neighbor_reference_index]
            / (1 + len(matches[x]["input_name"])),
        )
    else:
        sorted_keys = matches.keys()

    for game in sorted_keys:
        element = matches[game]

        dist_reference = element["match_distance"][neighbor_reference_index]
        game_name = element["input_name"]

        if dist_reference > 0 or check_database_of_problematic_game_names(game_name):
            print(
                "\n"
                + game_name
                + " ("
                + "length:"
                + str(len(game_name))
                + ")"
                + " ---> ",
                end="",
            )
            for neighbor_index in range(len(element["match_distance"])):
                dist = element["match_distance"][neighbor_index]
                print(
                    element["matched_name"][neighbor_index]
                    + " (appID: "
                    + element["matched_appID"][neighbor_index]
                    + " ; "
                    + "distance:"
                    + str(dist)
                    + ")",
                    end="\t",
                )

    print()


def normalize_votes(
    raw_votes: dict,
    matches: dict,
    goty_field: str = "goty_preferences",
) -> dict:
    # Index of the first neighbor
    neighbor_reference_index = 0

    normalized_votes = {}

    for voter_name in raw_votes:
        normalized_votes[voter_name] = {}
        normalized_votes[voter_name]["ballots"] = {}
        normalized_votes[voter_name]["distances"] = {}
        for position, game_name in raw_votes[voter_name][goty_field].items():
            if game_name in matches:
                # Display game name before error due to absence of any matched IGDB ID, in order to make it easier to
                # incrementally and manually add hard-coded matches:
                if len(matches[game_name]["matched_appID"]) == 0:
                    print(f"[Warning] no match found for {game_name}")

                normalized_votes[voter_name]["ballots"][position] = matches[game_name][
                    "matched_appID"
                ][neighbor_reference_index]
                normalized_votes[voter_name]["distances"][position] = matches[
                    game_name
                ]["match_distance"][neighbor_reference_index]
            else:
                normalized_votes[voter_name]["ballots"][position] = None
                normalized_votes[voter_name]["distances"][position] = None

    return normalized_votes


def standardize_ballots(
    ballots: dict,
    release_year: int | str | None,
    *,
    print_after_sort: bool = True,
    use_igdb: bool = False,
    retrieve_igdb_data_from_scratch: bool = True,
    apply_hard_coded_extension_and_fixes: bool = True,
    use_levenshtein_distance: bool = True,
    extend_previous_databases: bool = True,
    must_be_available_on_pc: bool = True,
    must_be_a_game: bool = True,
    goty_field: str = "goty_preferences",
    year_constraint: str = "equality",
    print_matches: bool = True,
    verbose: bool = False,
) -> tuple[dict, dict]:
    if use_igdb:
        # Using IGDB

        if retrieve_igdb_data_from_scratch:
            # By default, we extend the previous databases. If you do not want to, delete them before running the code.
            igdb_match_database, igdb_local_database = download_igdb_local_databases(
                ballots,
                release_year=release_year,
                apply_hard_coded_extension_and_fixes=apply_hard_coded_extension_and_fixes,
                extend_previous_databases=extend_previous_databases,
                must_be_available_on_pc=must_be_available_on_pc,
                must_be_a_game=must_be_a_game,
                goty_field=goty_field,
                year_constraint=year_constraint,
                verbose=verbose,
            )
        else:
            igdb_match_database, igdb_local_database = load_igdb_local_databases(
                ballots,
                release_year=release_year,
                apply_hard_coded_extension_and_fixes=apply_hard_coded_extension_and_fixes,
                must_be_available_on_pc=must_be_available_on_pc,
                must_be_a_game=must_be_a_game,
                goty_field=goty_field,
                year_constraint=year_constraint,
                verbose=verbose,
            )

        if print_matches:
            print_igdb_matches(
                igdb_match_database,
                igdb_local_database,
                constrained_release_year=release_year,
                year_constraint=year_constraint,
            )

        matches = transform_structure_of_matches(
            igdb_match_database,
            igdb_local_database,
        )

    else:
        # Using SteamSpy

        matches = precompute_matches(
            ballots,
            release_year=release_year,
            num_closest_neighbors=3,
            max_num_tries_for_year=2,
            use_levenshtein_distance=use_levenshtein_distance,
            year_constraint=year_constraint,
            goty_field=goty_field,
        )

        if print_matches:
            display_matches(matches, print_after_sort)

    standardized_ballots = normalize_votes(ballots, matches, goty_field=goty_field)

    return (standardized_ballots, matches)


if __name__ == "__main__":
    from load_ballots import get_ballot_file_name, load_ballots

    ballot_year = "2018"
    input_filename = get_ballot_file_name(ballot_year)
    use_levenshtein_distance = True

    ballots = load_ballots(input_filename)
    (standardized_ballots, matches) = standardize_ballots(
        ballots,
        release_year=ballot_year,
        use_levenshtein_distance=use_levenshtein_distance,
    )
