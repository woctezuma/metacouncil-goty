from anonymize_data import get_anonymized_file_prefix, load_input, remove_header
from parsing_params import (
    convert_params_to_indices,
    get_adjusted_parsing_params,
    get_categories,
    get_parsing_offset,
)


def extract_game_tokens(
    input_tokens: list[str],
    ind_list: list[int],
    num_choices: int,
    *,
    strip_game_name: bool = True,
) -> dict[int, str]:
    d = {}
    for i, ind in enumerate(ind_list):
        # Caveat: num_choices is not necessarily equal to len(ind_list)
        position = num_choices - i
        game_name = input_tokens[ind]
        if strip_game_name:
            game_name = game_name.strip()
        d[position] = game_name
    return d


def is_anonymized_file(fname: str) -> bool:
    return bool(get_anonymized_file_prefix() in fname)


def parse_csv(fname: str, parsing_params):
    text_data = load_input(fname)

    is_anonymized = is_anonymized_file(fname)

    if not is_anonymized:
        text_data = remove_header(text_data)

    return parse_text_data(text_data, parsing_params, is_anonymized=is_anonymized)


def parse_text_data(
    text_data: list[str],
    parsing_params,
    *,
    is_anonymized: bool,
) -> dict[str, dict]:
    offset = get_parsing_offset(is_anonymized=is_anonymized)
    indices: dict[str, dict[str, list[int | None]]] = convert_params_to_indices(
        parsing_params,
        offset=offset,
    )

    quote = '"'

    ballots = {}

    for line in text_data:
        tokens = [token.strip(quote) for token in line.split(';"')]

        voter_name = read_voter_name(tokens, indices)

        single_ballot: dict = {}
        single_ballot = fill_in_review(tokens, indices, single_ballot=single_ballot)
        single_ballot = fill_in_game_list(
            tokens,
            indices,
            parsing_params=parsing_params,
            single_ballot=single_ballot,
        )
        single_ballot = fill_in_best_optional(single_ballot=single_ballot)

        ballots[voter_name] = single_ballot

    return ballots


def read_voter_name(tokens, indices: dict[str, dict[str, list[int | None]]]):
    ind = indices["voter_name"]["index"][0]
    return tokens[ind]


def fill_in_review(
    tokens,
    indices: dict[str, dict[str, list[int | None]]],
    single_ballot,
):
    for categorie in get_categories("main"):
        ind = indices["review"][categorie][0]
        review = None if ind is None else tokens[ind]

        goty_review_field = f"{categorie}_description"
        single_ballot[goty_review_field] = review

    return single_ballot


def fill_in_game_list(
    tokens,
    indices: dict[str, dict[str, list[int | None]]],
    parsing_params,
    single_ballot,
) -> dict:
    for categorie_type in ("main", "optional"):
        for categorie in get_categories(categorie_type=categorie_type):
            ind_list = indices[categorie_type][categorie]
            d = extract_game_tokens(
                tokens,
                ind_list,
                parsing_params[categorie]["num_choices"],
            )

            goty_field = f"{categorie}_preferences"
            single_ballot[goty_field] = d

    return single_ballot


def fill_in_best_optional(single_ballot):
    for categorie in get_categories("optional"):
        goty_field = f"{categorie}_preferences"
        best_position = 1
        try:
            best_game = single_ballot[goty_field][best_position]
        except KeyError:
            best_game = None

        best_field = f"best_{categorie}"
        single_ballot[best_field] = best_game

    return single_ballot


if __name__ == "__main__":
    from load_ballots import get_ballot_file_name

    ballot_year = 2018
    input_filename = get_ballot_file_name(ballot_year, is_anonymized=True)

    params = get_adjusted_parsing_params(year=ballot_year)
    ballots = parse_csv(fname=input_filename, parsing_params=params)
    print(ballots)
