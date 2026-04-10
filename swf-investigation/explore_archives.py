import requests
import json

print("=" * 70)
print("EXPLORING EXISTING FLASH GAME ARCHIVES")
print("=" * 70)

# Check Archive.org SWF collections
archive_urls = [
    "https://archive.org/download/swf-flash-games/",
    "https://archive.org/details/armorgames",
    "https://archive.org/download/flash_201609/",
]

headers = {'User-Agent': 'Mozilla/5.0'}

for url in archive_urls:
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        print(f"\n{url}")
        print(f"  Status: {resp.status_code}")
        print(f"  Size: {len(resp.text)} bytes")
    except Exception as e:
        print(f"\n{url}")
        print(f"  Error: {e}")

# Check GitHub API for repo sizes
github_repos = [
    "BinBashBanana/gstore",
    "SJRNoodles/Flash-Game-Archive",
    "flashresurrection/Swf",
    "AmmarSAA/Flash-Games-Directory",
    "plasterboy83/Flash-Archive",
    "astrovm/flash"
]

print("\n" + "=" * 70)
print("GITHUB FLASH GAME REPOSITORIES")
print("=" * 70)

for repo in github_repos:
    try:
        api_url = f"https://api.github.com/repos/{repo}"
        resp = requests.get(api_url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            size_kb = data.get('size', 0)
            size_mb = size_kb / 1024
            size_gb = size_mb / 1024
            
            # Get size in human readable
            if size_gb >= 1:
                size_str = f"{size_gb:.2f} GB"
            elif size_mb >= 1:
                size_str = f"{size_mb:.2f} MB"
            else:
                size_str = f"{size_kb} KB"
            
            print(f"\n{repo}:")
            print(f"  Size: {size_str}")
            print(f"  Stars: {data.get('stargazers_count', 0)}")
            print(f"  Description: {data.get('description', 'N/A')[:60]}...")
            print(f"  URL: {data.get('html_url')}")
    except Exception as e:
        print(f"\n{repo}: Error - {e}")

print("\n" + "=" * 70)
