#!/usr/bin/env python3
"""
Daily Monitor Launcher
"""
import os
import subprocess
import sys

# Change to project directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Run daily monitor script
subprocess.run(['./daily-monitor.sh'])
