#!/usr/bin/env python3
"""
Analyze signal movement over time to determine if source is mobile
"""

import sys
import os
import csv
import glob
from collections import defaultdict
from datetime import datetime

def analyze_movement(session_dir):
    """Analyze all scans in a session to detect movement"""
    
    print(f"\n=== Movement Analysis ===")
    print(f"Session: {session_dir}\n")
    
    # Find all scan files
    scan_files = sorted(glob.glob(f"{session_dir}/scan_*.csv"))
    
    if len(scan_files) < 2:
        print("❌ Need at least 2 scans to analyze movement")
        return
    
    print(f"Analyzing {len(scan_files)} scans...\n")
    
    # Key frequencies to track
    key_freqs = [851e6, 760e6, 761e6, 762e6, 763e6, 764e6, 765e6, 766e6]
    
    # Track power over time for each frequency
    timeline = []
    
    for scan_file in scan_files:
        # Extract timestamp from filename
        basename = os.path.basename(scan_file)
        timestamp_str = basename.replace('scan_', '').replace('.csv', '')
        try:
            timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
        except:
            timestamp = None
        
        # Load scan data
        freq_data = defaultdict(list)
        
        with open(scan_file, 'r') as f:
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
        
        # Average power for each frequency
        freq_avg = {f: sum(p)/len(p) for f, p in freq_data.items()}
        
        # Extract key frequencies
        scan_data = {'timestamp': timestamp, 'file': basename}
        for key_freq in key_freqs:
            closest = min(freq_avg.keys(), key=lambda x: abs(x - key_freq))
            if abs(closest - key_freq) < 1e6:  # Within 1 MHz
                scan_data[f"{key_freq/1e6:.0f}"] = freq_avg[closest]
        
        timeline.append(scan_data)
    
    # Display timeline
    print("📊 Signal Strength Timeline:\n")
    print(f"{'Time':<12} {'851 MHz':<12} {'760 MHz':<12} {'763 MHz':<12} {'766 MHz':<12}")
    print("-" * 60)
    
    for scan in timeline:
        time_str = scan['timestamp'].strftime('%H:%M:%S') if scan['timestamp'] else 'Unknown'
        s851 = f"{scan.get('851', 0):.2f}" if '851' in scan else "N/A"
        s760 = f"{scan.get('760', 0):.2f}" if '760' in scan else "N/A"
        s763 = f"{scan.get('763', 0):.2f}" if '763' in scan else "N/A"
        s766 = f"{scan.get('766', 0):.2f}" if '766' in scan else "N/A"
        
        print(f"{time_str:<12} {s851:<12} {s760:<12} {s763:<12} {s766:<12}")
    
    print()
    
    # Analyze trends
    print("🔍 Movement Analysis:\n")
    
    # Check for signal strength changes
    for freq_label in ['851', '760', '763', '766']:
        values = [s.get(freq_label) for s in timeline if freq_label in s]
        
        if len(values) < 2:
            continue
        
        first_val = values[0]
        last_val = values[-1]
        max_val = max(values)
        min_val = min(values)
        avg_val = sum(values) / len(values)
        change = last_val - first_val
        variation = max_val - min_val
        
        print(f"{freq_label} MHz:")
        print(f"  First: {first_val:.2f} dBm")
        print(f"  Last:  {last_val:.2f} dBm")
        print(f"  Change: {change:+.2f} dB")
        print(f"  Variation: {variation:.2f} dB (max-min)")
        print(f"  Average: {avg_val:.2f} dBm")
        
        # Interpret
        if abs(change) > 5:
            if change > 0:
                print(f"  ⚠️  SIGNAL GETTING STRONGER (source moving closer)")
            else:
                print(f"  ⚠️  SIGNAL GETTING WEAKER (source moving away)")
        elif variation > 3:
            print(f"  ⚠️  SIGNAL FLUCTUATING (possible mobile source)")
        else:
            print(f"  ✅ SIGNAL STABLE (likely stationary)")
        
        print()
    
    # Overall assessment
    print("📍 Location Assessment:")
    
    # Check if all signals are stable
    all_stable = True
    any_moving = False
    
    for freq_label in ['851', '760', '763', '766']:
        values = [s.get(freq_label) for s in timeline if freq_label in s]
        if len(values) >= 2:
            variation = max(values) - min(values)
            change = values[-1] - values[0]
            
            if variation > 3 or abs(change) > 5:
                all_stable = False
            if abs(change) > 5:
                any_moving = True
    
    if all_stable:
        print("  ✅ All signals STABLE")
        print("  → Source is likely STATIONARY (e.g., fixed installation)")
        print("  → Consistent with lightpole/building installation")
    elif any_moving:
        print("  ⚠️  Signals showing DIRECTIONAL CHANGE")
        print("  → Source may be MOBILE (e.g., vehicle)")
        print("  → Monitor for continued movement pattern")
    else:
        print("  ⚠️  Signals FLUCTUATING")
        print("  → Could be environmental factors or mobile source")
        print("  → Continue monitoring")
    
    print()
    print(f"Total monitoring time: {len(scan_files)} scans")
    if timeline[0]['timestamp'] and timeline[-1]['timestamp']:
        duration = timeline[-1]['timestamp'] - timeline[0]['timestamp']
        print(f"Duration: {duration}")
    
    print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 analyze-movement.py <session_directory>")
        sys.exit(1)
    
    analyze_movement(sys.argv[1])
