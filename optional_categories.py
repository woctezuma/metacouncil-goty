from disqualify_vote import is_a_noisy_vote
from igdb_credentials import download_latest_credentials
from igdb_match_names import (
    download_igdb_local_databases,
    get_igdb_human_release_dates,
    get_link_to_igdb_website,
    load_igdb_local_databases,
)
from my_types import Ballots
from parsing_params import get_optional_categories
from steam_store_utils import get_link_to_store


def get_best_optional_categories() -> list[str]:
    return [f"best_{categorie}" for categorie in get_optional_categories()]


def get_optional_ballots(ballots: Ballots, category_name: str) -> list[str]:
    return [
        ballots[voter_name][category_name]
        for voter_name in ballots
        if category_name in ballots[voter_name]
        and ballots[voter_name][category_name] is not None
        and len(ballots[voter_name][category_name]) > 0
    ]


def filter_noise_from_optional_ballots(optional_ballots: list[str]) -> list[str]:
    return [element for element in optional_ballots if not is_a_noisy_vote(element)]


def get_dummy_field() -> str:
    return "dummy_preferences"


def format_optional_ballots_for_igdb_matching(
    optional_ballots: list[str],
    dummy_field: str | None = None,
) -> dict[str, dict[str, dict[int, str]]]:
    if dummy_field is None:
        dummy_field = get_dummy_field()

    dummy_voter = "dummy_voter"

    formatted_optional_ballots: dict[str, dict[str, dict[int, str]]] = {dummy_voter: {}}
    formatted_optional_ballots[dummy_voter][dummy_field] = dict(
        enumerate(optional_ballots),
    )

    return formatted_optional_ballots


def match_optional_ballots(
    optional_ballots: list[str],
    release_year: str | None = None,
    *,
    use_igdb: bool = False,
    retrieve_igdb_data_from_scratch: bool = True,
    apply_hard_coded_extension_and_fixes: bool = True,
    must_be_available_on_pc: bool = False,
    must_be_a_game: bool = False,
    use_levenshtein_distance: bool = True,
) -> list[str]:
    import steampi.calendar

    from extend_steamspy import load_extended_steamspy_database
    from match_names import find_closest_app_id

    seen_game_names = set()
    matches: dict = {}
    matched_optional_ballots = []

    dummy_field = get_dummy_field()

    formatted_optional_ballots = format_optional_ballots_for_igdb_matching(
        optional_ballots,
        dummy_field=dummy_field,
    )

    if use_igdb:
        # Code inspired from standardize_ballots() in match_names.py

        if retrieve_igdb_data_from_scratch:
            # Caveat: it is mandatory to set 'extend_previous_databases' to True, because:
            # i) databases are shared between GotY and optional categories, and we want to KEEP the data for GotY,
            # ii) databases are shared between optional categories, and there is a loop over the optional categories.
            extend_previous_databases = True

            igdb_match_database, local_database = download_igdb_local_databases(
                formatted_optional_ballots,
                release_year=release_year,
                apply_hard_coded_extension_and_fixes=apply_hard_coded_extension_and_fixes,
                extend_previous_databases=extend_previous_databases,
                must_be_available_on_pc=must_be_available_on_pc,
                must_be_a_game=must_be_a_game,
                goty_field=dummy_field,
            )
        else:
            igdb_match_database, local_database = load_igdb_local_databases(
                formatted_optional_ballots,
                release_year=release_year,
                apply_hard_coded_extension_and_fixes=apply_hard_coded_extension_and_fixes,
                must_be_available_on_pc=must_be_available_on_pc,
                must_be_a_game=must_be_a_game,
                goty_field=dummy_field,
            )
    else:
        igdb_match_database = {}
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
                    app_id = str(igdb_best_matched_id)

                    app_name = local_database[app_id]["name"]

                    _, app_id_release_date = get_igdb_human_release_dates(
                        app_id,
                        local_database,
                    )
                    app_url = get_link_to_igdb_website(app_id, local_database)
                else:
                    app_id = None
                    app_name = None
                    app_id_release_date = None
                    app_url = None

            else:
                # Using SteamSpy

                (closest_app_id, _) = find_closest_app_id(
                    raw_name,
                    steamspy_database=local_database,
                    use_levenshtein_distance=use_levenshtein_distance,
                )

                app_id = closest_app_id[0]

                app_name = local_database[app_id]["name"]

                app_id_release_date = steampi.calendar.get_release_date_as_str(app_id)

                app_url = get_link_to_store(app_id)

            if app_id_release_date is None:
                app_id_release_date = "an unknown date"

            matches[raw_name] = {}
            matches[raw_name]["matched_appID"] = app_id
            matches[raw_name]["matched_name"] = app_name
            matches[raw_name]["matched_release_date"] = app_id_release_date
            matches[raw_name]["matched_url"] = app_url

            id_description = "IGDB id" if use_igdb else "AppID"

            print(
                "\t{} ---> {}: {}\t;\t{} ({})".format(
                    raw_name,
                    id_description,
                    matches[raw_name]["matched_appID"],
                    matches[raw_name]["matched_name"],
                    matches[raw_name]["matched_release_date"],
                ),
            )

        my_str = "{} (appID: {}, released on {})".format(
            matches[raw_name]["matched_name"],
            matches[raw_name]["matched_url"],
            matches[raw_name]["matched_release_date"],
        )

        matched_optional_ballots.append(my_str)

    return matched_optional_ballots


def count_optional_ballots(optional_ballots: list[str]) -> dict[str, int]:
    optional_counts: dict[str, int] = {}

    for element in optional_ballots:
        try:
            optional_counts[element] += 1
        except KeyError:
            optional_counts[element] = 1

    return optional_counts


def compute_ranking_based_on_optional_ballots(
    optional_ballots: list[str],
) -> list[tuple[str, int]]:
    optional_counts = count_optional_ballots(optional_ballots)

    # Reference: https://stackoverflow.com/a/37693603
    return sorted(
        optional_counts.items(),
        key=lambda x: (-x[1], x[0]),
        reverse=False,
    )


def pretty_display(ranking: list[tuple[str, int]]) -> None:
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

        my_str = " with #votes = " if num_votes > 1 else " with #vote = "

        print(f"{rank:2} | " + game_name.strip() + my_str + str(num_votes))


def display_optional_ballots(
    input_filename: str,
    *,
    filter_noise: bool = True,
    release_year: str | None = None,
    use_igdb: bool = False,
    retrieve_igdb_data_from_scratch: bool = True,
    apply_hard_coded_extension_and_fixes: bool = True,
    use_levenshtein_distance: bool = True,
) -> bool:
    from load_ballots import load_ballots

    ballots = load_ballots(input_filename)

    for category_name in get_best_optional_categories():
        print("\nCategory: " + category_name)

        optional_ballots = get_optional_ballots(ballots, category_name)

        if filter_noise:
            optional_ballots = filter_noise_from_optional_ballots(optional_ballots)

        optional_ballots = match_optional_ballots(
            optional_ballots,
            release_year=release_year,
            use_igdb=use_igdb,
            retrieve_igdb_data_from_scratch=retrieve_igdb_data_from_scratch,
            apply_hard_coded_extension_and_fixes=apply_hard_coded_extension_and_fixes,
            use_levenshtein_distance=use_levenshtein_distance,
        )

        ranking = compute_ranking_based_on_optional_ballots(optional_ballots)
        pretty_display(ranking)

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

    # Optional Categories of the Year
    release_year = ballot_year

    display_optional_ballots(
        input_filename,
        filter_noise=True,
        release_year=release_year,
        use_igdb=use_igdb,
        retrieve_igdb_data_from_scratch=retrieve_igdb_data_from_scratch,
        apply_hard_coded_extension_and_fixes=apply_hard_coded_extension_and_fixes,
        use_levenshtein_distance=use_levenshtein_distance,
    )
