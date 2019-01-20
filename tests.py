import unittest

import anonymize_data
import disqualify_vote
import extend_steamspy
import hard_coded_matches
import load_ballots
import match_names
import optional_categories
import schulze_goty
import steam_store_utils


class TestSteamStoreUtilsMethods(unittest.TestCase):

    def test_get_link_to_store_case_valid_app_id(self):
        app_id = '583950'
        link_to_store = steam_store_utils.get_link_to_store(app_id)
        expected_link = '[URL=https://store.steampowered.com/app/' + app_id + '/]' + app_id + '[/URL]'

        self.assertEqual(link_to_store, expected_link)

    def test_get_link_to_store_case_dummy_app_id_to_show(self):
        app_id = '-1'
        link_to_store = steam_store_utils.get_link_to_store(app_id, hide_dummy_app_id=False)

        self.assertEqual(link_to_store, app_id)

    def test_get_link_to_store_case_dummy_app_id_to_hide(self):
        app_id = '-1'
        link_to_store = steam_store_utils.get_link_to_store(app_id, hide_dummy_app_id=True)

        self.assertEqual(link_to_store, 'n/a')


class TestAnonymizeDataMethods(unittest.TestCase):

    def test_load_and_anonymize(self):
        ballot_year = '2018'
        input_filename = 'dummy_pc_gaming_metacouncil_goty_awards_' + ballot_year + '.csv'
        anonymized_data = anonymize_data.load_and_anonymize(input_filename)

        self.assertEqual(len(anonymized_data), 3)


class TestLoadBallotsMethods(unittest.TestCase):

    def test_load_unanonymized_ballots(self):
        ballot_year = '2018'
        input_filename = 'dummy_pc_gaming_metacouncil_goty_awards_' + ballot_year + '.csv'
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

    def test_get_hard_coded_disqualified_app_ids(self):
        disqualified_app_id_dict = disqualify_vote.get_hard_coded_disqualified_app_ids()

        self.assertGreater(len(disqualified_app_id_dict), 0)

    def test_filter_out_votes_for_hard_coded_reasons(self):
        ballot_year = '2018'
        input_filename = 'anonymized_dummy_goty_awards_' + ballot_year + '.csv'

        ballots = load_ballots.load_ballots(input_filename)

        # Add dummy vote for a game disqualified
        ballots['dummy_voter_name'] = dict()
        ballots['dummy_voter_name']['goty_preferences'] = dict()
        ballots['dummy_voter_name']['goty_preferences'][1] = "Marvel's Spider-Man"  # exclusive to PS4

        (standardized_ballots, _) = match_names.standardize_ballots(ballots, release_year=ballot_year)

        standardized_ballots = disqualify_vote.filter_out_votes_for_hard_coded_reasons(standardized_ballots)

        self.assertTrue(bool(standardized_ballots['dummy_voter_name']['ballots'][1] is None))


class TestExtendSteamSpyMethods(unittest.TestCase):

    def test_load_extended_steamspy_database(self):
        extended_steamspy_database = extend_steamspy.load_extended_steamspy_database()

        self.assertGreater(len(extended_steamspy_database), 0)

    def test_load_twice_extended_steamspy_database(self):
        extended_steamspy_database = extend_steamspy.load_extended_steamspy_database()
        extended_steamspy_database = extend_steamspy.load_extended_steamspy_database(extended_steamspy_database)

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
        (standardized_ballots, _) = match_names.standardize_ballots(ballots, release_year=ballot_year)

        self.assertEqual(len(ballots), len(standardized_ballots))

    def test_find_closest_app_id(self):
        raw_name = 'Half-Life II'  # Typo ("II" instead of "2") on purpose to increase code coverage
        steamspy_database = extend_steamspy.load_extended_steamspy_database()

        (closest_appID, _) = match_names.find_closest_app_id(raw_name, steamspy_database,
                                                             release_year='2018',
                                                             num_closest_neighbors=1,
                                                             max_num_tries_for_year=2)

        database_entry = steamspy_database[closest_appID[0]]

        self.assertEqual(database_entry['appid'], 220)
        self.assertEqual(database_entry['name'], 'Half-Life 2')
        self.assertEqual(database_entry['developer'], 'Valve')
        self.assertEqual(database_entry['publisher'], 'Valve')


class TestSchulzeGotyMethods(unittest.TestCase):

    def test_apply_pipeline(self):
        ballot_year = '2018'
        input_filename = 'anonymized_dummy_goty_awards_' + ballot_year + '.csv'

        self.assertTrue(schulze_goty.apply_pipeline(input_filename, release_year=ballot_year, try_to_break_ties=True))

    def test_filtering_out(self):
        ballot_year = '2018'  # anything but '1998'
        input_filename = 'anonymized_dummy_goty_awards_' + ballot_year + '.csv'

        ballots = load_ballots.load_ballots(input_filename)

        # Add dummy vote for a game released in another year
        ballots['dummy_voter_name'] = dict()
        ballots['dummy_voter_name']['goty_preferences'] = dict()
        ballots['dummy_voter_name']['goty_preferences'][1] = "Half-Life"  # released in 1998

        (standardized_ballots, _) = match_names.standardize_ballots(ballots, release_year=ballot_year)

        standardized_ballots = schulze_goty.filter_out_votes_for_wrong_release_years(standardized_ballots,
                                                                                     target_release_year=ballot_year)

        self.assertTrue(bool(standardized_ballots['dummy_voter_name']['ballots'][1] is None))

    def test_filter_out_votes_for_early_access_titles(self):
        ballot_year = '2018'

        ballots = dict()

        # Add dummy vote for an Early Access game
        ballots['dummy_voter_name'] = dict()
        ballots['dummy_voter_name']['goty_preferences'] = dict()
        ballots['dummy_voter_name']['goty_preferences'][1] = 'SpyParty'  # app_id = '329070'
        ballots['dummy_voter_name']['goty_preferences'][2] = 'Celeste'  # app_id = '504230'

        (standardized_ballots, _) = match_names.standardize_ballots(ballots, release_year=ballot_year)

        standardized_ballots = schulze_goty.filter_out_votes_for_early_access_titles(standardized_ballots)

        self.assertTrue(bool(standardized_ballots['dummy_voter_name']['ballots'][1] == '504230'))
        self.assertTrue(bool(standardized_ballots['dummy_voter_name']['ballots'][2] is None))

    def test_try_to_break_ties_in_app_id_group(self):
        app_id_group = ['300']
        standardized_ballots = {
            'A': {
                'ballots': {1: '100', 2: '200', 3: None, 4: None, 5: None}
            },
            'B': {
                'ballots': {1: '200', 2: '100', 3: None, 4: None, 5: None}
            },
        }
        schulze_ranking_for_tied_app_id_group = schulze_goty.try_to_break_ties_in_app_id_group(app_id_group,
                                                                                               standardized_ballots)
        self.assertEqual(schulze_ranking_for_tied_app_id_group, [['300']])

    def test_try_to_break_ties_in_schulze_ranking(self):
        app_id_group = ['100', '200', '300']
        schulze_ranking = [app_id_group]
        standardized_ballots = {
            'A': {
                'ballots': {1: '100', 2: '300', 3: '200', 4: None, 5: None}
            },
            'B': {
                'ballots': {1: '200', 2: '100', 3: '300', 4: None, 5: None}
            },
        }
        untied_schulze_ranking = schulze_goty.try_to_break_ties_in_schulze_ranking(schulze_ranking,
                                                                                   standardized_ballots)

        for (i, element) in enumerate(untied_schulze_ranking):
            untied_schulze_ranking[i] = sorted(element)

        self.assertEqual(untied_schulze_ranking, [['100'], ['200', '300']])


class TestOptionalCategoriesMethods(unittest.TestCase):

    def test_display_optional_ballots(self):
        ballot_year = '2018'
        input_filename = 'anonymized_dummy_goty_awards_' + ballot_year + '.csv'

        self.assertTrue(optional_categories.display_optional_ballots(input_filename))


if __name__ == '__main__':
    unittest.main()
