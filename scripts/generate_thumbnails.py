#!/usr/bin/env python3
"""
Generate thumbnails for SWF files using Ruffle exporter.
Works with category subdirectories.
Runs on GitHub Actions or locally.
"""

import os
import subprocess
import sys
from pathlib import Path

ASSETS_DIR = "assets"
RUFFLE_EXPORTER = os.path.expanduser("~/ruffle/exporter")

def download_ruffle_exporter():
    """Download Ruffle exporter if not exists"""
    ruffle_dir = os.path.expanduser("~/ruffle")
    exporter_path = os.path.join(ruffle_dir, "exporter")
    
    if os.path.exists(exporter_path):
        print(f"✓ Ruffle exporter already exists at {exporter_path}")
        return exporter_path
    
    print("Downloading Ruffle exporter...")
    os.makedirs(ruffle_dir, exist_ok=True)
    
    # Download pre-built Linux binary
    url = "https://github.com/ruffle-rs/ruffle/releases/download/nightly-2024-01-15/exporter-linux-x86_64.tar.gz"
    tar_path = os.path.join(ruffle_dir, "exporter.tar.gz")
    
    try:
        import urllib.request
        print(f"  Downloading from {url}")
        urllib.request.urlretrieve(url, tar_path)
        
        print("  Extracting...")
        subprocess.run(["tar", "-xzf", tar_path, "-C", ruffle_dir], check=True)
        
        # Make executable
        os.chmod(exporter_path, 0o755)
        
        # Cleanup
        os.remove(tar_path)
        
        print(f"✓ Installed to {exporter_path}")
        return exporter_path
        
    except Exception as e:
        print(f"✗ Failed to download: {e}")
        return None


def generate_thumbnail(swf_path, exporter_path):
    """Generate a thumbnail for a SWF file"""
    swf_dir = os.path.dirname(swf_path)
    swf_name = Path(swf_path).stem
    thumb_path = os.path.join(swf_dir, f"{swf_name}.png")
    
    # Skip if thumbnail exists
    if os.path.exists(thumb_path):
        return "exists", thumb_path
    
    # Generate thumbnail
    try:
        result = subprocess.run(
            [exporter_path, swf_path, thumb_path, "--frame", "50"],
            capture_output=True,
            timeout=30
        )
        
        if os.path.exists(thumb_path):
            return "created", thumb_path
        else:
            return "failed", None
            
    except subprocess.TimeoutExpired:
        return "timeout", None
    except Exception as e:
        return "error", str(e)


def main():
    print("=" * 50)
    print("THUMBNAIL GENERATION")
    print("=" * 50)
    
    # Download Ruffle exporter
    exporter_path = download_ruffle_exporter()
    if not exporter_path:
        print("ERROR: Could not get Ruffle exporter")
        sys.exit(1)
    
    # Find all SWF files
    print(f"\nScanning {ASSETS_DIR} for SWF files...")
    swf_files = []
    for root, dirs, files in os.walk(ASSETS_DIR):
        for f in files:
            if f.lower().endswith('.swf'):
                swf_files.append(os.path.join(root, f))
    
    print(f"Found {len(swf_files)} SWF files")
    
    # Generate thumbnails
    stats = {"exists": 0, "created": 0, "failed": 0, "timeout": 0, "error": 0}
    
    for i, swf_path in enumerate(swf_files):
        rel_path = os.path.relpath(swf_path, ASSETS_DIR)
        print(f"\n[{i+1}/{len(swf_files)}] {rel_path}")
        
        status, result = generate_thumbnail(swf_path, exporter_path)
        stats[status] += 1
        
        if status == "exists":
            print(f"  ✓ Thumbnail exists")
        elif status == "created":
            size = os.path.getsize(result)
            print(f"  ✓ Created ({size} bytes)")
        else:
            print(f"  ✗ {status}: {result}")
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Total SWF files: {len(swf_files)}")
    print(f"Thumbnails already existed: {stats['exists']}")
    print(f"Thumbnails created: {stats['created']}")
    print(f"Failed: {stats['failed'] + stats['timeout'] + stats['error']}")


if __name__ == "__main__":
    main()
