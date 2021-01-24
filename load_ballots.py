def get_parsing_params(ballot_year='2018',
                       num_goty_games_per_voter=5,
                       num_gotd_games_per_voter=10):
    parsing_params = dict()

    parsing_params['num_goty_games_per_voter'] = num_goty_games_per_voter
    parsing_params['num_gotd_games_per_voter'] = num_gotd_games_per_voter

    goty_description_index = num_goty_games_per_voter + 1
    gotd_description_index = goty_description_index + num_gotd_games_per_voter + 1

    parsing_params['voter_name'] = 0
    parsing_params['voted_games'] = [
        i
        for i in range(1, num_goty_games_per_voter + 1)
    ]
    parsing_params['goty_description'] = goty_description_index

    # NB: if the ballot year ends with a "9", e.g. "2019", then it is the last year of its decade, and there is a GotD.
    if int(ballot_year) % 10 == 9:
        parsing_params['gotd_voted_games'] = [
            goty_description_index + i
            for i in range(1, num_gotd_games_per_voter + 1)
        ]
        parsing_params['gotd_description'] = gotd_description_index
    else:
        parsing_params['gotd_voted_games'] = []
        parsing_params['gotd_description'] = None

    # NB: in 2018, there was no vote for the best VR game. In 2019 and subsequent years, there was one.
    if int(ballot_year) == 2018:
        parsing_params['best_dlc'] = -3
        parsing_params['best_early_access'] = -2
        parsing_params['best_vr'] = None
        parsing_params['best_turd'] = -1
    else:
        parsing_params['best_dlc'] = -4
        parsing_params['best_early_access'] = -3
        parsing_params['best_vr'] = -2
        parsing_params['best_turd'] = -1

    return parsing_params


def parse_votes(data,
                parsing_params=None,
                ballot_year=None):
    if ballot_year is None:
        ballot_year = '2018'

    if parsing_params is None:
        parsing_params = get_parsing_params(ballot_year=ballot_year)

    num_goty_games_per_voter = parsing_params['num_goty_games_per_voter']
    num_gotd_games_per_voter = parsing_params['num_gotd_games_per_voter']

    # Games of the Year (GotY)
    goty_field = 'goty_preferences'
    goty_review_field = 'goty_description'

    # Games of the Decade (GotD)
    gotd_field = 'gotd_preferences'
    gotd_review_field = 'gotd_description'

    quote = '"'

    ballots = dict()

    for element in data:
        # Tokenize
        raw_tokens = element.split('";"')
        # Adjust the first two tokens and the last token due to formatting
        tokens = [t for t in raw_tokens[0].strip(quote).split(';"')] + raw_tokens[1:-1] + [raw_tokens[-1].strip(quote)]

        # Parse
        voter_name = tokens[parsing_params['voter_name']]

        voted_games = [
            tokens[i]
            for i in parsing_params['voted_games']
        ]

        goty_description = tokens[parsing_params['goty_description']]

        best_dlc = tokens[parsing_params['best_dlc']]
        best_early_access = tokens[parsing_params['best_early_access']]
        best_turd = tokens[parsing_params['best_turd']]

        gotd_voted_games = [
            tokens[i]
            for i in parsing_params['gotd_voted_games']
        ]

        gotd_description_index = parsing_params['gotd_description']
        try:
            gotd_description = tokens[gotd_description_index]
        except TypeError as e:
            gotd_description = None

        best_vr_index = parsing_params['best_vr']
        try:
            best_vr = tokens[best_vr_index]
        except TypeError as e:
            best_vr = None

        # Store the parsed data in a dictionary
        ballots[voter_name] = dict()

        if len(voted_games) > 0:
            ballots[voter_name][goty_field] = dict()
            for (i, game_name) in enumerate(voted_games):
                position = num_goty_games_per_voter - i
                ballots[voter_name][goty_field][position] = game_name

        ballots[voter_name][goty_review_field] = goty_description
        ballots[voter_name]['best_dlc'] = best_dlc
        ballots[voter_name]['best_early_access'] = best_early_access
        ballots[voter_name]['best_turd'] = best_turd

        if len(gotd_voted_games) > 0:
            ballots[voter_name][gotd_field] = dict()
            for (i, game_name) in enumerate(gotd_voted_games):
                position = num_gotd_games_per_voter - i
                ballots[voter_name][gotd_field][position] = game_name

        if gotd_description is not None:
            ballots[voter_name][gotd_review_field] = gotd_description

        if best_vr is not None:
            ballots[voter_name]['best_vr'] = best_vr

    return ballots


def load_ballots(input_filename,
                 file_encoding='utf8',
                 fake_author_name=True,
                 data_folder=None,
                 parsing_params=None):
    from anonymize_data import get_anonymized_file_prefix, load_input, load_and_anonymize

    if input_filename.startswith(get_anonymized_file_prefix()):
        anonymized_data = load_input(
            input_filename,
            file_encoding,
            data_folder=data_folder
        )
    else:
        anonymized_data = load_and_anonymize(
            input_filename,
            file_encoding,
            fake_author_name=fake_author_name,
            data_folder=data_folder,
        )

    ballots = parse_votes(anonymized_data,
                          parsing_params)

    return ballots


def print_reviews(ballots,
                  matches,
                  app_id,
                  goty_field='goty_preferences',
                  goty_review_field=None,
                  export_for_forum=True):
    if goty_review_field is None:
        goty_review_field = goty_field.replace('_preferences', '_description')

    # Constant parameters
    goty_position = 1
    neighbor_reference_index = 0

    seen_game_names = set()

    for voter_name in ballots:
        goty_raw_name = ballots[voter_name][goty_field][goty_position]
        try:
            goty_app_id = matches[goty_raw_name]['matched_appID'][neighbor_reference_index]
        except KeyError:
            # This happens if the voter did not submit any actual game at all, e.g.
            # - 'n/a' as the first game for GotY, so that the mandatory field in the form can be bypassed,
            # - no submitted game for the following games for GotY, because the fields were optional anyway.
            continue
        goty_standardized_name = matches[goty_raw_name]['matched_name'][neighbor_reference_index]

        if goty_app_id == app_id:
            goty_review = ballots[voter_name][goty_review_field]

            if goty_standardized_name not in seen_game_names:
                seen_game_names.add(goty_standardized_name)
                print('\n[game] ' + goty_standardized_name)

            if export_for_forum:
                print(f'\n[quote="{voter_name}"]')
            else:
                print('\nReviewer: ' + voter_name)
            print(goty_review)
            if export_for_forum:
                print('[/quote]')

    return


if __name__ == '__main__':
    ballot_year = '2019'
    input_filename = 'pc_gaming_metacouncil_goty_awards_' + ballot_year + '.csv'
    parsing_params = get_parsing_params(ballot_year=ballot_year)
    fake_author_name = False
    ballots = load_ballots(input_filename,
                           fake_author_name=fake_author_name,
                           parsing_params=parsing_params)
