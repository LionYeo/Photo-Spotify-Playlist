import cv2
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
from dataclasses import dataclass


@dataclass
class ColorPalette:
    colors_hsv: np.ndarray
    colors_hex: list[str]
    weights: np.ndarray
    dominant: np.ndarray


def load_image(path: str, max_dim: int = 300) -> np.ndarray:
    img = cv2.imread(path)
    if img is None:
        pil = Image.open(path).convert("RGB")
        img = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
    h, w = img.shape[:2]
    scale = max_dim / max(h, w)
    if scale < 1.0:
        img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    return img


def extract_palette(image_path: str, k: int = 5) -> ColorPalette:
    img_bgr = load_image(image_path)
    img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

    pixels = img_hsv.reshape(-1, 3).astype(np.float32)
    pixels_norm = pixels / np.array([179.0, 255.0, 255.0])

    kmeans = KMeans(n_clusters=k, n_init=10, random_state=42)
    labels = kmeans.fit_predict(pixels_norm)

    centers = kmeans.cluster_centers_
    counts = np.bincount(labels, minlength=k).astype(float)
    weights = counts / counts.sum()

    order = np.argsort(-weights)
    centers = centers[order]
    weights = weights[order]

    dominant = np.average(centers, axis=0, weights=weights)

    hex_codes = []
    for c in centers:
        hsv_cv = (c * np.array([179.0, 255.0, 255.0])).astype(np.uint8)
        rgb = cv2.cvtColor(np.array([[hsv_cv]], dtype=np.uint8), cv2.COLOR_HSV2RGB)[0][0]
        hex_codes.append("#{:02X}{:02X}{:02X}".format(*rgb))

    return ColorPalette(
        colors_hsv=centers,
        colors_hex=hex_codes,
        weights=weights,
        dominant=dominant,
    )
