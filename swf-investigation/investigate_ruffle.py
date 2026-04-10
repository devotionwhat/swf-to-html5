import requests
import re
import json

# Ruffle is an EMULATOR, not a converter
# It plays SWF files directly in browser via WebAssembly
# Let's find where FlashMuseum actually stores SWF files

print("=" * 60)
print("INVESTIGATING: FlashMuseum + Ruffle Architecture")
print("=" * 60)

# Check a specific game page to find SWF source
test_urls = [
    "https://flashmuseum.org/age-of-war/",
    "https://flashmuseum.org/earn-to-die/",
    "https://flashmuseum.org/happy-wheels/",
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

for url in test_urls:
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        html = resp.text
        
        # Look for SWF URLs
        swf_matches = re.findall(r'(https?://[^\s"\'<>]+\.swf)', html)
        
        # Look for Ruffle configuration
        ruffle_config = re.findall(r'new\s+Ruffle\s*\([^)]*\)', html)
        
        # Look for any JSON config
        json_configs = re.findall(r'var\s+\w+\s*=\s*(\{[^;]+\})', html)
        
        print(f"\n--- {url} ---")
        print(f"SWF URLs found: {len(swf_matches)}")
        for swf in swf_matches[:3]:
            print(f"  - {swf}")
        
        print(f"Ruffle instances: {len(ruffle_config)}")
        
        # Look for data attributes
        data_attrs = re.findall(r'data-[a-z-]+=["\']([^"\']+)["\']', html)
        swf_data = [d for d in data_attrs if '.swf' in d.lower() or 'flash' in d.lower()]
        if swf_data:
            print(f"SWF data attrs: {swf_data[:3]}")
            
    except Exception as e:
        print(f"Error with {url}: {e}")

print("\n" + "=" * 60)
print("SEARCHING GITHUB FOR FLASH GAME ARCHIVES")
print("=" * 60)
