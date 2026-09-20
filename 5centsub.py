"""Standalone CLI launcher: no install step, standard library only.

Usage from the project root:
    python 5centsub.py demo
    python 5centsub.py validate-ass <file.ass>
    python 5centsub.py estimate --source-seconds <n> ...
    python 5centsub.py prepare-audio <input> <output> --dry-run

It runs the source tree directly, so any Python >= 3.12 works.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from fivecentsub.cli import main

raise SystemExit(main())
