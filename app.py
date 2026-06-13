import streamlit as st
import tempfile
import os

from vision import extract_palette
from mood import palette_to_mood
from spotify import get_auth_url, get_spotify_from_code, fetch_recommendations, create_playlist

st.set_page_config(page_title="Synesthesia", page_icon="🎨", layout="centered")

st.markdown(
    """
    <style>
    .big-title { font-size: 2.8rem; font-weight: 800; letter-spacing: -1px; }
    .subtitle  { font-size: 1.1rem; color: #888; margin-top: -12px; }
    .swatch    { display:inline-block; width:36px; height:36px;
                 border-radius:50%; margin:4px; border:2px solid rgba(255,255,255,.3); }
    </style>
    """,
    unsafe_allow_html=True,
)

ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
REDIRECT_URI = "http://127.0.0.1:8501"


def _load_env():
    if not os.path.exists(ENV_PATH):
        return
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def _save_env(cid: str, csecret: str):
    with open(ENV_PATH, "w") as f:
        f.write(f"SPOTIFY_CLIENT_ID={cid}\n")
        f.write(f"SPOTIFY_CLIENT_SECRET={csecret}\n")
        f.write(f"SPOTIFY_REDIRECT_URI={REDIRECT_URI}\n")
    os.environ["SPOTIFY_CLIENT_ID"] = cid
    os.environ["SPOTIFY_CLIENT_SECRET"] = csecret
    os.environ["SPOTIFY_REDIRECT_URI"] = REDIRECT_URI


_load_env()

params = st.query_params
if "code" in params and "sp_client" not in st.session_state:
    with st.spinner("Connecting to Spotify..."):
        try:
            st.session_state["sp_client"] = get_spotify_from_code(params["code"], REDIRECT_URI)
            st.query_params.clear()
            st.success("Spotify connected!")
        except Exception as e:
            st.error(f"Spotify auth failed: {e}")

with st.sidebar:
    st.header("Spotify Setup")

    creds_present = bool(os.getenv("SPOTIFY_CLIENT_ID") and os.getenv("SPOTIFY_CLIENT_SECRET"))

    with st.expander("Step 1 — Get credentials", expanded=not creds_present):
        st.markdown(
            f"""
1. Go to [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
2. Click **Create app**
3. Under **Redirect URIs** add exactly:
   ```
   {REDIRECT_URI}
   ```
4. Save → open **Settings** → copy your Client ID & Secret
            """
        )

    client_id = st.text_input("Client ID", type="password",
                               value=os.getenv("SPOTIFY_CLIENT_ID", ""),
                               placeholder="Paste your Client ID")
    client_secret = st.text_input("Client Secret", type="password",
                                   value=os.getenv("SPOTIFY_CLIENT_SECRET", ""),
                                   placeholder="Paste your Client Secret")

    if st.button("Save credentials", use_container_width=True):
        if client_id and client_secret:
            _save_env(client_id, client_secret)
            st.success("Saved!")
            st.rerun()
        else:
            st.error("Both fields are required.")

    st.divider()

    sp_connected = "sp_client" in st.session_state
    if creds_present and not sp_connected:
        auth_url = get_auth_url(REDIRECT_URI)
        st.markdown("**Step 2 — Connect your Spotify account**")
        st.markdown(
            f'<a href="{auth_url}" target="_self">'
            f'<button style="width:100%;padding:8px;background:#1DB954;color:#000;'
            f'border:none;border-radius:6px;font-weight:700;cursor:pointer;font-size:.95rem;">'
            f'🎵 Log in with Spotify</button></a>',
            unsafe_allow_html=True,
        )
    elif sp_connected:
        st.success("✅ Spotify connected")
        if st.button("Disconnect", use_container_width=True):
            del st.session_state["sp_client"]
            st.rerun()

    st.divider()
    st.subheader("Tuning")
    k_clusters = st.slider("Color clusters (k)", 3, 8, 5,
                            help="How many dominant colors to extract")
    track_count = st.slider("Tracks in playlist", 10, 25, 20)

st.markdown('<p class="big-title">Synesthesia 🎨🎵</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Drop a photo. Get a playlist that <em>looks</em> like it sounds.</p>',
    unsafe_allow_html=True,
)
st.divider()

uploaded = st.file_uploader(
    "Upload an image",
    type=["jpg", "jpeg", "png", "webp", "heic"],
    label_visibility="collapsed",
)

if uploaded:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded.name)[1]) as tmp:
        tmp.write(uploaded.getvalue())
        tmp_path = tmp.name

    col_img, col_palette = st.columns([2, 1])

    with col_img:
        st.image(uploaded, use_container_width=True)

    with st.spinner("Extracting color palette..."):
        palette = extract_palette(tmp_path, k=k_clusters)

    with col_palette:
        st.markdown("**Dominant palette**")
        swatches = "".join(
            f'<span class="swatch" style="background:{h};" title="{h}"></span>'
            for h in palette.colors_hex
        )
        st.markdown(swatches, unsafe_allow_html=True)
        st.markdown("")
        for hex_, w in zip(palette.colors_hex, palette.weights):
            st.markdown(
                f'<span style="color:{hex_}">██</span> `{hex_}` — {w*100:.1f}%',
                unsafe_allow_html=True,
            )

    mood = palette_to_mood(palette)
    st.markdown(f"### Mood detected: **{mood.description}**")

    cols = st.columns(5)
    for col, (label, val) in zip(cols, [
        ("Energy", mood.energy), ("Valence", mood.valence), ("Dance", mood.danceability),
        ("Acoustic", mood.acousticness), ("Instrumental", mood.instrumentalness),
    ]):
        with col:
            st.metric(label, f"{val:.2f}")
            st.progress(val)

    st.caption(f"Tempo target: **{mood.tempo} BPM** | Seed genres: {', '.join(mood.seed_genres)}")
    st.divider()

    if "sp_client" not in st.session_state:
        st.warning("Log in with Spotify via the sidebar to generate a playlist.")
    else:
        if st.button("🎵 Generate Spotify Playlist", type="primary", use_container_width=True):
            sp = st.session_state["sp_client"]

            with st.spinner(f"Fetching {track_count} tracks..."):
                try:
                    track_uris = fetch_recommendations(sp, mood, limit=track_count)
                except Exception as e:
                    if "401" in str(e):
                        del st.session_state["sp_client"]
                        st.error("Spotify session expired. Please log in again via the sidebar.")
                    else:
                        st.error(f"Spotify error: {e}")
                    st.stop()

            if not track_uris:
                st.error("Couldn't find tracks. Try a different image.")
                st.stop()

            with st.spinner(f"Creating playlist with {len(track_uris)} tracks..."):
                url = create_playlist(sp, track_uris, palette.colors_hex[0], mood.description)

            st.success("Playlist created!")
            st.markdown(
                f"""
                <div style="text-align:center; margin-top:16px;">
                    <a href="{url}" target="_blank"
                       style="background:#1DB954;color:#000;padding:14px 32px;
                              border-radius:50px;font-weight:700;font-size:1.1rem;
                              text-decoration:none;">
                        Open on Spotify ↗
                    </a>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.balloons()

    os.unlink(tmp_path)

else:
    st.markdown(
        """
        <div style="text-align:center; padding:60px 0; color:#555;">
            <div style="font-size:4rem;">🖼️</div>
            <p>Upload any photo above to begin.</p>
            <p style="font-size:.85rem;">Works best with landscapes, abstract art, or photos with a strong color mood.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
