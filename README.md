# Observatorio de la Economía del Cuidado CDMX

Segundo avance: monolito modular en Python/Streamlit. Observatorio de las 16
alcaldías y demostración sintética de vinculación con centros comunitarios.
No es una plataforma de contratación de personas cuidadoras.

## Ejecución local (Python 3.12)

Desde la raíz del repositorio:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app_dashboard.py
```

El dataset público preparado está versionado. Al cambiar fuentes o ETL:

```bash
python -m cuidado.pipelines.preparar
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

## Documentación

- [Arquitectura y límites](docs/ARQUITECTURA.md)
- [Despliegue y permisos](docs/STREAMLIT.md)
- [Contratos de integración del equipo](docs/CONTRATOS.md)
- [Requisitos y pendientes del segundo avance](docs/SEGUNDO_AVANCE.md)
- [Contexto para el equipo y Copilot](CONTEXTO_PROYECTO.md)

## Módulos

`cuidado/ui`: presentación; `services`: coordinación; `domain`: matching;
`database`: conexión y esquema v2; `pipelines`: preparación territorial.
Los notebooks y fuentes originales se conservan. Los puntos de entrada en
`programas webapp/` se mantienen por compatibilidad.

El demo público no requiere DATABASE_URL, no registra personas y no escribe
sus simulaciones en una base compartida. Los módulos de Karla y Azael están
pendientes de recepción y validación, con su responsabilidad preservada.
