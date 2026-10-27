"""Configuración compartida, independiente de la interfaz."""
import os
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parents[1]

def database_url(explicit=None):
    url = explicit or os.getenv("DATABASE_URL") or f"sqlite:///{ROOT_DIR / 'sistema_vinculacion.db'}"
    if url.startswith("postgres://"):
        url = "postgresql+psycopg2://" + url[len("postgres://"):]
    elif url.startswith("postgresql://"):
        url = "postgresql+psycopg2://" + url[len("postgresql://"):]
    return url
