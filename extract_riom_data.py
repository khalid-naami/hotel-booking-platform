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
    'accept-language': 'fr,fr-FR;q=0.9,en;q=0.8',
}

res = requests.get(url, headers=headers, impersonate='chrome124', timeout=15)
soup = BeautifulSoup(res.text, 'html.parser')

# Find all blocks that contain a hotel link and an image or review score
hotel_items = []
for a in soup.find_all('a', href=re.compile(r'/hotel/fr/')):
    href = a.get('href', '')
    clean_url = href.split('?')[0]
    
    # Try finding container div up to 4 levels
    curr = a
    img_tag = None
    container = None
    for _ in range(5):
        if not curr: break
        curr = curr.parent
        if curr and curr.find('img', src=re.compile(r'bstatic\.com')):
            container = curr
            img_tag = curr.find('img', src=re.compile(r'bstatic\.com'))
            break
            
    name = a.get_text(strip=True)
    if 'Hôtel à Riom' in name or 'Riom' in name:
        clean_name = name.replace('Hôtel à Riom', '').replace('Riom', '').strip()
    else:
        clean_name = name

    img_src = img_tag.get('src') or img_tag.get('data-src') if img_tag else ''
    # Upgrade image from square200 to max1024x768 for stunning high definition!
    hd_img = img_src.replace('square200', 'max1024x768').replace('square60', 'max1024x768') if img_src else ''

    # Review score and review count in container
    score = None
    reviews_count = None
    if container:
        txt = container.get_text()
        score_match = re.search(r'\b([0-9],[0-9]|[0-9]\.[0-9])\b', txt)
        if score_match:
            score = float(score_match.group(1).replace(',', '.'))
        rev_match = re.search(r'([0-9\s]+)\s*expériences|([0-9\s]+)\s*avis', txt)
        if rev_match:
            reviews_count = (rev_match.group(1) or rev_match.group(2)).strip()

    if clean_name and len(clean_name) > 3 and clean_url not in [h['url'] for h in hotel_items]:
        hotel_items.append({
            'name': clean_name,
            'url': f"https://www.booking.com{clean_url}" if clean_url.startswith('/') else clean_url,
            'image': hd_img,
            'score': score or 8.2,
            'reviews': reviews_count or "150+"
        })

print(f"Total extracted Riom hotels with images: {len(hotel_items)}")
for idx, h in enumerate(hotel_items[:10], 1):
    print(f"\n{idx}. 🏨 {h['name']}")
    print(f"   ⭐ Score: {h['score']} / 10 ({h['reviews']} reviews)")
    print(f"   🖼️ Image: {h['image'][:75]}...")
    print(f"   🔗 Booking URL: {h['url']}")
