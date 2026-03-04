"""Parsea transacciones_1.txt a CSV usando posiciones del Excel de documentación."""

import logging
from pathlib import Path

import pandas as pd

from .schema import load_body_schema

log = logging.getLogger(__name__)

DOCS_DIR = Path(__file__).parents[2] / "docs"
DEFAULT_TXT = DOCS_DIR / "transacciones_1.txt"


def _find_xlsx(docs_dir: Path) -> Path:
    """Localiza el Excel de documentación de forma robusta (sin depender del encoding del nombre)."""
    candidates = list(docs_dir.glob("Documentaci*.xlsx"))
    if not candidates:
        raise FileNotFoundError(
            f"No se encontró archivo de documentación (Documentaci*.xlsx) en '{docs_dir}'. "
            "Asegúrate de que el archivo esté en la carpeta docs/."
        )
    if len(candidates) > 1:
        log.warning("Múltiples candidatos encontrados: %s. Usando el primero.", candidates)
    return candidates[0]


def parse_transacciones(
    txt_path: Path = DEFAULT_TXT,
    xlsx_path: Path | None = None,
    output_dir: Path = Path("output/punto_2"),
) -> Path:
    """
    Parsea el archivo fixed-width y genera output_dir/transacciones.csv.
    - Salta la primera línea (Header) y la última (Tail).
    - Usa posiciones de la hoja Body del Excel.
    - Columnas sin caracteres especiales.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    resolved_xlsx = xlsx_path or _find_xlsx(DOCS_DIR)

    log.info("Leyendo schema desde: %s", resolved_xlsx.name)
    fields = load_body_schema(resolved_xlsx)
    log.info("Campos leaf encontrados: %d", len(fields))

    # colspecs usa 0-indexed [start, end) — Excel usa 1-indexed inclusivo
    colspecs = [(f["pos_ini"] - 1, f["pos_fin"]) for f in fields]
    names = [f["name"] for f in fields]

    log.info("Parseando: %s", txt_path.name)
    df = pd.read_fwf(
        txt_path,
        colspecs=colspecs,
        names=names,
        header=None,
        skiprows=1,        # salta Header
        skipfooter=1,      # salta Tail
        dtype=str,         # todo como string — preserva ceros iniciales
        encoding="latin-1",
        engine="python",   # necesario para skipfooter
    )

    # Limpiar: strip de espacios en columnas string
    df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)

    out_path = output_dir / "transacciones.csv"
    df.to_csv(out_path, index=False, encoding="utf-8")
    log.info("CSV generado: %s (%s filas × %d columnas)", out_path, f"{len(df):,}", len(df.columns))
    return out_path
