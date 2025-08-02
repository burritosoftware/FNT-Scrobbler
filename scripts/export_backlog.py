import logging
import sys
from dotenv import load_dotenv
from os import getenv
logging.basicConfig(
    level=logging.INFO,
    force=True,
    stream=sys.stdout,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)
load_dotenv()
logger.setLevel(getenv("LOG_LEVEL", "INFO"))

import asyncio
import socketio
import re
import json

sio = socketio.AsyncClient()

@sio.on('backlog', namespace='/nowplaying')
async def receiveBacklog(data):
    print(f"Received {len(data)} tracks")
    tracks = []
    for t in data:
        if t['name'].startswith("XBN"):
          continue

        artist, title = t['name'].split(' — ', 1)

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
        title = re.sub(pattern, "", title).strip()

        tracks.append({"artist": artist, "title": title, "timestamp": t['date']})

    print("Saving backlog to backlog.json")
    with open("backlog.json", "w", encoding="utf-8") as f:
        # Make sure tracks is utf-8 encoded before dumping
        json.dump(tracks, f, ensure_ascii=False)

    print("Done, press CTRL+C to exit...")

@sio.event
async def connect():
    logger.info("[socket] CONNECTED: Connected to xbn.fm!")

@sio.event
async def connect_error(data):
    logger.error("[socket] CONNECT_ERROR: The connection failed!")

@sio.event
async def disconnect(reason):
    if reason != "client disconnect":
      logger.warning(f"[socket] DISCONNECTED: reason: {reason}")

async def startup() -> None:
    """Connect to xbn.fm until the program is stopped."""
    logger.info("[socket] CONNECTING: Connecting to xbn.fm...")
    await sio.connect("https://node.xbn.fm", socketio_path="/socket.io")
    await sio.wait()                       # blocks here

async def shutdown() -> None:
    """Disconnect from xbn.fm and wait for pending scrobbles."""
    logger.info("[socket] SHUTDOWN: Shutting down...")
    if sio.connected:
        await sio.disconnect()
    exit()

async def main() -> None:
    try:
        await startup()
    finally:
        await shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Second Ctrl+C before graceful exit just lands here
        logger.warning("[app] Forced exit")