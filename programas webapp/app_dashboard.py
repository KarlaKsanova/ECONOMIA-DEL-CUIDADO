"""Entrada anterior compatible; Cloud debe usar app_dashboard.py en la raíz."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cuidado.ui.app import main
if __name__ == "__main__":
    main()
