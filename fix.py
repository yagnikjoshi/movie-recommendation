content = open('app.py', encoding='utf-8').read()

r1 = '<img src="{m[\'poster_path\']}" class="poster-img" alt="{m[\'title\']}">'
n1 = '<img src="{m[\'poster_path\']}" data-title="{m[\'title\']}" data-year="{m.get(\'release_year\', \'\')}" class="poster-img tmdb-poster" alt="{m[\'title\']}">'
content = content.replace(r1, n1)

r2 = '<img src="{m2[\'poster_path\']}" class="poster-img">'
n2 = '<img src="{m2[\'poster_path\']}" data-title="{m2[\'title\']}" data-year="{m2.get(\'release_year\', \'\')}" class="poster-img tmdb-poster">'
content = content.replace(r2, n2)

r3 = '<img src="{row[\'poster_path\']}" class="poster-img">'
n3 = '<img src="{row[\'poster_path\']}" data-title="{row[\'title\']}" data-year="{row.get(\'release_year\', \'\')}" class=\"poster-img tmdb-poster\">'
content = content.replace(r3, n3)

r4 = '<img src="{item[\'poster_path\']}" class="poster-img">'
n4 = '<img src="{item[\'poster_path\']}" data-title="{item[\'title\']}" data-year="{item.get(\'release_year\', \'\')}" class="poster-img tmdb-poster">'
content = content.replace(r4, n4)

open('app.py', 'w', encoding='utf-8').write(content)
