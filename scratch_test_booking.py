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

print("Requesting Booking.com Riom page via curl_cffi...")
try:
    res = requests.get(url, headers=headers, impersonate='chrome124', timeout=15)
    print("HTTP Status Code:", res.status_code)
    print("Page HTML size:", len(res.text), "chars")
    soup = BeautifulSoup(res.text, 'html.parser')
    print("Page Title:", soup.title.string.strip() if soup.title else "N/A")
    
    # Check for hotel links
    hotel_links = soup.find_all('a', href=re.compile(r'/hotel/fr/'))
    print(f"Total hotel links found: {len(hotel_links)}")
    
    # Check for JSON-LD structured data (schema.org)
    scripts = soup.find_all('script', type='application/ld+json')
    print(f"Total JSON-LD scripts: {len(scripts)}")
    for s in scripts:
        try:
            data = json.loads(s.string)
            if isinstance(data, dict) and ('itemListElement' in data or data.get('@type') in ('Hotel', 'ItemList')):
                print("Found structured schema:", data.get('@type'))
        except Exception:
            pass

    # Extract distinct hotels
    distinct_hotels = {}
    for a in hotel_links:
        href = a.get('href', '')
        name = a.get_text(strip=True)
        clean_url = href.split('?')[0]
        if '/hotel/fr/' in clean_url and name and len(name) > 3 and clean_url not in distinct_hotels:
            distinct_hotels[clean_url] = name

    print(f"\nExtracted {len(distinct_hotels)} distinct hotels in Riom:")
    for u, n in list(distinct_hotels.items())[:10]:
        print(f"  🏨 {n} -> https://www.booking.com{u}")

except Exception as e:
    print("Error:", e)
