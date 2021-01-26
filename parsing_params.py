def get_main_categories():
    # Caveat: the order matters!
    return ["goty", "gotd"]


def get_optional_categories():
    # Caveat: the order matters!
    return ["dlc", "early_access", "vr", "turd"]


def get_categories(categorie_type="main"):
    if categorie_type == "main":
        categories = get_main_categories()
    else:
        categories = get_optional_categories()

    return categories


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

    for categorie in get_categories("main"):
        start, end, descr = get_next_indices(
            last_index=last_index, num_indices=params[categorie]["num_choices"]
        )
        indices["main"][categorie] = [i for i in range(start, end)]
        indices["review"][categorie] = descr

        if descr is not None:
            # range() will stop at end-1, and then the review is at index equal to end, so the last index is "end"
            last_index = end

    for categorie in get_categories("optional"):
        start, end, descr = get_next_indices(
            last_index=last_index, num_indices=params[categorie]["num_choices"]
        )
        indices["optional"][categorie] = [i for i in range(start, end)]

        # range() will stop at end-1, and then there is NO review for optional categories, so the last index is "end-1"
        last_index = end - 1

    return indices


def get_parsing_offset(is_anonymized):
    if is_anonymized:
        offset = 0
    else:
        offset = 9
    return offset


def get_parsing_indices(year, is_anonymized):
    params = get_parsing_params(year=year)
    offset = get_parsing_offset(is_anonymized)
    indices = convert_params_to_indices(params, offset)

    return indices


if __name__ == "__main__":
    ballot_year = 2018

    params = get_parsing_params(year=ballot_year)
    print(params)

    indices = get_parsing_indices(year=ballot_year, is_anonymized=False)
    print(indices)

    indices = get_parsing_indices(year=ballot_year, is_anonymized=True)
    print(indices)
