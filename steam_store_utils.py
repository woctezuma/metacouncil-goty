def get_link_to_store(app_id, remove_dummy_app_id=True):
    steam_store_base_url = 'https://store.steampowered.com/app/'

    if int(app_id) > 0:
        link_to_store = '[URL=' + steam_store_base_url + app_id + '/]' + app_id + '[/URL]'
    else:
        if remove_dummy_app_id:
            link_to_store = 'n/a'
        else:
            link_to_store = app_id
    return link_to_store
