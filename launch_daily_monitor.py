#!/usr/bin/env python3
"""
Daily Monitor Launcher
"""
import os
import subprocess
import sys

# Change to project directory
os.chdir('/Users/meep/Documents/EpiRay')

# Run daily monitor script
subprocess.run(['./daily-monitor.sh'])
