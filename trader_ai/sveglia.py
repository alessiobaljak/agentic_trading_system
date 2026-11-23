"""Quando richiamare il modello (REGOLE.md, sezione 3): lo decide lui, il codice guarda i prezzi ogni minuto senza costi.

Lo sveglia prima del tempo scelto quando scatta un suo allarme, quando una posizione si chiude sullo stop o quando una
moneta in portafoglio si muove di più del 5% dall'ultima chiamata. Fra due chiamate passano almeno 5 minuti.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Iterable, List, Optional

from trader_ai.schema import Allarme, Risposta

MINUTI_MIN, MINUTI_MAX = 15, 1440
ALLARMI_MAX = 20
SEGUI_MAX = 15
PAUSA_MIN = timedelta(minutes=5)
MOVIMENTO = 0.05
DOPO_ERRORE = timedelta(minutes=30)


@dataclass
class Sveglia:
    ultima: Optional[datetime] = None
    prossima: Optional[datetime] = None
    allarmi: List[Allarme] = field(default_factory=list)
    riferimento: Dict[str, float] = field(default_factory=dict)  # prezzo delle monete in portafoglio all'ultima chiamata

    def imposta(self, ora: datetime, risposta: Optional[Risposta], prezzi: Dict[str, float],
                in_portafoglio: Iterable[str]) -> None:
        """Dopo una chiamata: tempo scelto (portato fra 15 e 1.440 minuti), allarmi validi, prezzi di riferimento."""
        self.ultima = ora
        self.riferimento = {m: prezzi[m] for m in in_portafoglio if m in prezzi}
        if risposta is None:  # rifiuto, risposta fuori schema o errore: si riprova fra 30 minuti
            self.prossima = ora + DOPO_ERRORE
            return
        minuti = min(max(int(risposta.prossimo_controllo_minuti), MINUTI_MIN), MINUTI_MAX)
        self.prossima = ora + timedelta(minutes=minuti)
        validi = []
        for a in risposta.allarmi:
            m = a.moneta.strip().upper()
            if m in prezzi and (a.sopra is not None or a.sotto is not None):
                validi.append(a.model_copy(update={"moneta": m}))
        self.allarmi = validi[:ALLARMI_MAX]

    def motivo(self, ora: datetime, prezzi: Dict[str, float], stop_chiusi: Iterable[str] = ()) -> Optional[str]:
        """Perché chiamare adesso, o None. Gli allarmi scattati si tolgono (non suonano due volte)."""
        if self.ultima is None:
            return "primo avvio"
        if ora - self.ultima < PAUSA_MIN:
            return None
        chiusi = list(stop_chiusi)
        if chiusi:
            return "stop eseguito: " + ", ".join(chiusi)
        for a in list(self.allarmi):
            p = prezzi.get(a.moneta)
            if p is None:
                continue
            if a.sopra is not None and p >= a.sopra or a.sotto is not None and p <= a.sotto:
                self.allarmi.remove(a)
                return f"allarme {a.moneta} a {p:g}"
        for m, rif in self.riferimento.items():
            p = prezzi.get(m)
            if p and rif and abs(p / rif - 1) > MOVIMENTO:
                return f"movimento {m} {p / rif - 1:+.1%} dall'ultima chiamata"
        if self.prossima is not None and ora >= self.prossima:
            return "tempo scelto"
        return None
