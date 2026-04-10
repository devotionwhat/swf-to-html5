import requests
import re
import json
from html.parser import HTMLParser

# FlashMuseum categories from earlier scan
CATEGORIES = [
    "action", "adventure", "arcade", "board-game", "card", "casino",
    "defense", "dress-up", "driving", "education", "fighting", "girls",
    "jigsaw", "kids", "make-up", "matching", "multiplayer", "other",
    "puzzles", "racing", "rpg", "shooting", "sports", "strategy"
]

# Get Archive.org SWF file list
class SWFParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.files = []
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr, value in attrs:
                if attr == 'href' and value.endswith('.swf'):
                    self.files.append(value)

print("Fetching Archive.org SWF list...")
resp = requests.get("https://archive.org/download/swf-flash-games/", timeout=30)
parser = SWFParser()
parser.feed(resp.text)
print(f"Found {len(parser.files)} SWF files on Archive.org")

# Categorize function
def categorize_game(filename):
    name = filename.lower()
    name_decoded = requests.utils.unquote(filename).lower()
    
    keywords = {
        'action': ['fight', 'battle', 'combat', 'war', 'attack', 'strike', 'ninja', 'samurai', 'kung'],
        'adventure': ['adventure', 'quest', 'explore', 'escape', 'survival', 'island'],
        'arcade': ['arcade', 'classic', 'retro', 'pong', 'breakout', 'asteroid', 'space invader'],
        'board-game': ['board', 'chess', 'checkers', 'monopoly', 'dice', 'ludo'],
        'card': ['card', 'poker', 'solitaire', 'blackjack', 'hearts', 'bridge'],
        'casino': ['casino', 'slot', 'roulette', 'betting', 'gambl'],
        'defense': ['tower', 'defense', 'td', 'defend', 'protect', 'castle defense'],
        'dress-up': ['dress', 'fashion', 'wardrobe', 'style', 'outfit'],
        'driving': ['drive', 'driving', 'car', 'truck', 'bus', 'taxi', 'parking'],
        'education': ['math', 'spell', 'learn', 'education', 'teach', 'school', 'quiz'],
        'fighting': ['fight', 'fighter', 'versus', 'vs', 'mortal kombat', 'street fighter'],
        'girls': ['girl', 'princess', 'fairy', 'mermaid', 'pony', 'unicorn'],
        'jigsaw': ['jigsaw', 'puzzle piece'],
        'kids': ['kid', 'child', 'cartoon', 'disney', 'nickelodeon', 'dora'],
        'make-up': ['makeup', 'make-up', 'beauty', 'salon', 'spa', 'nail'],
        'matching': ['match', 'match3', 'match-3', 'bejeweled', 'candy', 'gem'],
        'multiplayer': ['multiplayer', '2 player', 'two player', 'versus'],
        'puzzles': ['puzzle', 'sudoku', 'tetris', '2048', 'brain', 'logic', 'sokoban'],
        'racing': ['race', 'racing', 'speed', 'formula', 'nascar', 'drag race'],
        'rpg': ['rpg', 'role playing', 'level up', 'stat', 'dungeon', 'fantasy rpg'],
        'shooting': ['shoot', 'gun', 'fps', 'sniper', 'zombie', 'alien', 'weapon'],
        'sports': ['sport', 'football', 'soccer', 'basketball', 'baseball', 'golf', 'tennis', 'bowling', 'pool', 'billiard'],
        'strategy': ['strategy', 'tactics', 'manage', 'tycoon', 'sim', 'build', 'empire']
    }
    
    for category, kws in keywords.items():
        for kw in kws:
            if kw in name or kw in name_decoded:
                return category
    return 'other'

# Categorize all files
categorized = {}
for swf in parser.files:
    cat = categorize_game(swf)
    if cat not in categorized:
        categorized[cat] = []
    categorized[cat].append(swf)

print("\n=== GAMES BY CATEGORY (matching FlashMuseum categories) ===")
for cat in sorted(categorized.keys()):
    count = len(categorized[cat])
    print(f"{cat}: {count} games")

# Save the mapping
mapping = {
    'archive_base': 'https://archive.org/download/swf-flash-games/',
    'categories': categorized
}
with open('game_mapping.json', 'w') as f:
    json.dump(mapping, f, indent=2)
print(f"\nSaved mapping to game_mapping.json")

# Print sample games per category
print("\n=== SAMPLE GAMES PER CATEGORY ===")
for cat in ['action', 'adventure', 'puzzles', 'racing', 'shooting', 'sports', 'strategy']:
    if cat in categorized:
        print(f"\n{cat.upper()}:")
        for game in categorized[cat][:5]:
            clean_name = requests.utils.unquote(game)
            print(f"  - {clean_name}")
