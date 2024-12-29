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
    def test_parse_text_data(self) -> None:
        voter_name = '"MyTestUserName";'
        goty_votes = '"Half-Life: Alyx";"The Walking Dead: Saints & Sinners";"Fall Guys";"Sakuna";"Yakuza";'
        goty_descr = """"I like the idea of a turn based Yakuza [..] game. Tl;DR, buy it, you won't regret it!";"""
        optional_votes = '"Deep Rock Galactic";"Phasmophobia";"The Walking Dead: Saints & Sinners";"Cyberpunk 2077"'

        line = voter_name + goty_votes + goty_descr + optional_votes

        ballots = parsing_utils.parse_text_data(
            text_data=[line],
            parsing_params=parsing_utils.get_adjusted_parsing_params(2020),
            is_anonymized=True,
        )

        assert ballots["MyTestUserName"]["goty_description"].startswith(
            "I like the idea",
        )
        assert ballots["MyTestUserName"]["goty_description"].endswith(
            "you won't regret it!",
        )
        assert ballots["MyTestUserName"]["best_dlc"] == "Deep Rock Galactic"
        assert ballots["MyTestUserName"]["best_early_access"] == "Phasmophobia"
        assert (
            ballots["MyTestUserName"]["best_vr"] == "The Walking Dead: Saints & Sinners"
        )
        assert ballots["MyTestUserName"]["best_turd"] == "Cyberpunk 2077"


class TestSteamStoreUtilsMethods(unittest.TestCase):
    def test_get_link_to_store_case_valid_app_id(self) -> None:
        app_id = "583950"
        link_to_store = steam_store_utils.get_link_to_store(app_id)
        expected_link = (
            "[URL=https://store.steampowered.com/app/"
            + app_id
            + "/]"
            + app_id
            + "[/URL]"
        )

        assert link_to_store == expected_link

    def test_get_link_to_store_case_dummy_app_id_to_show(self) -> None:
        app_id = "-1"
        link_to_store = steam_store_utils.get_link_to_store(
            app_id,
            hide_dummy_app_id=False,
        )

        assert link_to_store == app_id

    def test_get_link_to_store_case_dummy_app_id_to_hide(self) -> None:
        app_id = "-1"
        link_to_store = steam_store_utils.get_link_to_store(
            app_id,
            hide_dummy_app_id=True,
        )

        assert link_to_store == "n/a"


class TestAnonymizeDataMethods(unittest.TestCase):
    def test_get_author_name_token_index(self) -> None:
        expected_author_token_index = 18
        is_anonymized = False

        for ballot_year in [2018, 2019, 2020]:
            author_token_index = anonymize_data.get_author_name_token_index(
                ballot_year=ballot_year,
                is_anonymized=is_anonymized,
            )
            assert expected_author_token_index == author_token_index

    def test_get_review_token_indices(self) -> None:
        goty_description_token_index = 30
        gotd_description_token_index = 52
        is_anonymized = False

        ballot_year = "2018"
        review_token_indices = anonymize_data.get_review_token_indices(
            ballot_year=ballot_year,
            is_anonymized=is_anonymized,
        )
        assert len(review_token_indices) == 1
        assert goty_description_token_index in review_token_indices

        ballot_year = "2019"
        review_token_indices = anonymize_data.get_review_token_indices(
            ballot_year=ballot_year,
            is_anonymized=is_anonymized,
        )
        assert len(review_token_indices) == 2
        assert goty_description_token_index in review_token_indices
        assert gotd_description_token_index in review_token_indices

        ballot_year = "2020"
        review_token_indices = anonymize_data.get_review_token_indices(
            ballot_year=ballot_year,
            is_anonymized=is_anonymized,
        )
        assert len(review_token_indices) == 1
        assert goty_description_token_index in review_token_indices

    def test_load_and_anonymize(self) -> None:
        ballot_year = "2018"
        input_filename = (
            "dummy_pc_gaming_metacouncil_goty_awards_" + ballot_year + ".csv"
        )
        anonymized_data = anonymize_data.load_and_anonymize(
            input_filename,
            ballot_year=ballot_year,
        )

        assert len(anonymized_data) == 3


class TestParsingParamsMethods(unittest.TestCase):
    def test_get_parsing_indices(self) -> None:
        num_parameters = 4

        num_goty_games_per_voter = 5
        num_gotd_games_per_voter = 10

        goty_description_index = num_goty_games_per_voter + 1
        gotd_description_index = goty_description_index + num_gotd_games_per_voter + 1

        for ballot_year in ["2018", "2019", "2020"]:
            for is_anonymized in [True, False]:
                indices = parsing_params.get_parsing_indices(
                    year=ballot_year,
                    is_anonymized=is_anonymized,
                )

                assert len(indices.keys()) == num_parameters

                offset = 0 if is_anonymized else 9

                assert indices["voter_name"] == offset

                assert len(indices["main"]["goty"]) == num_goty_games_per_voter
                assert indices["review"]["goty"] == goty_description_index + offset

                if int(ballot_year) == 2019:
                    assert len(indices["main"]["gotd"]) == num_gotd_games_per_voter
                    assert indices["review"]["gotd"] == gotd_description_index + offset
                    # caveat: GOTD below, because there exists a GOTD
                    new_offset = gotd_description_index + offset
                else:
                    assert len(indices["main"]["gotd"]) == 0
                    assert indices["review"]["gotd"] is None
                    # caveat: GOTY below, because there is **no** GOTD
                    new_offset = goty_description_index + offset

                assert len(indices["optional"]["dlc"]) == 1
                assert len(indices["optional"]["early_access"]) == 1
                if int(ballot_year) == 2018:
                    assert len(indices["optional"]["vr"]) == 0
                else:
                    assert len(indices["optional"]["vr"]) == 1
                assert len(indices["optional"]["turd"]) == 1

                assert 1 + new_offset in indices["optional"]["dlc"]
                assert 2 + new_offset in indices["optional"]["early_access"]
                if int(ballot_year) == 2018:
                    assert 3 + new_offset in indices["optional"]["turd"]
                else:
                    assert 3 + new_offset in indices["optional"]["vr"]
                    assert 4 + new_offset in indices["optional"]["turd"]


class TestLoadBallotsMethods(unittest.TestCase):
    def test_get_parsing_params(self) -> None:
        num_parameters = 6

        num_goty_games_per_voter = 5
        num_gotd_games_per_voter = 10

        for ballot_year in ["2018", "2019", "2020"]:
            parsing_params = load_ballots.get_parsing_params(ballot_year=ballot_year)

            assert len(parsing_params.keys()) == num_parameters

            assert parsing_params["goty"]["num_choices"] == num_goty_games_per_voter

            if int(ballot_year) == 2019:
                assert parsing_params["gotd"]["num_choices"] == num_gotd_games_per_voter
            else:
                assert parsing_params["gotd"]["num_choices"] == 0

            assert parsing_params["dlc"]["num_choices"] == 1
            assert parsing_params["early_access"]["num_choices"] == 1

            if int(ballot_year) == 2018:
                assert parsing_params["vr"]["num_choices"] == 0
            else:
                assert parsing_params["vr"]["num_choices"] == 1

            assert parsing_params["turd"]["num_choices"] == 1

    def test_load_unanonymized_ballots(self) -> None:
        ballot_year = "2018"
        input_filename = (
            "dummy_pc_gaming_metacouncil_goty_awards_" + ballot_year + ".csv"
        )
        ballots = load_ballots.load_ballots(input_filename)

        assert len(ballots) == 3

    def test_load_ballots(self) -> None:
        ballot_year = "2018"
        input_filename = "anonymized_dummy_goty_awards_" + ballot_year + ".csv"
        ballots = load_ballots.load_ballots(input_filename)

        assert len(ballots) == 6


class TestHardCodedMatchesMethods(unittest.TestCase):
    def test_get_hard_coded_app_id_dict(self) -> None:
        hard_coded_dict = hard_coded_matches.get_hard_coded_app_id_dict()

        assert len(hard_coded_dict) > 0


class TestDisqualifyVoteMethods(unittest.TestCase):
    def test_get_hard_coded_noisy_votes(self) -> None:
        noisy_votes = disqualify_vote.get_hard_coded_noisy_votes()

        empty_game_name = ""
        # The empty string is not part of the hard-coded noisy votes, although it would be consider as noisy later on.
        assert empty_game_name not in noisy_votes

        for noisy_game_name in ["n/a", "N/A", "-"]:
            assert noisy_game_name in noisy_votes

    def test_is_a_noisy_vote(self) -> None:
        empty_game_name = ""
        game_name_is_a_noisy_vote = disqualify_vote.is_a_noisy_vote(empty_game_name)
        # The empty string is considered as noisy, although it is not part of the hard-coded noisy votes.
        assert game_name_is_a_noisy_vote

        for noisy_game_name in ["n/a", "N/A", "-"]:
            game_name_is_a_noisy_vote = disqualify_vote.is_a_noisy_vote(noisy_game_name)
            assert game_name_is_a_noisy_vote

        for real_game_name in ["Hitman", "Celeste", "SpyParty"]:
            game_name_is_a_noisy_vote = disqualify_vote.is_a_noisy_vote(real_game_name)
            assert not game_name_is_a_noisy_vote

    def test_get_hard_coded_disqualified_app_ids(self) -> None:
        disqualified_app_id_dict = disqualify_vote.get_hard_coded_disqualified_app_ids()

        assert len(disqualified_app_id_dict) > 0

    def test_filter_out_votes_for_hard_coded_reasons(self) -> None:
        ballot_year = "2018"
        input_filename = "anonymized_dummy_goty_awards_" + ballot_year + ".csv"

        ballots = load_ballots.load_ballots(input_filename)

        # Add dummy vote for a game disqualified
        ballots["dummy_voter_name"] = {}
        ballots["dummy_voter_name"]["goty_preferences"] = {}
        ballots["dummy_voter_name"]["goty_preferences"][1] = (
            "Marvel's Spider-Man"  # exclusive to PS4
        )

        (standardized_ballots, _) = match_names.standardize_ballots(
            ballots,
            release_year=ballot_year,
        )

        standardized_ballots = disqualify_vote.filter_out_votes_for_hard_coded_reasons(
            standardized_ballots,
        )

        assert bool(standardized_ballots["dummy_voter_name"]["ballots"][1] is None)


class TestExtendSteamSpyMethods(unittest.TestCase):
    def test_load_extended_steamspy_database(self) -> None:
        extended_steamspy_database = extend_steamspy.load_extended_steamspy_database()

        assert len(extended_steamspy_database) > 0

    def test_load_twice_extended_steamspy_database(self) -> None:
        extended_steamspy_database = extend_steamspy.load_extended_steamspy_database()
        extended_steamspy_database = extend_steamspy.load_extended_steamspy_database(
            extended_steamspy_database,
        )

        assert len(extended_steamspy_database) > 0


class TestMatchNamesMethods(unittest.TestCase):
    @staticmethod
    def get_ballots(ballot_year: str = "2018") -> dict:
        input_filename = "anonymized_dummy_goty_awards_" + ballot_year + ".csv"

        return load_ballots.load_ballots(input_filename)

    def test_precompute_matches(self) -> None:
        ballot_year = "2018"
        ballots = self.get_ballots(ballot_year)
        matches = match_names.precompute_matches(ballots, release_year=ballot_year)

        match_names.display_matches(matches, print_after_sort=False)

        match_names.display_matches(matches, print_after_sort=True)

        assert len(matches) > 0

    def test_standardize_ballots(self) -> None:
        ballot_year = "2018"
        ballots = self.get_ballots(ballot_year)
        (standardized_ballots, _) = match_names.standardize_ballots(
            ballots,
            release_year=ballot_year,
        )

        assert len(ballots) == len(standardized_ballots)

    def test_find_closest_app_id(self) -> None:
        raw_name = "Half-Life II"  # Typo ("II" instead of "2") on purpose to increase code coverage
        steamspy_database = extend_steamspy.load_extended_steamspy_database()

        (closest_app_id, _) = match_names.find_closest_app_id(
            raw_name,
            steamspy_database,
            release_year="2018",
            num_closest_neighbors=1,
            max_num_tries_for_year=2,
        )

        database_entry = steamspy_database[closest_app_id[0]]

        assert database_entry["appid"] == 220
        assert database_entry["name"] == "Half-Life 2"
        assert database_entry["developer"] == "Valve"
        assert database_entry["publisher"] == "Valve"


class TestSchulzeGotyMethods(unittest.TestCase):
    def test_apply_pipeline(self) -> None:
        ballot_year = "2018"
        input_filename = "anonymized_dummy_goty_awards_" + ballot_year + ".csv"

        assert schulze_goty.apply_pipeline(
            input_filename,
            release_year=ballot_year,
            try_to_break_ties=True,
        )

    def test_filtering_out(self) -> None:
        ballot_year = "2018"  # anything but '1998'
        input_filename = "anonymized_dummy_goty_awards_" + ballot_year + ".csv"

        ballots = load_ballots.load_ballots(input_filename)

        # Add dummy vote for a game released in another year
        ballots["dummy_voter_name"] = {}
        ballots["dummy_voter_name"]["goty_preferences"] = {}
        ballots["dummy_voter_name"]["goty_preferences"][1] = (
            "Half-Life"  # released in 1998
        )

        (standardized_ballots, _) = match_names.standardize_ballots(
            ballots,
            release_year=ballot_year,
        )

        standardized_ballots = schulze_goty.filter_out_votes_for_wrong_release_years(
            standardized_ballots,
            target_release_year=ballot_year,
        )

        assert bool(standardized_ballots["dummy_voter_name"]["ballots"][1] is None)

    def test_filter_out_votes_for_early_access_titles(self) -> None:
        ballot_year = "2018"

        ballots = {}

        # Add dummy vote for an Early Access game
        ballots["dummy_voter_name"] = {}
        ballots["dummy_voter_name"]["goty_preferences"] = {}
        # The following is a game released in Early Access in 2018, and still in Early Access in 2020:
        ballots["dummy_voter_name"]["goty_preferences"][1] = (
            "Aim Lab"  # app_id = '714010'
        )
        # The following is a game released in 2018:
        ballots["dummy_voter_name"]["goty_preferences"][2] = (
            "Celeste"  # app_id = '504230'
        )

        (standardized_ballots, _) = match_names.standardize_ballots(
            ballots,
            release_year=ballot_year,
        )

        standardized_ballots = schulze_goty.filter_out_votes_for_early_access_titles(
            standardized_ballots,
        )

        assert bool(standardized_ballots["dummy_voter_name"]["ballots"][1] == "504230")
        assert bool(standardized_ballots["dummy_voter_name"]["ballots"][2] is None)

    def test_try_to_break_ties_in_app_id_group(self) -> None:
        app_id_group = ["300"]
        standardized_ballots = {
            "A": {"ballots": {1: "100", 2: "200", 3: None, 4: None, 5: None}},
            "B": {"ballots": {1: "200", 2: "100", 3: None, 4: None, 5: None}},
        }
        schulze_ranking_for_tied_app_id_group = (
            schulze_goty.try_to_break_ties_in_app_id_group(
                app_id_group,
                standardized_ballots,
            )
        )
        assert schulze_ranking_for_tied_app_id_group == [["300"]]

    def test_try_to_break_ties_in_schulze_ranking(self) -> None:
        app_id_group = ["100", "200", "300"]
        schulze_ranking = [app_id_group]
        standardized_ballots = {
            "A": {"ballots": {1: "100", 2: "300", 3: "200", 4: None, 5: None}},
            "B": {"ballots": {1: "200", 2: "100", 3: "300", 4: None, 5: None}},
        }
        untied_schulze_ranking = schulze_goty.try_to_break_ties_in_schulze_ranking(
            schulze_ranking,
            standardized_ballots,
        )

        for i, element in enumerate(untied_schulze_ranking):
            untied_schulze_ranking[i] = sorted(element)

        assert untied_schulze_ranking == [["100"], ["200", "300"]]


class TestOptionalCategoriesMethods(unittest.TestCase):
    def test_display_optional_ballots(self) -> None:
        ballot_year = "2018"
        input_filename = "anonymized_dummy_goty_awards_" + ballot_year + ".csv"

        assert optional_categories.display_optional_ballots(input_filename)


class TestExtendIGDBMethods(unittest.TestCase):
    def test_get_file_name_for_fixes_to_igdb_database(self) -> None:
        for release_year in [None, "2018"]:
            for database_type in ["match", "local"]:
                file_name = extend_igdb.get_file_name_for_fixes_to_igdb_database(
                    release_year=release_year,
                    database_type=database_type,
                )
                if release_year is None:
                    expected_file_name = (
                        "data/fixes_to_igdb_" + database_type + "_database.json"
                    )
                else:
                    expected_file_name = (
                        "data/fixes_to_igdb_"
                        + database_type
                        + "_database_"
                        + str(release_year)
                        + ".json"
                    )

                assert file_name == expected_file_name

    def test_load_fixes_to_igdb_database(self) -> None:
        fixes_to_igdb_database = extend_igdb.load_fixes_to_igdb_database()
        assert len(fixes_to_igdb_database) >= 0

    def test_load_fixes_to_igdb_local_database(self) -> None:
        fixes_to_igdb_database = extend_igdb.load_fixes_to_igdb_local_database()
        assert len(fixes_to_igdb_database) >= 0

    def test_load_fixes_to_igdb_match_database(self) -> None:
        fixes_to_igdb_database = extend_igdb.load_fixes_to_igdb_match_database()
        assert len(fixes_to_igdb_database) >= 0

    def test_extend_igdb_local_database(self) -> None:
        release_year = "2018"
        extended_igdb_local_database = extend_igdb.extend_igdb_local_database(
            release_year=release_year,
        )
        assert len(extended_igdb_local_database) > 0

    def test_extend_igdb_match_database(self) -> None:
        release_year = "2018"
        extended_igdb_match_database = extend_igdb.extend_igdb_match_database(
            release_year=release_year,
        )
        assert len(extended_igdb_match_database) > 0

    def test_fill_in_blanks_in_the_local_database(self) -> None:
        augmented_igdb_local_database = (
            extend_igdb.fill_in_blanks_in_the_local_database(
                release_year="2018",
                save_to_disk=False,
            )
        )
        assert len(augmented_igdb_local_database) > 0

    def test_extend_both_igdb_databases(self) -> None:
        (
            extended_igdb_match_database,
            extended_igdb_local_database,
        ) = extend_igdb.extend_both_igdb_databases(release_year="2018")
        assert len(extended_igdb_match_database) > 0
        assert len(extended_igdb_local_database) > 0

    def test_main(self) -> None:
        assert extend_igdb.main()


class TestIGDBUtilsMethods(unittest.TestCase):
    def test_get_igdb_api_url(self) -> None:
        url = igdb_utils.get_igdb_api_url()
        assert url == "https://api.igdb.com/v4"

    def test_get_igdb_api_url_for_games(self) -> None:
        url = igdb_utils.get_igdb_api_url_for_games()
        assert url == "https://api.igdb.com/v4/games/"

    def test_get_igdb_api_url_for_release_dates(self) -> None:
        url = igdb_utils.get_igdb_api_url_for_release_dates()
        assert url == "https://api.igdb.com/v4/release_dates/"

    def test_get_time_stamp_for_year_start(self) -> None:
        time_stamp = igdb_utils.get_time_stamp_for_year_start(year=1971)
        assert int(time_stamp) >= 31532400

    def test_get_time_stamp_for_year_end(self) -> None:
        time_stamp = igdb_utils.get_time_stamp_for_year_end(year=1970)
        assert int(time_stamp) >= 31532400

    def test_get_igdb_user_key_file_name(self) -> None:
        file_name = igdb_local_secrets.get_igdb_user_key_file_name()
        assert file_name == "igdb_user_key.json"

    def test_load_igdb_user_key(self) -> None:
        igdb_user_key = igdb_local_secrets.load_igdb_user_key()
        assert "user-key" in igdb_user_key

    def test_get_igdb_request_headers(self) -> None:
        headers = igdb_look_up.get_igdb_request_headers()
        assert "Accept" in headers
        assert headers["Accept"] == "application/json"

    def test_get_igdb_request_params(self) -> None:
        params = igdb_utils.get_igdb_request_params()
        assert params["fields"] == "*"

    def test_get_pc_platform_no(self) -> None:
        value = igdb_utils.get_pc_platform_no()
        assert value == 6

    def test_get_pc_platform_range(self) -> None:
        value_list = igdb_utils.get_pc_platform_range()
        assert 6 in value_list

    def test_get_game_category_no(self) -> None:
        value_list = igdb_utils.get_game_category_no()
        assert value_list == [0, 3, 4]

    def test_get_dlc_category_no(self) -> None:
        value_list = igdb_utils.get_dlc_category_no()
        assert value_list == [1, 2]

    def test_get_released_status_no(self) -> None:
        value = igdb_utils.get_released_status_no()
        assert value == 0

    def test_get_steam_service_no(self) -> None:
        value = igdb_utils.get_steam_service_no()
        assert value == 1

    def test_append_filter_for_igdb_fields(self) -> None:
        fields = "name, slug"
        fields = igdb_utils.append_filter_for_igdb_fields(
            fields,
            "platforms",
            6,
            use_parenthesis=True,
        )
        assert "; where " in fields

    def test_get_igdb_fields_for_games(self) -> None:
        fields = igdb_utils.get_igdb_fields_for_games()
        assert len(fields) > 0

    def test_get_igdb_fields_for_release_dates(self) -> None:
        fields = igdb_utils.get_igdb_fields_for_release_dates()
        assert len(fields) > 0

    def test_format_list_of_platforms(self) -> None:
        platform_list = [
            {
                "id": 33,
                "abbreviation": "Game Boy",
                "category": 5,
                "name": "Game Boy",
                "slug": "gb",
                "url": "https://www.igdb.com/platforms/gb",
            },
            {
                "id": 22,
                "abbreviation": "GBC",
                "category": 5,
                "name": "Game Boy Color",
                "slug": "gbc",
                "url": "https://www.igdb.com/platforms/gbc",
            },
            {
                "id": 24,
                "abbreviation": "GBA",
                "alternative_name": "GBA",
                "category": 5,
                "name": "Game Boy Advance",
                "slug": "gba",
                "url": "https://www.igdb.com/platforms/gba",
            },
        ]

        formatted_list = igdb_utils.format_list_of_platforms(platform_list)

        assert len(formatted_list) == 3

    @staticmethod
    def get_read_dead_redemption_two() -> dict:
        return {
            "id": 25076,
            "name": "Red Dead Redemption 2",
            "platforms": [6, 48, 49, 170],
            "release_dates": [
                {"id": 137262, "human": "2018-Oct-26", "platform": 49, "y": 2018},
                {"id": 137263, "human": "2018-Oct-26", "platform": 48, "y": 2018},
                {"id": 137264, "human": "2018-Oct-26", "platform": 48, "y": 2018},
                {"id": 137265, "human": "2018-Oct-26", "platform": 48, "y": 2018},
                {"id": 137266, "human": "2018-Oct-26", "platform": 49, "y": 2018},
                {"id": 147060, "human": "2018-Oct-26", "platform": 49, "y": 2018},
                {"id": 177006, "human": "2019-Nov-05", "platform": 6, "y": 2019},
                {"id": 179286, "human": "2019-Nov-19", "platform": 170, "y": 2019},
            ],
            "slug": "red-dead-redemption-2",
        }

    def test_format_release_dates_for_manual_display(self) -> None:
        igdb_data = self.get_read_dead_redemption_two()
        release_years_as_str = igdb_utils.format_release_dates_for_manual_display(
            element=igdb_data,
        )

        assert release_years_as_str == "2018, 2019"


class TestIGDBMatchNamesMethods(unittest.TestCase):
    @staticmethod
    def get_dummy_match_database() -> dict[str, list[int]]:
        return {
            "Hello": [0],
            "World": [1, 2],
        }

    @staticmethod
    def get_dummy_local_database() -> dict[str, dict]:
        igdb_data = TestIGDBUtilsMethods.get_read_dead_redemption_two()
        return {"25076": igdb_data}

    def test_get_link_to_igdb_website_with_int_input(self) -> None:
        igdb_id = 25076
        igdb_local_database = self.get_dummy_local_database()
        url = igdb_match_names.get_link_to_igdb_website(igdb_id, igdb_local_database)
        assert (
            url == "[URL=https://www.igdb.com/games/red-dead-redemption-2/]25076[/URL]"
        )

    def test_get_link_to_igdb_website_with_str_input(self) -> None:
        igdb_id = "25076"
        igdb_local_database = self.get_dummy_local_database()
        url = igdb_match_names.get_link_to_igdb_website(igdb_id, igdb_local_database)
        assert (
            url == "[URL=https://www.igdb.com/games/red-dead-redemption-2/]25076[/URL]"
        )

    def test_get_igdb_human_release_dates_with_int_input(self) -> None:
        igdb_id = 25076
        igdb_local_database = self.get_dummy_local_database()
        (
            _human_release_dates,
            human_release_date_to_remember,
        ) = igdb_match_names.get_igdb_human_release_dates(igdb_id, igdb_local_database)
        assert human_release_date_to_remember == "2019-Nov-05"

    def test_get_igdb_human_release_dates_with_str_input(self) -> None:
        igdb_id = "25076"
        igdb_local_database = self.get_dummy_local_database()
        (
            _human_release_dates,
            human_release_date_to_remember,
        ) = igdb_match_names.get_igdb_human_release_dates(igdb_id, igdb_local_database)
        assert human_release_date_to_remember == "2019-Nov-05"

    def test_get_igdb_release_years_with_no_target(self) -> None:
        igdb_id = "25076"
        igdb_local_database = self.get_dummy_local_database()
        igdb_data = igdb_local_database[igdb_id]
        _release_years, year_to_remember = igdb_match_names.get_igdb_release_years(
            igdb_data,
        )
        assert year_to_remember == -1

    def test_get_igdb_release_years_with_a_target(self) -> None:
        igdb_id = "25076"
        igdb_local_database = self.get_dummy_local_database()
        igdb_data = igdb_local_database[igdb_id]
        _release_years, year_to_remember = igdb_match_names.get_igdb_release_years(
            igdb_data,
            target_release_year="2018",
        )
        assert year_to_remember == 2019

    def test_format_game_name_for_igdb(self) -> None:
        game_name = "Hello World"
        formatted_game_name = igdb_match_names.format_game_name_for_igdb(game_name)
        assert formatted_game_name == game_name

        formatted_game_name = igdb_match_names.format_game_name_for_igdb("Coca-Cola®")
        assert formatted_game_name == "Coca-Cola"

        formatted_game_name = igdb_match_names.format_game_name_for_igdb(
            "Atelier ~ Anime Game ~",
        )
        assert formatted_game_name == "Atelier   Anime Game"

    def test_print_igdb_matches(self) -> None:
        release_year = "2018"
        igdb_match_names.print_igdb_matches(
            igdb_match_database=igdb_databases.load_igdb_match_database(
                release_year=release_year,
            ),
            igdb_local_database=igdb_databases.load_igdb_local_database(
                release_year=release_year,
            ),
            constrained_release_year=release_year,
        )
        assert True

    def test_merge_databases_where_entry_is_updated(self) -> None:
        new_database = {"a": 2}
        previous_database = {"a": 0, "b": 1}

        merged_database = igdb_match_names.merge_databases(
            new_database=new_database,
            previous_database=previous_database,
        )
        assert len(merged_database) == 2
        assert merged_database["a"] == 2
        assert merged_database["b"] == 1

    def test_merge_databases_where_entry_did_not_exist(self) -> None:
        new_database = {"c": 2}
        previous_database = {"a": 0, "b": 1}

        merged_database = igdb_match_names.merge_databases(
            new_database=new_database,
            previous_database=previous_database,
        )
        assert len(merged_database) == 3
        assert merged_database["a"] == 0
        assert merged_database["b"] == 1
        assert merged_database["c"] == 2

    def test_figure_out_ballots_with_missing_data(self) -> None:
        dummy_voter = "dummy_voter_name"
        goty_field = "dummy_preferences"

        ballots = {}
        ballots[dummy_voter] = {}
        ballots[dummy_voter][goty_field] = {}
        ballots[dummy_voter][goty_field][1] = "Hello"
        ballots[dummy_voter][goty_field][2] = "Universe"

        igdb_match_database = self.get_dummy_match_database()

        release_year = "2018"

        new_ballots = igdb_match_names.figure_out_ballots_with_missing_data(
            ballots=ballots,
            igdb_match_database=igdb_match_database,
            release_year=release_year,
            goty_field=goty_field,
            verbose=True,
        )

        empty_vote = ""

        first_vote_is_now_empty = bool(
            new_ballots[dummy_voter][goty_field][1] == empty_vote,
        )
        assert first_vote_is_now_empty

        second_vote_is_still_intact = bool(
            new_ballots[dummy_voter][goty_field][2]
            == new_ballots[dummy_voter][goty_field][2],
        )
        assert second_vote_is_still_intact

    def test_load_igdb_local_databases(self) -> None:
        ballot_year = "2018"

        ballots = {}

        # Add dummy votes for the two actual GotY 2018 on MetaCouncil
        ballots["dummy_voter_name"] = {}
        ballots["dummy_voter_name"]["goty_preferences"] = {}
        ballots["dummy_voter_name"]["goty_preferences"][1] = (
            "HITMAN 2"  # IGDB id = '103210'
        )
        ballots["dummy_voter_name"]["goty_preferences"][2] = (
            "Pillars of Eternity 2: Deadfire"  # IGDB id = '26951'
        )

        (
            igdb_match_database,
            igdb_local_database,
        ) = igdb_match_names.load_igdb_local_databases(
            ballots=ballots,
            release_year=ballot_year,
        )

        assert len(igdb_match_database) > 0
        assert len(igdb_local_database) > 0

    def test_transform_structure_of_matches(self) -> None:
        release_year = "2018"
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
        assert len(matches) > 0

    def test_main(self) -> None:
        assert igdb_match_names.main()


class TestIGDBDatabasesMethods(unittest.TestCase):
    def test_get_igdb_file_name_suffix(self) -> None:
        for release_year in [None, "2018"]:
            suffix = igdb_databases.get_igdb_file_name_suffix(release_year=release_year)
            expected_suffix = "" if release_year is None else "_" + str(release_year)
            assert suffix == expected_suffix

    def test_get_igdb_match_database_file_name(self) -> None:
        for release_year in [None, "2018"]:
            file_name = igdb_databases.get_igdb_match_database_file_name(
                release_year=release_year,
            )
            if release_year is None:
                expected_file_name = "data/igdb_match_database.json"
            else:
                expected_file_name = (
                    "data/igdb_match_database_" + str(release_year) + ".json"
                )
            assert file_name == expected_file_name

    def test_get_igdb_local_database_file_name(self) -> None:
        for release_year in [None, "2018"]:
            file_name = igdb_databases.get_igdb_local_database_file_name(
                release_year=release_year,
            )
            if release_year is None:
                expected_file_name = "data/igdb_local_database.json"
            else:
                expected_file_name = (
                    "data/igdb_local_database_" + str(release_year) + ".json"
                )
            assert file_name == expected_file_name

    def test_load_igdb_match_database(self) -> None:
        release_year = "2018"
        data = igdb_databases.load_igdb_match_database(release_year=release_year)
        assert data is not None

    def test_save_igdb_match_database(self) -> None:
        data = {}
        file_name = "data/dummy_match_file_for_unit_test.json"
        igdb_databases.save_igdb_match_database(data, file_name=file_name)
        assert Path(file_name).exists()

    def test_load_igdb_local_database(self) -> None:
        release_year = "2018"
        data = igdb_databases.load_igdb_local_database(release_year=release_year)
        assert data is not None

    def test_save_igdb_local_database(self) -> None:
        data = {}
        file_name = "data/dummy_local_file_for_unit_test.json"
        igdb_databases.save_igdb_local_database(data, file_name=file_name)
        assert Path(file_name).exists()

    def test_main(self) -> None:
        assert igdb_databases.main()


class TestDisqualifyVoteIGDBMethods(unittest.TestCase):
    def test_get_file_name_for_disqualified_igdb_ids(self) -> None:
        for release_year in [None, "2018"]:
            file_name = disqualify_vote_igdb.get_file_name_for_disqualified_igdb_ids(
                release_year=release_year,
            )

            if release_year is None:
                expected_file_name = "data/disqualified_igdb_ids.json"
            else:
                expected_file_name = (
                    "data/disqualified_igdb_ids_" + str(release_year) + ".json"
                )

            assert file_name == expected_file_name

    def test_load_disqualified_igdb_ids(self) -> None:
        disqualified_igdb_ids = disqualify_vote_igdb.load_disqualified_igdb_ids()
        assert disqualified_igdb_ids is not None

    def test_main(self) -> None:
        assert disqualify_vote_igdb.main()


class TestWhiteListVoteIGDBMethods(unittest.TestCase):
    def test_get_file_name_for_whitelisted_igdb_ids(self) -> None:
        for release_year in [None, "2018"]:
            file_name = whitelist_vote_igdb.get_file_name_for_whitelisted_igdb_ids(
                release_year=release_year,
            )

            if release_year is None:
                expected_file_name = "data/whitelisted_igdb_ids.json"
            else:
                expected_file_name = (
                    "data/whitelisted_igdb_ids_" + str(release_year) + ".json"
                )

            assert file_name == expected_file_name

    def test_load_whitelisted_igdb_ids(self) -> None:
        whitelisted_igdb_ids = whitelist_vote_igdb.load_whitelisted_igdb_ids()
        assert whitelisted_igdb_ids is not None

    def test_main(self) -> None:
        assert whitelist_vote_igdb.main()


class TestWhiteListVoteMethods(unittest.TestCase):
    def test_get_hard_coded_whitelisted_app_ids(self) -> None:
        whitelisted_app_id_dict = whitelist_vote.get_hard_coded_whitelisted_app_ids()
        assert len(whitelisted_app_id_dict) > 0

    def test_load_whitelisted_ids(self) -> None:
        whitelisted_app_id_dict = whitelist_vote.load_whitelisted_ids(use_igdb=False)
        assert len(whitelisted_app_id_dict) > 0

    def test_main(self) -> None:
        assert whitelist_vote.main()


if __name__ == "__main__":
    unittest.main()
