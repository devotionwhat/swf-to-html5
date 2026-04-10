import requests
import os
import json
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# GitHub API to download files directly
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')

headers = {
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'SWF-Downloader'
}
if GITHUB_TOKEN:
    headers['Authorization'] = f'token {GITHUB_TOKEN}'

def get_repo_contents(owner, repo, path=''):
    """Get contents of a repo directory"""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return resp.json()
    return None

def get_rate_limit():
    """Check GitHub API rate limit"""
    resp = requests.get("https://api.github.com/rate_limit", headers=headers)
    return resp.json()

def download_file(url, dest_path):
    """Download a file from URL"""
    try:
        resp = requests.get(url, headers={'User-Agent': 'SWF-Downloader'}, timeout=30)
        if resp.status_code == 200:
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            with open(dest_path, 'wb') as f:
                f.write(resp.content)
            return True, len(resp.content)
    except Exception as e:
        return False, str(e)
    return False, "Unknown error"

# Check rate limit
rate = get_rate_limit()
print(f"GitHub API Rate Limit: {rate['rate']['remaining']}/{rate['rate']['limit']}")

# Start with smaller repos first
repos_to_check = [
    ("SJRNoodles", "Flash-Game-Archive", 57.9),  # 57.9 MB
    ("plasterboy83", "Flash-Archive", 69.1),     # 69 MB
    ("astrovm", "flash", 180),                   # 180 MB
]

for owner, repo, size_mb in repos_to_check:
    print(f"\n{'='*60}")
    print(f"Checking: {owner}/{repo} ({size_mb} MB)")
    print('='*60)
    
    contents = get_repo_contents(owner, repo)
    if contents:
        swf_count = 0
        for item in contents:
            if item['type'] == 'file' and item['name'].endswith('.swf'):
                swf_count += 1
                print(f"  SWF: {item['name']} ({item.get('size', 0)/1024:.1f} KB)")
        
        print(f"\n  Total SWF files: {swf_count}")
    else:
        print("  Could not fetch contents")

