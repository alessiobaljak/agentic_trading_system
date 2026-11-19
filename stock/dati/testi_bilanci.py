"""La somiglianza del testo di ogni bilancio con quello dello stesso tipo dell'anno prima (prova 41, `stock/prove/P041_lazy_prices.md`).

    SEC_CONTATTO="…" python -m stock.dati.testi_bilanci --minuti 100     # riprende da dove si è fermato; poi:
    python -m stock.dati.testi_bilanci --unisci                          # scrive stock/prove/dati/P041_somiglianze.csv.gz

Per ogni azienda (codici SEC di `stock/prove/dati/P039_codici.csv.gz`): l'elenco dei 10-K e 10-Q depositati dal 2015 al 2024 (non le
correzioni «/A») dall'elenco dei depositi della SEC; di ognuno si scarica il solo documento principale, si tolgono i dati nascosti
(`ix:header`), gli script, gli stili e i tag, si contano le parole (almeno 3 lettere, minuscole) e si calcola la somiglianza del coseno
con il bilancio dello stesso tipo depositato fra 9 e 15 mesi prima (il più vicino a 12 mesi). **I testi non si salvano**: per ogni azienda
resta un file con le sole somiglianze (`~/stock_dati/sec/somiglianze/`), così il lavoro si riprende azienda per azienda.

La SEC chiede un indirizzo di contatto nell'intestazione: solo dall'ambiente (`SEC_CONTATTO`, `dirigenti.intestazione`), mai in un file.
Al massimo 4 richieste al secondo (la SEC ne ammette 10).
"""
from __future__ import annotations

import html
import json
import math
import re
import sys
import time
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import requests

from stock.dati.archivio import cartella_dati
from stock.dati.dirigenti import intestazione

QUI = Path(__file__).resolve().parents[1] / "prove" / "dati"
ELENCO = "https://data.sec.gov/submissions/{nome}"
DOCUMENTO = "https://www.sec.gov/Archives/edgar/data/{cik}/{numero}/{doc}"
DAL, FINO = date(2015, 1, 1), date(2024, 12, 31)
TIPI = ("10-K", "10-Q")
DA, A = timedelta(days=273), timedelta(days=456)
PAUSA = 0.25
_ultimo = [0.0]


def _richiesta(url: str) -> requests.Response:
    for n in range(5):
        attesa = PAUSA - (time.monotonic() - _ultimo[0])
        if attesa > 0:
            time.sleep(attesa)
        _ultimo[0] = time.monotonic()
        try:
            r = requests.get(url, headers=intestazione(), timeout=120)
        except (requests.ConnectionError, requests.Timeout):   # la SEC chiude a volte la connessione: si riprova
            if n == 4:
                raise
            time.sleep(2 ** (n + 2))
            continue
        if r.status_code in (200, 404):
            return r
        time.sleep(2 ** (n + 1))
    r.raise_for_status()
    return r


# --- il testo (senza rete) ---------------------------------------------------------------------------------------------------------
_NASCOSTI = re.compile(r"<ix:header>.*?</ix:header>|<script.*?</script>|<style.*?</style>", re.IGNORECASE | re.DOTALL)
_TAG = re.compile(r"<[^>]+>")
_PAROLA = re.compile(r"[a-z]{3,}")


def parole(documento: str) -> Counter:
    t = _NASCOSTI.sub(" ", documento)
    t = _TAG.sub(" ", t)
    t = html.unescape(t).lower()
    return Counter(_PAROLA.findall(t))


def coseno(a: Counter, b: Counter) -> float:
    if not a or not b:
        return float("nan")
    piccolo, grande = (a, b) if len(a) < len(b) else (b, a)
    num = sum(v * grande.get(k, 0) for k, v in piccolo.items())
    return num / (math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values())))


def precedente(bilanci: list[tuple[str, date]], k: int) -> int | None:
    """L'indice del bilancio dello stesso tipo depositato fra 9 e 15 mesi prima del k-esimo, il più vicino a 12 mesi; None se non c'è."""
    tipo, d = bilanci[k]
    cand = [j for j, (t, dj) in enumerate(bilanci) if t == tipo and DA <= d - dj <= A]
    if not cand:
        return None
    return min(cand, key=lambda j: (abs((d - bilanci[j][1]) - timedelta(days=365)), -j))


# --- l'elenco e lo scarico -----------------------------------------------------------------------------------------------------------
def elenco_bilanci(cik: int) -> list[dict]:
    """I 10-K e 10-Q dal 2015 al 2024: tipo, deposito, numero, documento. Dall'elenco della SEC in cache (o scaricato e ridotto)."""
    base = cartella_dati() / "sec"
    righe = []
    nomi = [f"CIK{cik:010d}.json"]
    visti = set()
    while nomi:
        nome = nomi.pop()
        if nome in visti:
            continue
        visti.add(nome)
        p = base / nome
        ridotto = base / "elenchi" / nome
        if p.exists():
            j = json.loads(p.read_text())
        elif ridotto.exists():
            j = json.loads(ridotto.read_text())
        else:
            r = _richiesta(ELENCO.format(nome=nome))
            if r.status_code == 404:
                continue
            j = r.json()
            r_ = j["filings"]["recent"] if "filings" in j else j
            tieni = [i for i, f in enumerate(r_["form"]) if f in TIPI]
            piccolo = {c: [r_[c][i] for i in tieni] for c in ("form", "filingDate", "accessionNumber", "primaryDocument")}
            if "filings" in j:
                piccolo = {"filings": {"recent": piccolo, "files": j["filings"].get("files", [])}}
            ridotto.parent.mkdir(parents=True, exist_ok=True)
            ridotto.write_text(json.dumps(piccolo))
            j = piccolo
        r_ = j["filings"]["recent"] if "filings" in j else j
        nomi += [f["name"] for f in (j.get("filings", {}).get("files", []) if "filings" in j else [])]
        for f, d, a, doc in zip(r_["form"], r_["filingDate"], r_["accessionNumber"], r_["primaryDocument"]):
            dd = date.fromisoformat(d)
            if f in TIPI and DAL <= dd <= FINO and doc:
                righe.append({"tipo": f, "deposito": dd, "numero": a, "documento": doc})
    return sorted({(r["deposito"], r["numero"]): r for r in righe}.values(), key=lambda r: (r["deposito"], r["numero"]))


def azienda(cik: int) -> pd.DataFrame:
    """Le somiglianze dei bilanci di un'azienda (dalla memoria, o scaricando i documenti e buttando i testi)."""
    f = cartella_dati() / "sec" / "somiglianze" / f"{cik}.csv"
    if f.exists():
        return pd.read_csv(f, parse_dates=["deposito"])
    b = elenco_bilanci(cik)
    conteggi: dict[int, Counter] = {}
    chiavi = [(r["tipo"], r["deposito"]) for r in b]
    out = []
    for k, r in enumerate(b):
        j = precedente(chiavi, k)
        if j is None:
            continue
        for i in (j, k):
            if i not in conteggi:
                x = _richiesta(DOCUMENTO.format(cik=cik, numero=b[i]["numero"].replace("-", ""), doc=b[i]["documento"]))
                conteggi[i] = parole(x.text) if x.status_code == 200 else Counter()
        out.append({"cik": cik, "tipo": r["tipo"], "deposito": r["deposito"], "numero": r["numero"],
                    "somiglianza": round(coseno(conteggi[k], conteggi[j]), 6), "parole": sum(conteggi[k].values())})
        for i in [i for i in conteggi if i < j]:          # i testi vecchi non servono più
            del conteggi[i]
    df = pd.DataFrame(out, columns=["cik", "tipo", "deposito", "numero", "somiglianza", "parole"])
    f.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(f, index=False)
    return df


def main(argv: list[str]) -> None:
    c = pd.read_csv(QUI / "P039_codici.csv.gz")
    ciks = sorted(set(c["cik"].astype(int)))
    memoria = cartella_dati() / "sec" / "somiglianze"
    if "--unisci" in argv:
        pezzi = [pd.read_csv(memoria / f"{k}.csv") for k in ciks if (memoria / f"{k}.csv").exists()]
        df = pd.concat(pezzi)
        df.to_csv(QUI / "P041_somiglianze.csv.gz", index=False)
        print(f"aziende {len(pezzi)} su {len(ciks)}; bilanci con la somiglianza {len(df)}")
        return
    minuti = float(argv[argv.index("--minuti") + 1]) if "--minuti" in argv else 1e9
    fine = time.monotonic() + 60 * minuti
    fatte = sum((memoria / f"{k}.csv").exists() for k in ciks)
    for k in ciks:
        if time.monotonic() > fine:
            break
        if (memoria / f"{k}.csv").exists():
            continue
        azienda(k)
        fatte += 1
        if fatte % 25 == 0:
            print(f"aziende fatte {fatte} su {len(ciks)}", flush=True)
    print(f"fermo: aziende fatte {fatte} su {len(ciks)}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
