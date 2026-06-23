import subprocess
from pathlib import Path
import shutil

# Clean up
test_dir = Path("debug_test")
if test_dir.exists():
    shutil.rmtree(test_dir)
test_dir.mkdir()

# Initialize git repo
print("Initializing git repo...")
subprocess.run(["git", "init"], cwd=test_dir, check=True, capture_output=True)
print("Setting user name and email...")
subprocess.run(["git", "config", "user.name", "MIIE Generator"], cwd=test_dir, check=True, capture_output=True)
subprocess.run(["git", "config", "user.email", "miie@example.com"], cwd=test_dir, check=True, capture_output=True)

# Create files
(readme := test_dir / "README.md").write_text("# Test\n")
(src_dir := test_dir / "src").mkdir()
(main_py := src_dir / "main.py").write_text("# Main\n")
(tests_dir := test_dir / "tests").mkdir()
(test_main_py := tests_dir / "test_main.py").write_text("# Test\n")

print("Files created:")
print(f"  {readme.exists()}")
print(f"  {main_py.exists()}")
print(f"  {test_main_py.exists()}")

# Try to add and commit
print("Adding files...")
result_add = subprocess.run(
    ["git", "add", "README.md", "src/main.py", "tests/test_main.py"],
    cwd=test_dir,
    capture_output=True,
    text=True
)
print(f"Add return code: {result_add.returncode}")
print(f"Add stdout: {result_add.stdout}")
print(f"Add stderr: {result_add.stderr}")

print("Committing...")
result_commit = subprocess.run(
    ["git", "commit", "-m", "Initial commit"],
    cwd=test_dir,
    capture_output=True,
    text=True
)
print(f"Commit return code: {result_commit.returncode}")
print(f"Commit stdout: {result_commit.stdout}")
print(f"Commit stderr: {result_commit.stderr}")

# Check status
print("Status:")
result_status = subprocess.run(
    ["git", "status"],
    cwd=test_dir,
    capture_output=True,
    text=True
)
print(result_status.stdout)