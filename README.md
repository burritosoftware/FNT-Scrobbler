# Friday Night Tracks Scrobbler
![Icons](https://skillicons.dev/icons?i=py)

[![wakatime](https://wakatime.com/badge/github/burritosoftware/FNT-Scrobbler.svg)](https://wakatime.com/badge/github/burritosoftware/FNT-Scrobbler) [![Last updated](https://img.shields.io/github/last-commit/burritosoftware/FNT-Scrobbler/master?logo=github&label=last%20updated)](https://github.com/burritosoftware/FNT-Scrobbler/commits/master)

A scrobbler for Last.fm designed for [Friday Night Tracks](https://fridaynighttracks.com), that includes quality-of-life features for the monthly live radio show.  
This is a drop-in replacement for my now deprecated [Icecast Scrobbler](https://github.com/burritosoftware/Icecast-Scrobbler) (you can just copy the .env file to this, install dependencies and run! Although you should probably take a look at [`.env-example`](.env-example) since there's new options now).

## Get It Running
1. Make sure you have Python installed.
2. Install/upgrade dependencies:
```
pip install -U -r requirements.txt
```
3. Duplicate `.env-example` to `.env`, and add a Last.fm API key and secret from https://www.last.fm/api/account/create.
```
cp .env-example .env
nano .env
```
4. Start the scrobbler. On first run, it'll ask you to authorize in a web browser. Then it'll start sending what's currently playing and scrobble songs once they end.
```
python3 scrobble.py
```

## Contributing
All contributions welcome! And if you haven't, you should catch Friday Night Tracks live (check the website at https://fridaynighttracks.com for when it's live next :3)