#!/bin/bash
# Test HackRF One functionality

echo "=== HackRF One Hardware Test ==="
echo ""

# Check if HackRF is connected
echo "1. Checking HackRF connection..."
if ! hackrf_info &>/dev/null; then
    echo "❌ HackRF not detected!"
    echo "   - Check USB connection"
    echo "   - Try: sudo killall hackrf_*"
    echo "   - Reconnect device"
    exit 1
fi

echo "✅ HackRF connected"
echo ""

# Display device info
echo "2. Device Information:"
hackrf_info
echo ""

# Quick spectrum sweep test
echo "3. Running quick spectrum test..."
echo "   Scanning GSM-900 band (925-960 MHz)..."
hackrf_sweep -f 925:960 -N 10 -r test_sweep.csv 2>&1 | head -n 10

if [ -f test_sweep.csv ]; then
    lines=$(wc -l < test_sweep.csv)
    echo "✅ Sweep successful! Captured $lines data points"
    rm test_sweep.csv
else
    echo "❌ Sweep failed"
    exit 1
fi

echo ""
echo "=== Hardware Test Complete ==="
echo "✅ HackRF One is working correctly!"
echo ""
echo "Next: Run ./baseline-scan.sh to scan for cell towers"
