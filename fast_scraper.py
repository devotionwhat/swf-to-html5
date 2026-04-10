#!/usr/bin/env python3
"""
Fast Flash Museum Scraper - Downloads a curated list of top games
"""

import os
import re
import json
import time
import requests
from pathlib import Path

OUTPUT_DIR = Path("/home/z/my-project/swf_games")
SIZE_LIMIT = 1 * 1024 * 1024 * 1024  # Start with 1GB

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

session = requests.Session()
session.headers.update(HEADERS)
total_size = 0
downloaded_games = []

# Curated list of popular flash games with known SWF URLs
# These are well-known popular games
POPULAR_GAMES = [
    # Action
    {"name": "Age of War", "url": "https://flashmuseum.org/age-of-war/", "category": "action"},
    {"name": "Age of War 2", "url": "https://flashmuseum.org/age-of-war-2/", "category": "action"},
    {"name": "Raze", "url": "https://flashmuseum.org/raze/", "category": "action"},
    {"name": "Raze 2", "url": "https://flashmuseum.org/raze-2/", "category": "action"},
    {"name": "Raze 3", "url": "https://flashmuseum.org/raze-3/", "category": "action"},
    # Strategy
    {"name": "Kingdom Rush", "url": "https://flashmuseum.org/kingdom-rush/", "category": "strategy"},
    {"name": "Bloons TD 5", "url": "https://flashmuseum.org/bloons-td-5/", "category": "strategy"},
    {"name": "Cursed Treasure 2", "url": "https://flashmuseum.org/cursed-treasure-2/", "category": "strategy"},
    # Puzzle
    {"name": "Red Remover", "url": "https://flashmuseum.org/red-remover/", "category": "puzzle"},
    {"name": "Splitter 2", "url": "https://flashmuseum.org/splitter-2/", "category": "puzzle"},
    # Adventure
    {"name": "Epic Battle Fantasy 3", "url": "https://flashmuseum.org/epic-battle-fantasy-3/", "category": "adventure"},
    {"name": "Epic Battle Fantasy 4", "url": "https://flashmuseum.org/epic-battle-fantasy-4/", "category": "adventure"},
    {"name": "Sonny", "url": "https://flashmuseum.org/sonny/", "category": "adventure"},
    {"name": "Sonny 2", "url": "https://flashmuseum.org/sonny-2/", "category": "adventure"},
    # Shooter
    {"name": "Strike Force Heroes", "url": "https://flashmuseum.org/strike-force-heroes/", "category": "shooter"},
    {"name": "Strike Force Heroes 2", "url": "https://flashmuseum.org/strike-force-heroes-2/", "category": "shooter"},
    # Idle
    {"name": "Clicker Heroes", "url": "https://flashmuseum.org/clicker-heroes/", "category": "clicker"},
    {"name": "Adventure Capitalist", "url": "https://flashmuseum.org/adventure-capitalist/", "category": "clicker"},
    # Platformer
    {"name": "Learn to Fly", "url": "https://flashmuseum.org/learn-to-fly/", "category": "platformer"},
    {"name": "Learn to Fly 2", "url": "https://flashmuseum.org/learn-to-fly-2/", "category": "platformer"},
    {"name": "Learn to Fly 3", "url": "https://flashmuseum.org/learn-to-fly-3/", "category": "platformer"},
    # Tower Defense
    {"name": "Bloons Tower Defense", "url": "https://flashmuseum.org/bloons-tower-defense/", "category": "tower-defense"},
    {"name": "Bloons Tower Defense 2", "url": "https://flashmuseum.org/bloons-tower-defense-2/", "category": "tower-defense"},
    # Arcade
    {"name": "Flight", "url": "https://flashmuseum.org/flight/", "category": "arcade"},
    {"name": "Into Space", "url": "https://flashmuseum.org/into-space/", "category": "arcade"},
    {"name": "Into Space 2", "url": "https://flashmuseum.org/into-space-2/", "category": "arcade"},
]

def get_page(url):
    try:
        time.sleep(0.2)
        r = session.get(url, timeout=30)
        return r.text
    except Exception as e:
        print(f"Error: {e}")
        return ""

def extract_swf_url(html):
    """Extract SWF URL from game page"""
    # Try launchCommand
    match = re.search(r"'launchCommand':'([^']+\.swf[^']*)'", html)
    if match:
        return match.group(1)
    
    # Try fileName + rootURL
    file_match = re.search(r"'fileName':'([^']+\.swf)'", html)
    root_match = re.search(r"'rootURL':'([^']+)'", html)
    if file_match and root_match:
        return f"{root_match.group(1)}/games/{file_match.group(1)}"
    
    return None

def download_file(url, output_path, name):
    global total_size
    try:
        r = session.get(url, timeout=120, stream=True)
        r.raise_for_status()
        
        size = int(r.headers.get('Content-Length', 0))
        
        if total_size + size > SIZE_LIMIT:
            print(f"[SKIP] {name} - size limit")
            return 0
        
        total_size += size
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✓ {name}: {size/1024/1024:.1f}MB (Total: {total_size/1024**3:.2f}GB)")
        return size
    except Exception as e:
        print(f"✗ {name}: {e}")
        return 0

def main():
    global total_size, downloaded_games
    
    print("=" * 60)
    print("Fast Flash Museum Scraper")
    print(f"Target: {SIZE_LIMIT/1024**3:.1f}GB")
    print(f"Games: {len(POPULAR_GAMES)}")
    print("=" * 60)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    for game in POPULAR_GAMES:
        if total_size >= SIZE_LIMIT:
            print("\nSize limit reached!")
            break
        
        print(f"\n[{game['category']}] {game['name']}")
        
        # Get SWF URL
        html = get_page(game['url'])
        if not html:
            continue
        
        swf_url = extract_swf_url(html)
        if not swf_url:
            print(f"  No SWF URL found")
            continue
        
        # Download
        safe_name = re.sub(r'[^\w\s-]', '', game['name'])[:50].replace(' ', '_')
        output_path = OUTPUT_DIR / game['category'] / f"{safe_name}.swf"
        
        size = download_file(swf_url, output_path, game['name'])
        if size > 0:
            downloaded_games.append({
                'name': game['name'],
                'url': game['url'],
                'swf_url': swf_url,
                'category': game['category'],
                'file_size': size,
                'local_path': str(output_path)
            })
    
    # Save metadata
    with open('/home/z/my-project/games_metadata.json', 'w') as f:
        json.dump(downloaded_games, f, indent=2)
    
    print("\n" + "=" * 60)
    print(f"COMPLETE: {len(downloaded_games)} games, {total_size/1024**3:.2f}GB")
    print("=" * 60)

if __name__ == "__main__":
    main()
