import pandas as pd

import ast

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException

from tqdm import tqdm

import swifter
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

import time

import config

@retry(
    wait=wait_exponential(multiplier=1, min=1, max=10),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(SpotifyException),
)
def spotify_call(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except SpotifyException as e:
        if e.http_status == 429:
            retry_after = int(e.headers.get('Retry-After', 1))
            print(f"Rate limited :(. Retrying after {retry_after} seconds...")
            time.sleep(retry_after)
        raise

def get_artist_genres(artist_ids):
    genres = {}
    for i in tqdm(range(0, len(artist_ids), 50)):
        batch = artist_ids[i:i+50]
        try:
            artists = spotify_call(sp.artists, batch)["artists"]
            for artist in artists:
                if artist:
                    genres[artist["id"]] = artist["genres"]
                    config.EXTRA_VERBOSE and print(f"| ✓ {artist} genre(s) successfully found...")
        except Exception as e:
            print(f"L + Ratio {i}: {str(e)}")
    return genres

def get_track_genres(artist_ids):
    genres = []
    for artist_id in artist_ids:
        genres.extend(artist_genres.get(artist_id, []))
    return list(set(genres))

if __name__ == "__main__":
    auth = SpotifyClientCredentials(client_id=config.CLIENT_ID, client_secret=config.CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager=auth)

    config.VERBOSE and print(f"--> ○ Loading dataset from {config.DF_PATH}...")
    df = pd.read_csv(config.DF_PATH)
    config.VERBOSE and print(f"--> ✓ Dataset from {config.DF_PATH} loaded successfully...")

    # python moment
    config.VERBOSE and print(f"--> ○ Pre-processing arrays as python interpretable datatypes...")
    df["artist_ids"] = df["artist_ids"].apply(ast.literal_eval)
    config.VERBOSE and print(f"--> ✓ Pre-processing successful...")

    # artists show up more than once
    config.VERBOSE and print(f"--> ○ De-duplicating artist IDs...")
    artist_ids = df["artist_ids"].explode().unique().tolist()
    config.VERBOSE and print(f"--> ✓ Artist IDs de-duplicated...")

    config.VERBOSE and print(f"--> ○ Gathering artist genres by artist ID...")
    artist_genres = get_artist_genres(artist_ids)
    config.VERBOSE and print(f"--> ✓ Artist genres found...")

    config.VERBOSE and print(f"--> ○ Mapping artist genre(s) to tracks...")
    df["genres"] = df["artist_ids"].swifter.apply(get_track_genres)
    config.VERBOSE and print(f"--> ✓ Successfully mapped artist genre(s) to tracks")
    df.to_csv(config.DF_AFTER_OPERATION_PATH, index=False)
    config.VERBOSE and print(f"New dataset saved at {config.DF_AFTER_OPERATION_PATH}!")