"""Misura descrittiva per l'idea 102 (non una prova, non entra nel conto, non guarda i rendimenti di nessuna regola): quando il perpetuo
scende molto sotto il prezzo a pronti (l'indice del premio di Binance, candele orarie dell'archivio pubblico), in quante ore il buco si
chiude. Eventi: un'ora che chiude con il premio a −1% o sotto, dopo un'ora sopra −0,5%, al massimo uno ogni 24 ore per moneta, sulle monete
dell'universo di G1 nelle settimane in cui ci sono, dal gennaio 2024 al settembre 2026.

Uso: python3 -m research.programma7.buco_perpetuo
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma5.strumenti import motore5 as m5
from research.programma6 import scarico_giorni as sg
from research.programma6 import seconda as sc
from research.programma6 import terza as te

QUI = Path(__file__).parent
DATI = QUI.parent / "data" / "premio_indice"
DAL, AL = sc.giorno(2024, 1, 1), sc.giorno(2026, 10, 1)
SOGLIA, PRIMA, CHIUSO, DOPO = -0.01, -0.005, -0.0025, (1, 2, 4, 8, 24)


def mesi(g0: int, g1: int) -> list:
    return sorted({sc.data(g)[:7] for g in range(g0, g1)})


def premio_ore(s: str) -> pd.Series:
    file = sorted((DATI / s).glob("*.zip"))
    if not file:
        return pd.Series(dtype=float)
    df = pd.concat([m5._csv_da_zip(p, m5.KLINE) for p in file], ignore_index=True)
    df["ora"] = m5._ms(df["open_time"]) // 3_600_000
    df = df.drop_duplicates("ora", keep="last").set_index("ora").sort_index()
    return df["close"].astype(float)


def main() -> None:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    lun, U = ps["lunedi"], ps["U"]
    k = (lun >= DAL) & (lun < AL)
    lavori, settimane = [], {}
    for j, s in enumerate(ps["simboli"]):
        w = lun[k][U[k, j]]
        if len(w):
            settimane[s] = set(int(x) for x in w)
            for m in mesi(int(w.min()), int(w.max()) + 7):
                lavori.append((s, m))
    print(f"[buco] {len(settimane)} monete, {len(lavori)} file mensili", flush=True)

    def uno(x):
        s, m = x
        try:
            sg._scarica(f"data/futures/um/monthly/premiumIndexKlines/{s}/1h/{s}-1h-{m}.zip", DATI / s)
        except Exception:  # noqa: BLE001
            pass
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(uno, lavori))
    righe = []
    for s, sw in settimane.items():
        p = premio_ore(s)
        if p.empty:
            continue
        ultimo = -10 ** 9
        for h in p.index[(p.to_numpy() <= SOGLIA)]:
            g = int(h // 24)
            lun_h = g - ((g + 3) % 7)
            if lun_h not in sw or h - ultimo < 24 or (h - 1) not in p.index or not p.loc[h - 1] > PRIMA:
                continue
            ultimo = h
            r = {"moneta": s, "ora": int(h), "data": sc.data(g), "premio": float(p.loc[h])}
            for d in DOPO:
                r[f"h{d}"] = float(p.loc[h + d]) if (h + d) in p.index else np.nan
            righe.append(r)
    d = pd.DataFrame(righe)
    d.to_csv(QUI / "risultati_buco_perpetuo.csv", index=False)
    testo = ["# Il buco fra il perpetuo e il pronti nei crolli: in quante ore si chiude (misura descrittiva, idea 102)", "",
             "Script `buco_perpetuo.py`. L'indice del premio di Binance (il perpetuo rispetto al prezzo a pronti) a 1 ora, dall'archivio "
             "pubblico, sulle monete dell'universo di G1 nelle loro settimane, dal gennaio 2024 al settembre 2026. Evento: un'ora che chiude "
             "con il premio a −1% o sotto dopo un'ora sopra −0,5%, al massimo uno ogni 24 ore per moneta. Non guarda nessun rendimento: non "
             "è una prova e non entra nel conto.", "",
             f"* **{len(d)} eventi** su {d['moneta'].nunique() if len(d) else 0} monete; premio all'evento, mediana "
             f"{100 * d['premio'].median():.2f}% (il 10% più profondo sotto {100 * d['premio'].quantile(0.1):.2f}%).", "",
             "| Ore dopo | Premio mediano | Buco chiuso (premio sopra −0,25%) |", "|---|---|---|"]
    for h in DOPO:
        x = d[f"h{h}"].dropna()
        testo.append(f"| +{h} | {100 * x.median():.2f}% | {100 * (x > CHIUSO).mean():.0f}% |")
    testo += ["", "Per anno: " + ", ".join(f"{a} {len(g)} eventi, chiuso dopo 1 ora {100 * (g['h1'] > CHIUSO).mean():.0f}%"
                                         for a, g in d.groupby(d['data'].str[:4]))]
    t = "\n".join(testo) + "\n"
    (QUI / "BUCO_PERPETUO.md").write_text(t, encoding="utf-8")
    print(t, flush=True)


if __name__ == "__main__":
    main()
    print("BUCO FINITA", flush=True)
