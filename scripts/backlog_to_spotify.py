import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import json
client_id = ""
client_secret = ""
scope = "ugc-image-upload,playlist-modify-private,"
redirect_uri="http://127.0.0.1:9090"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope))

uris = []

# Read backlog.json
# For each object in backlog.json, search for the track on Spotify
with open("backlog.json", "r", encoding="utf-8") as f:
    backlog = json.load(f)
    for item in backlog:
        print(f"Searching for {item['title']} by {item['artist']}...")
        artist = item['artist']
        title = item['title']
        results = sp.search(q=f'{artist} {title}', type="track", limit=1)

        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            print(f"Found {track['name']} by {track['artists'][0]['name']}")
            uri = track['uri']
            uris.append(uri)
        else:
            print("Couldn't find track")
        time.sleep(3)

playlist = sp.user_playlist_create(user=sp.current_user()['id'], name="FNT Backlog", public=False, description="Backlog of tracks played on FNT Radio")
id = playlist['id']
print(uris)
sp.playlist_add_items(playlist_id=id, items=uris)