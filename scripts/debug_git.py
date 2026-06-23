import subprocess
from pathlib import Path

repo_path = Path("test_output/candidate_001")
print(f"Repo path: {repo_path}")
print(f"Repo path exists: {repo_path.exists()}")

# Create the file if it doesn't exist
loc_file = repo_path / "src" / "loc.txt"
print(f"Loc file: {loc_file}")
print(f"Loc file exists: {loc_file.exists()}")
if not loc_file.exists():
    loc_file.parent.mkdir(parents=True, exist_ok=True)
    loc_file.write_text("test")

noise_file = repo_path / "src" / "noise.txt"
print(f"Noise file: {noise_file}")
print(f"Noise file exists: {noise_file.exists()}")
if not noise_file.exists():
    noise_file.parent.mkdir(parents=True, exist_ok=True)
    noise_file.write_text("test")

# Try git add
cmd = ["git", "add", str(loc_file), str(noise_file)]
print(f"Running: {cmd}")
result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)
print(f"Return code: {result.returncode}")
print(f"Stdout: {result.stdout}")
print(f"Stderr: {result.stderr}")