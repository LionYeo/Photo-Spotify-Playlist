import numpy as np
from dataclasses import dataclass
from vision import ColorPalette


@dataclass
class MoodVector:
    energy: float
    valence: float
    danceability: float
    acousticness: float
    instrumentalness: float
    tempo: float
    seed_genres: list[str]
    search_terms: list[str]
    description: str


def _clamp(v: float) -> float:
    return float(np.clip(v, 0.0, 1.0))


def palette_to_mood(palette: ColorPalette) -> MoodVector:
    H, S, V = palette.dominant

    warm_score = np.cos(2 * np.pi * (H - 0.08)) * 0.5 + 0.5

    valence          = _clamp(warm_score * 0.65 + S * 0.2 + V * 0.15)
    energy           = _clamp(V * 0.55 + S * 0.45)
    danceability     = _clamp(energy * 0.55 + valence * 0.45)
    acousticness     = _clamp(1.0 - (energy * 0.55 + S * 0.45))
    cool_score       = 1.0 - warm_score
    instrumentalness = _clamp(cool_score * 0.5 + (1 - S) * 0.3 + (1 - V) * 0.2)
    tempo            = 60 + energy * 115

    genres, search_terms, description = _classify(H, S, V, energy, valence)

    return MoodVector(
        energy=round(energy, 3),
        valence=round(valence, 3),
        danceability=round(danceability, 3),
        acousticness=round(acousticness, 3),
        instrumentalness=round(instrumentalness, 3),
        tempo=round(tempo, 1),
        seed_genres=genres,
        search_terms=search_terms,
        description=description,
    )


def _classify(H: float, S: float, V: float, energy: float, valence: float):
    # Monochrome / near-gray
    if S < 0.15:
        if V > 0.75:
            return (["indie pop", "chillwave", "dream pop"],
                    ["dreamy", "soft pop", "lo-fi chill"], "Airy & Minimal")
        if V > 0.4:
            return (["jazz", "soul", "r&b"],
                    ["mellow jazz", "neo soul", "late night"], "Muted & Soulful")
        return (["ambient", "classical", "post-rock"],
                ["cinematic", "dark ambient", "instrumental"], "Dark & Cinematic")

    # Very dark saturated
    if V < 0.25:
        if H < 0.5:
            return (["blues", "dark folk", "gothic"],
                    ["dark blues", "moody", "underground"], "Deep & Brooding")
        return (["ambient", "electronic", "trip-hop"],
                ["dark electronic", "midnight", "trip hop"], "Nocturnal & Mysterious")

    # Warm: red / orange / yellow (H 0–0.19)
    if H < 0.19:
        if energy > 0.65:
            return (["pop", "dance pop", "funk"],
                    ["upbeat pop", "feel good", "summer hits"], "Vibrant & Euphoric")
        if energy > 0.4:
            return (["indie pop", "pop rock", "alternative"],
                    ["indie pop", "sunny", "road trip"], "Warm & Energetic")
        return (["acoustic", "folk", "singer-songwriter"],
                ["acoustic", "cozy", "morning coffee"], "Golden & Nostalgic")

    # Yellow-green (H 0.19–0.38)
    if H < 0.38:
        if S > 0.6 and energy > 0.55:
            return (["reggae", "afrobeats", "latin"],
                    ["tropical", "afrobeats", "feel good"], "Fresh & Lively")
        if energy > 0.5:
            return (["indie", "alternative", "pop rock"],
                    ["indie feel good", "spring playlist", "uplifting"], "Breezy & Optimistic")
        return (["acoustic", "folk", "ambient pop"],
                ["nature sounds", "forest folk", "calm acoustic"], "Earthy & Serene")

    # Cyan / teal (H 0.38–0.55)
    if H < 0.55:
        if energy > 0.6:
            return (["electronic", "chillwave", "synth pop"],
                    ["synthwave", "electronic chill", "beach vibes"], "Electric & Refreshing")
        return (["chillwave", "ambient", "lo-fi"],
                ["lo-fi study", "ocean sounds", "chill beats"], "Cool & Tranquil")

    # Blue (H 0.55–0.72)
    if H < 0.72:
        if V > 0.6 and energy > 0.5:
            return (["pop", "indie pop", "dance"],
                    ["blue aesthetic", "indie pop", "daydream"], "Dreamy & Wistful")
        if energy > 0.5:
            return (["rock", "alternative", "post-rock"],
                    ["post rock", "alternative rock", "driving"], "Intense & Driven")
        return (["classical", "ambient", "piano"],
                ["sad piano", "melancholy", "rainy day"], "Melancholic & Introspective")

    # Purple / violet (H 0.72–0.83)
    if H < 0.83:
        if energy > 0.6:
            return (["electronic", "synth pop", "indie electronic"],
                    ["synthpop", "80s", "neon lights"], "Mysterious & Electric")
        return (["r&b", "neo soul", "dream pop"],
                ["neo soul", "twilight", "r&b chill"], "Sultry & Dreamy")

    # Magenta / pink (H 0.83–1.0)
    if energy > 0.65:
        return (["pop", "dance pop", "electropop"],
                ["pop hits", "party", "feel good pop"], "Bold & Playful")
    return (["indie pop", "chillwave", "bedroom pop"],
            ["bedroom pop", "soft indie", "aesthetic"], "Soft & Romantic")
