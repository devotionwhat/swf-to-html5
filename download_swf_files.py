import requests
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

headers = {
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'SWF-Downloader'
}

# Directory to save SWF files
SAVE_DIR = "/home/z/my-project/flash-archives/swf-files"
os.makedirs(SAVE_DIR, exist_ok=True)

def download_file(url, dest_path):
    """Download a file from URL"""
    try:
        resp = requests.get(url, timeout=60, stream=True)
        if resp.status_code == 200:
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            with open(dest_path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True, len(resp.content)
        return False, f"HTTP {resp.status_code}"
    except Exception as e:
        return False, str(e)

def get_repo_contents(owner, repo, path=''):
    """Get contents of a repo directory"""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return resp.json()
    return None

def download_swf_from_repo(owner, repo, category="misc"):
    """Download all SWF files from a repo"""
    print(f"\nDownloading from {owner}/{repo}...")
    
    contents = get_repo_contents(owner, repo)
    if not contents:
        print(f"  Could not fetch contents")
        return []
    
    downloaded = []
    for item in contents:
        if item['type'] == 'file' and item['name'].endswith('.swf'):
            # Categorize based on filename
            name_lower = item['name'].lower()
            if 'papa' in name_lower or 'pizzeria' in name_lower or 'burgeria' in name_lower:
                cat = "restaurant"
            elif 'tower' in name_lower or 'defense' in name_lower:
                cat = "strategy"
            elif 'sonic' in name_lower or 'mario' in name_lower:
                cat = "platformer"
            elif 'puzzle' in name_lower or 'tetris' in name_lower or '2048' in name_lower:
                cat = "puzzle"
            elif 'duck' in name_lower or 'run' in name_lower:
                cat = "racing"
            else:
                cat = category
            
            dest_dir = os.path.join(SAVE_DIR, cat)
            dest_path = os.path.join(dest_dir, item['name'])
            
            # Get download URL
            download_url = item.get('download_url')
            if download_url:
                print(f"  Downloading: {item['name']} ({item['size']/1024:.1f} KB) -> {cat}/")
                success, result = download_file(download_url, dest_path)
                if success:
                    downloaded.append({
                        'name': item['name'],
                        'category': cat,
                        'size': result,
                        'path': dest_path
                    })
                else:
                    print(f"    Failed: {result}")
    
    return downloaded

# Download from smaller repos first
all_downloaded = []

# SJRNoodles/Flash-Game-Archive
downloaded = download_swf_from_repo("SJRNoodles", "Flash-Game-Archive", "action")
all_downloaded.extend(downloaded)

# plasterboy83/Flash-Archive
downloaded = download_swf_from_repo("plasterboy83", "Flash-Archive", "puzzle")
all_downloaded.extend(downloaded)

print(f"\n{'='*60}")
print(f"DOWNLOAD SUMMARY")
print(f"{'='*60}")
total_size = sum(d['size'] for d in all_downloaded)
print(f"Total files downloaded: {len(all_downloaded)}")
print(f"Total size: {total_size/1024/1024:.2f} MB")

# Save manifest
manifest_path = os.path.join(SAVE_DIR, 'manifest.json')
with open(manifest_path, 'w') as f:
    json.dump(all_downloaded, f, indent=2)
print(f"\nManifest saved to: {manifest_path}")
