def get_main_categories() -> list[str]:
    # Caveat: the order matters!
    return ["goty", "gotd"]


def get_optional_categories() -> list[str]:
    # Caveat: the order matters!
    return ["dlc", "early_access", "vr", "turd"]


def get_categories(categorie_type: str = "main") -> list[str]:
    if categorie_type == "main":
        categories = get_main_categories()
    else:
        categories = get_optional_categories()

    return categories


def get_default_parsing_params() -> dict[str, dict]:
    params = {}

    for categorie in get_main_categories():
        params[categorie] = {"num_choices": 5}

    for categorie in get_optional_categories():
        params[categorie] = {"num_choices": 1}

    return params


def adjust_params_to_year(params: dict[str, dict], year: str | int) -> dict[str, dict]:
    # NB: in 2018, there was no vote for the best VR game. In 2019 and subsequent years, there was one.
    if int(year) == 2018:
        params["vr"]["num_choices"] = 0

    # NB: if the ballot year ends with a "9", e.g. "2019", then it is the last year of its decade, and there is a GotD.
    if int(year) % 10 == 9:
        params["gotd"]["num_choices"] = 10
    else:
        params["gotd"]["num_choices"] = 0

    return params


def get_adjusted_parsing_params(year):
    return adjust_params_to_year(get_default_parsing_params(), year)


def get_next_indices(last_index: int = 0, num_indices: int = 0) -> tuple[int, int, int]:
    # The first index to include
    start = 1 + last_index

    # The first index NOT to include
    end = num_indices + start

    description_index = end if num_indices > 0 else None

    return start, end, description_index


def convert_params_to_indices(
    params: dict[str, dict],
    offset: int = 9,
) -> dict[str, dict]:
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
            last_index=last_index,
            num_indices=params[categorie]["num_choices"],
        )
        indices["main"][categorie] = list(range(start, end))
        indices["review"][categorie] = descr

        if descr is not None:
            # range() will stop at end-1, and then the review is at index equal to end, so the last index is "end"
            last_index = end

    for categorie in get_categories("optional"):
        start, end, descr = get_next_indices(
            last_index=last_index,
            num_indices=params[categorie]["num_choices"],
        )
        indices["optional"][categorie] = list(range(start, end))

        # range() will stop at end-1, and then there is NO review for optional categories, so the last index is "end-1"
        last_index = end - 1

    return indices


def get_parsing_offset(is_anonymized: bool) -> int:
    return 0 if is_anonymized else 9


def get_parsing_indices(year, is_anonymized):
    params = get_adjusted_parsing_params(year=year)
    offset = get_parsing_offset(is_anonymized)
    return convert_params_to_indices(params, offset)


if __name__ == "__main__":
    ballot_year = 2018

    params = get_adjusted_parsing_params(year=ballot_year)
    print(params)

    indices = get_parsing_indices(year=ballot_year, is_anonymized=False)
    print(indices)

    indices = get_parsing_indices(year=ballot_year, is_anonymized=True)
    print(indices)
