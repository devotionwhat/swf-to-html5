import requests
import os
import re
import urllib.request
import time
from html.parser import HTMLParser

SAVE_DIR = "/home/z/my-project/flash-archives/swf-files"
os.makedirs(SAVE_DIR, exist_ok=True)

class ArchiveFileParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.files = []
        
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr, value in attrs:
                if attr == 'href' and value.endswith('.swf'):
                    self.files.append(value)

def get_archive_files(archive_url):
    """Get list of SWF files from Archive.org directory"""
    try:
        resp = requests.get(archive_url, timeout=30)
        parser = ArchiveFileParser()
        parser.feed(resp.text)
        return parser.files
    except Exception as e:
        print(f"Error fetching {archive_url}: {e}")
        return []

# Archive.org SWF collections
archives = [
    "https://archive.org/download/swf-flash-games/",
    "https://archive.org/download/flash_201609/",
]

all_files = []
for archive_url in archives:
    print(f"\nScanning: {archive_url}")
    files = get_archive_files(archive_url)
    print(f"  Found {len(files)} SWF files")
    all_files.extend([(archive_url, f) for f in files])
    
    # Show first 10 files
    for f in files[:10]:
        print(f"    - {f}")
    if len(files) > 10:
        print(f"    ... and {len(files)-10} more")

print(f"\n{'='*60}")
print(f"Total SWF files found: {len(all_files)}")
print(f"{'='*60}")

# Download files (limit to 50 for now)
download_limit = 50
downloaded = []
total_size = 0

print(f"\nDownloading first {download_limit} files...")

for i, (base_url, filename) in enumerate(all_files[:download_limit]):
    url = base_url + filename
    
    # Categorize based on filename
    name_lower = filename.lower()
    if any(x in name_lower for x in ['mario', 'sonic', 'platform', 'jump']):
        category = "platformer"
    elif any(x in name_lower for x in ['puzzle', 'match', '2048', 'tetris', 'sudoku']):
        category = "puzzle"
    elif any(x in name_lower for x in ['racing', 'car', 'drive', 'race']):
        category = "racing"
    elif any(x in name_lower for x in ['shoot', 'gun', 'fps', 'weapon']):
        category = "shooter"
    elif any(x in name_lower for x in ['tower', 'defense', 'td', 'strategy']):
        category = "strategy"
    elif any(x in name_lower for x in ['adventure', 'rpg', 'quest']):
        category = "adventure"
    elif any(x in name_lower for x in ['sport', 'football', 'soccer', 'basketball', 'golf']):
        category = "sports"
    else:
        category = "action"
    
    dest_dir = os.path.join(SAVE_DIR, category)
    # Clean filename
    clean_name = re.sub(r'[^\w\-.]', '_', filename)
    dest_path = os.path.join(dest_dir, clean_name)
    
    print(f"  [{i+1}/{download_limit}] {filename[:40]} -> {category}/")
    
    try:
        os.makedirs(dest_dir, exist_ok=True)
        urllib.request.urlretrieve(url, dest_path)
        size = os.path.getsize(dest_path)
        total_size += size
        downloaded.append({
            'name': clean_name,
            'category': category,
            'size': size,
            'original_url': url
        })
        print(f"    ✓ {size/1024:.1f} KB")
    except Exception as e:
        print(f"    ✗ {e}")
    
    time.sleep(0.3)

print(f"\n{'='*60}")
print("DOWNLOAD SUMMARY")
print("="*60)
print(f"Files downloaded: {len(downloaded)}")
print(f"Total size: {total_size/1024/1024:.2f} MB")

# By category
categories = {}
for item in downloaded:
    cat = item['category']
    if cat not in categories:
        categories[cat] = 0
    categories[cat] += item['size']

print("\nBy Category:")
for cat, size in sorted(categories.items(), key=lambda x: -x[1]):
    print(f"  {cat}: {size/1024/1024:.2f} MB")

# Save manifest
import json
manifest_path = os.path.join(SAVE_DIR, 'archive_manifest.json')
with open(manifest_path, 'w') as f:
    json.dump(downloaded, f, indent=2)
print(f"\nManifest: {manifest_path}")
