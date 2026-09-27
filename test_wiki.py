import urllib.request, urllib.parse, json

def get_wiki_image(title):
    query = urllib.parse.quote(title)
    url = f"https://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles={query}"
    req = urllib.request.Request(url, headers={'User-Agent': 'MovieRecommenderBot/1.0 (test@example.com)'})
    try:
        response = urllib.request.urlopen(req)
        data = json.loads(response.read().decode('utf-8'))
        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if "original" in page_data:
                return page_data["original"]["source"]
    except Exception as e:
        pass
    return None

print(get_wiki_image("Kantara (film)"))
