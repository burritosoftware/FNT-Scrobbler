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

def scheduleScrobble(data):
    """
    Schedule a scrobble based on the provided data.
    """
    # Split the data into artist and title
    artist, title = data.split(' — ', 1)

    # Compile our tag regex for filtering
    fnt_regex = (
      r"\(Original Mix\)"        # (Original Mix)
      r"|\(Extended Mix\)"       # (Extended Mix)
      r"|\[Explicit\]"           # [Explicit]
      r"|\[FNT.*?Edit\]"         # [FNT … Edit]
      r"|\[FNT.*?Remaster\]"     # [FNT … Remaster]
      r"|\(Paradox.*?Edit\)"     # (Paradox … Edit)
    )
    if (getenv("TAG_REGEX")):
        pattern = getenv("TAG_REGEX")
    else:
        pattern = fnt_regex
    pattern = re.compile(pattern, re.IGNORECASE)

    # Remove matching tags
    logger.debug(f"[scrobbler] Original title: {title}")
    title = re.sub(pattern, "", title).strip()
    logger.debug(f"[scrobbler] Stripped title: {title}")

    # Get the track from Last.fm
    track = lastfm.get_track(artist, title)
    track_in_lastfm = True

    # Try to get the album: if fails, the track isn't on Last.fm
    try:
      album = track.get_album()
      album_title = album.get_name(True) if album else None
    except WSError:
      track_in_lastfm = False
      album_title = None

    # Update the now playing status (done as soon as the song starts playing)
    lastfm.update_now_playing(artist=artist, title=title, album=album_title)

    # Then we should lookup the song length, and follow the Last.fm scrobble conditions
    # We should schedule a scrobble only when the following conditions are met:
    # 1. The track must be longer than 30 seconds
    # 2. *And* the track has been played for at least half its duration, or for 4 minutes (whichever occurs earlier)
    # As soon as these conditions are met, the scrobble should fire. If 1 is good, and we calculate the shorter time for 2,
    # then schedule the scrobble for the number 2 time

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