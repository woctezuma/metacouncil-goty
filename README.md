# MetaCouncil's PC Games of the Year (GOTY) Awards

[![Build status][build-image]][build]
[![Updates][dependency-image]][pyup]
[![Python 3][python3-image]][pyup]
[![Code coverage][codecov-image]][codecov]
[![Code Quality][codacy-image]][codacy]

![MetaCouncil GOTY banner](https://raw.githubusercontent.com/wiki/woctezuma/metacouncil-goty/metacouncil-goty-banner.png)

## Introduction

These awards focus on PC games which we deem GOTY worthy, as well as the best Early Access game and the best DLC.

## Method

Ballots are cast on [MetaCouncil](https://metacouncil.com/threads/metacouncils-pc-games-of-the-year-awards-2018.473/) and processed with [our implementation](https://github.com/woctezuma/steam-era-goty) of Schulze method.

## Usage

-   To compute the GOTY ranking, run:

```bash
python schulze_goty.py
```

-   To compute the rankings for the optional categories (Early Access, DLC, etc.), run:

```bash
python optional_categories.py
```

-   If needed, edit hard-coded values, then run the two aforementioned scripts again:
    -   `extend_steamspy.py` (manual addition of a few appIDs to SteamSpy's database)
    -   `hard_coded_matches.py` (manual match of a few game names with appIDs)
    -   `disqualify_vote.py` (manual disqualification of a few appIDs)
    -   `whitelist_vote.py` (manual white-listing of a few appIDs)

## Results

Results are displayed:
-   on the [Wiki](https://github.com/woctezuma/metacouncil-goty/wiki),
-   on [MetaCouncil](https://metacouncil.com/threads/metacouncils-pc-games-of-the-year-awards-2018-results.525/).

## Perspectives

The current implementation relies on [SteamSpy](https://github.com/woctezuma/steamspypi)'s database, and matches game names with [Levenshtein distance](https://github.com/ztane/python-Levenshtein).

**Edit:** As of January 16, 2020, IGDB can be used in place of SteamSpy with the `use_igdb` flag.

Work-in-progress includes:
-   matching game names with the longest contiguous matching subsequence, as offered by [difflib](https://docs.python.org/3/library/difflib.html),
-   relying on [IGDB](https://www.igdb.com/api)'s database, which extends beyond Steam.

If we use SteamSpy, we have the choice between Levenshtein distance and difflib for name matching.
Difflib is notably slower than Levenshtein distance. 
In practice, Levenshtein distance is effective at fixing typos, but cannot work for cases where the input is short and the actual game title is long, e.g. for [Resident Evil 7](https://store.steampowered.com/app/418370/):

> RESIDENT EVIL 7 biohazard / BIOHAZARD 7 resident evil

If IGDB is used, then the API is queried, but the whole database is not locally available, so name matching is delegated to IGDB.
In theory, this could lead to worse results if there are typos in the input names.
However:
-   IGDB's database is larger than SteamSpy's, so name matching could be better, thanks to the availability of alternative names.
-   typos are not a big issue: they are rare in the input game names for the GotY votes.

A quantitative comparison is shown [in a benchmark](https://github.com/woctezuma/metacouncil-goty/wiki/Benchmark) on the Wiki.

The mismatches observed with the 2018 dataset are counted, and the best performing methods are:
1.  IGDB database with a constraint w.r.t. the release year: **8 mismatches**,
2.  IGDB database: 11 mismatches,
3.  vanilla SteamSpy database with difflib matching and a constraint w.r.t. the release yar: 12 mismatches,
4.  vanilla SteamSpy database with difflib matching: 14 mismatches,
5.  vanilla SteamSpy database with Levenshtein distance: 18 mismatches (same performance with and without constraint). 

In summary, in order to minimize the number of manual edits necessary to extend the database and to fix name mismatches,
the most promising method involves using the IGSB database with a constraint w.r.t. the release year.

## References

-   [Ranked-choice voting](https://en.wikipedia.org/wiki/Ranked_voting)
-   [Schulze method](https://en.wikipedia.org/wiki/Schulze_method)
-   [SteamSpy API](https://github.com/woctezuma/steamspypi)
-   [IGDB API](https://www.igdb.com/api)
-   [Levenshtein distance](https://github.com/ztane/python-Levenshtein)
-   [difflib](https://docs.python.org/3/library/difflib.html): the longest contiguous matching subsequence

<!-- Definitions -->

[build]: <https://travis-ci.org/woctezuma/metacouncil-goty>
[build-image]: <https://travis-ci.org/woctezuma/metacouncil-goty.svg?branch=master>

[pyup]: <https://pyup.io/repos/github/woctezuma/metacouncil-goty/>
[dependency-image]: <https://pyup.io/repos/github/woctezuma/metacouncil-goty/shield.svg>
[python3-image]: <https://pyup.io/repos/github/woctezuma/metacouncil-goty/python-3-shield.svg>

[codecov]: <https://codecov.io/gh/woctezuma/metacouncil-goty>
[codecov-image]: <https://codecov.io/gh/woctezuma/metacouncil-goty/branch/master/graph/badge.svg>

[codacy]: <https://www.codacy.com/app/woctezuma/metacouncil-goty>
[codacy-image]: <https://api.codacy.com/project/badge/Grade/d072d73231a24a5b91bc72c59737ca7d> 
