import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

# --- 1. THE STEALTH ENGINE ---
def get_stealth_session():
    session = requests.Session()
    # These headers mimic a real Chrome browser on Windows 10
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    })
    return session

def scrape_robust():
    url = "https://www.lankapropertyweb.com/house/forsale/mount-lavinia/"
    session = get_stealth_session()
    
    try:
        # Step 1: Visit the homepage first to get a "session cookie" (more human-like)
        session.get("https://www.lankapropertyweb.com/", timeout=10)
        time.sleep(1) # Wait a second to avoid looking robotic
        
        # Step 2: Now visit the actual search page
        response = session.get(url, timeout=15)
        
        if response.status_code != 200:
            return None, f"Still blocked (Error {response.status_code})."

        soup = BeautifulSoup(response.text, 'html.parser')
        listings = []
        
        # LankaProperty often puts listings in 'cl-listing-card'
        cards = soup.find_all('div', class_='cl-listing-card')
        
        for card in cards:
            title = card.find('h3').text.strip() if card.find('h3') else "No Title"
            price = card.select_one('.price').text.strip() if card.select_one('.price') else "Negotiable"
            link = card.find('a')['href']
            if not link.startswith('http'):
                link = "https://www.lankapropertyweb.com" + link
                
            listings.append({"Title": title, "Price": price, "Link": link})
            
        return listings, None

    except Exception as e:
        return None, str(e)

# --- 2. THE DASHBOARD ---
st.title("🏠 Dad's Real-Time Property Tracker")

if st.button('🚀 Fetch Latest Houses'):
    results, err = scrape_robust()
    if err:
        st.error(f"⚠️ {err}")
        st.info("Try clicking again in 1 minute. The site might be rate-limiting us.")
    elif not results:
        st.warning("Connected successfully, but no houses found. Check the URL!")
    else:
        st.success(f"Found {len(results)} listings!")
        for item in results:
            with st.container(border=True):
                st.subheader(item['Title'])
                st.write(f"**Price:** {item['Price']}")
                st.link_button("View Details", item['Link'])
