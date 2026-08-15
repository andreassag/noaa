FROM python:3.14-slim

LABEL org.opencontainers.image.source="https://github.com/andreassag/noaa"
LABEL org.opencontainers.image.description="NOAA Climate Data Online API Client"
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml ./
COPY README.md ./
COPY src/noaa ./src/noaa/

# Install the package
RUN uv pip install --system --no-cache --no-build-isolation -e .

# Default command
CMD ["python", "-c", "import noaa; print(f'NOAA API Client v{noaa.__version__} ready')"]
