#!/usr/bin/env python3
"""
Analyze HackRF spectrum sweep data to identify cell towers
"""

import sys
import csv
from collections import defaultdict
from datetime import datetime

def analyze_sweep(filename):
    """Analyze a hackrf_sweep CSV file"""
    
    print(f"\n=== Analyzing {filename} ===\n")
    
    # Data structure: freq -> [power readings]
    freq_data = defaultdict(list)
    
    # Read CSV file
    try:
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 6:
                    continue
                    
                # hackrf_sweep format: date, time, hz_low, hz_high, hz_bin_width, num_samples, dB, dB, ...
                try:
                    hz_low = int(row[2])
                    hz_high = int(row[3])
                    hz_bin_width = float(row[4])
                    
                    # Parse power readings (dB values)
                    power_readings = [float(x) for x in row[6:] if x]
                    
                    # Calculate frequency for each bin
                    for i, power in enumerate(power_readings):
                        freq = hz_low + (i * hz_bin_width)
                        freq_data[freq].append(power)
                        
                except (ValueError, IndexError):
                    continue
                    
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        sys.exit(1)
    
    if not freq_data:
        print("❌ No valid data found in file")
        sys.exit(1)
    
    # Calculate average power for each frequency
    freq_avg = {}
    for freq, powers in freq_data.items():
        freq_avg[freq] = sum(powers) / len(powers)
    
    # Find strong signals (potential cell towers)
    # Threshold: -60 dBm or higher (strong signal)
    threshold = -60
    strong_signals = [(freq, power) for freq, power in freq_avg.items() if power > threshold]
    strong_signals.sort(key=lambda x: x[1], reverse=True)
    
    print(f"📊 Statistics:")
    print(f"   Total frequency bins: {len(freq_data)}")
    print(f"   Frequency range: {min(freq_data.keys())/1e6:.2f} - {max(freq_data.keys())/1e6:.2f} MHz")
    print(f"   Strong signals (>{threshold} dBm): {len(strong_signals)}")
    print()
    
    # Display top signals
    print(f"🔝 Top 20 Strongest Signals:")
    print(f"{'Frequency (MHz)':<20} {'Power (dBm)':<15} {'Band':<20}")
    print("-" * 60)
    
    for freq, power in strong_signals[:20]:
        freq_mhz = freq / 1e6
        band = identify_band(freq)
        print(f"{freq_mhz:<20.3f} {power:<15.2f} {band:<20}")
    
    print()
    
    # Group by cellular band
    band_signals = defaultdict(list)
    for freq, power in strong_signals:
        band = identify_band(freq)
        if "GSM" in band or "LTE" in band or "5G" in band:
            band_signals[band].append((freq, power))
    
    print(f"📱 Signals by Cellular Band:")
    for band, signals in sorted(band_signals.items()):
        print(f"   {band}: {len(signals)} signals")
    
    print()
    print("💡 Next Steps:")
    print("   1. Note the strongest frequencies - these are likely legitimate towers")
    print("   2. Run this scan multiple times to establish baseline")
    print("   3. Compare future scans to detect new/disappearing signals")
    print("   4. Use GQRX to visually inspect suspicious frequencies")
    print()

def identify_band(freq_hz):
    """Identify cellular band from frequency"""
    freq_mhz = freq_hz / 1e6
    
    # GSM bands
    if 824 <= freq_mhz <= 849:
        return "GSM-850 (downlink)"
    elif 869 <= freq_mhz <= 894:
        return "GSM-850 (uplink)"
    elif 890 <= freq_mhz <= 915:
        return "GSM-900 (downlink)"
    elif 925 <= freq_mhz <= 960:
        return "GSM-900 (uplink)"
    elif 1710 <= freq_mhz <= 1785:
        return "GSM-1800 (downlink)"
    elif 1805 <= freq_mhz <= 1880:
        return "GSM-1800 (uplink)"
    elif 1850 <= freq_mhz <= 1910:
        return "GSM-1900 (downlink)"
    elif 1930 <= freq_mhz <= 1990:
        return "GSM-1900 (uplink)"
    
    # LTE bands (US)
    elif 698 <= freq_mhz <= 716:
        return "LTE Band 12/17 (uplink)"
    elif 728 <= freq_mhz <= 746:
        return "LTE Band 12/17 (downlink)"
    elif 777 <= freq_mhz <= 787:
        return "LTE Band 13 (uplink)"
    elif 746 <= freq_mhz <= 756:
        return "LTE Band 13 (downlink)"
    elif 1710 <= freq_mhz <= 1755:
        return "LTE Band 4 (uplink)"
    elif 2110 <= freq_mhz <= 2155:
        return "LTE Band 4 (downlink)"
    elif 1850 <= freq_mhz <= 1910:
        return "LTE Band 2 (uplink)"
    elif 1930 <= freq_mhz <= 1990:
        return "LTE Band 2 (downlink)"
    
    # 5G bands
    elif 3700 <= freq_mhz <= 3980:
        return "5G n77 (C-band)"
    elif 24250 <= freq_mhz <= 24450:
        return "5G n258 (mmWave)"
    
    else:
        return "Other"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 analyze-spectrum.py <sweep_file.csv>")
        print("\nExample:")
        print("  python3 analyze-spectrum.py detection-logs/baseline/scan_20250101_120000.csv")
        sys.exit(1)
    
    analyze_sweep(sys.argv[1])
