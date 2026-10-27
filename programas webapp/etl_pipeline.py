"""Compatibilidad con scripts existentes. Implementación en cuidado.pipelines.territorial."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cuidado.pipelines.territorial import *
