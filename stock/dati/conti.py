"""I conti delle aziende dalla SEC (prova 31): l'utile lordo, i ricavi, il costo del venduto e il totale dei beni.

    python -m stock.dati.conti          # scarica le cornici in ~/stock_dati/sec/cornici e scrive stock/prove/dati/P031_redditivita.csv.gz

Fonte: le «cornici» di https://data.sec.gov/api/xbrl/frames/us-gaap/<voce>/USD/CY<anno>.json (un valore annuale per azienda, il
periodo che meglio coincide con l'anno solare) e .../CY<anno>Q<n>I.json (un valore istantaneo per azienda, alla fine del trimestre più
vicino). Sono gli ultimi valori depositati (un bilancio corretto dopo si vede corretto). Dati pubblici della SEC: nel repository va solo
la redditività calcolata per azienda ed esercizio.
"""
from __future__ import annotations

import json
import time
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import requests

from stock.dati.archivio import cartella_dati

UA = {"User-Agent": "agentic-trading-system research"}
URL = "https://data.sec.gov/api/xbrl/frames/us-gaap/{voce}/USD/{periodo}.json"
ANNI = range(2013, 2026)
UTILE = "GrossProfit"
RICAVI = ("Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet",
          "RevenueFromContractWithCustomerIncludingAssessedTax")
COSTO = ("CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold",
         "CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization")
BENI = "Assets"
GIORNI_PRIMA = 31
QUI = Path(__file__).resolve().parent


def cartella() -> Path:
    p = cartella_dati() / "sec" / "cornici"
    p.mkdir(parents=True, exist_ok=True)
    return p


def cornice(voce: str, periodo: str) -> list[dict]:
    """I valori di una voce per un periodo (CY2019 annuale, CY2019Q4I istantaneo); lista vuota se la SEC non ha la cornice."""
    f = cartella() / f"{voce}_{periodo}.json"
    if not f.exists():
        for prova in range(4):
            r = requests.get(URL.format(voce=voce, periodo=periodo), headers=UA, timeout=60)
            if r.status_code == 404:
                f.write_text("[]")
                break
            if r.status_code == 200:
                f.write_text(json.dumps(r.json().get("data", [])))
                break
            time.sleep(2 * (prova + 1))
        else:
            raise RuntimeError(f"SEC {voce} {periodo}: {r.status_code}")
        time.sleep(0.15)
    return json.loads(f.read_text())


def annuali(voce: str) -> dict[int, list[tuple[date, float]]]:
    """Codice SEC -> [(fine dell'esercizio, valore)] da tutte le cornici annuali."""
    out: dict[int, list[tuple[date, float]]] = {}
    for a in ANNI:
        for x in cornice(voce, f"CY{a}"):
            out.setdefault(int(x["cik"]), []).append((date.fromisoformat(x["end"]), float(x["val"])))
    return out


def istantanei(voce: str) -> dict[int, dict[date, float]]:
    out: dict[int, dict[date, float]] = {}
    for a in ANNI:
        for q in range(1, 5):
            for x in cornice(voce, f"CY{a}Q{q}I"):
                out.setdefault(int(x["cik"]), {})[date.fromisoformat(x["end"])] = float(x["val"])
    return out


def utile_lordo(cik: int, utile, ricavi, costi) -> dict[date, tuple[float, str]]:
    """Fine dell'esercizio -> (utile lordo, voce usata): `GrossProfit` se c'è; altrimenti la prima voce dei ricavi presente meno la
    prima voce del costo presente con la stessa data di fine."""
    out = {fine: (v, UTILE) for fine, v in utile.get(cik, [])}
    for nome_r in RICAVI:
        for fine, r in ricavi[nome_r].get(cik, []):
            if fine in out:
                continue
            for nome_c in COSTO:
                c = dict(costi[nome_c].get(cik, [])).get(fine)
                if c is not None:
                    out[fine] = (r - c, f"{nome_r}-{nome_c}")
                    break
    return out


def beni_a(fine: date, beni: dict[date, float]) -> float | None:
    if fine in beni:
        return beni[fine]
    prima = [d for d in beni if fine - timedelta(days=GIORNI_PRIMA) <= d < fine]
    return beni[max(prima)] if prima else None


def settore(cik: int) -> int | None:
    """Il codice SIC dalla SEC (dal file già scaricato per la prova 20, o scaricato ora)."""
    f = cartella_dati() / "sec" / f"CIK{cik:010d}.json"
    if not f.exists():
        r = requests.get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json", headers=UA, timeout=60)
        time.sleep(0.15)
        if r.status_code != 200:
            return None
        f.write_text(r.text)
    s = json.loads(f.read_text()).get("sic")
    return int(s) if s and str(s).isdigit() else None


def costruisci(ciks: list[int]) -> pd.DataFrame:
    utile = annuali(UTILE)
    ricavi = {v: annuali(v) for v in RICAVI}
    costi = {v: annuali(v) for v in COSTO}
    beni = istantanei(BENI)
    righe = []
    for cik in ciks:
        sic = settore(cik)
        esercizi = sorted(utile_lordo(cik, utile, ricavi, costi).items())
        if not esercizi:       # una riga senza esercizio: serve a sapere il settore (finanziarie) anche di chi non ha l'utile lordo
            righe.append({"cik": cik, "fine": None, "sic": sic, "utile_lordo": None, "beni": None, "voce": None, "redditivita": None})
        for fine, (u, voce) in esercizi:
            b = beni_a(fine, beni.get(cik, {}))
            righe.append({"cik": cik, "fine": fine, "sic": sic, "utile_lordo": u, "beni": b, "voce": voce,
                          "redditivita": u / b if b and b > 0 else None})
    return pd.DataFrame(righe)


def main():
    ciks = sorted(set(pd.read_csv(QUI.parent / "universo" / "codici_sec.csv")["cik"].astype(int)))
    df = costruisci(ciks)
    out = QUI.parent / "prove" / "dati" / "P031_redditivita.csv.gz"
    df.to_csv(out, index=False)
    print(f"{df['fine'].notna().sum()} esercizi di {df.dropna(subset=['fine'])['cik'].nunique()} aziende su {len(ciks)}; con la redditività {df['redditivita'].notna().sum()}; "
          f"voci: {df['voce'].value_counts().head(4).to_dict()}")


if __name__ == "__main__":
    main()
