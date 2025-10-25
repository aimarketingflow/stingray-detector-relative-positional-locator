#!/usr/bin/env python3
"""
Stingray Detector GUI Launcher
"""
import os
import sys

# Change to project directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Import and run the GUI
import stingray_detector_gui
stingray_detector_gui.main()
