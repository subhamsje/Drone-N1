#!/usr/bin/env python3
"""Launch Altaria N1 cognitive backend platform."""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from backend.api.app import main

if __name__ == "__main__":
    main()
