from load_ballots import load_ballots
from my_types import Ballots


def generate_thank_you_message(ballots: Ballots, *, verbose: bool = True) -> str:
    voter_names = list(ballots.keys())
    voters = ", ".join(f"@{name}" for name in sorted(voter_names))
    sentence = f"A big thanks to the following who voted and just for being awesome people on MetaCouncil: {voters}."

    if verbose:
        print(sentence)

    return sentence


if __name__ == "__main__":
    from load_ballots import get_ballot_file_name

    ballot_year = "2024"
    input_filename = get_ballot_file_name(ballot_year)
    ballots = load_ballots(input_filename)
    sentence = generate_thank_you_message(ballots)
