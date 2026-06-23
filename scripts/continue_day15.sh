#!/bin/bash

# Script to continue Day 15 implementation and check for completion

echo "Running D02 Correlation Breakdown Detector unit tests..."
python -m pytest tests/unit/test_d02_correlation_breakdown.py -v
TEST_RESULT=$?

if [ $TEST_RESULT -ne 0 ]; then
    echo "D02 unit tests failed. Fixing needed."
    exit 1
fi

echo "D02 unit tests passed."

echo "Running dry-run pipeline to verify integration..."
python -m miie analyze --dry-run --repo . --output ./test_output_dryrun --seed 42
PIPELINE_RESULT=$?

if [ $PIPELINE_RESULT -ne 0 ]; then
    echo "Dry-run pipeline failed. Integration issues."
    exit 1
fi

echo "Dry-run pipeline succeeded."

# Check if the evidence.json was generated and has the expected structure
if [ -f "./test_output_dryrun/evidence.json" ]; then
    echo "Evidence generated. Checking for D-02 outputs..."
    # We can do a simple check for the presence of D-02 in the evidence
    if grep -q '"D-02"' "./test_output_dryrun/evidence.json"; then
        echo "D-02 detected in evidence. Day 15 implementation appears complete."
        exit 0
    else
        echo "D-02 not found in evidence. Implementation may be incomplete."
        exit 1
    fi
else
    echo "Evidence not generated. Something is wrong."
    exit 1
fi