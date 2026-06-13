# Synesthesia 🎨🎵

Upload a photo, get a Spotify playlist that matches its vibe.

Extracts the dominant color palette using K-Means clustering, maps the colors to audio mood features (energy, valence, tempo), then searches Spotify for tracks that fit.

![Python](https://img.shields.io/badge/Python-3.12-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.28-red) ![Spotify](https://img.shields.io/badge/Spotify-API-1DB954?logo=spotify&logoColor=white)

---

## Setup

**1. Clone and create a virtual environment**

```bash
git clone <your-repo-url>
cd Synesthesia
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**2. Get Spotify API credentials**

1. Go to [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
2. Click **Create app**
3. Add this as a Redirect URI:
   ```
   http://127.0.0.1:8501
   ```
4. Copy your **Client ID** and **Client Secret**

**3. Run the app**

```bash
.venv/bin/streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501), paste your credentials into the sidebar, and log in with Spotify.

---

## How it works

| Step | File | What happens |
|------|------|-------------|
| 1 | `vision.py` | Image is resized, converted to HSV, K-Means finds dominant colors |
| 2 | `mood.py` | HSV values map to energy, valence, tempo, and genre seeds |
| 3 | `spotify.py` | Spotify track search using genre + mood queries |
| 4 | `app.py` | Playlist created on your Spotify account |

## CLI usage

```bash
python pipeline.py path/to/photo.jpg
# optional: k_clusters (default 5), track_count (default 20)
python pipeline.py sunset.jpg 4 15
```

---

## Project structure

```
├── app.py            # Streamlit UI
├── pipeline.py       # CLI entry point
├── vision.py         # Color extraction
├── mood.py           # Color → mood mapping
├── spotify.py        # Spotify API
├── requirements.txt
├── .env.example      # Copy to .env and fill in credentials
└── .gitignore
```

## Notes

- Your `.env` file contains your Spotify credentials — it is gitignored and never committed
- Spotify's dev tier limits search to 5 results per query; the app runs multiple queries to fill the playlist
- The `/recommendations` endpoint was removed by Spotify in November 2024; this app uses track search as a workaround
