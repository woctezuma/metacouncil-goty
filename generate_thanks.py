from load_ballots import load_ballots


def generate_thank_you_message(ballots, verbose=True):
    voter_names = list(ballots.keys())
    voters = ", ".join(f"@{name}" for name in sorted(voter_names))
    sentence = f"A big thanks to the following who voted and just for being awesome people on MetaCouncil: {voters}."

    if verbose:
        print(sentence)

    return sentence


if __name__ == "__main__":
    ballot_year = "2020"
    input_filename = "pc_gaming_metacouncil_goty_awards_" + ballot_year + ".csv"

    ballots = load_ballots(input_filename, fake_author_name=False)
    sentence = generate_thank_you_message(ballots)
