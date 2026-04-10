#!/bin/bash
# Enhanced version supporting category subfolders
# Organizes games by category and generates proper HTML wrappers

CLEAN_UP=1 #Set to 0 to disable
THUMBNAIL_DIR="./thumbnails"

# Create assets folder if it doesn't exist
if [ ! -d "./assets" ]; then
    mkdir -p "./assets"
    chmod 700 "./assets"
    echo "assets folder created. Go ahead and dump .swf files in this folder and re-run this script"
    exit 0
fi

# Create thumbnails directory
mkdir -p ${THUMBNAIL_DIR}

if [ ${CLEAN_UP} -eq 1 ]; then
    echo "Cleaning up old files..."
    find ./assets -name "*.html" -delete 2>/dev/null
fi

getimage(){
    while [[ "${RANDOM_IMAGE}" = "${LAST_IMAGE_USED}" ]]; do
        RANDOM_IMAGE=`ls images/ | shuf -n 1`
    done;
    LAST_IMAGE_USED=${RANDOM_IMAGE}
}
getimage
LAST_IMAGE_USED=${RANDOM_IMAGE}

add_card(){
    # First Parameter: Name
    # Second Parameter: URL
    # Third Parameter: IMG
    # Fourth Parameter: white/black
    # Fifth Parameter: Category (optional)
    NAME="$1"
    URL="$2"
    CATEGORY="$5"
    if [ -z "$3" ]; then
        getimage
        IMAGE_URL=images/${RANDOM_IMAGE}
    else
        IMAGE_URL="$3"
    fi
    if [ -z "$4" ]; then
        TITLE_COLOR=white
    else
        TITLE_COLOR="$4"
    fi
    echo "Adding ${NAME}: ${URL} : ${IMAGE_URL}"
cat <<EOF >> index.html
        <div class="card ${RANDOM}" onclick="location.href='${URL}';" data-category="${CATEGORY}">
                <div class="card_image">
                    <img src="${IMAGE_URL}" />
                    <div class="card_title title-${TITLE_COLOR}">
                        <p>${NAME}</p>
                    </div>
                </div>
        </div>

EOF
}

add_category_header(){
    CATEGORY="$1"
    CAT_DISPLAY=$(echo "$CATEGORY" | sed 's/-/ /g' | sed 's/\b\(.\)/\u\1/g')
cat <<EOF >> index.html
    <div class="category-header" id="category-${CATEGORY}">
        <h2>${CAT_DISPLAY}</h2>
    </div>
EOF
}

cat <<EOF > index.html
<!DOCTYPE html>
<html>

<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Flash Games Archive - SWF to HTML5</title>
    <link rel="stylesheet" type="text/css" href="css/auroral2.css" />
    <link rel="stylesheet" href="css/cards.css">
    <style>
        .category-header {
            clear: both;
            width: 100%;
            padding: 20px 10px 10px;
            margin-top: 20px;
            border-bottom: 2px solid rgba(255,255,255,0.3);
        }
        .category-header h2 {
            color: white;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            margin: 0;
        }
        .category-nav {
            position: fixed;
            top: 10px;
            right: 10px;
            background: rgba(0,0,0,0.7);
            padding: 15px;
            border-radius: 10px;
            z-index: 1000;
            max-height: 80vh;
            overflow-y: auto;
        }
        .category-nav a {
            display: block;
            color: white;
            text-decoration: none;
            padding: 5px 10px;
            margin: 2px 0;
            border-radius: 5px;
        }
        .category-nav a:hover {
            background: rgba(255,255,255,0.2);
        }
    </style>
</head>

<body>
    <div class="auroral-info">
        <h1>Flash Games Archive</h1>
        <p style="color: white; text-align: center;">Classic Flash Games - Preserved with Ruffle</p>

        <div class="cards-list">

EOF

# Category navigation (will be added at the end)
CATEGORY_NAV=""

# Process SWF files - handle both flat and subfolder structure
# First, process flat files in assets root
shopt -s nullglob
FLAT_SWFS=(./assets/*.swf)
shopt -u nullglob

for f in "${FLAT_SWFS[@]}"; do
    if [ -f "$f" ]; then
        SWF_TITLE=`basename -s .swf ${f}`
        SWF_BASENAME=`basename ${f}`
        
        echo "Generating file for ${f}..."
        
        # Output Fullscreen SWF page
cat <<EOF > ${f}.html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>${SWF_TITLE}</title>
    <style>
        body { margin: 0; padding: 0; overflow: hidden; }
        embed { width: 100vw; height: 100vh; }
    </style>
</head>
<body>
    <embed src="../${f}" width="100%" height="100%"></embed>
    <script src="https://unpkg.com/@aspect-build/ruffle-wasm@latest/ruffle.js"></script>
</body>
</html>
EOF
        
        # Add to Main Page
        IMG_PATH=`find assets thumbnails -name "*${SWF_BASENAME}.jpg" -o -name "*${SWF_BASENAME}.png" -o -name "*${SWF_BASENAME}.gif" 2>/dev/null | head -1`
        if [[ -f ${IMG_PATH} && ! -z ${IMG_PATH} ]]; then
            echo "Image exists. Using ${IMG_PATH}..."
cat <<EOF >> index.html
    <div class="card 1" onclick="location.href='./assets/${SWF_BASENAME}.html';">
            <div class="card_image">
                <img src="${IMG_PATH}" />
            </div>
    </div>
EOF
        else
            echo "Using random image..."
            getimage
cat <<EOF >> index.html
    <div class="card 1" onclick="location.href='./assets/${SWF_BASENAME}.html';">
            <div class="card_image">
                <img src="images/${RANDOM_IMAGE}" />
                 <div class="card_title title-white">
                    <p>${SWF_TITLE}</p>
                </div>
            </div>
    </div>
EOF
        fi
    fi
done

# Now process category subfolders
CATEGORIES=$(find ./assets -mindepth 1 -maxdepth 1 -type d | sort)

for CAT_DIR in $CATEGORIES; do
    CATEGORY=$(basename "$CAT_DIR")
    CAT_DISPLAY=$(echo "$CATEGORY" | sed 's/-/ /g' | sed 's/\b\(.\)/\u\1/g')
    
    # Count SWF files in category
    SWF_COUNT=$(find "$CAT_DIR" -name "*.swf" -type f | wc -l)
    
    if [ $SWF_COUNT -gt 0 ]; then
        echo ""
        echo "Processing category: ${CATEGORY} (${SWF_COUNT} games)"
        
        # Add category header
        add_category_header "$CATEGORY"
        
        # Add to navigation
        CATEGORY_NAV="${CATEGORY_NAV}<a href=\"#category-${CATEGORY}\">${CAT_DISPLAY}</a>\n"
        
        # Process each SWF in category
        for f in ${CAT_DIR}/*.swf; do
            if [ -f "$f" ]; then
                SWF_TITLE=`basename -s .swf ${f}`
                SWF_BASENAME=`basename ${f}`
                
                echo "  Generating: ${SWF_TITLE}..."
                
                # Output Fullscreen SWF page
cat <<EOF > ${f}.html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>${SWF_TITLE}</title>
    <style>
        body { margin: 0; padding: 0; overflow: hidden; background: #000; }
        #game-container { width: 100vw; height: 100vh; }
    </style>
</head>
<body>
    <div id="game-container">
        <embed src="../${f}" width="100%" height="100%"></embed>
    </div>
    <script src="https://unpkg.com/@aspect-build/ruffle-wasm@latest/ruffle.js"></script>
</body>
</html>
EOF
                
                # Check for thumbnail
                IMG_PATH=`find thumbnails assets -path "*/${CATEGORY}/*" -name "*${SWF_BASENAME%.swf}*" 2>/dev/null | grep -E '\.(jpg|png|gif)$' | head -1`
                
                if [[ -f ${IMG_PATH} && ! -z ${IMG_PATH} ]]; then
                    echo "    Using thumbnail: ${IMG_PATH}"
cat <<EOF >> index.html
    <div class="card 1" onclick="location.href='./${CAT_DIR}/${SWF_BASENAME}.html';" data-category="${CATEGORY}">
            <div class="card_image">
                <img src="${IMG_PATH}" />
                 <div class="card_title title-white">
                    <p>${SWF_TITLE}</p>
                </div>
            </div>
    </div>
EOF
                else
                    getimage
cat <<EOF >> index.html
    <div class="card 1" onclick="location.href='./${CAT_DIR}/${SWF_BASENAME}.html';" data-category="${CATEGORY}">
            <div class="card_image">
                <img src="images/${RANDOM_IMAGE}" />
                 <div class="card_title title-white">
                    <p>${SWF_TITLE}</p>
                </div>
            </div>
    </div>
EOF
                fi
            fi
        done
    fi
done

# Wrap up main page
cat <<EOF >> index.html
  </div>
    </div>
    
    <!-- Category Navigation -->
    <div class="category-nav">
        <strong style="color: white;">Categories</strong><br>
EOF

# Add category links
echo -e "$CATEGORY_NAV" >> index.html

cat <<EOF >> index.html
    </div>
    
    <!-- Theme Selector -->
    <div class="container">
        <div id="northern" class="auroral auroral-northern"></div>
        <div id="northern-intense" class="auroral auroral-northern-intense"></div>
        <div id="northern-dimmed" class="auroral auroral-northern-dimmed"></div>
        <div id="northern-dusk" class="auroral auroral-northern-dusk"></div>
        <div id="northern-warm" class="auroral auroral-northern-warm"></div>
        <div id="agrabah" class="auroral auroral-agrabah"></div>
        <div class="auroral-stars"></div>
    </div>
</body>

</html>
EOF

echo ""
echo "========================================"
echo "Generation complete!"
echo "========================================"
echo "Total categories processed: $(echo "$CATEGORIES" | wc -w)"
echo "Index.html created."
