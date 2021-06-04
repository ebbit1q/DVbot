#/bin/bash
# blacken all the source files!
cd "${BASH_SOURCE%/*}/" || exit 2
black -l 79 *.py
