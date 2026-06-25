import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def scrape_mh_exhibitions():
    url = "REPLACE_WITH_ACTUAL_MH_URL"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'lxml')
    
    exhibitions = []
    
    # We'll fix these selectors together later
    for item in soup.select('.exhibition-item'):
        title = item.select_one('.title').text.strip() if item.select_one('.title') else "No title"
        date = item.select_one('.date').text.strip() if item.select_one('.date') else "No date"
        venue = item.select_one('.venue').text.strip() if item.select_one('.venue') else "No venue"
        
        exhibitions.append({
            "title": title,
            "date": date, 
            "venue": venue,
            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
    
    return exhibitions

if __name__ == "__main__":
    data = scrape_mh_exhibitions()
    df = pd.DataFrame(data)
    df.to_csv('exhibitions.csv', index=False)
    print(f"Saved {len(data)} exhibitions")
