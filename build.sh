#!/usr/bin/env bash
# Render: decodifica binários enviados como .b64 (o push é por texto)
set -e
find public -name '*.b64' | while read -r f; do base64 -d "$f" > "${f%.b64}"; rm -f "$f"; done
echo ok
