import requests
import os
import json
import time
import urllib.request
from urllib.parse import unquote

# Load mapping
with open('game_mapping.json', 'r') as f:
    mapping = json.load(f)

ARCHIVE_BASE = mapping['archive_base']
categories = mapping['categories']

# Create assets directory structure
ASSETS_DIR = 'assets'
os.makedirs(ASSETS_DIR, exist_ok=True)

# Download settings
MAX_PER_CATEGORY = 15  # Limit per category to reach ~4GB
total_size = 0
downloaded_count = 0

print("=" * 60)
print("DOWNLOADING SWF FILES TO ASSETS FOLDER")
print("=" * 60)

for category, games in categories.items():
    if category == 'other':
        continue  # Skip uncategorized for now
    
    # Create category folder
    cat_dir = os.path.join(ASSETS_DIR, category)
    os.makedirs(cat_dir, exist_ok=True)
    
    print(f"\n[{category.upper()}] - {len(games)} games available")
    
    for game in games[:MAX_PER_CATEGORY]:
        # Clean filename
        clean_name = unquote(game)
        dest_path = os.path.join(cat_dir, clean_name)
        
        # Skip if already exists
        if os.path.exists(dest_path):
            size = os.path.getsize(dest_path)
            total_size += size
            downloaded_count += 1
            print(f"  ✓ EXISTS: {clean_name[:50]} ({size/1024:.1f} KB)")
            continue
        
        # Download
        url = ARCHIVE_BASE + game
        try:
            print(f"  Downloading: {clean_name[:50]}...", end=" ")
            urllib.request.urlretrieve(url, dest_path)
            size = os.path.getsize(dest_path)
            total_size += size
            downloaded_count += 1
            print(f"✓ {size/1024:.1f} KB")
            time.sleep(0.2)
        except Exception as e:
            print(f"✗ {e}")

print("\n" + "=" * 60)
print("DOWNLOAD SUMMARY")
print("=" * 60)
print(f"Files downloaded: {downloaded_count}")
print(f"Total size: {total_size/1024/1024:.2f} MB ({total_size/1024/1024/1024:.2f} GB)")

# List directory structure
print("\n=== FOLDER STRUCTURE ===")
for cat in sorted(os.listdir(ASSETS_DIR)):
    cat_path = os.path.join(ASSETS_DIR, cat)
    if os.path.isdir(cat_path):
        files = [f for f in os.listdir(cat_path) if f.endswith('.swf')]
        size = sum(os.path.getsize(os.path.join(cat_path, f)) for f in files)
        print(f"{cat}: {len(files)} games, {size/1024/1024:.1f} MB")
