# MetaCouncil's PC Games of the Year (GOTY) Awards

 [![Build status][build image]][build] [![Updates][dependency image]][pyup] [![Python 3][python3 image]][pyup] [![Code coverage][codecov image]][codecov]

![MetaCouncil GOTY banner](https://raw.githubusercontent.com/wiki/woctezuma/metacouncil-goty/metacouncil-goty-banner.png)

## Introduction

These awards focus on PC games which we deem GOTY worthy, as well as the best Early Access game and the best DLC.

## Method

Ballots are cast on [MetaCouncil](https://metacouncil.com/threads/metacouncils-pc-games-of-the-year-awards-2018.473/) and processed with [our implementation](https://github.com/woctezuma/steam-era-goty) of Schulze method.

## Usage ##

- To compute the GOTY ranking, run:

```bash
python schulze_goty.py
```

- To compute the rankings for the optional categories (Early Access, DLC, etc.), run:

```bash
python optional_categories.py
```

- If needed, edit hard-coded values, then run the two aforementioned scripts again:
    * `extend_steamspy.py` (manual addition of a few appIDs to SteamSpy's database)
    * `hard_coded_matches.py` (manual match of a few game names with appIDs)
    * `disqualify_vote.py` (manual disqualification of a few appIDs)

## Results

Not available before January 20, 2019.

## References

* [Ranked-choice voting](https://en.wikipedia.org/wiki/Ranked_voting)
* [Schulze method](https://en.wikipedia.org/wiki/Schulze_method)

  [build]: https://travis-ci.org/woctezuma/metacouncil-goty
  [build image]: https://travis-ci.org/woctezuma/metacouncil-goty.svg?branch=master

  [pyup]: https://pyup.io/repos/github/woctezuma/metacouncil-goty/
  [dependency image]: https://pyup.io/repos/github/woctezuma/metacouncil-goty/shield.svg
  [python3 image]: https://pyup.io/repos/github/woctezuma/metacouncil-goty/python-3-shield.svg

  [codecov]: https://codecov.io/gh/woctezuma/metacouncil-goty
  [codecov image]: https://codecov.io/gh/woctezuma/metacouncil-goty/branch/master/graph/badge.svg
