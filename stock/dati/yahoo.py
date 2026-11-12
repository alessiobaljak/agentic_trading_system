"""La seconda fonte per dividendi e frazionamenti: Yahoo (solo gli eventi, non i prezzi).

    python -m stock.dati.yahoo SPY QQQ ... --esito stock/dati/ESITO_DIVIDENDI.md

Confronta con le azioni societarie di Alpaca già scaricate (`stock.dati.scarica`) e scrive le
differenze. Yahoo divide gli importi per i frazionamenti successivi: il confronto li riporta a quelli
di allora (`integrazioni.confronta_dividendi`).
"""
from __future__ import annotations

import argparse
import time
from datetime import UTC, datetime

import requests

from stock.dati import archivio
from stock.dati.integrazioni import DIVIDENDI_AGGIUNTI, confronta_dividendi

URL = "https://query1.finance.yahoo.com/v8/finance/chart/{s}"


def eventi(simbolo: str, dal: str, al: str) -> tuple[dict, dict]:
    """(dividendi, frazionamenti) di Yahoo per giorno di stacco. Il simbolo con il punto (BRK.B) per
    Yahoo si scrive col trattino."""
    p1 = int(datetime.fromisoformat(dal).replace(tzinfo=UTC).timestamp())
    p2 = int(datetime.fromisoformat(al).replace(tzinfo=UTC).timestamp()) + 86400
    for n in range(4):
        r = requests.get(URL.format(s=simbolo.replace(".", "-")), timeout=30, headers={"User-Agent": "Mozilla/5.0"},
                         params={"period1": p1, "period2": p2, "interval": "1mo", "events": "div|split"})
        if r.status_code == 200:
            break
        time.sleep(2 ** (n + 1))
    r.raise_for_status()
    ev = r.json()["chart"]["result"][0].get("events", {})
    giorno = lambda v: datetime.fromtimestamp(v["date"], UTC).date()  # noqa: E731
    div = {giorno(v): float(v["amount"]) for v in ev.get("dividends", {}).values()}
    fr = {giorno(v): v["numerator"] / v["denominator"] for v in ev.get("splits", {}).values()}
    return div, fr


def prezzi(simbolo: str, dal: str, al: str):
    """Le barre al giorno di Yahoo come scambiate (open, high, low, close, volume), la chiusura rettificata per dividendi e
    frazionamenti (`rettificata`) e il dividendo sul giorno di stacco. Per i fondi quotati delle prove senza le chiavi di Alpaca
    (`stock/prove/P026_tendenza_altre_classi.md`). I prezzi restano fuori dal repository."""
    import pandas as pd
    p1 = int(datetime.fromisoformat(dal).replace(tzinfo=UTC).timestamp())
    p2 = int(datetime.fromisoformat(al).replace(tzinfo=UTC).timestamp()) + 86400
    for n in range(4):
        r = requests.get(URL.format(s=simbolo.replace(".", "-")), timeout=30, headers={"User-Agent": "Mozilla/5.0"},
                         params={"period1": p1, "period2": p2, "interval": "1d", "events": "div|split"})
        if r.status_code == 200:
            break
        time.sleep(2 ** (n + 1))
    r.raise_for_status()
    ris = r.json()["chart"]["result"][0]
    q = ris["indicators"]["quote"][0]
    # l'ora di Yahoo è l'apertura di New York: l'indice è il giorno di New York, a mezzogiorno UTC (come giorno, non come ora)
    giorni = pd.to_datetime(ris["timestamp"], unit="s", utc=True).tz_convert("America/New_York").normalize()
    df = pd.DataFrame({c: q[c] for c in ("open", "high", "low", "close", "volume")}, index=giorni)
    df["rettificata"] = ris["indicators"]["adjclose"][0]["adjclose"]
    ev = ris.get("events", {})
    div = {pd.Timestamp(v["date"], unit="s", tz="UTC").tz_convert("America/New_York").normalize(): float(v["amount"])
           for v in ev.get("dividends", {}).values()}
    df["dividendo"] = [div.get(g, 0.0) for g in df.index]
    df["frazionamento"] = 1.0
    if ev.get("splits"):
        raise ValueError(f"{simbolo}: frazionamenti nel periodo, i prezzi di Yahoo non sono quelli scambiati")
    return df.dropna(subset=["open", "close"])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("simboli", nargs="+")
    ap.add_argument("--dal", default="2016-01-01")
    ap.add_argument("--al", default="2024-12-31")
    ap.add_argument("--esito")
    a = ap.parse_args(argv)
    righe = ["# Dividendi e frazionamenti: Alpaca contro Yahoo", "",
             f"Scritto da `python -m stock.dati.yahoo` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC, dal {a.dal} al {a.al}. "
             "Gli importi di Yahoo sono riportati a quelli di allora (moltiplicati per i frazionamenti successivi); "
             "tolleranza 1%.", "",
             "| Titolo | Dividendi Alpaca | Dividendi Yahoo | Frazionamenti uguali | Differenze |", "|---|---|---|---|---|"]
    dettagli = []
    for s in a.simboli:
        nostri = archivio.carica(s, "azioni")
        div, fr = eventi(s, a.dal, a.al)
        nostri_fr = dict(zip(nostri.loc[nostri.tipo == "frazionamento", "data"], nostri.loc[nostri.tipo == "frazionamento", "rapporto"]))
        diff = confronta_dividendi(nostri, div, fr)
        n_al = int((nostri.tipo == "dividendo").sum())
        righe.append(f"| {s} | {n_al} | {len(div)} | {'sì' if nostri_fr == fr else 'NO'} | {len(diff)} |")
        for d in diff:
            agg = any(x[0] == d["data"] for x in DIVIDENDI_AGGIUNTI.get(s, []))
            f = lambda x: "—" if x is None else f"{x:.4f}"  # noqa: E731
            dettagli.append(f"* {s}, {d['data']}: {d['tipo']} (Alpaca {f(d['nostro'])}, Yahoo {f(d['altro'])})"
                            + (" → aggiunto a mano (`integrazioni.py`)" if agg else ""))
        time.sleep(1)
    righe += ["", "## Le differenze", ""] + (dettagli or ["Nessuna."])
    testo = "\n".join(righe) + "\n"
    if a.esito:
        open(a.esito, "w").write(testo)
    print(testo)


if __name__ == "__main__":
    main()
