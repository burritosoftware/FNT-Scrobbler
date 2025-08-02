from utils.session import getLastFMNetwork
import re
import time
import logging

logger = logging.getLogger(__name__)

lastfm = getLastFMNetwork()

def scheduleScrobble(data):
    """
    Schedule a scrobble based on the provided data.
    """
    # Split artist and song title by dash
    # E.g. Gloria Tells — Heartbreaker (Instrumental Version)

    # Split the data into artist and title
    artist, title = data.split(' — ', 1)

    # Strip data using our tag regex
    fnt_regex = r"\(Original Mix\)|\(Extended Mix\)|\[Explicit\]|\[FNT.*?Edit\]"
    pattern = fnt_regex
    pattern = re.compile(pattern, re.IGNORECASE)

    # Remove matching substrings
    logger.debug(f"Original title: {title}")
    title = re.sub(pattern, "", title).strip()
    logger.debug(f"Stripped title: {title}")

    # First try to obtain an album so we can scrobble that
    album = lastfm.get_album(artist, title)
    album_title = album.get_name() if album else None

    # Then we can update the now playing status,
    lastfm.update_now_playing(artist=artist, title=title, album=album_title)

    # Then we should lookup the song length, and follow the scrobble conditions
    # We should schedule a scrobble with asyncio by adding a task to scrobble,
    # only when the following conditions are met:
    # 1. The track must be longer than 30 seconds
    # 2. *And* the track has been played for at least half its duration, or for 4 minutes (whichever occurs earlier)
    # As soon as these conditions are met, the scrobble should fire. If 1 is good, and we calculate the shorter time for 2,
    # then schedule the scrobble for the number 2 time with asyncio
    
    # Lookup the track
    track = lastfm.get_track(artist, title)

    if track:
        track_length = track.get_duration()
        # Must convert milliseconds to seconds
        track_length = track_length / 1000
        if track_length == 0.0:
           # The track is 0.0 likely because it isn't indexed
           # We'll pass 240 to ensure we will get a scrobble
           # at 2 minutes of playtime
           track_length = 240
        print(f"Track length: {track_length}")
    
    # First check if it's longer than 30, if not we won't even send a task so if 30
    # Then, if it is longer than 30, compute either if half the duration or 4 minutes is shorter,
    # then schedule a scrobble task with that delay

    if track_length > 30.0:
      delay = min(track_length / 2, 240)  # Half the duration or 4 minutes
      print(f"Scheduling scrobble in {delay} seconds")
      time.sleep(delay)
      lastfm.scrobble(artist=artist, title=title, timestamp=int(time.time()), album=album_title)
      print(f"Scrobbled Artist: {artist}, Title: {title}, Album: {album_title}")