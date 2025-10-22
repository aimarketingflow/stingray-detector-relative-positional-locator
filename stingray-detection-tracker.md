# Stingray Detection & Monitoring Project

## Project Goal
Detect and document potential IMSI catcher (Stingray) activity in the local area using legal monitoring techniques.

---

## Equipment Inventory

### Hardware
- [ ] HackRF One SDR
- [ ] Copper pipe RF containment system (Faraday cage)
- [ ] Android device(s) for detection apps
- [ ] Laptop/computer for SDR analysis
- [ ] Antennas (appropriate for cellular bands)

### Software to Install
- [ ] **AIMSICD** (Android IMSI-Catcher Detector)
- [ ] **SnoopSnitch** (requires root)
- [ ] **GNU Radio** + `gr-gsm`
- [ ] **GQRX** (spectrum visualization)
- [ ] **kalibrate-rtl** (cell tower finder)
- [ ] **LTE-Cell-Scanner**
- [ ] **hackrf_sweep** (included with HackRF tools)

---

## Setup Tasks

### Phase 1: Baseline Establishment
- [ ] Install HackRF drivers and tools
- [ ] Test HackRF receive functionality
- [ ] Install detection apps on phone(s)
- [ ] Document legitimate cell towers in area
  - [ ] Record Cell IDs
  - [ ] Record frequencies
  - [ ] Record signal strengths
  - [ ] Map physical locations (OpenCellID)
- [ ] Create baseline logs (1-2 weeks normal activity)

### Phase 2: RF Containment Testing
- [ ] Test copper pipe Faraday cage effectiveness
- [ ] Measure signal attenuation inside cage
- [ ] Document phone behavior in shielded vs unshielded
- [ ] Establish controlled testing protocol

### Phase 3: Monitoring System
- [ ] Set up continuous spectrum monitoring
- [ ] Configure automated logging
- [ ] Create alert system for anomalies
- [ ] Set up multi-device correlation

---

## Monitoring Checklist

### Daily Observations
- [ ] Check IMSI catcher detection apps
- [ ] Note any unusual cell tower changes
- [ ] Log battery drain anomalies
- [ ] Record network downgrades (LTE → 2G/3G)
- [ ] Document SMS/call issues

### Weekly Analysis
- [ ] Review spectrum analyzer logs
- [ ] Compare cell tower IDs against baseline
- [ ] Analyze signal strength patterns
- [ ] Check for new/disappearing towers
- [ ] Correlate events across devices

---

## Detection Indicators

### Suspicious Activity Signs
- **Network Behavior:**
  - [ ] Forced 2G downgrade
  - [ ] Encryption downgrade alerts
  - [ ] Frequent re-authentication
  - [ ] New cell tower IDs appearing temporarily
  
- **Device Behavior:**
  - [ ] Excessive battery drain when idle
  - [ ] Phone warm without usage
  - [ ] SMS delivery delays/failures
  - [ ] Call quality degradation

- **RF Analysis:**
  - [ ] Unexpected signals in cellular bands
  - [ ] Signal strength anomalies
  - [ ] Tower location mismatches
  - [ ] Timing advance irregularities

---

## Documentation Protocol

### Data to Collect
- **Timestamp** (date/time)
- **Location** (GPS coordinates)
- **Cell Tower Info:**
  - Cell ID (CID)
  - Location Area Code (LAC)
  - Mobile Country Code (MCC)
  - Mobile Network Code (MNC)
  - Signal strength (dBm)
  - Frequency
- **Network Type** (2G/3G/4G/5G)
- **App Alerts** (screenshots)
- **Spectrum Data** (CSV exports)
- **Observations** (notes)

### File Organization
```
/detection-logs/
  /baseline/
  /incidents/
  /spectrum-data/
  /screenshots/
  /reports/
```

---

## Command Reference

### HackRF Commands
```bash
# Scan cellular bands (GSM 850/900/1800/1900, LTE)
hackrf_sweep -f 700:960 -f 1710:2170 -w scan_$(date +%Y%m%d_%H%M%S).csv

# Continuous monitoring
hackrf_sweep -f 700:960 -f 1710:2170 -w output.csv -N 1000000

# Check HackRF info
hackrf_info
```

### GNU Radio / GSM
```bash
# Scan for GSM towers
grgsm_scanner -v

# Find GSM base stations
grgsm_livemon

# Calibrate frequency
kal -s GSM900
```

### Analysis
```bash
# Find cell towers with kalibrate
kalibrate-hackrf -s GSM900 -g 40

# LTE cell scanning
LTE-Cell-Scanner -s 739e6
```

---

## Legal Compliance

### ✅ Legal Activities
- Receiving RF signals (passive monitoring)
- Running detection apps
- Documenting observations
- Spectrum analysis (receive-only)
- Using Faraday cages for shielding

### ❌ Illegal Activities (DO NOT DO)
- Transmitting on cellular frequencies
- Operating unauthorized base station
- Jamming signals
- Interfering with communications
- "Hacking back" or active countermeasures

---

## Reporting Channels

### If Suspicious Activity Detected
- **EFF (Electronic Frontier Foundation)**: privacy@eff.org
- **ACLU**: Local chapter + national
- **FBI IC3**: https://www.ic3.gov (if criminal actors)
- **FCC**: https://consumercomplaints.fcc.gov
- **Local investigative journalists**
- **Immigration rights orgs** (if ICE-related): ACLU, NILC

### Evidence Package
- [ ] Timeline of incidents
- [ ] Cell tower logs
- [ ] Spectrum analyzer data
- [ ] App screenshots/alerts
- [ ] Correlation analysis
- [ ] Location data
- [ ] Summary report

---

## Resources

### Documentation
- [AIMSICD Wiki](https://github.com/CellularPrivacy/Android-IMSI-Catcher-Detector/wiki)
- [gr-gsm Documentation](https://github.com/ptrkrysik/gr-gsm)
- [HackRF Documentation](https://hackrf.readthedocs.io/)
- [OpenCellID Database](https://opencellid.org/)

### Learning
- [Cellular Security Basics](https://www.eff.org/wp/gotta-catch-em-all-understanding-how-imsi-catchers-exploit-cell-networks)
- [GSM Security](https://www.rtl-sdr.com/rtl-sdr-tutorial-analyzing-gsm-with-airprobe-and-wireshark/)
- [LTE Protocol](https://www.sharetechnote.com/html/Handbook_LTE.html)

---

## Progress Log

### [Date] - Initial Setup
- Status:
- Notes:
- Next steps:

### [Date] - Baseline Collection
- Status:
- Notes:
- Next steps:

### [Date] - Monitoring Active
- Status:
- Notes:
- Next steps:

---

## Notes & Observations

### General Notes
- 

### Anomalies Detected
- 

### Questions / Research Needed
- 

---

**Last Updated:** [Date]
**Project Status:** Planning / Setup / Active Monitoring / Analysis
