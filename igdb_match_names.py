import copy
import time

from disqualify_vote import is_a_noisy_vote
from extend_igdb import extend_both_igdb_databases, extend_igdb_match_database
from igdb_databases import (
    load_igdb_local_database,
    load_igdb_match_database,
    save_igdb_local_database,
    save_igdb_match_database,
)
from igdb_look_up import look_up_game_name, wait_for_cooldown
from igdb_utils import get_pc_platform_no, get_pc_platform_range, get_steam_service_no
from load_ballots import load_ballots


def get_link_to_igdb_website(igdb_id, igdb_local_database, hide_dummy_app_id=True):
    igdb_base_url = "https://www.igdb.com/games/"

    igdb_id_as_str = str(igdb_id)

    igdb_data = igdb_local_database[igdb_id_as_str]
    slug = igdb_data["slug"]

    if int(igdb_id) > 0:
        link_to_store = (
            "[URL=" + igdb_base_url + slug + "/]" + igdb_id_as_str + "[/URL]"
        )
    else:
        if hide_dummy_app_id:
            link_to_store = "n/a"
        else:
            link_to_store = igdb_id_as_str
    return link_to_store


def get_igdb_human_release_dates(igdb_id, igdb_local_database):
    igdb_id_as_str = str(igdb_id)

    igdb_data = igdb_local_database[igdb_id_as_str]

    try:
        human_release_dates = {
            date["human"]
            for date in igdb_data["release_dates"]
            if "human" in date and (date["platform"] in get_pc_platform_range())
        }
    except KeyError:
        # Unknown release date
        human_release_dates = [None]

    if len(human_release_dates) > 0:
        human_release_date_to_remember = max(human_release_dates)
    else:
        human_release_date_to_remember = None

    return human_release_dates, human_release_date_to_remember


def get_igdb_release_years(igdb_data, target_release_year=None):
    try:
        release_years = {
            date["y"]
            for date in igdb_data["release_dates"]
            if "y" in date and (date["platform"] in get_pc_platform_range())
        }
    except KeyError:
        # Unknown release date
        release_years = [None]

    year_to_remember = -1

    if target_release_year is not None:
        target_release_year_as_int = int(target_release_year)

        if len(release_years) > 0:
            if target_release_year_as_int in release_years:
                year_to_remember = target_release_year_as_int
            else:
                the_most_recent_date = max(release_years)
                year_to_remember = the_most_recent_date

                if year_to_remember is None:
                    year_to_remember = -1

    return release_years, year_to_remember


def format_game_name_for_igdb(raw_name, verbose=True):
    formatted_game_name_for_igdb = raw_name

    for character in ["®", "~", "'", ": ", " - ", "!", "™", " / "]:
        formatted_game_name_for_igdb = formatted_game_name_for_igdb.replace(
            character,
            " ",
        )

    formatted_game_name_for_igdb = formatted_game_name_for_igdb.strip()

    if verbose:
        print(
            "Game name is reformatted from {} to {}".format(
                raw_name,
                formatted_game_name_for_igdb,
            ),
        )

    return formatted_game_name_for_igdb


def match_names_with_igdb(
    raw_votes,
    release_year=None,
    must_be_available_on_pc=True,
    must_be_a_game=True,
    goty_field="goty_preferences",
    year_constraint="equality",
    verbose=True,
):
    seen_game_names = set()
    igdb_match_database = {}
    igdb_local_database = {}
    num_requests = 0
    start_time = time.time()

    for voter in raw_votes:
        for raw_name in raw_votes[voter][goty_field].values():
            if raw_name not in seen_game_names:
                seen_game_names.add(raw_name)

                if not is_a_noisy_vote(raw_name):
                    formatted_game_name_for_igdb = format_game_name_for_igdb(raw_name)

                    igdb_matches = look_up_game_name(
                        game_name=formatted_game_name_for_igdb,
                        enforced_year=release_year,
                        must_be_available_on_pc=must_be_available_on_pc,
                        must_be_a_game=must_be_a_game,
                        year_constraint=year_constraint,
                    )
                    num_requests += 1
                    start_time = wait_for_cooldown(
                        num_requests=num_requests,
                        start_time=start_time,
                    )

                    try:
                        igdb_best_match = igdb_matches[0]
                    except IndexError:
                        print(f"Relaxing the year constraint for {raw_name}")

                        igdb_matches = look_up_game_name(
                            game_name=formatted_game_name_for_igdb,
                            enforced_year=None,
                            must_be_available_on_pc=must_be_available_on_pc,
                            must_be_a_game=must_be_a_game,
                        )
                        num_requests += 1
                        start_time = wait_for_cooldown(
                            num_requests=num_requests,
                            start_time=start_time,
                        )

                        try:
                            igdb_best_match = igdb_matches[0]
                        except IndexError:
                            print(
                                "Relaxing all of the constraints for {}".format(
                                    raw_name,
                                ),
                            )

                            igdb_matches = look_up_game_name(
                                game_name=formatted_game_name_for_igdb,
                                enforced_year=None,
                                must_be_available_on_pc=False,
                                must_be_a_game=False,
                            )
                            num_requests += 1
                            start_time = wait_for_cooldown(
                                num_requests=num_requests,
                                start_time=start_time,
                            )

                    igdb_matched_ids = []

                    for element in igdb_matches:
                        igdb_id = element["id"]
                        igdb_data = element

                        igdb_matched_ids.append(igdb_id)

                        igdb_local_database[igdb_id] = igdb_data

                    # Caveat: For now, matches returned by match_names_with_igdb() does not have the same structure as
                    #         matches returned by precompute_matches(). cf. transform_structure_of_matches()
                    igdb_match_database[raw_name] = igdb_matched_ids

    if verbose:
        recently_matched_game_names = sorted(
            [name for name in seen_game_names if not is_a_noisy_vote(name)],
        )
        if len(recently_matched_game_names) > 0:
            s = [
                f"{i + 1}) {name}" for i, name in enumerate(recently_matched_game_names)
            ]
            print("[Changelog]\n{}\n".format("\n".join(s)))

    return igdb_match_database, igdb_local_database


def print_igdb_matches(
    igdb_match_database,
    igdb_local_database,
    constrained_release_year=None,
    year_constraint="equality",
):
    sorted_input_names = sorted(igdb_match_database.keys())

    for raw_name in sorted_input_names:
        igdb_matched_ids = igdb_match_database[raw_name]

        try:
            igdb_best_matched_id = igdb_matched_ids[0]
        except IndexError:
            igdb_best_matched_id = None

        if igdb_best_matched_id is not None:
            igdb_data = igdb_local_database[str(igdb_best_matched_id)]

            release_years, year_to_remember = get_igdb_release_years(
                igdb_data,
                target_release_year=constrained_release_year,
            )

            if len(release_years) > 1:
                displayed_release_years = sorted(release_years)
                print(f"[!]\tSeveral release years are found for {raw_name}.")
            else:
                try:
                    displayed_release_years = list(release_years)[0]
                except IndexError:
                    displayed_release_years = None

            if constrained_release_year is not None:
                cleaned_release_years = [
                    int(year) for year in release_years if year is not None
                ]

                if year_constraint == "equality":
                    constraint_is_okay = any(
                        year == int(constrained_release_year)
                        for year in cleaned_release_years
                    )
                elif year_constraint == "minimum":
                    constraint_is_okay = any(
                        year >= int(constrained_release_year)
                        for year in cleaned_release_years
                    )
                elif year_constraint == "maximum":
                    constraint_is_okay = any(
                        year <= int(constrained_release_year)
                        for year in cleaned_release_years
                    )
                else:
                    # There is an issue if a constrained release year is provided without a valid type of constraint.
                    constraint_is_okay = False

                if not constraint_is_okay:
                    print(
                        "[!]\tRelease year(s) ({}) do not match the ballot year ({}, constraint:{}) for {}.".format(
                            displayed_release_years,
                            constrained_release_year,
                            year_constraint,
                            raw_name,
                        ),
                    )

            print(
                "\t{} ---> IGDB id: {}\t;\t{} ({})".format(
                    raw_name,
                    igdb_data["id"],
                    igdb_data["name"],
                    displayed_release_years,
                ),
            )
        else:
            print(f"[X]\t{raw_name}")

    return


def merge_databases(new_database, previous_database):
    merged_database = new_database

    for element in previous_database:
        if element not in merged_database:
            merged_database[element] = previous_database[element]

    return merged_database


def download_igdb_local_databases(
    ballots,
    release_year=None,
    apply_hard_coded_extension_and_fixes=True,
    extend_previous_databases=True,
    must_be_available_on_pc=True,
    must_be_a_game=True,
    goty_field="goty_preferences",
    year_constraint="equality",
    verbose=True,
):
    igdb_match_database, igdb_local_database = match_names_with_igdb(
        ballots,
        release_year=release_year,
        must_be_available_on_pc=must_be_available_on_pc,
        must_be_a_game=must_be_a_game,
        goty_field=goty_field,
        year_constraint=year_constraint,
    )

    # Merge with previous databases, if they were passed to the function as optional parameters
    if extend_previous_databases:
        try:
            previous_igdb_match_database = load_igdb_match_database(
                release_year=release_year,
            )
        except FileNotFoundError:
            previous_igdb_match_database = {}

        try:
            previous_igdb_local_database = load_igdb_local_database(
                release_year=release_year,
            )
        except FileNotFoundError:
            previous_igdb_local_database = {}

        igdb_match_database = merge_databases(
            igdb_match_database,
            previous_database=previous_igdb_match_database,
        )

        igdb_local_database = merge_databases(
            igdb_local_database,
            previous_database=previous_igdb_local_database,
        )

    # Save data before applying any hard-coded change
    num_queries = 0
    for voter_name in ballots:
        for _game_position, game_name in ballots[voter_name][goty_field].items():
            if not is_a_noisy_vote(game_name):
                num_queries += 1

    save_to_disk = bool(num_queries > 0)

    if save_to_disk:
        save_igdb_match_database(data=igdb_match_database, release_year=release_year)

        save_igdb_local_database(data=igdb_local_database, release_year=release_year)

    # Apply hard-coded changes: i) database extension and ii) fixes to name matching

    if apply_hard_coded_extension_and_fixes:
        igdb_match_database, igdb_local_database = extend_both_igdb_databases(
            release_year=release_year,
            igdb_match_database=igdb_match_database,
            igdb_local_database=igdb_local_database,
            verbose=verbose,
        )

    return igdb_match_database, igdb_local_database


def figure_out_ballots_with_missing_data(
    ballots,
    igdb_match_database=None,
    release_year=None,
    goty_field="goty_preferences",
    verbose=False,
):
    # The extended match database is loaded so that there is no IGDB query for games which are already manually matched.
    # This means that we could work in offline mode once the manual matches cover all the empty results of IGDB queries.
    #
    # If you want to try again to automatically match these games, backup and delete the manual fixes to match database.
    extended_igdb_match_database = extend_igdb_match_database(
        release_year=release_year,
        igdb_match_database=igdb_match_database,
        verbose=verbose,
    )

    # Reference: https://stackoverflow.com/a/5105554
    new_ballots = copy.deepcopy(ballots)

    for voter_name in new_ballots:
        for game_position, game_name in new_ballots[voter_name][goty_field].items():
            if (
                game_name in extended_igdb_match_database
                and len(extended_igdb_match_database[game_name]) > 0
            ):
                new_ballots[voter_name][goty_field][game_position] = ""

    return new_ballots


def download_igdb_data_for_ballots_with_missing_data(
    new_ballots,
    release_year=None,
    apply_hard_coded_extension_and_fixes=True,
    must_be_available_on_pc=True,
    must_be_a_game=True,
    goty_field="goty_preferences",
    year_constraint="equality",
    verbose=False,
):
    # Caveat: it is mandatory to set 'extend_previous_databases' to True, if you want to:
    # - first download data for new ballots,
    # - then merge the result with databases stored on the disk for the previously seen ballots,
    # Otherwise, you will obtain incomplete databases (for new ballots), and overwrite the stored databases, likely
    # losing progress in the process.
    extend_previous_databases = True

    igdb_match_database, igdb_local_database = download_igdb_local_databases(
        new_ballots,
        release_year=release_year,
        apply_hard_coded_extension_and_fixes=apply_hard_coded_extension_and_fixes,
        extend_previous_databases=extend_previous_databases,
        must_be_available_on_pc=must_be_available_on_pc,
        must_be_a_game=must_be_a_game,
        goty_field=goty_field,
        year_constraint=year_constraint,
        verbose=verbose,
    )

    return igdb_match_database, igdb_local_database


def load_igdb_local_databases(
    ballots,
    release_year=None,
    apply_hard_coded_extension_and_fixes=True,
    must_be_available_on_pc=True,
    must_be_a_game=True,
    goty_field="goty_preferences",
    year_constraint="equality",
    verbose=False,
):
    try:
        igdb_match_database = load_igdb_match_database(release_year=release_year)
    except FileNotFoundError:
        igdb_match_database = {}

    # Download missing data for some ballots

    new_ballots = figure_out_ballots_with_missing_data(
        ballots=ballots,
        igdb_match_database=igdb_match_database,
        release_year=release_year,
        goty_field=goty_field,
        verbose=verbose,
    )

    (
        igdb_match_database,
        igdb_local_database,
    ) = download_igdb_data_for_ballots_with_missing_data(
        new_ballots=new_ballots,
        release_year=release_year,
        apply_hard_coded_extension_and_fixes=apply_hard_coded_extension_and_fixes,
        must_be_available_on_pc=must_be_available_on_pc,
        must_be_a_game=must_be_a_game,
        goty_field=goty_field,
        year_constraint=year_constraint,
        verbose=verbose,
    )

    # Apply hard-coded changes: i) database extension and ii) fixes to name matching

    if apply_hard_coded_extension_and_fixes:
        igdb_match_database, igdb_local_database = extend_both_igdb_databases(
            release_year=release_year,
            igdb_match_database=igdb_match_database,
            igdb_local_database=igdb_local_database,
            verbose=verbose,
        )

    if verbose:
        print_igdb_matches(
            igdb_match_database,
            igdb_local_database,
            constrained_release_year=release_year,
            year_constraint=year_constraint,
        )

    return igdb_match_database, igdb_local_database


def transform_structure_of_matches(igdb_match_database, igdb_local_database):
    # Retro-compatibility with code written for SteamSpy

    matches = {}

    for raw_name in igdb_match_database:
        igdb_matched_ids = [str(igdb_id) for igdb_id in igdb_match_database[raw_name]]

        igdb_matched_pc_release_dates = []
        for igdb_id_as_str in igdb_matched_ids:
            try:
                release_dates = igdb_local_database[igdb_id_as_str]["release_dates"]
            except KeyError:
                continue
            for element in release_dates:
                if element["platform"] == get_pc_platform_no():
                    release_date = element["human"]
                    igdb_matched_pc_release_dates.append(release_date)

        steam_matched_ids = []
        for igdb_id_as_str in igdb_matched_ids:
            try:
                external_games = igdb_local_database[igdb_id_as_str]["external_games"]
            except KeyError:
                continue
            for element in external_games:
                if element["category"] == get_steam_service_no():
                    steam_app_id = element["uid"]
                    steam_matched_ids.append(steam_app_id)

        igdb_matched_slugs = [
            igdb_local_database[igdb_id_as_str]["slug"]
            for igdb_id_as_str in igdb_matched_ids
        ]

        igdb_matched_names = [
            igdb_local_database[igdb_id_as_str]["name"]
            for igdb_id_as_str in igdb_matched_ids
        ]

        dummy_distances = [None for _ in igdb_matched_ids]

        element = {}
        element["input_name"] = raw_name
        element["matched_appID"] = (
            igdb_matched_ids  # For IGDB, this is IGDB ID. For SteamSpy, this is Steam appID.
        )
        element["matched_pc_release_date"] = igdb_matched_pc_release_dates
        element["matched_steam_appID"] = (
            steam_matched_ids  # Steam urls use an appID, which is the game ID on the store
        )
        element["matched_slug"] = (
            igdb_matched_slugs  # IGDB urls rely on the slug, which is an url-friendly game name.
        )
        element["matched_name"] = igdb_matched_names
        element["match_distance"] = dummy_distances

        matches[raw_name] = element

    return matches


def main():
    from load_ballots import get_ballot_file_name

    ballot_year = "2018"
    input_filename = get_ballot_file_name(ballot_year, is_anonymized=True)
    ballots = load_ballots(input_filename)

    release_year = ballot_year

    # Before manual fixes

    igdb_match_database, igdb_local_database = load_igdb_local_databases(
        ballots,
        release_year=release_year,
        apply_hard_coded_extension_and_fixes=False,
    )

    print_igdb_matches(
        igdb_match_database,
        igdb_local_database,
        constrained_release_year=release_year,
    )

    # After manual fixes

    igdb_match_database, igdb_local_database = load_igdb_local_databases(
        ballots,
        release_year=release_year,
        apply_hard_coded_extension_and_fixes=True,
    )

    print_igdb_matches(
        igdb_match_database,
        igdb_local_database,
        constrained_release_year=release_year,
    )

    return True


if __name__ == "__main__":
    main()
