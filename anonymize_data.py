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


def get_review_token_indices(ballot_year='2018'):
    # Valid for 2018 and 2019 data
    goty_description_token_index = 30
    # Only valid for 2019 data
    gotd_description_token_index = 52

    if int(ballot_year) % 10 == 9:
        review_token_indices = [goty_description_token_index,
                                gotd_description_token_index]
    else:
        review_token_indices = [goty_description_token_index]

    return review_token_indices


def anonymize(data,
              author_name_token_index=18,
              fake_author_name=True,
              review_token_indices=None,
              redact_reviews=False,
              verbose=True):
    if review_token_indices is None:
        default_ballot_year = '2018'
        review_token_indices = get_review_token_indices(ballot_year=default_ballot_year)

    import re

    from faker import Faker

    fake = Faker('fr_FR')

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
                       file_encoding='utf-8',
                       fake_author_name=True,
                       review_token_indices=None,
                       redact_reviews=False,
                       data_folder=None,
                       verbose=True):
    output_filename = get_anonymized_file_prefix() + input_filename

    data = load_input(input_filename, file_encoding, data_folder=data_folder)

    data_content = remove_header(data, content_start_criterion='"1"')

    # Assumption: the name of the author appears as the 18th token on each line of the original data
    anonymized_data = anonymize(data_content,
                                author_name_token_index=18,
                                fake_author_name=fake_author_name,
                                review_token_indices=review_token_indices,
                                redact_reviews=redact_reviews,
                                verbose=verbose)

    write_output(anonymized_data, output_filename, file_encoding)

    return anonymized_data


if __name__ == '__main__':
    ballot_year = '2020'
    input_filename = 'pc_gaming_metacouncil_goty_awards_' + ballot_year + '.csv'

    review_token_indices = get_review_token_indices(ballot_year)

    fake_author_name = True
    redact_reviews = False
    verbose = True

    anonymized_data = load_and_anonymize(input_filename,
                                         fake_author_name=fake_author_name,
                                         review_token_indices=review_token_indices,
                                         redact_reviews=redact_reviews,
                                         verbose=verbose)
