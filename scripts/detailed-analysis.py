#!/usr/bin/env python3
"""
Detailed analysis of suspicious frequencies
"""

import sys
import csv
from collections import defaultdict

def detailed_analysis(scan_file, focus_freq_min=700, focus_freq_max=900):
    """Analyze specific frequency range in detail"""
    
    print(f"\n=== Detailed Analysis: {scan_file} ===")
    print(f"Focus range: {focus_freq_min}-{focus_freq_max} MHz\n")
    
    freq_data = defaultdict(list)
    
    # Read scan
    with open(scan_file, 'r') as f:
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
    
    # Calculate averages
    freq_avg = {}
    for freq, powers in freq_data.items():
        freq_avg[freq] = sum(powers) / len(powers)
    
    # Filter to focus range
    focus_signals = []
    for freq, power in freq_avg.items():
        freq_mhz = freq / 1e6
        if focus_freq_min <= freq_mhz <= focus_freq_max:
            focus_signals.append((freq, power))
    
    focus_signals.sort(key=lambda x: x[1], reverse=True)
    
    print(f"📡 Top 50 Signals in {focus_freq_min}-{focus_freq_max} MHz:")
    print(f"{'Frequency (MHz)':<20} {'Power (dBm)':<15} {'Band':<30} {'Notes'}")
    print("-" * 100)
    
    for freq, power in focus_signals[:50]:
        freq_mhz = freq / 1e6
        band = identify_band(freq)
        notes = get_notes(freq_mhz, power)
        print(f"{freq_mhz:<20.3f} {power:<15.2f} {band:<30} {notes}")
    
    # Identify clusters
    print(f"\n🔍 Signal Clusters:")
    clusters = find_clusters(focus_signals[:50])
    for cluster_center, cluster_signals in clusters:
        print(f"\n  Cluster around {cluster_center:.1f} MHz ({len(cluster_signals)} signals):")
        avg_power = sum(s[1] for s in cluster_signals) / len(cluster_signals)
        print(f"    Average power: {avg_power:.2f} dBm")
        print(f"    Range: {min(s[0]/1e6 for s in cluster_signals):.1f} - {max(s[0]/1e6 for s in cluster_signals):.1f} MHz")
        print(f"    Band: {identify_band(cluster_signals[0][0])}")

def find_clusters(signals, threshold_mhz=5):
    """Group nearby frequencies into clusters"""
    if not signals:
        return []
    
    clusters = []
    current_cluster = [signals[0]]
    
    for i in range(1, len(signals)):
        freq_diff = abs(signals[i][0] - current_cluster[-1][0]) / 1e6
        if freq_diff <= threshold_mhz:
            current_cluster.append(signals[i])
        else:
            if len(current_cluster) >= 3:
                center = sum(s[0] for s in current_cluster) / len(current_cluster) / 1e6
                clusters.append((center, current_cluster))
            current_cluster = [signals[i]]
    
    if len(current_cluster) >= 3:
        center = sum(s[0] for s in current_cluster) / len(current_cluster) / 1e6
        clusters.append((center, current_cluster))
    
    return clusters

def get_notes(freq_mhz, power):
    """Get notes about suspicious signals"""
    notes = []
    
    # Very strong signal
    if power > -20:
        notes.append("⚠️ VERY STRONG")
    elif power > -30:
        notes.append("Strong")
    
    # LTE Band 13 (public safety - used by FirstNet)
    if 746 <= freq_mhz <= 756 or 777 <= freq_mhz <= 787:
        notes.append("PUBLIC SAFETY BAND")
    
    # Check for unusual frequencies
    if 758 <= freq_mhz <= 768:
        notes.append("⚠️ Between LTE bands (unusual)")
    
    if 850 <= freq_mhz <= 853:
        notes.append("⚠️ Edge of GSM-850 (check)")
    
    return " | ".join(notes) if notes else ""

def identify_band(freq_hz):
    """Identify cellular band"""
    freq_mhz = freq_hz / 1e6
    
    if 824 <= freq_mhz <= 849:
        return "GSM-850 (downlink)"
    elif 869 <= freq_mhz <= 894:
        return "GSM-850 (uplink)"
    elif 890 <= freq_mhz <= 915:
        return "GSM-900 (downlink)"
    elif 925 <= freq_mhz <= 960:
        return "GSM-900 (uplink)"
    elif 698 <= freq_mhz <= 716:
        return "LTE Band 12/17 (uplink)"
    elif 728 <= freq_mhz <= 746:
        return "LTE Band 12/17 (downlink)"
    elif 746 <= freq_mhz <= 756:
        return "LTE Band 13 (downlink)"
    elif 777 <= freq_mhz <= 787:
        return "LTE Band 13 (uplink)"
    else:
        return "Other/Unknown"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 detailed-analysis.py <scan_file.csv> [freq_min] [freq_max]")
        print("\nExample:")
        print("  python3 detailed-analysis.py detection-logs/incidents/check_*.csv")
        print("  python3 detailed-analysis.py scan.csv 700 900")
        sys.exit(1)
    
    scan_file = sys.argv[1]
    freq_min = int(sys.argv[2]) if len(sys.argv) > 2 else 700
    freq_max = int(sys.argv[3]) if len(sys.argv) > 3 else 900
    
    detailed_analysis(scan_file, freq_min, freq_max)
