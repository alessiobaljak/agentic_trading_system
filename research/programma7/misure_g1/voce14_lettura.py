"""Voce 14 di G1 (VOCE14_REGOLE.md): le notizie delle monete vendute, lette ogni mattina prima dei prezzi.

Prepara il foglio della lettura del giorno: le monete del lato venduto del paper G1 (dall'ultima risposta «stato» della macchina) e,
per ciascuna, gli articoli dell'archivio delle notizie delle 24 ore prima. Il giudizio lo scrive a mano la sessione principale nel
foglio, prima di guardare qualunque prezzo del giorno, e il foglio si committa subito.

Uso: python3 -m research.programma7.misure_g1.voce14_lettura   (scrive misure_g1/voce14_letture/AAAA-MM-GG.md, a schermo poche righe)
"""
from __future__ import annotations

import gzip
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from research.notizie import raccolta

RADICE = Path(__file__).resolve().parents[3]
RISULTATI = RADICE / "ops" / "results"
LETTURE = Path(__file__).resolve().parent / "voce14_letture"
RIGA = re.compile(r"([0-9A-Z一-鿿]+USDT) ([+-]\d+\.\d+)/([+-]\d+\.\d+)")


def ultimo_stato() -> tuple[Path, datetime, dict]:
    """L'ultima risposta «stato» con la tabella dei pesi: file, ora della lettura, pesi del paper G1 (in % del conto)."""
    for f in sorted(RISULTATI.glob("*stato*.md"), reverse=True):
        t = f.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"Letto il (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC\. In % del conto, paper/demo", t)
        if not m:
            continue
        ora = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        blocco = t[m.end():].split("\n## ", 1)[0]
        pesi = {s: float(p) for s, p, _ in RIGA.findall(blocco)}
        return f, ora, pesi
    raise SystemExit("nessuna risposta «stato» con la tabella dei pesi in ops/results/")


def _quando(r: dict) -> datetime | None:
    x = r.get("pubblicato") or r.get("visto")
    if not x:
        return None
    try:
        return datetime.fromisoformat(str(x).replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def articoli(fine: datetime) -> list:
    """Gli articoli dell'archivio pubblicati (o visti, se manca l'ora) nelle 24 ore prima di `fine`."""
    out = []
    for k in (0, 1):
        f = raccolta.ARCHIVIO / f"{(fine - timedelta(days=k)).strftime('%Y-%m-%d')}.jsonl.gz"
        if f.exists():
            with gzip.open(f, "rt", encoding="utf-8") as g:
                for r in g:
                    if r.strip():
                        a = json.loads(r)
                        q = _quando(a)
                        if q and fine - timedelta(hours=24) <= q < fine:
                            out.append((q, a))
    return sorted(out, key=lambda x: x[0])


def sigla_di(simbolo: str) -> str:
    s = simbolo[:-4]
    return re.sub(r"^1000+", "", s)


def cita(testo: str, simbolo: str, elenco: dict) -> bool:
    """Come `raccolta.citate`; per le monete fuori dall'elenco dei nomi, solo la sigla (VOCE14_REGOLE.md, punto 3)."""
    if simbolo in elenco:
        return simbolo in raccolta.citate(testo, {simbolo: elenco[simbolo]})
    sigla = sigla_di(simbolo)
    if re.search(r"\$" + re.escape(sigla) + r"\b", testo, re.I):
        return True
    return len(sigla) >= 3 and sigla not in raccolta.PAROLE and bool(
        re.search(r"(?<![A-Za-z0-9])" + re.escape(sigla) + r"(?![A-Za-z0-9])", testo))


def main() -> None:
    f, ora, pesi = ultimo_stato()
    vendute = sorted(((s, p) for s, p in pesi.items() if p < 0), key=lambda x: x[1])
    elenco = json.loads(raccolta.nomi(ora).read_text())["elenco"]
    arts = articoli(ora)
    righe = [f"# Lettura delle notizie delle monete vendute da G1 — {ora:%Y-%m-%d}",
             "",
             f"Pesi del paper G1 da `{f.relative_to(RADICE)}` (letti alle {ora:%H:%M} UTC); articoli dell'archivio dalle "
             f"{ora - timedelta(hours=24):%Y-%m-%d %H:%M} alle {ora:%Y-%m-%d %H:%M} UTC: {len(arts)}. Regole: `VOCE14_REGOLE.md`.",
             "Il giudizio (colonna «a rischio di salire») si scrive prima di guardare qualunque prezzo di oggi; il foglio si committa subito.",
             "",
             "| moneta | peso | articoli | a rischio di salire | perché (una riga) |",
             "|---|---|---|---|---|"]
    dettagli = []
    for s, p in vendute:
        trovati = [(q, a) for q, a in arts if cita(f"{a.get('titolo', '')} {a.get('sommario', '')}", s, elenco)]
        righe.append(f"| {s} | {p:+.2f}% | {len(trovati)} | {'no (nessuna notizia)' if not trovati else '?'} | |")
        if trovati:
            dettagli.append(f"\n### {s}")
            for q, a in trovati[:8]:
                dettagli.append(f"- {q:%m-%d %H:%M} {a.get('fonte', '')}: {a.get('titolo', '')} — {str(a.get('sommario', ''))[:220]}")
            if len(trovati) > 8:
                dettagli.append(f"- (altri {len(trovati) - 8})")
    LETTURE.mkdir(exist_ok=True)
    out = LETTURE / f"{ora:%Y-%m-%d}.md"
    if out.exists():
        raise SystemExit(f"{out.name} esiste già: una lettura non si riscrive (VOCE14_REGOLE.md, punto 5)")
    web = [s for s, p in vendute if p <= -2.0]
    righe += ["", f"Ricerche sul web ammesse (regola 3b, peso di almeno il 2%): {', '.join(web) or 'nessuna'}.",
              "Ricerche fatte e cosa hanno dato: (da scrivere)", "", "Commit della lettura: (l'ora del commit è la prova)"]
    out.write_text("\n".join(righe + ["", "## Gli articoli"] + dettagli) + "\n", encoding="utf-8")
    con = sum(1 for r in righe if r.endswith("| ? | |"))
    print(f"{out.relative_to(RADICE)}: {len(vendute)} monete vendute, {con} con notizie da leggere, {len(arts)} articoli nelle 24 ore")


if __name__ == "__main__":
    main()
