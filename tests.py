import unittest

import anonymize_data
import schulze_goty


class TestAnonymizeDataMethods(unittest.TestCase):

    def test_load_and_anonymize(self):
        input_filename = 'dummy_pc_gaming_metacouncil_goty_awards_2018.csv'
        anonymized_data = anonymize_data.load_and_anonymize(input_filename)

        self.assertEqual(len(anonymized_data), 3)


class TestSchulzeGotyMethods(unittest.TestCase):

    def test_main(self):
        self.assertTrue(schulze_goty.main())


if __name__ == '__main__':
    unittest.main()
