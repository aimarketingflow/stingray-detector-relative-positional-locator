#!/bin/bash
# Daily monitoring script for ongoing Stingray surveillance documentation

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATE_READABLE=$(date "+%B %d, %Y at %I:%M %p")
DAILY_DIR="detection-logs/daily/$(date +%Y%m%d)"

mkdir -p "$DAILY_DIR"

echo "==================================="
echo "Daily Stingray Monitoring"
echo "$DATE_READABLE"
echo "==================================="
echo ""

# Quick scan of suspicious frequencies
echo "📡 Scanning suspicious frequencies..."
hackrf_sweep \
    -f 750:770 \
    -f 850:860 \
    -a 1 \
    -l 32 \
    -g 40 \
    -N 100 \
    -r "${DAILY_DIR}/scan_${TIMESTAMP}.csv"

echo ""
echo "🔍 Analyzing results..."
echo ""

# Analyze the scan
python3 scripts/detailed-analysis.py "${DAILY_DIR}/scan_${TIMESTAMP}.csv" 750 870

# Compare to baseline
echo ""
echo "📊 Comparing to baseline..."
echo ""

BASELINE=$(ls -t detection-logs/baseline/*.csv | head -n 1)
python3 scripts/compare-scans.py "$BASELINE" "${DAILY_DIR}/scan_${TIMESTAMP}.csv" -50

# Log summary
echo ""
echo "✅ Daily scan complete"
echo "Data saved to: ${DAILY_DIR}/scan_${TIMESTAMP}.csv"
echo ""

# Create daily summary
cat > "${DAILY_DIR}/summary_$(date +%Y%m%d).txt" <<EOF
Daily Monitoring Summary
Date: $DATE_READABLE
Scan file: scan_${TIMESTAMP}.csv

Status: Scan completed successfully
Location: ${DAILY_DIR}/

Next steps:
- Review detailed analysis above
- Compare signal patterns to previous days
- Document any changes in signal strength or behavior
- Note any physical observations (vehicles, people, changes to device)

Evidence collection day: $(find detection-logs/daily -type d -name "202*" | wc -l)
EOF

echo "Summary saved to: ${DAILY_DIR}/summary_$(date +%Y%m%d).txt"
