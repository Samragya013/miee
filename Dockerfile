FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-dev --no-interaction

COPY src/ src/
COPY tests/ tests/

RUN miie --version

ENTRYPOINT ["miie"]
CMD ["--help"]
