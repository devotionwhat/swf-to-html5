#!/usr/bin/env python3
"""
Generate HTML wrappers for SWF files.
Creates individual HTML files for each game and a main index.html.

This script handles:
- Category subfolders in assets/
- Filenames with spaces
- Ruffle integration via CDN
- Responsive game display
"""

import os
import json
import random
from pathlib import Path

# Configuration
ASSETS_DIR = "assets"
OUTPUT_INDEX = "index.html"
MANIFEST_FILE = "assets/manifest.json"
RUFFLE_CDN = "https://unpkg.com/@aspect-build/ruffle-wasm@latest/ruffle.js"

# Category display names (proper capitalization)
CATEGORY_NAMES = {
    'action': 'Action',
    'adventure': 'Adventure',
    'arcade': 'Arcade',
    'board-game': 'Board Games',
    'card': 'Card Games',
    'casino': 'Casino',
    'defense': 'Tower Defense',
    'dress-up': 'Dress Up',
    'driving': 'Driving',
    'education': 'Education',
    'fighting': 'Fighting',
    'girls': 'Girls',
    'jigsaw': 'Jigsaw',
    'kids': 'Kids',
    'make-up': 'Make Up',
    'matching': 'Matching',
    'multiplayer': 'Multiplayer',
    'other': 'Other',
    'puzzles': 'Puzzles',
    'racing': 'Racing',
    'rpg': 'RPG',
    'shooting': 'Shooting',
    'sports': 'Sports',
    'strategy': 'Strategy'
}


def get_random_image(images_dir="images"):
    """Get a random placeholder image from the images directory"""
    if not os.path.exists(images_dir):
        return None
    
    images = [f for f in os.listdir(images_dir) 
              if f.lower().endswith(('.jpg', '.png', '.gif'))]
    
    if images:
        return f"{images_dir}/{random.choice(images)}"
    return None


def generate_game_html(swf_path, game_title):
    """Generate HTML wrapper for a single SWF file"""
    return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{game_title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            background: #1a1a2e; 
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        #game-container {{ 
            width: 100vw; 
            height: 100vh; 
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        #back-btn {{
            position: fixed;
            top: 15px;
            left: 15px;
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 14px;
            backdrop-filter: blur(10px);
            z-index: 1000;
            text-decoration: none;
        }}
        #back-btn:hover {{ background: rgba(255,255,255,0.3); }}
        embed {{ width: 100%; height: 100%; }}
    </style>
</head>
<body>
    <a href="../../index.html" id="back-btn">← Back to Games</a>
    <div id="game-container">
        <embed src="../{swf_path}" type="application/x-shockwave-flash">
    </div>
    <script src="{RUFFLE_CDN}"></script>
</body>
</html>'''


def generate_index_html(games_by_category):
    """Generate the main index.html with all games organized by category"""
    
    # Start of HTML
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Flash Games Archive - SWF to HTML5</title>
    <link rel="stylesheet" type="text/css" href="css/auroral2.css">
    <link rel="stylesheet" href="css/cards.css">
    <style>
        * {{ box-sizing: border-box; }}
        body {{ 
            margin: 0; 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        .auroral-info {{
            position: relative;
            z-index: 10;
            padding: 20px;
        }}
        .auroral-info h1 {{
            color: white;
            text-align: center;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            margin-bottom: 5px;
        }}
        .auroral-info .subtitle {{
            color: rgba(255,255,255,0.8);
            text-align: center;
            margin-bottom: 20px;
        }}
        .category-nav {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 8px;
            margin-bottom: 30px;
            padding: 15px;
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
            max-width: 1200px;
            margin-left: auto;
            margin-right: auto;
        }}
        .category-nav a {{
            color: white;
            text-decoration: none;
            padding: 8px 16px;
            background: rgba(255,255,255,0.1);
            border-radius: 20px;
            font-size: 14px;
            transition: all 0.3s;
        }}
        .category-nav a:hover {{
            background: rgba(255,255,255,0.3);
            transform: translateY(-2px);
        }}
        .category-section {{
            margin-bottom: 40px;
            padding: 0 20px;
        }}
        .category-header {{
            color: white;
            font-size: 1.8em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            border-bottom: 2px solid rgba(255,255,255,0.3);
            padding-bottom: 10px;
            margin-bottom: 20px;
            max-width: 1200px;
            margin-left: auto;
            margin-right: auto;
        }}
        .category-header .count {{
            font-size: 0.5em;
            opacity: 0.7;
        }}
        .cards-list {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 20px;
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        .card {{
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            overflow: hidden;
            cursor: pointer;
            transition: all 0.3s;
            aspect-ratio: 3/4;
            position: relative;
        }}
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        .card_image {{
            width: 100%;
            height: 100%;
            position: relative;
        }}
        .card_image img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        .card_title {{
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 15px 10px;
            background: linear-gradient(transparent, rgba(0,0,0,0.8));
        }}
        .card_title p {{
            color: white;
            font-size: 14px;
            margin: 0;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        .stats {{
            text-align: center;
            color: rgba(255,255,255,0.7);
            padding: 20px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="auroral-info">
        <h1>🎮 Flash Games Archive</h1>
        <p class="subtitle">Classic Flash Games Preserved with Ruffle Emulator</p>
        
        <div class="category-nav">
'''
    
    # Add category navigation links
    for category in sorted(games_by_category.keys()):
        display_name = CATEGORY_NAMES.get(category, category.title())
        html += f'            <a href="#{category}">{display_name}</a>\n'
    
    html += '''        </div>
        
        <div class="cards-list">
'''
    
    # Add games by category
    for category in sorted(games_by_category.keys()):
        games = games_by_category[category]
        display_name = CATEGORY_NAMES.get(category, category.title())
        
        # Category header (close previous section, start new)
        html += f'''        </div>
        
        <div class="category-section" id="{category}">
            <h2 class="category-header">{display_name} <span class="count">({len(games)} games)</span></h2>
            <div class="cards-list">
'''
        
        # Add cards for each game
        for game in games:
            name = game['name']
            html_path = game['html_path']
            img_path = game.get('thumbnail') or get_random_image()
            
            html += f'''            <div class="card" onclick="location.href='{html_path}';">
                <div class="card_image">
                    <img src="{img_path}" alt="{name}" onerror="this.src='images/landscape.jpg'">
                    <div class="card_title">
                        <p>{name}</p>
                    </div>
                </div>
            </div>
'''
    
    # Close and add footer
    total_games = sum(len(g) for g in games_by_category.values())
    
    html += f'''        </div>
        
        <div class="stats">
            <p>Total Games: {total_games} | Powered by Ruffle Flash Emulator</p>
        </div>
    </div>
    
    <!-- Background Effects -->
    <div class="container">
        <div id="northern" class="auroral auroral-northern"></div>
        <div id="northern-intense" class="auroral auroral-northern-intense"></div>
        <div id="northern-dimmed" class="auroral auroral-northern-dimmed"></div>
        <div class="auroral-stars"></div>
    </div>
</body>
</html>'''
    
    return html


def main():
    print("=== Generating HTML Wrappers ===")
    
    # Scan for SWF files
    games_by_category = {}
    total_games = 0
    total_size = 0
    
    # Process category subfolders
    if os.path.exists(ASSETS_DIR):
        for category in os.listdir(ASSETS_DIR):
            cat_path = os.path.join(ASSETS_DIR, category)
            
            if os.path.isdir(cat_path):
                games_by_category[category] = []
                
                for filename in os.listdir(cat_path):
                    if filename.lower().endswith('.swf'):
                        swf_path = os.path.join(cat_path, filename)
                        
                        # Generate clean title
                        title = Path(filename).stem
                        
                        # Generate HTML wrapper path
                        html_filename = f"{filename}.html"
                        html_path = os.path.join(cat_path, html_filename)
                        
                        # Write HTML wrapper
                        html_content = generate_game_html(filename, title)
                        with open(html_path, 'w', encoding='utf-8') as f:
                            f.write(html_content)
                        
                        # Get file size
                        size = os.path.getsize(swf_path)
                        total_size += size
                        
                        # Add to games list
                        games_by_category[category].append({
                            'name': title,
                            'swf': swf_path,
                            'html_path': html_path,
                            'size': size
                        })
                        total_games += 1
                
                print(f"  {category}: {len(games_by_category[category])} games")
    
    print(f"\nTotal: {total_games} games, {total_size/1024/1024:.2f} MB")
    
    # Generate index.html
    print("\nGenerating index.html...")
    index_html = generate_index_html(games_by_category)
    with open(OUTPUT_INDEX, 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    print(f"✓ Created {OUTPUT_INDEX}")
    print(f"✓ Generated HTML wrappers for {total_games} games")
    
    return total_games


if __name__ == '__main__':
    main()
