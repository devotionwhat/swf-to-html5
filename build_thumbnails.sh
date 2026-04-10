#!/bin/bash
# Generate thumbnails for SWF game files
# Uses Python/Pillow to create styled game card thumbnails
# Falls back gracefully if Ruffle exporter is available

PATH_TO_ASSETS="$(pwd)/assets"

echo "ASSETS: ${PATH_TO_ASSETS}"

# Check if Ruffle exporter (cargo) is available for real SWF frame extraction
USE_RUFFLE=0
if command -v cargo &> /dev/null && [ -d "$HOME/ruffle" ]; then
    USE_RUFFLE=1
    echo "Ruffle exporter found. Will use for frame extraction."
else
    echo "Ruffle exporter not available. Using Python/Pillow for thumbnail generation."
fi

if [ $USE_RUFFLE -eq 1 ]; then
    # Original Ruffle-based thumbnail generation (requires Rust/Cargo build of Ruffle)
    cd "$HOME/ruffle"
    for f in "${PATH_TO_ASSETS}"/*.swf; do
        SWF_BASENAME=$(basename "$f")
        IMG_PATH=$(find "${PATH_TO_ASSETS}" -name "*${SWF_BASENAME}.jpg" -o -name "*${SWF_BASENAME}.png" -o -name "*${SWF_BASENAME}.gif" 2>/dev/null | head -1)
        if [[ -f "${IMG_PATH}" && ! -z "${IMG_PATH}" ]]; then
            echo "Thumbnail exists. Skipping ${SWF_BASENAME}..."
        else
            echo "Generating thumbnail for ${SWF_BASENAME}..."
            cargo run --package=exporter -- "${PATH_TO_ASSETS}/${SWF_BASENAME}" "${PATH_TO_ASSETS}/${SWF_BASENAME}.png" --skipframes 100
        fi
    done
else
    # Python/Pillow-based thumbnail generation
    python3 << 'PYEOF'
from PIL import Image, ImageDraw, ImageFont
import os
import struct
import zlib

def parse_swf_rect(data):
    """Parse SWF Rect structure from binary data"""
    nbits = (data[0] >> 3) & 0x1F
    total_bits = 5 + 4 * nbits
    total_bytes = (total_bits + 7) // 8
    bits = ''
    for byte in data[:total_bytes]:
        bits += format(byte, '08b')
    pos = 5
    values = []
    for _ in range(4):
        val = int(bits[pos:pos+nbits], 2)
        values.append(val)
        pos += nbits
    return values[0], values[1], values[2], values[3]

def get_swf_dimensions(filepath):
    """Get SWF file dimensions in pixels"""
    with open(filepath, 'rb') as f:
        sig = f.read(3)
        f.read(1)  # version
        f.read(4)  # length
        if sig == b'CWS':
            decompressed = zlib.decompress(f.read())
            rect = parse_swf_rect(decompressed[:32])
        elif sig == b'FWS':
            rect = parse_swf_rect(f.read(32))
        else:
            return 300, 300
        return (rect[1] - rect[0]) // 20, (rect[3] - rect[2]) // 20

def create_gradient(w, h, color1, color2):
    img = Image.new('RGB', (w, h))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        ratio = y / h
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return img

def draw_game_icon(draw, name, w, h, color):
    cx, cy = w // 2, h // 2 - 30
    name_lower = name.lower()

    if 'pacman' in name_lower or 'pacxon' in name_lower:
        r = min(w, h) // 5
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(255, 255, 0))
        draw.polygon([(cx, cy), (cx+r, cy-r//2), (cx+r, cy+r//2)], fill=color)
        eye_y = cy - r//2
        draw.ellipse([cx+r//4-4, eye_y-4, cx+r//4+4, eye_y+4], fill=(0, 0, 0))
        for i in range(3):
            dx = cx + r + 20 + i * 25
            draw.ellipse([dx-5, cy-5, dx+5, cy+5], fill=(255, 255, 255))
    elif 'mario' in name_lower:
        r = min(w, h) // 5
        draw.rectangle([cx-r, cy-r, cx+r, cy+r], fill=(180, 80, 0), outline=(0, 0, 0))
        draw.rectangle([cx-r+6, cy-r+6, cx+r-6, cy+r-6], fill=(255, 200, 0), outline=(0, 0, 0))
    else:
        # Generic game icon - colorful blocks
        r = min(w, h) // 5
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 128, 0)]
        size = r // 2
        for i, row in enumerate(range(-1, 2)):
            for j, col in enumerate(range(-1, 2)):
                bx = cx + col * (size + 4)
                by = cy + row * (size + 4)
                c = colors[(i * 3 + j) % len(colors)]
                draw.rectangle([bx-size//2, by-size//2, bx+size//2, by+size//2], fill=c, outline=(40, 40, 40))

# Find available font
font_path = None
for fp in [
    '/usr/share/fonts/truetype/english/Roboto-Bold.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    '/usr/share/fonts/truetype/chinese/SimHei.ttf',
]:
    if os.path.exists(fp):
        font_path = fp
        break

assets_dir = os.environ.get('PATH_TO_ASSETS', './assets')
if not os.path.isabs(assets_dir):
    assets_dir = os.path.join(os.getcwd(), assets_dir)

# Color palette for different games
colors = [
    (0, 0, 180), (180, 0, 0), (0, 0, 200), (0, 0, 150),
    (0, 100, 180), (180, 0, 0), (0, 120, 100), (100, 0, 180),
]

swf_files = sorted([f for f in os.listdir(assets_dir) if f.endswith('.swf')])

for idx, swf_file in enumerate(swf_files):
    filepath = os.path.join(assets_dir, swf_file)
    name = os.path.splitext(swf_file)[0]
    out_path = os.path.join(assets_dir, swf_file + '.jpg')

    # Skip if thumbnail already exists
    if os.path.exists(out_path):
        print(f"Thumbnail exists. Skipping {swf_file}...")
        continue

    w, h = 300, 300
    base_color = colors[idx % len(colors)]
    color2 = tuple(max(0, c - 80) for c in base_color)

    img = create_gradient(w, h, base_color, color2)
    draw = ImageDraw.Draw(img)

    # Grid pattern
    for x in range(0, w, 20):
        draw.line([(x, 0), (x, h)], fill=(255, 255, 255, 10), width=1)
    for y in range(0, h, 20):
        draw.line([(0, y), (w, y)], fill=(255, 255, 255, 10), width=1)

    # Game icon
    draw_game_icon(draw, name, w, h, base_color)

    # Title bar
    draw.rectangle([(0, h-55), (w, h)], fill=(0, 0, 0))

    try:
        font = ImageFont.truetype(font_path, 28) if font_path else ImageFont.load_default()
    except:
        font = ImageFont.load_default()

    # Center text
    bbox = draw.textbbox((0, 0), name, font=font)
    text_w = bbox[2] - bbox[0]
    text_x = (w - text_w) // 2
    text_y = h - 45
    draw.text((text_x, text_y), name, fill=(255, 255, 255), font=font)

    img.convert('RGB').save(out_path, 'JPEG', quality=90)
    print(f"Generated thumbnail: {swf_file}.jpg")

print("All thumbnails generated!")
PYEOF
fi
