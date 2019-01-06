def get_hard_coded_disqualified_app_ids():
    disqualified_app_id_dict = {

        "-1": {
            "reason": "Marvel's Spider-Man is not available on PC: it is exclusive to PS4.",
        },

    }

    return disqualified_app_id_dict


def filter_out_votes_for_hard_coded_reasons(standardized_ballots):
    # Objective: remove appID which gathered votes but were manually marked for disqualification

    print()

    removed_app_ids = []

    disqualified_app_id_dict = get_hard_coded_disqualified_app_ids()

    for voter in standardized_ballots.keys():
        current_ballots = standardized_ballots[voter]['ballots']

        current_ballots_list = []
        for position in sorted(current_ballots.keys()):
            app_id = current_ballots[position]
            if app_id is not None:
                if app_id not in disqualified_app_id_dict:
                    current_ballots_list.append(app_id)
                else:
                    if app_id not in removed_app_ids:
                        print('AppID ' + app_id + ' removed because ' + disqualified_app_id_dict[app_id]["reason"])
                        removed_app_ids.append(app_id)

        for i in range(len(current_ballots_list)):
            position = i + 1
            standardized_ballots[voter]['ballots'][position] = current_ballots_list[i]
        for i in range(len(current_ballots_list), len(current_ballots.keys())):
            position = i + 1
            standardized_ballots[voter]['ballots'][position] = None

    return standardized_ballots


if __name__ == '__main__':
    disqualified_app_id_dict = get_hard_coded_disqualified_app_ids()
