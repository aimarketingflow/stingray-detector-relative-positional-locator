#!/usr/bin/env python3
"""
Compare two spectrum scans to detect changes (potential Stingray activity)
"""

import sys
import csv
from collections import defaultdict

def load_scan(filename):
    """Load and process a scan file"""
    freq_data = defaultdict(list)
    
    try:
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 6:
                    continue
                    
                try:
                    hz_low = int(row[2])
                    hz_high = int(row[3])
                    hz_bin_width = float(row[4])
                    power_readings = [float(x) for x in row[6:] if x]
                    
                    for i, power in enumerate(power_readings):
                        freq = hz_low + (i * hz_bin_width)
                        freq_data[freq].append(power)
                        
                except (ValueError, IndexError):
                    continue
                    
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        sys.exit(1)
    
    # Calculate average power for each frequency
    freq_avg = {}
    for freq, powers in freq_data.items():
        freq_avg[freq] = sum(powers) / len(powers)
    
    return freq_avg

def compare_scans(baseline_file, current_file, threshold=-60):
    """Compare two scans and identify differences"""
    
    print(f"\n=== Comparing Scans ===")
    print(f"Baseline: {baseline_file}")
    print(f"Current:  {current_file}")
    print(f"Threshold: {threshold} dBm")
    print()
    
    baseline = load_scan(baseline_file)
    current = load_scan(current_file)
    
    # Find strong signals in each
    baseline_strong = {freq: power for freq, power in baseline.items() if power > threshold}
    current_strong = {freq: power for freq, power in current.items() if power > threshold}
    
    # Find new signals (in current but not baseline)
    new_signals = []
    for freq in current_strong:
        if freq not in baseline_strong:
            new_signals.append((freq, current_strong[freq]))
    
    # Find disappeared signals (in baseline but not current)
    disappeared_signals = []
    for freq in baseline_strong:
        if freq not in current_strong:
            disappeared_signals.append((freq, baseline_strong[freq]))
    
    # Find changed signals (significant power difference)
    changed_signals = []
    for freq in baseline_strong:
        if freq in current_strong:
            power_diff = current_strong[freq] - baseline_strong[freq]
            if abs(power_diff) > 5:  # 5 dBm threshold
                changed_signals.append((freq, baseline_strong[freq], current_strong[freq], power_diff))
    
    # Report findings
    print("📊 Summary:")
    print(f"   Baseline strong signals: {len(baseline_strong)}")
    print(f"   Current strong signals:  {len(current_strong)}")
    print()
    
    if new_signals:
        print("🚨 NEW SIGNALS DETECTED (SUSPICIOUS!):")
        new_signals.sort(key=lambda x: x[1], reverse=True)
        for freq, power in new_signals:
            freq_mhz = freq / 1e6
            band = identify_band(freq)
            print(f"   {freq_mhz:.3f} MHz: {power:.2f} dBm ({band})")
        print()
    else:
        print("✅ No new signals detected")
        print()
    
    if disappeared_signals:
        print("⚠️  DISAPPEARED SIGNALS:")
        disappeared_signals.sort(key=lambda x: x[1], reverse=True)
        for freq, power in disappeared_signals:
            freq_mhz = freq / 1e6
            band = identify_band(freq)
            print(f"   {freq_mhz:.3f} MHz: {power:.2f} dBm ({band})")
        print()
    else:
        print("✅ No signals disappeared")
        print()
    
    if changed_signals:
        print("📈 SIGNIFICANT POWER CHANGES:")
        changed_signals.sort(key=lambda x: abs(x[3]), reverse=True)
        for freq, old_power, new_power, diff in changed_signals:
            freq_mhz = freq / 1e6
            band = identify_band(freq)
            direction = "↑" if diff > 0 else "↓"
            print(f"   {freq_mhz:.3f} MHz: {old_power:.2f} → {new_power:.2f} dBm ({direction}{abs(diff):.2f} dB) ({band})")
        print()
    else:
        print("✅ No significant power changes")
        print()
    
    # Threat assessment
    print("🔍 Threat Assessment:")
    if new_signals:
        print("   ⚠️  HIGH ALERT: New signals detected!")
        print("   Action: Investigate these frequencies immediately")
        print("   - Use GQRX to listen to the signal")
        print("   - Check if signal persists over time")
        print("   - Compare with OpenCellID database")
    elif changed_signals:
        print("   ⚠️  MODERATE: Signal strength changes detected")
        print("   Action: Monitor for continued changes")
    elif disappeared_signals:
        print("   ℹ️  INFO: Some signals disappeared (could be normal)")
        print("   Action: Run another scan to verify")
    else:
        print("   ✅ NORMAL: No suspicious activity detected")
    print()

def identify_band(freq_hz):
    """Identify cellular band from frequency"""
    freq_mhz = freq_hz / 1e6
    
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
    else:
        return "Other"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 compare-scans.py <baseline.csv> <current.csv> [threshold_dBm]")
        print("\nExample:")
        print("  python3 compare-scans.py scan1.csv scan2.csv")
        print("  python3 compare-scans.py scan1.csv scan2.csv -55")
        sys.exit(1)
    
    baseline_file = sys.argv[1]
    current_file = sys.argv[2]
    threshold = float(sys.argv[3]) if len(sys.argv) > 3 else -60
    
    compare_scans(baseline_file, current_file, threshold)
