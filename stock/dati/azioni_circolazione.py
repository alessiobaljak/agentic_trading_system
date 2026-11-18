"""Le azioni in circolazione dichiarate alla SEC e il codice SEC del simbolo di allora (prova 39, `stock/prove/P039_emissione_netta.md`).

    SEC_CONTATTO="…" python -m stock.dati.azioni_circolazione     # scrive stock/prove/dati/P039_codici.csv.gz e P039_azioni.csv.gz

* **Il codice SEC di allora:** dai moduli 3, 4 e 5 dei dirigenti (`~/stock_dati/sec/form345/`, `stock/dati/dirigenti.py`): per ogni
  simbolo, codice dell'azienda e mese, l'ultimo giorno in cui un modulo con quel simbolo è stato depositato. Così un simbolo passato a
  un'altra azienda prende il codice giusto per ogni periodo (il difetto della prova 31).
* **Le azioni:** i fatti dell'azienda (`https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json`), elemento
  `dei:EntityCommonStockSharesOutstanding` (il numero scritto in copertina): per ogni deposito e data di riferimento la somma delle
  classi, con la data del deposito. Solo i depositi fino al 31 dicembre 2024.

La SEC chiede un indirizzo di contatto nell'intestazione: si legge solo dall'ambiente (`SEC_CONTATTO`, `dirigenti.intestazione`), mai
in un file. Al massimo una richiesta al secondo. Nel repository vanno solo dati pubblici della SEC, niente prezzi.
"""
from __future__ import annotations

import bisect
import json
import time
from datetime import date
from pathlib import Path

import pandas as pd
import requests

from stock.dati.archivio import cartella_dati
from stock.dati.dirigenti import cartella as cartella_345
from stock.dati.dirigenti import intestazione

QUI = Path(__file__).resolve().parents[1] / "prove" / "dati"
URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
FINO = date(2024, 12, 31)


def codici_dei_moduli(dal: int = 2015, al: int = 2024, cartella: Path | None = None) -> pd.DataFrame:
    """Per simbolo, codice e mese: l'ultimo giorno di deposito di un modulo dei dirigenti con quel simbolo. Colonne: simbolo, cik, giorno."""
    base = cartella or cartella_345()
    pezzi = []
    for d in sorted(p for p in base.iterdir() if p.is_dir() and dal <= int(p.name[:4]) <= al):
        s = pd.read_csv(d / "SUBMISSION.tsv", sep="\t", dtype=str, keep_default_na=False,
                        usecols=["FILING_DATE", "ISSUERCIK", "ISSUERTRADINGSYMBOL"])
        s = s[(s["ISSUERTRADINGSYMBOL"] != "") & (s["ISSUERCIK"] != "")]
        pezzi.append(pd.DataFrame({"simbolo": s["ISSUERTRADINGSYMBOL"].str.upper().str.strip().str.replace("-", ".", regex=False),
                                   "cik": pd.to_numeric(s["ISSUERCIK"], errors="coerce"),
                                   "giorno": pd.to_datetime(s["FILING_DATE"], format="%d-%b-%Y", errors="coerce")}))
    x = pd.concat(pezzi).dropna()
    x = x[x["giorno"].dt.date <= FINO]
    x["cik"] = x["cik"].astype(int)
    x["mese"] = x["giorno"].dt.to_period("M")
    x = x.sort_values("giorno").groupby(["simbolo", "cik", "mese"], as_index=False).last()
    x["giorno"] = x["giorno"].dt.date
    return x[["simbolo", "cik", "giorno"]].sort_values(["simbolo", "giorno", "cik"]).reset_index(drop=True)


def codice_al(righe: list[tuple[date, int]], giorno: date, finestra: int = 365) -> int | None:
    """`righe`: (giorno, cik) di un simbolo in ordine. Il codice dell'ultimo deposito prima di `giorno`, entro `finestra` giorni."""
    k = bisect.bisect_left(righe, (giorno, -1)) - 1
    if k < 0 or (giorno - righe[k][0]).days > finestra:
        return None
    return righe[k][1]


def ridotto(j: dict) -> dict:
    """Dei fatti di un'azienda, solo `dei:EntityCommonStockSharesOutstanding`."""
    try:
        return {"facts": {"dei": {"EntityCommonStockSharesOutstanding": j["facts"]["dei"]["EntityCommonStockSharesOutstanding"]}}}
    except (KeyError, TypeError):
        return {"facts": {}}


def fatti(cik: int) -> dict | None:
    p = cartella_dati() / "sec" / "fatti" / f"CIK{cik:010d}.json"
    if p.exists():
        t = p.read_text()
        return json.loads(t) if t else None
    p.parent.mkdir(parents=True, exist_ok=True)
    for n in range(5):
        r = requests.get(URL.format(cik=cik), headers=intestazione(), timeout=60)
        time.sleep(1.0)
        if r.status_code == 200:
            j = ridotto(r.json())                 # i fatti interi pesano megabyte: si tiene solo l'elemento che serve
            p.write_text(json.dumps(j))
            return j
        if r.status_code == 404:
            p.write_text("")
            return None
        time.sleep(2 ** (n + 1))
    r.raise_for_status()
    return None


def azioni_dichiarate(j: dict | None) -> pd.DataFrame:
    """(fine, deposito, numero, azioni): per ogni deposito e data di riferimento, la somma delle classi; depositi fino al 31 dicembre 2024."""
    colonne = ["fine", "deposito", "numero", "azioni"]
    try:
        v = j["facts"]["dei"]["EntityCommonStockSharesOutstanding"]["units"]["shares"]
    except (KeyError, TypeError):
        return pd.DataFrame(columns=colonne)
    d = pd.DataFrame(v)
    if d.empty or not {"end", "filed", "accn", "val"} <= set(d.columns):
        return pd.DataFrame(columns=colonne)
    d["fine"] = pd.to_datetime(d["end"]).dt.date
    d["deposito"] = pd.to_datetime(d["filed"]).dt.date
    d = d[d["deposito"] <= FINO].drop_duplicates(["accn", "end", "val"])
    g = d.groupby(["accn", "fine", "deposito"], as_index=False)["val"].sum()
    g = g.rename(columns={"accn": "numero", "val": "azioni"})
    return g[colonne].sort_values(["deposito", "fine"]).reset_index(drop=True)


def main() -> None:
    from stock.prove.p028 import decisioni
    fini, membri = decisioni()
    simboli = sorted(set().union(*membri.values()))
    c = codici_dei_moduli()
    c = c[c["simbolo"].isin(simboli)].reset_index(drop=True)
    c.to_csv(QUI / "P039_codici.csv.gz", index=False)
    per_simbolo = {s: list(zip(g["giorno"], g["cik"])) for s, g in c.groupby("simbolo")}
    serve = set()
    senza = 0
    for g in fini:
        for s in membri[g]:
            k = codice_al(per_simbolo.get(s, []), g)
            if k is None:
                senza += 1
            else:
                serve.add(k)
    pezzi = []
    for k, cik in enumerate(sorted(serve)):
        a = azioni_dichiarate(fatti(cik))
        if len(a):
            pezzi.append(a.assign(cik=cik))
        if k % 100 == 99:
            print(f"fatti {k + 1} su {len(serve)}", flush=True)
    a = pd.concat(pezzi)[["cik", "fine", "deposito", "numero", "azioni"]]
    a.to_csv(QUI / "P039_azioni.csv.gz", index=False)
    print(f"simboli dell'indice {len(simboli)}; righe di codici {len(c)}; (membro, mese) senza codice {senza}; aziende {len(serve)}, "
          f"con le azioni {a['cik'].nunique()}; righe di azioni {len(a)}")


if __name__ == "__main__":
    main()
