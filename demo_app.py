#!/usr/bin/env python3
"""Entry point for Streamlit demo - handles import path automatically."""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Now import and run the actual demo
from src.ui.demo_app import main

if __name__ == "__main__":
    main()
