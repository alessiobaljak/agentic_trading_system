"""I dati della prova 20: codici SEC dei titoli dell'S&P 500, date dei comunicati sui risultati, barre al minuto dei soli giorni
degli eventi (il giorno del deposito e quello dopo).

    python -m stock.dati.eventi_minuti codici            # stock/universo/codici_sec.csv
    python -m stock.dati.eventi_minuti date              # ~/stock_dati/eventi/comunicati.csv
    python -m stock.dati.eventi_minuti minuti PARTE PARTI   # ~/stock_dati/eventi/minuti/AAAA-MM-GG.csv.gz
"""
from __future__ import annotations

import bisect
import sys
from datetime import date, datetime, timedelta, timezone

import pandas as pd

from stock.dati import alpaca, bilanci
from stock.dati.archivio import cartella_dati
from stock.dati.dirigenti import cartella as cartella_form345
from stock.universo.costruisci import QUI as CARTELLA_UNIVERSO
from stock.universo.costruisci import cambi_di_nome, carica_composizione

NY = "America/New_York"


def membri_e_periodi():
    """Per ogni simbolo (con i cambi di nome), il primo e l'ultimo giorno nell'S&P 500 fra il 2016 e il 2024."""
    from pathlib import Path
    comp = carica_composizione(Path.home() / "stock_dati" / "sp500_storico.csv")
    cambi = cambi_di_nome()
    periodi: dict[str, list[date]] = {}
    for d, m in comp:
        if date(2015, 12, 1) <= d <= date(2024, 12, 31):
            for t in m:
                periodi.setdefault(t, [d, d])[1] = d
                periodi[t][0] = min(periodi[t][0], d)
    return periodi, cambi


def codici():
    """Il codice SEC di ogni simbolo: fra i codici che i moduli dei dirigenti associano al simbolo, quello con più moduli depositati
    mentre il simbolo era nell'indice."""
    periodi, _ = membri_e_periodi()
    pezzi = []
    for p in sorted(cartella_form345().iterdir()):
        s = pd.read_csv(p / "SUBMISSION.tsv", sep="\t", dtype=str, usecols=["FILING_DATE", "ISSUERCIK", "ISSUERTRADINGSYMBOL"])
        pezzi.append(s)
    s = pd.concat(pezzi)
    s["simbolo"] = s["ISSUERTRADINGSYMBOL"].str.upper().str.strip().str.replace("-", ".", regex=False)
    s["data"] = pd.to_datetime(s["FILING_DATE"], format="%d-%b-%Y").dt.date
    s = s[s["simbolo"].isin(periodi)]
    s = s[[periodi[t][0] <= d <= periodi[t][1] for t, d in zip(s["simbolo"], s["data"])]]
    m = s.groupby(["simbolo", "ISSUERCIK"]).size().reset_index(name="moduli").sort_values("moduli", ascending=False)
    m = m.drop_duplicates("simbolo").sort_values("simbolo")
    m["cik"] = m["ISSUERCIK"].astype(int)
    m[["simbolo", "cik", "moduli"]].to_csv(CARTELLA_UNIVERSO / "codici_sec.csv", index=False)
    print(len(m), "simboli con codice su", len(periodi))


def date_dei_comunicati():
    m = pd.read_csv(CARTELLA_UNIVERSO / "codici_sec.csv")
    _, cambi = membri_e_periodi()
    righe = []
    for s, c in zip(m["simbolo"], m["cik"]):
        _, giorni = bilanci.comunicati_del_simbolo(s, int(c))
        for d in bilanci.un_evento_per_trimestre([g for g in giorni if date(2016, 1, 1) <= g <= date(2024, 12, 31)]):
            righe.append({"simbolo": cambi.get(s, s), "simbolo_allora": s, "deposito": d})
    out = cartella_dati() / "eventi"
    out.mkdir(exist_ok=True)
    pd.DataFrame(righe).to_csv(out / "comunicati.csv", index=False)
    print(len(righe), "comunicati")


def minuti(parte: int, parti: int):
    """Per ogni giorno di borsa, le barre al minuto (seduta 9:30-16:00) dei titoli con un comunicato depositato quel giorno o il
    giorno di borsa prima (il giorno della reazione può essere l'uno o l'altro)."""
    cal = sorted(alpaca.calendario("2016-01-01", "2024-12-31").index)
    ev = pd.read_csv(cartella_dati() / "eventi" / "comunicati.csv", parse_dates=["deposito"])
    per_giorno: dict[date, set] = {}
    for s, d in zip(ev["simbolo"], ev["deposito"].dt.date):
        k = bisect.bisect_left(cal, d)
        for j in (k, k + 1):
            if j < len(cal):
                per_giorno.setdefault(cal[j], set()).add(s)
    out = cartella_dati() / "eventi" / "minuti"
    out.mkdir(parents=True, exist_ok=True)
    giorni = sorted(per_giorno)
    for i, g in enumerate(giorni):
        if i % parti != parte:
            continue
        f = out / f"{g}.csv.gz"
        if f.exists():
            continue
        t0 = pd.Timestamp(f"{g} 09:30", tz=NY).tz_convert("UTC").to_pydatetime()
        t1 = pd.Timestamp(f"{g} 16:00", tz=NY).tz_convert("UTC").to_pydatetime()
        simboli = sorted(per_giorno[g] | {"SPY"})
        pezzi = []
        for k in range(0, len(simboli), 50):
            for s, df in alpaca.barre_di_piu(simboli[k:k + 50], "1Min", t0, t1).items():
                if not df.empty:
                    pezzi.append(df.assign(simbolo=s))
        if pezzi:
            pd.concat(pezzi).to_csv(f, compression="gzip")
        if i % 200 == parte:
            print(parte, i, len(giorni), flush=True)
    print("FINE", parte, flush=True)


if __name__ == "__main__":
    {"codici": lambda: codici(), "date": lambda: date_dei_comunicati(),
     "minuti": lambda: minuti(int(sys.argv[2]), int(sys.argv[3]))}[sys.argv[1]]()
