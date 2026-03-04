"""HTTP client para Spotify API con retry y token automático."""

import logging
import time

import requests

from .auth import SpotifyAuth

log = logging.getLogger(__name__)
BASE_URL = "https://api.spotify.com/v1"


class SpotifyClient:
    def __init__(self):
        self._auth = SpotifyAuth()
        self._session = requests.Session()

    def get(self, path: str, params: dict | None = None, retries: int = 3) -> dict:
        url = f"{BASE_URL}{path}"
        for attempt in range(retries):
            headers = {"Authorization": f"Bearer {self._auth.get_token()}"}
            resp = self._session.get(url, headers=headers, params=params, timeout=15)

            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", 2))
                log.warning("Rate limit Spotify. Esperando %ss (intento %d/%d)", wait, attempt + 1, retries)
                time.sleep(wait)
                continue

            if resp.status_code == 401:
                log.warning("Token expirado, refrescando... (intento %d/%d)", attempt + 1, retries)
                self._auth.invalidate()
                continue

            resp.raise_for_status()
            return resp.json()

        raise RuntimeError(f"Spotify API falló después de {retries} intentos: {path}")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._session.close()
