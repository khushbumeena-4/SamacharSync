import streamlit as st
import requests
from bs4 import BeautifulSoup

st.title("📰 News Aggregator")

headers = {"User-Agent": "Mozilla/5.0"}

def get_news(url, base):
    news = []
    try:
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")

        for a in soup.find_all("a", href=True):
            title = a.get_text().strip()
            link = a["href"]

            if len(title) > 25:
                full_link = link if link.startswith("http") else base + link
                news.append((title, full_link))

            if len(news) >= 10:
                break
    except:
        st.write("Error loading news")

    return news


# Sources
bbc = get_news("https://www.bbc.com/news", "https://www.bbc.com")
cnn = get_news("https://edition.cnn.com", "https://edition.cnn.com")
toi = get_news("https://timesofindia.indiatimes.com", "https://timesofindia.indiatimes.com")

source = st.sidebar.selectbox("Select Source", ["BBC", "CNN", "TOI"])

if source == "BBC":
    data = bbc
elif source == "CNN":
    data = cnn
else:
    data = toi

for title, link in data:
    st.write(f"[{title}]({link})")
    st.write("---")