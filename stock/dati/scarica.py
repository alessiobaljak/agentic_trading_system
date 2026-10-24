"""Scarica i prezzi da Alpaca, li tiene in locale (fuori dal repository) e li controlla.

    python -m stock.dati.scarica SPY QQQ AAPL --dal 2016-01-01 --al 2024-12-31 [--minuti] [--scarto]
        [--esito stock/dati/ESITO_CONTROLLI.md]

L'esito scritto contiene solo i conteggi e le date dei problemi, MAI i prezzi (la licenza dei dati
di borsa di regola non permette di ripubblicarli; il repository è pubblico).
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

import pandas as pd

from stock.dati import alpaca, archivio, controlli, scarto

NY = "America/New_York"


def _utc(d: str, fine: bool = False) -> datetime:
    t = datetime.fromisoformat(d).replace(tzinfo=timezone.utc)
    return t + timedelta(days=1) if fine else t


def scarica_titolo(simbolo: str, dal: str, al: str, minuti: bool, cartella=None) -> dict:
    i, f = _utc(dal), _utc(al, fine=True)
    out = {}
    for rett in ("raw", "split", "all"):
        df = alpaca.barre(simbolo, "1Day", i, f, rettifica=rett)
        archivio.salva(df, simbolo, f"1Day_{rett}", cartella)
        out[rett] = df
    out["azioni"] = alpaca.azioni_societarie(simbolo, i, f)
    archivio.salva(out["azioni"], simbolo, "azioni", cartella)
    if minuti:
        df = alpaca.barre(simbolo, "1Min", i, f, rettifica="raw")
        archivio.salva(df, simbolo, "1Min_raw", cartella)
        out["minuti"] = df
    return out


def misura_scarto(simbolo: str, cal: pd.DataFrame, orari=("10:00", "12:30", "15:30"), durata_min: int = 5) -> dict:
    """Lo scarto sul primo giorno di borsa di ogni trimestre, in tre finestre di `durata_min` minuti
    (mattina, mezzogiorno, ultima mezz'ora)."""
    giorni = pd.Series(list(cal.index), index=pd.to_datetime(list(cal.index)))
    primi = giorni.groupby(giorni.index.to_period("Q")).first()
    pezzi = []
    for d in primi:
        for o in orari:
            t0 = pd.Timestamp(f"{d} {o}", tz=NY)
            if t0 >= cal.loc[d, "chiusura"]:
                continue
            q = alpaca.quotazioni(simbolo, t0.tz_convert("UTC").to_pydatetime(),
                                  (t0 + pd.Timedelta(minutes=durata_min)).tz_convert("UTC").to_pydatetime())
            pezzi.append(q)
    q = pd.concat(pezzi) if pezzi else pd.DataFrame(columns=["bid", "ask"])
    m = scarto.misura(q)
    m["giorni"] = int(len(primi))
    return m


def controlla_titolo(simbolo: str, dati: dict, cal: pd.DataFrame) -> dict:
    raw, az = dati["raw"], dati["azioni"]
    r = {
        "barre_giorno": int(len(raw)),
        "frazionamenti": int((az["tipo"] == "frazionamento").sum()) if not az.empty else 0,
        "dividendi": int((az["tipo"] == "dividendo").sum()) if not az.empty else 0,
        "problemi": {
            "barre": controlli.controlla_barre(raw),
            "giorni": controlli.controlla_giorni(raw, cal),
            "salti": controlli.controlla_salti(raw, az),
            "rettifica frazionamenti": controlli.controlla_rettifica(raw, dati["split"], az, dividendi=False),
            "rettifica dividendi": controlli.controlla_rettifica(raw, dati["all"], az),
            "cadenza dividendi": controlli.controlla_cadenza_dividendi(az),
        },
    }
    if "minuti" in dati:
        p, riep = controlli.controlla_minuti(dati["minuti"], cal)
        r["problemi"]["minuti"] = controlli.controlla_barre(dati["minuti"]) + p
        r["minuti"] = riep
    return r


def esito_markdown(esiti: dict, dal: str, al: str, quando: str) -> str:
    righe = [f"# L'esito dei controlli dei prezzi", "",
             f"Scritto da `python -m stock.dati.scarica` il {quando}, prezzi di Alpaca (tutte le borse americane, "
             f"feed «sip») dal {dal} al {al}. Solo conteggi e date: i prezzi restano in locale.", "",
             "| Titolo | Barre al giorno | Frazionamenti | Dividendi | Problemi | Barre al minuto (dentro / fuori seduta) | Scarto mediano (90° perc.) |",
             "|---|---|---|---|---|---|---|"]
    for s, e in esiti.items():
        n = sum(len(v) for v in e["problemi"].values())
        mi = e.get("minuti")
        sc = e.get("scarto")
        sc_txt = (f"{sc['mediana'] * 1e4:.2f} ({sc['p90'] * 1e4:.2f}) punti base su {sc['fotografie']} fotografie"
                  if sc and sc.get("mediana") is not None else "—")
        righe.append(f"| {s} | {e['barre_giorno']} | {e['frazionamenti']} | {e['dividendi']} | {n} | "
                     f"{f'{mi['dentro']} / {mi['fuori']}' if mi else '—'} | {sc_txt} |")
    righe += ["", "## I problemi trovati", ""]
    for s, e in esiti.items():
        for k, v in e["problemi"].items():
            if not v:
                continue
            righe.append(f"**{s}, {k}** ({len(v)}):")
            for p in v[:15]:
                righe.append(f"* {p['quando']}: {p['controllo']} — {p['dettaglio']}")
            if len(v) > 15:
                righe.append(f"* … e altri {len(v) - 15}")
            righe.append("")
    if all(not v for e in esiti.values() for v in e["problemi"].values()):
        righe.append("Nessuno.")
    return "\n".join(righe) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("simboli", nargs="+")
    ap.add_argument("--dal", default="2016-01-01")
    ap.add_argument("--al", default="2024-12-31")
    ap.add_argument("--minuti", action="store_true")
    ap.add_argument("--scarto", action="store_true")
    ap.add_argument("--esito")
    a = ap.parse_args(argv)
    cal = alpaca.calendario(a.dal, a.al)
    esiti = {}
    for s in a.simboli:
        print(f"{s}: scarico", flush=True)
        dati = scarica_titolo(s, a.dal, a.al, a.minuti)
        esiti[s] = controlla_titolo(s, dati, cal)
        if a.scarto:
            esiti[s]["scarto"] = misura_scarto(s, cal)
        n = sum(len(v) for v in esiti[s]["problemi"].values())
        print(f"{s}: {esiti[s]['barre_giorno']} barre al giorno, {n} problemi", flush=True)
    testo = esito_markdown(esiti, a.dal, a.al, datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
    if a.esito:
        with open(a.esito, "w") as fh:
            fh.write(testo)
    print(testo)


if __name__ == "__main__":
    main()
