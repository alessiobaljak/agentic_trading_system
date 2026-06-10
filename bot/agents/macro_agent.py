"""
Macro & News Agent.

  * NewsAPI free tier per le crypto headline.
  * Classificazione dell'impatto news via Claude (basso/medio/alto).
  * Eventi macro high-impact (FOMC, CPI, NFP) -> usati dai circuit breaker per
    imporre il "flat ±2h".

Tutto degrada con grazia: senza chiavi ritorna liste vuote.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Optional

import requests

from bot.config import settings

NEWSAPI = "https://newsapi.org/v2/everything"


class MacroNewsAgent:
    def __init__(
        self,
        newsapi_key: str = settings.NEWSAPI_KEY,
        anthropic_key: str = settings.ANTHROPIC_API_KEY,
        timeout: int = 12,
    ) -> None:
        self.newsapi_key = newsapi_key
        self.anthropic_key = anthropic_key
        self.timeout = timeout

    def fetch_headlines(self, query: str = "crypto OR bitcoin OR ethereum", limit: int = 10) -> list[dict]:
        if not self.newsapi_key:
            return []
        try:
            r = requests.get(NEWSAPI, params={
                "q": query, "language": "en", "sortBy": "publishedAt",
                "pageSize": limit, "apiKey": self.newsapi_key,
            }, timeout=self.timeout)
            r.raise_for_status()
            return [
                {"title": a["title"], "source": a.get("source", {}).get("name"),
                 "publishedAt": a.get("publishedAt")}
                for a in r.json().get("articles", [])
            ]
        except Exception as exc:  # noqa: BLE001
            print(f"[macro_agent] newsapi fallito: {exc}")
            return []

    def classify_impact(self, headlines: list[dict]) -> dict:
        """
        Usa Claude per classificare l'impatto complessivo delle news.
        Ritorna {impact: low|medium|high, rationale: str}.
        """
        if not self.anthropic_key or not headlines:
            return {"impact": "low", "rationale": "nessuna news o API non configurata"}
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self.anthropic_key)
            titles = "\n".join(f"- {h['title']}" for h in headlines)
            msg = client.messages.create(
                model=settings.ANTHROPIC_MODEL,
                max_tokens=300,
                messages=[{
                    "role": "user",
                    "content": (
                        "Classifica l'impatto di mercato crypto di queste headline. "
                        "Rispondi SOLO con JSON {\"impact\": \"low|medium|high\", "
                        "\"rationale\": \"...\"}.\n\n" + titles
                    ),
                }],
            )
            text = msg.content[0].text.strip()
            start, end = text.find("{"), text.rfind("}")
            return json.loads(text[start:end + 1])
        except Exception as exc:  # noqa: BLE001
            print(f"[macro_agent] classificazione fallita: {exc}")
            return {"impact": "low", "rationale": f"errore: {exc}"}

    def upcoming_high_impact_events(self) -> list[dict]:
        """
        Eventi macro high-impact noti nelle prossime 4h.
        Placeholder: in produzione, scraping del calendario economico (es.
        Investing.com / ForexFactory). Ritorna [{name, timestamp_utc}].
        Documentato in docs/data_sources.md.
        """
        return []
