from disqualify_vote_igdb import load_disqualified_igdb_ids
from my_types import HardCodedIDs


def get_hard_coded_disqualified_app_ids() -> HardCodedIDs:
    return {
        "-1": {
            "reason": "Marvel's Spider-Man is not available on PC: it is exclusive to PS4.",
        },
    }


def get_hard_coded_noisy_votes() -> list[str]:
    return [
        "-",
        "None played",
        "n/a",
        "N/A",
        "None",
    ]


def is_a_noisy_vote(game_name: str) -> bool:
    noisy_votes = get_hard_coded_noisy_votes()

    return bool(not game_name or (game_name in noisy_votes))


def filter_out_votes_for_hard_coded_reasons(
    standardized_ballots: dict,
    release_year: str | None = None,
    *,
    use_igdb: bool = False,
) -> dict:
    # Objective: remove appID which gathered votes but were manually marked for disqualification

    print()

    removed_app_ids = []

    if use_igdb:
        disqualified_app_id_dict = load_disqualified_igdb_ids(release_year=release_year)
    else:
        disqualified_app_id_dict = get_hard_coded_disqualified_app_ids()

    for voter in standardized_ballots:
        current_ballots = standardized_ballots[voter]["ballots"]

        current_ballots_list = []
        for position in sorted(current_ballots.keys()):
            app_id = current_ballots[position]
            if app_id is not None:
                if app_id not in disqualified_app_id_dict:
                    current_ballots_list.append(app_id)
                elif app_id not in removed_app_ids:
                    print(
                        "AppID "
                        + app_id
                        + " removed because "
                        + disqualified_app_id_dict[app_id]["reason"],
                    )
                    removed_app_ids.append(app_id)

        for i, current_ballot in enumerate(current_ballots_list):
            position = i + 1
            standardized_ballots[voter]["ballots"][position] = current_ballot
        for i in range(len(current_ballots_list), len(current_ballots.keys())):
            position = i + 1
            standardized_ballots[voter]["ballots"][position] = None

    return standardized_ballots


if __name__ == "__main__":
    disqualified_app_id_dict = get_hard_coded_disqualified_app_ids()
