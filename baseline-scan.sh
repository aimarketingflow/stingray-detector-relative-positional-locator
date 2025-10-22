#!/bin/bash
# Establish baseline of legitimate cell towers

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="detection-logs/baseline"
SCAN_FILE="${OUTPUT_DIR}/scan_${TIMESTAMP}.csv"
LOG_FILE="${OUTPUT_DIR}/scan_${TIMESTAMP}.log"

echo "=== Baseline Cell Tower Scan ===" | tee "$LOG_FILE"
echo "Started: $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Cellular frequency bands to scan
# GSM-850: 869-894 MHz (uplink)
# GSM-900: 925-960 MHz (uplink)  
# GSM-1800: 1805-1880 MHz (uplink)
# GSM-1900: 1930-1990 MHz (uplink)
# LTE Band 12: 729-746 MHz (uplink)
# LTE Band 13: 746-756 MHz (uplink)
# LTE Band 17: 704-716 MHz (uplink)
# LTE Band 2: 1850-1910 MHz (uplink)
# LTE Band 4: 1710-1755 MHz (uplink)

echo "📡 Scanning cellular frequency bands..." | tee -a "$LOG_FILE"
echo "This will take approximately 2-3 minutes..." | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Comprehensive scan of cellular bands
hackrf_sweep \
    -f 700:960 \
    -f 1710:1990 \
    -N 100 \
    -r "$SCAN_FILE" \
    2>&1 | tee -a "$LOG_FILE"

if [ -f "$SCAN_FILE" ]; then
    lines=$(wc -l < "$SCAN_FILE")
    size=$(du -h "$SCAN_FILE" | cut -f1)
    echo "" | tee -a "$LOG_FILE"
    echo "✅ Scan complete!" | tee -a "$LOG_FILE"
    echo "   Data points: $lines" | tee -a "$LOG_FILE"
    echo "   File size: $size" | tee -a "$LOG_FILE"
    echo "   Saved to: $SCAN_FILE" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    echo "Next steps:" | tee -a "$LOG_FILE"
    echo "1. Run this scan multiple times at different times of day" | tee -a "$LOG_FILE"
    echo "2. Use python3 scripts/analyze-spectrum.py to analyze results" | tee -a "$LOG_FILE"
    echo "3. Compare future scans against this baseline" | tee -a "$LOG_FILE"
else
    echo "❌ Scan failed!" | tee -a "$LOG_FILE"
    exit 1
fi

echo "" | tee -a "$LOG_FILE"
echo "Completed: $(date)" | tee -a "$LOG_FILE"
