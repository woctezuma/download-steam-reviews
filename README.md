# Download Steam Reviews [![Build status][Build image]][Build]

  [Build]: https://travis-ci.org/woctezuma/download-steam-reviews
  [Build image]: https://travis-ci.org/woctezuma/download-steam-reviews.svg?branch=master

This repository contains Python code to download every Steam review for the games of your choice.

## Requirements

- Install the latest version of [Python 3.X](https://www.python.org/downloads/).

- Install the required packages:

```
pip install -r requirements.txt
```

## Usage

- For every game of interest, write down its appID in a text file named `idlist.txt`. There should be an appID per line.

If you do not know the appID of a game, look for it on the Steam store. The appID is a unique number in the URL.
For instance, for [SpyParty](https://store.steampowered.com/app/329070/SpyParty/), the appID is 329070.

![appID for SpyParty](https://i.imgur.com/LNlyUFW.png)

- Call the Python script. The Steam API is rate-limited so you should be able to download about 10 reviews per second.

```
python download_reviews.py
```

## References

- [my original Steam-Reviews repository](https://github.com/woctezuma/steam-reviews)

- [a snapshot of Steam-Reviews data for hidden gems](https://github.com/woctezuma/steam-reviews-data)
