import unittest

import anonymize_data
import load_ballots
import match_names
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


class TestMatchNamesMethods(unittest.TestCase):

    @staticmethod
    def get_ballots(ballot_year='2018'):
        from load_ballots import load_ballots

        input_filename = 'anonymized_dummy_goty_awards_' + ballot_year + '.csv'

        ballots = load_ballots(input_filename)

        return ballots

    def test_get_matches(self):
        ballot_year = '2018'
        ballots = self.get_ballots(ballot_year)
        matches = match_names.get_matches(ballots, release_year=ballot_year)

        self.assertGreater(len(matches), 0)

    def test_standardize_ballots(self):
        ballot_year = '2018'
        ballots = self.get_ballots(ballot_year)
        standardized_ballots = match_names.standardize_ballots(ballots, release_year=ballot_year)

        self.assertEqual(len(ballots), len(standardized_ballots))

    def test_find_closest_app_id(self):
        raw_name = 'Half-Life'
        steamspy_database = match_names.load_extended_steamspy_database()

        (closest_appID, closest_distance) = match_names.find_closest_app_id(raw_name, steamspy_database,
                                                                            num_closest_neighbors=1,
                                                                            release_year='2018',
                                                                            max_num_tries_for_year=2)

        self.assertEqual(steamspy_database[closest_appID[0]]['developer'], 'Valve')


class TestSchulzeGotyMethods(unittest.TestCase):

    def test_apply_pipeline(self):
        ballot_year = '2018'
        input_filename = 'anonymized_dummy_goty_awards_' + ballot_year + '.csv'

        self.assertTrue(schulze_goty.apply_pipeline(input_filename, release_year=ballot_year))


if __name__ == '__main__':
    unittest.main()
