#!/usr/bin/env python3
"""
Flash Museum Scraper - Download top Flash games by category
Target: ~4GB total, organized by category folders
"""

import os
import re
import json
import time
import requests
import urllib.parse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import threading

# Configuration
BASE_URL = "https://flashmuseum.org"
TAGS_URL = f"{BASE_URL}/browse/tags"
OUTPUT_DIR = Path("/home/z/my-project/swf-to-html5/assets")
DOWNLOAD_DIR = Path("/home/z/my-project/swf_games")
METADATA_FILE = Path("/home/z/my-project/games_metadata.json")

# Size limit: 4.1GB (middle of 4-4.2GB range)
SIZE_LIMIT = 4.1 * 1024 * 1024 * 1024  # ~4.1GB in bytes

# Rate limiting
REQUEST_DELAY = 0.5  # seconds between requests
MAX_WORKERS = 5

# Headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

@dataclass
class Game:
    name: str
    url: str
    swf_url: str
    category: str
    rating: float
    rating_count: int
    file_size: int = 0
    downloaded: bool = False
    local_path: str = ""

class FlashScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.total_size = 0
        self.games: List[Game] = []
        self.lock = threading.Lock()
        self.request_count = 0
        
    def get_page(self, url: str) -> str:
        """Fetch a page with rate limiting"""
        time.sleep(REQUEST_DELAY)
        self.request_count += 1
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return ""
    
    def get_all_categories(self) -> List[str]:
        """Extract all category URLs from the tags page"""
        print("Fetching all categories...")
        categories = set()
        
        # Fetch main tags page
        html = self.get_page(f"{BASE_URL}/browse/tags/")
        
        # Extract tag URLs
        pattern = r'href="(https://flashmuseum\.org/browse/tags/[^/]+/)"'
        matches = re.findall(pattern, html)
        categories.update(matches)
        
        # Check for pagination - get all pages
        page_match = re.search(r'/page/(\d+)/', html)
        if page_match:
            max_page = int(page_match.group(1))
            print(f"Found {max_page} pages of categories")
            
            # Fetch a few more pages to get more categories
            for page in range(2, min(max_page + 1, 10)):  # Limit to first 10 pages
                html = self.get_page(f"{BASE_URL}/browse/tags/page/{page}/")
                matches = re.findall(pattern, html)
                categories.update(matches)
        
        print(f"Found {len(categories)} categories")
        return sorted(list(categories))
    
    def get_games_from_category_page(self, category_url: str, page: int = 1) -> List[str]:
        """Get game URLs from a category page"""
        if page == 1:
            url = category_url
        else:
            url = category_url.rstrip('/') + f'/page/{page}/'
        
        html = self.get_page(url)
        
        # Extract game URLs (not tag URLs, not page URLs)
        pattern = r'href="(https://flashmuseum\.org/([a-z0-9-]+)/)"'
        matches = re.findall(pattern, html)
        
        game_urls = []
        exclude_patterns = ['/browse/', '/feed/', '/comments/', '/wp-']
        
        for url, slug in matches:
            # Filter out non-game URLs
            if not any(ex in url for ex in exclude_patterns):
                # Skip if slug contains special keywords that suggest it's not a game
                if not any(kw in slug for kw in ['tag', 'browse', 'category', 'author', 'page']):
                    game_urls.append(url)
        
        return list(set(game_urls))
    
    def extract_game_info(self, game_url: str, category: str) -> Optional[Game]:
        """Extract game information from a game page"""
        html = self.get_page(game_url)
        if not html:
            return None
        
        # Extract game name from title
        title_match = re.search(r'<title>([^|]+)\s*\|', html)
        name = title_match.group(1).strip() if title_match else "Unknown"
        
        # Extract SWF configuration
        config_match = re.search(
            r"const\s*\{[^}]*\}\s*=\s*\{[^}]*'fileName'\s*:\s*'([^']+)'[^}]*"
            r"'gameType'\s*:\s*'([^']+)'[^}]*"
            r"'launchCommand'\s*:\s*'([^']+)'[^}]*"
            r"'rootURL'\s*:\s*'([^']+)'[^}]*"
            r"'uuid'\s*:\s*'([^']+)'",
            html, re.DOTALL
        )
        
        if not config_match:
            # Try alternative pattern
            config_match = re.search(
                r"'fileName':'([^']+)'[^}]*'gameType':'([^']+)'[^}]*"
                r"'launchCommand':'([^']+)'[^}]*'rootURL':'([^']+)'[^}]*'uuid':'([^']+)'",
                html
            )
        
        if not config_match:
            return None
        
        file_name = config_match.group(1)
        game_type = config_match.group(2)
        launch_command = config_match.group(3)
        root_url = config_match.group(4)
        uuid = config_match.group(5)
        
        # Determine SWF URL
        if launch_command and launch_command.startswith('http'):
            swf_url = launch_command
        else:
            # Construct from rootURL and fileName
            swf_url = f"{root_url}/games/{file_name}"
        
        # Extract rating
        rating = 0.0
        rating_count = 0
        rating_match = re.search(r'"ratingValue"\s*:\s*([\d.]+)', html)
        count_match = re.search(r'"ratingCount"\s*:\s*(\d+)', html)
        
        if rating_match:
            rating = float(rating_match.group(1))
        if count_match:
            rating_count = int(count_match.group(1))
        
        return Game(
            name=name,
            url=game_url,
            swf_url=swf_url,
            category=category,
            rating=rating,
            rating_count=rating_count
        )
    
    def get_file_size(self, url: str) -> int:
        """Get file size via HEAD request"""
        try:
            response = self.session.head(url, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                return int(response.headers.get('Content-Length', 0))
        except:
            pass
        return 0
    
    def download_file(self, game: Game, output_path: Path) -> bool:
        """Download a SWF file"""
        try:
            response = self.session.get(game.swf_url, timeout=60, stream=True)
            response.raise_for_status()
            
            size = int(response.headers.get('Content-Length', 0))
            
            with self.lock:
                if self.total_size + size > SIZE_LIMIT:
                    print(f"Size limit reached! Current: {self.total_size / (1024**3):.2f}GB")
                    return False
                self.total_size += size
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            game.file_size = size
            game.downloaded = True
            game.local_path = str(output_path)
            
            print(f"Downloaded: {game.name} ({size / (1024*1024):.2f}MB) - {self.total_size / (1024**3):.2f}GB total")
            return True
            
        except Exception as e:
            print(f"Error downloading {game.name}: {e}")
            return False
    
    def process_category(self, category_url: str, games_per_category: int = 10) -> List[Game]:
        """Process a category and get top games"""
        category_name = category_url.rstrip('/').split('/')[-1]
        print(f"\nProcessing category: {category_name}")
        
        # Get games from first page
        game_urls = self.get_games_from_category_page(category_url)
        
        # If not enough games, get more pages
        page = 2
        while len(game_urls) < games_per_category * 2 and page < 5:
            more_urls = self.get_games_from_category_page(category_url, page)
            if not more_urls:
                break
            game_urls.extend(more_urls)
            page += 1
        
        # Extract info for each game
        category_games = []
        for url in game_urls[:games_per_category * 3]:  # Get more than needed for sorting
            game = self.extract_game_info(url, category_name)
            if game:
                category_games.append(game)
        
        # Sort by rating * log(rating_count) for popularity score
        import math
        category_games.sort(
            key=lambda g: g.rating * math.log10(g.rating_count + 1),
            reverse=True
        )
        
        # Return top games_per_category
        return category_games[:games_per_category]
    
    def run(self, games_per_category: int = 10):
        """Main scraping workflow"""
        print("=" * 60)
        print("Flash Museum Scraper")
        print(f"Target size: {SIZE_LIMIT / (1024**3):.1f}GB")
        print(f"Games per category: {games_per_category}")
        print("=" * 60)
        
        # Create output directories
        DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
        
        # Get all categories
        categories = self.get_all_categories()
        
        # Process each category
        all_games = []
        for cat_url in categories:
            if self.total_size >= SIZE_LIMIT:
                print("\nSize limit reached!")
                break
            
            games = self.process_category(cat_url, games_per_category)
            
            for game in games:
                if self.total_size >= SIZE_LIMIT:
                    break
                
                # Get file size first
                size = self.get_file_size(game.swf_url)
                
                with self.lock:
                    if self.total_size + size > SIZE_LIMIT:
                        continue
                    self.total_size += size
                
                # Download the file
                safe_name = re.sub(r'[^\w\s-]', '', game.name).strip().replace(' ', '_')
                category_dir = DOWNLOAD_DIR / game.category
                output_path = category_dir / f"{safe_name}.swf"
                
                if self.download_file(game, output_path):
                    all_games.append(game)
        
        # Save metadata
        metadata = [asdict(g) for g in all_games]
        with open(METADATA_FILE, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print("\n" + "=" * 60)
        print("SCRAPING COMPLETE!")
        print(f"Total games: {len(all_games)}")
        print(f"Total size: {self.total_size / (1024**3):.2f}GB")
        print(f"Metadata saved to: {METADATA_FILE}")
        print(f"Games saved to: {DOWNLOAD_DIR}")
        print("=" * 60)
        
        return all_games

if __name__ == "__main__":
    scraper = FlashScraper()
    games = scraper.run(games_per_category=10)
