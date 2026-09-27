import urllib.request, re, urllib.parse

def get_tmdb_poster(title, year):
    query = urllib.parse.quote(f"{title} {year}")
    url = f"https://www.themoviedb.org/search?query={query}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        html = urllib.request.urlopen(req).read().decode('utf-8')
        # TMDB images look like: class="poster" src="/t/p/w94_and_h141_bestv2/..."
        # or data-src="https://media.themoviedb.org/t/p/w94_and_h141_bestv2/..."
        # Let's extract any t/p/w... link
        match = re.search(r'/t/p/w[^"]+\.jpg', html)
        if match:
            # Change width to w500
            path = match.group(0).split('/')[-1]
            return f"https://image.tmdb.org/t/p/w500/{path}"
    except Exception as e:
        print(f"Error for {title}: {e}")
    return None

print(get_tmdb_poster("Kantara", 2022))
