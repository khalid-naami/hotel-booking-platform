import sys
sys.stdout.reconfigure(encoding='utf-8')
from curl_cffi import requests
from bs4 import BeautifulSoup
import re
import json

url = 'https://www.booking.com/city/fr/riom.fr.html'
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'accept-language': 'en-US,en;q=0.9,fr;q=0.8',
}

res = requests.get(url, headers=headers, impersonate='chrome124', timeout=15)
soup = BeautifulSoup(res.text, 'html.parser')

# Check property cards
cards = soup.select('[data-testid="property-card"]')
print(f"Property cards with data-testid='property-card': {len(cards)}")

if not cards:
    # Alternative selectors
    cards = soup.select('.sr_item, [data-testid="item"], .featuredRooms, .c-frequent-flights-card, div[data-id]')
    print(f"Alternative cards: {len(cards)}")

# Search for any divs containing hotel images, titles, and reviews
hotels = []
for a in soup.find_all('a', href=re.compile(r'/hotel/fr/')):
    href = a.get('href', '')
    title_elem = a.find(['h3', 'div', 'span'])
    name = a.get_text(strip=True)
    img = a.find('img')
    img_src = img.get('src') or img.get('data-src') if img else ''
    
    # Try finding parent container
    parent = a.find_parent('div', class_=re.compile(r'card|item|sr|property|featured', re.I)) or a.parent
    score_elem = parent.find(string=re.compile(r'^[0-9],[0-9]$|^[0-9]\.[0-9]$')) if parent else None
    
    clean_url = href.split('?')[0]
    if '/hotel/fr/' in clean_url and name and len(name) > 3:
        if not any(h['url'] == clean_url for h in hotels):
            hotels.append({
                'name': name,
                'url': f"https://www.booking.com{clean_url}" if clean_url.startswith('/') else clean_url,
                'img': img_src,
                'score': score_elem.strip() if score_elem else None
            })

print(f"Extracted {len(hotels)} hotels from Riom page:")
for h in hotels[:8]:
    print(f"  - {h['name']} | Img: {bool(h['img'])} | URL: {h['url']}")
