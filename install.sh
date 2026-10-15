#!/bin/sh
# Abacus installer: thin wrapper so `./install.sh` works from a fresh clone.
exec python3 "$(dirname "$0")/bin/abacus" install "$@"
