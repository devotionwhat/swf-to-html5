#!/usr/bin/env python3
"""
Download SWF files from Archive.org and organize by category.
This script runs on GitHub Actions or Codespaces - downloads directly to repo.

Categories match FlashMuseum.org structure:
- action, adventure, arcade, board-game, card, casino
- defense, dress-up, driving, education, fighting, girls
- jigsaw, kids, make-up, matching, multiplayer, other
- puzzles, racing, rpg, shooting, sports, strategy
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

# Configuration
ARCHIVE_BASE = "https://archive.org/download/swf-flash-games/"
ASSETS_DIR = "assets"
MANIFEST_FILE = "assets/manifest.json"

# Category keywords (matching FlashMuseum.org categories)
CATEGORY_KEYWORDS = {
    'action': ['fight', 'battle', 'combat', 'war', 'attack', 'strike', 'ninja', 'samurai', 'kung', 'assassin'],
    'adventure': ['adventure', 'quest', 'explore', 'escape', 'survival', 'island', 'journey'],
    'arcade': ['arcade', 'classic', 'retro', 'pong', 'breakout', 'asteroid', 'space invader', 'frogger', 'pacman'],
    'board-game': ['board', 'chess', 'checkers', 'monopoly', 'dice', 'ludo', 'backgammon'],
    'card': ['card', 'poker', 'solitaire', 'blackjack', 'hearts', 'bridge', 'uno'],
    'casino': ['casino', 'slot', 'roulette', 'betting', 'gambl'],
    'defense': ['tower', 'defense', 'td', 'defend', 'protect', 'castle'],
    'dress-up': ['dress', 'fashion', 'wardrobe', 'style', 'outfit', 'clothing'],
    'driving': ['drive', 'driving', 'car', 'truck', 'bus', 'taxi', 'parking', 'traffic'],
    'education': ['math', 'spell', 'learn', 'education', 'teach', 'school', 'quiz', 'typing'],
    'fighting': ['versus', 'vs', 'mortal kombat', 'street fighter', 'tekken', 'fighter'],
    'girls': ['girl', 'princess', 'fairy', 'mermaid', 'pony', 'unicorn', 'barbie'],
    'jigsaw': ['jigsaw', 'puzzle piece'],
    'kids': ['kid', 'child', 'cartoon', 'disney', 'nickelodeon', 'dora', 'spongebob'],
    'make-up': ['makeup', 'make-up', 'beauty', 'salon', 'spa', 'nail', 'hair'],
    'matching': ['match', 'match3', 'match-3', 'bejeweled', 'candy', 'gem', 'bubble shooter'],
    'multiplayer': ['multiplayer', '2 player', 'two player'],
    'puzzles': ['puzzle', 'sudoku', 'tetris', '2048', 'brain', 'logic', 'sokoban', 'slide'],
    'racing': ['race', 'racing', 'speed', 'formula', 'nascar', 'drag', 'moto', 'bike'],
    'rpg': ['rpg', 'role playing', 'level up', 'dungeon', 'fantasy', 'dragon', 'knight'],
    'shooting': ['shoot', 'gun', 'fps', 'sniper', 'zombie', 'alien', 'weapon', 'hominid'],
    'sports': ['sport', 'football', 'soccer', 'basketball', 'baseball', 'golf', 'tennis', 'bowling', 'pool', 'billiard', 'ski', 'snowboard'],
    'strategy': ['strategy', 'tactics', 'manage', 'tycoon', 'sim', 'build', 'empire', 'civilization']
}


class SWFListParser(HTMLParser):
    """Parse Archive.org directory listing for SWF files"""
    def __init__(self):
        super().__init__()
        self.files = []
        
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr, value in attrs:
                if attr == 'href' and value.endswith('.swf'):
                    self.files.append(value)


def categorize_game(filename):
    """Categorize a game based on filename keywords"""
    name = urllib.parse.unquote(filename).lower()
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in name:
                return category
    return 'other'


def get_swf_list():
    """Fetch list of SWF files from Archive.org"""
    print(f"Fetching SWF list from {ARCHIVE_BASE}")
    
    try:
        response = requests.get(ARCHIVE_BASE, timeout=30)
        parser = SWFListParser()
        parser.feed(response.text)
        print(f"Found {len(parser.files)} SWF files")
        return parser.files
    except Exception as e:
        print(f"Error fetching SWF list: {e}")
        return []


def download_file(url, dest_path):
    """Download a file from URL to destination path"""
    try:
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        urllib.request.urlretrieve(url, dest_path)
        return True, os.path.getsize(dest_path)
    except Exception as e:
        return False, str(e)


def main():
    parser = argparse.ArgumentParser(description='Download SWF games from Archive.org')
    parser.add_argument('--max-per-category', type=int, default=20, help='Max games per category')
    parser.add_argument('--categories', type=str, default='all', help='Categories to download (comma-separated)')
    args = parser.parse_args()
    
    # Parse categories filter
    if args.categories.lower() == 'all':
        categories_filter = None
    else:
        categories_filter = [c.strip().lower() for c in args.categories.split(',')]
    
    # Get SWF file list
    swf_files = get_swf_list()
    if not swf_files:
        print("No SWF files found!")
        return
    
    # Categorize all files
    categorized = {}
    for swf in swf_files:
        category = categorize_game(swf)
        if category not in categorized:
            categorized[category] = []
        categorized[category].append(swf)
    
    print(f"\n=== Categories found ===")
    for cat in sorted(categorized.keys()):
        print(f"  {cat}: {len(categorized[cat])} games")
    
    # Download files
    manifest = {'games': [], 'total_size': 0, 'categories': {}}
    total_downloaded = 0
    total_size = 0
    
    print(f"\n=== Downloading (max {args.max_per_category} per category) ===")
    
    for category in sorted(categorized.keys()):
        # Skip if not in filter
        if categories_filter and category not in categories_filter:
            continue
            
        games = categorized[category][:args.max_per_category]
        cat_dir = os.path.join(ASSETS_DIR, category)
        
        print(f"\n[{category.upper()}] Downloading {len(games)} games...")
        
        manifest['categories'][category] = {'count': 0, 'size': 0}
        
        for swf in games:
            clean_name = urllib.parse.unquote(swf)
            dest_path = os.path.join(cat_dir, clean_name)
            
            # Skip if exists
            if os.path.exists(dest_path):
                size = os.path.getsize(dest_path)
                print(f"  ✓ EXISTS: {clean_name[:50]} ({size/1024:.1f} KB)")
                total_size += size
                total_downloaded += 1
                manifest['games'].append({
                    'name': clean_name,
                    'category': category,
                    'size': size,
                    'status': 'exists'
                })
                manifest['categories'][category]['count'] += 1
                manifest['categories'][category]['size'] += size
                continue
            
            # Download
            url = ARCHIVE_BASE + swf
            print(f"  Downloading: {clean_name[:50]}...", end=" ")
            
            success, result = download_file(url, dest_path)
            
            if success:
                print(f"✓ {result/1024:.1f} KB")
                total_size += result
                total_downloaded += 1
                manifest['games'].append({
                    'name': clean_name,
                    'category': category,
                    'size': result,
                    'status': 'downloaded'
                })
                manifest['categories'][category]['count'] += 1
                manifest['categories'][category]['size'] += result
            else:
                print(f"✗ {result}")
            
            time.sleep(0.1)  # Small delay
    
    # Save manifest
    manifest['total_size'] = total_size
    os.makedirs(ASSETS_DIR, exist_ok=True)
    with open(MANIFEST_FILE, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n{'='*60}")
    print("DOWNLOAD SUMMARY")
    print("="*60)
    print(f"Total games: {total_downloaded}")
    print(f"Total size: {total_size/1024/1024:.2f} MB ({total_size/1024/1024/1024:.2f} GB)")
    print(f"Manifest saved to: {MANIFEST_FILE}")


if __name__ == '__main__':
    main()
