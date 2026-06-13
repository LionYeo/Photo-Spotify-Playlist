"""
CLI entry point: python pipeline.py <image_path> [k_clusters] [track_count]
"""

import sys
from vision import extract_palette
from mood import palette_to_mood
from spotify import get_spotify_client, fetch_recommendations, create_playlist


def run_pipeline(image_path: str, k: int = 5, track_count: int = 20) -> dict:
    print(f"[1/4] Extracting palette from: {image_path}")
    palette = extract_palette(image_path, k=k)

    print(f"[2/4] Translating colors to mood...")
    print(f"      Palette: {' '.join(palette.colors_hex)}")
    mood = palette_to_mood(palette)
    print(f"      Mood: {mood.description}  |  Energy={mood.energy}  Valence={mood.valence}")

    print(f"[3/4] Fetching {track_count} tracks from Spotify...")
    sp = get_spotify_client()
    track_uris = fetch_recommendations(sp, mood, limit=track_count)
    print(f"      Got {len(track_uris)} tracks")

    print(f"[4/4] Creating playlist...")
    url = create_playlist(sp, track_uris, palette.colors_hex[0], mood.description)
    print(f"\n      {url}\n")

    return {"palette": palette, "mood": mood, "track_uris": track_uris, "playlist_url": url}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pipeline.py <image_path> [k_clusters] [track_count]")
        sys.exit(1)

    run_pipeline(
        sys.argv[1],
        k=int(sys.argv[2]) if len(sys.argv) > 2 else 5,
        track_count=int(sys.argv[3]) if len(sys.argv) > 3 else 20,
    )
