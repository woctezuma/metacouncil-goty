import steampi.api


def get_link_to_store(app_id: str, *, hide_dummy_app_id: bool = True) -> str:
    steam_store_base_url = "https://store.steampowered.com/app/"

    if int(app_id) > 0:
        link_to_store = (
            "[URL=" + steam_store_base_url + app_id + "/]" + app_id + "[/URL]"
        )
    elif hide_dummy_app_id:
        link_to_store = "n/a"
    else:
        link_to_store = app_id
    return link_to_store


def get_early_access_status(app_id: str) -> bool:
    if int(app_id) > 0:
        app_details, _, _ = steampi.api.load_app_details(app_id)
    else:
        app_details = {}

    try:
        is_early_access = any(
            genre["description"] == "Early Access" for genre in app_details["genres"]
        )
    except KeyError:
        is_early_access = False

    return is_early_access
