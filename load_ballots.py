from my_types import Ballots, Params
from parsing_params import get_adjusted_parsing_params
from parsing_utils import parse_csv


def get_ballot_file_name(ballot_year: str, *, is_anonymized: bool = False) -> str:
    from anonymize_data import get_anonymized_file_prefix

    fname = f"pc_gaming_metacouncil_goty_awards_{ballot_year}.csv"
    if is_anonymized:
        fname = get_anonymized_file_prefix() + fname

    return fname


def convert_fname_to_year(
    fname: str,
    year_prefixe: str = "20",
    num_digits: int = 4,
) -> str:
    year_index = fname.find(year_prefixe)
    return fname[year_index : (year_index + num_digits)]


def get_parsing_params(ballot_year: str) -> Params:
    return get_adjusted_parsing_params(year=ballot_year)


def load_ballots(input_filename: str) -> Ballots:
    ballot_year = convert_fname_to_year(fname=input_filename)
    parsing_params = get_parsing_params(ballot_year=ballot_year)
    return parse_csv(input_filename, parsing_params)


def print_reviews(
    ballots: Ballots,
    matches: dict,
    app_id: str,
    goty_field: str = "goty_preferences",
    goty_review_field: str | None = None,
    *,
    export_for_forum: bool = True,
) -> None:
    if goty_review_field is None:
        goty_review_field = goty_field.replace("_preferences", "_description")

    # Constant parameters
    goty_position = 1
    neighbor_reference_index = 0

    seen_game_names = set()

    for voter_name in ballots:
        goty_raw_name = ballots[voter_name][goty_field][goty_position]
        try:
            goty_app_id = matches[goty_raw_name]["matched_appID"][
                neighbor_reference_index
            ]
        except KeyError:
            # This happens if the voter did not submit any actual game at all, e.g.
            # - 'n/a' as the first game for GotY, so that the mandatory field in the form can be bypassed,
            # - no submitted game for the following games for GotY, because the fields were optional anyway.
            continue
        goty_standardized_name = matches[goty_raw_name]["matched_name"][
            neighbor_reference_index
        ]

        if goty_app_id == app_id:
            goty_review = ballots[voter_name][goty_review_field]

            if goty_standardized_name not in seen_game_names:
                seen_game_names.add(goty_standardized_name)
                print("\n[game] " + goty_standardized_name)

            if len(goty_review) > 0:
                if export_for_forum:
                    print(f'\n[quote="{voter_name}"]')
                else:
                    print("\nReviewer: " + voter_name)
                print(goty_review)
                if export_for_forum:
                    print("[/quote]")


if __name__ == "__main__":
    ballot_year = "2019"
    input_filename = get_ballot_file_name(ballot_year)
    ballots = load_ballots(input_filename)
