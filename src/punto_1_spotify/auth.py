"""Spotify OAuth — Client Credentials Flow."""

import os
import time

import requests

TOKEN_URL = "https://accounts.spotify.com/api/token"


def _require_env(key: str) -> str:
    """Lee variable de entorno obligatoria con mensaje de error claro."""
    value = os.environ.get(key)
    if not value:
        raise EnvironmentError(
            f"Variable de entorno '{key}' no definida. "
            "Crea un archivo .env basado en .env.example con tus credenciales de Spotify."
        )
    return value


class SpotifyAuth:
    def __init__(self):
        self._client_id = _require_env("SPOTIFY_CLIENT_ID")
        self._client_secret = _require_env("SPOTIFY_CLIENT_SECRET")
        self._token: str | None = None
        self._expires_at: float = 0

    def get_token(self) -> str:
        if self._token and time.time() < self._expires_at - 30:
            return self._token
        return self._refresh()

    def invalidate(self) -> None:
        """Invalida el token actual para forzar refresh en la próxima llamada."""
        self._token = None
        self._expires_at = 0

    def _refresh(self) -> str:
        resp = requests.post(
            TOKEN_URL,
            data={"grant_type": "client_credentials"},
            auth=(self._client_id, self._client_secret),
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        self._token = data["access_token"]
        self._expires_at = time.time() + data["expires_in"]
        return self._token
