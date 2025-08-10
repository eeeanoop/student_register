"""Utilities for computing and caching face embeddings.

The module relies on the ``face_recognition`` package.  If it isn't
installed, the functions gracefully fall back to no-ops so that the rest
of the application can continue to function using only the LBPH
recogniser.
"""

from __future__ import annotations

import os
from typing import Dict

import numpy as np

try:  # Optional dependency
    import face_recognition  # type: ignore
except Exception:  # pragma: no cover - optional dependency might be missing
    face_recognition = None  # type: ignore


def load_embeddings(image_dir: str) -> Dict[str, np.ndarray]:
    """Load student images and compute embeddings.

    Parameters
    ----------
    image_dir:
        Directory containing student photos.  The filename (without
        extension) is used as the student's name.

    Returns
    -------
    dict
        Mapping of student names to their 128-d embedding vectors.
    """

    embeddings: Dict[str, np.ndarray] = {}
    if face_recognition is None or not os.path.isdir(image_dir):
        return embeddings

    for filename in sorted(os.listdir(image_dir)):
        if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        path = os.path.join(image_dir, filename)
        image = face_recognition.load_image_file(path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            name = os.path.splitext(filename)[0]
            embeddings[name] = encodings[0]
    return embeddings


def compute_embedding(image: np.ndarray) -> np.ndarray | None:
    """Compute an embedding for a single face image.

    Parameters
    ----------
    image:
        BGR image array of a cropped face.

    Returns
    -------
    numpy.ndarray or None
        128-d embedding vector or ``None`` if no face is detected or the
        dependency is missing.
    """

    if face_recognition is None:
        return None
    rgb = image[:, :, ::-1]  # BGR to RGB
    encodings = face_recognition.face_encodings(rgb)
    return encodings[0] if encodings else None


def compare_embeddings(a: np.ndarray, b: np.ndarray) -> float:
    """Return the Euclidean distance between two embeddings."""

    return float(np.linalg.norm(a - b))
