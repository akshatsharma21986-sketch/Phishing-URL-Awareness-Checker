#!/usr/bin/env python3
"""
Quick-launch script located at workspace root.
Allows running the EWB Phishing URL Awareness Checker directly without cd'ing first.
"""
import os
import sys

# Ensure project directory is in sys.path
PROJECT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phishing-url-awareness")
if os.path.isdir(PROJECT_DIR):
    if PROJECT_DIR not in sys.path:
        sys.path.insert(0, PROJECT_DIR)
    os.chdir(PROJECT_DIR)
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

from phishing_checker import main

if __name__ == "__main__":
    main()
