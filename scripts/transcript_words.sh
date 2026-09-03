#!/usr/bin/env bash
# Print a transcript file's prose as one word per line, ignoring frontmatter and
# headings, so two versions can be diffed to prove the words survived an edit.
set -euo pipefail
awk 'NR==1&&/^---$/{fm=1;next} fm&&/^---$/{fm=0;next} !fm&&!/^#/' "$1" \
  | tr -s '[:space:]' '\n' | grep -v '^$'
