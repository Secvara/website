#!/usr/bin/env python3
"""
Run the entire Google marketing automation workflow in sequence.

This simply stitches together the existing scripts so you can execute
one command after the environment variables are populated.
"""
from __future__ import annotations

import subprocess
import sys
from typing import List


def run_module(module: str, args: List[str] | None = None) -> None:
    command = [sys.executable, "-m", module]
    if args:
        command.extend(args)
    print(f"\n--- Running {' '.join(command)} ---")
    subprocess.check_call(command)


def main() -> int:
    base_module = "scripts.google"
    run_module(f"{base_module}.gtm_sync")
    run_module(f"{base_module}.ga4_setup")
    run_module(f"{base_module}.google_ads_setup")
    print("\nAutomation workflow complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
