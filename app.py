import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime
import os

# --- CONFIGURATION ---
TARGET_URL = "https://www.lankapropertyweb.com/house/forsale/mount-lavinia/"
DB_FILE = "property_db.csv"

def get_data():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(TARGET_URL, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        listings = []
        for card in soup.select('.cl-listing-card'):
            link_tag = card.find('a')
            if not link_tag: continue
            link = "https://www.lankapropertyweb.com" + link_tag['href']
            prop_id = link.split('/')[-2] 
            listings.append({
                "id": str(prop_id), # Ensure ID is always a string
                "title": card.select_one('.cl-listing-title').text.strip(),
                "price": card.select_one('.price').text.strip(),
                "link": link,
                "date_found": datetime.date.today().strftime("%Y-%m-%d")
            })
        return pd.DataFrame(listings)
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame(columns=["id", "title", "price", "link", "date_found"])

# --- APP INTERFACE ---
st.title("👨‍🦳 Dad's Property Assistant")

# Safety Check: Load or create history
if os.path.exists(DB_FILE):
    history_df = pd.read_csv(DB_FILE, dtype={'id': str})
else:
    # This part prevents the KeyError you saw
    history_df = pd.DataFrame(columns=["id", "shortlisted"])

live_df = get_data()

# Logic: Filter out what he has already seen
if not live_df.empty:
    new_listings = live_df[~live_df['id'].isin(history_df['id'])]
else:
    new_listings = pd.DataFrame()

tab1, tab2 = st.tabs(["🆕 New Matches", "⭐ Shortlist"])

with tab1:
    if new_listings.empty:
        st.info("No new houses found since your last check!")
    else:
        st.subheader(f"Found {len(new_listings)} new properties")
        for _, row in new_listings.iterrows():
            with st.container(border=True):
                st.write(f"**{row['title']}**")
                st.write(f"💰 {row['price']}")
                col1, col2 = st.columns(2)
                col1.link_button("View Website", row['link'])
                if col2.button("⭐ Shortlist", key=row['id']):
                    st.success("Saved!")

with tab2:
    st.write("Shortlisted items will appear here soon.")
