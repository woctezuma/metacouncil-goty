import unittest
from pathlib import Path

import anonymize_data
import disqualify_vote
import disqualify_vote_igdb
import extend_igdb
import extend_steamspy
import hard_coded_matches
import igdb_databases
import igdb_local_secrets
import igdb_look_up
import igdb_match_names
import igdb_utils
import load_ballots
import match_names
import optional_categories
import parsing_params
import parsing_utils
import schulze_goty
import steam_store_utils
import whitelist_vote
import whitelist_vote_igdb


class TestParsingUtilsMethods(unittest.TestCase):
    def test_parse_text_data(self):
        voter_name = '"MyTestUserName";'
        goty_votes = '"Half-Life: Alyx";"The Walking Dead: Saints & Sinners";"Fall Guys";"Sakuna";"Yakuza";'
        goty_descr = '''"I like the idea of a turn based Yakuza [..] game. Tl;DR, buy it, you won't regret it!";'''
        optional_votes = '"Deep Rock Galactic";"Phasmophobia";"The Walking Dead: Saints & Sinners";"Cyberpunk 2077"'

        line = voter_name + goty_votes + goty_descr + optional_votes

        ballots = parsing_utils.parse_text_data(
            text_data=[line],
            parsing_params=parsing_utils.get_adjusted_parsing_params(2020),
            is_anonymized=True,
        )

        self.assertTrue(
            ballots['MyTestUserName']['goty_description'].startswith("I like the idea"),
        )
        self.assertTrue(
            ballots['MyTestUserName']['goty_description'].endswith(
                "you won't regret it!",
            ),
        )
        self.assertEqual(ballots['MyTestUserName']['best_dlc'], 'Deep Rock Galactic')
        self.assertEqual(ballots['MyTestUserName']['best_early_access'], 'Phasmophobia')
        self.assertEqual(
            ballots['MyTestUserName']['best_vr'],
            'The Walking Dead: Saints & Sinners',
        )
        self.assertEqual(ballots['MyTestUserName']['best_turd'], 'Cyberpunk 2077')


class TestSteamStoreUtilsMethods(unittest.TestCase):
    def test_get_link_to_store_case_valid_app_id(self):
        app_id = '583950'
        link_to_store = steam_store_utils.get_link_to_store(app_id)
        expected_link = (
            '[URL=https://store.steampowered.com/app/'
            + app_id
            + '/]'
            + app_id
            + '[/URL]'
        )

        self.assertEqual(link_to_store, expected_link)

    def test_get_link_to_store_case_dummy_app_id_to_show(self):
        app_id = '-1'
        link_to_store = steam_store_utils.get_link_to_store(
            app_id,
            hide_dummy_app_id=False,
        )

        self.assertEqual(link_to_store, app_id)

    def test_get_link_to_store_case_dummy_app_id_to_hide(self):
        app_id = '-1'
        link_to_store = steam_store_utils.get_link_to_store(
            app_id,
            hide_dummy_app_id=True,
        )

        self.assertEqual(link_to_store, 'n/a')


class TestAnonymizeDataMethods(unittest.TestCase):
    def test_get_author_name_token_index(self):
        expected_author_token_index = 18
        is_anonymized = False

        for ballot_year in [2018, 2019, 2020]:
            author_token_index = anonymize_data.get_author_name_token_index(
                ballot_year=ballot_year,
                is_anonymized=is_anonymized,
            )
            self.assertTrue(expected_author_token_index == author_token_index)

    def test_get_review_token_indices(self):
        goty_description_token_index = 30
        gotd_description_token_index = 52
        is_anonymized = False

        ballot_year = '2018'
        review_token_indices = anonymize_data.get_review_token_indices(
            ballot_year=ballot_year,
            is_anonymized=is_anonymized,
        )
        self.assertTrue(len(review_token_indices) == 1)
        self.assertTrue(goty_description_token_index in review_token_indices)

        ballot_year = '2019'
        review_token_indices = anonymize_data.get_review_token_indices(
            ballot_year=ballot_year,
            is_anonymized=is_anonymized,
        )
        self.assertTrue(len(review_token_indices) == 2)
        self.assertTrue(goty_description_token_index in review_token_indices)
        self.assertTrue(gotd_description_token_index in review_token_indices)

        ballot_year = '2020'
        review_token_indices = anonymize_data.get_review_token_indices(
            ballot_year=ballot_year,
            is_anonymized=is_anonymized,
        )
        self.assertTrue(len(review_token_indices) == 1)
        self.assertTrue(goty_description_token_index in review_token_indices)

    def test_load_and_anonymize(self):
        ballot_year = '2018'
        input_filename = (
            'dummy_pc_gaming_metacouncil_goty_awards_' + ballot_year + '.csv'
        )
        anonymized_data = anonymize_data.load_and_anonymize(
            input_filename,
            ballot_year=ballot_year,
        )

        self.assertEqual(len(anonymized_data), 3)


class TestParsingParamsMethods(unittest.TestCase):
    def test_get_parsing_indices(self):
        num_parameters = 4

        num_goty_games_per_voter = 5
        num_gotd_games_per_voter = 10

        goty_description_index = num_goty_games_per_voter + 1
        gotd_description_index = goty_description_index + num_gotd_games_per_voter + 1

        for ballot_year in ['2018', '2019', '2020']:
            for is_anonymized in [True, False]:
                indices = parsing_params.get_parsing_indices(
                    year=ballot_year,
                    is_anonymized=is_anonymized,
                )

                self.assertEqual(len(indices.keys()), num_parameters)

                offset = 0 if is_anonymized else 9

                self.assertEqual(indices['voter_name'], offset)

                self.assertEqual(len(indices['main']['goty']), num_goty_games_per_voter)
                self.assertEqual(
                    indices['review']['goty'],
                    goty_description_index + offset,
                )

                if int(ballot_year) == 2019:
                    self.assertEqual(
                        len(indices['main']['gotd']),
                        num_gotd_games_per_voter,
                    )
                    self.assertEqual(
                        indices['review']['gotd'],
                        gotd_description_index + offset,
                    )
                    # caveat: GOTD below, because there exists a GOTD
                    new_offset = gotd_description_index + offset
                else:
                    self.assertEqual(len(indices['main']['gotd']), 0)
                    self.assertEqual(indices['review']['gotd'], None)
                    # caveat: GOTY below, because there is **no** GOTD
                    new_offset = goty_description_index + offset

                self.assertEqual(len(indices['optional']['dlc']), 1)
                self.assertEqual(len(indices['optional']['early_access']), 1)
                if int(ballot_year) == 2018:
                    self.assertEqual(len(indices['optional']['vr']), 0)
                else:
                    self.assertEqual(len(indices['optional']['vr']), 1)
                self.assertEqual(len(indices['optional']['turd']), 1)

                self.assertTrue((1 + new_offset) in indices['optional']['dlc'])
                self.assertTrue((2 + new_offset) in indices['optional']['early_access'])
                if int(ballot_year) == 2018:
                    self.assertTrue((3 + new_offset) in indices['optional']['turd'])
                else:
                    self.assertTrue((3 + new_offset) in indices['optional']['vr'])
                    self.assertTrue((4 + new_offset) in indices['optional']['turd'])


class TestLoadBallotsMethods(unittest.TestCase):
    def test_get_parsing_params(self):
        num_parameters = 6

        num_goty_games_per_voter = 5
        num_gotd_games_per_voter = 10

        for ballot_year in ['2018', '2019', '2020']:
            parsing_params = load_ballots.get_parsing_params(ballot_year=ballot_year)

            self.assertEqual(len(parsing_params.keys()), num_parameters)

            self.assertEqual(
                parsing_params['goty']['num_choices'],
                num_goty_games_per_voter,
            )

            if int(ballot_year) == 2019:
                self.assertEqual(
                    parsing_params['gotd']['num_choices'],
                    num_gotd_games_per_voter,
                )
            else:
                self.assertEqual(parsing_params['gotd']['num_choices'], 0)

            self.assertEqual(parsing_params['dlc']['num_choices'], 1)
            self.assertEqual(parsing_params['early_access']['num_choices'], 1)

            if int(ballot_year) == 2018:
                self.assertEqual(parsing_params['vr']['num_choices'], 0)
            else:
                self.assertEqual(parsing_params['vr']['num_choices'], 1)

            self.assertEqual(parsing_params['turd']['num_choices'], 1)

    def test_load_unanonymized_ballots(self):
        ballot_year = '2018'
        input_filename = (
            'dummy_pc_gaming_metacouncil_goty_awards_' + ballot_year + '.csv'
        )
        ballots = load_ballots.load_ballots(input_filename)

        self.assertEqual(len(ballots), 3)

    def test_load_ballots(self):
        ballot_year = '2018'
        input_filename = 'anonymized_dummy_goty_awards_' + ballot_year + '.csv'
        ballots = load_ballots.load_ballots(input_filename)

        self.assertEqual(len(ballots), 6)


class TestHardCodedMatchesMethods(unittest.TestCase):
    def test_get_hard_coded_app_id_dict(self):
        hard_coded_dict = hard_coded_matches.get_hard_coded_app_id_dict()

        self.assertGreater(len(hard_coded_dict), 0)


class TestDisqualifyVoteMethods(unittest.TestCase):
    def test_get_hard_coded_noisy_votes(self):
        noisy_votes = disqualify_vote.get_hard_coded_noisy_votes()

        empty_game_name = ''
        # The empty string is not part of the hard-coded noisy votes, although it would be consider as noisy later on.
        self.assertTrue(empty_game_name not in noisy_votes)

        for noisy_game_name in ['n/a', 'N/A', '-']:
            self.assertTrue(noisy_game_name in noisy_votes)

    def test_is_a_noisy_vote(self):
        empty_game_name = ''
        game_name_is_a_noisy_vote = disqualify_vote.is_a_noisy_vote(empty_game_name)
        # The empty string is considered as noisy, although it is not part of the hard-coded noisy votes.
        self.assertTrue(game_name_is_a_noisy_vote)

        for noisy_game_name in ['n/a', 'N/A', '-']:
            game_name_is_a_noisy_vote = disqualify_vote.is_a_noisy_vote(noisy_game_name)
            self.assertTrue(game_name_is_a_noisy_vote)

        for real_game_name in ['Hitman', 'Celeste', 'SpyParty']:
            game_name_is_a_noisy_vote = disqualify_vote.is_a_noisy_vote(real_game_name)
            self.assertTrue(not game_name_is_a_noisy_vote)

    def test_get_hard_coded_disqualified_app_ids(self):
        disqualified_app_id_dict = disqualify_vote.get_hard_coded_disqualified_app_ids()

        self.assertGreater(len(disqualified_app_id_dict), 0)

    def test_filter_out_votes_for_hard_coded_reasons(self):
        ballot_year = '2018'
        input_filename = 'anonymized_dummy_goty_awards_' + ballot_year + '.csv'

        ballots = load_ballots.load_ballots(input_filename)

        # Add dummy vote for a game disqualified
        ballots['dummy_voter_name'] = {}
        ballots['dummy_voter_name']['goty_preferences'] = {}
        ballots['dummy_voter_name']['goty_preferences'][
            1
        ] = "Marvel's Spider-Man"  # exclusive to PS4

        (standardized_ballots, _) = match_names.standardize_ballots(
            ballots,
            release_year=ballot_year,
        )

        standardized_ballots = disqualify_vote.filter_out_votes_for_hard_coded_reasons(
            standardized_ballots,
        )

        self.assertTrue(
            bool(standardized_ballots['dummy_voter_name']['ballots'][1] is None),
        )


class TestExtendSteamSpyMethods(unittest.TestCase):
    def test_load_extended_steamspy_database(self):
        extended_steamspy_database = extend_steamspy.load_extended_steamspy_database()

        self.assertGreater(len(extended_steamspy_database), 0)

    def test_load_twice_extended_steamspy_database(self):
        extended_steamspy_database = extend_steamspy.load_extended_steamspy_database()
        extended_steamspy_database = extend_steamspy.load_extended_steamspy_database(
            extended_steamspy_database,
        )

        self.assertGreater(len(extended_steamspy_database), 0)


class TestMatchNamesMethods(unittest.TestCase):
    @staticmethod
    def get_ballots(ballot_year='2018'):
        input_filename = 'anonymized_dummy_goty_awards_' + ballot_year + '.csv'

        ballots = load_ballots.load_ballots(input_filename)

        return ballots

    def test_precompute_matches(self):
        ballot_year = '2018'
        ballots = self.get_ballots(ballot_year)
        matches = match_names.precompute_matches(ballots, release_year=ballot_year)

        match_names.display_matches(matches, print_after_sort=False)

        match_names.display_matches(matches, print_after_sort=True)

        self.assertGreater(len(matches), 0)

    def test_standardize_ballots(self):
        ballot_year = '2018'
        ballots = self.get_ballots(ballot_year)
        (standardized_ballots, _) = match_names.standardize_ballots(
            ballots,
            release_year=ballot_year,
        )

        self.assertEqual(len(ballots), len(standardized_ballots))

    def test_find_closest_app_id(self):
        raw_name = 'Half-Life II'  # Typo ("II" instead of "2") on purpose to increase code coverage
        steamspy_database = extend_steamspy.load_extended_steamspy_database()

        (closest_appID, _) = match_names.find_closest_app_id(
            raw_name,
            steamspy_database,
            release_year='2018',
            num_closest_neighbors=1,
            max_num_tries_for_year=2,
        )

        database_entry = steamspy_database[closest_appID[0]]

        self.assertEqual(database_entry['appid'], 220)
        self.assertEqual(database_entry['name'], 'Half-Life 2')
        self.assertEqual(database_entry['developer'], 'Valve')
        self.assertEqual(database_entry['publisher'], 'Valve')


class TestSchulzeGotyMethods(unittest.TestCase):
    def test_apply_pipeline(self):
        ballot_year = '2018'
        input_filename = 'anonymized_dummy_goty_awards_' + ballot_year + '.csv'

        self.assertTrue(
            schulze_goty.apply_pipeline(
                input_filename,
                release_year=ballot_year,
                try_to_break_ties=True,
            ),
        )

    def test_filtering_out(self):
        ballot_year = '2018'  # anything but '1998'
        input_filename = 'anonymized_dummy_goty_awards_' + ballot_year + '.csv'

        ballots = load_ballots.load_ballots(input_filename)

        # Add dummy vote for a game released in another year
        ballots['dummy_voter_name'] = {}
        ballots['dummy_voter_name']['goty_preferences'] = {}
        ballots['dummy_voter_name']['goty_preferences'][
            1
        ] = "Half-Life"  # released in 1998

        (standardized_ballots, _) = match_names.standardize_ballots(
            ballots,
            release_year=ballot_year,
        )

        standardized_ballots = schulze_goty.filter_out_votes_for_wrong_release_years(
            standardized_ballots,
            target_release_year=ballot_year,
        )

        self.assertTrue(
            bool(standardized_ballots['dummy_voter_name']['ballots'][1] is None),
        )

    def test_filter_out_votes_for_early_access_titles(self):
        ballot_year = '2018'

        ballots = {}

        # Add dummy vote for an Early Access game
        ballots['dummy_voter_name'] = {}
        ballots['dummy_voter_name']['goty_preferences'] = {}
        # The following is a game released in Early Access in 2018, and still in Early Access in 2020:
        ballots['dummy_voter_name']['goty_preferences'][
            1
        ] = 'Aim Lab'  # app_id = '714010'
        # The following is a game released in 2018:
        ballots['dummy_voter_name']['goty_preferences'][
            2
        ] = 'Celeste'  # app_id = '504230'

        (standardized_ballots, _) = match_names.standardize_ballots(
            ballots,
            release_year=ballot_year,
        )

        standardized_ballots = schulze_goty.filter_out_votes_for_early_access_titles(
            standardized_ballots,
        )

        self.assertTrue(
            bool(standardized_ballots['dummy_voter_name']['ballots'][1] == '504230'),
        )
        self.assertTrue(
            bool(standardized_ballots['dummy_voter_name']['ballots'][2] is None),
        )

    def test_try_to_break_ties_in_app_id_group(self):
        app_id_group = ['300']
        standardized_ballots = {
            'A': {'ballots': {1: '100', 2: '200', 3: None, 4: None, 5: None}},
            'B': {'ballots': {1: '200', 2: '100', 3: None, 4: None, 5: None}},
        }
        schulze_ranking_for_tied_app_id_group = (
            schulze_goty.try_to_break_ties_in_app_id_group(
                app_id_group,
                standardized_ballots,
            )
        )
        self.assertEqual(schulze_ranking_for_tied_app_id_group, [['300']])

    def test_try_to_break_ties_in_schulze_ranking(self):
        app_id_group = ['100', '200', '300']
        schulze_ranking = [app_id_group]
        standardized_ballots = {
            'A': {'ballots': {1: '100', 2: '300', 3: '200', 4: None, 5: None}},
            'B': {'ballots': {1: '200', 2: '100', 3: '300', 4: None, 5: None}},
        }
        untied_schulze_ranking = schulze_goty.try_to_break_ties_in_schulze_ranking(
            schulze_ranking,
            standardized_ballots,
        )

        for i, element in enumerate(untied_schulze_ranking):
            untied_schulze_ranking[i] = sorted(element)

        self.assertEqual(untied_schulze_ranking, [['100'], ['200', '300']])


class TestOptionalCategoriesMethods(unittest.TestCase):
    def test_display_optional_ballots(self):
        ballot_year = '2018'
        input_filename = 'anonymized_dummy_goty_awards_' + ballot_year + '.csv'

        self.assertTrue(optional_categories.display_optional_ballots(input_filename))


class TestExtendIGDBMethods(unittest.TestCase):
    def test_get_file_name_for_fixes_to_igdb_database(self):
        for release_year in [None, '2018']:
            for database_type in ['match', 'local']:
                file_name = extend_igdb.get_file_name_for_fixes_to_igdb_database(
                    release_year=release_year,
                    database_type=database_type,
                )
                if release_year is None:
                    expected_file_name = (
                        'data/fixes_to_igdb_' + database_type + '_database.json'
                    )
                else:
                    expected_file_name = (
                        'data/fixes_to_igdb_'
                        + database_type
                        + '_database_'
                        + str(release_year)
                        + '.json'
                    )

                self.assertEqual(file_name, expected_file_name)

    def test_load_fixes_to_igdb_database(self):
        fixes_to_igdb_database = extend_igdb.load_fixes_to_igdb_database()
        self.assertGreaterEqual(len(fixes_to_igdb_database), 0)

    def test_load_fixes_to_igdb_local_database(self):
        fixes_to_igdb_database = extend_igdb.load_fixes_to_igdb_local_database()
        self.assertGreaterEqual(len(fixes_to_igdb_database), 0)

    def test_load_fixes_to_igdb_match_database(self):
        fixes_to_igdb_database = extend_igdb.load_fixes_to_igdb_match_database()
        self.assertGreaterEqual(len(fixes_to_igdb_database), 0)

    def test_extend_igdb_local_database(self):
        release_year = '2018'
        extended_igdb_local_database = extend_igdb.extend_igdb_local_database(
            release_year=release_year,
        )
        self.assertGreater(len(extended_igdb_local_database), 0)

    def test_extend_igdb_match_database(self):
        release_year = '2018'
        extended_igdb_match_database = extend_igdb.extend_igdb_match_database(
            release_year=release_year,
        )
        self.assertGreater(len(extended_igdb_match_database), 0)

    def test_fill_in_blanks_in_the_local_database(self):
        augmented_igdb_local_database = (
            extend_igdb.fill_in_blanks_in_the_local_database(
                release_year='2018',
                save_to_disk=False,
            )
        )
        self.assertGreater(len(augmented_igdb_local_database), 0)

    def test_extend_both_igdb_databases(self):
        (
            extended_igdb_match_database,
            extended_igdb_local_database,
        ) = extend_igdb.extend_both_igdb_databases(release_year='2018')
        self.assertGreater(len(extended_igdb_match_database), 0)
        self.assertGreater(len(extended_igdb_local_database), 0)

    def test_main(self):
        self.assertTrue(extend_igdb.main())


class TestIGDBUtilsMethods(unittest.TestCase):
    def test_get_igdb_api_url(self):
        url = igdb_utils.get_igdb_api_url()
        self.assertEqual(url, 'https://api.igdb.com/v4')

    def test_get_igdb_api_url_for_games(self):
        url = igdb_utils.get_igdb_api_url_for_games()
        self.assertEqual(url, 'https://api.igdb.com/v4/games/')

    def test_get_igdb_api_url_for_release_dates(self):
        url = igdb_utils.get_igdb_api_url_for_release_dates()
        self.assertEqual(url, 'https://api.igdb.com/v4/release_dates/')

    def test_get_time_stamp_for_year_start(self):
        time_stamp = igdb_utils.get_time_stamp_for_year_start(year=1971)
        self.assertGreaterEqual(int(time_stamp), 31532400)

    def test_get_time_stamp_for_year_end(self):
        time_stamp = igdb_utils.get_time_stamp_for_year_end(year=1970)
        self.assertGreaterEqual(int(time_stamp), 31532400)

    def test_get_igdb_user_key_file_name(self):
        file_name = igdb_local_secrets.get_igdb_user_key_file_name()
        self.assertEqual(file_name, 'igdb_user_key.json')

    def test_load_igdb_user_key(self):
        igdb_user_key = igdb_local_secrets.load_igdb_user_key()
        self.assertTrue('user-key' in igdb_user_key)

    def test_get_igdb_request_headers(self):
        headers = igdb_look_up.get_igdb_request_headers()
        self.assertTrue('Accept' in headers)
        self.assertEqual(headers['Accept'], 'application/json')

    def test_get_igdb_request_params(self):
        params = igdb_utils.get_igdb_request_params()
        self.assertEqual(params['fields'], '*')

    def test_get_pc_platform_no(self):
        value = igdb_utils.get_pc_platform_no()
        self.assertEqual(value, 6)

    def test_get_pc_platform_range(self):
        value_list = igdb_utils.get_pc_platform_range()
        self.assertTrue(6 in value_list)

    def test_get_game_category_no(self):
        value_list = igdb_utils.get_game_category_no()
        self.assertEqual(value_list, [0, 3, 4])

    def test_get_dlc_category_no(self):
        value_list = igdb_utils.get_dlc_category_no()
        self.assertEqual(value_list, [1, 2])

    def test_get_released_status_no(self):
        value = igdb_utils.get_released_status_no()
        self.assertEqual(value, 0)

    def test_get_steam_service_no(self):
        value = igdb_utils.get_steam_service_no()
        self.assertEqual(value, 1)

    def test_append_filter_for_igdb_fields(self):
        fields = 'name, slug'
        fields = igdb_utils.append_filter_for_igdb_fields(
            fields,
            'platforms',
            6,
            use_parenthesis=True,
        )
        self.assertTrue('; where ' in fields)

    def test_get_igdb_fields_for_games(self):
        fields = igdb_utils.get_igdb_fields_for_games()
        self.assertGreater(len(fields), 0)

    def test_get_igdb_fields_for_release_dates(self):
        fields = igdb_utils.get_igdb_fields_for_release_dates()
        self.assertGreater(len(fields), 0)

    def test_format_list_of_platforms(self):
        platform_list = [
            {
                'id': 33,
                'abbreviation': 'Game Boy',
                'category': 5,
                'name': 'Game Boy',
                'slug': 'gb',
                'url': 'https://www.igdb.com/platforms/gb',
            },
            {
                'id': 22,
                'abbreviation': 'GBC',
                'category': 5,
                'name': 'Game Boy Color',
                'slug': 'gbc',
                'url': 'https://www.igdb.com/platforms/gbc',
            },
            {
                'id': 24,
                'abbreviation': 'GBA',
                'alternative_name': 'GBA',
                'category': 5,
                'name': 'Game Boy Advance',
                'slug': 'gba',
                'url': 'https://www.igdb.com/platforms/gba',
            },
        ]

        formatted_list = igdb_utils.format_list_of_platforms(platform_list)

        self.assertEqual(len(formatted_list), 3)

    @staticmethod
    def get_read_dead_redemption_two():
        igdb_data = {
            'id': 25076,
            'name': 'Red Dead Redemption 2',
            'platforms': [6, 48, 49, 170],
            'release_dates': [
                {'id': 137262, 'human': '2018-Oct-26', 'platform': 49, 'y': 2018},
                {'id': 137263, 'human': '2018-Oct-26', 'platform': 48, 'y': 2018},
                {'id': 137264, 'human': '2018-Oct-26', 'platform': 48, 'y': 2018},
                {'id': 137265, 'human': '2018-Oct-26', 'platform': 48, 'y': 2018},
                {'id': 137266, 'human': '2018-Oct-26', 'platform': 49, 'y': 2018},
                {'id': 147060, 'human': '2018-Oct-26', 'platform': 49, 'y': 2018},
                {'id': 177006, 'human': '2019-Nov-05', 'platform': 6, 'y': 2019},
                {'id': 179286, 'human': '2019-Nov-19', 'platform': 170, 'y': 2019},
            ],
            'slug': 'red-dead-redemption-2',
        }

        return igdb_data

    def test_format_release_dates_for_manual_display(self):
        igdb_data = self.get_read_dead_redemption_two()
        release_years_as_str = igdb_utils.format_release_dates_for_manual_display(
            element=igdb_data,
        )

        self.assertEqual(release_years_as_str, '2018, 2019')


class TestIGDBMatchNamesMethods(unittest.TestCase):
    @staticmethod
    def get_dummy_match_database():
        dummy_match_database = {
            "Hello": [0],
            "World": [1, 2],
        }

        return dummy_match_database

    @staticmethod
    def get_dummy_local_database():
        igdb_data = TestIGDBUtilsMethods.get_read_dead_redemption_two()
        dummy_local_database = {"25076": igdb_data}

        return dummy_local_database

    def test_get_link_to_igdb_website_with_int_input(self):
        igdb_id = 25076
        igdb_local_database = self.get_dummy_local_database()
        url = igdb_match_names.get_link_to_igdb_website(igdb_id, igdb_local_database)
        self.assertEqual(
            url,
            '[URL=https://www.igdb.com/games/red-dead-redemption-2/]25076[/URL]',
        )

    def test_get_link_to_igdb_website_with_str_input(self):
        igdb_id = '25076'
        igdb_local_database = self.get_dummy_local_database()
        url = igdb_match_names.get_link_to_igdb_website(igdb_id, igdb_local_database)
        self.assertEqual(
            url,
            '[URL=https://www.igdb.com/games/red-dead-redemption-2/]25076[/URL]',
        )

    def test_get_igdb_human_release_dates_with_int_input(self):
        igdb_id = 25076
        igdb_local_database = self.get_dummy_local_database()
        (
            human_release_dates,
            human_release_date_to_remember,
        ) = igdb_match_names.get_igdb_human_release_dates(igdb_id, igdb_local_database)
        self.assertEqual(human_release_date_to_remember, '2019-Nov-05')

    def test_get_igdb_human_release_dates_with_str_input(self):
        igdb_id = '25076'
        igdb_local_database = self.get_dummy_local_database()
        (
            human_release_dates,
            human_release_date_to_remember,
        ) = igdb_match_names.get_igdb_human_release_dates(igdb_id, igdb_local_database)
        self.assertEqual(human_release_date_to_remember, '2019-Nov-05')

    def test_get_igdb_release_years_with_no_target(self):
        igdb_id = '25076'
        igdb_local_database = self.get_dummy_local_database()
        igdb_data = igdb_local_database[igdb_id]
        release_years, year_to_remember = igdb_match_names.get_igdb_release_years(
            igdb_data,
        )
        self.assertEqual(year_to_remember, -1)

    def test_get_igdb_release_years_with_a_target(self):
        igdb_id = '25076'
        igdb_local_database = self.get_dummy_local_database()
        igdb_data = igdb_local_database[igdb_id]
        release_years, year_to_remember = igdb_match_names.get_igdb_release_years(
            igdb_data,
            target_release_year='2018',
        )
        self.assertEqual(year_to_remember, 2019)

    def test_format_game_name_for_igdb(self):
        game_name = 'Hello World'
        formatted_game_name = igdb_match_names.format_game_name_for_igdb(game_name)
        self.assertEqual(formatted_game_name, game_name)

        formatted_game_name = igdb_match_names.format_game_name_for_igdb('Coca-Cola®')
        self.assertEqual(formatted_game_name, 'Coca-Cola')

        formatted_game_name = igdb_match_names.format_game_name_for_igdb(
            'Atelier ~ Anime Game ~',
        )
        self.assertEqual(formatted_game_name, 'Atelier   Anime Game')

    def test_print_igdb_matches(self):
        release_year = '2018'
        igdb_match_names.print_igdb_matches(
            igdb_match_database=igdb_databases.load_igdb_match_database(
                release_year=release_year,
            ),
            igdb_local_database=igdb_databases.load_igdb_local_database(
                release_year=release_year,
            ),
            constrained_release_year=release_year,
        )
        self.assertTrue(True)

    def test_merge_databases_where_entry_is_updated(self):
        new_database = {"a": 2}
        previous_database = {"a": 0, "b": 1}

        merged_database = igdb_match_names.merge_databases(
            new_database=new_database,
            previous_database=previous_database,
        )
        self.assertEqual(len(merged_database), 2)
        self.assertEqual(merged_database["a"], 2)
        self.assertEqual(merged_database["b"], 1)

    def test_merge_databases_where_entry_did_not_exist(self):
        new_database = {"c": 2}
        previous_database = {"a": 0, "b": 1}

        merged_database = igdb_match_names.merge_databases(
            new_database=new_database,
            previous_database=previous_database,
        )
        self.assertEqual(len(merged_database), 3)
        self.assertEqual(merged_database["a"], 0)
        self.assertEqual(merged_database["b"], 1)
        self.assertEqual(merged_database["c"], 2)

    def test_figure_out_ballots_with_missing_data(self):
        dummy_voter = 'dummy_voter_name'
        goty_field = 'dummy_preferences'

        ballots = {}
        ballots[dummy_voter] = {}
        ballots[dummy_voter][goty_field] = {}
        ballots[dummy_voter][goty_field][1] = 'Hello'
        ballots[dummy_voter][goty_field][2] = 'Universe'

        igdb_match_database = self.get_dummy_match_database()

        release_year = '2018'

        new_ballots = igdb_match_names.figure_out_ballots_with_missing_data(
            ballots=ballots,
            igdb_match_database=igdb_match_database,
            release_year=release_year,
            goty_field=goty_field,
            verbose=True,
        )

        empty_vote = ''

        first_vote_is_now_empty = bool(
            new_ballots[dummy_voter][goty_field][1] == empty_vote,
        )
        self.assertTrue(first_vote_is_now_empty)

        second_vote_is_still_intact = bool(
            new_ballots[dummy_voter][goty_field][2]
            == new_ballots[dummy_voter][goty_field][2],
        )
        self.assertTrue(second_vote_is_still_intact)

    def test_load_igdb_local_databases(self):
        ballot_year = '2018'

        ballots = {}

        # Add dummy votes for the two actual GotY 2018 on MetaCouncil
        ballots['dummy_voter_name'] = {}
        ballots['dummy_voter_name']['goty_preferences'] = {}
        ballots['dummy_voter_name']['goty_preferences'][
            1
        ] = 'HITMAN 2'  # IGDB id = '103210'
        ballots['dummy_voter_name']['goty_preferences'][
            2
        ] = 'Pillars of Eternity 2: Deadfire'  # IGDB id = '26951'

        (
            igdb_match_database,
            igdb_local_database,
        ) = igdb_match_names.load_igdb_local_databases(
            ballots=ballots,
            release_year=ballot_year,
        )

        self.assertGreater(len(igdb_match_database), 0)
        self.assertGreater(len(igdb_local_database), 0)

    def test_transform_structure_of_matches(self):
        release_year = '2018'
        igdb_match_database = igdb_databases.load_igdb_match_database(
            release_year=release_year,
        )
        igdb_local_database = igdb_databases.load_igdb_local_database(
            release_year=release_year,
        )

        matches = igdb_match_names.transform_structure_of_matches(
            igdb_match_database=igdb_match_database,
            igdb_local_database=igdb_local_database,
        )
        self.assertGreater(len(matches), 0)

    def test_main(self):
        self.assertTrue(igdb_match_names.main())


class TestIGDBDatabasesMethods(unittest.TestCase):
    def test_get_igdb_file_name_suffix(self):
        for release_year in [None, '2018']:
            suffix = igdb_databases.get_igdb_file_name_suffix(release_year=release_year)
            expected_suffix = '' if release_year is None else '_' + str(release_year)
            self.assertEqual(suffix, expected_suffix)

    def test_get_igdb_match_database_file_name(self):
        for release_year in [None, '2018']:
            file_name = igdb_databases.get_igdb_match_database_file_name(
                release_year=release_year,
            )
            if release_year is None:
                expected_file_name = 'data/igdb_match_database.json'
            else:
                expected_file_name = (
                    'data/igdb_match_database_' + str(release_year) + '.json'
                )
            self.assertEqual(file_name, expected_file_name)

    def test_get_igdb_local_database_file_name(self):
        for release_year in [None, '2018']:
            file_name = igdb_databases.get_igdb_local_database_file_name(
                release_year=release_year,
            )
            if release_year is None:
                expected_file_name = 'data/igdb_local_database.json'
            else:
                expected_file_name = (
                    'data/igdb_local_database_' + str(release_year) + '.json'
                )
            self.assertEqual(file_name, expected_file_name)

    def test_load_igdb_match_database(self):
        release_year = '2018'
        data = igdb_databases.load_igdb_match_database(release_year=release_year)
        self.assertTrue(data is not None)

    def test_save_igdb_match_database(self):
        data = {}
        file_name = 'data/dummy_match_file_for_unit_test.json'
        igdb_databases.save_igdb_match_database(data, file_name=file_name)
        self.assertTrue(Path(file_name).exists())

    def test_load_igdb_local_database(self):
        release_year = '2018'
        data = igdb_databases.load_igdb_local_database(release_year=release_year)
        self.assertTrue(data is not None)

    def test_save_igdb_local_database(self):
        data = {}
        file_name = 'data/dummy_local_file_for_unit_test.json'
        igdb_databases.save_igdb_local_database(data, file_name=file_name)
        self.assertTrue(Path(file_name).exists())

    def test_main(self):
        self.assertTrue(igdb_databases.main())


class TestDisqualifyVoteIGDBMethods(unittest.TestCase):
    def test_get_file_name_for_disqualified_igdb_ids(self):
        for release_year in [None, '2018']:
            file_name = disqualify_vote_igdb.get_file_name_for_disqualified_igdb_ids(
                release_year=release_year,
            )

            if release_year is None:
                expected_file_name = 'data/disqualified_igdb_ids.json'
            else:
                expected_file_name = (
                    'data/disqualified_igdb_ids_' + str(release_year) + '.json'
                )

            self.assertEqual(file_name, expected_file_name)

    def test_load_disqualified_igdb_ids(self):
        disqualified_igdb_ids = disqualify_vote_igdb.load_disqualified_igdb_ids()
        self.assertTrue(disqualified_igdb_ids is not None)

    def test_main(self):
        self.assertTrue(disqualify_vote_igdb.main())


class TestWhiteListVoteIGDBMethods(unittest.TestCase):
    def test_get_file_name_for_whitelisted_igdb_ids(self):
        for release_year in [None, '2018']:
            file_name = whitelist_vote_igdb.get_file_name_for_whitelisted_igdb_ids(
                release_year=release_year,
            )

            if release_year is None:
                expected_file_name = 'data/whitelisted_igdb_ids.json'
            else:
                expected_file_name = (
                    'data/whitelisted_igdb_ids_' + str(release_year) + '.json'
                )

            self.assertEqual(file_name, expected_file_name)

    def test_load_whitelisted_igdb_ids(self):
        whitelisted_igdb_ids = whitelist_vote_igdb.load_whitelisted_igdb_ids()
        self.assertTrue(whitelisted_igdb_ids is not None)

    def test_main(self):
        self.assertTrue(whitelist_vote_igdb.main())


class TestWhiteListVoteMethods(unittest.TestCase):
    def test_get_hard_coded_whitelisted_app_ids(self):
        whitelisted_app_id_dict = whitelist_vote.get_hard_coded_whitelisted_app_ids()
        self.assertGreater(len(whitelisted_app_id_dict), 0)

    def test_load_whitelisted_ids(self):
        whitelisted_app_id_dict = whitelist_vote.load_whitelisted_ids(use_igdb=False)
        self.assertGreater(len(whitelisted_app_id_dict), 0)

    def test_main(self):
        self.assertTrue(whitelist_vote.main())


if __name__ == '__main__':
    unittest.main()
