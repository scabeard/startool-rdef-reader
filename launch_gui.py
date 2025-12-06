#!/usr/bin/env python3
"""
Launcher script for the NASA RDEF File Reader GUI

This script adds the current directory to the Python path
and launches the GUI application.
"""

import sys
import os

# Add the current directory to Python path so we can import nasa_rdef_reader
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Now import and launch the GUI
from nasa_rdef_reader.gui import main

if __name__ == "__main__":
    main()
