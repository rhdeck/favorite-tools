#!/usr/bin/env bash
# Symlink the budget-aware review scripts onto PATH so `budget`, `review`, and
# `pick-review-engine` work interactively in a shell (not just from the skill).
# Idempotent — safe to re-run. Default target: ~/.local/bin.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN="${1:-$HOME/.local/bin}"
mkdir -p "$BIN"
for s in budget review pick-review-engine; do
  chmod +x "$HERE/$s"
  ln -sf "$HERE/$s" "$BIN/$s"
  echo "linked $BIN/$s -> $HERE/$s"
done
case ":$PATH:" in
  *":$BIN:"*) ;;
  *) echo "NOTE: $BIN is not on your PATH — add it to use these from the shell." ;;
esac
