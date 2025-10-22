# 🎯 Stingray Detector & Relative Positional Locator

**Detect, track, and locate IMSI catchers (Stingrays) using Software Defined Radio (SDR) and RF spectrum analysis.**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-lightgrey.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)

---

## 🚨 What is This?

This toolkit allows you to:
- ✅ **Detect** unauthorized cellular surveillance devices (Stingrays/IMSI catchers)
- ✅ **Track** signal patterns over time to identify mobile vs. stationary devices
- ✅ **Locate** the physical position of the device using directional scanning and triangulation
- ✅ **Monitor** continuously with automated scheduling
- ✅ **Document** evidence for legal/advocacy purposes

**100% Legal:** All monitoring is receive-only (no transmission), fully compliant with FCC regulations.

---

## 📹 Video Tutorial

Coming soon: Complete walkthrough showing real-world detection and location of a Stingray device.

---

## 🛠️ Equipment Needed

### Required:
- **HackRF One** (~$300) - Software Defined Radio
  - [Buy from Great Scott Gadgets](https://greatscottgadgets.com/hackrf/)
  - Alternative: RTL-SDR (~$30) for basic detection only
- **Laptop** (Mac, Linux, or Windows)
- **Antenna** (included with HackRF)

### Optional:
- **Directional antenna** for better triangulation
- **External battery** for portable operation

**Total cost: ~$300-400**

---

## 🚀 Quick Start

### 1. Install Dependencies

**macOS:**
```bash
# Install Homebrew if needed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install HackRF tools and dependencies
brew install hackrf
brew install python3
brew install pyqt@6

# Clone this repository
git clone https://github.com/aimarketingflow/stingray-detector-relative-positional-locator.git
cd stingray-detector-relative-positional-locator

# Make scripts executable
chmod +x *.sh scripts/*.py
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install hackrf python3 python3-pip python3-pyqt6
git clone https://github.com/aimarketingflow/stingray-detector-relative-positional-locator.git
cd stingray-detector-relative-positional-locator
chmod +x *.sh scripts/*.py
```

### 2. Test Your HackRF

```bash
./test-hackrf.sh
```

### 3. Run Your First Scan

```bash
# Establish baseline (normal RF environment)
./baseline-scan-boosted.sh

# Quick threat check
./quick-check.sh
```

### 4. Launch GUI (macOS)

```bash
python3 stingray_detector_gui.py
```

Or use the desktop app (macOS only):
```bash
# Copy to desktop
cp -R "Stingray Detector.app" ~/Desktop/
```

---

## 📊 Features

### 🔍 Detection Methods

**1. Spectrum Analysis**
- Scans cellular frequencies (700-960 MHz, 1710-1990 MHz)
- Identifies unusual signals in guard bands
- Detects very strong nearby sources

**2. Directional Scanning**
- 8-direction antenna positioning (N, S, E, W, NE, NW, SE, SW, Up, Down)
- Visual GUI with compass diagrams
- Pinpoints signal source location

**3. Triangulation**
- Two-point position estimation
- Calculates distance using Free Space Path Loss (FSPL)
- Estimates height and 3D position

**4. Movement Tracking**
- Monitors signal strength over time
- Distinguishes mobile (vehicle) vs. stationary (fixed installation)
- Detects power cycling and directional changes

**5. Multipath Analysis**
- Identifies signal reflections from buildings
- Confirms nearby reflectors
- Improves location accuracy

### 🎯 What We Look For

**Suspicious Frequency Bands:**
- **758-767 MHz** - Between LTE bands (unusual, often used by Stingrays)
- **850-853 MHz** - Edge of GSM-850 (evasion tactic)
- **746-756 MHz** - LTE Band 13 (public safety/FirstNet)

**Signal Characteristics:**
- Very strong power (-10 to -30 dBm = very close)
- Persistent over time
- Operating in multiple bands simultaneously
- High variance (multipath from structures)

---

## 📱 GUI Application

### Directional Scanner Tab
- Step-by-step visual guide
- Compass rose showing antenna direction
- Automatic scanning and analysis
- Position estimation with antenna height input

### Monitoring & Schedule Tab
- **Quick test plans:** 5 min, 10 min, 30 min, 1 hour, 2 hours
- **Automated scheduling:** Daily monitoring at set time
- **Smart HackRF management:** Auto-kills conflicting processes
- **Missed schedule recovery:** Runs when HackRF detected

---

## 🖥️ Command Line Tools

### Basic Scanning

```bash
# Quick threat check
./quick-check.sh

# Daily monitoring (saves to detection-logs/daily/)
./daily-monitor.sh

# Directional scan (interactive)
./directional-scan.sh

# Movement tracking (60 min, 2 min intervals)
./track-movement.sh 60 120
```

### Analysis Scripts

```bash
# Analyze spectrum
python3 scripts/analyze-spectrum.py scan.csv

# Compare two scans
python3 scripts/compare-scans.py baseline.csv current.csv -50

# Detailed frequency analysis
python3 scripts/detailed-analysis.py scan.csv 700 900

# Multipath/reflection analysis
python3 scripts/multipath-analysis.py scan.csv

# Position estimation
python3 scripts/estimate-position.py detection-logs/directional/ 12

# Compare directional scans
python3 scripts/compare-directions.py detection-logs/directional/

# Movement analysis
python3 scripts/analyze-movement.py detection-logs/tracking/session_*/
```

### Scheduling

```bash
# Start scheduler daemon
./manage-scheduler.sh start

# Check status
./manage-scheduler.sh status

# View logs
./manage-scheduler.sh logs

# Stop scheduler
./manage-scheduler.sh stop
```

---

## 📂 Project Structure

```
stingray-detector-relative-positional-locator/
├── README.md                          # This file
├── LICENSE                            # MIT License
├── EVIDENCE_PACKAGE.md               # Template for legal documentation
├── YOUTUBE_TUTORIAL_OUTLINE.md       # Video tutorial outline
├── stingray-detection-tracker.md     # Project tracking document
│
├── stingray_detector_gui.py          # Main GUI application
├── scheduler.py                       # Automated scheduling daemon
│
├── setup.sh                           # Initial setup script
├── test-hackrf.sh                     # Test HackRF connection
├── baseline-scan.sh                   # Basic baseline scan
├── baseline-scan-boosted.sh           # Enhanced baseline scan
├── quick-check.sh                     # Quick threat detection
├── daily-monitor.sh                   # Daily monitoring
├── directional-scan.sh                # Interactive directional scanning
├── track-movement.sh                  # Movement tracking
├── manage-scheduler.sh                # Scheduler management
│
├── scripts/
│   ├── analyze-spectrum.py            # Spectrum analysis
│   ├── compare-scans.py               # Baseline comparison
│   ├── detailed-analysis.py           # Detailed frequency analysis
│   ├── multipath-analysis.py          # Reflection/multipath detection
│   ├── estimate-position.py           # Position triangulation
│   ├── compare-directions.py          # Directional scan comparison
│   └── analyze-movement.py            # Movement pattern analysis
│
├── detection-logs/                    # Scan data (gitignored)
│   ├── baseline/                      # Baseline scans
│   ├── incidents/                     # Threat detections
│   ├── daily/                         # Daily monitoring
│   ├── tracking/                      # Movement tracking sessions
│   ├── directional/                   # Directional scans
│   └── treadmill/                     # Secondary position scans
│
└── docs/                              # Documentation
    ├── TUTORIAL.md                    # Detailed tutorial
    ├── FREQUENCY_REFERENCE.md         # Frequency band guide
    ├── LEGAL_GUIDE.md                 # Legal information
    └── EQUIPMENT.md                   # Hardware recommendations
```

---

## 🎓 How It Works

### 1. Baseline Establishment
First, we scan the RF environment to understand what's "normal":
```bash
./baseline-scan-boosted.sh
```

This creates a reference of legitimate cell towers and RF activity.

### 2. Detection
Compare current scans against baseline to find anomalies:
```bash
./quick-check.sh
```

Looks for:
- New strong signals
- Unusual frequency usage
- Signals in guard bands

### 3. Directional Scanning
Point antenna in 8 directions to find signal source:
```bash
./directional-scan.sh
# Or use GUI for visual guidance
```

### 4. Triangulation
Scan from 2+ locations to calculate exact position:
```bash
python3 scripts/estimate-position.py detection-logs/directional/ [antenna_height]
```

Uses Free Space Path Loss (FSPL) formula:
```
FSPL (dB) = 20*log10(d) + 20*log10(f) + 32.45
```

### 5. Movement Tracking
Monitor over time to determine if source is mobile or stationary:
```bash
./track-movement.sh 60 120  # 60 min, 2 min intervals
```

---

## 🔬 Technical Details

### Frequencies Monitored

**GSM Bands:**
- GSM-850: 824-849 MHz (downlink), 869-894 MHz (uplink)
- GSM-900: 890-915 MHz (downlink), 925-960 MHz (uplink)
- GSM-1800: 1710-1785 MHz (downlink), 1805-1880 MHz (uplink)
- GSM-1900: 1850-1910 MHz (downlink), 1930-1990 MHz (uplink)

**LTE Bands:**
- Band 12/17: 698-716 MHz (uplink), 728-746 MHz (downlink)
- Band 13: 746-756 MHz (downlink), 777-787 MHz (uplink) - Public Safety

**Suspicious Ranges:**
- 758-768 MHz (between LTE bands - guard band)
- 850-853 MHz (edge of GSM-850)

### HackRF Settings

```bash
hackrf_sweep \
    -f 700:960 \          # Frequency range (MHz)
    -f 1710:1990 \        # Second range
    -a 1 \                # Enable RF amplifier (+14 dB)
    -l 32 \               # LNA gain (0-40 dB)
    -g 40 \               # VGA gain (0-62 dB)
    -N 100 \              # Number of sweeps
    -r output.csv         # Output file
```

### Signal Strength Reference

- **-10 to -30 dBm:** Very strong (device very close, <100m)
- **-30 to -50 dBm:** Strong (typical cell tower at moderate distance)
- **-50 to -70 dBm:** Moderate (normal cellular signal)
- **-70 to -90 dBm:** Weak (edge of coverage)
- **Below -90 dBm:** Very weak

---

## ⚖️ Legal Information

### ✅ What's Legal

**Receive-Only Monitoring:**
- 100% legal under FCC regulations
- No license required
- Passive observation of RF spectrum
- Educational and security research

**Documentation:**
- Recording RF data
- Taking photos/videos
- Reporting to authorities
- Publishing findings

### ❌ What's Illegal

**DO NOT:**
- ❌ Transmit on cellular frequencies
- ❌ Jam or interfere with signals
- ❌ Attempt to "hack back" or counter-attack
- ❌ Access cellular networks without authorization
- ❌ Intercept communications content

### 📋 Reporting

If you detect a Stingray:

**Privacy Organizations:**
- **ACLU:** https://www.aclu.org/contact
- **EFF:** info@eff.org, (415) 436-9333

**Government:**
- **FCC:** https://consumercomplaints.fcc.gov
- **FBI:** https://tips.fbi.gov (if criminal activity)

**Media:**
- **ProPublica:** tips@propublica.org
- **The Intercept:** tips@theintercept.com

---

## 🛡️ Privacy & Security

### Protect Yourself

**While Monitoring:**
- Use encrypted messaging (Signal, WhatsApp)
- Enable airplane mode when not using phone
- Use VPN for internet traffic
- Be aware of physical surveillance

**Data Security:**
- Backup all scan data
- Encrypt sensitive files
- Store evidence in multiple locations
- Document chain of custody

### Faraday Protection

Consider a Faraday bag or cage for your phone:
- Blocks all RF signals
- Prevents tracking when not in use
- Can be DIY (copper mesh, aluminum foil)

---

## 🎥 YouTube Tutorial

### Planned Content

1. **Introduction** - What are Stingrays and why this matters
2. **Equipment Setup** - Unboxing and installation
3. **First Detection** - Running baseline and threat scans
4. **Directional Scanning** - Using the GUI to locate device
5. **Triangulation** - Pinpointing exact position
6. **Movement Tracking** - Determining if mobile or stationary
7. **Evidence Collection** - Documentation for legal action
8. **Reporting** - Who to contact and how

**Subscribe for updates!**

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Areas for Contribution

- **Windows support** - Port scripts and GUI
- **Additional SDR support** - RTL-SDR, LimeSDR, etc.
- **Machine learning** - Automated threat classification
- **Mobile app** - iOS/Android companion
- **Visualization** - Heat maps, 3D positioning
- **Documentation** - Translations, tutorials

---

## 📜 License

MIT License - See [LICENSE](LICENSE) file

**Use responsibly and legally. This tool is for educational purposes and legitimate security research.**

---

## 🙏 Acknowledgments

- **Great Scott Gadgets** - HackRF One hardware
- **GNU Radio** - Signal processing framework
- **EFF & ACLU** - Privacy advocacy and legal guidance
- **Security research community** - Techniques and methodologies

---

## 📞 Contact

- **Issues:** https://github.com/aimarketingflow/stingray-detector-relative-positional-locator/issues
- **Discussions:** https://github.com/aimarketingflow/stingray-detector-relative-positional-locator/discussions

---

## ⚠️ Disclaimer

This software is provided for educational and security research purposes only. Users are responsible for complying with all applicable laws and regulations. The authors are not responsible for any misuse or illegal activities conducted with this software.

**Always:**
- Operate in receive-only mode
- Respect privacy laws
- Report findings to appropriate authorities
- Use for defensive purposes only

---

**Stay safe. Protect your privacy. Know your rights.**

🔒 **Privacy is a right, not a privilege.**
