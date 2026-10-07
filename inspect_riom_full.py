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

print(f"Status: {res.status_code}, HTML length: {len(res.text)}")

# Find all images hosted on bstatic
bstatic_imgs = []
for img in soup.find_all('img'):
    src = img.get('src') or img.get('data-src') or ''
    if 'bstatic.com' in src and ('hotel' in src or 'square' in src):
        bstatic_imgs.append(src)

print(f"Found {len(bstatic_imgs)} bstatic hotel images on Riom page!")
for img in bstatic_imgs[:5]:
    print("  🖼️", img)

# Search for any window.booking or env data in scripts
scripts_text = ""
for s in soup.find_all('script'):
    if s.string and ('b_hotels' in s.string or 'hotel_name' in s.string or 'b_rooms' in s.string or 'featured_hotels' in s.string):
        print("Found relevant script block!")
        scripts_text += s.string[:500] + "\n"

print("Scripts preview:", scripts_text[:300])
