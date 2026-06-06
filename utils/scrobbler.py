from utils.session import getLastFMNetwork
import re
import time
import logging
from os import getenv
from dotenv import load_dotenv
load_dotenv()
from pylast import WSError

logger = logging.getLogger(__name__)

lastfm = getLastFMNetwork()

def _getTagPattern():
    fnt_regex = (
      r"\(Original.*?Mix\)"      # (Original … Mix)
      r"|\(Extended.*?Mix\)"     # (Extended … Mix)
      r"|\[Explicit\]"           # [Explicit]
      r"|\[Clean\]"              # [Clean]
      r"|\[FNT.*?Edit\]"         # [FNT … Edit]
      r"|\[FNT.*?Remaster\]"     # [FNT … Remaster]
      r"|\(Paradox.*?Edit\)"     # (Paradox … Edit)
    )
    pattern = getenv("TAG_REGEX") or fnt_regex
    return re.compile(pattern, re.IGNORECASE)

def parseTrack(data):
    artist, title = data.split(' — ', 1)
    pattern = _getTagPattern()

    logger.debug(f"[scrobbler] Original title: {title}")
    title = re.sub(pattern, "", title).strip()
    logger.debug(f"[scrobbler] Stripped title: {title}")

    track = lastfm.get_track(artist, title)
    track_in_lastfm = True

    try:
      album = track.get_album()
      album_title = album.get_name(True) if album else None
    except WSError:
      track_in_lastfm = False
      album_title = None

    return artist, title, album_title, track, track_in_lastfm

def sendNowPlaying(data):
    artist, title, album_title, _, _ = parseTrack(data)
    lastfm.update_now_playing(artist=artist, title=title, album=album_title)
    logger.info(f"[scrobbler] NOW PLAYING: {artist} - {title}")

def scheduleScrobble(data):
    """
    Schedule a scrobble based on the provided data.
    """
    artist, title, album_title, track, track_in_lastfm = parseTrack(data)

    track_length = 0

    if track_in_lastfm:
      track_length = track.get_duration()
      track_length = track_length / 1000
      if track_length == 0.0:
        track_length = 240
    else:
      track_length = 240 # 2 mins = 240/2

    if track_length > 30:
      delay = min(track_length / 2, 240)  # Half the duration or 4 minutes
      logger.info(f"[scrobbler] SCHEDULING: {artist} - {title} in {delay} seconds")
      time.sleep(delay)
      lastfm.scrobble(artist=artist, title=title, timestamp=int(time.time()), album=album_title)
      logger.info(f"[scrobbler] SCROBBLED: {artist} - {title}")
