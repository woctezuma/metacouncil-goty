def parse_votes(data, num_games_per_voter=5):
    ballots = dict()

    for element in data:
        # Tokenize
        raw_tokens = element.split('";"')
        # Adjust the first two tokens and the last token due to formatting
        tokens = [t for t in raw_tokens[0].split(';"')] + raw_tokens[1:-1] + [raw_tokens[-1].strip('"')]

        # Parse
        voter_name = tokens[0]
        voted_games = [tokens[i] for i in range(1, num_games_per_voter + 1)]
        goty_description = tokens[num_games_per_voter + 1]
        best_dlc = tokens[-3]
        best_early_access = tokens[-2]
        best_turd = tokens[-1]

        # Store the parsed data in a dictionary
        ballots[voter_name] = dict()

        ballots[voter_name]['goty_preferences'] = dict()
        for i in range(len(voted_games)):
            position = num_games_per_voter - i

            game_name = voted_games[i]

            ballots[voter_name]['goty_preferences'][position] = game_name

        ballots[voter_name]['goty_description'] = goty_description
        ballots[voter_name]['best_dlc'] = best_dlc
        ballots[voter_name]['best_early_access'] = best_early_access
        ballots[voter_name]['best_turd'] = best_turd

    return ballots


def load_ballots(input_filename, file_encoding='utf8'):
    from anonymize_data import get_anonymized_file_prefix, load_input, load_and_anonymize

    if input_filename.startswith(get_anonymized_file_prefix()):
        anonymized_data = load_input(input_filename, file_encoding)
    else:
        anonymized_data = load_and_anonymize(input_filename, file_encoding)

    ballots = parse_votes(anonymized_data)

    return ballots


def print_reviews(ballots, matches, app_id):
    # Constant parameters
    goty_position = 1
    neighbor_reference_index = 0

    seen_game_names = set()

    for voter_name in ballots:
        goty_raw_name = ballots[voter_name]['goty_preferences'][goty_position]
        goty_app_id = matches[goty_raw_name]['matched_appID'][neighbor_reference_index]
        goty_standardized_name = matches[goty_raw_name]['matched_name'][neighbor_reference_index]

        if goty_app_id == app_id:
            goty_review = ballots[voter_name]['goty_description']

            if goty_standardized_name not in seen_game_names:
                seen_game_names.add(goty_standardized_name)
                print('\n[game] ' + goty_standardized_name)

            print('\nReviewer: ' + voter_name)
            print(goty_review)

    return


if __name__ == '__main__':
    ballot_year = '2018'
    input_filename = 'pc_gaming_metacouncil_goty_awards_' + ballot_year + '.csv'
    ballots = load_ballots(input_filename)
