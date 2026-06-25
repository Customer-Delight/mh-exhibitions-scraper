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
        "name": "tradefairdates-mh",
        "url": "https://www.tradefairdates.com/Fairs-Maharashtra-L17-S1.html",
        "parser": "tradefairdates"
    },
    {
        "name": "allevents-mh",
        "url": "https://allevents.in/maharashtra/exhibitions",
        "parser": "allevents"
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
        "name": "businesseventsindia",
        "url": "https://www.businesseventsindia.com/maharashtra/",
        "parser": "generic"
    },
    {
        "name": "indiatradefair",
        "url": "https://www.indiatradefair.com/maharashtra/",
        "parser": "generic"
    }
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9"
}

all_data = []

def parse_exhibitions_india(html):
    soup = BeautifulSoup(html, 'html.parser')
    data = []
    for card in soup.select('div.exhibition-card, article.event,.event-item'):
        try:
            title = card.select_one('h3, h2,.title,.event-title').get_text(strip=True)
            date = card.select_one('.date, time,.event-date,.dates').get_text(strip=True)
            venue = card.select_one('.venue,.location,.event-venue,.place').get_text(strip=True)
            if title and len(title) > 3:
                data.append({"title": title, "date": date, "venue": venue})
        except: continue
    return data

def parse_10times(html):
    soup = BeautifulSoup(html, 'html.parser')
    data = []
    for row in soup.select('table.table tr,.event-list tr'):
        try:
            cols = row.find_all(['td', 'th'])
            if len(cols) >= 3:
                title = cols[0].get_text(strip=True)
                date = cols[1].get_text(strip=True)
                venue = cols[2].get_text(strip=True)
                if len(title) > 5:
                    data.append({"title": title, "date": date, "venue": venue})
        except: continue
    return data

def parse_tradefairdates(html):
    soup = BeautifulSoup(html, 'html.parser')
    data = []
    for row in soup.select('tr.fair'):
        try:
            title = row.select_one('.fair-name').get_text(strip=True)
            date = row.select_one('.fair-date').get_text(strip=True)
            venue = row.select_one('.fair-city').get_text(strip=True)
            if title:
                data.append({"title": title, "date": date, "venue": venue})
        except: continue
    return data

def parse_allevents(html):
    soup = BeautifulSoup(html, 'html.parser')
    data = []
    for card in soup.select('.event-card, li.event-item'):
        try:
            title = card.select_one('h3,.event-name').get_text(strip=True)
            date = card.select_one('.event-date,.date').get_text(strip=True)
            venue = card.select_one('.event-venue,.venue').get_text(strip=True)
            if title:
                data.append({"title": title, "date": date, "venue": venue})
        except: continue
    return data

def parse_eventbrite(html):
    soup = BeautifulSoup(html, 'html.parser')
    data = []
    for card in soup.select('[data-testid="event-card"],.eds-event-card'):
        try:
            title = card.select_one('h3,.eds-event-card__formatted-name').get_text(strip=True)
            date = card.select_one('.eds-event-card__sub-title, time').get_text(strip=True)
            venue = "Mumbai/Pune" # Eventbrite hides venue without click
            if title:
                data.append({"title": title, "date": date, "venue": venue})
        except: continue
    return data

def parse_generic(html):
    data = []
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator='\n')
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    for i, line in enumerate(lines):
        if any(k in line for k in ['Expo', 'Exhibition', 'Trade Fair', 'Convention', 'Summit']):
            if 15 < len(line) < 150 and not line.startswith('http'):
                date = lines[i+1] if i+1 < len(lines) and len(lines[i+1]) < 50 else "Check website"
                venue = lines[i+2] if i+2 < len(lines) and len(lines[i+2]) < 80 else "Maharashtra"
                data.append({"title": line, "date": date, "venue": venue})
    return data[:30]

PARSERS = {
    "exhibitions_india": parse_exhibitions_india,
    "10times": parse_10times,
    "tradefairdates": parse_tradefairdates,
    "allevents": parse_allevents,
    "eventbrite": parse_eventbrite,
    "generic": parse_generic
}

for source in SOURCES:
    print(f"\n--- Trying {source['name']} ---")
    try:
        r = requests.get(source['url'], headers=headers, timeout=12)
        print(f"Status: {r.status_code}, Size: {len(r.text)}")

        if r.status_code == 200 and len(r.text) > 5000:
            parser_func = PARSERS.get(source['parser'], parse_generic)
            parsed = parser_func(r.text)
            print(f"Parsed {len(parsed)} items from {source['name']}")

            for item in parsed:
                item['source'] = source['name']
                item['scraped_at'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                item['city'] = "Maharashtra"
                all_data.append(item)

            if len(all_data
