"""La chiamata al modello (REGOLE.md, sezioni 2 e 5) e il modello finto per i test.

Nessun ripiego su altri modelli: il modello l'ha scelto il proprietario (23 novembre 2026). Rifiuto, risposta fuori schema,
risposta tagliata o errore del servizio: nessuna operazione nuova; si riprova alla candela da 15 minuti dopo.

Dal 26 novembre 2026 (controllo del 26 novembre, punti 2.3 e 2.7): le istruzioni e la memoria stabile stanno nella cache da un'ora;
il ragionamento torna riassunto (`display: "summarized"`: si paga uguale, ma si vede come ragiona) e si misura la durata.
"""
from __future__ import annotations

import os
import random
import time
from dataclasses import dataclass, field
from typing import List, Optional, Union

from trader_ai.costi import MAX_TOKENS, MODELLO
from trader_ai.schema import Risposta


@dataclass
class Esito:
    risposta: Optional[Risposta]
    stato: str                      # «ok», «rifiuto», «troncata», «fuori_schema», «errore»
    usage: dict = field(default_factory=dict)
    dettaglio: str = ""
    pensiero: str = ""              # il riassunto del ragionamento
    durata_s: float = 0.0


def crea_client():
    """Client dell'SDK ufficiale; la chiave arriva da ANTHROPIC_API_KEY (mai da un file del repository)."""
    import anthropic

    ws = (os.environ.get("ANTHROPIC_WORKSPACE_ID") or "").strip()  # chiavi d'organizzazione: vedi bot/ai/client.py
    # max_retries=0: ogni tentativo si paga; il tetto conta una chiamata per giro, quindi l'SDK non deve riprovare da solo
    return anthropic.Anthropic(timeout=600.0, max_retries=0,   # sforzo «high»: fino a 5 minuti
                               default_headers={"anthropic-workspace-id": ws} if ws else None)


CACHE = {"type": "ephemeral", "ttl": "1h"}


def contenuto(utente: Union[str, List[str]]) -> list:
    """Il messaggio in blocchi: il primo (la memoria stabile) nella cache da un'ora, gli altri no. Nessun blocco vuoto (l'API li
    rifiuta)."""
    blocchi = [utente] if isinstance(utente, str) else [b for b in utente if b]
    out = [{"type": "text", "text": b} for b in blocchi]
    if len(out) > 1:
        out[0]["cache_control"] = CACHE
    return out


def chiama(client, system: str, utente: Union[str, List[str]], max_tokens: int = MAX_TOKENS) -> Esito:
    """Una chiamata con l'uscita strutturata (`output_config.format`, lo schema di `Risposta`). La risposta si valida qui, dopo aver
    guardato `stop_reason`: così una risposta tagliata mentre scrive il JSON resta «troncata» e tiene i token dichiarati (con
    `messages.parse` l'SDK lanciava subito un errore di validazione e i token si perdevano: revisione del 26 novembre 2026, R7-08)."""
    import anthropic
    import pydantic

    inizio = time.monotonic()
    try:
        r = client.messages.create(
            model=MODELLO,
            max_tokens=max_tokens,
            system=[{"type": "text", "text": system, "cache_control": CACHE}],
            messages=[{"role": "user", "content": contenuto(utente)}],
            thinking={"type": "adaptive", "display": "summarized"},
            # sforzo alto: il proprietario, 26 novembre: «se non pensa...»
            output_config={"effort": "high", "format": {"type": "json_schema", "schema": anthropic.transform_schema(Risposta)}},
        )
    except anthropic.APIError as e:
        return Esito(None, "errore", dettaglio=f"{type(e).__name__}: {str(e)[:300]}",
                     durata_s=round(time.monotonic() - inizio, 1))
    durata = round(time.monotonic() - inizio, 1)
    usage = r.usage.model_dump() if r.usage else {}
    blocchi = getattr(r, "content", None) or []
    pensiero = "\n".join(getattr(b, "thinking", "") or "" for b in blocchi if getattr(b, "type", "") == "thinking").strip()
    if r.stop_reason == "refusal":
        cat = getattr(getattr(r, "stop_details", None), "category", None)
        return Esito(None, "rifiuto", usage, f"categoria {cat}", pensiero, durata)
    if r.stop_reason == "max_tokens":
        return Esito(None, "troncata", usage, "", pensiero, durata)
    testo = "".join(getattr(b, "text", "") or "" for b in blocchi if getattr(b, "type", "") == "text")
    try:
        risposta = Risposta.model_validate_json(testo)
    except pydantic.ValidationError as e:
        return Esito(None, "fuori_schema", usage, str(e)[:300], pensiero, durata)
    return Esito(risposta, "ok", usage, getattr(r, "_request_id", "") or "", pensiero, durata)


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
