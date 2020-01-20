# MetaCouncil's PC Games of the Year (GOTY) Awards

[![Build status][build-image]][build]
[![Updates][dependency-image]][pyup]
[![Python 3][python3-image]][pyup]
[![Code coverage][codecov-image]][codecov]
[![Code Quality][codacy-image]][codacy]

![MetaCouncil GOTY banner](https://raw.githubusercontent.com/wiki/woctezuma/metacouncil-goty/metacouncil-goty-banner.png)

## Introduction

These awards focus on PC games which we deem GOTY worthy, as well as the best DLC / Ongoing game, the best Early Access
game, and the best VR game. Exceptionally, for 2019, there is also an award for the Game of the Decade (GOTD).

## Method

Ballots are cast on MetaCouncil ([2018](https://metacouncil.com/threads/metacouncils-pc-games-of-the-year-awards-2018.473/), [2019](https://metacouncil.com/threads/metacouncils-pc-games-of-the-year-awards-2019.1729/)) and processed with [our implementation](https://github.com/woctezuma/steam-era-goty) of Schulze method.

## Usage

-   To compute the GOTY ranking, run:

```bash
python schulze_goty.py
```

-   To compute the GOTD ranking, run:

```bash
python schulze_gotd.py
```

-   To compute the rankings for the optional categories (DLC / Ongoing, Early Access, VR, etc.), run:

```bash
python optional_categories.py
```

### With SteamSpy

-   If needed, edit hard-coded values below, then run the three aforementioned scripts again:
    -   `extend_steamspy.py` (manual addition of a few appIDs to SteamSpy's database)
    -   `hard_coded_matches.py` (manual match of a few game names with appIDs)
    -   `disqualify_vote.py` (manual disqualification of a few appIDs)
    -   `whitelist_vote.py` (manual white-listing of a few appIDs)

### With IGDB

Let us assume the target release year is `2018` for this section, i.e. we focus on games released during the year 2018.

-   If needed, edit hard-coded values below, then run the three aforementioned scripts again:
    -   `fixes_to_igdb_local_database_2018.json` (manual addition of a few appIDs to IGDB's database)
    -   `fixes_to_igdb_match_database_2018.json` (manual match of a few game names with appIDs)
    -   `disqualified_igdb_ids_2018.json` (manual disqualification of a few appIDs)
    -   `whitelisted_igdb_ids_2018.json` (manual white-listing of a few appIDs)

The fixes to the local database allow to extend the IGDB database, in case a game is missing from IGDB, e.g. Steam games in the adult section of the store.

The fixes to the match database allow to manually enforce matches between input game names and IGDB ids, in order to
edit results from the automatic matching method:
-   fix empty matches: no match could be found by IGDB,
-   fix actual mismatches: the match is factually wrong,
-   merge matches for different versions (vanilla, definitive, etc.) of the same game, e.g. Darks Souls 1.
Without merging versions of the same game, votes for this same game would be spread to the detriment of the game rank.

The black-list allows to disqualify some games for manually specified reasons.

The white-list allows to prevent the automatic disqualification of some games due to their reported release date differing from the target release year.

## Results

Results are displayed:
-   on the Wiki ([GotY 2018](https://github.com/woctezuma/metacouncil-goty/wiki/Games_of_the_Year_2018.md), [GotY 2019]((https://github.com/woctezuma/metacouncil-goty/wiki/Games_of_the_Year_2019.md)), [GotD 201X]((https://github.com/woctezuma/metacouncil-goty/wiki/Games_of_the_Decade_201X.md))),
-   on MetaCouncil ([GotY 2018](https://metacouncil.com/threads/metacouncils-pc-games-of-the-year-awards-2018-results.525/), [GotY 2019](https://metacouncil.com/threads/metacouncils-pc-games-of-the-year-awards-2019-results.1766/), [GotD 201X](https://metacouncil.com/threads/metacouncils-pc-games-of-the-decade-awards-2010-2019-results.1771/)).

## Alternative methods for game name matching

### SteamSpy and Levenshtein distance

The first implementation relied on [SteamSpy](https://github.com/woctezuma/steamspypi)'s database, and matched game names with [Levenshtein distance](https://github.com/ztane/python-Levenshtein).

In practice, Levenshtein distance is effective at fixing typos, but cannot work for cases where the input is short and the actual game title is long, e.g. for [Resident Evil 7](https://store.steampowered.com/app/418370/):

> RESIDENT EVIL 7 biohazard / BIOHAZARD 7 resident evil

### SteamSpy and difflib

If we use SteamSpy, we have the choice between Levenshtein distance and difflib for name matching.

[Difflib](https://docs.python.org/3/library/difflib.html) allows to match game names with the longest contiguous matching subsequence.
However, difflib is notably slower than Levenshtein distance.

### IGDB

As of January 2020, [IGDB](https://www.igdb.com/api)'s database, which extends beyond Steam, can be used in place of SteamSpy with the `use_igdb` flag.

If IGDB is to be used, then you need to have a user secret key to be authorized.
It is free, but you need to register on IGDB.
 
The API is queried whenever it is necessary, and the responses are locally saved to avoid unnecessary requests.
As a free user, there is a monthly allowance of 50k requests per month.

Name matching is delegated to IGDB because the whole IGDB database is not locally available.
In theory, this could lead to worse results if there are typos in the input names.
However:
-   IGDB's database is larger than SteamSpy's, so name matching could be better, thanks to the availability of alternative names.
-   IGDB also offers access to information about DLC, which could be useful for at least one of the optional categories,
-   typos are not a big issue: they are rare in the input game names for the GotY votes.

### Benchmark

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
