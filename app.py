import streamlit as st
import requests
import time

API_KEY = "a246fe035696496cbd05283f2b828b0c"  # Your NewsAPI key

# Page configuration
st.set_page_config(
    page_title="📰 SamacharSync",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
if 'news_cache' not in st.session_state:
    st.session_state.news_cache = {}

# Theme toggle function
def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

# CSS Styling with gradient backgrounds
def apply_styles():
    if st.session_state.theme == 'dark':
        bg_gradient = "linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)"
        card_bg = "rgba(255, 255, 255, 0.05)"
        text_color = "#ffffff"
        secondary_text = "#b0b0b0"
        accent_color = "#e94560"
        border_color = "rgba(255, 255, 255, 0.1)"
        input_bg = "rgba(255, 255, 255, 0.1)"
        sidebar_bg = "linear-gradient(180deg, #1a1a2e 0%, #16213e 100%)"
    else:
        bg_gradient = "linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)"
        card_bg = "rgba(255, 255, 255, 0.9)"
        text_color = "#1a1a2e"
        secondary_text = "#4a4a4a"
        accent_color = "#e94560"
        border_color = "rgba(0, 0, 0, 0.1)"
        input_bg = "rgba(255, 255, 255, 0.8)"
        sidebar_bg = "linear-gradient(180deg, #667eea 0%, #764ba2 100%)"

    st.markdown(f"""
    <style>
        .stApp {{
            background: {bg_gradient};
            background-attachment: fixed;
        }}
        [data-testid="stSidebar"] {{
            background: {sidebar_bg};
        }}
        [data-testid="stSidebar"] * {{
            color: {text_color} !important;
        }}
        .main-header {{
            font-size: 3rem;
            font-weight: 700;
            text-align: center;
            color: {text_color};
            padding: 1rem 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            margin-bottom: 1rem;
        }}
        .news-card {{
            background: {card_bg};
            border-radius: 16px;
            padding: 1.5rem;
            margin: 1rem 0;
            border: 1px solid {border_color};
            backdrop-filter: blur(10px);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        .news-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        .news-title {{
            font-size: 1.2rem;
            font-weight: 600;
            color: {text_color};
            margin-bottom: 0.5rem;
            line-height: 1.4;
        }}
        .news-title a {{
            color: {text_color};
            text-decoration: none;
        }}
        .news-title a:hover {{
            color: {accent_color};
        }}
        .news-meta {{
            font-size: 0.85rem;
            color: {secondary_text};
        }}
        .category-badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-right: 0.5rem;
            background: {accent_color};
            color: white;
        }}
        .trending-section {{
            background: linear-gradient(135deg, {accent_color} 0%, #ff6b6b 100%);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }}
        .trending-title {{
            font-size: 1.5rem;
            font-weight: 700;
            color: white;
            margin-bottom: 1rem;
        }}
        .trending-item {{
            background: rgba(255,255,255,0.15);
            border-radius: 10px;
            padding: 0.75rem 1rem;
            margin: 0.5rem 0;
            color: white;
        }}
        .trending-item a {{
            color: white;
            text-decoration: none;
        }}
        .stTextInput > div > div > input {{
            background: {input_bg} !important;
            border-radius: 25px !important;
            color: {text_color} !important;
            border: 1px solid {border_color} !important;
            padding: 0.75rem 1.5rem !important;
        }}
        .stButton > button {{
            border-radius: 25px !important;
            padding: 0.5rem 2rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }}
        .news-image {{
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-radius: 12px;
            margin-bottom: 1rem;
        }}
        .loading-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 2rem;
        }}
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        .loading-text {{
            animation: pulse 1.5s ease-in-out infinite;
            color: {text_color};
            font-size: 1.2rem;
        }}
        .section-divider {{
            height: 3px;
            background: linear-gradient(90deg, transparent, {accent_color}, transparent);
            margin: 2rem 0;
            border-radius: 2px;
        }}
        .stat-card {{
            background: {card_bg};
            border-radius: 12px;
            padding: 1rem;
            text-align: center;
            border: 1px solid {border_color};
        }}
        .stat-number {{
            font-size: 2rem;
            font-weight: 700;
            color: {accent_color};
        }}
        .stat-label {{
            color: {secondary_text};
            font-size: 0.9rem;
        }}
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

apply_styles()

# Category keywords for filtering
CATEGORY_KEYWORDS = {
    "Technology": ["tech", "technology", "ai", "artificial", "robot", "software", "apple", "google", "microsoft", "computer", "digital", "cyber", "internet", "startup", "innovation", "gadget", "smartphone", "app"],
    "Sports": ["sport", "football", "soccer", "cricket", "tennis", "basketball", "olympics", "nba", "nfl", "fifa", "match", "tournament", "championship", "athlete", "team", "game", "league", "player"],
    "Business": ["business", "economy", "market", "stock", "finance", "bank", "investment", "company", "corporate", "trade", "economic", "profit", "revenue", "startup", "entrepreneur", "ceo"],
    "Entertainment": ["entertainment", "movie", "film", "music", "celebrity", "hollywood", "bollywood", "actor", "actress", "concert", "album", "tv", "show", "streaming", "netflix", "disney"],
    "Politics": ["politic", "government", "election", "minister", "president", "parliament", "congress", "senate", "vote", "policy", "law", "legislation", "democracy", "campaign"],
    "Health": ["health", "medical", "doctor", "hospital", "disease", "vaccine", "covid", "treatment", "medicine", "healthcare", "wellness", "mental", "fitness", "diet", "nutrition"],
    "Science": ["science", "research", "study", "discover", "space", "nasa", "climate", "environment", "physics", "chemistry", "biology", "scientist", "laboratory", "experiment"]
}

def categorize_news(title):
    title_lower = title.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in title_lower for keyword in keywords):
            return category
    return "General"

# Map your sidebar "sources" to NewsAPI sources or queries
NEWSAPI_SOURCES = {
    "BBC": {"sources": "bbc-news"},
    "CNN": {"sources": "cnn"},
    "Reuters": {"sources": "reuters"},
    "The Guardian": {"sources": "the-guardian-uk"},
    # Indian sources not in NewsAPI: use query instead
    "Times of India": {"q": "India"},
    "The Hindu": {"q": "India"},
    "Dainik Bhaskar": {"q": "India"},
    "Economic Times": {"q": "business OR economy"},
}

def fetch_news_from_newsapi(source_name, search_query=None, page_size=20):
    """Fetch news using NewsAPI instead of scraping."""
    cache_key = f"{source_name}_{search_query or ''}"
    # Cache for 5 minutes
    if cache_key in st.session_state.news_cache:
        cache_time, data = st.session_state.news_cache[cache_key]
        if time.time() - cache_time < 300:
            return data

    params = {
        "apiKey": API_KEY,
        "language": "en",
        "pageSize": page_size,
        "sortBy": "publishedAt"
    }

    base_params = NEWSAPI_SOURCES.get(source_name, {})
    params.update(base_params)

    # Apply search query if provided
    if search_query:
        # If base already has q, append search term
        if "q" in params:
            params["q"] = f"{params['q']} {search_query}"
        else:
            params["q"] = search_query

    # Use /everything for flexibility (domains, queries, etc.)
    url = "https://newsapi.org/v2/everything"
    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        if data.get("status") != "ok":
            st.error(f"NewsAPI error for {source_name}: {data.get('message', 'Unknown error')}")
            articles = []
        else:
            articles = data.get("articles", [])

        news_items = []
        for art in articles:
            title = art.get("title") or ""
            if not title:
                continue
            category = categorize_news(title)
            news_items.append({
                "title": title,
                "link": art.get("url"),
                "category": category,
                "image": art.get("urlToImage"),
                "source": source_name
            })

        st.session_state.news_cache[cache_key] = (time.time(), news_items)
        return news_items

    except Exception as e:
        st.error(f"Error loading news from {source_name}: {str(e)}")
        return []

def display_news_card(item, show_image=True):
    image_html = ""
    if show_image and item.get("image"):
        image_html = f'<img src="{item["image"]}" class="news-image" onerror="this.style.display=\'none\'" />'

    st.markdown(f"""
    <div class="news-card">
        {image_html}
        <span class="category-badge">{item['category']}</span>
        <span class="category-badge" style="background: #3498db;">{item['source']}</span>
        <div class="news-title">
            <a href="{item['link']}" target="_blank">{item['title']}</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_trending(news_items):
    if not news_items:
        return

    trending = news_items[:5]
    st.markdown("""
    <div class="trending-section">
        <div class="trending-title">🔥 Trending Now</div>
    """, unsafe_allow_html=True)

    for i, item in enumerate(trending, 1):
        st.markdown(f"""
        <div class="trending-item">
            <strong>#{i}</strong> <a href="{item['link']}" target="_blank">{item['title'][:80]}...</a>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")

    # Theme toggle
    theme_label = "🌙 Dark Mode" if st.session_state.theme == 'light' else "☀️ Light Mode"
    if st.button(theme_label, use_container_width=True):
        toggle_theme()
        st.rerun()

    st.markdown("---")

    # Source selection
    st.markdown("### 📡 News Sources")
    sources = st.multiselect(
        "Select sources",
        [
            "BBC",
            "CNN",
            "Times of India",
            "The Hindu",
            "Dainik Bhaskar",
            "Economic Times",
            "Reuters",
            "The Guardian"
        ],
        default=["Times of India", "The Hindu", "Economic Times"]
    )

    st.markdown("---")

    # Category filter
    st.markdown("### 🏷️ Categories")
    categories = st.multiselect(
        "Filter by category",
        ["All", "Technology", "Sports", "Business", "Entertainment", "Politics", "Health", "Science", "General"],
        default=["All"]
    )

    st.markdown("---")

    # Display options
    st.markdown("### 🖼️ Display Options")
    show_images = st.checkbox("Show image previews", value=True)
    show_trending = st.checkbox("Show trending section", value=True)

    st.markdown("---")

    # Refresh button
    if st.button("🔄 Refresh News", use_container_width=True):
        st.session_state.news_cache = {}
        st.rerun()

# Main content
st.markdown('<h1 class="main-header">📰 SamacharSync</h1>', unsafe_allow_html=True)

# Search bar
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    search_query = st.text_input("🔍 Search news...", placeholder="Enter keywords to search")

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# Fetch news (from NewsAPI)
all_news = []

if sources:
    with st.spinner("📡 Fetching latest news..."):
        progress_bar = st.progress(0)
        for i, source in enumerate(sources):
            if source in NEWSAPI_SOURCES:
                news = fetch_news_from_newsapi(source, search_query=search_query)
                all_news.extend(news)
            progress_bar.progress((i + 1) / len(sources))
        progress_bar.empty()

# Filter by category (after fetching)
if "All" not in categories and categories:
    all_news = [item for item in all_news if item['category'] in categories]

# Display stats
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{len(all_news)}</div>
        <div class="stat-label">Articles Found</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{len(sources)}</div>
        <div class="stat-label">Sources Active</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    tech_count = len([n for n in all_news if n['category'] == 'Technology'])
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{tech_count}</div>
        <div class="stat-label">Tech Articles</div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    sports_count = len([n for n in all_news if n['category'] == 'Sports'])
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{sports_count}</div>
        <div class="stat-label">Sports Articles</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# Trending
if show_trending and all_news and not search_query:
    display_trending(all_news)
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# News grid
if all_news:
    cols = st.columns(2)
    for i, item in enumerate(all_news):
        with cols[i % 2]:
            display_news_card(item, show_images)
else:
    st.markdown("""
    <div style="text-align: center; padding: 3rem;">
        <h2>No news found</h2>
        <p>Try adjusting your filters or search query</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; opacity: 0.7; padding: 1rem;">
    <p>📰 SamacharSync| Data refreshes every 5 minutes</p>
</div>
""", unsafe_allow_html=True)

