import requests
import pandas as pd
from datetime import datetime

print("=== SCRAPER STARTED ===")

url = "https://10times.com/india/maharashtra/exhibitions"
headers = {"User-Agent": "Mozilla/5.0"}

print("Fetching URL...")
try:
    r = requests.get(url, headers=headers, timeout=15)
    print("Status code:", r.status_code)
    print("Page size:", len(r.text))
except Exception as e:
    print("REQUEST FAILED:", e)
    r = None

data = []
if r and r.status_code == 200:
    # Just grab any line mentioning these keywords
    for line in r.text.split('\n'):
        clean = line.strip()
        if any(word in clean for word in ['Expo', 'Exhibition', 'Trade Show', 'Fair']):
            if 20 < len(clean) < 150:
                data.append({
                    "title": clean,
                    "date": "Check website",
                    "venue": "Maharashtra",
                    "source": "10times",
                    "scraped_at": datetime.now().strftime("%Y-%m-%d")
                })

# If scraping failed, add dummy row so file is never empty
if len(data) == 0:
    print("WARNING: No data found, adding placeholder")
    data.append({
        "title": "No exhibitions found - site may be blocking GitHub",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "venue": "N/A",
        "source": "Debug",
        "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    })

df = pd.DataFrame(data)
df.to_csv('exhibitions.csv', index=False)
print(f"=== FINISHED: Saved {len(df)} rows to CSV ===")
