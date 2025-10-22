#!/bin/bash
# Quick check for suspicious activity - compares against latest baseline

echo "=== Quick Stingray Check ==="
echo ""

# Find the most recent baseline scan
BASELINE=$(ls -t detection-logs/baseline/scan_*.csv | head -n 1)

if [ -z "$BASELINE" ]; then
    echo "❌ No baseline found. Run ./baseline-scan-boosted.sh first"
    exit 1
fi

echo "📊 Using baseline: $(basename $BASELINE)"
echo ""

# Run new scan
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SCAN_FILE="detection-logs/incidents/check_${TIMESTAMP}.csv"

mkdir -p detection-logs/incidents

echo "📡 Scanning..."

# Check if HackRF is accessible
if ! hackrf_info &>/dev/null; then
    echo "⚠️  HackRF access issue. Trying to reset..."
    sudo killall hackrf_sweep hackrf_info 2>/dev/null
    sleep 1
fi

hackrf_sweep \
    -f 700:960 \
    -f 1710:1990 \
    -a 1 \
    -l 32 \
    -g 40 \
    -N 100 \
    -r "$SCAN_FILE"

# Wait for file to be fully written
sleep 1

echo ""
echo "🔍 Analyzing for threats..."
echo ""

# Verify scan file exists
if [ ! -f "$SCAN_FILE" ]; then
    echo "❌ Scan failed - no data file created"
    exit 1
fi

# Compare against baseline
python3 scripts/compare-scans.py "$BASELINE" "$SCAN_FILE" -50

echo ""
echo "Scan saved to: $SCAN_FILE"
