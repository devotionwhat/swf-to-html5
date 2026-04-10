#!/usr/bin/env python3
"""
Simple Flash Museum Scraper - Quick extraction and download
"""

import os
import re
import json
import time
import requests
from pathlib import Path
from urllib.parse import urlparse, unquote

# Configuration
BASE_URL = "https://flashmuseum.org"
OUTPUT_DIR = Path("/home/z/my-project/swf_games")
SIZE_LIMIT = 4.1 * 1024 * 1024 * 1024  # 4.1GB

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

session = requests.Session()
session.headers.update(HEADERS)
total_size = 0
downloaded_games = []

def get_page(url):
    try:
        r = session.get(url, timeout=30)
        return r.text
    except Exception as e:
        print(f"Error: {e}")
        return ""

def get_categories():
    """Get all categories from tags page"""
    html = get_page(f"{BASE_URL}/browse/tags/")
    pattern = r'href="(https://flashmuseum\.org/browse/tags/([^/]+)/)"'
    matches = re.findall(pattern, html)
    
    categories = {}
    for url, name in matches:
        if name not in ['feed', 'page']:
            categories[name] = url
    
    print(f"Found {len(categories)} categories")
    return categories

def get_game_urls(category_url, max_games=15):
    """Get game URLs from a category page"""
    html = get_page(category_url)
    
    # Find all game links
    pattern = r'href="(https://flashmuseum\.org/([a-z0-9-]+?)/)"'
    matches = re.findall(pattern, html)
    
    exclude = ['browse', 'tag', 'feed', 'page', 'comments', 'wp-content', 'wp-includes']
    games = []
    
    for url, slug in matches:
        if not any(ex in url for ex in exclude) and len(slug) > 3:
            games.append((url, slug.replace('-', ' ').title()))
    
    # Remove duplicates while preserving order
    seen = set()
    unique_games = []
    for url, name in games:
        if url not in seen:
            seen.add(url)
            unique_games.append((url, name))
    
    return unique_games[:max_games]

def extract_swf_url(game_url):
    """Extract SWF URL from game page"""
    html = get_page(game_url)
    
    # Extract configuration
    patterns = [
        r"'launchCommand':'([^']+\.swf[^']*)'",
        r'"launchCommand":"([^"]+\.swf[^"]*)"',
        r'fileName[\'"]?\s*:\s*[\'"]([^\'"]+\.swf)[\'"]',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, html)
        if match:
            return match.group(1)
    
    # Try to find rootURL and fileName
    root_match = re.search(r"'rootURL':'([^']+)'", html)
    file_match = re.search(r"'fileName':'([^']+\.swf)'", html)
    
    if root_match and file_match:
        return f"{root_match.group(1)}/games/{file_match.group(1)}"
    
    return None

def get_rating(html):
    """Extract rating from game page"""
    rating_match = re.search(r'"ratingValue"\s*:\s*([\d.]+)', html)
    count_match = re.search(r'"ratingCount"\s*:\s*(\d+)', html)
    
    rating = float(rating_match.group(1)) if rating_match else 0
    count = int(count_match.group(1)) if count_match else 0
    
    return rating, count

def download_swf(swf_url, output_path, game_name):
    """Download a SWF file"""
    global total_size
    
    try:
        # Get file size first
        r = session.head(swf_url, timeout=10, allow_redirects=True)
        size = int(r.headers.get('Content-Length', 0))
        
        if size == 0:
            # Try GET request for size
            r = session.get(swf_url, timeout=30, stream=True)
            size = int(r.headers.get('Content-Length', 0))
            if size == 0:
                print(f"  Skipping {game_name} - unknown size")
                return False
        
        if total_size + size > SIZE_LIMIT:
            print(f"  Size limit reached ({total_size / (1024**3):.2f}GB)")
            return False
        
        # Download
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not output_path.exists():
            r = session.get(swf_url, timeout=60, stream=True)
            with open(output_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        
        total_size += size
        print(f"  ✓ {game_name}: {size / (1024*1024):.1f}MB (Total: {total_size / (1024**3):.2f}GB)")
        return True
        
    except Exception as e:
        print(f"  ✗ Error downloading {game_name}: {e}")
        return False

def main():
    global total_size, downloaded_games
    
    print("=" * 60)
    print("Flash Museum Game Scraper")
    print(f"Target: {SIZE_LIMIT / (1024**3):.1f}GB")
    print("=" * 60)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Get categories
    categories = get_categories()
    
    # Process each category
    for cat_name, cat_url in categories.items():
        if total_size >= SIZE_LIMIT:
            print("\nSize limit reached!")
            break
        
        print(f"\n[{cat_name.upper()}]")
        
        # Get games from category
        games = get_game_urls(cat_url, max_games=15)
        
        # Process each game
        for game_url, game_name in games:
            if total_size >= SIZE_LIMIT:
                break
            
            # Get SWF URL
            swf_url = extract_swf_url(game_url)
            
            if swf_url:
                # Create safe filename
                safe_name = re.sub(r'[^\w\s-]', '', game_name).strip().replace(' ', '_')
                category_dir = OUTPUT_DIR / cat_name
                output_path = category_dir / f"{safe_name}.swf"
                
                if download_swf(swf_url, output_path, game_name):
                    downloaded_games.append({
                        'name': game_name,
                        'url': game_url,
                        'swf_url': swf_url,
                        'category': cat_name,
                        'local_path': str(output_path)
                    })
                
                time.sleep(0.3)  # Rate limiting
    
    # Save metadata
    with open('/home/z/my-project/games_metadata.json', 'w') as f:
        json.dump(downloaded_games, f, indent=2)
    
    print("\n" + "=" * 60)
    print("COMPLETE!")
    print(f"Games: {len(downloaded_games)}")
    print(f"Total size: {total_size / (1024**3):.2f}GB")
    print("=" * 60)

if __name__ == "__main__":
    main()
