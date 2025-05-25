from spotapi import Song

def search_spotify(query, limit=5):
    song = Song()
    results = song.query_songs(query, limit=limit)
    tracks = results["data"]["searchV2"]["tracksV2"]["items"]

    for i, item in enumerate(tracks, 1):
        track_data = item["item"]["data"]
        title = track_data["name"]
        artists = ", ".join(artist["profile"]["name"] for artist in track_data["artists"]["items"])
        album = track_data["albumOfTrack"]["name"]
        url = f"https://open.spotify.com/track/{track_data['id']}"
        print(f"{i}. {title} by {artists} — {album}\n   {url}\n")

if __name__ == "__main__":
    search_spotify("love me")
