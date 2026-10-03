FROM python:3.11-slim

WORKDIR /app

# LightGBM's prebuilt wheel needs the OpenMP runtime. Psycopg's binary wheel bundles libpq.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=60 --retries=10 -r requirements.txt

COPY . .

# Make entrypoint scripts executable
RUN chmod +x entrypoint.sh entrypoint.prod.sh


EXPOSE 8000

# Default command (overridden by entrypoint.sh in compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
