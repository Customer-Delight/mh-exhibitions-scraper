import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def scrape_mh_exhibitions():
    url = "https://10times.com/india/maharashtra/exhibitions"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    print("Fetching data from 10times.com...")
    response = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(response.content, 'lxml')

    exhibitions = []

    for row in soup.select('table.table tr')[1:]:
        cols = row.find_all('td')
        if len(cols) >= 3:
            title = cols[0].get_text(strip=True)
            date = cols[1].get_text(strip=True)
            venue = cols[2].get_text(strip=True)

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
