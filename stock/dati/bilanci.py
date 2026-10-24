"""Le date dei comunicati sui risultati (i bilanci trimestrali), dalla SEC.

Un comunicato sui risultati è un modulo 8-K con la voce 2.02 («Results of Operations and Financial Condition»). La SEC
lo pubblica in https://data.sec.gov/submissions/CIK##########.json (e nei file «-submissions-NNN.json» per i più vecchi).

**Si usa solo la data del deposito (`filingDate`), non l'ora.** Il 24 ottobre 2026 l'ora (`acceptanceDateTime`) è stata
controllata: per Intel e Visa (comunicato poco dopo le 16:00 di New York) il campo dice 20:05-20:10Z, cioè l'ora vera in
UTC; per Apple (comunicato alle 16:30) dice 00:30Z del giorno dopo, cioè le 20:30 di New York: il modulo può essere
depositato ore dopo il comunicato. L'ora del deposito quindi non dice quando il mercato ha saputo. Con la sola data d, la
reazione si misura dalla chiusura del giorno di borsa prima di d alla chiusura del giorno di borsa dopo d: la finestra
contiene la reazione sia per i comunicati della sera prima del deposito sia per quelli del mattino.

Il codice di ogni azienda (CIK) viene dall'elenco dell'S&P 500 di https://github.com/fja05680/sp500 (`sp500.csv`) e si
controlla sul nome che la SEC restituisce.
"""
from __future__ import annotations

import json
import time
from datetime import date
from pathlib import Path

import pandas as pd
import requests

from stock.dati.archivio import cartella_dati

NY = "America/New_York"
UA = {"User-Agent": "agentic-trading-system research"}
URL = "https://data.sec.gov/submissions/{nome}"
# aziende che non sono più nell'elenco di oggi (controllate sul nome restituito dalla SEC)
# (XOM: nell'elenco di oggi c'è il codice di «ExxonMobil Holdings Corp», che non ha i bilanci passati; quello giusto è
# «EXXON MOBIL CORP», 34088)
CIK_A_MANO = {"AGN": 1578845, "FB": 1326801, "XOM": 34088}
# aziende che hanno cambiato codice: si leggono tutti (Broadcom Ltd fino al 2018, poi Broadcom Inc.)
CIK_IN_PIU = {"AVGO": [1649338]}


def _scarica(nome: str) -> dict:
    p = cartella_dati() / "sec" / nome
    if p.exists():
        return json.loads(p.read_text())
    p.parent.mkdir(parents=True, exist_ok=True)
    for n in range(5):
        r = requests.get(URL.format(nome=nome), headers=UA, timeout=60)
        if r.status_code == 200:
            p.write_text(r.text)
            time.sleep(0.15)                    # la SEC chiede al massimo 10 richieste al secondo
            return r.json()
        time.sleep(2 ** (n + 1))
    r.raise_for_status()


def comunicati(cik: int) -> tuple[str, list[date]]:
    """Il nome dell'azienda e le date di deposito di tutti i suoi 8-K con la voce 2.02."""
    j = _scarica(f"CIK{cik:010d}.json")
    pezzi = [j["filings"]["recent"]] + [_scarica(f["name"]) for f in j["filings"].get("files", [])]
    giorni = set()
    for r in pezzi:
        for f, d, it in zip(r["form"], r["filingDate"], r["items"]):
            if f in ("8-K", "8-K/A") and "2.02" in str(it).split(","):
                giorni.add(date.fromisoformat(d))
    return j.get("name", ""), sorted(giorni)


def un_evento_per_trimestre(giorni: list[date], giorni_minimi: int = 20) -> list[date]:
    """Toglie i 2.02 che arrivano entro `giorni_minimi` dal precedente (correzioni, comunicati ripetuti)."""
    out = []
    for o in sorted(giorni):
        if not out or (o - out[-1]).days >= giorni_minimi:
            out.append(o)
    return out


def cik_dei_simboli(percorso_sp500: Path, simboli: list[str]) -> dict[str, int]:
    df = pd.read_csv(percorso_sp500)
    m = dict(zip(df["Symbol"], df["CIK"]))
    out = {}
    for s in simboli:
        out[s] = int(CIK_A_MANO.get(s) or m.get(s) or m.get(s.replace(".", "-")) or 0)
    return out


def comunicati_del_simbolo(simbolo: str, cik: int) -> tuple[str, list[date]]:
    """Come `comunicati`, unendo anche i codici vecchi dell'azienda (`CIK_IN_PIU`)."""
    nome, giorni = comunicati(cik)
    for altro in CIK_IN_PIU.get(simbolo, []):
        giorni = sorted(set(giorni) | set(comunicati(altro)[1]))
    return nome, giorni
