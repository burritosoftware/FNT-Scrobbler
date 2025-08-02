import logging
import sys
from dotenv import load_dotenv
from os import getenv
logging.basicConfig(
    level=logging.INFO,              # or INFO
    force=True,                       # reset any prior configs
    stream=sys.stdout,                # Explicitly target stdout
    format="%(asctime)s [%(levelname)s] %(threadName)s:%(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)
load_dotenv()
logger.setLevel(getenv("LOG_LEVEL", "INFO"))

import asyncio
import socketio
from utils.scrobbler import scheduleScrobble

sio = socketio.AsyncClient()
scrobble_tasks: set[asyncio.Task] = set()

@sio.on('update', namespace="/nowplaying")
async def receiveNowPlayingMessages(data) -> None:
  """
  Listener for /nowplaying messages from xbn. When a song is received,
  it will create a new thread to process, schedule, and scrobble the song.
  """
  logger.debug("Received /nowplaying update")
  logger.debug(f"Raw data: {data}")
  # create_task: disassociate it from receiveNowPlayingMessages
  # to_thread: run in a separate thread to avoid blocking
  task = asyncio.create_task(asyncio.to_thread(scheduleScrobble, data), name=data)
  scrobble_tasks.add(task)
  task.add_done_callback(scrobble_tasks.discard)

@sio.on('update', namespace="/broadcast/fnt")
async def receiveBroadcastMessages(data):
  # Heck yeah this is where the code goes
  logger.info("/broadcast/fnt namespace")
  logger.info(data)

@sio.event
async def connect():
    logger.info("Connected to xbn.fm!")

@sio.event
async def connect_error(data):
    logger.error("The connection failed!")

@sio.event
async def disconnect(reason):
    logger.warning(f"I'm disconnected! reason: {reason}")

async def startup() -> None:
    """Connect to xbn.fm until the program is stopped."""
    logger.info("Connecting to xbn.fm...")
    await sio.connect("https://node.xbn.fm", socketio_path="/socket.io")
    await sio.wait()                       # blocks here

async def shutdown() -> None:
    """Disconnect from xbn.fm and wait for pending scrobbles."""
    logger.info("Shutting down...")
    if sio.connected:
        await sio.disconnect()
    
    # scrobble_tasks is the set you’ve been maintaining
    pending = [t for t in scrobble_tasks if not t.done()]

    if pending:
        logger.info("Waiting for %d song-scrobble task(s) to finish:", len(pending))
        for t in pending:
            # .get_name() works on Python 3.8+.  Fallback to repr if missing.
            task_name = t.get_name() if hasattr(t, "get_name") else repr(t)
            logger.info("  • %s", task_name)

        # Let them finish (or gather exceptions) before exiting
        await asyncio.gather(*pending, return_exceptions=True)

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
        logger.warning("Forced exit")