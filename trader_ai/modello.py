"""La chiamata al modello (REGOLE.md, sezioni 2 e 5) e il modello finto per i test.

Nessun ripiego su altri modelli: il modello l'ha scelto il proprietario (23 novembre 2026). Rifiuto, risposta fuori schema,
risposta tagliata o errore del servizio: nessuna operazione nuova, la sveglia riprova fra 30 minuti.
"""
from __future__ import annotations

import os
import random
from dataclasses import dataclass, field
from typing import List, Optional

from trader_ai.costi import MAX_TOKENS, MODELLO
from trader_ai.schema import Allarme, Decisione, Risposta


@dataclass
class Esito:
    risposta: Optional[Risposta]
    stato: str                      # «ok», «rifiuto», «troncata», «fuori_schema», «errore»
    usage: dict = field(default_factory=dict)
    dettaglio: str = ""


def crea_client():
    """Client dell'SDK ufficiale; la chiave arriva da ANTHROPIC_API_KEY (mai da un file del repository)."""
    import anthropic

    ws = (os.environ.get("ANTHROPIC_WORKSPACE_ID") or "").strip()  # chiavi d'organizzazione: vedi bot/ai/client.py
    return anthropic.Anthropic(timeout=300.0, default_headers={"anthropic-workspace-id": ws} if ws else None)


def chiama(client, system: str, utente: str, max_tokens: int = MAX_TOKENS) -> Esito:
    import anthropic
    import pydantic

    try:
        r = client.messages.parse(
            model=MODELLO,
            max_tokens=max_tokens,
            system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": utente}],
            output_config={"effort": "medium"},
            output_format=Risposta,
        )
    except pydantic.ValidationError as e:
        return Esito(None, "fuori_schema", dettaglio=str(e)[:500])
    except anthropic.APIError as e:
        return Esito(None, "errore", dettaglio=f"{type(e).__name__}: {str(e)[:300]}")
    usage = r.usage.model_dump() if r.usage else {}
    if r.stop_reason == "refusal":
        cat = getattr(getattr(r, "stop_details", None), "category", None)
        return Esito(None, "rifiuto", usage, f"categoria {cat}")
    if r.stop_reason == "max_tokens":
        return Esito(None, "troncata", usage)
    if r.parsed_output is None:
        return Esito(None, "fuori_schema", usage)
    return Esito(r.parsed_output, "ok", usage, getattr(r, "_request_id", "") or "")


class ModelloFinto:
    """Risponde a caso dentro lo schema, a volte con numeri fuori limite: serve a provare che il codice li scarta."""

    def __init__(self, seme: int = 0):
        self.rng = random.Random(seme)

    def chiama(self, monete: List[str], prezzi: dict, in_portafoglio: List[str]) -> Esito:
        rng = self.rng
        decisioni = []
        for m in rng.sample(monete, k=min(len(monete), rng.randint(0, 3))):
            p = prezzi[m]
            lungo = rng.random() < 0.5
            stop = p * (1 - rng.uniform(0.001, 0.4)) if lungo else p * (1 + rng.uniform(0.001, 0.4))
            decisioni.append(Decisione(moneta=m, azione="apri_lungo" if lungo else "apri_corto",
                                       quota_conto=rng.choice([0.05, 0.1, 0.2, 0.5]), leva=rng.choice([1, 2, 3, 10]),
                                       stop_prezzo=stop, motivo="prova del modello finto"))
        for m in in_portafoglio:
            if rng.random() < 0.3:
                decisioni.append(Decisione(moneta=m, azione="chiudi", motivo="prova del modello finto"))
        allarmi = [Allarme(moneta=m, sopra=prezzi[m] * 1.03) for m in rng.sample(monete, k=min(2, len(monete)))]
        risposta = Risposta(decisioni=decisioni, segui=monete[:5], prossimo_controllo_minuti=rng.choice([1, 30, 240, 5000]),
                            allarmi=allarmi, diario="modello finto")
        return Esito(risposta, "ok", {"input_tokens": 20000, "output_tokens": 3000})
