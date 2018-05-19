# Download Steam Reviews

[![PyPI status][PyPI image]][PyPI] [![Build status][Build image]][Build] [![Updates][Dependency image]][PyUp] [![Python 3][Python3 image]][PyUp] [![Code coverage][Coveralls image]][Coveralls] [![Code coverage BIS][Codecov image]][Codecov]

  [PyPI]: https://pypi.python.org/pypi/steamreviews
  [PyPI image]: https://badge.fury.io/py/steamreviews.svg

  [Build]: https://travis-ci.org/woctezuma/download-steam-reviews
  [Build image]: https://travis-ci.org/woctezuma/download-steam-reviews.svg?branch=master

  [PyUp]: https://pyup.io/repos/github/woctezuma/download-steam-reviews/
  [Dependency image]: https://pyup.io/repos/github/woctezuma/download-steam-reviews/shield.svg
  [Python3 image]: https://pyup.io/repos/github/woctezuma/download-steam-reviews/python-3-shield.svg

  [Coveralls]: https://coveralls.io/github/woctezuma/download-steam-reviews?branch=master
  [Coveralls image]: https://coveralls.io/repos/github/woctezuma/download-steam-reviews/badge.svg?branch=master

  [Codecov]: https://codecov.io/gh/woctezuma/download-steam-reviews
  [Codecov image]: https://codecov.io/gh/woctezuma/download-steam-reviews/branch/master/graph/badge.svg

This repository contains Python code to download every Steam review for the games of your choice.

## Installation

The code is packaged for [PyPI](https://pypi.org/project/steamreviews/), so that the installation consists in running:

```bash
pip install steamreviews
```

## Usage

The Steam API is rate-limited so you should be able to download about 10 reviews per second.

### Process a batch of appIDs, written down in a text file

- For every game of interest, write down its appID in a text file named `idlist.txt`. There should be an appID per line.

If you do not know the appID of a game, look for it on the Steam store. The appID is a unique number in the URL.
For instance, for [SpyParty](https://store.steampowered.com/app/329070/SpyParty/), the appID is 329070.

![appID for SpyParty](https://i.imgur.com/LNlyUFW.png)

- Then proceed as follows: 

```python
import steamreviews

steamreviews.download_reviews_for_app_id_batch()
```

### Process a batch of appIDs

```python
import steamreviews

app_ids = [329070, 573170]
steamreviews.download_reviews_for_app_id_batch(app_ids)
```

### Download reviews for one appID

```python
import steamreviews

app_id = 573170
review_dict, query_count = steamreviews.download_reviews_for_app_id(app_id)
```

### Load reviews for one appID

```python
import steamreviews

app_id = 329070
review_dict = steamreviews.load_review_dict(app_id)
```

## References

- [my original Steam-Reviews repository](https://github.com/woctezuma/steam-reviews)

- [a snapshot of Steam-Reviews data for hidden gems](https://github.com/woctezuma/steam-reviews-data)
