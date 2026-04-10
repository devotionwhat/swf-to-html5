#!/usr/bin/env python3
"""
Generate HTML structure for Flash Games Archive.
Creates:
1. index.html - Main page with category cards (with thumbnails)
2. assets/[category].html - Category pages showing ALL games
3. assets/[category]/[game].swf.html - Individual game pages (centered, full screen)
"""

import os
import random
from pathlib import Path

ASSETS_DIR = "assets"
RUFFLE_CDN = "https://cdn.jsdelivr.net/npm/ruffle-mirror@latest/ruffle.js"

CATEGORY_NAMES = {
    'action': 'Action Games', 'adventure': 'Adventure Games', 'arcade': 'Arcade Games',
    'board-game': 'Board Games', 'card': 'Card Games', 'casino': 'Casino Games',
    'defense': 'Tower Defense', 'dress-up': 'Dress Up Games', 'driving': 'Driving Games',
    'education': 'Education Games', 'fighting': 'Fighting Games', 'girls': 'Girls Games',
    'jigsaw': 'Jigsaw Puzzles', 'kids': 'Kids Games', 'make-up': 'Make Up Games',
    'matching': 'Matching Games', 'multiplayer': 'Multiplayer Games', 'other': 'Other Games',
    'puzzles': 'Puzzle Games', 'racing': 'Racing Games', 'rpg': 'RPG Games',
    'shooting': 'Shooting Games', 'sports': 'Sports Games', 'strategy': 'Strategy Games'
}

# Category icons/emojis for visual appeal
CATEGORY_ICONS = {
    'action': '⚔️', 'adventure': '🗺️', 'arcade': '👾', 'board-game': '🎲',
    'card': '🃏', 'casino': '🎰', 'defense': '🏰', 'dress-up': '👗',
    'driving': '🚗', 'education': '📚', 'fighting': '🥊', 'girls': '👸',
    'jigsaw': '🧩', 'kids': '🧸', 'make-up': '💄', 'matching': '💎',
    'multiplayer': '👥', 'other': '🎮', 'puzzles': '🧠', 'racing': '🏁',
    'rpg': '🐉', 'shooting': '🎯', 'sports': '⚽', 'strategy': '♟️'
}

def get_random_image():
    images_dir = "images"
    if os.path.exists(images_dir):
        images = [f for f in os.listdir(images_dir) if f.lower().endswith(('.jpg', '.png', '.gif'))]
        if images:
            return f"images/{random.choice(images)}"
    return "images/landscape.jpg"

def generate_game_page(swf_filename, game_title, category):
    """Generate individual game play page - CENTERED and FULL SCREEN"""
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>{game_title}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:100%;height:100%;overflow:hidden;background:#1a1a2e}}
#game-container{{width:100vw;height:100vh;display:flex;align-items:center;justify-content:center}}
#game-container embed,#game-container object,#game-container canvas{{max-width:100%;max-height:100%;display:block}}
.back{{position:fixed;top:15px;left:15px;background:rgba(255,255,255,0.2);color:white;
text-decoration:none;padding:10px 20px;border-radius:25px;z-index:1000;backdrop-filter:blur(10px)}}
.back:hover{{background:rgba(255,255,255,0.3)}}
.fullscreen{{position:fixed;top:15px;right:15px;background:rgba(255,255,255,0.2);color:white;
border:none;padding:10px 20px;border-radius:25px;z-index:1000;cursor:pointer;backdrop-filter:blur(10px)}}
.fullscreen:hover{{background:rgba(255,255,255,0.3)}}
</style></head>
<body>
<a href="../{category}.html" class="back">← Back to {CATEGORY_NAMES.get(category, category)}</a>
<button class="fullscreen" onclick="toggleFullscreen()">⛶ Fullscreen</button>
<div id="game-container"><embed src="{swf_filename}" type="application/x-shockwave-flash"></div>
<script src="{RUFFLE_CDN}"></script>
<script>
function toggleFullscreen() {{
    if (!document.fullscreenElement) document.documentElement.requestFullscreen();
    else document.exitFullscreen();
}}
</script>
</body></html>'''

def get_thumbnail(swf_path, category, filename):
    """Get thumbnail for a game - check for actual thumbnail first, then random"""
    swf_dir = os.path.dirname(swf_path)
    base_name = filename.rsplit('.', 1)[0]
    
    # Check for thumbnail files
    for ext in ['.png', '.jpg', '.gif']:
        thumb_path = os.path.join(swf_dir, base_name + ext)
        if os.path.exists(thumb_path):
            return f"assets/{category}/{base_name}{ext}"
    
    # Fall back to random placeholder - use correct relative path from assets/
    return f"../images/{random.choice(os.listdir('images')) if os.path.exists('images') else 'landscape.jpg'}"

def generate_category_page(category, games):
    """Generate category page showing ALL games with thumbnails"""
    display_name = CATEGORY_NAMES.get(category, category.title())
    icon = CATEGORY_ICONS.get(category, '🎮')
    games_html = ""
    
    for g in games:
        # Use relative path from assets/ folder
        img = g.get('thumbnail') or f"../images/{random.choice(os.listdir('images')) if os.path.exists('images') else 'landscape.jpg'}"
        games_html += f'''<div class="game" onclick="location.href='{g['category']}/{g['html']}'">
<img src="{img}" alt="{g['title']}" onerror="this.src='../images/landscape.jpg'">
<div class="title"><p>{g['title']}</p></div></div>\n'''
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>{display_name} - Flash Games Archive</title>
<style>*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);min-height:100vh;color:white}}
.header{{background:rgba(0,0,0,0.3);padding:20px;text-align:center;backdrop-filter:blur(10px)}}
.header h1{{font-size:2em;text-shadow:2px 2px 4px rgba(0,0,0,0.5)}}
.back{{display:inline-block;background:rgba(255,255,255,0.2);color:white;text-decoration:none;
padding:10px 25px;border-radius:25px;margin:15px;transition:all 0.3s}}
.back:hover{{background:rgba(255,255,255,0.3);transform:translateY(-2px)}}
.games{{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));
gap:20px;padding:20px;max-width:1400px;margin:0 auto}}
.game{{background:rgba(255,255,255,0.1);border-radius:15px;overflow:hidden;cursor:pointer;
transition:all 0.3s;aspect-ratio:3/4;position:relative}}
.game:hover{{transform:translateY(-5px);box-shadow:0 10px 30px rgba(0,0,0,0.4)}}
.game img{{width:100%;height:100%;object-fit:cover}}
.game .title{{position:absolute;bottom:0;left:0;right:0;padding:15px 10px;
background:linear-gradient(transparent,rgba(0,0,0,0.9))}}
.game .title p{{font-size:13px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.stats{{background:rgba(0,0,0,0.3);padding:15px;text-align:center;color:rgba(255,255,255,0.7)}}</style>
</head><body><div class="header"><h1>{icon} {display_name}</h1><p>{len(games)} games</p>
<a href="../index.html" class="back">← All Categories</a></div>
<div class="games">{games_html}</div>
<div class="stats"><p>{len(games)} games | Ruffle Flash Emulator</p></div></body></html>'''

def generate_index(categories_data):
    """Generate main index with category cards WITH THUMBNAILS"""
    total = sum(len(g) for g in categories_data.values())
    cats_html = ""
    
    # List of available images for category backgrounds
    images = [f for f in os.listdir('images') if f.lower().endswith(('.jpg', '.png', '.gif'))] if os.path.exists('images') else ['landscape.jpg']
    
    for cat in sorted(categories_data.keys()):
        games = categories_data[cat]
        name = CATEGORY_NAMES.get(cat, cat.title())
        icon = CATEGORY_ICONS.get(cat, '🎮')
        # Pick a random image for each category
        img = f"images/{random.choice(images)}"
        cats_html += f'''<div class="cat" onclick="location.href='assets/{cat}.html'" style="background-image:linear-gradient(rgba(0,0,0,0.5),rgba(0,0,0,0.7)),url('{img}');background-size:cover;background-position:center">
<span class="icon">{icon}</span>
<h2>{name}</h2><div class="count">{len(games)}</div><div class="label">games</div></div>\n'''
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Flash Games Archive</title>
<style>*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);min-height:100vh;color:white}}
.header{{background:rgba(0,0,0,0.3);padding:20px;text-align:center;backdrop-filter:blur(10px)}}
.header h1{{font-size:2.5em;text-shadow:2px 2px 4px rgba(0,0,0,0.5)}}
.header p{{color:rgba(255,255,255,0.7)}}
.cats{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));
gap:25px;padding:30px;max-width:1400px;margin:0 auto}}
.cat{{border-radius:20px;padding:30px;text-align:center;
cursor:pointer;transition:all 0.3s;border:2px solid rgba(255,255,255,0.1);min-height:180px;
display:flex;flex-direction:column;justify-content:center;align-items:center}}
.cat:hover{{transform:translateY(-8px) scale(1.02);border-color:rgba(255,255,255,0.4);box-shadow:0 20px 50px rgba(0,0,0,0.4)}}
.cat .icon{{font-size:3em;margin-bottom:10px}}
.cat h2{{font-size:1.3em;margin-bottom:8px;text-shadow:2px 2px 4px rgba(0,0,0,0.5)}}
.cat .count{{font-size:2.2em;font-weight:bold;color:#4fc3f7;text-shadow:2px 2px 4px rgba(0,0,0,0.3)}}
.cat .label{{color:rgba(255,255,255,0.7);font-size:0.9em}}
.stats{{background:rgba(0,0,0,0.3);padding:15px;text-align:center;color:rgba(255,255,255,0.7)}}</style>
</head><body><div class="header"><h1>🎮 Flash Games Archive</h1>
<p>{total} classic Flash games preserved with Ruffle</p></div>
<div class="cats">{cats_html}</div>
<div class="stats"><p>{total} games across {len(categories_data)} categories | Click a category to play</p></div>
</body></html>'''

def main():
    print("=== Generating HTML Structure ===")
    print("Structure: index.html → category pages → game pages\n")
    
    categories_data = {}
    total_games = 0
    total_size = 0
    
    # Scan SWF files by category
    if os.path.exists(ASSETS_DIR):
        for category in os.listdir(ASSETS_DIR):
            cat_path = os.path.join(ASSETS_DIR, category)
            if os.path.isdir(cat_path) and not category.startswith('.'):
                categories_data[category] = []
                
                for filename in os.listdir(cat_path):
                    if filename.lower().endswith('.swf'):
                        swf_path = os.path.join(cat_path, filename)
                        title = Path(filename).stem
                        html_file = f"{filename}.html"
                        html_path = os.path.join(cat_path, html_file)
                        
                        # Generate game page (OVERWRITE, not append)
                        with open(html_path, 'w', encoding='utf-8') as f:
                            f.write(generate_game_page(filename, title, category))
                        
                        size = os.path.getsize(swf_path)
                        total_size += size
                        total_games += 1
                        
                        categories_data[category].append({
                            'title': title, 'category': category,
                            'swf': swf_path, 'html': html_file, 'size': size
                        })
                
                print(f"  {category}: {len(categories_data[category])} games")
    
    # Generate category pages
    print("\nGenerating category pages...")
    for category, games in categories_data.items():
        cat_html = generate_category_page(category, games)
        cat_path = os.path.join(ASSETS_DIR, f"{category}.html")
        with open(cat_path, 'w', encoding='utf-8') as f:
            f.write(cat_html)
        print(f"  Created: assets/{category}.html")
    
    # Generate index
    print("\nGenerating index.html...")
    with open("index.html", 'w', encoding='utf-8') as f:
        f.write(generate_index(categories_data))
    
    print(f"\n{'='*50}")
    print(f"COMPLETE: {total_games} games, {total_size/1024/1024:.1f} MB, {len(categories_data)} categories")
    print("="*50)

if __name__ == '__main__':
    main()
