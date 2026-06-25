import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def scrape_mh_exhibitions():
    url = "https://stayhappening.com/mumbai-mh/exhibitions"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'lxml')

    exhibitions = []

    # StayHappening uses h3 for titles and p tags for details
    for item in soup.select('.event-card'): # each event block
        title_tag = item.select_one('h3')
        title = title_tag.text.strip() if title_tag else "No title"

        # Date and venue are usually in paragraph tags
        details = item.select('p')
        date = details[0].text.strip() if len(details) > 0 else "No date"
        venue = details[1].text.strip() if len(details) > 1 else "No venue"

        exhibitions.append({
            "title": title,
            "date": date,
            "venue": venue,
            "source": "StayHappening",
            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        })

    return exhibitions

if __name__ == "__main__":
    data = scrape_mh_exhibitions()
    df = pd.DataFrame(data)
    df.to_csv('exhibitions.csv', index=False)
    print(f"Saved {len(data)} exhibitions")
