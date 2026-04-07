FROM python:3.12-slim

# Instalace systémových závislostí
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Kopírování requirements a instalace
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopírování zbytku aplikace
COPY . .

# Flask musí běžet na portu, který mu přidělí systém
CMD ["python", "app.py"]
