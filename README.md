# 🍵 ItsBrewing Daily News

> AI-powered India news digest — global news filtered for India, summarized in real time.

---

## What It Does

ItsBrewing is a Streamlit web app that automatically:

1. **Fetches** the latest news from 8 major global and Indian RSS feeds
2. **Filters** articles relevant to India using keyword matching
3. **Summarizes** each article on demand using Groq's LLM (Llama 3.3 70B)
4. **Generates** a daily AI digest of top headlines on page load

All AI features are **free** via Groq's API (30 req/min, 14,400 req/day).

---

## Features

| Feature | Details |
|---|---|
| 📡 Multi-source news | BBC, Reuters, NDTV, Times of India, Al Jazeera, The Hindu, Economic Times |
| 🇮🇳 India filter | 30+ keywords filter global news for India relevance |
| 🤖 AI Daily Digest | Auto-generated summary of top headlines on every load |
| ⚡ Streaming summaries | Per-article AI analysis streamed in real time |
| 💾 Smart caching | News cached 15 min · Summaries cached per session |
| 🔍 Source filter | Multi-select filter to view articles by source |
| 🔄 Manual refresh | One-click refresh clears all caches |

---

## Project Structure

```
itsbrewing/
├── app.py              # Streamlit UI — layout, caching, article cards
├── news_fetcher.py     # RSS feed aggregator + India keyword filter
├── summarizer.py       # Groq AI — streaming summaries + daily digest
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
└── .gitignore
```

### `news_fetcher.py`
- Defines `Article` dataclass with `title`, `description`, `link`, `source`, `published`, `image_url`
- `INDIA_FEEDS` — 5 India-specific RSS feeds (fetched without filtering)
- `GLOBAL_FEEDS` — 3 global feeds (filtered by India keywords)
- `fetch_all_news(max_total)` — fetches, filters, deduplicates, and returns articles

### `summarizer.py`
- `stream_summary(article)` — streams a structured AI analysis per article (generator)
- `get_daily_digest(articles)` — returns a 3–4 sentence digest of top headlines

### `app.py`
- Sidebar: article count slider, refresh button, API key status, source list
- Main: header → AI digest → source filter → article cards with streaming summaries
- Uses `st.cache_data(ttl=900)` for news and `st.session_state` for summaries

---

## Getting Started

### 1. Prerequisites

- Python 3.10+
- A free [Groq API key](https://console.groq.com)

### 2. Install dependencies

```powershell
py -m pip install -r requirements.txt
```

### 3. Configure environment

```powershell
copy .env.example .env
```

Open `.env` and add your Groq API key:

```
GROQ_API_KEY=gsk_your-key-here
```

### 4. Run the app

```powershell
py -m streamlit run app.py
```

The app opens at **http://localhost:8501**

---

## News Sources

| Source | Type | Feed |
|---|---|---|
| BBC India | India-specific | BBC World Asia/India RSS |
| Times of India | India-specific | TOI default RSS |
| NDTV | India-specific | NDTV latest RSS |
| The Hindu | India-specific | The Hindu news RSS |
| Economic Times | India-specific | ET default RSS |
| Reuters World | Global (filtered) | Reuters world news RSS |
| Al Jazeera | Global (filtered) | Al Jazeera all news RSS |
| BBC World | Global (filtered) | BBC world news RSS |

Global feeds are filtered using 30+ India-related keywords including: `india`, `modi`, `rupee`, `rbi`, `isro`, `kashmir`, `indo-pacific`, `lok sabha`, and more.

---

## AI Model

| Property | Value |
|---|---|
| Provider | [Groq](https://groq.com) |
| Model | `llama-3.3-70b-versatile` |
| Summary max tokens | 350 |
| Digest max tokens | 250 |
| Cost | Free (Groq free tier) |

Each AI summary follows a structured format:
- **Headline Take** — punchy one-line interpretation
- **Key Facts** — 2–3 bullet points
- **India Angle** — why it matters for India
- **Sentiment** — POSITIVE / NEGATIVE / NEUTRAL / DEVELOPING

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | Your Groq API key from [console.groq.com](https://console.groq.com) |

---

## Tech Stack

- **[Streamlit](https://streamlit.io)** — web UI framework
- **[Groq](https://groq.com)** — LLM inference (free tier)
- **[feedparser](https://feedparser.readthedocs.io)** — RSS feed parsing
- **[python-dotenv](https://pypi.org/project/python-dotenv/)** — environment variable management

---

## Repository

**GitHub:** [github.com/yashdesai-22/itsbrewing](https://github.com/yashdesai-22/itsbrewing)
