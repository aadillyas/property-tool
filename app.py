import streamlit as st
import pandas as pd
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import shutil
import os

# --- PATH FINDER ---
def get_chrome_path():
    # Streamlit Cloud usually puts chromium here
    paths = ["/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome"]
    for path in paths:
        if os.path.exists(path):
            return path
    return shutil.which("chromium") or shutil.which("google-chrome")

def get_listings():
    chrome_path = get_chrome_path()
    
    options = uc.ChromeOptions()
    options.binary_location = chrome_path  # FIX: This solves the 'Binary Location' error
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    try:
        # Initializing the driver with explicit binary path
        driver = uc.Chrome(options=options, browser_executable_path=chrome_path)
        driver.get("https://www.lankapropertyweb.com/house/forsale/mount-lavinia/")
        
        # Wait for Cloudflare "Human" check
        time.sleep(10) 
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()
        
        listings = []
        for card in soup.find_all('div', class_='cl-listing-card'):
            try:
                title = card.find('h3').text.strip()
                price = card.select_one('.price').text.strip()
                link = card.find('a')['href']
                full_link = "https://www.lankapropertyweb.com" + link if not link.startswith('http') else link
                listings.append({"Title": title, "Price": price, "Link": full_link})
            except: continue
        return listings
    except Exception as e:
        st.error(f"Technical Error: {e}")
        return []

# --- INTERFACE ---
st.title("👨‍🦳 Dad's Property Assistant")

if st.button("🚀 Run Live Sync"):
    with st.spinner("Engaging stealth browser..."):
        data = get_listings()
        if data:
            st.success(f"Found {len(data)} properties!")
            for item in data:
                with st.container(border=True):
                    st.subheader(item['Title'])
                    st.write(f"💰 {item['Price']}")
                    st.link_button("View Listing", item['Link'])
        else:
            st.warning("No listings found. The site might be blocking this specific attempt.")
