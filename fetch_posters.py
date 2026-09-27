from duckduckgo_search import DDGS
import re
import time

ddgs = DDGS()

with open('dataset.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

out_lines = []
current_title = ""
current_year = ""

for i, line in enumerate(lines):
    title_match = re.search(r'"title":\s*"([^"]+)"', line)
    if title_match:
        current_title = title_match.group(1)
        
    year_match = re.search(r'"release_year":\s*(\d+)', line)
    if year_match:
        current_year = year_match.group(1)
    
    if 'placehold.co' in line:
        query = f"{current_title} {current_year} movie poster"
        print(f"Searching for: {query}")
        try:
            results = list(ddgs.images(query, max_results=10))
            image_url = None
            # Prioritize TMDB
            for r in results:
                if 'tmdb.org' in r['image']:
                    image_url = r['image']
                    break
            # Fallback to IMDB or others
            if not image_url and results:
                for r in results:
                    if 'media-amazon' not in r['image'] and 'imdb' not in r['image']: 
                        image_url = r['image']
                        break
                if not image_url:
                    image_url = results[0]['image']
                    
            if image_url:
                line = re.sub(r'https://placehold.co/[^"]+', image_url, line)
                print(f"  -> Found: {image_url}")
            time.sleep(1.5)
        except Exception as e:
            print(f"  -> Error: {e}")
            
    out_lines.append(line)

with open('dataset.py', 'w', encoding='utf-8') as f:
    f.writelines(out_lines)
