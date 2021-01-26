from anonymize_data import load_input, remove_header
from parsing_params import (
    get_categories,
    get_parsing_params,
    convert_params_to_indices,
    get_parsing_offset,
)


def extract_tokens(input_tokens, ind_list, num_choices):
    d = dict()
    for i, ind in enumerate(ind_list):
        # Caveat: num_choices is not necessarily equal to len(ind_list)
        position = num_choices - i
        game_name = input_tokens[ind]
        d[position] = game_name
    return d


def is_anonymized_file(fname):
    return bool("anonymized" in fname)


def parse_csv(fname, params):
    text_data = load_input(fname)

    is_anonymized = is_anonymized_file(fname)

    offset = get_parsing_offset(is_anonymized=is_anonymized)

    if not is_anonymized:
        text_data = remove_header(text_data)

    indices = convert_params_to_indices(params, offset=offset)

    quote = '"'

    ballots = dict()

    for line in text_data:
        tokens = [token.strip(quote) for token in line.split(";")]

        voter_name = read_voter_name(tokens, indices)

        single_ballot = dict()
        single_ballot = fill_in_review(tokens, indices, single_ballot=single_ballot)
        single_ballot = fill_in_game_list(tokens, indices, params, single_ballot=single_ballot)
        single_ballot = fill_in_best_optional(single_ballot=single_ballot)

        ballots[voter_name] = single_ballot

    return ballots


def read_voter_name(tokens, indices):
    ind = indices["voter_name"]
    voter_name = tokens[ind]

    return voter_name


def fill_in_review(tokens, indices, single_ballot):
    for categorie in get_categories("main"):
        ind = indices["review"][categorie]
        if ind is None:
            review = ""
        else:
            review = tokens[ind]

        goty_review_field = f"{categorie}_description"
        single_ballot[goty_review_field] = review

    return single_ballot


def fill_in_game_list(tokens, indices, params, single_ballot):
    for categorie_type in ["main", "optional"]:
        for categorie in get_categories(categorie_type=categorie_type):
            ind_list = indices[categorie_type][categorie]
            d = extract_tokens(tokens, ind_list, params[categorie]["num_choices"])

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
    ballot_year = 2018
    input_filename = f"anonymized_pc_gaming_metacouncil_goty_awards_{ballot_year}.csv"

    params = get_parsing_params(year=ballot_year)
    ballots = parse_csv(fname=input_filename, params=params)
    print(ballots)
