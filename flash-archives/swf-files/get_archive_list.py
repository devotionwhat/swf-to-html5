import requests
from html.parser import HTMLParser

class SWFParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.files = []
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr, value in attrs:
                if attr == 'href' and value.endswith('.swf'):
                    self.files.append(value)

# Get list from Archive.org
url = "https://archive.org/download/swf-flash-games/"
resp = requests.get(url, timeout=30)
parser = SWFParser()
parser.feed(resp.text)

print(f"Total SWF files: {len(parser.files)}")
# Save list to file
with open('archive_list.txt', 'w') as f:
    for swf in parser.files:
        f.write(swf + '\n')
print("Saved to archive_list.txt")

# Show sample
print("\nFirst 20 files:")
for swf in parser.files[:20]:
    print(f"  {swf}")
