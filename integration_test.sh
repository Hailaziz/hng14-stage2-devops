#!/bin/bash
set -e

echo "Starting integration test..."

# Wait for frontend to be ready
MAX_WAIT=60
WAITED=0
until curl -sf http://localhost:3000/health > /dev/null; do
    if [ $WAITED -ge $MAX_WAIT ]; then
        echo "Timeout waiting for frontend"
        exit 1
    fi
    echo "Waiting for frontend... ($WAITED s)"
    sleep 2
    WAITED=$((WAITED + 2))
done
echo "Frontend is ready"

# Submit a job
RESPONSE=$(curl -sf -X POST http://localhost:3000/submit)
JOB_ID=$(echo $RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin)['job_id'])")
echo "Submitted job: $JOB_ID"

# Poll for completion
MAX_WAIT=60
WAITED=0
while true; do
    if [ $WAITED -ge $MAX_WAIT ]; then
        echo "Timeout waiting for job completion"
        exit 1
    fi
    STATUS=$(curl -sf http://localhost:3000/status/$JOB_ID | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))")
    echo "Job status: $STATUS ($WAITED s)"
    if [ "$STATUS" = "completed" ]; then
        echo "Integration test PASSED"
        exit 0
    fi
    sleep 2
    WAITED=$((WAITED + 2))
done
