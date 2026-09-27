import urllib.parse
import re

with open('dataset.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

out_lines = []
current_title = "Movie"

for line in lines:
    title_match = re.search(r'"title":\s*"([^"]+)"', line)
    if title_match:
        current_title = title_match.group(1)
    
    if 'm.media-amazon.com' in line:
        encoded_title = urllib.parse.quote(current_title.replace(' ', '+'))
        new_url = f"https://placehold.co/500x750/1e1e2f/94a3b8?text={encoded_title}"
        line = re.sub(r'https://m.media-amazon.com[^"]+', new_url, line)
        
    out_lines.append(line)

with open('dataset.py', 'w', encoding='utf-8') as f:
    f.writelines(out_lines)

print("Fixed dataset.py Amazon links!")
