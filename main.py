"""CLI principal — Prueba técnica Simetrik."""

import logging
from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

# Cargar .env una sola vez al inicio, antes de cualquier import de módulos propios
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

app = typer.Typer(name="prueba", help="Prueba técnica Simetrik — Integraciones", add_completion=False)
console = Console()


@app.command()
def p1(
    country: str = typer.Option("CO", "--country", "-c", help="Código de país Spotify (ej: CO, US, MX)"),
    output: Path = typer.Option(Path("output/punto_1"), "--output", "-o"),
) -> None:
    """Punto 1: Extrae top canciones por género desde Spotify API."""
    from src.punto_1_spotify.extractor import extract_top_songs_by_genre

    console.print(f"[bold #1DB954]Spotify Extractor[/] — País: [bold]{country}[/]")
    generated = extract_top_songs_by_genre(country=country, output_dir=output)

    table = Table(title=f"CSVs generados ({len(generated)})")
    table.add_column("Archivo", style="bold")
    table.add_column("Ruta")
    for p in generated:
        table.add_row(p.name, str(p))
    console.print(table)


@app.command()
def p2(
    output: Path = typer.Option(Path("output/punto_2"), "--output", "-o"),
) -> None:
    """Punto 2: Parsea transacciones_1.txt a CSV usando posiciones del Excel."""
    from src.punto_2_parser.parser import parse_transacciones

    console.print("[bold cyan]Parser transacciones[/]")
    out = parse_transacciones(output_dir=output)
    console.print(f"[green]Listo:[/] {out}")


@app.command()
def p3() -> None:
    """Punto 3: Muestra las queries SQL preparadas para los ejercicios en vivo."""
    sql_path = Path(__file__).parent / "src" / "punto_3_sql" / "queries.sql"
    console.print("[bold yellow]Queries SQL — Punto 3[/]")
    console.print(f"Archivo: [bold]{sql_path}[/]\n")
    console.print(sql_path.read_text())


if __name__ == "__main__":
    app()
