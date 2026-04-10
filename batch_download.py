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

# Get current total size
def get_total_size():
    total = 0
    for root, dirs, files in os.walk(SAVE_DIR):
        for f in files:
            if f.endswith('.swf'):
                total += os.path.getsize(os.path.join(root, f))
    return total

# Target: 4GB
TARGET_SIZE = 4 * 1024 * 1024 * 1024  # 4GB

current_size = get_total_size()
print(f"Current size: {current_size/1024/1024:.1f} MB")
print(f"Target size: {TARGET_SIZE/1024/1024/1024:.1f} GB")

# Archive.org collections
archives = [
    "https://archive.org/download/swf-flash-games/",
]

all_swf_urls = []
for archive_url in archives:
    print(f"\nScanning: {archive_url}")
    try:
        resp = requests.get(archive_url, timeout=30)
        parser = ArchiveFileParser()
        parser.feed(resp.text)
        for f in parser.files:
            all_swf_urls.append(archive_url + f)
        print(f"Found {len(parser.files)} SWF files")
    except Exception as e:
        print(f"Error: {e}")

print(f"\nTotal SWF URLs found: {len(all_swf_urls)}")

# Filter out already downloaded files
existing_files = set()
for root, dirs, files in os.walk(SAVE_DIR):
    for f in files:
        if f.endswith('.swf'):
            existing_files.add(f.lower())

to_download = []
for url in all_swf_urls:
    filename = url.split('/')[-1]
    clean_name = re.sub(r'[^\w\-.]', '_', filename)
    if clean_name.lower() not in existing_files:
        to_download.append(url)

print(f"Files to download: {len(to_download)}")

# Download in batches
batch_size = 50
downloaded = 0
errors = 0

for i, url in enumerate(to_download[:500]):  # Limit to 500 files
    filename = url.split('/')[-1]
    clean_name = re.sub(r'[^\w\-.]', '_', filename)
    
    # Categorize
    name_lower = filename.lower()
    if any(x in name_lower for x in ['mario', 'sonic', 'platform', 'jump', 'hedgehog']):
        category = "platformer"
    elif any(x in name_lower for x in ['puzzle', 'match', '2048', 'tetris', 'sudoku', 'brain']):
        category = "puzzle"
    elif any(x in name_lower for x in ['racing', 'car', 'drive', 'race', 'truck', 'moto', 'bike']):
        category = "racing"
    elif any(x in name_lower for x in ['shoot', 'gun', 'fps', 'weapon', 'zombie', 'alien']):
        category = "shooter"
    elif any(x in name_lower for x in ['tower', 'defense', 'td', 'strategy', 'war', 'battle']):
        category = "strategy"
    elif any(x in name_lower for x in ['adventure', 'rpg', 'quest', 'escape']):
        category = "adventure"
    elif any(x in name_lower for x in ['sport', 'football', 'soccer', 'basketball', 'golf', 'tennis', 'ball']):
        category = "sports"
    elif any(x in name_lower for x in ['papa', 'restaurant', 'cooking', 'food']):
        category = "restaurant"
    elif any(x in name_lower for x in ['dress', 'fashion', 'makeup', 'spa']):
        category = "girls"
    else:
        category = "action"
    
    dest_dir = os.path.join(SAVE_DIR, category)
    dest_path = os.path.join(dest_dir, clean_name)
    
    if (i+1) % 10 == 0:
        current = get_total_size()
        print(f"[{i+1}/{len(to_download[:500])}] Size: {current/1024/1024:.1f} MB - {category}/")
    
    try:
        os.makedirs(dest_dir, exist_ok=True)
        urllib.request.urlretrieve(url, dest_path)
        downloaded += 1
    except Exception as e:
        errors += 1
    
    time.sleep(0.1)

final_size = get_total_size()
print(f"\n{'='*60}")
print("FINAL SUMMARY")
print("="*60)
print(f"Downloaded: {downloaded} files")
print(f"Errors: {errors}")
print(f"Total size: {final_size/1024/1024:.1f} MB ({final_size/1024/1024/1024:.2f} GB)")
