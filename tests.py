import unittest

import anonymize_data
import disqualify_vote
import extend_steamspy
import hard_coded_matches
import load_ballots
import match_names
import optional_categories
import schulze_goty


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

        self.assertTrue(schulze_goty.apply_pipeline(input_filename, release_year=ballot_year))

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


class TestOptionalCategoriesMethods(unittest.TestCase):

    def test_display_optional_ballots(self):
        ballot_year = '2018'
        input_filename = 'anonymized_dummy_goty_awards_' + ballot_year + '.csv'

        self.assertTrue(optional_categories.display_optional_ballots(input_filename))


if __name__ == '__main__':
    unittest.main()
