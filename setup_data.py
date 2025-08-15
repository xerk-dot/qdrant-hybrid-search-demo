#!/usr/bin/env python3
"""Entry point for data setup - handles import path automatically."""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Now import and run the actual setup
from src.data.setup_data import main

if __name__ == "__main__":
    main()
