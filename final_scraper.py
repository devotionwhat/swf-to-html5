#!/usr/bin/env python3
"""
Flash Museum Game Scraper - Downloads top games by category
Target: ~4GB total, organized by category folders
"""

import os
import re
import json
import time
import math
import requests
from pathlib import Path
from urllib.parse import urlparse

# Configuration
OUTPUT_DIR = Path("/home/z/my-project/swf_games")
SIZE_LIMIT = 4.1 * 1024 * 1024 * 1024  # 4.1GB
GAMES_PER_CATEGORY = 10

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

session = requests.Session()
session.headers.update(HEADERS)
total_size = 0
downloaded_games = []

def get_page(url):
    """Fetch a page with error handling"""
    try:
        time.sleep(0.3)  # Rate limiting
        r = session.get(url, timeout=30)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

def extract_categories(html):
    """Extract categories from tags page"""
    pattern = r'class="button-term"[^>]*href="https://flashmuseum\.org/browse/tags/([^/]+)/[^"]*"[^>]*>\s*([^<]+)\s*\((\d+)\)'
    matches = re.findall(pattern, html)
    
    categories = []
    for slug, name, count in matches:
        categories.append({
            'slug': slug,
            'name': name.strip(),
            'count': int(count),
            'url': f"https://flashmuseum.org/browse/tags/{slug}/"
        })
    
    # Sort by count (most games first)
    categories.sort(key=lambda x: x['count'], reverse=True)
    return categories

def get_game_urls(category_url, max_games=20):
    """Get game URLs from category page"""
    html = get_page(category_url)
    
    # Find game links - they are direct links to game pages
    # Exclude navigation/category links
    all_links = re.findall(r'href="(https://flashmuseum\.org/([a-z0-9-]+)/)"', html)
    
    exclude = ['browse', 'tag', 'feed', 'page', 'comments', 'wp-', 'random', 'library']
    games = []
    
    for url, slug in all_links:
        if not any(ex in url for ex in exclude) and len(slug) > 3:
            # Check it's not a category URL
            if '/browse/' not in url:
                games.append(url)
    
    # Remove duplicates while preserving order
    seen = set()
    unique = []
    for url in games:
        if url not in seen:
            seen.add(url)
            unique.append(url)
    
    return unique[:max_games]

def extract_game_info(html, game_url, category):
    """Extract SWF URL and metadata from game page"""
    # Extract title
    title_match = re.search(r'<title>([^|]+)\s*\|', html)
    name = title_match.group(1).strip() if title_match else "Unknown"
    
    # Extract SWF configuration
    # Pattern 1: launchCommand with full URL
    launch_match = re.search(r"'launchCommand':'([^']+\.swf[^']*)'", html)
    
    # Pattern 2: fileName + rootURL
    file_match = re.search(r"'fileName':'([^']+\.swf)'", html)
    root_match = re.search(r"'rootURL':'([^']+)'", html)
    
    swf_url = None
    if launch_match:
        swf_url = launch_match.group(1)
    elif file_match and root_match:
        swf_url = f"{root_match.group(1)}/games/{file_match.group(1)}"
    
    # Extract rating
    rating_match = re.search(r'"ratingValue"\s*:\s*([\d.]+)', html)
    count_match = re.search(r'"ratingCount"\s*:\s*(\d+)', html)
    
    rating = float(rating_match.group(1)) if rating_match else 0
    rating_count = int(count_match.group(1)) if count_match else 0
    
    # Calculate popularity score (rating * log(rating_count + 1))
    popularity = rating * math.log10(rating_count + 1) if rating > 0 else 0
    
    return {
        'name': name,
        'url': game_url,
        'swf_url': swf_url,
        'category': category,
        'rating': rating,
        'rating_count': rating_count,
        'popularity': popularity
    }

def get_file_size(url):
    """Get file size via HEAD request"""
    try:
        r = session.head(url, timeout=10, allow_redirects=True)
        return int(r.headers.get('Content-Length', 0))
    except:
        return 0

def download_file(url, output_path, game_name):
    """Download a SWF file"""
    global total_size
    
    try:
        r = session.get(url, timeout=120, stream=True)
        r.raise_for_status()
        
        size = int(r.headers.get('Content-Length', 0))
        
        # Check size limit
        if total_size + size > SIZE_LIMIT:
            print(f"  [SKIP] {game_name} - would exceed size limit")
            return False
        
        total_size += size
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"  ✓ {game_name}: {size / (1024*1024):.1f}MB (Total: {total_size / (1024**3):.2f}GB)")
        return size
        
    except Exception as e:
        print(f"  ✗ Error downloading {game_name}: {e}")
        return 0

def main():
    global total_size, downloaded_games
    
    print("=" * 70)
    print("Flash Museum Game Scraper")
    print(f"Target size: {SIZE_LIMIT / (1024**3):.1f}GB")
    print(f"Games per category: {GAMES_PER_CATEGORY}")
    print("=" * 70)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Fetch main tags page
    print("\nFetching categories...")
    html = get_page("https://flashmuseum.org/browse/tags/")
    
    if not html:
        print("Failed to fetch tags page!")
        return
    
    categories = extract_categories(html)
    print(f"Found {len(categories)} categories")
    
    # Process each category
    for cat in categories:
        if total_size >= SIZE_LIMIT:
            print("\n[SIZE LIMIT REACHED]")
            break
        
        print(f"\n[{cat['name']}] ({cat['count']} games)")
        
        # Get game URLs from category
        game_urls = get_game_urls(cat['url'], max_games=GAMES_PER_CATEGORY * 2)
        
        # Extract info and sort by popularity
        games_info = []
        for url in game_urls:
            if total_size >= SIZE_LIMIT:
                break
            
            game_html = get_page(url)
            if game_html:
                info = extract_game_info(game_html, url, cat['slug'])
                if info['swf_url']:
                    games_info.append(info)
        
        # Sort by popularity
        games_info.sort(key=lambda x: x['popularity'], reverse=True)
        
        # Download top games
        downloaded = 0
        for game in games_info:
            if total_size >= SIZE_LIMIT:
                break
            if downloaded >= GAMES_PER_CATEGORY:
                break
            
            # Create safe filename (max 100 chars)
            safe_name = re.sub(r'[^\w\s-]', '', game['name']).strip().replace(' ', '_')
            safe_name = safe_name[:100]  # Truncate to avoid filename too long error
            if not safe_name:
                safe_name = game['url'].split('/')[-2][:100]
            
            category_dir = OUTPUT_DIR / cat['slug']
            output_path = category_dir / f"{safe_name}.swf"
            
            # Skip if already downloaded
            if output_path.exists():
                size = output_path.stat().st_size
                total_size += size
                print(f"  [EXISTS] {game['name']}: {size / (1024*1024):.1f}MB")
                downloaded += 1
                continue
            
            # Download
            size = download_file(game['swf_url'], output_path, game['name'])
            if size > 0:
                game['file_size'] = size
                game['local_path'] = str(output_path)
                downloaded_games.append(game)
                downloaded += 1
    
    # Save metadata
    print("\n" + "=" * 70)
    print("Saving metadata...")
    with open('/home/z/my-project/games_metadata.json', 'w') as f:
        json.dump(downloaded_games, f, indent=2)
    
    print("=" * 70)
    print("SCRAPING COMPLETE!")
    print(f"Total games: {len(downloaded_games)}")
    print(f"Total size: {total_size / (1024**3):.2f}GB")
    print(f"Output: {OUTPUT_DIR}")
    print("=" * 70)

if __name__ == "__main__":
    main()
