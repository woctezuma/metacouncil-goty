from parsing_params import get_parsing_indices


def get_data_folder():
    data_folder = 'data/'
    return data_folder


def get_anonymized_file_prefix():
    anonymized_file_prefix = 'anonymized_'
    return anonymized_file_prefix


def load_input(filename, file_encoding='utf8', data_folder=None):
    if data_folder is None:
        data_folder = get_data_folder()

    data = []

    full_path_to_file = data_folder + filename

    with open(full_path_to_file, 'r', encoding=file_encoding) as f:
        for line in f.readlines():
            line = line.strip()
            # Remove empty lines and comments
            if len(line) > 0 and line[0:2] != '# ':
                data.append(line)

    return data


def remove_header(data, content_start_criterion='"1"'):
    # Skip (header) lines until the first block of data content is encountered.
    num_rows_header = 0
    for row in data:
        if row[0:len(content_start_criterion)] == content_start_criterion:
            break
        num_rows_header += 1

    data_content = data[num_rows_header:]

    if len(data_content) == 0:
        # This situation occurs if the header has not been found, because the file was likely previously anonymized.
        # Ensure that we do not skip all of the (already anonymized) data by trying to remove a non-existent header!
        data_content = data

    return data_content


def get_review_token_indices(ballot_year='2018', is_anonymized=False):
    indices = get_parsing_indices(year=ballot_year, is_anonymized=is_anonymized)
    review_token_indices = [2 * v for v in indices['review'].values() if v is not None]
    # NB: we multiply the index by 2, because count starts at 0 and there are ";" separators in the original data.
    # Expected results for a file which was not anonymized:
    # - [30] for GOTY in 2018 and 2020
    # - [30, 52] for GOTY and GOTD in 2019

    return review_token_indices


def get_author_name_token_index(ballot_year='2018', is_anonymized=False):
    indices = get_parsing_indices(year=ballot_year, is_anonymized=is_anonymized)
    author_token_index = 2 * indices['voter_name']
    # NB: we multiply the index by 2, because count starts at 0 and there are ";" separators in the original data.
    # Expected result for a file which was not anonymized: 18.

    return author_token_index


def anonymize(data,
              ballot_year,
              fake_author_name=True,
              redact_reviews=False,
              faker_seed=0,
              verbose=True):
    is_anonymized = False
    author_name_token_index = get_author_name_token_index(ballot_year=ballot_year, is_anonymized=is_anonymized)
    review_token_indices = get_review_token_indices(ballot_year=ballot_year, is_anonymized=is_anonymized)

    import re

    from faker import Faker

    fake = Faker('fr_FR')
    fake.seed_instance(faker_seed)

    anonymized_data = []

    for element in data:
        tokens = re.split('(;)', element)
        if fake_author_name:
            tokens[author_name_token_index] = fake.name()

        if redact_reviews:
            # Delete 'goty_description' and 'gotd_description'
            for review_token_index in review_token_indices:
                if verbose:
                    review_content = tokens[review_token_index]
                    print('Redacting review content: {}'.format(review_content))
                tokens[review_token_index] = '""'

        # Remove leading metadata
        # Consequence: the fake author name should now appear as the first token on each line of the anonymized data.
        tokens = tokens[author_name_token_index:]

        line = ''.join(tokens)

        anonymized_data.append(line)

    return anonymized_data


def write_output(anonymized_data, output_filename, file_encoding='utf8'):
    import pathlib

    full_path_to_file = get_data_folder() + output_filename

    data_path = pathlib.Path(full_path_to_file).parent

    pathlib.Path(data_path).mkdir(parents=True, exist_ok=True)

    with open(full_path_to_file, 'w', encoding=file_encoding) as outfile:
        for element in anonymized_data:
            print(element, file=outfile)

    return


def load_and_anonymize(input_filename,
                       ballot_year,
                       file_encoding='utf-8',
                       fake_author_name=True,
                       redact_reviews=False,
                       data_folder=None,
                       verbose=True):
    output_filename = get_anonymized_file_prefix() + input_filename

    data = load_input(input_filename, file_encoding, data_folder=data_folder)

    data_content = remove_header(data, content_start_criterion='"1"')

    anonymized_data = anonymize(data_content,
                                ballot_year=ballot_year,
                                fake_author_name=fake_author_name,
                                redact_reviews=redact_reviews,
                                verbose=verbose)

    write_output(anonymized_data, output_filename, file_encoding)

    return anonymized_data


if __name__ == '__main__':
    from load_ballots import get_ballot_file_name

    ballot_year = '2020'
    input_filename = get_ballot_file_name(ballot_year)

    fake_author_name = True
    redact_reviews = False
    verbose = True

    anonymized_data = load_and_anonymize(input_filename,
                                         ballot_year=ballot_year,
                                         fake_author_name=fake_author_name,
                                         redact_reviews=redact_reviews,
                                         verbose=verbose)
