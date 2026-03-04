"""Extrae top canciones por género de una región y guarda un CSV por género.

Estrategia: /search?type=track&q=genre:{genre}&market={country}
(Los endpoints browse/recommendations fueron deprecados en Nov 2024)
"""

import logging
import re
from pathlib import Path

import pandas as pd

from .client import SpotifyClient

log = logging.getLogger(__name__)

# Géneros representativos — cubre los principales para Colombia y Latinoamérica
GENRES = [
    "pop", "rock", "latin", "reggaeton", "salsa", "cumbia", "vallenato",
    "hip-hop", "r-n-b", "electronic", "jazz", "classical", "country",
    "metal", "indie", "folk", "blues", "soul", "trap", "bachata",
]


def search_tracks_by_genre(
    client: SpotifyClient, genre: str, market: str, total: int = 50
) -> list[dict]:
    """Busca tracks por género usando /search con paginación.
    Nota: genre: filter acepta máximo 10 por request — paginamos con offset.
    """
    rows: list[dict] = []
    page_size = 10  # límite máximo permitido por Spotify con genre: filter
    for offset in range(0, total, page_size):
        data = client.get(
            "/search",
            params={
                "q": f"genre:{genre}",
                "type": "track",
                "market": market,
                "limit": page_size,
                "offset": offset,
            },
        )
        tracks_data = data.get("tracks", {})
        items = tracks_data.get("items", [])
        total_available = tracks_data.get("total", 0)
        if not items or offset >= total_available:
            break
        for track in items:
            if not track:
                continue
            # Guard: artistas con name=None son posibles en metadata incompleta
            artists = ", ".join(a["name"] for a in track.get("artists", []) if a.get("name"))
            album = track.get("album", {}).get("name", "")
            rows.append({
                "track_name": track.get("name", ""),
                "artist": artists,
                "album": album,
                "popularity": track.get("popularity", 0),
                "duration_ms": track.get("duration_ms", 0),
            })
    return rows


def extract_top_songs_by_genre(
    country: str = "CO",
    output_dir: Path = Path("output/punto_1"),
    genres: list[str] | None = None,
) -> list[Path]:
    """
    Extrae canciones por género para un mercado usando /search.
    Genera un CSV por género en output_dir.
    Retorna lista de archivos generados.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []
    genre_list = genres or GENRES

    log.info("Extrayendo %d géneros para mercado: %s", len(genre_list), country)

    with SpotifyClient() as client:
        for genre in genre_list:
            log.info("Procesando género: %s", genre)
            tracks = search_tracks_by_genre(client, genre, market=country)

            if not tracks:
                log.warning("Sin resultados para género: %s", genre)
                continue

            df = pd.DataFrame(tracks)
            df["genre"] = genre
            df["country"] = country
            df = df.drop_duplicates(subset=["track_name", "artist"])
            df = df.sort_values("popularity", ascending=False)

            # Sanitizar nombre: reemplaza cualquier caracter no-alfanumérico por _
            safe_name = re.sub(r"[^\w\-]", "_", genre)
            out_path = output_dir / f"{safe_name}.csv"
            df.to_csv(out_path, index=False, encoding="utf-8")
            log.info("Guardado: %s (%d tracks)", out_path.name, len(df))
            generated.append(out_path)

    return generated
