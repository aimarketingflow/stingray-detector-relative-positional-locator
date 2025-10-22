#!/usr/bin/env python3
"""
Compare directional scans to determine signal source location
"""

import sys
import os
import csv
import glob
from collections import defaultdict

def load_scan(filename):
    """Load scan and return average power for key frequencies"""
    freq_data = defaultdict(list)
    
    with open(filename, 'r') as f:
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
    
    # Average for key frequencies
    key_freqs = [851e6, 760e6, 763e6, 766e6]
    results = {}
    
    for key_freq in key_freqs:
        closest = min(freq_data.keys(), key=lambda x: abs(x - key_freq))
        if abs(closest - key_freq) < 1e6:
            powers = freq_data[closest]
            results[f"{key_freq/1e6:.0f}"] = sum(powers) / len(powers)
    
    return results

def compare_directions(directory):
    """Compare all directional scans"""
    
    print("\n=== Directional Scan Comparison ===\n")
    
    # Find all directional scans
    directions = ['north', 'south', 'east', 'west', 'southwest', 'northeast', 'up', 'down']
    results = {}
    
    for direction in directions:
        files = glob.glob(f"{directory}/{direction}_*.csv")
        if files:
            # Use most recent
            latest = max(files, key=os.path.getctime)
            results[direction] = load_scan(latest)
            print(f"✅ Loaded {direction}: {os.path.basename(latest)}")
        else:
            print(f"⚠️  No scan found for {direction}")
    
    if len(results) < 2:
        print("\n❌ Need at least 2 directional scans to compare")
        return
    
    print("\n📊 Signal Strength by Direction:\n")
    print(f"{'Direction':<12} {'851 MHz':<12} {'760 MHz':<12} {'763 MHz':<12} {'766 MHz':<12} {'Average':<12}")
    print("-" * 80)
    
    averages = {}
    for direction, powers in results.items():
        avg = sum(powers.values()) / len(powers) if powers else 0
        averages[direction] = avg
        
        s851 = f"{powers.get('851', 0):.2f}" if '851' in powers else "N/A"
        s760 = f"{powers.get('760', 0):.2f}" if '760' in powers else "N/A"
        s763 = f"{powers.get('763', 0):.2f}" if '763' in powers else "N/A"
        s766 = f"{powers.get('766', 0):.2f}" if '766' in powers else "N/A"
        
        print(f"{direction.upper():<12} {s851:<12} {s760:<12} {s763:<12} {s766:<12} {avg:<12.2f}")
    
    print()
    
    # Find strongest direction
    if averages:
        strongest = max(averages.items(), key=lambda x: x[1])
        weakest = min(averages.items(), key=lambda x: x[1])
        
        print(f"🎯 Strongest signal: {strongest[0].upper()} ({strongest[1]:.2f} dBm)")
        print(f"📉 Weakest signal: {weakest[0].upper()} ({weakest[1]:.2f} dBm)")
        print(f"📊 Difference: {strongest[1] - weakest[1]:.2f} dB")
        print()
        
        # Interpret results
        print("💡 Location Analysis:")
        print()
        
        if strongest[0] == 'southwest':
            print("  ✅ Strongest signal to SOUTHWEST")
            print("  → Source is SOUTHWEST of your position")
            print("  → ✅ CONSISTENT WITH LIGHTPOLE LOCATION!")
        elif strongest[0] == 'northeast':
            print("  ⚠️  Strongest signal to NORTHEAST")
            print("  → Source may be northeast, OR")
            print("  → Strong reflection from building to northeast")
        elif strongest[0] == 'north':
            print("  ✅ Strongest signal to NORTH")
            print("  → Source is likely NORTH of your position")
        elif strongest[0] == 'south':
            print("  ⚠️  Strongest signal to SOUTH")
            print("  → Source is likely SOUTH of your position")
        elif strongest[0] == 'up':
            print("  ✅ Strongest signal UPWARD")
            print("  → Source is elevated (top of lightpole, building, etc.)")
            print("  → Consistent with elevated installation")
        elif strongest[0] == 'down':
            print("  ⚠️  Strongest signal DOWNWARD")
            print("  → Source may be at ground level or underground")
        
        print()
        
        # Check for reflection pattern
        if 'north' in averages and 'south' in averages:
            north_south_diff = abs(averages['north'] - averages['south'])
            if north_south_diff < 3:
                print("  ⚠️  North and South signals similar strength")
                print("  → Strong reflection from building creating multipath")
                print("  → Source likely at lightpole with building reflecting")
            elif averages['north'] > averages['south']:
                print("  ✅ North significantly stronger than South")
                print("  → Direct path to north dominates")
                print("  → Source is to the NORTH (lightpole)")
            else:
                print("  ⚠️  South stronger than North")
                print("  → May indicate reflection dominance or source to south")
        
        print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 compare-directions.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    if not os.path.isdir(directory):
        os.makedirs(directory)
    
    compare_directions(directory)
