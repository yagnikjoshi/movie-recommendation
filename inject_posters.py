import json
import re

known_urls = {
    "Hellaro": "https://image.tmdb.org/t/p/w500/b1rnAdQe2wxnBMqYhhvC34O3lLC.jpg",
    "Chal Jeevi Laiye!": "https://en.wikipedia.org/wiki/Special:FilePath/Chal_Jeevi_Laiye_poster.jpg",
    "Chhello Divas": "https://en.wikipedia.org/wiki/Special:FilePath/Chhello_Divas.jpg",
    "Love Ni Bhavai": "https://en.wikipedia.org/wiki/Special:FilePath/Love_Ni_Bhavai_poster.jpg",
    "Kevi Rite Jaish": "https://en.wikipedia.org/wiki/Special:FilePath/Kevi_Rite_Jaish_poster.jpg",
    "Bey Yaar": "https://image.tmdb.org/t/p/w500/8CpqWJ6sQ7o0wS2prgI5RWzpeZO.jpg",
    "Gujjubhai the Great": "https://upload.wikimedia.org/wikipedia/en/5/51/Gujjubhai_The_Great_Poster.jpg",
    "Naadi Dosh": "https://image.tmdb.org/t/p/w500/bDR3HJIXSOgUFLxRIU4eDLEQmcz.jpg",
    "Vash": "https://image.tmdb.org/t/p/w500/zedSgAiBlbpnbETIHZjyXsuO3ZX.jpg",
    "Shu Thayu?": "https://en.wikipedia.org/wiki/Special:FilePath/Shu_Thayu_poster.jpg",
    "Kantara": "https://upload.wikimedia.org/wikipedia/en/8/84/Kantara_poster.jpeg",
    "777 Charlie": "https://image.tmdb.org/t/p/w500/7mMOmXAAkVSlQB8eG8hCSpsTV0G.jpg",
    "Eega": "https://en.wikipedia.org/wiki/Special:FilePath/Eega_poster.jpg",
    "Arjun Reddy": "https://image.tmdb.org/t/p/w500/At69gkkW1VY2GYqAx5j5FiOpCiq.jpg",
    "Minnal Murali": "https://image.tmdb.org/t/p/w500/5jHnykugFB3awLTwDM5LQ93TIzs.jpg",
    "Bangalore Days": "https://image.tmdb.org/t/p/w500/iFMyZw1DTGvZ8hPa0eTseSFiRT1.jpg",
    "Kaithi": "https://image.tmdb.org/t/p/w500/tUvB6kC440qLzF4G4h3q6g18jJd.jpg",
    "Asuran": "https://upload.wikimedia.org/wikipedia/en/7/78/Asuran_2019_poster.jpg",
    "OMG: Oh My God!": "https://en.wikipedia.org/wiki/Special:FilePath/OMG_Oh_My_God_Poster.jpg",
    "Kahaani": "https://en.wikipedia.org/wiki/Special:FilePath/Kahaani_Poster.jpg",
    "Ala Vaikunthapurramuloo": "https://en.wikipedia.org/wiki/Special:FilePath/Ala_Vaikunthapurramuloo.jpeg",
    "Ustad Hotel": "https://en.wikipedia.org/wiki/Special:FilePath/Ustad_Hotel_Poster.jpg",
    "Pariyerum Perumal": "https://en.wikipedia.org/wiki/Special:FilePath/Pariyerum_Perumal_poster.jpg",
    "Jersey": "https://en.wikipedia.org/wiki/Special:FilePath/Jersey_2019_poster.jpg",
    "Lucia": "https://en.wikipedia.org/wiki/Special:FilePath/Lucia_Poster.jpg"
}

with open('dataset.py', 'r', encoding='utf-8') as f:
    content = f.read()

for title, url in known_urls.items():
    # Find the title pattern and replace the NEXT poster_path
    # This is a bit tricky with regex, we can process line by line
    pass

with open('dataset.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

out_lines = []
current_title = ""

for line in lines:
    title_match = re.search(r'"title":\s*"([^"]+)"', line)
    if title_match:
        current_title = title_match.group(1)
        
    if '"poster_path":' in line and 'placehold.co' in line:
        if current_title in known_urls:
            line = re.sub(r'https://placehold.co/[^"]+', known_urls[current_title], line)
    
    out_lines.append(line)

with open('dataset.py', 'w', encoding='utf-8') as f:
    f.writelines(out_lines)

print("Injected actual posters into dataset.py!")
