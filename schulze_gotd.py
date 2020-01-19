from load_ballots import get_parsing_params
from schulze_goty import apply_pipeline

if __name__ == '__main__':
    ballot_year = '2019'
    input_filename = 'pc_gaming_metacouncil_goty_awards_' + ballot_year + '.csv'
    use_igdb = True
    retrieve_igdb_data_from_scratch = False
    apply_hard_coded_extension_and_fixes = True
    use_levenshtein_distance = True

    parsing_params = get_parsing_params(ballot_year=ballot_year)

    # Game of the Decade
    # Caveat: pay attention to the d in 'gotd'.
    goty_field = 'gotd_preferences'
    # Either:
    duration_in_years = 10
    release_year = str(int(ballot_year) - duration_in_years + 1)
    year_constraint = 'minimum'
    # Or:
    # release_year = None
    # year_constraint = None

    apply_pipeline(input_filename,
                   release_year=release_year,
                   fake_author_name=False,
                   try_to_break_ties=False,
                   use_igdb=use_igdb,
                   retrieve_igdb_data_from_scratch=retrieve_igdb_data_from_scratch,
                   apply_hard_coded_extension_and_fixes=apply_hard_coded_extension_and_fixes,
                   use_levenshtein_distance=use_levenshtein_distance,
                   goty_field=goty_field,
                   year_constraint=year_constraint,
                   parsing_params=parsing_params,
                   num_app_id_groups_to_display=9)
