#!/bin/bash
# Directional scanning guide to help locate source

echo "=== Directional Scanning Guide ==="
echo ""
echo "This will help you pinpoint the exact location of the signal source."
echo ""
echo "📍 Instructions:"
echo ""
echo "1. Position your HackRF antenna pointing in different directions"
echo "2. Run a scan for each direction"
echo "3. Compare signal strengths to find the strongest direction"
echo ""
echo "Directions to test:"
echo "  - North"
echo "  - South"
echo "  - East"
echo "  - West"
echo "  - Southwest (toward lightpole)"
echo "  - Northeast (toward building)"
echo "  - Up (toward top of lightpole)"
echo "  - Down (toward ground)"
echo ""

read -p "Press Enter when antenna is pointing NORTH..."
echo "Scanning North..."
hackrf_sweep -f 750:770 -f 850:860 -a 1 -l 32 -g 40 -N 50 -r detection-logs/directional/north_$(date +%Y%m%d_%H%M%S).csv
echo "✅ North scan complete"
echo ""

read -p "Press Enter when antenna is pointing SOUTH..."
echo "Scanning South..."
hackrf_sweep -f 750:770 -f 850:860 -a 1 -l 32 -g 40 -N 50 -r detection-logs/directional/south_$(date +%Y%m%d_%H%M%S).csv
echo "✅ South scan complete"
echo ""

read -p "Press Enter when antenna is pointing EAST..."
echo "Scanning East..."
hackrf_sweep -f 750:770 -f 850:860 -a 1 -l 32 -g 40 -N 50 -r detection-logs/directional/east_$(date +%Y%m%d_%H%M%S).csv
echo "✅ East scan complete"
echo ""

read -p "Press Enter when antenna is pointing WEST..."
echo "Scanning West..."
hackrf_sweep -f 750:770 -f 850:860 -a 1 -l 32 -g 40 -N 50 -r detection-logs/directional/west_$(date +%Y%m%d_%H%M%S).csv
echo "✅ West scan complete"
echo ""

read -p "Press Enter when antenna is pointing SOUTHWEST (toward lightpole)..."
echo "Scanning Southwest..."
hackrf_sweep -f 750:770 -f 850:860 -a 1 -l 32 -g 40 -N 50 -r detection-logs/directional/southwest_$(date +%Y%m%d_%H%M%S).csv
echo "✅ Southwest scan complete"
echo ""

read -p "Press Enter when antenna is pointing NORTHEAST (toward building)..."
echo "Scanning Northeast..."
hackrf_sweep -f 750:770 -f 850:860 -a 1 -l 32 -g 40 -N 50 -r detection-logs/directional/northeast_$(date +%Y%m%d_%H%M%S).csv
echo "✅ Northeast scan complete"
echo ""

read -p "Press Enter when antenna is pointing UP (toward sky/top of lightpole)..."
echo "Scanning Up..."
hackrf_sweep -f 750:770 -f 850:860 -a 1 -l 32 -g 40 -N 50 -r detection-logs/directional/up_$(date +%Y%m%d_%H%M%S).csv
echo "✅ Up scan complete"
echo ""

read -p "Press Enter when antenna is pointing DOWN (toward ground)..."
echo "Scanning Down..."
hackrf_sweep -f 750:770 -f 850:860 -a 1 -l 32 -g 40 -N 50 -r detection-logs/directional/down_$(date +%Y%m%d_%H%M%S).csv
echo "✅ Down scan complete"
echo ""

echo "=== All directional scans complete ==="
echo ""
echo "Analyzing results..."
python3 scripts/compare-directions.py detection-logs/directional/
