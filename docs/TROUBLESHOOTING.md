# Troubleshooting

## Common Issues

### "No such file or directory" when analyzing a repository

**Cause:** The repository path is invalid or the repository doesn't exist.

**Fix:**
```bash
# Check the path exists
ls -la /path/to/repo

# Make sure it's a git repository
git -C /path/to/repo status
```

### "Git clone failed" for GitHub repositories

**Cause:** Authentication failure or network issue.

**Fix:**
```bash
# Set up GitHub token
export GITHUB_TOKEN=ghp_xxxxx

# Or use the CLI flag
miie analyze https://github.com/user/repo --auth-token ghp_xxxxx
```

### "Insufficient analysis windows"

**Cause:** The repository doesn't have enough commit history for the configured window size.

**Fix:**
```bash
# Use a smaller window size
miie analyze /path/to/repo --window-size 3

# Or use a repository with more history
```

### Windows terminal shows garbled characters

**Cause:** Windows console doesn't support Unicode box-drawing characters.

**Fix:**
- Use Windows Terminal (not cmd.exe)
- Or enable UTF-8: `chcp 65001`
- Or use WSL

### "ModuleNotFoundError: No module named 'miie'"

**Cause:** MIIE is not installed or not in the Python path.

**Fix:**
```bash
# Install from source
pip install -e /path/to/miie

# Or install from PyPI
pip install miie
```

### Slow analysis on large repositories

**Cause:** Large repositories with many commits take longer to process.

**Fix:**
```bash
# Use a specific time window
miie analyze /path/to/repo --window-size 30

# Use fewer metrics
miie analyze /path/to/repo --metrics M-01

# Increase timeout (if supported)
```

### Docker: "miie: command not found"

**Cause:** Package not installed in Docker image.

**Fix:**
```bash
# Rebuild the image
docker build -t miie .

# Or use docker-compose
docker compose build
```

## Getting Help

- Check the [CLI Guide](CLI_GUIDE.md) for command reference
- See [Examples](../examples/) for runnable examples
- Open an issue at [GitHub Issues](https://github.com/Samragya013/miie/issues)
