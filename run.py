import asyncio
import socketio
import time
import logging
import re
from utils.scrobbler import scheduleScrobble

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
sio = socketio.AsyncClient()

@sio.on('update', namespace="/nowplaying")
async def receiveNowPlayingUpdates(data) -> None:
  """
  Listener for /nowplaying updates from xbn. When received, it will
  pass the data onto the processor task to handle scrobbling.
  """
  await scheduleScrobble(data)

@sio.on('update', namespace="/broadcast/fnt")
async def receiveBroadcastUpdates(data):
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

async def main():
  logger.info("Connecting to xbn.fm...")
  await sio.connect('https://node.xbn.fm', socketio_path='/socket.io')
  await sio.wait()

if __name__ == '__main__':
  asyncio.run(main())