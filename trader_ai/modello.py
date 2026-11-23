"""La chiamata al modello (REGOLE.md, sezioni 2 e 5) e il modello finto per i test.

Nessun ripiego su altri modelli: il modello l'ha scelto il proprietario (23 novembre 2026). Rifiuto, risposta fuori schema,
risposta tagliata o errore del servizio: nessuna operazione nuova; si riprova alla candela da 15 minuti dopo.
"""
from __future__ import annotations

import os
import random
from dataclasses import dataclass, field
from typing import Optional

from trader_ai.costi import MAX_TOKENS, MODELLO
from trader_ai.schema import Risposta


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
    # max_retries=0: ogni tentativo si paga; il tetto conta una chiamata per giro, quindi l'SDK non deve riprovare da solo
    return anthropic.Anthropic(timeout=300.0, max_retries=0,
                               default_headers={"anthropic-workspace-id": ws} if ws else None)


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
    """Risponde a caso dentro lo schema, a volte con numeri fuori regola: serve a provare che il codice li scarta."""

    def __init__(self, seme: int = 0):
        self.rng = random.Random(seme)

    def chiama(self, prezzo: float, ha_posizione: bool) -> Esito:
        rng = self.rng
        azioni = ["aspetta", "chiudi", "modifica"] if ha_posizione else ["aspetta", "apri_lungo", "apri_corto", "chiudi"]
        azione = rng.choice(azioni)
        leva = rng.choice([1, 3, 5, 10, 20])
        lungo = azione == "apri_lungo"
        dist = rng.uniform(0.001, 0.2)
        stop = prezzo * (1 - dist if lungo else 1 + dist)
        r = Risposta(azione=azione, margine_usdt=rng.choice([5, 50, 200, 5000]), leva=leva, stop_prezzo=stop,
                     approccio="prova del modello finto", cambio_approccio=rng.random() < 0.1, diario="modello finto")
        return Esito(r, "ok", {"input_tokens": 6000, "output_tokens": 2000})
