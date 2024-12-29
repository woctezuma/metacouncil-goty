from whitelist_vote_igdb import load_whitelisted_igdb_ids


def get_hard_coded_whitelisted_app_ids() -> dict[str, dict[str, str]]:
    return {
        "0": {
            "reason": "[placeholder]",
        },
    }


def load_whitelisted_ids(
    release_year: int | str | None = None,
    *,
    use_igdb: bool = False,
) -> dict:
    if use_igdb:
        whitelisted_app_id_dict = load_whitelisted_igdb_ids(release_year=release_year)
    else:
        whitelisted_app_id_dict = get_hard_coded_whitelisted_app_ids()

    return whitelisted_app_id_dict


def main() -> bool:
    release_year = "2018"
    use_igdb = True

    load_whitelisted_ids(
        release_year=release_year,
        use_igdb=use_igdb,
    )

    return True


if __name__ == "__main__":
    main()
