import requests
import pandas as pd
from datetime import datetime
import re

print("=== SCRAPER STARTED ===")

# This URL works as of June 2026
url = "https://www.tradeindia.com/trade-shows/maharashtra/"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

print("Fetching tradeindia.com...")
try:
    r = requests.get(url, headers=headers, timeout=15)
    print("Status code:", r.status_code)
    print("Page size:", len(r.text))
except Exception as e:
    print("REQUEST FAILED:", e)
    r = None

data = []
if r and r.status_code == 200:
    # tradeindia lists events in <li> tags with class 'show'
    shows = re.findall(r'<li class="show".*?</li>', r.text, re.DOTALL)
    print(f"Found {len(shows)} show blocks")
    
    for show in shows:
        try:
            title = re.search(r'<a[^>]*title="([^"]+)"', show).group(1)
            date = re.search(r'<span class="date">([^<]+)</span>', show).group(1)
            venue = re.search(r'<span class="venue">([^<]+)</span>', show).group(1)
            
            data.append({
                "title": title.strip(),
                "date": date.strip(),
                "venue": venue.strip(),
                "city": "Maharashtra",
                "source": "tradeindia",
                "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
        except:
            continue

print(f"Parsed {len(data)} exhibitions")

if len(data) == 0:
    print("WARNING: No data parsed, check HTML structure")
    data.append({
        "title": "Scraper ran but found no matches",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "venue": "Check logs",
        "city": "MH",
        "source": "debug",
        "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    })

df = pd.DataFrame(data)
df.to_csv('exhibitions.csv', index=False)
print(f"=== FINISHED: Saved {len(df)} rows to CSV ===")
