from anonymize_data import load_input, remove_header


def get_main_categories():
    return ["goty", "gotd"]


def get_optional_categories():
    # Caveat: the order matters!
    return ["dlc", "early_access", "vr", "turd"]


def get_default_parsing_params():
    params = dict()

    for categorie in get_main_categories():
        params[categorie] = {"num_choices": 5}

    for categorie in get_optional_categories():
        params[categorie] = {"num_choices": 1}

    return params


def adjust_params_to_year(params, year):
    if int(year) == 2018:
        params["vr"]["num_choices"] = 0

    if int(year) % 10 == 9:
        params["gotd"]["num_choices"] = 10
    else:
        params["gotd"]["num_choices"] = 0

    return params


def get_parsing_params(year):
    return adjust_params_to_year(get_default_parsing_params(), year)


def get_next_indices(last_index=0, num_indices=0):
    # The first index to include
    start = 1 + last_index

    # The first index NOT to include
    end = num_indices + start

    if num_indices > 0:
        description_index = end
    else:
        description_index = None

    return start, end, description_index


def convert_params_to_indices(params, offset=9):
    voter_index = offset

    indices = {
        "voter_name": voter_index,
        "main": {},
        "review": {},
        "optional": {},
    }

    last_index = voter_index

    for categorie in get_main_categories():
        start, end, descr = get_next_indices(
            last_index=last_index, num_indices=params[categorie]["num_choices"]
        )
        indices["main"][categorie] = [i for i in range(start, end)]
        indices["review"][categorie] = descr

        if descr is not None:
            # range() will stop at end-1, and then the review is at index equal to end, so the last index is "end"
            last_index = end

    for categorie in get_optional_categories():
        start, end, descr = get_next_indices(
            last_index=last_index, num_indices=params[categorie]["num_choices"]
        )
        indices["optional"][categorie] = [i for i in range(start, end)]

        # range() will stop at end-1, and then there is NO review for optional categories, so the last index is "end-1"
        last_index = end - 1

    return indices


def extract_tokens(input_tokens, params, categorie, ind_list):
    d = dict()
    for i, ind in enumerate(ind_list):
        position = params[categorie]["num_choices"] - i
        game_name = input_tokens[ind]
        d[position] = game_name
    return d


def parse_csv(fname, params):
    text_data = load_input(fname)

    is_anonymized = 'anonymized' in fname

    if is_anonymized:
        offset = 0
    else:
        text_data = remove_header(text_data)
        offset = 9

    indices = convert_params_to_indices(params, offset=offset)

    quote = '"'

    ballots = dict()

    for line in text_data:
        tokens = [token.strip(quote) for token in line.split(";")]

        ind = indices["voter_name"]
        voter_name = tokens[ind]

        ballots[voter_name] = dict()

        for categorie in get_main_categories():
            ind = indices["review"][categorie]
            goty_review_field = f"{categorie}_description"
            if ind is None:
                review = ''
            else:
                review = tokens[ind]
            ballots[voter_name][goty_review_field] = review

        for categorie in get_main_categories():
            ind_list = indices["main"][categorie]
            d = extract_tokens(tokens, params, categorie, ind_list)

            goty_field = f"{categorie}_preferences"
            ballots[voter_name][goty_field] = d

        for categorie in get_optional_categories():
            ind_list = indices["optional"][categorie]
            d = extract_tokens(tokens, params, categorie, ind_list)

            goty_field = f"{categorie}_preferences"
            ballots[voter_name][goty_field] = d

            best_position = 1
            best_field = f"best_{categorie}"
            try:
                best_game = d[best_position]
            except KeyError:
                best_game = None
            ballots[voter_name][best_field] = best_game

    return ballots


if __name__ == "__main__":
    ballot_year = 2018
    input_filename = f"anonymized_pc_gaming_metacouncil_goty_awards_{ballot_year}.csv"

    params = get_parsing_params(year=ballot_year)
    ballots = parse_csv(fname=input_filename, params=params)
    print(ballots)
