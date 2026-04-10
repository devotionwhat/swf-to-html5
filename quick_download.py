import requests
import os
import re
import urllib.request

SAVE_DIR = "/home/z/my-project/flash-archives/swf-files"
os.makedirs(SAVE_DIR, exist_ok=True)

# Quick test - download a few known SWF files from Archive.org
test_files = [
    "https://archive.org/download/swf-flash-games/Street%20Fighter%20II%20-%20Ryu%20Vs.%20Sagat.swf",
    "https://archive.org/download/swf-flash-games/super_mario_63.swf",
    "https://archive.org/download/flash_201609/flash.swf",
]

for url in test_files:
    filename = url.split('/')[-1]
    clean_name = re.sub(r'[^\w\-.]', '_', filename)
    dest_path = os.path.join(SAVE_DIR, "action", clean_name)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    print(f"Downloading: {filename[:50]}")
    try:
        urllib.request.urlretrieve(url, dest_path)
        size = os.path.getsize(dest_path)
        print(f"  ✓ Success: {size/1024:.1f} KB")
    except Exception as e:
        print(f"  ✗ Failed: {e}")

# List what we have
print("\n" + "="*50)
print("Files downloaded so far:")
for root, dirs, files in os.walk(SAVE_DIR):
    for f in files:
        if f.endswith('.swf'):
            path = os.path.join(root, f)
            size = os.path.getsize(path)
            print(f"  {f}: {size/1024:.1f} KB")
