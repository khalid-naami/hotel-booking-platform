import sys
sys.stdout.reconfigure(encoding='utf-8')
from curl_cffi import requests
from bs4 import BeautifulSoup
import re

url = 'https://www.booking.com/hotel/fr/b-amp-b-riom.fr.html'
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'accept-language': 'en-US,en;q=0.9',
}

res = requests.get(url, headers=headers, impersonate='chrome124', timeout=15)
print("Status:", res.status_code)
print("Size:", len(res.text))

soup = BeautifulSoup(res.text, 'html.parser')
title = soup.find('h2', class_=re.compile(r'pp-header__title|d2fee87e0e', re.I)) or soup.find('h2')
print("Hotel Title:", title.get_text(strip=True) if title else soup.title.string.strip() if soup.title else "N/A")

# Look for address
address = soup.find(['span', 'p'], class_=re.compile(r'address|hp_address', re.I))
print("Address:", address.get_text(strip=True) if address else "N/A")

# Look for review score
score = soup.find(['div', 'span'], class_=re.compile(r'd10a6220b4|review-score|a3b878294d', re.I))
print("Review score element:", score.get_text(strip=True) if score else "N/A")

# Look for images
images = []
for img in soup.find_all('img', src=re.compile(r'bstatic\.com/xdata/images/hotel')):
    images.append(img.get('src'))
print(f"Found {len(images)} high-res hotel images on page:")
for im in images[:3]:
    print(" -", im)
