FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ src/
COPY pyproject.toml .

# Install the package
RUN pip install --no-cache-dir -e .

# Verify installation
RUN miie --version

ENTRYPOINT ["miie"]
CMD ["--help"]
