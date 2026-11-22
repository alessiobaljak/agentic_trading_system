"""I fatti gravi del giorno prima (FATTI_GRAVI.md, idea 158 del registro): prepara il foglio della lettura di ogni mattina.

Elenca le monete con il perpetuo di Binance citate negli articoli dell'archivio delle 24 ore prima, con i titoli. Il giudizio («fatto
grave», direzione, forza, ore, perché) lo scrive a mano la sessione principale nel foglio, prima di guardare qualunque prezzo del
giorno, e il foglio si committa subito.

Uso: python3 -m research.notizie.fatti_gravi   (scrive research/notizie/fatti_gravi/AAAA-MM-GG.md, a schermo una riga)
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from research.notizie import raccolta
from research.programma7.misure_g1 import voce14_lettura as v14

QUI = Path(__file__).resolve().parent
FOGLI = QUI / "fatti_gravi"
RADICE = QUI.parents[1]
TITOLI_MAX = 6


def main(ora: datetime | None = None) -> Path:
    ora = (ora or datetime.now(timezone.utc)).replace(second=0, microsecond=0)
    elenco = json.loads(raccolta.nomi(ora).read_text())["elenco"]
    arts = v14.articoli(ora)
    per_moneta: dict = {}
    for q, a in arts:
        for s in raccolta.citate(f"{a.get('titolo', '')} {a.get('sommario', '')}", elenco):
            per_moneta.setdefault(s, []).append((q, a))
    ordine = sorted(per_moneta, key=lambda s: (-len(per_moneta[s]), s))
    righe = [f"# I fatti gravi del giorno prima — {ora:%Y-%m-%d}", "",
             f"Foglio preparato alle {ora:%H:%M} UTC; articoli dell'archivio dalle {ora - timedelta(hours=24):%Y-%m-%d %H:%M} alle "
             f"{ora:%Y-%m-%d %H:%M} UTC: {len(arts)}; monete con il perpetuo citate: {len(ordine)}. Regole: `FATTI_GRAVI.md`.",
             "Il giudizio si scrive prima di guardare qualunque prezzo di oggi; il foglio si committa subito. Dove non è scritto «sì», vale «no».",
             "", "## I casi segnati", "",
             "| moneta | fatto grave | direzione | forza | ore dalla prima notizia | perché (una riga) e collegamento |",
             "|---|---|---|---|---|---|", "| (da scrivere) | | | | | |", "",
             "Ricerche sul web fatte (al più una per moneta segnata): (da scrivere)", "",
             "Commit della lettura: l'ora del commit è la prova.", "", "## Le monete citate e i titoli"]
    for s in ordine:
        xs = per_moneta[s]
        righe.append(f"\n### {s} — {len(xs)} articoli (prima notizia {xs[0][0]:%m-%d %H:%M})")
        for q, a in xs[:TITOLI_MAX]:
            righe.append(f"- {q:%m-%d %H:%M} {a.get('fonte', '')}: {a.get('titolo', '')} — {str(a.get('sommario', ''))[:200]} "
                         f"<{a.get('link', '')}>")
        if len(xs) > TITOLI_MAX:
            righe.append(f"- (altri {len(xs) - TITOLI_MAX})")
    FOGLI.mkdir(exist_ok=True)
    out = FOGLI / f"{ora:%Y-%m-%d}.md"
    if out.exists():
        raise SystemExit(f"{out.name} esiste già: una lettura non si riscrive (FATTI_GRAVI.md, punto 5)")
    out.write_text("\n".join(righe) + "\n", encoding="utf-8")
    print(f"{out.relative_to(RADICE)}: {len(ordine)} monete citate, {len(arts)} articoli nelle 24 ore")
    return out


if __name__ == "__main__":
    main()
