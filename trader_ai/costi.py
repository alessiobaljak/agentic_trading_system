"""Il costo delle chiamate al modello e il tetto di spesa giornaliero (REGOLE.md, sezione 2).

Prezzi di Claude Opus 5.5 dalla pagina ufficiale (https://platform.claude.com/docs/en/about-claude/models/overview,
letta il 21 novembre 2026; guida della cache rivista il 26 novembre): 4 dollari al milione di token in entrata, 20 in uscita;
lettura dalla cache al 5% dell'entrata (0,20); scrittura in cache da 5 minuti a 1,25 volte (5,00), da un'ora a 2 volte (8,00).
Dal 26 novembre la cache è da un'ora (controllo del 26 novembre 2026, punto 2.3: con una chiamata ogni 15 minuti quella da 5
minuti scadeva sempre: 100 scritture e 4 letture su 104 chiamate). Il tetto è 5,00 dollari al giorno UTC (il proprietario ha
detto 5 euro: 5 dollari restano sotto finché l'euro vale più del dollaro).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

MODELLO = "claude-opus-5-5"
PREZZI = {  # dollari al milione di token
    "claude-opus-5-5": {"entrata": 4.00, "uscita": 20.00, "cache_lettura": 0.20, "cache_scrittura_5m": 5.00,
                        "cache_scrittura_1h": 8.00},
}
TETTO_GIORNO_DOLLARI = 5.00
#: Token della risposta al massimo (pensiero compreso): fissa anche il costo massimo della risposta (16.000 x 20 / milione
#: = 0,32 dollari).
MAX_TOKENS = 16000   # sforzo «high» dal 26 novembre: più spazio per il ragionamento
#: Caratteri per token, per difetto: misurati circa 1,8 (alle 07:00 del 26 novembre 2026, 9.287 token per circa 16.600
#: caratteri); con 1,5 la stima dei token sta in eccesso.
CARATTERI_PER_TOKEN = 1.5


def costo_dollari(usage: dict, modello: str = MODELLO) -> float:
    """Costo di una risposta dai token che dichiara (campi `usage` dell'API). Le scritture in cache si pagano secondo la durata
    (`cache_creation`: da 5 minuti e da un'ora); `cache_creation_input_tokens` è la loro somma e non si conta due volte. Senza il
    dettaglio, tutte al prezzo più alto."""
    p = PREZZI[modello]
    dettaglio = usage.get("cache_creation") or {}
    s5, s1 = dettaglio.get("ephemeral_5m_input_tokens"), dettaglio.get("ephemeral_1h_input_tokens")
    if s5 is None and s1 is None:
        s5, s1 = 0, usage.get("cache_creation_input_tokens") or 0
    return (
        (usage.get("input_tokens") or 0) * p["entrata"]
        + (usage.get("output_tokens") or 0) * p["uscita"]
        + (usage.get("cache_read_input_tokens") or 0) * p["cache_lettura"]
        + (s5 or 0) * p["cache_scrittura_5m"] + (s1 or 0) * p["cache_scrittura_1h"]
    ) / 1_000_000


def costo_massimo(caratteri: int, max_tokens: int = MAX_TOKENS, modello: str = MODELLO) -> float:
    """Il costo più alto che una chiamata può avere, calcolato prima di farla: tutto il messaggio pagato al prezzo più caro (la
    scrittura nella cache da un'ora, 2 volte l'entrata) e la risposta lunga quanto il massimo permesso."""
    p = PREZZI[modello]
    return (caratteri / CARATTERI_PER_TOKEN * p["cache_scrittura_1h"] + max_tokens * p["uscita"]) / 1_000_000


def giorno_utc(ora: datetime) -> str:
    return ora.astimezone(timezone.utc).strftime("%Y-%m-%d")


@dataclass
class Budget:
    """Registro della spesa per giorno UTC, salvato in un file JSON ({giorno: dollari})."""

    percorso: Path
    tetto: float = TETTO_GIORNO_DOLLARI

    def _leggi(self) -> dict:
        try:
            return json.loads(Path(self.percorso).read_text())
        except FileNotFoundError:
            return {}

    def speso(self, ora: datetime) -> float:
        return float(self._leggi().get(giorno_utc(ora), 0.0))

    def rimasto(self, ora: datetime) -> float:
        return max(0.0, self.tetto - self.speso(ora))

    def puo_chiamare(self, ora: datetime, costo_massimo: float) -> bool:
        """Si chiama solo se anche il costo più alto possibile della chiamata sta sotto il tetto."""
        return costo_massimo <= self.rimasto(ora)

    def registra(self, ora: datetime, dollari: float) -> None:
        dati = self._leggi()
        g = giorno_utc(ora)
        dati[g] = round(float(dati.get(g, 0.0)) + dollari, 6)
        p = Path(self.percorso)
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps(dati, indent=1, sort_keys=True))
        tmp.replace(p)
