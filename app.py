import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime

# --- CONFIGURATION ---
TARGET_URL = "https://www.lankapropertyweb.com/house/san-pila/mount-lavinia/"
DB_FILE = "property_db.csv"

def get_data():
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(TARGET_URL, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    listings = []
    for card in soup.select('.cl-listing-card'):
        try:
            # Extract unique ID from the link to track "Seen" status
            link = "https://www.lankapropertyweb.com" + card.find('a')['href']
            prop_id = link.split('/')[-2] 
            
            listings.append({
                "id": prop_id,
                "title": card.select_one('.cl-listing-title').text.strip(),
                "price": card.select_one('.price').text.strip(),
                "link": link,
                "date_found": datetime.date.today().strftime("%Y-%m-%d")
            })
        except: continue
    return pd.DataFrame(listings)

# --- APP INTERFACE ---
st.title("👨‍🦳 Dad's Property Assistant")

# Load memory
try:
    history_df = pd.read_csv(DB_FILE)
except:
    history_df = pd.DataFrame(columns=["id", "shortlisted"])

live_df = get_data()

# Logic: Mark what is new
new_listings = live_df[~live_df['id'].isin(history_df['id'])]

tab1, tab2 = st.tabs(["🆕 New Matches", "⭐ Shortlist"])

with tab1:
    st.subheader(f"Found {len(new_listings)} new properties today")
    for _, row in new_listings.iterrows():
        col1, col2 = st.columns([3, 1])
        col1.write(f"**{row['title']}**\n{row['price']}")
        if col2.button("⭐ Shortlist", key=row['id']):
            # Logic to save to shortlist (requires a small backend write)
            st.success("Added!")

with tab2:
    st.write("Shortlisted items will appear here.")
