#!/bin/bash
# Generate thumbnails for SWF files using Ruffle exporter
# Works with category subdirectories

PATH_TO_RUFFLE_BASE=~/ruffle
PATH_TO_ASSETS=`pwd`/assets

echo "=========================================="
echo "THUMBNAIL GENERATION SCRIPT"
echo "=========================================="
echo "RUFFLE_BASE: ${PATH_TO_RUFFLE_BASE}"
echo "ASSETS: ${PATH_TO_ASSETS}"
echo ""

# Check if Ruffle exporter exists
if [ ! -f "${PATH_TO_RUFFLE_BASE}/exporter" ]; then
    echo "ERROR: Ruffle exporter not found at ${PATH_TO_RUFFLE_BASE}/exporter"
    echo "Please install Ruffle exporter first:"
    echo "  mkdir -p ~/ruffle"
    echo "  cd ~/ruffle"
    echo "  wget https://github.com/ruffle-rs/ruffle/releases/download/nightly-2024-01-15/exporter-linux-x86_64.tar.gz"
    echo "  tar -xzf exporter-linux-x86_64.tar.gz"
    exit 1
fi

cd ${PATH_TO_RUFFLE_BASE}

TOTAL=0
SUCCESS=0
SKIPPED=0

# Find ALL SWF files recursively (including subdirectories)
echo "Finding SWF files in subdirectories..."
while IFS= read -r -d '' swf_file; do
    TOTAL=$((TOTAL + 1))
    
    # Get directory and filename
    SWF_DIR=$(dirname "$swf_file")
    SWF_BASENAME=$(basename "$swf_file")
    SWF_TITLE="${SWF_BASENAME%.swf}"  # Remove .swf extension
    
    # Expected thumbnail path (same directory as SWF)
    THUMB_PATH="${SWF_DIR}/${SWF_TITLE}.png"
    
    echo ""
    echo "[$TOTAL] Processing: ${SWF_BASENAME}"
    echo "  Directory: ${SWF_DIR#$PATH_TO_ASSETS/}"
    
    # Check if thumbnail already exists
    if [ -f "$THUMB_PATH" ]; then
        echo "  ✓ Thumbnail exists: ${SWF_TITLE}.png"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi
    
    # Generate thumbnail
    echo "  Generating thumbnail..."
    timeout 30s ${PATH_TO_RUFFLE_BASE}/exporter "$swf_file" "$THUMB_PATH" --frame 50 2>/dev/null
    
    if [ -f "$THUMB_PATH" ]; then
        SIZE=$(stat -f%z "$THUMB_PATH" 2>/dev/null || stat -c%s "$THUMB_PATH" 2>/dev/null)
        echo "  ✓ Created: ${SWF_TITLE}.png (${SIZE} bytes)"
        SUCCESS=$((SUCCESS + 1))
    else
        echo "  ✗ Failed to generate thumbnail"
    fi
    
done < <(find ${PATH_TO_ASSETS} -name "*.swf" -type f -print0)

echo ""
echo "=========================================="
echo "SUMMARY"
echo "=========================================="
echo "Total SWF files: ${TOTAL}"
echo "Thumbnails generated: ${SUCCESS}"
echo "Already existed: ${SKIPPED}"
echo "Failed: $((TOTAL - SUCCESS - SKIPPED))"
