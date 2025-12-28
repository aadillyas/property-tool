import streamlit as st
import pandas as pd
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import os

# --- APP SETUP ---
st.set_page_config(page_title="LankaProperty Pro", layout="wide")
st.title("🏡 LankaProperty Scalable Sync")

def get_listings(category_url):
    options = uc.ChromeOptions()
    options.add_argument('--headless') # Runs in the background
    options.add_argument('--no-sandbox')
    
    # Start the "Stealth" browser
    try:
        driver = uc.Chrome(options=options)
        driver.get(category_url)
        
        # IMPORTANT: Wait for Cloudflare to finish its 5-second check
        time.sleep(7) 
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()
        
        listings = []
        # Target the listing cards specifically found on LankaProperty
        cards = soup.find_all('div', class_='cl-listing-card')
        
        for card in cards:
            try:
                title = card.find('h3').text.strip()
                price = card.select_one('.price').text.strip()
                link = "https://www.lankapropertyweb.com" + card.find('a')['href']
                
                listings.append({
                    "Title": title, 
                    "Price": price, 
                    "Link": link,
                    "ID": link.split('/')[-2]
                })
            except: continue
        return listings
    except Exception as e:
        st.error(f"Sync failed: {e}")
        return []

# --- THE INTERFACE ---
col1, col2 = st.columns(2)
with col1:
    if st.button("🔍 Sync Houses (Mount Lavinia)"):
        url = "https://www.lankapropertyweb.com/house/forsale/mount-lavinia/"
        data = get_listings(url)
        st.session_state['listings'] = data

with col2:
    if st.button("🌳 Sync Lands"):
        url = "https://www.lankapropertyweb.com/land/sale/mount-lavinia/"
        data = get_listings(url)
        st.session_state['listings'] = data

if 'listings' in st.session_state:
    df = pd.DataFrame(st.session_state['listings'])
    
    # Dad's Filters (Applied to the data we just found)
    st.divider()
    st.subheader("Results")
    
    for _, item in df.iterrows():
        with st.container(border=True):
            st.write(f"### {item['Title']}")
            st.write(f"💰 **{item['Price']}**")
            st.link_button("View on LankaProperty", item['Link'])
