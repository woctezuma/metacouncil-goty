from parsing_params import get_adjusted_parsing_params
from parsing_utils import parse_csv


def get_ballot_file_name(ballot_year, is_anonymized=False):
    from anonymize_data import get_anonymized_file_prefix

    fname = f'pc_gaming_metacouncil_goty_awards_{ballot_year}.csv'
    if is_anonymized:
        fname = get_anonymized_file_prefix() + fname

    return fname


def convert_fname_to_year(fname, year_prefixe='20', num_digits=4):
    year_index = fname.find(year_prefixe)
    year_str = fname[year_index:(year_index + num_digits)]
    ballot_year = int(year_str)

    return ballot_year


def get_parsing_params(ballot_year):
    return get_adjusted_parsing_params(year=ballot_year)


def load_ballots(input_filename):
    ballot_year = convert_fname_to_year(fname=input_filename)
    parsing_params = get_parsing_params(ballot_year=ballot_year)
    ballots = parse_csv(input_filename, parsing_params)

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
