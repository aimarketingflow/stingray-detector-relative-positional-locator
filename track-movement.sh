#!/bin/bash
# Track signal movement over time to determine if source is mobile

DURATION_MINUTES=${1:-60}  # Default 60 minutes
INTERVAL_SECONDS=${2:-120}  # Default 2 minutes

TRACK_DIR="detection-logs/tracking"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SESSION_DIR="${TRACK_DIR}/session_${TIMESTAMP}"
LOG_FILE="${SESSION_DIR}/tracking_log.txt"
SUMMARY_FILE="${SESSION_DIR}/summary.txt"

mkdir -p "$SESSION_DIR"

echo "=== Stingray Movement Tracking ===" | tee "$LOG_FILE"
echo "Started: $(date)" | tee -a "$LOG_FILE"
echo "Duration: $DURATION_MINUTES minutes" | tee -a "$LOG_FILE"
echo "Interval: $INTERVAL_SECONDS seconds ($(($INTERVAL_SECONDS / 60)) minutes)" | tee -a "$LOG_FILE"
echo "Session: $SESSION_DIR" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Calculate number of scans
NUM_SCANS=$(( ($DURATION_MINUTES * 60) / $INTERVAL_SECONDS ))

echo "Will perform $NUM_SCANS scans" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Key frequencies to track
KEY_FREQS="851 760 761 762 763 764 765 766"

# Initialize tracking
echo "Tracking key frequencies: $KEY_FREQS MHz" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

for i in $(seq 1 $NUM_SCANS); do
    SCAN_TIME=$(date +%Y%m%d_%H%M%S)
    SCAN_FILE="${SESSION_DIR}/scan_${SCAN_TIME}.csv"
    
    echo "[$i/$NUM_SCANS] Scan at $(date +%H:%M:%S)" | tee -a "$LOG_FILE"
    
    # Run focused scan on suspicious frequencies
    hackrf_sweep \
        -f 750:770 \
        -f 850:860 \
        -a 1 \
        -l 32 \
        -g 40 \
        -N 50 \
        -r "$SCAN_FILE" \
        2>&1 | grep -E "(Total sweeps)" | tee -a "$LOG_FILE"
    
    # Quick analysis - extract power levels for key frequencies
    if [ -f "$SCAN_FILE" ]; then
        echo "  Key signal strengths:" | tee -a "$LOG_FILE"
        
        # Parse CSV and find strongest signals
        python3 - <<EOF | tee -a "$LOG_FILE"
import csv
from collections import defaultdict

freq_data = defaultdict(list)

with open("$SCAN_FILE", 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) < 6:
            continue
        try:
            hz_low = int(row[2])
            hz_bin_width = float(row[4])
            power_readings = [float(x) for x in row[6:] if x]
            
            for idx, power in enumerate(power_readings):
                freq = hz_low + (idx * hz_bin_width)
                freq_data[freq].append(power)
        except:
            continue

# Average and find key frequencies
freq_avg = {f: sum(p)/len(p) for f, p in freq_data.items()}

# Check key frequencies
key_freqs = [851e6, 760e6, 761e6, 762e6, 763e6, 764e6, 765e6, 766e6]
for key_freq in key_freqs:
    # Find closest frequency in data
    closest = min(freq_avg.keys(), key=lambda x: abs(x - key_freq))
    if abs(closest - key_freq) < 1e6:  # Within 1 MHz
        print(f"    {closest/1e6:.1f} MHz: {freq_avg[closest]:.2f} dBm")
EOF
        
        echo "" | tee -a "$LOG_FILE"
    else
        echo "  ❌ Scan failed!" | tee -a "$LOG_FILE"
    fi
    
    # Wait for next scan (unless last scan)
    if [ $i -lt $NUM_SCANS ]; then
        echo "  Waiting $INTERVAL_SECONDS seconds until next scan..." | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
        sleep $INTERVAL_SECONDS
    fi
done

echo "" | tee -a "$LOG_FILE"
echo "=== Tracking Complete ===" | tee -a "$LOG_FILE"
echo "Completed: $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Generate summary
echo "Generating movement analysis..." | tee -a "$LOG_FILE"
python3 scripts/analyze-movement.py "$SESSION_DIR" | tee "$SUMMARY_FILE"

echo "" | tee -a "$LOG_FILE"
echo "Summary saved to: $SUMMARY_FILE" | tee -a "$LOG_FILE"
echo "All scans saved to: $SESSION_DIR" | tee -a "$LOG_FILE"
