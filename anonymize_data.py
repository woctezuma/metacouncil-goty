from pathlib import Path

from parsing_params import get_parsing_indices


def get_data_folder() -> str:
    return "data/"


def get_anonymized_file_prefix() -> str:
    return "anonymized_"


def load_input(
    filename: str,
    file_encoding: str = "utf8",
    data_folder: str | None = None,
) -> list[str]:
    if data_folder is None:
        data_folder = get_data_folder()

    data = []

    full_path_to_file = data_folder + filename

    with Path(full_path_to_file).open(encoding=file_encoding) as f:
        for raw_line in f:
            line = raw_line.strip()
            # Remove empty lines and comments
            if line and line[0:2] != "# ":
                data.append(line)

    return data


def remove_header(data: list[str], content_start_criterion: str = '"1"') -> list[str]:
    # Skip (header) lines until the first block of data content is encountered.
    num_rows_header = 0
    for row in data:
        if row[0 : len(content_start_criterion)] == content_start_criterion:
            break
        num_rows_header += 1

    data_content = data[num_rows_header:]

    if not data_content:
        # This situation occurs if the header has not been found, because the file was likely previously anonymized.
        # Ensure that we do not skip all of the (already anonymized) data by trying to remove a non-existent header!
        data_content = data

    return data_content


def get_review_token_indices(
    ballot_year: str = "2018",
    *,
    is_anonymized: bool = False,
) -> list[int]:
    indices = get_parsing_indices(year=ballot_year, is_anonymized=is_anonymized)
    return [2 * v[0] for v in indices["review"].values() if v[0] is not None]
    # NB: we multiply the index by 2, because count starts at 0 and there are ";" separators in the original data.
    # Expected results for a file which was not anonymized:
    # - [30] for GOTY in 2018 and 2020
    # - [30, 52] for GOTY and GOTD in 2019


def get_author_name_token_index(
    ballot_year: str = "2018",
    *,
    is_anonymized: bool = False,
) -> int:
    indices = get_parsing_indices(year=ballot_year, is_anonymized=is_anonymized)
    ind = indices["voter_name"]["index"][0]
    return 2 * ind if ind is not None else -1
    # NB: we multiply the index by 2, because count starts at 0 and there are ";" separators in the original data.
    # Expected result for a file which was not anonymized: 18.


def anonymize(
    data: list[str],
    ballot_year: str,
    *,
    fake_author_name: bool = True,
    redact_reviews: bool = False,
    faker_seed: int = 0,
    input_is_anonymized: bool = False,
    verbose: bool = True,
) -> list[str]:
    author_name_token_index = get_author_name_token_index(
        ballot_year=ballot_year,
        is_anonymized=input_is_anonymized,
    )
    review_token_indices = get_review_token_indices(
        ballot_year=ballot_year,
        is_anonymized=input_is_anonymized,
    )

    import re

    from faker import Faker

    fake = Faker("fr_FR")
    fake.seed_instance(faker_seed)

    anonymized_data = []

    for element in data:
        tokens = re.split("(;)", element)
        if fake_author_name:
            tokens[author_name_token_index] = fake.name()

        if redact_reviews:
            # Delete 'goty_description' and 'gotd_description'
            for review_token_index in review_token_indices:
                if verbose:
                    review_content = tokens[review_token_index]
                    print(f"Redacting review content: {review_content}")
                tokens[review_token_index] = '""'

        # Remove leading metadata
        # Consequence: the fake author name should now appear as the first token on each line of the anonymized data.
        tokens = tokens[author_name_token_index:]

        line = "".join(tokens)

        anonymized_data.append(line)

    return anonymized_data


def write_output(
    anonymized_data: list[str],
    output_filename: str,
    file_encoding: str = "utf8",
) -> None:
    full_path_to_file = get_data_folder() + output_filename

    data_path = Path(full_path_to_file).parent

    Path(data_path).mkdir(parents=True, exist_ok=True)

    with Path(full_path_to_file).open("w", encoding=file_encoding) as outfile:
        for element in anonymized_data:
            print(element, file=outfile)


def load_and_anonymize(
    input_filename: str,
    ballot_year: str,
    file_encoding: str = "utf-8",
    *,
    fake_author_name: bool = True,
    redact_reviews: bool = False,
    data_folder: str | None = None,
    verbose: bool = True,
) -> list[str]:
    output_filename = get_anonymized_file_prefix() + input_filename

    data = load_input(input_filename, file_encoding, data_folder=data_folder)

    data_content = remove_header(data, content_start_criterion='"1"')

    anonymized_data = anonymize(
        data_content,
        ballot_year=ballot_year,
        fake_author_name=fake_author_name,
        redact_reviews=redact_reviews,
        verbose=verbose,
    )

    write_output(anonymized_data, output_filename, file_encoding)

    return anonymized_data


if __name__ == "__main__":
    from load_ballots import get_ballot_file_name

    ballot_year = "2024"
    input_filename = get_ballot_file_name(ballot_year)

    fake_author_name = True
    redact_reviews = True
    verbose = True

    anonymized_data = load_and_anonymize(
        input_filename,
        ballot_year=ballot_year,
        fake_author_name=fake_author_name,
        redact_reviews=redact_reviews,
        verbose=verbose,
    )
