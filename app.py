import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import math
import dataset
from recommendation_engine import RecommendationEngine
from styles import inject_custom_css, render_star_rating, render_match_bar, render_genre_badges

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="CineIndia | Indian Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "CineIndia – Indian Movie Recommendation System. Bollywood, Tamil, Telugu, Malayalam & Kannada."
    }
)

inject_custom_css()

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
defaults = {
    'watchlist':      [],
    'surprise_movie': None,
    # Recommendation quiz
    'rec_step':    0,
    'rec_answers': {},
    'rec_results': None,
    # Mood quiz
    'mood_step':    0,
    'mood_answers': {},
    'mood_results': None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────
# DATA & ENGINE
# ─────────────────────────────────────────────
@st.cache_data
def load_data(dummy_bust_cache=2):
    return dataset.get_movie_data()

@st.cache_resource
def build_engine(df):
    return RecommendationEngine(df)

df            = load_data()
engine        = build_engine(df)
all_genres    = dataset.get_all_genres(df)
all_industries= dataset.get_all_industries(df)
all_languages = dataset.get_all_languages(df)
all_years     = sorted(df['release_year'].unique().tolist())

IND_CLR = {
    "Bollywood": "#FF9933",
    "Tamil":     "#138808",
    "Telugu":    "#4169E1",
    "Malayalam": "#9370DB",
    "Kannada":   "#e53935",
    "Gujarati":  "#f43f5e",
    "Hollywood": "#00d2ff"
}

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🎬 CineMatch Pro</div>', unsafe_allow_html=True)
    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-title">⚙️ Settings</div>', unsafe_allow_html=True)
    top_n      = st.slider("Recommendations to show", 3, 12, 6)
    pop_weight = st.slider("Popularity ↔ Similarity", 0.0, 1.0, 0.25, 0.05,
                           help="0 = Pure content match | 1 = Most popular")

    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-title">🎭 Industries</div>', unsafe_allow_html=True)
    ind_counts = df['industry'].value_counts()
    for ind, cnt in ind_counts.items():
        clr = IND_CLR.get(ind, "#94a3b8")
        st.markdown(
            f'<div style="font-size:0.8rem;padding:3px 0;display:flex;justify-content:space-between;">'
            f'<span style="color:{clr};font-weight:700;">● {ind}</span>'
            f'<span style="color:#475569;">{cnt} films</span></div>',
            unsafe_allow_html=True)

    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-title">📊 Stats</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="stat-box"><div class="val">{len(df):,}</div><div class="lbl">Movies</div></div>',
                    unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-box"><div class="val">{len(all_genres)}</div><div class="lbl">Genres</div></div>',
                    unsafe_allow_html=True)
    st.markdown(f'<div class="stat-box"><div class="val">{df["vote_average"].mean():.1f}</div><div class="lbl">Avg Rating</div></div>',
                unsafe_allow_html=True)
    st.markdown(f'<div class="stat-box"><div class="val">{int(df["runtime"].mean())}m</div><div class="lbl">Avg Runtime</div></div>',
                unsafe_allow_html=True)

    wl = len(st.session_state.watchlist)
    if wl:
        st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-box"><div class="val">{wl}</div><div class="lbl">📌 Watchlist</div></div>',
                    unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HERO BANNER
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="hero-banner">
    <div class="main-title">🌍 CineMatch Pro</div>
    <div class="sub-title">AI-powered Global Movie Recommendations — Hollywood • Bollywood • Regional Indian</div>
    <div class="stats-row">
        <div class="stat-pill">🎬 <strong>{len(df):,}</strong> Films</div>
        <div class="stat-pill">🎭 <strong>{len(all_genres)}</strong> Genres</div>
        <div class="stat-pill">⭐ Avg <strong>{df['vote_average'].mean():.1f}</strong>/10</div>
        <div class="stat-pill">🎦 <strong>{len(all_industries)}</strong> Industries</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab_discover, tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🌟 Discover",
    "🎯 Recommendations",
    "🎭 Mood Finder",
    "🔍 Browse",
    "📊 Analytics",
    "🆚 Compare",
    "📌 Watchlist",
    "🎲 Surprise Me",
])

# ══════════════════════════════════════════════════════════════════
# TAB 0 – DISCOVER (IMDb Style)
# ══════════════════════════════════════════════════════════════════
with tab_discover:
    st.markdown('<div class="section-header"><span class="icon">🌟</span> Discover Masterpieces & Trending</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#64748b;margin-bottom:1.5rem;">Explore the highest-rated films based on the official IMDb weighted rating formula, trending blockbusters, and dynamic content matches.</p>', unsafe_allow_html=True)

    def render_movie_card(m):
        mpct = int(m.get('norm_rating', 0.8) * 100) if 'norm_rating' in m else 95
        iclr = IND_CLR.get(m.get('industry',''), '#94a3b8')
        # We must NOT have leading spaces in the HTML, otherwise Streamlit markdown treats it as a code block!
        return f"""
<div class="scroll-item">
    <div class="movie-card" style="margin-bottom:0; height:100%;">
        <img src="{m['poster_path']}" data-title="{m['title']}" data-year="{m.get('release_year', '')}" class="poster-img tmdb-poster" style="aspect-ratio:2/3; background:#1e1e2f;">
        <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
            <span class="rating-badge" style="font-size:0.75rem;">⭐ {m['vote_average']}</span>
            <span class="year-badge" style="font-size:0.75rem;">{m['release_year']}</span>
        </div>
        <div class="movie-title" style="font-size:0.9rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{m['title']}</div>
        <div style="margin:4px 0;">
            <span style="font-size:0.65rem;font-weight:700;color:{iclr};
                background:rgba(255,255,255,0.05);padding:2px 6px;border-radius:10px;
                border:1px solid {iclr}44;">● {m.get('industry','')}</span>
        </div>
    </div>
</div>
"""

    # Section 1: IMDb Top Rated
    st.markdown("#### 🏆 All-Time Masterpieces (IMDb Weighted Rating)")
    # Using engine.df because it contains the computed 'norm_rating' and 'weighted_rating'
    top_rated = engine.df.sort_values('norm_rating', ascending=False).head(15).to_dict('records')
    cards_html = "".join([render_movie_card(m) for m in top_rated])
    st.markdown(f'<div class="horizontal-scroll-container">{cards_html}</div>', unsafe_allow_html=True)

    # Section 2: Blockbusters (Most Voted)
    st.markdown("#### 🔥 Trending Blockbusters (Most Votes)")
    trending = df.sort_values('vote_count', ascending=False).head(15).to_dict('records')
    cards_html2 = "".join([render_movie_card(m) for m in trending])
    st.markdown(f'<div class="horizontal-scroll-container">{cards_html2}</div>', unsafe_allow_html=True)

    # Section 3: Dynamic Because You Liked
    import random
    random_top_movie = random.choice(top_rated[:30]) if len(top_rated) > 0 else df.iloc[0].to_dict()
    st.markdown(f"#### 💡 Because you might like **{random_top_movie['title']}**")
    recs = engine.recommend(random_top_movie['title'], top_n=10)
    if not recs.empty:
        cards_html3 = "".join([render_movie_card(m) for m in recs.to_dict('records')])
        st.markdown(f'<div class="horizontal-scroll-container">{cards_html3}</div>', unsafe_allow_html=True)

    # Magic Client-Side Script to Fetch Posters!
    import streamlit.components.v1 as components
    components.html("""
    <script>
        const tmdbKey = '15d2ea6d0dc1d476efbca3eba2b9bbfb'; // Public key used for tutorials
        // Wait a tiny bit for DOM to render in parent
        setTimeout(() => {
            const posters = window.parent.document.querySelectorAll('.tmdb-poster');
            posters.forEach(img => {
                if(img.dataset.loaded) return;
                img.dataset.loaded = "true";
                
                let q = encodeURIComponent(img.dataset.title);
                let y = img.dataset.year ? `&year=${img.dataset.year}` : '';
                let url = `https://api.themoviedb.org/3/search/movie?api_key=${tmdbKey}&query=${q}${y}`;
                
                fetch(url)
                    .then(res => res.json())
                    .then(data => {
                        if(data.results && data.results.length > 0 && data.results[0].poster_path) {
                            img.src = 'https://image.tmdb.org/t/p/w500' + data.results[0].poster_path;
                        }
                    })
                    .catch(e => console.error(e));
            });
        }, 500);
    </script>
    """, height=0, width=0)

# ══════════════════════════════════════════════════════════════════
# TAB 1 – SMART RECOMMENDATIONS  (question-driven)
# ══════════════════════════════════════════════════════════════════
with tab1:

    # ── Shared data for quiz ──────────────────────────────────────
    ACTOR_OPTIONS    = ["Any actor 🌐"] + sorted({
        a.strip() for row in df['cast'] for a in row.split(',') if len(a.strip()) > 3
    })
    DIRECTOR_OPTIONS = ["Any director 🌐"] + sorted(df['director'].unique().tolist())

    GENRE_OPTIONS = [
        "🎭 Drama",          "❤️ Romance",        "💥 Action",
        "😂 Comedy",         "🔍 Thriller",       "🏅 Sport / Bio",
        "👻 Horror / Dark",  "🏰 Historical",     "🚀 Sci-Fi / Fantasy",
        "🎵 Music / Dance",  "🕵️ Crime / Heist",  "👨‍👩‍👧 Family",
    ]
    THEME_OPTIONS = [
        "💪 Underdog rises",      "❤️‍🔥 Forbidden love",    "👨‍👧 Father–child bond",
        "🤝 Friendship forever",  "🇮🇳 Patriotism & freedom","🧠 Social injustice",
        "🌍 Road trip / Journey", "🏆 Chasing a dream",      "🕵️ Mystery & twists",
        "⚔️ Power & revenge",     "🎓 College / Youth",       "💸 Rags to riches",
        "👻 Supernatural / Myth", "👩 Woman's journey",       "🎸 Art & creativity",
    ]
    GENRE_KW_MAP = {
        "🎭 Drama":            "Drama",
        "❤️ Romance":          "Romance",
        "💥 Action":           "Action",
        "😂 Comedy":           "Comedy",
        "🔍 Thriller":         "Thriller",
        "🏅 Sport / Bio":      "Sport|Biography",
        "👻 Horror / Dark":    "Horror",
        "🏰 Historical":       "Historical",
        "🚀 Sci-Fi / Fantasy": "Sci-Fi|Fantasy|Mythology",
        "🎵 Music / Dance":    "Music",
        "🕵️ Crime / Heist":    "Crime",
        "👨‍👩‍👧 Family":          "Family",
    }
    THEME_KW_MAP = {
        "💪 Underdog rises":       ["underdog","struggle","rise","dream","ambition"],
        "❤️‍🔥 Forbidden love":      ["forbidden","love","romance","heartbreak","secret"],
        "👨‍👧 Father–child bond":    ["father","daughter","son","parent","family"],
        "🤝 Friendship forever":   ["friendship","friend","dosti","college","buddy"],
        "🇮🇳 Patriotism & freedom": ["freedom","patriot","independence","india","british"],
        "🧠 Social injustice":     ["justice","caste","society","inequality","rights"],
        "🌍 Road trip / Journey":  ["journey","road trip","travel","spain","europe"],
        "🏆 Chasing a dream":      ["dream","success","achievement","win","ambition"],
        "🕵️ Mystery & twists":     ["twist","mystery","suspense","secret","unexpected"],
        "⚔️ Power & revenge":      ["revenge","power","empire","war","battle"],
        "🎓 College / Youth":      ["college","youth","campus","student","young"],
        "💸 Rags to riches":       ["poor","rich","rags","rise","wealth"],
        "👻 Supernatural / Myth":  ["myth","supernatural","ghost","spirit","divine"],
        "👩 Woman's journey":      ["woman","female","girl","independent","empowerment"],
        "🎸 Art & creativity":     ["art","music","painting","creative","dance"],
    }
    ERA_RANGE = {
        "🌐 Any Era":            (1900, 2100),
        "🕰 Classic (pre-2000)": (1900, 1999),
        "🎞 2000s – 2015":       (2000, 2015),
        "🆕 2016 and beyond":    (2016, 2100),
    }
    RUNTIME_RANGE = {
        "🌐 Any Length":         (0,   9999),
        "⚡ Short  (< 2 hrs)":   (0,   119),
        "🎬 Standard (2–3 hrs)": (120, 179),
        "🍿 Epic  (3+ hrs)":     (180, 9999),
    }

    REC_QUESTIONS = [
        {
            "id": "genre", "type": "multi_grid", "cols": 3, "max_select": 99,
            "q":   "🎬 What kind of movie do you want to watch?",
            "sub": "Choose one or more genres — the more you pick, the better we match",
            "options": GENRE_OPTIONS,
        },
        {
            "id": "theme", "type": "multi_grid", "cols": 3, "max_select": 3,
            "q":   "💡 Which themes excite you?",
            "sub": "Pick up to 3 story themes",
            "options": THEME_OPTIONS,
        },
        {
            "id": "industry", "type": "single_grid", "cols": 3,
            "q":   "🎦 Which film industry?",
            "sub": "Bollywood, South Indian, or all of India?",
            "options": ["🌐 All Industries"] + all_industries,
        },
        {
            "id": "era", "type": "single_grid", "cols": 2,
            "q":   "📅 Which era of cinema?",
            "sub": "Choose a time period",
            "options": list(ERA_RANGE.keys()),
        },
        {
            "id": "runtime", "type": "single_grid", "cols": 2,
            "q":   "⏱ How long should the film be?",
            "sub": "Match your schedule",
            "options": list(RUNTIME_RANGE.keys()),
        },
        {
            "id": "actor", "type": "dropdown",
            "q":   "⭐ Any favourite actor?",
            "sub": "Optional — or skip to see all",
            "options": ACTOR_OPTIONS,
        },
        {
            "id": "director", "type": "dropdown",
            "q":   "🎥 Preferred director?",
            "sub": "Optional — or skip",
            "options": DIRECTOR_OPTIONS,
        },
        {
            "id": "min_rating", "type": "rating_slider",
            "q":   "⭐ Minimum acceptable rating?",
            "sub": "Slide to set your quality bar",
            "min": 5, "max": 9, "default": 7,
        },
    ]
    TOTAL_REC = len(REC_QUESTIONS)
    r_step    = st.session_state.rec_step
    r_ans     = st.session_state.rec_answers

    # ── Helper: render a question card header ─────────────────────
    def q_header(q_dict):
        st.markdown(f"""
        <div style="background:rgba(15,16,28,0.92);border:1px solid rgba(255,255,255,0.09);
                    border-left:4px solid #e50914;border-radius:18px;padding:24px 28px;
                    margin-bottom:1.4rem;box-shadow:0 14px 44px rgba(0,0,0,0.5);">
            <div style="font-family:'Outfit',sans-serif;font-weight:800;font-size:1.5rem;
                        color:#f8fafc;margin-bottom:5px;">{q_dict['q']}</div>
            <div style="font-size:0.87rem;color:#64748b;">{q_dict['sub']}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Helper: tricolor step progress ───────────────────────────
    def progress_bar(current, total):
        pct = int(current / total * 100)
        dots = "".join([
            f'<div style="width:26px;height:26px;border-radius:50%;display:flex;align-items:center;'
            f'justify-content:center;font-size:0.68rem;font-weight:700;'
            + ('background:linear-gradient(135deg,#FF9933,#e50914);color:#fff;box-shadow:0 2px 8px rgba(229,9,20,0.4);'
               if i < current else
               'background:rgba(229,9,20,0.75);color:#fff;'
               if i == current else
               'background:rgba(255,255,255,0.06);color:#475569;')
            + f'">{i+1}</div>'
            for i in range(total)
        ])
        st.markdown(f"""
        <div style="margin-bottom:2rem;">
            <div style="display:flex;justify-content:space-between;font-size:0.76rem;color:#475569;margin-bottom:7px;">
                <span>Question {current+1} of {total}</span><span>{pct}% complete</span>
            </div>
            <div style="background:rgba(255,255,255,0.05);border-radius:50px;height:7px;overflow:hidden;">
                <div style="height:100%;width:{pct}%;
                    background:linear-gradient(90deg,#FF9933 0%,#ffffff 50%,#138808 100%);
                    border-radius:50px;transition:width 0.6s ease;
                    box-shadow:0 0 10px rgba(255,153,51,0.35);"></div>
            </div>
            <div style="display:flex;gap:6px;margin-top:8px;">{dots}</div>
        </div>
        """, unsafe_allow_html=True)

    # ════════════════════════════════════════
    # QUIZ IN PROGRESS
    # ════════════════════════════════════════
    if r_step < TOTAL_REC and st.session_state.rec_results is None:

        st.markdown("""
        <div style="text-align:center;padding:0.8rem 0 1.8rem;">
            <div style="font-family:'Outfit',sans-serif;font-weight:900;font-size:2.1rem;
                background:linear-gradient(90deg,#FF9933,#ffffff,#138808);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
                🎯 Find Your Perfect Indian Film
            </div>
            <div style="color:#64748b;font-size:0.92rem;margin-top:5px;">
                Answer 8 quick questions — we'll do the rest
            </div>
        </div>
        """, unsafe_allow_html=True)

        progress_bar(r_step, TOTAL_REC)
        q = REC_QUESTIONS[r_step]
        q_header(q)

        # ── Multi-select grid ─────────────────────
        if q["type"] in ("multi_grid", "single_grid"):
            is_multi  = q["type"] == "multi_grid"
            max_sel   = q.get("max_select", 99)
            current   = r_ans.get(q["id"], []) if is_multi else r_ans.get(q["id"], None)
            ncols     = q.get("cols", 3)
            gcols     = st.columns(ncols)

            for gi, opt in enumerate(q["options"]):
                is_sel = (opt in current) if is_multi else (opt == current)
                bdr    = "#e50914"             if is_sel else "rgba(255,255,255,0.07)"
                bg     = "rgba(229,9,20,0.18)" if is_sel else "rgba(20,21,36,0.72)"
                fw     = "800"   if is_sel else "500"
                fc     = "#f8fafc" if is_sel else "#94a3b8"
                chk    = "✓ "    if is_sel else ""

                with gcols[gi % ncols]:
                    st.markdown(f"""
                    <div style="background:{bg};border:2px solid {bdr};border-radius:13px;
                                padding:13px 11px;margin-bottom:10px;text-align:center;
                                font-size:0.9rem;font-weight:{fw};color:{fc};cursor:pointer;">
                        {chk}{opt}
                    </div>
                    """, unsafe_allow_html=True)
                    lbl = "✓ Selected" if is_sel else "Select"
                    if st.button(lbl, key=f"rq_{r_step}_{gi}"):
                        if is_multi:
                            lst = list(r_ans.get(q["id"], []))
                            if opt in lst:
                                lst.remove(opt)
                            elif len(lst) < max_sel:
                                lst.append(opt)
                            st.session_state.rec_answers[q["id"]] = lst
                            st.rerun()
                        else:
                            st.session_state.rec_answers[q["id"]] = opt
                            st.session_state.rec_step += 1
                            st.rerun()

            if is_multi:
                cnt = len(r_ans.get(q["id"], []))
                st.markdown(f'<div style="color:#64748b;font-size:0.8rem;margin-top:2px;">{cnt} selected</div>',
                            unsafe_allow_html=True)
                nc, _ = st.columns([1, 5])
                with nc:
                    if st.button("Next ➡️", key=f"multi_next_{r_step}", disabled=(cnt == 0)):
                        st.session_state.rec_step += 1
                        st.rerun()

        # ── Dropdown ──────────────────────────────
        elif q["type"] == "dropdown":
            sel = st.selectbox("", q["options"], index=0, key=f"dd_{r_step}")
            dc1, dc2 = st.columns([1, 1])
            with dc1:
                if st.button("Confirm ✓", key=f"dd_ok_{r_step}"):
                    st.session_state.rec_answers[q["id"]] = sel
                    st.session_state.rec_step += 1
                    st.rerun()
            with dc2:
                if st.button("Skip ⏭", key=f"dd_skip_{r_step}"):
                    st.session_state.rec_answers[q["id"]] = q["options"][0]
                    st.session_state.rec_step += 1
                    st.rerun()

        # ── Rating slider ─────────────────────────
        elif q["type"] == "rating_slider":
            val = st.slider("Min Rating", q["min"], q["max"], q["default"],
                            key=f"rs_{r_step}")
            qlabels = {5:"Any quality",6:"Decent+",7:"Good+",8:"Great+",9:"Masterpiece only"}
            stars   = "⭐" * val + "☆" * (10 - val)
            st.markdown(f"""
            <div style="text-align:center;padding:14px;background:rgba(251,191,36,0.08);
                        border:1px solid rgba(251,191,36,0.2);border-radius:12px;margin:12px 0 18px;">
                <div style="font-size:1.3rem;letter-spacing:2px;margin-bottom:4px;">{stars[:10]}</div>
                <div style="font-size:1.05rem;font-weight:700;color:#fbbf24;">
                    {val}/10 — {qlabels.get(val, "Good")}
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🎬 Find My Movies!", key=f"rs_next_{r_step}"):
                st.session_state.rec_answers[q["id"]] = val
                st.session_state.rec_step += 1
                st.rerun()

        # ── Navigation row ────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        nb1, nb2, nb3 = st.columns([1, 1, 5])
        with nb1:
            if r_step > 0:
                if st.button("← Back", key="rec_back"):
                    st.session_state.rec_step -= 1
                    st.rerun()
        with nb2:
            if q["type"] != "rating_slider":
                if st.button("Skip ⏭", key="rec_skip"):
                    st.session_state.rec_step += 1
                    st.rerun()
        with nb3:
            if st.button("🗑 Start Over", key="rec_reset"):
                st.session_state.rec_step    = 0
                st.session_state.rec_answers = {}
                st.session_state.rec_results = None
                st.rerun()

    # ════════════════════════════════════════
    # COMPUTE + SHOW RESULTS
    # ════════════════════════════════════════
    else:
        # ── Compute once ─────────────────────────
        if st.session_state.rec_results is None:
            ans          = st.session_state.rec_answers
            sel_genres   = ans.get("genre",   [])
            sel_themes   = ans.get("theme",   [])
            sel_industry = ans.get("industry","🌐 All Industries")
            sel_era      = ans.get("era",     "🌐 Any Era")
            sel_runtime  = ans.get("runtime", "🌐 Any Length")
            sel_actor    = ans.get("actor",   "Any actor 🌐")
            sel_director = ans.get("director","Any director 🌐")
            min_rating   = float(ans.get("min_rating", 7))

            era_rng = ERA_RANGE.get(sel_era,     (1900, 2100))
            rt_rng  = RUNTIME_RANGE.get(sel_runtime, (0, 9999))

            cdf = df.copy()
            cdf = cdf[cdf['vote_average'] >= min_rating]
            cdf = cdf[(cdf['release_year'] >= era_rng[0]) & (cdf['release_year'] <= era_rng[1])]
            cdf = cdf[(cdf['runtime'] >= rt_rng[0]) & (cdf['runtime'] <= rt_rng[1])]
            if sel_industry != "🌐 All Industries":
                cdf = cdf[cdf['industry'] == sel_industry]
            if sel_actor != "Any actor 🌐":
                cdf = cdf[cdf['cast'].str.contains(sel_actor.strip(), case=False, na=False)]
            if sel_director != "Any director 🌐":
                cdf = cdf[cdf['director'].str.contains(sel_director.strip(), case=False, na=False)]

            if len(cdf) < 3:           # safety fallback
                cdf = df[df['vote_average'] >= max(6.0, min_rating - 1.5)].copy()

            def rec_score(row):
                s   = 0
                gl  = row['genres'].lower()
                kl  = row['keywords'].lower()
                ol  = row['overview'].lower()
                com = gl + " " + kl + " " + ol
                for g in sel_genres:
                    for part in GENRE_KW_MAP.get(g, "").split("|"):
                        if part.lower() in gl: s += 20
                for t in sel_themes:
                    for kw in THEME_KW_MAP.get(t, []):
                        if kw in com: s += 10
                s += row['vote_average'] * 4
                s += math.log1p(row['vote_count']) * 0.5
                return s

            cdf = cdf.copy()
            cdf['rec_score'] = cdf.apply(rec_score, axis=1)
            cdf = cdf.sort_values('rec_score', ascending=False)
            max_s = cdf['rec_score'].max()
            min_s = cdf['rec_score'].min()
            cdf['match_pct'] = cdf['rec_score'].apply(
                lambda x: int(65 + (x - min_s) / max(1, max_s - min_s) * 34)
            )
            st.session_state.rec_results = cdf.head(top_n).to_dict(orient='records')

        # ── Render profile banner ─────────────────
        ans = st.session_state.rec_answers
        genre_tags = " ".join(
            f'<span class="genre-badge">{g}</span>' for g in ans.get("genre", [])
        )
        theme_tags = " ".join(
            f'<span class="genre-badge" style="background:rgba(19,136,8,0.15);color:#34d399;border-color:#34d399;">{t}</span>'
            for t in ans.get("theme", [])
        )
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba(255,153,51,0.08),rgba(255,255,255,0.02),rgba(19,136,8,0.06));
                    border:1px solid rgba(255,153,51,0.2);border-radius:20px;
                    padding:20px 24px;margin-bottom:1.8rem;">
            <div style="font-family:'Outfit',sans-serif;font-weight:800;font-size:1.2rem;
                        color:#f8fafc;margin-bottom:12px;">🎯 Your Recommendation Profile</div>
            <div style="margin-bottom:8px;">{genre_tags or '<span style="color:#475569;">Any genre</span>'}</div>
            <div style="margin-bottom:10px;">{theme_tags or '<span style="color:#475569;">Any theme</span>'}</div>
            <div style="display:flex;flex-wrap:wrap;gap:20px;font-size:0.8rem;color:#64748b;">
                <span>🎦 {ans.get('industry','Any')}</span>
                <span>📅 {ans.get('era','Any era')}</span>
                <span>⏱ {ans.get('runtime','Any length')}</span>
                <span>⭐ Min {ans.get('min_rating',7)}/10</span>
                <span>🎬 {ans.get('actor','Any actor')}</span>
                <span>🎥 {ans.get('director','Any director')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        results = st.session_state.rec_results
        st.markdown(
            f'<div class="section-header"><span class="icon">✨</span> {len(results)} Movies Picked Just For You</div>',
            unsafe_allow_html=True
        )

        if not results:
            st.warning("No movies matched all your filters. Try **Start Over** with broader options.")
        else:
            rcols = st.columns(3)
            for ri, m in enumerate(results):
                with rcols[ri % 3]:
                    mpct    = m.get('match_pct', 75)
                    iclr    = IND_CLR.get(m.get('industry',''), '#94a3b8')
                    b_cls   = "match-badge high-match" if mpct >= 85 else "match-badge"
                    st.markdown(f"""
                    <div class="movie-card">
                        <img src="{m['poster_path']}" data-title="{m['title']}" data-year="{m.get('release_year', '')}" class="poster-img tmdb-poster" alt="{m['title']}">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                            <span class="{b_cls}">🎯 {mpct}% Match</span>
                            <span class="year-badge">{m['release_year']}</span>
                        </div>
                        <div class="movie-title">{m['title']}</div>
                        <div style="margin:4px 0;">
                            <span style="font-size:0.7rem;font-weight:700;color:{iclr};
                                background:rgba(255,255,255,0.05);padding:2px 8px;border-radius:10px;
                                border:1px solid {iclr}44;">● {m.get('industry','')}</span>
                            <span style="font-size:0.7rem;color:#64748b;margin-left:4px;">({m.get('language','')})</span>
                        </div>
                        <div class="movie-meta">🎬 {m['director']}</div>
                        {render_star_rating(m['vote_average'])}
                        {render_genre_badges(m['genres'])}
                        {render_match_bar(mpct)}
                    </div>
                    """, unsafe_allow_html=True)

                    with st.expander("📖 Details & Actions"):
                        st.markdown(f"**Overview:** {m['overview']}")
                        st.markdown(f"**Cast:** {m['cast']}")
                        st.markdown(f"**Runtime:** {m['runtime']} min  |  **Votes:** {m['vote_count']:,}")
                        da1, da2 = st.columns(2)
                        with da1:
                            tq = m['title'].replace(' ', '+') + "+official+trailer"
                            st.markdown(f"[▶️ Trailer](https://www.youtube.com/results?search_query={tq})")
                        with da2:
                            if st.button("📌 Save", key=f"wl_rec_{m['id']}"):
                                if m['title'] not in [x['title'] for x in st.session_state.watchlist]:
                                    st.session_state.watchlist.append(m)
                                    st.toast(f"✅ Added '{m['title']}'!")
                                else:
                                    st.toast("ℹ️ Already in Watchlist!")

        # ── Action buttons ────────────────────────
        st.markdown("---")
        ab1, ab2, ab3, _ = st.columns([1, 1, 1, 3])
        with ab1:
            if st.button("🔄 Start Over", key="rec_restart"):
                st.session_state.rec_step    = 0
                st.session_state.rec_answers = {}
                st.session_state.rec_results = None
                st.rerun()
        with ab2:
            if st.button("🎲 Reshuffle", key="rec_reshuffle"):
                st.session_state.rec_results = None
                st.rerun()
        with ab3:
            if st.button("✏️ Edit Answers", key="rec_edit"):
                st.session_state.rec_step    = 0
                st.session_state.rec_results = None
                st.rerun()


# ══════════════════════════════════════════════════════════════════
# TAB 2 – MOOD FINDER
# ══════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header"><span class="icon">🎭</span> Mood-Based Movie Finder</div>',
                unsafe_allow_html=True)
    st.markdown('<p style="color:#64748b;margin-bottom:1.5rem;">Answer a few quick questions and we\'ll find the perfect Indian film for your mood right now.</p>',
                unsafe_allow_html=True)

    MOOD_MAP = {
        "😄 Happy & Upbeat":       {"genres":["Comedy","Romance","Family"],       "keywords":["friendship","love","joy","comedy","fun","celebration"], "avoid":["Horror","Crime"]},
        "😢 Emotional & Sad":      {"genres":["Drama","Romance","Family"],         "keywords":["emotion","sacrifice","loss","heartbreak","tear","mother","father","love"], "avoid":["Comedy","Horror"]},
        "😤 Pumped & Hyped":       {"genres":["Action","Thriller","Adventure"],    "keywords":["action","fight","revenge","power","battle","war","chase"], "avoid":["Romance"]},
        "😍 Romantic & Dreamy":    {"genres":["Romance","Drama","Music"],          "keywords":["love","romance","relationship","nostalgia","dream","heart"], "avoid":["Horror","Crime"]},
        "🤔 Thoughtful & Deep":    {"genres":["Drama","Biography","Historical","Legal Drama"], "keywords":["society","justice","truth","human","struggle","poverty","caste"], "avoid":[]},
        "😱 Thrilled & Tense":     {"genres":["Thriller","Crime","Mystery","Horror"], "keywords":["suspense","twist","murder","police","dark","crime","investigation"], "avoid":["Comedy","Romance"]},
        "😂 Laugh Out Loud":       {"genres":["Comedy","Drama"],                  "keywords":["comedy","funny","laugh","jugaad","college","family","satire"], "avoid":["Horror","Thriller"]},
        "🌟 Inspired & Motivated": {"genres":["Biography","Drama","Sport"],        "keywords":["success","dream","fight","inspiration","underdog","win","ambition"], "avoid":[]},
        "😌 Calm & Nostalgic":     {"genres":["Drama","Romance","Music"],          "keywords":["nostalgia","memory","childhood","village","family","classic","tradition"], "avoid":["Horror","Thriller"]},
        "🤩 Epic & Adventurous":   {"genres":["Action","Adventure","Sci-Fi","Mythology"], "keywords":["epic","war","battle","kingdom","empire","adventure","hero","quest"], "avoid":[]},
    }
    COMPANION_MAP = {
        "👤 Solo":         {"genres":["Thriller","Crime","Mystery","Drama","Biography"], "boost":["dark","introspective","mature","complex"]},
        "💑 Partner":      {"genres":["Romance","Drama","Comedy"],                       "boost":["romance","love","couple","heart"]},
        "👨‍👩‍👧‍👦 Family":      {"genres":["Family","Comedy","Drama","Sport","Biography"],   "boost":["family","children","wholesome","village"]},
        "👯 Friends":      {"genres":["Comedy","Action","Adventure","Thriller"],          "boost":["fun","group","adventure","college","friendship"]},
    }
    TIME_MAP2 = {
        "⚡ Under 2 hours":    (0,  119),
        "🎬 2 – 3 hours":      (120,179),
        "🍿 3+ hours (Epic!)": (180,999),
    }
    ERA_MAP2 = {
        "🕰 Classic (pre-2000)":  (1900,1999),
        "🎞 2000s – 2015":        (2000,2015),
        "🆕 Recent (2016+)":      (2016,2100),
        "🌐 Any Era":             (1900,2100),
    }

    MOOD_QUESTIONS = [
        {"id":"mood",       "type":"emoji_grid",   "cols":2,
         "q":"🎭 How are you feeling right now?",    "sub":"Pick the mood that best describes you",
         "options":list(MOOD_MAP.keys())},
        {"id":"companion",  "type":"button_grid",   "cols":2,
         "q":"👥 Who are you watching with?",         "sub":"Your company matters!",
         "options":list(COMPANION_MAP.keys())},
        {"id":"time",       "type":"button_grid",   "cols":3,
         "q":"⏱ How much time do you have?",         "sub":"We'll match to your schedule",
         "options":list(TIME_MAP2.keys())},
        {"id":"era",        "type":"button_grid",   "cols":2,
         "q":"📅 Which era of cinema?",               "sub":"Classic, modern or latest?",
         "options":list(ERA_MAP2.keys())},
        {"id":"language",   "type":"button_grid",   "cols":3,
         "q":"🗣️ Language preference?",              "sub":"Pick your preferred film language",
         "options":["🌐 Any Language"] + all_languages},
        {"id":"industry",   "type":"button_grid",   "cols":3,
         "q":"🎦 Favourite film industry?",           "sub":"Or explore them all!",
         "options":["🌐 All Industries"] + all_industries},
        {"id":"intensity",  "type":"slider",
         "q":"🔥 How intense should the film be?",   "sub":"Light-hearted or heavy-hitting?",
         "min":1,"max":5,"labels":["😌 Very Light","🙂 Light","😐 Medium","😤 Intense","🔥 Very Intense"]},
        {"id":"min_rating2","type":"slider",
         "q":"⭐ Minimum rating?",                   "sub":"Only certified hits?",
         "min":5,"max":9,"labels":["5.0","6.0","7.0","8.0","9.0"]},
    ]
    TOTAL_MOOD = len(MOOD_QUESTIONS)
    m_step = st.session_state.mood_step
    m_ans  = st.session_state.mood_answers

    if m_step < TOTAL_MOOD and st.session_state.mood_results is None:
        # Progress
        mpct2 = int(m_step / TOTAL_MOOD * 100)
        st.markdown(f"""
        <div style="margin-bottom:1.6rem;">
            <div style="display:flex;justify-content:space-between;font-size:0.77rem;color:#475569;margin-bottom:7px;">
                <span>Question {m_step+1} of {TOTAL_MOOD}</span><span>{mpct2}% complete</span>
            </div>
            <div style="background:rgba(255,255,255,0.06);border-radius:50px;height:6px;overflow:hidden;">
                <div style="height:100%;width:{mpct2}%;
                    background:linear-gradient(90deg,#FF9933,#e50914,#138808);
                    border-radius:50px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        mq = MOOD_QUESTIONS[m_step]
        st.markdown(f"""
        <div style="background:rgba(20,21,36,0.85);border:1px solid rgba(255,255,255,0.08);
                    border-radius:18px;padding:24px 28px;margin-bottom:1.4rem;">
            <div style="font-family:'Outfit',sans-serif;font-weight:800;font-size:1.45rem;
                        color:#f8fafc;margin-bottom:5px;">{mq['q']}</div>
            <div style="font-size:0.87rem;color:#64748b;">{mq['sub']}</div>
        </div>
        """, unsafe_allow_html=True)

        if mq["type"] in ("emoji_grid","button_grid"):
            ncols2 = mq.get("cols", 2)
            mc_cols = st.columns(ncols2)
            for mi, opt in enumerate(mq["options"]):
                is_sel2 = m_ans.get(mq["id"]) == opt
                bdr2 = "#e50914" if is_sel2 else "rgba(255,255,255,0.07)"
                bg2  = "rgba(229,9,20,0.15)" if is_sel2 else "rgba(20,21,36,0.7)"
                with mc_cols[mi % ncols2]:
                    st.markdown(f"""
                    <div style="background:{bg2};border:2px solid {bdr2};border-radius:13px;
                                padding:13px 12px;margin-bottom:10px;text-align:center;
                                font-size:{'1.05' if mq['type']=='emoji_grid' else '0.9'}rem;
                                font-weight:{'700' if is_sel2 else '500'};
                                color:{'#f8fafc' if is_sel2 else '#94a3b8'};">
                        {'✓ ' if is_sel2 else ''}{opt}
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("Select" if not is_sel2 else "✓ Picked",
                                 key=f"mq_{m_step}_{mi}"):
                        st.session_state.mood_answers[mq["id"]] = opt
                        st.session_state.mood_step += 1
                        st.rerun()

        elif mq["type"] == "slider":
            sv = st.slider("", mq["min"], mq["max"], (mq["min"]+mq["max"])//2,
                           key=f"ms_{m_step}")
            sl = mq["labels"][min(sv - mq["min"], len(mq["labels"])-1)]
            st.markdown(f'<div style="text-align:center;color:#00d2ff;font-size:1.05rem;font-weight:700;margin:8px 0 16px;">{sl}</div>',
                        unsafe_allow_html=True)
            if st.button("➡️ Next", key=f"ms_next_{m_step}"):
                st.session_state.mood_answers[mq["id"]] = sv
                st.session_state.mood_step += 1
                st.rerun()

        mn1, _, mn3 = st.columns([1,4,1])
        with mn1:
            if m_step > 0:
                if st.button("← Back", key="mood_back"):
                    st.session_state.mood_step -= 1
                    st.rerun()
        with mn3:
            if st.button("Skip ⏭", key="mood_skip"):
                st.session_state.mood_step += 1
                st.rerun()

    else:
        # ── Compute mood results ───────────────────
        if st.session_state.mood_results is None:
            mood_key  = m_ans.get("mood",       list(MOOD_MAP.keys())[0])
            comp_key  = m_ans.get("companion",   "👤 Solo")
            time_key  = m_ans.get("time",        "🎬 2 – 3 hours")
            era_key2  = m_ans.get("era",         "🌐 Any Era")
            lang_key  = m_ans.get("language",    "🌐 Any Language")
            ind_key2  = m_ans.get("industry",    "🌐 All Industries")
            intensity = int(m_ans.get("intensity", 3))
            min_r2    = float(m_ans.get("min_rating2", 7))

            mcfg  = MOOD_MAP.get(mood_key, list(MOOD_MAP.values())[0])
            ccfg  = COMPANION_MAP.get(comp_key, list(COMPANION_MAP.values())[0])
            trng  = TIME_MAP2.get(time_key, (0,999))
            erng  = ERA_MAP2.get(era_key2, (1900,2100))

            cdf2  = df.copy()
            cdf2  = cdf2[cdf2['vote_average'] >= min_r2]
            cdf2  = cdf2[(cdf2['runtime'] >= trng[0]) & (cdf2['runtime'] <= trng[1])]
            cdf2  = cdf2[(cdf2['release_year'] >= erng[0]) & (cdf2['release_year'] <= erng[1])]
            if lang_key != "🌐 Any Language":
                cdf2 = cdf2[cdf2['language'] == lang_key]
            if ind_key2 != "🌐 All Industries":
                cdf2 = cdf2[cdf2['industry'] == ind_key2]
            for ag in mcfg.get("avoid",[]):
                cdf2 = cdf2[~cdf2['genres'].str.contains(ag, case=False, na=False)]
            if cdf2.empty:
                cdf2 = df[df['vote_average'] >= max(6.0, min_r2 - 1)].copy()

            def mood_score(row):
                s  = 0
                gl = row['genres'].lower()
                kl = row['keywords'].lower()
                com= gl + " " + kl
                for g in mcfg["genres"]:
                    if g.lower() in gl: s += 15
                for kw in mcfg["keywords"]:
                    if kw.lower() in com: s += 8
                for g in ccfg["genres"]:
                    if g.lower() in gl: s += 10
                for kw in ccfg["boost"]:
                    if kw.lower() in com: s += 5
                s += row['vote_average'] * 3
                aw = ["action","fight","war","battle","chase","violence","dark","revenge"]
                ac = sum(1 for w in aw if w in com)
                if intensity >= 4: s += ac * 4
                elif intensity <= 2: s -= ac * 3
                return s

            cdf2 = cdf2.copy()
            cdf2['m_score'] = cdf2.apply(mood_score, axis=1)
            cdf2 = cdf2.sort_values('m_score', ascending=False)
            st.session_state.mood_results = cdf2.head(6).to_dict(orient='records')

        # ── Profile summary ────────────────────────
        st.markdown("""
        <div style="background:linear-gradient(135deg,rgba(255,153,51,0.1),rgba(19,136,8,0.08));
                    border:1px solid rgba(255,153,51,0.25);border-radius:18px;
                    padding:20px 24px;margin-bottom:1.5rem;">
            <div style="font-family:'Outfit',sans-serif;font-weight:800;font-size:1.2rem;
                        color:#f8fafc;margin-bottom:12px;">🎉 Your CineIndia Profile</div>
        """, unsafe_allow_html=True)
        summary = {
            "🎭 Mood": m_ans.get("mood","—"), "👥 Watching with": m_ans.get("companion","—"),
            "⏱ Time": m_ans.get("time","—"), "📅 Era": m_ans.get("era","—"),
            "🗣️ Language": m_ans.get("language","—"), "🎦 Industry": m_ans.get("industry","—"),
            "🔥 Intensity": f"{m_ans.get('intensity',3)}/5",
            "⭐ Min Rating": f"{m_ans.get('min_rating2',7)}+",
        }
        scols = st.columns(4)
        for si,(k,v) in enumerate(summary.items()):
            with scols[si % 4]:
                st.markdown(
                    f'<div style="background:rgba(255,255,255,0.04);border-radius:10px;padding:10px 12px;margin-bottom:8px;">'
                    f'<div style="font-size:0.68rem;color:#475569;margin-bottom:2px;">{k}</div>'
                    f'<div style="font-size:0.8rem;font-weight:600;color:#e2e8f0;">{v}</div></div>',
                    unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        mood_label = m_ans.get("mood","your mood")
        st.markdown(f'<div class="section-header"><span class="icon">✨</span> Perfect Picks for <em>{mood_label}</em></div>',
                    unsafe_allow_html=True)

        mresults = st.session_state.mood_results
        if not mresults:
            st.warning("No movies matched. Try Retake Quiz with looser filters.")
        else:
            mr_cols = st.columns(3)
            for ri2, m2 in enumerate(mresults):
                with mr_cols[ri2 % 3]:
                    mpct3  = min(99, max(62, int(55 + m2.get('m_score',50)*0.35)))
                    iclr2  = IND_CLR.get(m2.get('industry',''), '#94a3b8')
                    st.markdown(f"""
                    <div class="movie-card">
                        <img src="{m2['poster_path']}" data-title="{m2['title']}" data-year="{m2.get('release_year', '')}" class="poster-img tmdb-poster">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                            <span class="match-badge">🎭 {mpct3}% Mood Match</span>
                            <span class="year-badge">{m2['release_year']}</span>
                        </div>
                        <div class="movie-title">{m2['title']}</div>
                        <div style="margin:4px 0;">
                            <span style="font-size:0.7rem;font-weight:700;color:{iclr2};
                                background:rgba(255,255,255,0.06);padding:2px 8px;border-radius:10px;
                                border:1px solid {iclr2}44;">● {m2.get('industry','')}</span>
                            <span style="font-size:0.7rem;color:#64748b;margin-left:4px;">({m2.get('language','')})</span>
                        </div>
                        <div class="movie-meta">🎬 {m2['director']}</div>
                        {render_star_rating(m2['vote_average'])}
                        {render_genre_badges(m2['genres'])}
                        {render_match_bar(mpct3)}
                    </div>
                    """, unsafe_allow_html=True)
                    with st.expander("📖 Synopsis & Actions"):
                        st.markdown(f"{m2['overview']}")
                        st.markdown(f"**Cast:** {m2['cast']}  |  **Runtime:** {m2['runtime']} min")
                        mc1, mc2 = st.columns(2)
                        with mc1:
                            tq = m2['title'].replace(' ','+') + "+official+trailer"
                            st.markdown(f"[▶️ Trailer](https://www.youtube.com/results?search_query={tq})")
                        with mc2:
                            if st.button("📌 Save", key=f"mood_wl_{m2['id']}"):
                                if m2['title'] not in [x['title'] for x in st.session_state.watchlist]:
                                    st.session_state.watchlist.append(m2)
                                    st.toast(f"✅ Added '{m2['title']}'!")

        st.markdown("---")
        rb1, rb2, _ = st.columns([1, 1, 4])
        with rb1:
            if st.button("🔄 Retake Quiz", key="mood_restart"):
                st.session_state.mood_step    = 0
                st.session_state.mood_answers = {}
                st.session_state.mood_results = None
                st.rerun()
        with rb2:
            if st.button("🎲 Shuffle", key="mood_shuffle"):
                st.session_state.mood_results = None
                st.rerun()


# ══════════════════════════════════════════════════════════════════
# TAB 3 – BROWSE CATALOG
# ══════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header"><span class="icon">🔍</span> Browse Indian Cinema</div>',
                unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns([3,2,2,2])
    with f1:
        search_q = st.text_input("🔎 Search title, cast, director:", placeholder="e.g. Aamir Khan, love, cricket…")
    with f2:
        genre_sel = st.selectbox("🎭 Genre", ["All"] + all_genres)
    with f3:
        year_range = st.slider("📅 Year", int(min(all_years)), int(max(all_years)),
                               (int(min(all_years)), int(max(all_years))))
    with f4:
        min_r = st.slider("⭐ Min Rating", 0.0, 10.0, 7.0, 0.1)

    ff1, ff2, _ = st.columns([2, 2, 5])
    with ff1:
        industry_sel = st.selectbox("🎦 Industry", ["All"] + all_industries)
    with ff2:
        language_sel = st.selectbox("🗣️ Language", ["All"] + all_languages)

    sc1, sc2 = st.columns([2,1])
    with sc1:
        sort_by = st.selectbox("Sort by:", ["Rating (High→Low)","Rating (Low→High)",
                                            "Year (Newest)","Year (Oldest)","Title A→Z","Runtime"])
    with sc2:
        view_mode = st.radio("View:", ["🃏 Cards","📋 Table"], horizontal=True)

    fdf = df.copy()
    if search_q:
        mask = (fdf['title'].str.contains(search_q, case=False, na=False) |
                fdf['cast'].str.contains(search_q, case=False, na=False) |
                fdf['director'].str.contains(search_q, case=False, na=False) |
                fdf['keywords'].str.contains(search_q, case=False, na=False) |
                fdf['overview'].str.contains(search_q, case=False, na=False))
        fdf = fdf[mask]
    if genre_sel    != "All": fdf = fdf[fdf['genres'].str.contains(genre_sel, case=False, na=False)]
    if industry_sel != "All": fdf = fdf[fdf['industry'] == industry_sel]
    if language_sel != "All": fdf = fdf[fdf['language'] == language_sel]
    fdf = fdf[(fdf['release_year'] >= year_range[0]) & (fdf['release_year'] <= year_range[1])]
    fdf = fdf[fdf['vote_average'] >= min_r]

    sort_map = {"Rating (High→Low)":('vote_average',False),"Rating (Low→High)":('vote_average',True),
                "Year (Newest)":('release_year',False),"Year (Oldest)":('release_year',True),
                "Title A→Z":('title',True),"Runtime":('runtime',False)}
    col_s, asc_s = sort_map[sort_by]
    fdf = fdf.sort_values(col_s, ascending=asc_s)

    st.markdown(f"<div style='color:#64748b;font-size:0.88rem;margin:0.5rem 0;'>"
                f"Showing <strong style='color:#00d2ff'>{len(fdf)}</strong> of <strong>{len(df)}</strong> films</div>",
                unsafe_allow_html=True)

    if fdf.empty:
        st.info("No movies match your filters. Try broadening your search.")
    elif "Table" in view_mode:
        dcols = ['title','release_year','industry','language','genres','director','vote_average','runtime']
        ddf   = fdf[dcols].copy()
        ddf.columns = ['Title','Year','Industry','Language','Genres','Director','Rating','Runtime (min)']
        st.dataframe(ddf.reset_index(drop=True), use_container_width=True, height=520,
                     column_config={
                         "Rating":       st.column_config.ProgressColumn("Rating", min_value=0, max_value=10, format="%.1f"),
                         "Runtime (min)":st.column_config.NumberColumn("Runtime (min)", format="%d min"),
                     })
    else:
        grid = st.columns(4)
        for i, (_, row) in enumerate(fdf.iterrows()):
            with grid[i % 4]:
                iclr3 = IND_CLR.get(row['industry'], '#94a3b8')
                st.markdown(f"""
                <div class="movie-card">
                    <img src="{row['poster_path']}" data-title="{row['title']}" data-year="{row.get('release_year', '')}" class="poster-img tmdb-poster">
                    <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                        <span class="rating-badge">⭐ {row['vote_average']}</span>
                        <span class="year-badge">{row['release_year']}</span>
                    </div>
                    <div class="movie-title" style="font-size:0.9rem;">{row['title']}</div>
                    <div class="movie-meta">{row['director']}</div>
                    <div style="margin:4px 0;">
                        <span style="font-size:0.68rem;font-weight:700;color:{iclr3};
                            background:rgba(255,255,255,0.05);padding:2px 7px;border-radius:10px;
                            border:1px solid {iclr3}44;">● {row['industry']}</span>
                        <span style="font-size:0.68rem;color:#64748b;margin-left:3px;">({row['language']})</span>
                    </div>
                    {render_genre_badges(row['genres'])}
                </div>
                """, unsafe_allow_html=True)
                if st.button("📌", key=f"bwl_{row['id']}", help="Add to Watchlist"):
                    if row['title'] not in [m['title'] for m in st.session_state.watchlist]:
                        st.session_state.watchlist.append(row.to_dict())
                        st.toast(f"Added {row['title']}!")


# ══════════════════════════════════════════════════════════════════
# TAB 4 – ANALYTICS
# ══════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header"><span class="icon">📊</span> Analytics Dashboard</div>',
                unsafe_allow_html=True)

    r1, r2 = st.columns(2)
    with r1:
        gl = []
        for gs in df['genres']: gl.extend([g.strip() for g in gs.split(',')])
        gc = pd.Series(gl).value_counts().reset_index()
        gc.columns = ['Genre','Count']
        fig1 = px.bar(gc, x='Count', y='Genre', orientation='h', color='Count',
                      color_continuous_scale='Reds', title="🎭 Genre Distribution")
        fig1.update_layout(template="plotly_dark", height=380,
                           paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                           title_font=dict(size=14,color='#f1f5f9'),
                           margin=dict(t=50,l=0,r=0,b=0), coloraxis_showscale=False)
        st.plotly_chart(fig1, use_container_width=True)

    with r2:
        ind_df = df.groupby('industry').agg(count=('title','count'),avg=('vote_average','mean')).reset_index()
        fig2 = px.bar(ind_df, x='industry', y='count', color='avg',
                      color_continuous_scale='RdYlGn',
                      title="🎦 Films per Industry (colored by avg rating)",
                      labels={'industry':'Industry','count':'# Films','avg':'Avg Rating'})
        fig2.update_layout(template="plotly_dark", height=380,
                           paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                           title_font=dict(size=14,color='#f1f5f9'),
                           margin=dict(t=50,l=0,r=0,b=0))
        st.plotly_chart(fig2, use_container_width=True)

    r3, r4 = st.columns(2)
    with r3:
        fig3 = px.scatter(df, x='vote_count', y='vote_average', size='runtime',
                          color='industry', hover_name='title',
                          color_discrete_map=IND_CLR,
                          title="🔥 Popularity vs Quality",
                          labels={'vote_count':'Vote Count','vote_average':'Rating','industry':'Industry'})
        fig3.update_layout(template="plotly_dark", height=380,
                           paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                           title_font=dict(size=14,color='#f1f5f9'),
                           margin=dict(t=50,l=0,r=0,b=0))
        st.plotly_chart(fig3, use_container_width=True)

    with r4:
        dir_c = df['director'].value_counts().head(10).reset_index()
        dir_c.columns = ['Director','Movies']
        fig4 = px.bar(dir_c, x='Movies', y='Director', orientation='h',
                      color='Movies', color_continuous_scale='Blues_r',
                      title="🎬 Top Directors")
        fig4.update_layout(template="plotly_dark", height=380,
                           paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                           title_font=dict(size=14,color='#f1f5f9'),
                           margin=dict(t=50,l=0,r=0,b=0), coloraxis_showscale=False)
        st.plotly_chart(fig4, use_container_width=True)

    r5, r6 = st.columns(2)
    with r5:
        fig5 = px.histogram(df, x='vote_average', nbins=18, color='industry',
                            color_discrete_map=IND_CLR,
                            title="⭐ Rating Distribution by Industry",
                            labels={'vote_average':'Rating'}, barmode='overlay', opacity=0.75)
        fig5.update_layout(template="plotly_dark", height=360,
                           paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                           title_font=dict(size=14,color='#f1f5f9'),
                           margin=dict(t=50,l=0,r=0,b=0))
        st.plotly_chart(fig5, use_container_width=True)

    with r6:
        df2 = df.copy()
        df2['decade'] = (df2['release_year']//10*10).astype(str)+'s'
        dc = df2.groupby('decade').agg(count=('title','count'), avg=('vote_average','mean')).reset_index()
        fig6 = go.Figure()
        fig6.add_trace(go.Bar(x=dc['decade'],y=dc['count'],name='Films',
                              marker_color='#e50914',opacity=0.8))
        fig6.add_trace(go.Scatter(x=dc['decade'],y=dc['avg'],name='Avg Rating',
                                  yaxis='y2',mode='lines+markers',
                                  line=dict(color='#00d2ff',width=2.5),marker=dict(size=8)))
        fig6.update_layout(template="plotly_dark", height=360,
                           paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                           title=dict(text="📅 Films per Decade",font=dict(size=14,color='#f1f5f9')),
                           yaxis=dict(title='# Films'),
                           yaxis2=dict(title='Avg Rating',overlaying='y',side='right',range=[6,10]),
                           margin=dict(t=50,l=0,r=40,b=0),
                           legend=dict(orientation='h',y=1.1))
        st.plotly_chart(fig6, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 🧬 Content Similarity Heatmap (Top 12 Films)")
    n12 = min(12, len(df))
    s12 = df.head(n12)
    sim_sub = engine.get_similarity_matrix_for_movies(list(s12.index))
    short_t = [t if len(t)<=18 else t[:16]+'…' for t in s12['title'].tolist()]
    fig7 = px.imshow(sim_sub, x=short_t, y=short_t, color_continuous_scale='Hot',
                     zmin=0, zmax=1, text_auto=".2f",
                     title="Pairwise Content Similarity")
    fig7.update_layout(template="plotly_dark", height=500,
                       paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                       title_font=dict(size=14,color='#f1f5f9'),
                       margin=dict(t=50,l=60,r=0,b=60), xaxis_tickangle=-35)
    st.plotly_chart(fig7, use_container_width=True)


# ══════════════════════════════════════════════════════════════════
# TAB 5 – COMPARE MOVIES
# ══════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-header"><span class="icon">🆚</span> Compare Two Movies</div>',
                unsafe_allow_html=True)

    cc1, cc_vs, cc2 = st.columns([5,1,5])
    with cc1:
        movie_a = st.selectbox("Movie A:", df['title'].tolist(), index=0, key="cmp_a")
    with cc_vs:
        st.markdown('<div class="compare-vs">VS</div>', unsafe_allow_html=True)
    with cc2:
        movie_b = st.selectbox("Movie B:", df['title'].tolist(), index=1, key="cmp_b")

    rowA = df[df['title']==movie_a].iloc[0]
    rowB = df[df['title']==movie_b].iloc[0]

    pa, pb = st.columns(2)
    for panel, row, clr in [(pa,rowA,'#e50914'),(pb,rowB,'#00d2ff')]:
        with panel:
            iclr4 = IND_CLR.get(row['industry'],'#94a3b8')
            st.markdown('<div class="compare-panel">', unsafe_allow_html=True)
            st.image(row['poster_path'], use_container_width=True)
            st.markdown(f'<div class="movie-title" style="font-size:1.1rem;color:{clr};">'
                        f'{row["title"]} ({row["release_year"]})</div>', unsafe_allow_html=True)
            st.markdown(render_star_rating(row["vote_average"]), unsafe_allow_html=True)
            st.markdown(render_genre_badges(row["genres"]), unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:0.72rem;font-weight:700;color:{iclr4};">● {row["industry"]} ({row["language"]})</div>',
                        unsafe_allow_html=True)
            st.markdown(f'<div class="movie-meta">🎬 {row["director"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="movie-meta">⏱ {row["runtime"]} min &nbsp;|&nbsp; 👥 {row["vote_count"]:,} votes</div>',
                        unsafe_allow_html=True)
            st.markdown(f'<p class="overview-text">{row["overview"]}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 📡 Head-to-Head Radar")

    def norm(v, lo, hi): return round((v-lo)/max(1,hi-lo)*10, 2)
    cats = ['Rating','Cast Size','Runtime','Year','Vote Count']

    def radar_vals(row):
        return [
            row['vote_average'],
            norm(len(row['cast']), 20, 120),
            norm(row['runtime'], df['runtime'].min(), df['runtime'].max())*10,
            norm(row['release_year'], int(min(all_years)), int(max(all_years)))*10,
            norm(row['vote_count'], df['vote_count'].min(), df['vote_count'].max())*10,
        ]

    vA = radar_vals(rowA)
    vB = radar_vals(rowB)
    fig_r = go.Figure()
    fig_r.add_trace(go.Scatterpolar(r=vA+[vA[0]], theta=cats+[cats[0]],
                    fill='toself', name=rowA['title'],
                    line_color='#e50914', fillcolor='rgba(229,9,20,0.15)'))
    fig_r.add_trace(go.Scatterpolar(r=vB+[vB[0]], theta=cats+[cats[0]],
                    fill='toself', name=rowB['title'],
                    line_color='#00d2ff', fillcolor='rgba(0,210,255,0.15)'))
    fig_r.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0,10], color='#475569'),
                   bgcolor='rgba(0,0,0,0)'),
        showlegend=True, template='plotly_dark', height=420,
        paper_bgcolor='rgba(0,0,0,0)', legend=dict(orientation='h', y=-0.1))
    st.plotly_chart(fig_r, use_container_width=True)

    shared = engine.get_common_keywords(movie_a, movie_b)
    if shared:
        badges = " ".join(f'<span class="genre-badge">{g}</span>' for g in shared)
        st.markdown(f"**🔗 Shared Genres:** {badges}", unsafe_allow_html=True)

    idxA = df[df['title']==movie_a].index[0]
    idxB = df[df['title']==movie_b].index[0]
    sim  = float(engine.cosine_sim[idxA][idxB])
    spct = int(round(sim*100))
    st.markdown("**🧬 Content Similarity:**")
    st.markdown(render_match_bar(max(spct,1)), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# TAB 6 – WATCHLIST
# ══════════════════════════════════════════════════════════════════
with tab6:
    st.markdown('<div class="section-header"><span class="icon">📌</span> My Watchlist</div>',
                unsafe_allow_html=True)

    if not st.session_state.watchlist:
        st.markdown("""
        <div class="empty-state">
            <div class="icon">🎬</div>
            <h3>Your watchlist is empty</h3>
            <p>Hit <strong>📌 Save</strong> on any movie to bookmark it here.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        wl_df = pd.DataFrame(st.session_state.watchlist)
        hc1, hc2 = st.columns([4,1])
        with hc1:
            st.markdown(f"<div style='color:#64748b;font-size:0.9rem;'>📌 <strong style='color:#00d2ff'>{len(wl_df)}</strong> movies saved</div>",
                        unsafe_allow_html=True)
        with hc2:
            if st.button("🗑️ Clear All"):
                st.session_state.watchlist = []
                st.rerun()

        if len(wl_df) > 1:
            ms1, ms2, ms3 = st.columns(3)
            ms1.metric("Avg Rating", f"{wl_df['vote_average'].mean():.1f} ⭐")
            ms2.metric("Avg Runtime", f"{int(wl_df['runtime'].mean())} min")
            ms3.metric("Genres", len({g.strip() for gs in wl_df['genres'] for g in gs.split(',')}))

        st.markdown("---")
        wlc = st.columns(3)
        for i, item in enumerate(st.session_state.watchlist):
            with wlc[i % 3]:
                iclr5 = IND_CLR.get(item.get('industry',''), '#94a3b8')
                st.markdown(f"""
                <div class="movie-card">
                    <img src="{item['poster_path']}" data-title="{item['title']}" data-year="{item.get('release_year', '')}" class="poster-img tmdb-poster">
                    <div class="movie-title">{item['title']} ({item['release_year']})</div>
                    <div style="margin:4px 0;">
                        <span style="font-size:0.7rem;font-weight:700;color:{iclr5};
                            background:rgba(255,255,255,0.05);padding:2px 7px;border-radius:10px;
                            border:1px solid {iclr5}44;">● {item.get('industry','')}</span>
                    </div>
                    {render_star_rating(item['vote_average'])}
                    {render_genre_badges(item['genres'])}
                    <div class="movie-meta">🎬 {item['director']} &nbsp;|&nbsp; ⏱ {item['runtime']} min</div>
                </div>
                """, unsafe_allow_html=True)
                wc1, wc2 = st.columns(2)
                with wc1:
                    tq = item['title'].replace(' ','+') + "+trailer"
                    st.markdown(f"[▶️ Trailer](https://www.youtube.com/results?search_query={tq})")
                with wc2:
                    if st.button("❌ Remove", key=f"rm_{i}"):
                        st.session_state.watchlist.pop(i)
                        st.rerun()


# ══════════════════════════════════════════════════════════════════
# TAB 7 – SURPRISE ME
# ══════════════════════════════════════════════════════════════════
with tab7:
    st.markdown('<div class="section-header"><span class="icon">🎲</span> Surprise Me!</div>',
                unsafe_allow_html=True)

    sp1c, sp2c, sp3c = st.columns(3)
    with sp1c:
        sp_genre = st.selectbox("Pick a genre (or any):", ["🎰 Any"] + all_genres, key="sp_genre")
    with sp2c:
        sp_min_r = st.slider("Min rating:", 6.0, 10.0, 7.5, 0.1, key="sp_rating")
    with sp3c:
        sp_era = st.selectbox("Era:", ["All Time","Classic (pre-2000)","Modern (2000–2015)","Recent (2016+)"],
                              key="sp_era")

    st.markdown("""
    <div class="surprise-card">
        <div style="font-size:3rem;margin-bottom:1rem;">🎰</div>
        <h2>Can't decide what to watch?</h2>
        <p>Let CineIndia pick the perfect Indian movie for you!</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🎲 Spin the Wheel!", key="surprise_roll"):
        sp_df = df[df['vote_average'] >= sp_min_r].copy()
        if sp_genre != "🎰 Any":
            sp_df = sp_df[sp_df['genres'].str.contains(sp_genre, case=False, na=False)]
        if sp_era == "Classic (pre-2000)":   sp_df = sp_df[sp_df['release_year'] < 2000]
        elif sp_era == "Modern (2000–2015)": sp_df = sp_df[(sp_df['release_year']>=2000) & (sp_df['release_year']<=2015)]
        elif sp_era == "Recent (2016+)":     sp_df = sp_df[sp_df['release_year'] >= 2016]
        if sp_df.empty:
            st.error("No movies match those filters. Relax your criteria!")
        else:
            st.session_state.surprise_movie = sp_df.sample(1).iloc[0].to_dict()
            st.balloons()

    if st.session_state.surprise_movie:
        m = st.session_state.surprise_movie
        st.markdown("---")
        st.markdown("### 🎉 Tonight's Pick:")
        sm1, sm2 = st.columns([1,3])
        with sm1:
            st.image(m['poster_path'], use_container_width=True)
        with sm2:
            iclr6 = IND_CLR.get(m.get('industry',''), '#94a3b8')
            st.markdown(f"## **{m['title']}** ({m['release_year']})")
            st.markdown(f'<span style="font-size:0.75rem;font-weight:700;color:{iclr6};'
                        f'background:rgba(255,255,255,0.06);padding:3px 10px;border-radius:10px;'
                        f'border:1px solid {iclr6}44;">● {m.get("industry","")} ({m.get("language","")})</span>',
                        unsafe_allow_html=True)
            st.markdown(render_star_rating(m['vote_average']), unsafe_allow_html=True)
            st.markdown(render_genre_badges(m['genres']), unsafe_allow_html=True)
            st.markdown(f"🎬 **Director:** {m['director']}  |  ⏱ **{m['runtime']} min**")
            st.markdown(f"**Synopsis:** {m['overview']}")
            sa, sb, sc2 = st.columns(3)
            with sa:
                tq = m['title'].replace(' ','+') + "+official+trailer"
                st.markdown(f"[▶️ Trailer](https://www.youtube.com/results?search_query={tq})")
            with sb:
                if st.button("📌 Save to Watchlist", key="sp_save"):
                    if m['title'] not in [x['title'] for x in st.session_state.watchlist]:
                        st.session_state.watchlist.append(m)
                        st.toast("✅ Added to Watchlist!")
            with sc2:
                if st.button("🔄 Roll Again", key="sp_reroll"):
                    st.session_state.surprise_movie = None
                    st.rerun()
