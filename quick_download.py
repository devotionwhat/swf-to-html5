import requests
import os
import json
import urllib.request
from urllib.parse import unquote

with open('game_mapping.json', 'r') as f:
    mapping = json.load(f)

ARCHIVE_BASE = mapping['archive_base']
ASSETS_DIR = 'assets'

# Just download top games from each category
top_games = [
    # Action
    ("action", "1942 Battles In The Sky.swf"),
    ("action", "Alien Hominid.swf"),
    ("action", "Apple Shooter.swf"),
    # Adventure  
    ("adventure", "Big Truck Adventures 2.swf"),
    # Arcade
    ("arcade", "3D Frogger.swf"),
    ("arcade", "4way Pong.swf"),
    # Driving
    ("driving", "3D Car Racing.swf"),
    ("driving", "3D Rally Racing.swf"),
    # Racing
    ("racing", "3D Motorbike Racer.swf"),
    # Shooting
    ("shooting", "Alien Hominid.swf"),
    # Sports
    ("sports", "Billiards.swf"),
    ("sports", "Bowling (Big Fish Games).swf"),
    # Strategy
    ("strategy", "Build Your Coaster.swf"),
    # Puzzles
    ("puzzles", "Tetris (2).swf"),
]

print("Quick download test...")
total = 0

for category, game in top_games:
    cat_dir = os.path.join(ASSETS_DIR, category)
    os.makedirs(cat_dir, exist_ok=True)
    
    dest = os.path.join(cat_dir, game)
    if os.path.exists(dest):
        size = os.path.getsize(dest)
        total += size
        print(f"✓ EXISTS: {category}/{game} ({size/1024:.1f} KB)")
        continue
    
    # URL encode the filename
    encoded = requests.utils.quote(game)
    url = ARCHIVE_BASE + encoded
    
    try:
        urllib.request.urlretrieve(url, dest)
        size = os.path.getsize(dest)
        total += size
        print(f"✓ DOWNLOADED: {category}/{game} ({size/1024:.1f} KB)")
    except Exception as e:
        print(f"✗ FAILED: {category}/{game} - {e}")

print(f"\nTotal: {total/1024/1024:.2f} MB")
