import requests
import os
import json
import time
import urllib.request

# Directory to save SWF files
SAVE_DIR = "/home/z/my-project/flash-archives/swf-files"
os.makedirs(SAVE_DIR, exist_ok=True)

def download_file(url, dest_path):
    """Download a file using urllib (more reliable)"""
    try:
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        urllib.request.urlretrieve(url, dest_path)
        size = os.path.getsize(dest_path)
        return True, size
    except Exception as e:
        return False, str(e)

# SWF files to download (from our GitHub API scan)
swf_files = [
    # SJRNoodles/Flash-Game-Archive
    ("https://raw.githubusercontent.com/SJRNoodles/Flash-Game-Archive/main/2048%20(1).swf", "puzzle/2048.swf"),
    ("https://raw.githubusercontent.com/SJRNoodles/Flash-Game-Archive/main/Fireboy%20and%20Watergirl%20in%20The%20Light%20Temple.swf", "action/fireboy-watergirl-light-temple.swf"),
    ("https://raw.githubusercontent.com/SJRNoodles/Flash-Game-Archive/main/Papas%20Burgeria.swf", "restaurant/papas-burgeria.swf"),
    ("https://raw.githubusercontent.com/SJRNoodles/Flash-Game-Archive/main/Papas%20Freezeria.swf", "restaurant/papas-freezeria.swf"),
    ("https://raw.githubusercontent.com/SJRNoodles/Flash-Game-Archive/main/Papas%20Pancakeria.swf", "restaurant/papas-pancakeria.swf"),
    ("https://raw.githubusercontent.com/SJRNoodles/Flash-Game-Archive/main/Papas%20Pizzeria.swf", "restaurant/papas-pizzeria.swf"),
    ("https://raw.githubusercontent.com/SJRNoodles/Flash-Game-Archive/main/bloons-tower-defense-5.swf", "strategy/bloons-td-5.swf"),
    ("https://raw.githubusercontent.com/SJRNoodles/Flash-Game-Archive/main/ducklife1.swf", "racing/duck-life-1.swf"),
    ("https://raw.githubusercontent.com/SJRNoodles/Flash-Game-Archive/main/run2.swf", "racing/run-2.swf"),
    ("https://raw.githubusercontent.com/SJRNoodles/Flash-Game-Archive/main/ultimateflashsonicwidescreen.swf", "platformer/sonic.swf"),
    ("https://raw.githubusercontent.com/SJRNoodles/Flash-Game-Archive/main/pacman.swf", "action/pacman.swf"),
    ("https://raw.githubusercontent.com/SJRNoodles/Flash-Game-Archive/main/bonkio.swf", "action/bonkio.swf"),
    ("https://raw.githubusercontent.com/SJRNoodles/Flash-Game-Archive/main/papalouie_v2.swf", "restaurant/papa-louie-2.swf"),
    ("https://raw.githubusercontent.com/SJRNoodles/Flash-Game-Archive/main/papashotdoggeria.swf", "restaurant/papas-hotdoggeria.swf"),
    ("https://raw.githubusercontent.com/SJRNoodles/Flash-Game-Archive/main/tetris%20(2).swf", "puzzle/tetris.swf"),
    # plasterboy83/Flash-Archive
    ("https://raw.githubusercontent.com/plasterboy83/Flash-Archive/main/whg.swf", "puzzle/worlds-hardest-game.swf"),
    ("https://raw.githubusercontent.com/plasterboy83/Flash-Archive/main/whg2.swf", "puzzle/worlds-hardest-game-2.swf"),
]

print(f"Downloading {len(swf_files)} SWF files...")
print("="*60)

all_downloaded = []
total_size = 0

for url, rel_path in swf_files:
    dest_path = os.path.join(SAVE_DIR, rel_path)
    filename = os.path.basename(rel_path)
    category = os.path.dirname(rel_path)
    
    print(f"Downloading: {filename} -> {category}/")
    success, result = download_file(url, dest_path)
    
    if success:
        size_kb = result / 1024
        print(f"  ✓ Success: {size_kb:.1f} KB")
        total_size += result
        all_downloaded.append({
            'name': filename,
            'category': category,
            'size': result,
            'path': dest_path
        })
    else:
        print(f"  ✗ Failed: {result}")
    
    time.sleep(0.2)  # Small delay between downloads

print("\n" + "="*60)
print("DOWNLOAD SUMMARY")
print("="*60)
print(f"Total files downloaded: {len(all_downloaded)}")
print(f"Total size: {total_size/1024/1024:.2f} MB")

# List by category
categories = {}
for item in all_downloaded:
    cat = item['category']
    if cat not in categories:
        categories[cat] = []
    categories[cat].append(item['name'])

print("\nBy Category:")
for cat, files in categories.items():
    print(f"  {cat}: {len(files)} games")

# Save manifest
manifest_path = os.path.join(SAVE_DIR, 'manifest.json')
with open(manifest_path, 'w') as f:
    json.dump(all_downloaded, f, indent=2)
print(f"\nManifest saved to: {manifest_path}")
