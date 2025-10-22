# 📸 Screenshot Checklist for Tutorial

## Setup & Installation

### 1. Terminal - HackRF Connection Test
**File:** `screenshot-01-hackrf-test.png`
**Command:** `./test-hackrf.sh`
**Show:**
- Terminal window
- Command output showing "✅ HackRF detected!"
- Device serial number
- Firmware version

---

## Baseline Scanning

### 2. Terminal - Baseline Scan Running
**File:** `screenshot-02-baseline-running.png`
**Command:** `./baseline-scan-boosted.sh`
**Show:**
- Terminal with scrolling frequency data
- Progress indicator
- Frequency ranges being scanned

### 3. Terminal - Baseline Analysis Results
**File:** `screenshot-03-baseline-results.png`
**Show:**
- Analysis output from baseline scan
- Strong signals detected
- Frequency bands identified
- Signal strength values

---

## Threat Detection

### 4. Terminal - Quick Check Running
**File:** `screenshot-04-quick-check.png`
**Command:** `./quick-check.sh`
**Show:**
- "Scanning..." message
- "Analyzing for threats..." message

### 5. Terminal - Detection Results (Threat Found)
**File:** `screenshot-05-detection-alert.png`
**Show:**
- "SIGNIFICANT POWER CHANGES" message
- Frequency and power change details
- Example: "851.000 MHz: -21.78 → -11.36 dB"

---

## GUI - Main Interface

### 6. GUI - Main Window with Tabs
**File:** `screenshot-06-gui-main.png`
**Show:**
- Full application window
- Three tabs visible: "📡 Directional Scanner", "⏱️ Monitoring & Schedule", "📸 Photo & Report"
- Clean, professional appearance

---

## GUI - Directional Scanner

### 7. GUI - Directional Scanner Tab (North)
**File:** `screenshot-07-directional-north.png`
**Show:**
- Compass rose diagram
- Red arrow pointing North
- "Start Scan" button
- Progress bar at 0/8

### 8. GUI - Scan in Progress
**File:** `screenshot-08-scan-progress.png`
**Show:**
- Progress bar showing "3/8 directions complete"
- Current direction highlighted
- Status message

### 9. GUI - Antenna Height Dialog
**File:** `screenshot-09-antenna-height.png`
**Show:**
- Dialog box for entering antenna height
- Input field showing "12.0 feet"
- Examples listed (Ground floor, Second floor, etc.)
- OK/Cancel buttons

### 10. GUI - Analysis Results
**File:** `screenshot-10-analysis-results.png`
**Show:**
- Results text area with analysis output
- "Strongest signal: SOUTHWEST (-16.28 dBm)"
- Position estimation
- "Estimated: 8 feet South, 8 feet West, 12 feet high"

---

## GUI - Monitoring & Schedule

### 11. GUI - Monitoring Tab
**File:** `screenshot-11-monitoring-tab.png`
**Show:**
- Quick test plan buttons (5 min, 10 min, 30 min, 1 hour, 2 hours)
- Scheduling section below
- Clean layout

### 12. GUI - Monitoring in Progress
**File:** `screenshot-12-monitoring-active.png`
**Show:**
- Status window with real-time updates
- "[19:00:42] Starting 60 minute monitoring..."
- Signal strength readings
- "851.0 MHz: -15.95 dBm"

### 13. GUI - Schedule Configuration
**File:** `screenshot-13-schedule-config.png`
**Show:**
- "Enable daily automated monitoring" checkbox (checked)
- Time picker showing "08:00 PM"
- Duration: "60 minutes"
- Interval: "120 seconds"
- "Save Schedule" button

---

## GUI - Photo & Report

### 14. GUI - Photo Annotation Tab
**File:** `screenshot-14-photo-tab.png`
**Show:**
- "Select Photo" button
- Measurement input fields (Species, Distance, Direction, Height, Signal)
- Photo preview area
- "Annotate Photo" button

### 15. GUI - Photo Selected with Preview
**File:** `screenshot-15-photo-preview.png`
**Show:**
- Photo path filled in
- Photo preview displayed
- Measurement fields filled with example data

### 16. GUI - Annotated Photo Result
**File:** `screenshot-16-annotated-result.png`
**Show:**
- Annotated photo in preview area
- Overlay text visible:
  - Top: "🎯 LightPolaflag"
  - "📏 Distance: 12 feet"
  - "🧭 Direction: Southwest"
  - Bottom: "📐 Height: 10 feet above ground"
  - "📡 Signal: -15.5 dBm"

### 17. GUI - GitHub Upload Dialog
**File:** `screenshot-17-github-upload.png`
**Show:**
- Dialog box with upload instructions
- "📤 Share Your Findings!" title
- Step-by-step instructions
- "Open GitHub" and "Cancel" buttons

---

## Command Line - Advanced Features

### 18. Terminal - Movement Analysis Results
**File:** `screenshot-18-movement-analysis.png`
**Command:** `python3 scripts/analyze-movement.py detection-logs/tracking/session_*/`
**Show:**
- Signal strength timeline
- Movement analysis for each frequency
- "SIGNAL FLUCTUATING" or "SIGNAL STABLE" assessment
- Location assessment (mobile vs stationary)

### 19. Terminal - Stingray Pokedex
**File:** `screenshot-19-pokedex.png`
**Command:** `./stingray_map.py list`
**Show:**
- "🎯 STINGRAY POKEDEX 🎯" header
- Collection stats (Total caught, Mobile, Fixed)
- Active Stingrays list with details
- Species names, locations, signal strengths

### 20. Terminal - Position Estimation
**File:** `screenshot-20-position-estimate.png`
**Command:** `python3 scripts/estimate-position.py detection-logs/directional/ 12`
**Show:**
- Distance estimation table
- Vertical analysis
- 3D position summary
- "Estimated: X feet South, Y feet West, Z feet high"

---

## Bonus Screenshots (Optional but Helpful)

### 21. Finder - Project Directory Structure
**File:** `screenshot-21-directory.png`
**Show:**
- Finder window showing project folders
- Scripts, detection-logs, docs folders visible

### 22. Desktop - App Icons
**File:** `screenshot-22-desktop-apps.png`
**Show:**
- Desktop with "Stingray Detector", "Daily Monitor", "Stingray Check" apps

### 23. Terminal - Scheduler Status
**File:** `screenshot-23-scheduler.png`
**Command:** `./manage-scheduler.sh status`
**Show:**
- Scheduler running status
- Recent log entries

---

## Screenshot Guidelines

**Resolution:** 1920x1080 or higher
**Format:** PNG (for clarity)
**Naming:** Use the exact filenames listed above
**Location:** Save to `docs/screenshots/` folder

**Tips:**
- Use clean terminal with readable font size
- Ensure GUI windows are fully visible
- Crop out unnecessary desktop clutter
- Use macOS screenshot tool: Cmd+Shift+4 (select area)
- For full window: Cmd+Shift+4, then Space, click window

**After taking screenshots:**
1. Create folder: `mkdir docs/screenshots`
2. Move all screenshots there
3. Update HTML files to reference them:
   - Replace `<div class="screenshot-placeholder">` with `<img src="screenshots/screenshot-XX-name.png">`

---

## Quick Screenshot Commands

```bash
# Take all the command-line screenshots in sequence:

# 1. Test HackRF
./test-hackrf.sh

# 2-3. Baseline
./baseline-scan-boosted.sh

# 4-5. Detection
./quick-check.sh

# 18. Movement analysis (if you have tracking data)
python3 scripts/analyze-movement.py detection-logs/tracking/session_*/

# 19. Pokedex (if you have catches)
./stingray_map.py list

# 20. Position estimate (if you have directional scans)
python3 scripts/estimate-position.py detection-logs/directional/ 12

# 23. Scheduler
./manage-scheduler.sh status
```

**For GUI screenshots:** Just launch `python3 stingray_detector_gui.py` and go through each tab!

---

**Total Screenshots Needed: 20-23**
**Estimated Time: 15-20 minutes**

Good luck! 📸
