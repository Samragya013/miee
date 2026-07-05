# Installation Guide

## Requirements

- Python 3.10, 3.11, or 3.12
- Git (for repository analysis)
- pip or Poetry

## Install from PyPI

```bash
pip install miie
```

## Install from Source

```bash
git clone https://github.com/Samragya013/miie.git
cd miie
pip install .
```

## Development Install

```bash
git clone https://github.com/Samragya013/miie.git
cd miie
pip install -e .
```

Or with Poetry:

```bash
poetry install
poetry run pre-commit install
```

## Platform-Specific Notes

### Windows

- Use Windows Terminal for best Unicode support
- Git must be in PATH
- WSL recommended for large repositories

### macOS

- Install Xcode Command Line Tools: `xcode-select --install`
- Homebrew Python recommended

### Linux

- Install git: `sudo apt install git` (Debian/Ubuntu)
- No additional system dependencies needed

## Docker

```bash
docker build -t miie .
docker run miie --version
```

Or with docker-compose:

```bash
docker compose run miie --version
```

## Verify Installation

```bash
miie --version
miie --help
miie status
```
