# Download Steam Reviews

[![PyPI status][pypi-image]][pypi]
[![Build status][build-image]][build]
[![Updates][dependency-image]][pyup]
[![Python 3][python3-image]][pyup]
[![Code coverage][codecov-image]][codecov]
[![Code Quality][codacy-image]][codacy]

This repository contains Python code to download every Steam review for the games of your choice.

## Installation

The code is packaged for [PyPI](https://pypi.org/project/steamreviews/), so that the installation consists in running:

```bash
pip install steamreviews
```

## Usage

The Steam API is rate-limited so you should be able to download about 10 reviews per second.

NB: If you do not know the appID of a game, look for it on the Steam store. The appID is a unique number in the URL.

For instance, for [SpyParty](https://store.steampowered.com/app/329070/SpyParty/), the appID is 329070.

![appID for SpyParty](https://i.imgur.com/LNlyUFW.png)

### Process a batch of appIDs

```python
import steamreviews

app_ids = [329070, 573170]
steamreviews.download_reviews_for_app_id_batch(app_ids)
```

### Process a batch of appIDs, written down in a text file

-   For every game of interest, write down its appID in a text file named `idlist.txt`. There should be an appID per line.
-   Then proceed as follows: 

```python
import steamreviews

steamreviews.download_reviews_for_app_id_batch()
```

### Load reviews for one appID

```python
import steamreviews

app_id = 329070
review_dict = steamreviews.load_review_dict(app_id)
```

### Download reviews for one appID

```python
import steamreviews

app_id = 573170
review_dict, query_count = steamreviews.download_reviews_for_app_id(app_id)
```

### Download reviews for one appID, with specific request parameters (language, sentiment, store)

**Caveat**: the following parameters do not appear in the output filename,
so make sure that you start the download from scratch (instead of updating existing JSON review data)
if you ever decide to **change** them, e.g the value of the `review_type` (set to `all`, `positive` or `negative`).

```python
import steamreviews

request_params = dict()
# Reference: https://partner.steamgames.com/doc/store/localization#supported_languages
request_params['language'] = 'english'
# Reference: https://partner.steamgames.com/doc/store/getreviews
request_params['review_type'] = 'positive'
request_params['purchase_type'] = 'steam'

app_id = 573170
review_dict, query_count = steamreviews.download_reviews_for_app_id(app_id,
                                                                    chosen_request_params=request_params)
```

### Download a few of the most helpful reviews for one appID, which were created in a time-window

**Caveat**: with `filter` set to `all`, you will only be able to download **a few** reviews within the specified time-window.

```python
import steamreviews

request_params = dict()
# Reference: https://partner.steamgames.com/doc/store/getreviews
request_params['filter'] = 'all'  # reviews are sorted by helpfulness instead of chronology
request_params['day_range'] = '28'  # focus on reviews which were published during the past four weeks

app_id = 573170
review_dict, query_count = steamreviews.download_reviews_for_app_id(app_id,
                                                                    chosen_request_params=request_params)
```

### Download reviews for one appID, which were created within a specific time-window

```python
import steamreviews

request_params = dict()
request_params['filter'] = 'recent'
request_params['day_range'] = '28'

app_id = 573170
review_dict, query_count = steamreviews.download_reviews_for_app_id(app_id,
                                                                    chosen_request_params=request_params)
```

### Download reviews for one appID, which were updated within a specific time-window

```python
import steamreviews

request_params = dict()
request_params['filter'] = 'updated'
request_params['day_range'] = '28'

app_id = 573170
review_dict, query_count = steamreviews.download_reviews_for_app_id(app_id,
                                                                    chosen_request_params=request_params)
```

## References

- [my original Steam-Reviews repository](https://github.com/woctezuma/steam-reviews)

- [a snapshot of Steam-Reviews data for hidden gems](https://github.com/woctezuma/steam-reviews-data)

<!-- Definitions for badges -->

[pypi]: <https://pypi.python.org/pypi/steamreviews>
[pypi-image]: <https://badge.fury.io/py/steamreviews.svg>

[build]: <https://github.com/woctezuma/download-steam-reviews/actions>
[build-image]: <https://github.com/woctezuma/download-steam-reviews/workflows/Python package/badge.svg?branch=master>
[publish-image]: <https://github.com/woctezuma/download-steam-reviews/workflows/Upload Python Package/badge.svg?branch=master>

[pyup]: <https://pyup.io/repos/github/woctezuma/download-steam-reviews/>
[dependency-image]: <https://pyup.io/repos/github/woctezuma/download-steam-reviews/shield.svg>
[python3-image]: <https://pyup.io/repos/github/woctezuma/download-steam-reviews/python-3-shield.svg>

[codecov]: <https://codecov.io/gh/woctezuma/download-steam-reviews>
[codecov-image]: <https://codecov.io/gh/woctezuma/download-steam-reviews/branch/master/graph/badge.svg>

[codacy]: <https://www.codacy.com/app/woctezuma/gamedatacrunch>
[codacy-image]: <https://api.codacy.com/project/badge/Grade/253164b80b704f00a1fd2b083f1348bb>
