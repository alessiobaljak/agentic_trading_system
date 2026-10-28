"""Programma 7, cinquantottesima prova (CINQUANTOTTESIMA.md): ST, il Bitcoin dopo gli acquisti annunciati da Strategy. Eventi: i moduli
8-K (EDGAR) con «acquired approximately N bitcoin(s)»; short il perpetuo del Bitcoin 5 minuti dopo l'accettazione della SEC, per 24 ore.

Uso: python3 -m research.programma7.cinquantottesima
"""
from __future__ import annotations

import json
import re
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import seconda as sc
from research.programma6 import trentesima as tr
from research.trader_copiati.analisi_trader2 import minuti

QUI = Path(__file__).parent
RADICE = QUI.parents[1]
RIS = QUI / "risultati_cinquantottesima"
DATI = RADICE / "research" / "data" / "sec_strategy"
CIK = "0001050446"
UA = {"User-Agent": "ricerca agentic-trading-system"}
FRASE = re.compile(r"acquired\s+(?:an\s+aggregate\s+of\s+)?approximately\s+[\d,]+\s+bitcoins?", re.I)
DAL = "2020-08-01"
RITARDO, DURATA = 5, 1440
PROVE_A_EVENTI = 36


def _get(url: str, testo: bool = False):
    for k in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                b = r.read()
            time.sleep(0.15)
            return b.decode("utf-8", errors="ignore") if testo else json.loads(b)
        except Exception:  # noqa: BLE001
            time.sleep(2 * (k + 1))
    return None


def moduli() -> list:
    """[(accettazione UTC, numero, documento)] dei moduli 8-K dal 2020-08."""
    d = _get(f"https://data.sec.gov/submissions/CIK{CIK}.json")
    blocchi = [d["filings"]["recent"]] + [_get(f"https://data.sec.gov/submissions/{f['name']}") for f in d["filings"].get("files", [])]
    out = []
    for b in blocchi:
        if not b:
            continue
        for i in range(len(b["form"])):
            if b["form"][i] == "8-K" and b["filingDate"][i] >= DAL:
                out.append((b["acceptanceDateTime"][i], b["accessionNumber"][i], b["primaryDocument"][i]))
    return sorted(set(out))


def testo(numero: str, documento: str) -> str:
    f = DATI / f"{numero}.txt"
    if f.exists():
        return f.read_text(encoding="utf-8")
    html = _get(f"https://www.sec.gov/Archives/edgar/data/{int(CIK)}/{numero.replace('-', '')}/{documento}", testo=True) or ""
    t = re.sub(r"<[^>]+>", " ", html)
    t = re.sub(r"&#160;|&nbsp;", " ", t)
    t = re.sub(r"\s+", " ", t)
    DATI.mkdir(parents=True, exist_ok=True)
    f.write_text(t, encoding="utf-8")
    return t


def minuto_utc(s: str) -> int:
    return int(datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc).timestamp() // 60)


def serie_btc(da: int, a: int) -> pd.DataFrame:
    parti = [minuti("BTCUSDT", sc.data(g)) for g in range(da // 1440, a // 1440 + 1)]
    parti = [p for p in parti if not p.empty]
    return pd.concat(parti).sort_index() if parti else pd.DataFrame()


def ritorno(e: int, durata: int) -> float:
    w = serie_btc(e, e + durata)
    if w.empty or e not in w.index or (e + durata) not in w.index:
        return np.nan
    return float(w.loc[e + durata, "open"] / w.loc[e, "open"] - 1)


def esegui(log=print) -> dict:
    pan = sc.pannello()
    j = pan["simboli"].index("BTCUSDT")
    costo = float(sc.costi_moneta(["BTCUSDT"])[0])
    mod = moduli()
    log(f"[cinquantottesima] {len(mod)} moduli 8-K dal 2020-08; leggo i testi")
    ev = [(minuto_utc(a), a, n) for a, n, doc in mod if FRASE.search(testo(n, doc))]
    ev = sorted(ev)
    giorni_ev = {m // 1440 for m, _, _ in ev}
    log(f"[cinquantottesima] {len(ev)} comunicazioni di acquisto")

    def operazione(m: int) -> dict | None:
        e = m + RITARDO
        r = ritorno(e, DURATA)
        if not np.isfinite(r):
            return None
        k = e // 1440 - pan["t0"]
        f = float(np.nan_to_num(pan["funding"][k, j])) if 0 <= k < pan["funding"].shape[0] else 0.0
        return {"data": sc.data(e // 1440), "annuncio": int((e // 1440 + 3) // 7), "r": -r - 2 * costo + f, "btc_24h": r}

    righe = []
    for m, a, n in ev:
        op = operazione(m)
        if op is None:
            continue
        prima = ritorno(m - DURATA, DURATA)
        righe.append({**op, "accettazione": a, "modulo": n, "giorno_settimana": datetime.fromtimestamp(m * 60, timezone.utc).weekday(),
                      "btc_24h_prima": prima, "btc_1h": ritorno(m + RITARDO, 60), "btc_4h": ritorno(m + RITARDO, 240)})
    df = pd.DataFrame(righe)
    rng = np.random.default_rng(2026)
    caso = []
    for m, _, _ in ev:
        candidati = [m - 7 * 1440 * w for w in range(4, 53) if (m - 7 * 1440 * w) // 1440 not in giorni_ev]
        scelti = list(rng.choice(candidati, size=min(5, len(candidati)), replace=False)) if candidati else []
        if not scelti:
            altri = [m + 1440 * d for d in range(-365, 366) if (m + 1440 * d) // 1440 not in giorni_ev]
            scelti = list(rng.choice(altri, size=min(5, len(altri)), replace=False))
        for t in scelti:
            op = operazione(int(t))
            if op:
                caso.append(op)
    dc = pd.DataFrame(caso)
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "eventi_ST.csv", index=False)
    dc.to_csv(RIS / "controllo.csv", index=False)
    ex_ = tr.esame(df, "r")
    out = {"moduli": len(mod), "eventi": len(df), "esame": ex_,
           "controllo": {"operazioni": len(dc), "media": float(dc["r"].mean()) if len(dc) else None},
           "btc_24h_prima": float(df["btc_24h_prima"].mean()), "btc_1h": float(df["btc_1h"].mean()), "btc_4h": float(df["btc_4h"].mean()),
           "btc_24h": float(df["btc_24h"].mean()), "lunedi": float((df["giorno_settimana"] == 0).mean()),
           "soglia_tutte": 0.01 / PROVE_A_EVENTI}
    sopra = out["controllo"]["media"] is not None and ex_["boot"]["media"] > out["controllo"]["media"]
    out["esito"] = ("VALIDA" if ex_["esito"] == "VALIDA" and sopra and ex_["boot"]["p"] <= out["soglia_tutte"] else
                    "passa l'esame scritto (p ≤ 0,01) ma non la soglia di tutte le prove a eventi" if ex_["esito"] == "VALIDA" and sopra else
                    "non sopra il controllo" if ex_["esito"] == "VALIDA" else ex_["esito"])
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    b = ex_["boot"]
    testo_ = "\n".join([
        "# Programma 7 — risultati della cinquantottesima prova (ST: il Bitcoin dopo gli acquisti annunciati da Strategy)", "",
        "Regole in `CINQUANTOTTESIMA.md` (scritte prima). Moduli 8-K di Strategy (EDGAR), candele a 1 minuto di Binance.", "",
        f"* {out['moduli']} moduli 8-K dall'agosto 2020; **{out['eventi']} comunicazioni di acquisto** (il {100 * out['lunedi']:.0f}% di lunedì).",
        f"* **Short il Bitcoin per 24 ore: {100 * b['media']:+.2f}% a evento** dopo i costi (intervallo {100 * b['basso']:+.2f}%; "
        f"{100 * b['alto']:+.2f}%, p {b['p']:.4f}); mediana {100 * ex_['mediana']:+.2f}%, vinte {100 * ex_['vinti']:.0f}%; metà "
        f"{100 * ex_['prima_meta']:+.2f}% e {100 * ex_['seconda_meta']:+.2f}%; senza le 5 migliori {100 * ex_['senza_5_migliori']:+.2f}%.",
        f"* **Il controllo** (stessa ora, stesso giorno della settimana, settimane senza annunci): {out['controllo']['operazioni']} operazioni, "
        f"{100 * (out['controllo']['media'] or 0):+.2f}%.",
        "* Per anno: " + ", ".join(f"{a} {100 * v['media']:+.2f}% ({v['eventi']})" for a, v in ex_["per_anno"].items()) + ".",
        f"* Il Bitcoin nelle 24 ore prima dell'annuncio {100 * out['btc_24h_prima']:+.2f}%; dopo: 1 ora {100 * out['btc_1h']:+.2f}%, 4 ore "
        f"{100 * out['btc_4h']:+.2f}%, 24 ore {100 * out['btc_24h']:+.2f}%.", "",
        f"**Esito: {out['esito']}** (soglia contando le {PROVE_A_EVENTI} prove a eventi: {out['soglia_tutte']:.5f})."]) + "\n"
    (QUI / "RISULTATI_CINQUANTOTTESIMA.md").write_text(testo_, encoding="utf-8")
    log(testo_)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("CINQUANTOTTESIMA FINITA", flush=True)
