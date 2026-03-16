from typing import Generator
import os
from dotenv import load_dotenv
from groq import Groq
from news_fetcher import Article

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


def stream_summary(article: Article) -> Generator[str, None, None]:
    """Stream an eye-catching AI summary for a single article."""
    prompt = f"""You are a sharp news analyst for an AI-powered Indian news digest called ItsBrewingNews.

Create a punchy, eye-catching summary of this news article. Format:

**[emoji] HEADLINE TAKE**
[One sentence punchy interpretation of the headline]

**Key Facts:**
• [Fact 1]
• [Fact 2]
• [Fact 3 if relevant]

**India Angle:** [Why this matters specifically for India — 1 crisp sentence]

**Sentiment:** POSITIVE 📈 / NEGATIVE 📉 / NEUTRAL ➡️ / DEVELOPING 🔄

Be factual, concise, and engaging. No filler phrases.

---
Title: {article.title}
Source: {article.source}
Content: {article.description}"""

    stream = client.chat.completions.create(
        model=MODEL,
        max_tokens=350,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    for chunk in stream:
        yield chunk.choices[0].delta.content or ""


def get_daily_digest(articles: list[Article]) -> str:
    """Generate a short AI daily digest from top headlines."""
    headlines = "\n".join(
        f"- {a.title} ({a.source})" for a in articles[:10]
    )
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=250,
        messages=[
            {
                "role": "user",
                "content": f"""You are an AI news anchor for ItsBrewingNews, an India-focused news digest.

Write a 3–4 sentence "Today's India News Digest" from these headlines. Make it engaging, like a polished TV news intro. Start with "🇮🇳 **TODAY'S DIGEST —**"

Headlines:
{headlines}""",
            }
        ],
    )
    return response.choices[0].message.content
