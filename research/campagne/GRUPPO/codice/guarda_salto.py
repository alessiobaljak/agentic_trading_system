"""Fase 0 (regole.md, sezione 2, punto 9): guarda le candele giornaliere di last e mark intorno a un salto di prezzo.

Uso: python3 -u guarda_salto.py SIMBOLO AAAA-MM-GG GIORNI
Stampa, per i giorni intorno: apertura, massimo, minimo, chiusura del last, chiusura del mark, volume in moneta e in
USDT. Un cambio di contratto (ridenominazione) darebbe un fattore tondo e permanente su prezzo e volume in moneta,
con il volume in USDT continuo; un movimento vero da' volume in USDT alto e prezzo che si muove anche dopo.
"""
import sys
from datetime import date, timedelta

from comune import RADICE_RICERCA, dati

if __name__ == "__main__":
    simbolo, giorno, n = sys.argv[1], date.fromisoformat(sys.argv[2]), int(sys.argv[3])
    inizio, fine = giorno - timedelta(days=n), giorno + timedelta(days=n)
    s = dati.carica_serie_allineate(simbolo, "1d", inizio, fine, RADICE_RICERCA)
    for c, m in zip(s["candele"], s["candele_mark"]):
        g = date(1970, 1, 1) + timedelta(days=c.ts // 86_400_000)
        print(g, f"o {c.open:.4f} h {c.high:.4f} l {c.low:.4f} c {c.close:.4f} mark {m.close:.4f} "
                 f"vol {c.volume:.0f} usdt {s['volume_usdt'][c.ts] / 1e6:.1f}M")
