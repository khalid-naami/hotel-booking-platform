import sys
sys.stdout.reconfigure(encoding='utf-8')
from curl_cffi import requests
from bs4 import BeautifulSoup
import re

url = 'https://www.booking.com/searchresults.html?ss=Riom%2C+Auvergne%2C+France'
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'accept-language': 'en-US,en;q=0.9',
}

print("Fetching Booking.com search results for Riom, France...")
res = requests.get(url, headers=headers, impersonate='chrome124', timeout=15)
soup = BeautifulSoup(res.text, 'html.parser')
cards = soup.select('[data-testid="property-card"]')
print(f"Booking.com Search: Found {len(cards)} live property cards!")

for idx, c in enumerate(cards[:8], 1):
    title = c.select_one('[data-testid="title"]')
    price = c.select_one('[data-testid="price-and-discounted-price"]')
    score = c.select_one('[data-testid="review-score"]')
    img = c.select_one('img')
    img_url = img.get('src') if img else ''
    dist = c.select_one('[data-testid="distance"]')
    link = c.select_one('a[href*="/hotel/"]')
    href = link.get('href', '') if link else ''
    
    print(f"\n{idx}. 🏨 {title.text.strip() if title else 'N/A'}")
    print(f"   💰 Price: {price.text.strip() if price else 'N/A'}")
    print(f"   ⭐ Score: {' '.join(score.text.split()) if score else 'N/A'}")
    print(f"   📍 Distance: {dist.text.strip() if dist else 'N/A'}")
    print(f"   🖼️ Image: {img_url[:75]}...")
    print(f"   🔗 Link: {href[:80]}...")
