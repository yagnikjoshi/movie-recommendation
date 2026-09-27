import streamlit as st

def inject_custom_css():
    """Inject modern cinematic dark mode styles into Streamlit app."""
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* =========================================================
       MAIN BACKGROUND
    ========================================================= */
    .stApp {
        background: radial-gradient(ellipse at 10% 20%, rgba(229,9,20,0.07) 0%, transparent 50%),
                    radial-gradient(ellipse at 90% 80%, rgba(0,210,255,0.06) 0%, transparent 50%),
                    linear-gradient(160deg, #09090f 0%, #0f0f1b 40%, #141427 100%);
        color: #e0e6ed;
        min-height: 100vh;
    }

    /* Remove Streamlit default top-padding */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
    }

    /* =========================================================
       HERO SECTION
    ========================================================= */
    .hero-banner {
        text-align: center;
        padding: 2.5rem 1rem 1.5rem;
        position: relative;
    }

    .hero-banner::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: radial-gradient(ellipse at center, rgba(229,9,20,0.12) 0%, transparent 70%);
        pointer-events: none;
    }

    .main-title {
        font-family: 'Outfit', sans-serif;
        font-weight: 900;
        font-size: 3.6rem;
        background: linear-gradient(90deg, #ff1e1e 0%, #ff6b6b 35%, #ffd6d6 55%, #00d2ff 80%, #0099cc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -1px;
        line-height: 1.1;
        animation: titleShimmer 4s ease-in-out infinite;
    }

    @keyframes titleShimmer {
        0%, 100% { filter: brightness(1); }
        50% { filter: brightness(1.15); }
    }

    .sub-title {
        font-size: 1.1rem;
        color: #7f8fa6;
        font-weight: 400;
        margin-top: 0.5rem;
        margin-bottom: 1.5rem;
        letter-spacing: 0.3px;
    }

    /* =========================================================
       STAT PILL CARDS
    ========================================================= */
    .stats-row {
        display: flex;
        gap: 12px;
        justify-content: center;
        flex-wrap: wrap;
        margin-bottom: 2rem;
    }

    .stat-pill {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 50px;
        padding: 8px 20px;
        font-size: 0.85rem;
        color: #94a3b8;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        backdrop-filter: blur(8px);
    }

    .stat-pill strong {
        color: #00d2ff;
        font-weight: 700;
    }

    /* =========================================================
       TABS
    ========================================================= */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: rgba(15,15,27,0.8);
        padding: 6px;
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.06);
        backdrop-filter: blur(16px);
    }

    .stTabs [data-baseweb="tab"] {
        height: 44px;
        white-space: pre-wrap;
        border-radius: 12px;
        color: #64748b;
        font-weight: 500;
        font-size: 0.9rem;
        padding: 0 18px;
        transition: all 0.25s ease;
        border: 1px solid transparent;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #cbd5e1;
        background: rgba(255,255,255,0.04);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(229,9,20,0.25) 0%, rgba(0,210,255,0.18) 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border: 1px solid rgba(229,9,20,0.4) !important;
        box-shadow: 0 4px 16px rgba(229,9,20,0.2);
    }

    /* =========================================================
       NETFLIX-STYLE HORIZONTAL SCROLL
    ========================================================= */
    .horizontal-scroll-container {
        display: flex;
        overflow-x: auto;
        gap: 16px;
        padding: 10px 0 20px 0;
        scroll-snap-type: x mandatory;
        scrollbar-width: thin;
        scrollbar-color: rgba(229,9,20,0.6) rgba(0,0,0,0.2);
    }
    
    .horizontal-scroll-container::-webkit-scrollbar {
        height: 8px;
    }
    
    .horizontal-scroll-container::-webkit-scrollbar-track {
        background: rgba(0,0,0,0.2);
        border-radius: 10px;
    }
    
    .horizontal-scroll-container::-webkit-scrollbar-thumb {
        background: rgba(229,9,20,0.6);
        border-radius: 10px;
    }

    .horizontal-scroll-container::-webkit-scrollbar-thumb:hover {
        background: rgba(229,9,20,0.8);
    }

    .scroll-item {
        flex: 0 0 220px; /* Fixed width for cards */
        scroll-snap-align: start;
    }

    /* =========================================================
       GLASSMORPHISM MOVIE CARDS
    ========================================================= */
    .movie-card {
        background: rgba(20, 21, 36, 0.80);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 18px;
        padding: 14px;
        transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275),
                    box-shadow 0.3s ease,
                    border-color 0.3s ease;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        position: relative;
        overflow: hidden;
    }

    .movie-card::after {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 2px;
        background: linear-gradient(90deg, transparent, rgba(229,9,20,0.5), transparent);
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .movie-card:hover {
        transform: translateY(-8px) scale(1.01);
        border-color: rgba(229,9,20,0.35);
        box-shadow: 0 24px 48px -12px rgba(229,9,20,0.25), 0 8px 32px rgba(0,0,0,0.5);
    }

    .movie-card:hover::after {
        opacity: 1;
    }

    /* Poster Image */
    .poster-img {
        width: 100%;
        border-radius: 12px;
        object-fit: cover;
        aspect-ratio: 2/3;
        box-shadow: 0 6px 20px rgba(0,0,0,0.5);
        margin-bottom: 12px;
        transition: transform 0.4s ease;
        display: block;
    }

    .movie-card:hover .poster-img {
        transform: scale(1.03);
    }

    .movie-title {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        font-size: 1.0rem;
        color: #f1f5f9;
        margin: 6px 0 4px;
        line-height: 1.3;
    }

    .movie-meta {
        font-size: 0.75rem;
        color: #64748b;
        margin-bottom: 8px;
    }

    /* =========================================================
       BADGES
    ========================================================= */
    .badge-container {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
        margin: 6px 0 10px;
    }

    .genre-badge {
        background: rgba(0,210,255,0.12);
        color: #38bdf8;
        border: 1px solid rgba(56,189,248,0.25);
        padding: 2px 9px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.2px;
        white-space: nowrap;
    }

    .rating-badge {
        background: rgba(251,191,36,0.12);
        color: #fbbf24;
        border: 1px solid rgba(251,191,36,0.3);
        padding: 2px 9px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
    }

    .year-badge {
        background: rgba(148,163,184,0.1);
        color: #94a3b8;
        border: 1px solid rgba(148,163,184,0.2);
        padding: 2px 9px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 500;
    }

    .match-badge {
        background: linear-gradient(90deg, #e50914, #ff6060);
        color: #fff;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 800;
        box-shadow: 0 4px 12px rgba(229,9,20,0.4);
        letter-spacing: 0.3px;
    }

    .high-match {
        background: linear-gradient(90deg, #059669, #34d399);
        box-shadow: 0 4px 12px rgba(5,150,105,0.4);
    }

    /* =========================================================
       STAR RATING DISPLAY
    ========================================================= */
    .star-row {
        display: flex;
        align-items: center;
        gap: 4px;
        margin: 4px 0;
    }

    .star-filled { color: #fbbf24; font-size: 0.85rem; }
    .star-empty  { color: #374151; font-size: 0.85rem; }
    .rating-num  { color: #94a3b8; font-size: 0.75rem; margin-left: 4px; }

    /* =========================================================
       PROGRESS / SIMILARITY BAR
    ========================================================= */
    .sim-bar-container {
        background: rgba(255,255,255,0.06);
        border-radius: 50px;
        height: 6px;
        margin-top: 6px;
        overflow: hidden;
    }

    .sim-bar-fill {
        height: 100%;
        border-radius: 50px;
        background: linear-gradient(90deg, #e50914, #ff758c);
        transition: width 0.6s ease;
    }

    /* =========================================================
       SECTION HEADERS
    ========================================================= */
    .section-header {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        font-size: 1.5rem;
        color: #f1f5f9;
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 1.2rem;
        padding-bottom: 0.6rem;
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }

    .section-header .icon {
        background: linear-gradient(135deg, #e50914, #ff4b4b);
        width: 36px; height: 36px;
        border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.1rem;
        box-shadow: 0 4px 12px rgba(229,9,20,0.3);
    }

    /* =========================================================
       SELECTED MOVIE DETAIL CARD
    ========================================================= */
    .seed-card {
        background: linear-gradient(135deg, rgba(229,9,20,0.08) 0%, rgba(0,210,255,0.06) 100%);
        border: 1px solid rgba(229,9,20,0.2);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px rgba(229,9,20,0.1);
    }

    .seed-card h3 {
        font-family: 'Outfit', sans-serif;
        font-weight: 800;
        font-size: 1.6rem;
        color: #f8fafc;
        margin: 0 0 6px;
    }

    .overview-text {
        font-size: 0.88rem;
        line-height: 1.65;
        color: #94a3b8;
    }

    /* =========================================================
       BUTTONS
    ========================================================= */
    .stButton > button {
        background: linear-gradient(90deg, #e50914 0%, #ff4b4b 100%);
        color: white !important;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        border: none !important;
        border-radius: 10px;
        padding: 0.55rem 1.2rem;
        transition: all 0.25s ease;
        box-shadow: 0 4px 14px rgba(229,9,20,0.3);
        width: 100%;
        letter-spacing: 0.2px;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(229,9,20,0.55) !important;
        background: linear-gradient(90deg, #ff1e27 0%, #ff6565 100%) !important;
    }

    .stButton > button:active {
        transform: translateY(0px);
    }

    /* =========================================================
       SIDEBAR
    ========================================================= */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0c0d18 0%, #111120 100%);
        border-right: 1px solid rgba(255,255,255,0.05);
    }

    [data-testid="stSidebar"] .sidebar-logo {
        font-family: 'Outfit', sans-serif;
        font-weight: 900;
        font-size: 1.6rem;
        background: linear-gradient(90deg, #e50914, #ff758c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        padding: 0.5rem 0;
    }

    .sidebar-divider {
        border: none;
        border-top: 1px solid rgba(255,255,255,0.06);
        margin: 1rem 0;
    }

    .sidebar-section-title {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        color: #475569;
        margin-bottom: 0.6rem;
    }

    .stat-box {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 8px;
        text-align: center;
    }

    .stat-box .val { font-size: 1.6rem; font-weight: 800; color: #00d2ff; font-family: 'Outfit', sans-serif; }
    .stat-box .lbl { font-size: 0.72rem; color: #475569; margin-top: 2px; }

    /* =========================================================
       COMPARE MOVIE PANEL
    ========================================================= */
    .compare-panel {
        background: rgba(20,21,36,0.7);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 18px;
        padding: 18px;
        height: 100%;
    }

    .compare-vs {
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Outfit', sans-serif;
        font-weight: 900;
        font-size: 2rem;
        color: #e50914;
        height: 100%;
        text-shadow: 0 0 30px rgba(229,9,20,0.5);
    }

    /* =========================================================
       WATCHLIST EMPTY STATE
    ========================================================= */
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        color: #475569;
    }

    .empty-state .icon {
        font-size: 3.5rem;
        margin-bottom: 1rem;
    }

    .empty-state h3 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        font-size: 1.3rem;
        color: #64748b;
        margin-bottom: 0.5rem;
    }

    .empty-state p {
        font-size: 0.9rem;
    }

    /* =========================================================
       SURPRISE ME
    ========================================================= */
    .surprise-card {
        background: linear-gradient(135deg, rgba(229,9,20,0.1) 0%, rgba(0,210,255,0.08) 100%);
        border: 1px solid rgba(229,9,20,0.25);
        border-radius: 22px;
        padding: 28px;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 12px 40px rgba(229,9,20,0.12);
    }

    .surprise-card h2 {
        font-family: 'Outfit', sans-serif;
        font-weight: 900;
        font-size: 2rem;
        color: #f8fafc;
        margin-bottom: 0.5rem;
    }

    .surprise-card p {
        color: #7f8fa6;
        font-size: 0.95rem;
    }

    /* =========================================================
       FILTER ROW PILLS
    ========================================================= */
    .filter-tag {
        display: inline-block;
        background: rgba(229,9,20,0.15);
        border: 1px solid rgba(229,9,20,0.3);
        color: #ff6b6b;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        margin: 2px;
    }

    /* =========================================================
       SCROLLBAR STYLING
    ========================================================= */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0f0f1b; }
    ::-webkit-scrollbar-thumb { background: #e50914; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #ff4b4b; }

    /* =========================================================
       INPUT / SELECT OVERRIDES
    ========================================================= */
    .stSelectbox > div > div,
    .stTextInput > div > div > input {
        background: rgba(20,21,36,0.9) !important;
        border: 1px solid rgba(255,255,255,0.09) !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
    }

    .stSelectbox > div > div:focus-within,
    .stTextInput > div > div > input:focus {
        border-color: rgba(229,9,20,0.5) !important;
        box-shadow: 0 0 0 2px rgba(229,9,20,0.15) !important;
    }

    /* =========================================================
       EXPANDER
    ========================================================= */
    .streamlit-expanderHeader {
        background: rgba(20,21,36,0.6) !important;
        border: 1px solid rgba(255,255,255,0.07) !important;
        border-radius: 10px !important;
        color: #94a3b8 !important;
        font-size: 0.9rem !important;
    }

    /* =========================================================
       METRICS
    ========================================================= */
    [data-testid="metric-container"] {
        background: rgba(20,21,36,0.7);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 12px 16px;
    }

    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #00d2ff !important;
        font-family: 'Outfit', sans-serif;
    }

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_star_rating(rating, max_stars=10, display_stars=5):
    """Render a visual star rating component."""
    filled = round((rating / max_stars) * display_stars)
    stars_html = ""
    for i in range(display_stars):
        if i < filled:
            stars_html += '<span class="star-filled">★</span>'
        else:
            stars_html += '<span class="star-empty">★</span>'
    return f'<div class="star-row">{stars_html}<span class="rating-num">{rating}/10</span></div>'


def render_match_bar(match_pct):
    """Render a horizontal similarity bar."""
    color = "#34d399" if match_pct >= 80 else "#fbbf24" if match_pct >= 70 else "#f87171"
    return f"""
    <div class="sim-bar-container">
        <div class="sim-bar-fill" style="width:{match_pct}%; background: {color};"></div>
    </div>
    <div style="font-size:0.7rem; color:#64748b; margin-top:3px;">{match_pct}% content match</div>
    """


def render_genre_badges(genres_str):
    """Render genre badge pills from comma-separated string."""
    badges = ""
    for g in genres_str.split(","):
        g = g.strip()
        if g:
            badges += f'<span class="genre-badge">{g}</span>'
    return f'<div class="badge-container">{badges}</div>'
