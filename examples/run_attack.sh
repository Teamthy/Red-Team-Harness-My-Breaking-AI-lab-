#!/usr/bin/env bash
set -euo pipefail

python -m pip install -e .
breaklab attack --target mock://echo
