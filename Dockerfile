FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

WORKDIR /app

# Runtime/build libraries required by GeoPandas, Shapely, Pyogrio and PyProj.
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        gdal-bin \
        libgdal-dev \
        libgeos-dev \
        libproj-dev \
        libspatialindex-dev \
    && rm -rf /var/lib/apt/lists/*

COPY programas\ webapp/requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Cloud Run sends traffic to $PORT; the app binds to all container interfaces.
EXPOSE 8080

RUN useradd --create-home --shell /usr/sbin/nologin appuser \
    && chown -R appuser:appuser /app
USER appuser

CMD ["streamlit", "run", "programas webapp/app_dashboard.py", "--server.port=8080", "--server.address=0.0.0.0"]