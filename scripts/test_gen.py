import sys
import shutil
sys.path.insert(0, 'src')
from src.miie.benchmark.generator import BenchmarkDatasetGenerator
from pathlib import Path

print("Cleaning up test output directory...")
output_dir = Path("test_output")
if output_dir.exists():
    print(f"Removing existing {output_dir}")
    shutil.rmtree(output_dir)
else:
    print(f"{output_dir} does not exist")

print("Creating BenchmarkDatasetGenerator...")
generator = BenchmarkDatasetGenerator()

output_dir = Path("test_output")
print(f"Output directory exists before generation: {output_dir.exists()}")
if output_dir.exists():
    print(f"Contents of {output_dir}: {list(output_dir.iterdir())}")

print("Generating 1 candidate...")
paths = generator.generate("metric-drift", 1, output_dir, seed=42)
print(f"Generated {len(paths)} candidates")
print(f"Path: {paths[0]}")
print("Checking if it's a git repo...")
import subprocess
result = subprocess.run(["git", "status"], cwd=paths[0], capture_output=True, text=True)
print(f"Git status return code: {result.returncode}")
if result.returncode == 0:
    print("Git status succeeded")
else:
    print(f"Git status failed: {result.stderr}")