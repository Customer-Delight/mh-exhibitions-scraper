import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
import re

print("=== MULTI-SOURCE SCRAPER STARTED ===")

SOURCES = [
    {
        "name": "exhibitions-india",
        "url": "https://www.exhibitions-india.com/state/maharashtra/",
        "parser": "exhibitions_india"
    },
    {
        "name": "10times-mh",
        "url": "https://10times.com/india/maharashtra/exhibitions",
        "parser": "10times"
    },
    {
        "name": "eventbrite-mumbai",
        "url": "https://www.eventbrite.com/d/india--mumbai/events--exhibitions/",
        "parser": "eventbrite"
    },
    {
        "name": "eventbrite-pune", 
        "url": "https://www.eventbrite.com/d/india--pune/events--exhibitions/",
        "parser": "eventbrite"
    },
    {
        "name": "allevents-mh",
        "url": "https://allevents.in/maharashtra/exhibitions",
        "parser": "allevents"
    },
    {
        "name": "tradefairdates-mh",
        "url": "https://www.tradefairdates.com/Fairs-Maharashtra-L17-S1.html",
        "parser": "tradefairdates"
    },
    {
        "name": "businesseventsmh",
        "url": "https://www.businesseventsindia.com/maharashtra/",
        "parser": "generic"
    },
    {
        "name": "india-tradefairs",
        "url": "https://www.indiatradefair.com/maharashtra/",
        "parser": "generic"
    }
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml"
}

all_data = []

def parse_exhibitions_india(html):
    soup = BeautifulSoup(html, 'html.parser')
    data = []
    for card in soup.select('div.exhibition-card, article.event'):
        try:
            title = card.select_one('h3, h2, .title').get_text(strip=True)
            date = card.select_one('.date, time, .event-date').get_text(strip=True)
            venue = card.select_one('.venue, .location, .event-venue').get_text(strip=True)
            if title: data.append({"title": title, "date": date, "venue": venue})
        except: continue
    return data

def parse_generic(html):
    data = []
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if any(k in line for k in ['Expo', 'Exhibition', 'Trade Fair', 'Convention']):
            if 15 < len(line.strip()) < 120:
                data.append({
                    "title": line.strip(),
                    "date": lines[i+1].strip() if i+1 < len(lines) else "Check website",
                    "venue": lines[i+2].strip() if i+2 < len(lines) else "Maharashtra"
                })
    return data[:30]

for source in SOURCES:
    print(f"\n--- Trying {source['name']} ---")
    try:
        r = requests.get(source['url'], headers=headers, timeout=10)
        print(f"Status: {r.status_code}, Size: {len(r.text)}")
        
        if r.status_code == 200 and len(r.text) > 5000:
            if source['parser'] == 'exhibitions_india':
                parsed = parse_exhibitions_india(r.text)
            else:
                parsed = parse_generic(r.text)
                
            print(f"Parsed {len(parsed)} items from {source['name']}")
            
            for item in parsed:
                item['source'] = source['name']
                item['scraped_at'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                item['city'] = "Maharashtra"
                all_data.append(item)
            
            if len(all_data) >= 10:
                print(f"SUCCESS: Got enough data from {source['name']}, stopping")
                break
                
    except Exception as e:
        print(f"FAILED {source['name']}: {e}")
        continue

print(f"\n=== TOTAL: Found {len(all_data)} exhibitions from {len(set([d['source'] for d in all_data]))} sources ===")

# Fixed line: was missing )
if len(all_data) == 0:
    print("CRITICAL: All sources failed")
    all_data.append({
        "title": "All sources blocked/empty - check logs",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "venue": "N/A",
        "city": "MH",
        "source": "error",
        "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    })

df = pd.DataFrame(all_data)
df.drop_duplicates(subset=['title'], inplace=True)
df.to_csv('exhibitions.csv', index=False)
print(f"=== FINISHED: Saved {len(df)} unique rows to CSV ===")
