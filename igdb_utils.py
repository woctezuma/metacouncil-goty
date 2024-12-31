# Objective: look-up games and release dates on IGDB:
#
# Reference: https://api-docs.igdb.com/?kotlin#endpoints

import datetime
import operator

FIELD_SEPARATOR: str = ", "


def get_igdb_api_url(end_point: str | None = None) -> str:
    igdb_api_url = "https://api.igdb.com/v4"

    if end_point is not None:
        url_separator = "/"

        if not end_point.startswith(url_separator):
            end_point = url_separator + end_point

        if not end_point.endswith(url_separator):
            end_point += url_separator

        # NB: the end-point should look like '/games/' or '/release_dates/'

        igdb_api_url += end_point

    return igdb_api_url


def get_igdb_api_url_for_games() -> str:
    end_point = "/games/"
    return get_igdb_api_url(end_point=end_point)


def get_igdb_api_url_for_release_dates() -> str:
    end_point = "/release_dates/"
    return get_igdb_api_url(end_point=end_point)


def get_time_stamp_for_year_start(year: int) -> float:
    return datetime.datetime(year, 1, 1, tzinfo=datetime.UTC).timestamp()


def get_time_stamp_for_year_end(year: int) -> float:
    return get_time_stamp_for_year_start(year=year + 1)


def get_igdb_request_params() -> dict[str, str | int]:
    return {
        "fields": "*",  # It would be better if the fields were explicitly stated (and narrowed down to what is needed)!
        "limit": 10,  # max value is 500
    }


def get_pc_platform_no() -> int:
    # name 	                value
    # ====================  =====
    # console 	            1
    # arcade 	            2
    # platform 	            3
    # operating_system 	    4
    # portable_console 	    5
    # computer 	            6

    return 6


def get_pc_platform_range() -> list[int]:
    return [get_pc_platform_no()]


def get_game_category_no() -> list[int]:
    # name 	                value
    # ====================  =====
    # main_game 	        0
    # dlc_addon 	        1
    # expansion 	        2
    # bundle 	            3
    # standalone_expansion 	4

    # Reference: https://www.igdb.com/contribution_guidelines?page=addinggamedata

    return [0, 3, 4]


def get_dlc_category_no() -> list[int]:
    # name 	                value
    # ====================  =====
    # main_game 	        0
    # dlc_addon 	        1
    # expansion 	        2
    # bundle 	            3
    # standalone_expansion 	4

    # Reference: https://www.igdb.com/contribution_guidelines?page=addinggamedata

    return [1, 2]


def get_released_status_no() -> int:
    # name 	                value
    # ====================  =====
    # released 	            0
    # alpha 	            2
    # beta 	                3
    # early_access 	        4
    # offline 	            5
    # cancelled 	        6

    # Caveat: the release status is often missing from IGDB. Avoid using it for now, or you will get empty responses!

    return 0


def get_steam_service_no() -> int:
    # name 	                value
    # ====================  =====
    # steam 	            1
    # gog 	                5
    # youtube 	            10
    # microsoft 	        11
    # apple 	            13
    # twitch 	            14
    # android 	            15

    return 1


def append_filter_for_igdb_fields(
    igdb_fields: str,
    filter_name: str,
    filter_value: str,
    *,
    use_parenthesis: bool = False,
    comparison_symbol: str = "=",
) -> str:
    where_statement = " ; where "
    conjunction_statement = " & "

    try:
        filter_value_as_int = int(filter_value)
    except TypeError:
        filter_value_as_int = None

    if filter_name.startswith("platform"):
        # The filter name can be singular or plural:
        # - 'platforms' when used for games,
        # - 'platform' when used for release dates.
        use_parenthesis = True

    if filter_name == "category":
        # We will force the use of parenthesis if the filter value contains several game categories,
        # e.g. '1,4' or [1,4] will lead to a filtering with (1,4).

        if filter_value_as_int is None:
            # Assume filter value is either a string or a list of integers.
            num_enforced_game_categories = len(filter_value)
        else:
            # The exception suggests that filter value is actually an integer.
            num_enforced_game_categories = 1

        use_parenthesis = bool(num_enforced_game_categories > 1)

        if num_enforced_game_categories > 1:
            category_separator = ","

            if category_separator in filter_value:
                # Adjust the count of game categories, because we previously included the separators in our count.
                num_enforced_game_categories -= filter_value.count(category_separator)

                # filter_value is already a string, e.g. '1,4' or '(1,4)'. So we do not need to change it, unless it
                # already contains parenthesis.
                if filter_value.startswith("(") and filter_value.endswith(")"):
                    filter_value = filter_value[1:-1]
                    num_enforced_game_categories -= len("()")
            else:
                # Convert filter_value from a list of integers, e.g. [1,4], to a string, e.g. '1,4'.
                filter_value = category_separator.join(
                    str(category_no) for category_no in filter_value
                )

    if use_parenthesis:
        # Use parenthesis, e.g. (6), to look for games released on platform n°6, without discarding multi-platform games
        # Reference: https://medium.com/igdb/its-here-the-new-igdb-api-f6ad745b53fe
        statement_to_append = f"{filter_name} {comparison_symbol} ({filter_value})"
    else:
        statement_to_append = f"{filter_name} {comparison_symbol} {filter_value}"

    if where_statement in igdb_fields:
        igdb_fields += conjunction_statement + statement_to_append
    else:
        igdb_fields += where_statement + statement_to_append

    return igdb_fields


def get_comparison_symbol(year_constraint: str = "equality") -> str:
    if year_constraint == "equality":
        comparison_symbol = "="
    elif year_constraint == "minimum":
        comparison_symbol = ">="
    elif year_constraint == "maximum":
        comparison_symbol = "<="
    else:
        comparison_symbol = "="

    return comparison_symbol


def get_igdb_fields_for_games(
    *,
    must_be_available_on_pc: bool = True,
    must_be_a_game: bool = True,
    enforced_platform: int | None = None,
    enforced_game_category: list[int] | None = None,
    enforced_year: str | None = None,
    year_constraint: str = "equality",
) -> str:
    # Reference: https://api-docs.igdb.com/?kotlin#game

    igdb_fields_for_games = FIELD_SEPARATOR.join(
        [
            "name",
            "slug",
            "platforms",
            "category",
            "release_dates.y",
            "release_dates.platform",
            "release_dates.human",
            "external_games.category",
            "external_games.name",
            "external_games.uid",
            "external_games.url",
            "external_games.year",
            "alternative_names.comment",
            "alternative_names.name",
        ],
    )

    if must_be_available_on_pc or enforced_platform is not None:
        if enforced_platform is None:
            enforced_platform = get_pc_platform_no()

        igdb_fields_for_games = append_filter_for_igdb_fields(
            igdb_fields_for_games,
            "platforms",
            str(enforced_platform),
            use_parenthesis=True,
        )

    if must_be_a_game or enforced_game_category is not None:
        if enforced_game_category is None:
            enforced_game_category = get_game_category_no()

        igdb_fields_for_games = append_filter_for_igdb_fields(
            igdb_fields_for_games,
            "category",
            str(enforced_game_category),
        )

    if enforced_year is not None:
        comparison_symbol = get_comparison_symbol(year_constraint=year_constraint)

        igdb_fields_for_games = append_filter_for_igdb_fields(
            igdb_fields_for_games,
            "release_dates.y",
            str(enforced_year),
            comparison_symbol=comparison_symbol,
        )

    return igdb_fields_for_games


def get_igdb_fields_for_release_dates(
    *,
    must_be_available_on_pc: bool = True,
    enforced_platform: int | None = None,
    enforced_year: str | None = None,
) -> str:
    # Reference: https://api-docs.igdb.com/?kotlin#release-date

    igdb_fields_for_release_dates = FIELD_SEPARATOR.join(
        [
            "game.name",
            "game.slug",
            "game.platforms",
            "game.category",
            "platform",
            "human",
            "y",
        ],
    )

    if must_be_available_on_pc or enforced_platform is not None:
        if enforced_platform is None:
            enforced_platform = get_pc_platform_no()

        igdb_fields_for_release_dates = append_filter_for_igdb_fields(
            igdb_fields_for_release_dates,
            "platform",
            str(enforced_platform),
            use_parenthesis=True,
        )

    if enforced_year is not None:
        igdb_fields_for_release_dates = append_filter_for_igdb_fields(
            igdb_fields_for_release_dates,
            "y",
            str(enforced_year),
        )

    return igdb_fields_for_release_dates


def format_list_of_platforms(
    raw_data_platforms: list[dict[str, int | str]],
    *,
    verbose: bool = True,
) -> dict[int | str, dict[str, int | str | None]]:
    formatted_data_platforms: dict[int | str, dict[str, int | str | None]] = {}

    sorted_data_platforms = sorted(raw_data_platforms, key=operator.itemgetter("id"))

    for e in sorted_data_platforms:
        element_id = e["id"]

        formatted_data_platforms[element_id] = {}
        formatted_data_platforms[element_id]["slug"] = e["slug"]
        formatted_data_platforms[element_id]["slug"] = e["name"]

        try:
            formatted_data_platforms[element_id]["category"] = e["category"]
        except KeyError:
            formatted_data_platforms[element_id]["category"] = None

    if verbose:
        for element_id in formatted_data_platforms:
            category = formatted_data_platforms[element_id]["category"]

            if category == get_pc_platform_no():
                slug = formatted_data_platforms[element_id]["slug"]

                print(
                    f"Category: {category} ; ID: {element_id} ; Slug: {slug}",
                )

    return formatted_data_platforms


def format_release_dates_for_manual_display(element: dict) -> str | None:
    if "release_dates" in element:
        release_years = {
            str(date["y"]) for date in element["release_dates"] if "y" in date
        }
    else:
        release_years = None

    if release_years is not None:
        release_years_as_str = FIELD_SEPARATOR.join(sorted(release_years))
    else:
        release_years_as_str = None

    return release_years_as_str
