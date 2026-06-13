# Synesthesia — Setup Guide

## 1. Create & activate the virtual environment

```bash
cd Synesthesia
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Get Spotify credentials

1. Go to [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
2. Click **Create app**
3. Set **Redirect URI** to `http://localhost:8888/callback`
4. Copy your **Client ID** and **Client Secret**

## 3. Create a `.env` file

```bash
cp .env.example .env
# then open .env and paste in your credentials
```

`.env` contents:
```
SPOTIFY_CLIENT_ID=abc123...
SPOTIFY_CLIENT_SECRET=def456...
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
```

## 4. Run

### Option A — Streamlit UI (recommended)
```bash
streamlit run app.py
```
Opens at `http://localhost:8501`.  
Drop in any photo → see the color palette → click **Generate Spotify Playlist**.

### Option B — CLI
```bash
python pipeline.py path/to/photo.jpg
# optional args: k_clusters (default 5) and track_count (default 25)
python pipeline.py sunset.jpg 4 30
```

First run triggers a browser login to Spotify. Token is cached in `.spotify_cache`.

---

## File map

| File | What it does |
|------|-------------|
| `vision.py` | K-Means color extraction (Phase 2) |
| `mood.py` | HSV → Spotify audio feature mapping (Phase 2) |
| `spotify.py` | OAuth, recommendations, playlist creation (Phase 3) |
| `pipeline.py` | Master orchestrator + CLI (Phase 4) |
| `app.py` | Streamlit drag-and-drop UI (Phase 4) |
