import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# --- 1. SEARCH CONFIGURATION ---
# We'll use a more general search URL to ensure we get results first
SEARCH_URL = "https://www.lankapropertyweb.com/house/forsale/mount-lavinia/"

def scrape_with_validation():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(SEARCH_URL, headers=headers, timeout=10)
        if response.status_code != 200:
            return None, f"Site blocked us (Status {response.status_code})"
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # LankaProperty uses 'cl-listing-card' or 'listing-card'
        # Let's try to find any link that looks like a property
        listings = []
        cards = soup.find_all('div', class_='cl-listing-card')
        
        for card in cards:
            try:
                title_elem = card.select_one('.cl-listing-title') or card.find('h3')
                price_elem = card.select_one('.price')
                link_elem = card.find('a', href=True)
                
                if title_elem and link_elem:
                    listings.append({
                        "title": title_elem.text.strip(),
                        "price": price_elem.text.strip() if price_elem else "Contact for Price",
                        "link": "https://www.lankapropertyweb.com" + link_elem['href'] if not link_elem['href'].startswith('http') else link_elem['href']
                    })
            except Exception:
                continue
        
        return listings, None
    except Exception as e:
        return None, str(e)

# --- 2. THE INTERFACE ---
st.set_page_config(page_title="Lanka Property Scraper", layout="wide")
st.title("🔎 Real-Time LankaProperty Sync")

if st.button('🔄 Sync Now'):
    with st.spinner('Fetching live data...'):
        data, error = scrape_with_validation()
        
        if error:
            st.error(f"Scraper Error: {error}")
        elif not data:
            st.warning("Connected to site, but found 0 listings. The website structure might have changed.")
            # Debugging: Show the HTML if it fails
            # st.code(response.text[:500]) 
        else:
            st.success(f"Successfully found {len(data)} listings!")
            
            # Display as a nice table
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            
            # Display as Cards
            for item in data:
                with st.expander(f"🏠 {item['title']} - {item['price']}"):
                    st.write(f"Link: {item['link']}")
                    st.link_button("Go to Listing", item['link'])
