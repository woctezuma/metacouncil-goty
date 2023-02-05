from whitelist_vote_igdb import load_whitelisted_igdb_ids


def get_hard_coded_whitelisted_app_ids():
    whitelisted_app_id_dict = {
        "0": {
            "reason": "[placeholder]",
        },
    }

    return whitelisted_app_id_dict


def load_whitelisted_ids(release_year=None, use_igdb=False):
    if use_igdb:
        whitelisted_app_id_dict = load_whitelisted_igdb_ids(release_year=release_year)
    else:
        whitelisted_app_id_dict = get_hard_coded_whitelisted_app_ids()

    return whitelisted_app_id_dict


def main():
    release_year = '2018'
    use_igdb = True

    whitelisted_app_id_dict = load_whitelisted_ids(
        release_year=release_year,
        use_igdb=use_igdb,
    )

    return True


if __name__ == '__main__':
    main()
