#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root/manuscript"
pdflatex -interaction=nonstopmode -halt-on-error pairpulse.tex
pdflatex -interaction=nonstopmode -halt-on-error pairpulse.tex
