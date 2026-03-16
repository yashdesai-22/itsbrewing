import os
import streamlit as st
from dotenv import load_dotenv
from news_fetcher import fetch_all_news
from summarizer import stream_summary, get_daily_digest

load_dotenv()

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ItsBrewing",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .block-container { padding-top: 1.5rem; }
    .ai-badge {
        display: inline-block;
        background: linear-gradient(90deg, #FF6B35, #e55a2b);
        color: white;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 20px;
        letter-spacing: 0.5px;
    }
    .source-tag {
        background: #f0f2f6;
        color: #444;
        font-size: 0.72rem;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .digest-box {
        border-left: 4px solid #FF6B35;
        padding: 0.8rem 1.2rem;
        background: #fff8f5;
        border-radius: 0 8px 8px 0;
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("# 🍵 Daily News")
    st.caption("AI-powered India news digest")
    st.divider()

    max_articles = st.slider("Articles to load", min_value=10, max_value=50, value=20, step=5)

    st.divider()
    if st.button("🔄 Refresh News", use_container_width=True):
        st.cache_data.clear()
        st.session_state.clear()
        st.rerun()

    st.divider()
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        st.success("🤖 Groq AI: Connected")
    else:
        st.error("⚠️ GROQ_API_KEY not set")
        st.code("# Add to .env file:\nGROQ_API_KEY=gsk_...")

    st.divider()
    st.caption("📡 **Sources**")

    st.caption("BBC · Reuters · Times of India · Al Jazeera · The Hindu · Economic Times")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# ItsBrewing Daily News")
st.markdown("*Global news filtered for India — summarized by AI in real time.*")
st.divider()

# ── Fetch news (cached 15 min) ────────────────────────────────────────────────
@st.cache_data(ttl=900)
def load_news(n: int) -> list:
    return fetch_all_news(n)


with st.spinner("📡 Fetching latest India news..."):
    articles = load_news(max_articles)

if not articles:
    st.error("No articles found. Check your internet connection or try refreshing.")
    st.stop()

# ── Stats row ─────────────────────────────────────────────────────────────────
sources = sorted({a.source for a in articles})
# c1, c2, c3 = st.columns(3)
# c1.metric("📰 Articles Found", len(articles))
# c2.metric("📡 News Sources", len(sources))
# c3.metric("⏱️ Cache Duration", "15 min")
# st.divider()

# ── AI Daily Digest ───────────────────────────────────────────────────────────
if api_key:
    digest_key = "digest_" + "_".join(a.title[:15] for a in articles[:5])
    if digest_key not in st.session_state:
        with st.spinner("🤖 Generating today's digest..."):
            st.session_state[digest_key] = get_daily_digest(articles)

    st.markdown(
        f'<div class="digest-box">{st.session_state[digest_key]}</div>',
        unsafe_allow_html=True,
    )
    st.divider()

# ── Source filter ─────────────────────────────────────────────────────────────
selected = st.multiselect(
    "Filter by source",
    options=sources,
    default=sources,
    label_visibility="collapsed",
)
filtered = [a for a in articles if a.source in selected]
st.caption(f"Showing **{len(filtered)}** articles")
st.divider()

# ── Article cards ─────────────────────────────────────────────────────────────
for i, article in enumerate(filtered):
    with st.container(border=True):

        # Title + meta
        st.markdown(f"### {article.title}")
        pub = article.published[:25] if article.published else "Unknown"
        st.markdown(
            f'<span class="source-tag">{article.source}</span>&nbsp; 🕐 {pub}',
            unsafe_allow_html=True,
        )

        # Description snippet
        if article.description:
            st.markdown(
                f"<small style='color:#666'>{article.description[:280]}{'…' if len(article.description) > 280 else ''}</small>",
                unsafe_allow_html=True,
            )

        # Action row
        col_read, col_ai = st.columns([1, 1])
        with col_read:
            st.link_button("📰 Read full article", article.link, use_container_width=True)

        summary_key = f"summary_{hash(article.title)}"

        with col_ai:
            if not api_key:
                st.button("🤖 AI Summary", key=f"btn_{i}", disabled=True, use_container_width=True,
                          help="Set GROQ_API_KEY in .env to enable")
            elif summary_key not in st.session_state:
                if st.button("🤖 AI Summary", key=f"btn_{i}", use_container_width=True):
                    st.markdown('<span class="ai-badge">AI ANALYSIS</span>', unsafe_allow_html=True)
                    chunks: list[str] = []
                    placeholder = st.empty()
                    for chunk in stream_summary(article):
                        chunks.append(chunk)
                        placeholder.markdown("".join(chunks) + "▌")
                    full = "".join(chunks)
                    placeholder.markdown(full)
                    st.session_state[summary_key] = full
            else:
                st.button("✅ Summary cached", key=f"btn_{i}", disabled=True, use_container_width=True)

        # Show cached AI summary
        if summary_key in st.session_state:
            with st.expander("🤖 AI Analysis", expanded=False):
                st.markdown(st.session_state[summary_key])

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "📡 News from BBC, Reuters, NDTV, TOI, Al Jazeera, The Hindu, ET · "
    "🔄 Auto-refresh every 15 min"
)
