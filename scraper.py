import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def scrape_mh_exhibitions():
    url = "https://10times.com/india/maharashtra/exhibitions"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9"
    }

    print("Fetching data from 10times.com...")
    response = requests.get(url, headers=headers, timeout=15)

    # DEBUG: Show what we actually got
    print(f"Status code: {response.status_code}")
    print(f"Page length: {len(response.text)} characters")
    print(f"First 300 chars: {response.text[:300]}")

    soup = BeautifulSoup(response.content, 'lxml')
    exhibitions = []

    # DEBUG: Count how many tables exist
    tables = soup.select('table')
    print(f"Found {len(tables)} tables on page")

    # Try multiple selectors - 10times changes layouts
    rows = soup.select('table.table tr') or soup.select('table tr') or soup.select('.event-list tr')
    print(f"Found {len(rows)} total rows")

    for row in rows[1:]: # skip header
        cols = row.find_all(['td', 'th'])
        if len(cols) >= 3:
            title = cols[0].get_text(strip=True)
            date = cols[1].get_text(strip=True)
            venue = cols[2].get_text(strip=True)

            if len(title) > 5: # ignore empty/short titles
                exhibitions.append({
                    "title": title,
                    "date": date,
                    "venue": venue,
                    "city": "Maharashtra",
                    "source": "10times",
                    "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                })

    print(f"Found {len(exhibitions)} exhibitions")
    return exhibitions

if __name__ == "__main__":
    data = scrape_mh_exhibitions()
    df = pd.DataFrame(data)
    df.to_csv('exhibitions.csv', index=False)
    print(f"Saved {len(data)} exhibitions to CSV")
