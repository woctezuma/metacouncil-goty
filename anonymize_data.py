def get_data_folder():
    data_folder = 'data/'
    return data_folder


def get_anonymized_file_prefix():
    anonymized_file_prefix = 'anonymized_'
    return anonymized_file_prefix


def load_input(filename, file_encoding='utf8'):
    data = []

    full_path_to_file = get_data_folder() + filename

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

    return data_content


def anonymize(data, author_name_token_index=18):
    import re

    from faker import Faker

    fake = Faker('fr_FR')

    anonymized_data = []

    for element in data:
        tokens = re.split('(;)', element)
        tokens[author_name_token_index] = fake.name()

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


def load_and_anonymize(input_filename):
    output_filename = get_anonymized_file_prefix() + input_filename
    file_encoding = 'utf-8'

    data = load_input(input_filename, file_encoding)

    data_content = remove_header(data, content_start_criterion='"1"')

    # Assumption: the name of the author appears as the 18th token on each line of the original data
    anonymized_data = anonymize(data_content, author_name_token_index=18)

    write_output(anonymized_data, output_filename, file_encoding)

    return anonymized_data


if __name__ == '__main__':
    input_filename = 'pc_gaming_metacouncil_goty_awards_2018.csv'
    anonymized_data = load_and_anonymize(input_filename)
