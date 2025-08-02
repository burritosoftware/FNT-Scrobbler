from pylast import SessionKeyGenerator, LastFMNetwork, WSError
from os import getenv, getcwd, path
from dotenv import load_dotenv
load_dotenv()

def getLastFMNetwork() -> LastFMNetwork:
    """
    Get the Last.fm network by authorizing with the Last.fm API.
    If no existing session key, prompt the user to authorize the application.
    """
    # Define the session key file path
    # This will be used to store the session key after authorization
    SESSION_KEY_FILE = getenv("LASTFM_SESSION_KEY_FILE", ".lfm-session-key")

    # Initialize LastFMNetwork with API credentials
    lastfm = LastFMNetwork(
        api_key=getenv("LASTFM_API_KEY"),
        api_secret=getenv("LASTFM_API_SECRET"),
        session_key=None  # Initially no session key
    )

    # If we don't have a session key we will generate an authorization URL to get one
    if not path.exists(SESSION_KEY_FILE):
        skg = SessionKeyGenerator(lastfm)
        url = skg.get_web_auth_url()

        print(f"Please authorize FNT Scrobbler to access your Last.fm account: {url}\n")
        import time
        import webbrowser

        # Open the authorization URL in the default web browser
        webbrowser.open(url)

        while True:
            try:
                session_key = skg.get_web_auth_session_key(url)
                with open(SESSION_KEY_FILE, "w") as f:
                    f.write(session_key)
                break
            except WSError:
                time.sleep(1)
    else:
        # Found an existing session key, reading
        session_key = open(SESSION_KEY_FILE).read()
    
    # Attach the session key to the network object and return it
    lastfm.session_key = session_key
    return lastfm