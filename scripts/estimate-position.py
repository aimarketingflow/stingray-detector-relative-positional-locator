#!/usr/bin/env python3
"""
Estimate 3D position of signal source using directional scan data
Uses Free Space Path Loss (FSPL) model and signal strength
"""

import sys
import os
import csv
import glob
import math
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
    
    # Return average across all frequencies
    if results:
        return sum(results.values()) / len(results)
    return None

def estimate_distance(power_dbm, freq_mhz=760, tx_power_dbm=20):
    """
    Estimate distance using Free Space Path Loss (FSPL)
    
    FSPL (dB) = 20*log10(d) + 20*log10(f) + 32.45
    where d is distance in km, f is frequency in MHz
    
    Path Loss = TX_power - RX_power
    """
    
    # Received power
    rx_power = power_dbm
    
    # Path loss
    path_loss = tx_power_dbm - rx_power
    
    # Solve for distance
    # path_loss = 20*log10(d_km) + 20*log10(f_MHz) + 32.45
    # 20*log10(d_km) = path_loss - 20*log10(f_MHz) - 32.45
    # log10(d_km) = (path_loss - 20*log10(f_MHz) - 32.45) / 20
    # d_km = 10^((path_loss - 20*log10(f_MHz) - 32.45) / 20)
    
    freq_term = 20 * math.log10(freq_mhz)
    log_d_km = (path_loss - freq_term - 32.45) / 20
    d_km = 10 ** log_d_km
    d_meters = d_km * 1000
    d_feet = d_meters * 3.28084
    
    return d_meters, d_feet

def estimate_position(directory, antenna_height_ft=2.5):
    """
    Estimate 3D position of signal source from directional scans
    """
    
    print("\n=== Signal Source Position Estimation ===\n")
    print(f"Antenna height: {antenna_height_ft:.1f} feet above ground\n")
    
    # Load all directional scans
    directions = {
        'north': 0,      # degrees
        'northeast': 45,
        'east': 90,
        'south': 180,
        'southwest': 225,
        'west': 270,
        'up': None,      # elevation
        'down': None
    }
    
    scan_data = {}
    
    for direction in directions.keys():
        files = glob.glob(f"{directory}/{direction}_*.csv")
        if files:
            latest = max(files, key=os.path.getctime)
            power = load_scan(latest)
            if power:
                scan_data[direction] = power
                print(f"✅ {direction.upper():<12} {power:.2f} dBm")
    
    if len(scan_data) < 4:
        print("\n❌ Need at least 4 directional scans for position estimation")
        return
    
    print()
    
    # Find strongest horizontal direction
    horizontal_dirs = ['north', 'south', 'east', 'west', 'northeast', 'southwest']
    horizontal_data = {d: p for d, p in scan_data.items() if d in horizontal_dirs}
    
    if not horizontal_data:
        print("❌ No horizontal directional data")
        return
    
    strongest_dir = max(horizontal_data.items(), key=lambda x: x[1])
    strongest_power = strongest_dir[1]
    
    print(f"🎯 Strongest horizontal direction: {strongest_dir[0].upper()} ({strongest_power:.2f} dBm)")
    print()
    
    # Estimate distance using different TX power assumptions
    print("📏 Distance Estimation (using Free Space Path Loss):\n")
    
    tx_powers = [10, 20, 30, 40]  # Typical Stingray power levels
    
    print(f"{'TX Power':<12} {'Distance (m)':<15} {'Distance (ft)':<15}")
    print("-" * 45)
    
    estimated_distances = []
    for tx_power in tx_powers:
        d_m, d_ft = estimate_distance(strongest_power, freq_mhz=760, tx_power_dbm=tx_power)
        estimated_distances.append((tx_power, d_m, d_ft))
        print(f"{tx_power} dBm{'':<6} {d_m:<15.1f} {d_ft:<15.1f}")
    
    print()
    print("💡 Most likely scenario (20-30 dBm TX power for portable Stingray):")
    
    # Use 25 dBm as typical
    d_m, d_ft = estimate_distance(strongest_power, freq_mhz=760, tx_power_dbm=25)
    print(f"   Estimated distance: {d_m:.1f} meters ({d_ft:.1f} feet)")
    print()
    
    # Determine vertical position
    vertical_estimate = "unknown"
    vertical_offset_ft = 0
    
    if 'up' in scan_data and 'down' in scan_data:
        up_power = scan_data['up']
        down_power = scan_data['down']
        diff = down_power - up_power
        
        print(f"📐 Vertical Analysis:")
        print(f"   UP signal:   {up_power:.2f} dBm")
        print(f"   DOWN signal: {down_power:.2f} dBm")
        print(f"   Difference:  {diff:+.2f} dB")
        print()
        
        if diff > 3:
            vertical_estimate = "below antenna"
            # Rough estimate: 6 dB = factor of 2 in distance
            # If down is 3-6 dB stronger, source is significantly below
            if diff > 6:
                print(f"   ✅ Source is WELL BELOW antenna level")
                print(f"   → Estimated: 4-8 feet below antenna")
                vertical_offset_ft = -6
            else:
                print(f"   ✅ Source is BELOW antenna level")
                print(f"   → Estimated: 2-4 feet below antenna")
                vertical_offset_ft = -3
        elif diff < -3:
            vertical_estimate = "above antenna"
            print(f"   ✅ Source is ABOVE antenna level")
            vertical_offset_ft = 3
        else:
            vertical_estimate = "at antenna level"
            print(f"   ✅ Source is approximately at antenna level")
            vertical_offset_ft = 0
        
        print()
    
    # Calculate 3D position
    print("🎯 Estimated 3D Position from Your Antenna:\n")
    
    # Horizontal components based on strongest direction
    angle = directions.get(strongest_dir[0], 0)
    
    if angle is not None:
        # Convert to radians
        angle_rad = math.radians(angle)
        
        # Calculate horizontal offsets
        # North = 0°, East = 90°, South = 180°, West = 270°
        east_offset_ft = d_ft * math.sin(angle_rad)
        north_offset_ft = d_ft * math.cos(angle_rad)
        south_offset_ft = -north_offset_ft
        west_offset_ft = -east_offset_ft
        
        print(f"   Horizontal distance: {d_ft:.1f} feet")
        print(f"   Direction: {strongest_dir[0].upper()} ({angle}°)")
        print()
        print(f"   Offset breakdown:")
        
        if abs(north_offset_ft) > 1:
            if north_offset_ft > 0:
                print(f"      North: {north_offset_ft:.1f} feet")
            else:
                print(f"      South: {abs(north_offset_ft):.1f} feet")
        
        if abs(east_offset_ft) > 1:
            if east_offset_ft > 0:
                print(f"      East:  {east_offset_ft:.1f} feet")
            else:
                print(f"      West:  {abs(east_offset_ft):.1f} feet")
        
        print(f"      Vertical: {vertical_offset_ft:+.1f} feet (relative to antenna)")
        print()
        
        # Absolute height
        source_height_ft = antenna_height_ft + vertical_offset_ft
        print(f"   Estimated height above ground: {source_height_ft:.1f} feet")
        print()
        
        # Summary
        print("📍 SUMMARY:")
        print(f"   From your antenna position, the signal source is approximately:")
        print()
        
        if north_offset_ft > 0:
            print(f"   • {abs(north_offset_ft):.0f} feet NORTH")
        elif north_offset_ft < 0:
            print(f"   • {abs(north_offset_ft):.0f} feet SOUTH")
        
        if east_offset_ft > 0:
            print(f"   • {abs(east_offset_ft):.0f} feet EAST")
        elif east_offset_ft < 0:
            print(f"   • {abs(east_offset_ft):.0f} feet WEST")
        
        print(f"   • {abs(vertical_offset_ft):.0f} feet {'BELOW' if vertical_offset_ft < 0 else 'ABOVE'} antenna")
        print()
        print(f"   Height above ground: ~{source_height_ft:.0f} feet")
        print()
        
        # Confidence assessment
        print("⚠️  Accuracy Notes:")
        print("   • Distance estimates assume free space propagation")
        print("   • Actual distance may be shorter due to reflections/multipath")
        print("   • Indoor obstacles reduce accuracy")
        print("   • Typical accuracy: ±30-50% for distance")
        print("   • Direction is more reliable than distance")
        print()
        
        if source_height_ft < 3:
            print("   💡 Low height suggests ground-level installation")
            print("      → Utility box, base of lightpole, or ground-mounted equipment")
        elif source_height_ft < 10:
            print("   💡 Mid-height suggests pole-mounted equipment")
            print("      → Mid-section of lightpole or building-mounted")
        else:
            print("   💡 High elevation suggests rooftop or top of pole")
            print("      → Top of lightpole, rooftop, or elevated structure")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 estimate-position.py <directional_scan_directory> [antenna_height_ft]")
        print("\nExample:")
        print("  python3 estimate-position.py detection-logs/directional/")
        print("  python3 estimate-position.py detection-logs/directional/ 3.0")
        sys.exit(1)
    
    directory = sys.argv[1]
    antenna_height = float(sys.argv[2]) if len(sys.argv) > 2 else 2.5
    
    estimate_position(directory, antenna_height)
