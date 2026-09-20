"""Run the test suite from the project root without installing the package.

If `fivecentsub` is already importable (e.g. installed in a venv), this does
nothing. Otherwise it puts `src/` on `sys.path` using only the standard
library, so plain `python -m pytest` works with any Python >= 3.12 that has
pytest available.
"""

import os
import sys

try:
    import fivecentsub  # noqa: F401
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
