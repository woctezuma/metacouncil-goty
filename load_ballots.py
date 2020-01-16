def parse_votes(data,
                num_goty_games_per_voter=5,
                num_gotd_games_per_voter=10):
    # Games of the Year (GotY)
    goty_field = 'goty_preferences'
    goty_review_field = 'goty_description'

    # Games of the Decade (GotD)
    gotd_field = 'gotd_preferences'
    gotd_review_field = 'gotd_description'

    ballots = dict()

    for element in data:
        # Tokenize
        raw_tokens = element.split('";"')
        # Adjust the first two tokens and the last token due to formatting
        tokens = [t for t in raw_tokens[0].split(';"')] + raw_tokens[1:-1] + [raw_tokens[-1].strip('"')]

        # Parse
        voter_name = tokens[0]
        voted_games = [tokens[i] for i in range(1, num_goty_games_per_voter + 1)]
        goty_description = tokens[num_goty_games_per_voter + 1]
        best_dlc = tokens[-3]
        best_early_access = tokens[-2]
        best_turd = tokens[-1]

        # Store the parsed data in a dictionary
        ballots[voter_name] = dict()

        ballots[voter_name][goty_field] = dict()
        for (i, game_name) in enumerate(voted_games):
            position = num_goty_games_per_voter - i
            ballots[voter_name][goty_field][position] = game_name

        ballots[voter_name][goty_review_field] = goty_description
        ballots[voter_name]['best_dlc'] = best_dlc
        ballots[voter_name]['best_early_access'] = best_early_access
        ballots[voter_name]['best_turd'] = best_turd

    return ballots


def load_ballots(input_filename, file_encoding='utf8', fake_author_name=True):
    from anonymize_data import get_anonymized_file_prefix, load_input, load_and_anonymize

    if input_filename.startswith(get_anonymized_file_prefix()):
        anonymized_data = load_input(input_filename, file_encoding)
    else:
        anonymized_data = load_and_anonymize(input_filename, file_encoding, fake_author_name=fake_author_name)

    ballots = parse_votes(anonymized_data)

    return ballots


def print_reviews(ballots,
                  matches,
                  app_id,
                  goty_field='goty_preferences',
                  goty_review_field='goty_description'):
    # Constant parameters
    goty_position = 1
    neighbor_reference_index = 0

    seen_game_names = set()

    for voter_name in ballots:
        goty_raw_name = ballots[voter_name][goty_field][goty_position]
        goty_app_id = matches[goty_raw_name]['matched_appID'][neighbor_reference_index]
        goty_standardized_name = matches[goty_raw_name]['matched_name'][neighbor_reference_index]

        if goty_app_id == app_id:
            goty_review = ballots[voter_name][goty_review_field]

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
