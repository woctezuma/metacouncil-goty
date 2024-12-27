from igdb_credentials import download_latest_credentials
from load_ballots import load_ballots
from match_names import standardize_ballots
from parsing_params import get_optional_categories
from schulze_goty import (
    compute_schulze_ranking,
    print_ballot_distribution_for_top_ranked_games,
    print_schulze_ranking,
    print_voter_stats,
    try_to_break_ties_in_schulze_ranking,
)


def apply_pipeline_for_optional_categories(
    input_filename,
    release_year="2020",
    try_to_break_ties=True,
    use_igdb=True,
    retrieve_igdb_data_from_scratch=True,
    apply_hard_coded_extension_and_fixes=True,
    use_levenshtein_distance=True,
    goty_field="goty_preferences",
    year_constraint="equality",
    print_matches=True,
    num_app_id_groups_to_display=3,
    must_be_available_on_pc=False,
    must_be_a_game=False,
    verbose=False,
):
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
        must_be_available_on_pc=must_be_available_on_pc,
        must_be_a_game=must_be_a_game,
        goty_field=goty_field,
        year_constraint=year_constraint,
        print_matches=print_matches,
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

    if verbose:
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

    return True


if __name__ == "__main__":
    from load_ballots import get_ballot_file_name

    ballot_year = "2020"
    input_filename = get_ballot_file_name(ballot_year, is_anonymized=True)

    update_credentials = False

    if update_credentials:
        download_latest_credentials(verbose=False)

    # Optional Categories of the Year
    release_year = ballot_year
    retrieve_igdb_data_from_scratch = False
    apply_hard_coded_extension_and_fixes = True
    print_matches = False

    for categorie in get_optional_categories():
        goty_field = f"{categorie}_preferences"
        year_constraint = "equality"

        must_be_available_on_pc = False
        must_be_a_game = False

        print("Category: " + categorie)
        apply_pipeline_for_optional_categories(
            input_filename,
            release_year=release_year,
            try_to_break_ties=True,
            retrieve_igdb_data_from_scratch=retrieve_igdb_data_from_scratch,
            apply_hard_coded_extension_and_fixes=apply_hard_coded_extension_and_fixes,
            use_levenshtein_distance=True,
            goty_field=goty_field,
            year_constraint=year_constraint,
            print_matches=print_matches,
            must_be_available_on_pc=must_be_available_on_pc,
            must_be_a_game=must_be_a_game,
        )
        print()
