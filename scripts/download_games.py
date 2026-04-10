#!/usr/bin/env python3
"""
Download SWF files from multiple sources and organize by category.
Sources: Archive.org, GitHub repos
"""

import os
import sys
import json
import time
import argparse
import urllib.request
import urllib.parse
from html.parser import HTMLParser

try:
    import requests
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

ASSETS_DIR = "assets"
MANIFEST_FILE = "assets/manifest.json"

# Category keywords
CATEGORY_KEYWORDS = {
    'action': ['fight', 'battle', 'combat', 'war', 'attack', 'strike', 'ninja', 'samurai', 'kung'],
    'adventure': ['adventure', 'quest', 'explore', 'escape', 'survival', 'island', 'journey'],
    'arcade': ['arcade', 'classic', 'retro', 'pong', 'breakout', 'asteroid', 'frogger', 'pacman'],
    'board-game': ['board', 'chess', 'checkers', 'monopoly', 'dice', 'ludo'],
    'card': ['card', 'poker', 'solitaire', 'blackjack', 'hearts', 'bridge'],
    'casino': ['casino', 'slot', 'roulette', 'betting', 'gambl'],
    'defense': ['tower', 'defense', 'td', 'defend', 'protect', 'castle'],
    'dress-up': ['dress', 'fashion', 'wardrobe', 'style', 'outfit'],
    'driving': ['drive', 'driving', 'car', 'truck', 'bus', 'taxi', 'parking'],
    'education': ['math', 'spell', 'learn', 'education', 'teach', 'school', 'quiz'],
    'fighting': ['versus', 'vs', 'mortal kombat', 'street fighter', 'tekken'],
    'girls': ['girl', 'princess', 'fairy', 'mermaid', 'pony', 'unicorn'],
    'jigsaw': ['jigsaw', 'puzzle piece'],
    'kids': ['kid', 'child', 'cartoon', 'disney', 'nickelodeon', 'dora'],
    'make-up': ['makeup', 'make-up', 'beauty', 'salon', 'spa', 'nail'],
    'matching': ['match', 'match3', 'match-3', 'bejeweled', 'candy', 'gem', 'bubble'],
    'multiplayer': ['multiplayer', '2 player', 'two player'],
    'puzzles': ['puzzle', 'sudoku', 'tetris', '2048', 'brain', 'logic', 'sokoban'],
    'racing': ['race', 'racing', 'speed', 'formula', 'nascar', 'drag', 'moto', 'bike'],
    'rpg': ['rpg', 'role playing', 'level up', 'dungeon', 'fantasy', 'dragon'],
    'shooting': ['shoot', 'gun', 'fps', 'sniper', 'zombie', 'alien', 'weapon'],
    'sports': ['sport', 'football', 'soccer', 'basketball', 'baseball', 'golf', 'tennis', 'bowling', 'pool', 'billiard'],
    'strategy': ['strategy', 'tactics', 'manage', 'tycoon', 'sim', 'build', 'empire']
}

# GitHub sources
GITHUB_SOURCES = [
    {'repo': 'AmmarSAA/Flash-Games-Directory', 'api': 'https://api.github.com/repos/AmmarSAA/Flash-Games-Directory/contents', 'raw': 'https://raw.githubusercontent.com/AmmarSAA/Flash-Games-Directory/main/'},
    {'repo': 'SJRNoodles/Flash-Game-Archive', 'api': 'https://api.github.com/repos/SJRNoodles/Flash-Game-Archive/contents', 'raw': 'https://raw.githubusercontent.com/SJRNoodles/Flash-Game-Archive/main/'},
    {'repo': 'plasterboy83/Flash-Archive', 'api': 'https://api.github.com/repos/plasterboy83/Flash-Archive/contents', 'raw': 'https://raw.githubusercontent.com/plasterboy83/Flash-Archive/main/'},
]


class SWFParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.files = []
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr, value in attrs:
                if attr == 'href' and value.endswith('.swf'):
                    self.files.append(value)


def categorize(filename):
    name = urllib.parse.unquote(filename).lower()
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in name:
                return cat
    return 'other'


def get_archive_files():
    """Get SWF files from Archive.org"""
    print("Fetching from Archive.org...")
    try:
        resp = requests.get("https://archive.org/download/swf-flash-games/", timeout=30)
        parser = SWFParser()
        parser.feed(resp.text)
        files = [(f, f"https://archive.org/download/swf-flash-games/{f}") for f in parser.files]
        print(f"  Found {len(files)} files")
        return files
    except Exception as e:
        print(f"  Error: {e}")
        return []


def get_github_files():
    """Get SWF files from GitHub repos"""
    all_files = []
    for src in GITHUB_SOURCES:
        print(f"Fetching from {src['repo']}...")
        try:
            resp = requests.get(src['api'], timeout=30)
            if resp.status_code == 200:
                for item in resp.json():
                    if item['type'] == 'file' and item['name'].endswith('.swf'):
                        all_files.append((item['name'], src['raw'] + item['name']))
                print(f"  Found {len([f for f in all_files if src['repo'] in f[1]])} files")
        except Exception as e:
            print(f"  Error: {e}")
    return all_files


def download_file(url, dest):
    try:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        urllib.request.urlretrieve(url, dest)
        return True, os.path.getsize(dest)
    except Exception as e:
        return False, str(e)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-per-category', type=int, default=1000)
    parser.add_argument('--categories', type=str, default='all')
    args = parser.parse_args()
    
    filter_cats = None if args.categories.lower() == 'all' else [c.strip().lower() for c in args.categories.split(',')]
    
    # Collect all files from all sources
    all_files = []
    all_files.extend(get_archive_files())
    all_files.extend(get_github_files())
    print(f"\nTotal files from all sources: {len(all_files)}")
    
    # Categorize
    categorized = {}
    for name, url in all_files:
        cat = categorize(name)
        if cat not in categorized:
            categorized[cat] = []
        categorized[cat].append((name, url))
    
    # Download
    manifest = {'games': [], 'total_size': 0, 'categories': {}}
    total = 0
    total_size = 0
    
    for cat in sorted(categorized.keys()):
        if filter_cats and cat not in filter_cats:
            continue
        
        files = categorized[cat][:args.max_per_category]
        cat_dir = os.path.join(ASSETS_DIR, cat)
        manifest['categories'][cat] = {'count': 0, 'size': 0}
        
        print(f"\n[{cat.upper()}] {len(files)} files")
        
        for name, url in files:
            clean = urllib.parse.unquote(name)
            dest = os.path.join(cat_dir, clean)
            
            if os.path.exists(dest):
                size = os.path.getsize(dest)
                total_size += size
                total += 1
                manifest['categories'][cat]['count'] += 1
                manifest['categories'][cat]['size'] += size
                print(f"  ✓ {clean[:40]}: {size//1024}KB")
                continue
            
            ok, result = download_file(url, dest)
            if ok:
                total_size += result
                total += 1
                manifest['categories'][cat]['count'] += 1
                manifest['categories'][cat]['size'] += result
                print(f"  ✓ {clean[:40]}: {result//1024}KB")
            else:
                print(f"  ✗ {clean[:40]}: {result}")
            time.sleep(0.05)
    
    manifest['total_size'] = total_size
    os.makedirs(ASSETS_DIR, exist_ok=True)
    with open(MANIFEST_FILE, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n{'='*50}")
    print(f"DONE: {total} games, {total_size/1024/1024:.1f} MB")
    print(f"Progress: {total_size/1024/1024/4096*100:.1f}% of 4GB target")


if __name__ == '__main__':
    main()
