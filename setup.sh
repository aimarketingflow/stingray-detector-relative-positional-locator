#!/bin/bash
# Stingray Detection System Setup Script

set -e

echo "=== Stingray Detection System Setup ==="
echo ""

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found. Install from https://brew.sh"
    exit 1
fi

echo "✅ Homebrew found"

# Install required packages
echo ""
echo "📦 Installing required packages..."
echo ""

# Core SDR tools
packages=(
    "gqrx"              # Spectrum analyzer GUI
    "gnuradio"          # SDR framework
    "python@3.11"       # Python for scripts
)

for package in "${packages[@]}"; do
    if brew list "$package" &>/dev/null; then
        echo "✅ $package already installed"
    else
        echo "📥 Installing $package..."
        brew install "$package"
    fi
done

# Install Python dependencies
echo ""
echo "🐍 Installing Python dependencies..."
pip3 install --user numpy scipy matplotlib pandas

# Create directory structure
echo ""
echo "📁 Creating directory structure..."
mkdir -p detection-logs/{baseline,incidents,spectrum-data,screenshots,reports}
mkdir -p scripts

echo "✅ Directories created"

# Check HackRF connection
echo ""
echo "🔍 Checking HackRF connection..."
if hackrf_info &>/dev/null; then
    echo "✅ HackRF detected!"
    hackrf_info
else
    echo "⚠️  HackRF not detected. Please connect your HackRF One."
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Install gr-gsm: https://github.com/ptrkrysik/gr-gsm"
echo "2. Install kalibrate-hackrf: https://github.com/scateu/kalibrate-hackrf"
echo "3. Run ./test-hackrf.sh to verify hardware"
echo "4. Run ./baseline-scan.sh to establish baseline"
