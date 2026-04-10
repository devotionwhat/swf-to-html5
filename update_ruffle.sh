#!/bin/bash
# Updated to use GitHub releases instead of deprecated S3 URL
# Fetches the latest nightly selfhosted build of Ruffle

REPO_API="https://api.github.com/repos/ruffle-rs/ruffle/releases?per_page=1"

echo "Fetching latest Ruffle release info..."
DOWNLOAD_URL=$(curl -s "$REPO_API" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if isinstance(data, list) and len(data) > 0:
    for asset in data[0].get('assets', []):
        if 'selfhosted' in asset.get('name', ''):
            print(asset.get('browser_download_url', ''))
            break
" 2>/dev/null)

if [ -z "$DOWNLOAD_URL" ]; then
    echo "ERROR: Could not find selfhosted download URL."
    echo "Falling back to latest known nightly..."
    DOWNLOAD_URL="https://github.com/ruffle-rs/ruffle/releases/download/nightly-2026-04-09/ruffle-nightly-2026_04_09-web-selfhosted.zip"
fi

echo "Download URL: ${DOWNLOAD_URL}"

rm -rf ruffle_web_latest
mkdir -p ruffle_web_latest
cd ruffle_web_latest

TMPFILE=$(mktemp)
echo "Downloading Ruffle..."
wget "${DOWNLOAD_URL}" -O "${TMPFILE}" 2>&1

echo "Extracting..."
unzip -o "${TMPFILE}" 2>&1

rm "${TMPFILE}"
echo "Done! Ruffle web player is in ruffle_web_latest/"
