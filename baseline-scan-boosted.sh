#!/bin/bash
# Baseline scan with amplifier and gain enabled for better reception

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="detection-logs/baseline"
SCAN_FILE="${OUTPUT_DIR}/scan_${TIMESTAMP}.csv"
LOG_FILE="${OUTPUT_DIR}/scan_${TIMESTAMP}.log"

echo "=== Baseline Cell Tower Scan (Boosted) ===" | tee "$LOG_FILE"
echo "Started: $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

mkdir -p "$OUTPUT_DIR"

echo "📡 Scanning with amplifier and gain enabled..." | tee -a "$LOG_FILE"
echo "This will take approximately 2-3 minutes..." | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Scan with amplifier and gain
# -a 1: Enable RX RF amplifier
# -l 32: RX LNA gain 32dB
# -g 40: RX VGA gain 40dB
hackrf_sweep \
    -f 700:960 \
    -f 1710:1990 \
    -a 1 \
    -l 32 \
    -g 40 \
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
    echo "Analyzing results..." | tee -a "$LOG_FILE"
    python3 scripts/analyze-spectrum.py "$SCAN_FILE" | tee -a "$LOG_FILE"
else
    echo "❌ Scan failed!" | tee -a "$LOG_FILE"
    exit 1
fi

echo "" | tee -a "$LOG_FILE"
echo "Completed: $(date)" | tee -a "$LOG_FILE"
