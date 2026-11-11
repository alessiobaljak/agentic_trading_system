"""Audit della prova 28 (11 novembre 2026), sezione A: i dati usati da K2, F5 e M7 nel periodo della prova.

Solo lettura: importa le funzioni della ricerca, non esegue nessun ``main`` (catalogo, voce 11). Scrive solo
``audits/repro/prova28_dati_2026-11-11_esito.json``.

Uso: python3 audits/repro/prova28_dati_2026-11-11.py
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma5.strumenti import motore5 as m5
from research.programma6 import dodicesima as do
from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import undicesima as un
from research.programma6 import ventiquattresima as vq
from research.src.dati import funding_da_zip

QUI = Path(__file__).parent
DAL = sc.giorno(2021, 12, 1)          # 30 giorni prima del primo lunedi' dell'esame (3 gennaio 2022)


def main() -> dict:
    pan = sc.pannello()
    t0 = pan["t0"]
    T, S = pan["close"].shape
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    pm = un.pannello_metrics(pan)
    lun = ps["lunedi"] - t0
    sig = ot.sigma_30(pan, lun)
    k = do.segnale_k1(pan, ps, pm)
    Wk2 = vq.pesi_banda(np.where(np.isfinite(sig), k, np.nan), ps["U"], sig)
    Wf5 = vq.pesi_banda(np.where(np.isfinite(sig), -se.funding_7(pan, lun), np.nan), ps["U"], sig)
    sett = np.flatnonzero(ps["lunedi"] >= sc.giorno(2022, 1, 3))
    in_u = ps["U"][sett].any(axis=0)
    tenute = ((Wk2[sett] != 0) | (Wf5[sett] != 0)).any(axis=0)
    monete = [ps["simboli"][j] for j in np.flatnonzero(in_u)]
    out = {"pannello": {"primo": sc.data(t0), "ultimo": sc.data(t0 + T - 1), "monete": S},
           "settimane_esame": int(len(sett)), "ultimo_lunedi": sc.data(int(ps["lunedi"][-1])),
           "monete_nell_universo_dal_2022": len(monete), "monete_tenute_K2_o_F5": int(tenute.sum())}

    # 1. buchi fra la prima e l'ultima candela (dal 1 dicembre 2021), sulle monete dell'universo
    C = pan["close"]
    buchi = {}
    for j in np.flatnonzero(in_u):
        ok = np.isfinite(C[:, j])
        a, b = np.flatnonzero(ok)[[0, -1]]
        dentro = np.arange(max(a, DAL - t0), b + 1)
        mancano = dentro[~ok[dentro]]
        if len(mancano):
            buchi[ps["simboli"][j]] = [sc.data(int(g) + t0) for g in mancano][:10]
    out["buchi_universo"] = {"monete": len(buchi), "esempi": dict(list(buchi.items())[:10])}
    g28 = sc.giorno(2026, 10, 28) - t0
    out["28_ottobre_2026"] = {d: int(np.isfinite(C[g28 + d]).sum()) for d in (-1, 0, 1)}

    # 2. valori anomali sulle monete dell'universo, nelle settimane in cui ci sono
    O, H, L, V = pan["open"], pan["high"], pan["low"], pan["quote_volume"]
    giorno_u = np.zeros((T, S), bool)
    for w in sett:
        m = lun[w]
        giorno_u[m: m + 7] |= ps["U"][w]
    with np.errstate(all="ignore"):
        r = C[1:] / C[:-1] - 1
        r = np.vstack([np.full((1, S), np.nan), r])
        alto_basso = (H < L) & giorno_u
        fuori = ((O > H * (1 + 1e-9)) | (O < L * (1 - 1e-9)) | (C > H * (1 + 1e-9)) | (C < L * (1 - 1e-9))) & giorno_u
        non_pos = ((O <= 0) | (C <= 0) | (L <= 0)) & giorno_u
        salti = (np.abs(r) > 0.5) & giorno_u
    elenco_salti = sorted(((float(r[t, j]), ps["simboli"][j], sc.data(t + t0)) for t, j in zip(*np.nonzero(salti))),
                          key=lambda x: -abs(x[0]))
    out["anomali_nell_universo"] = {"massimo_sotto_minimo": int(alto_basso.sum()), "apertura_o_chiusura_fuori": int(fuori.sum()),
                                    "prezzi_non_positivi": int(non_pos.sum()), "giorni_oltre_50%": len(elenco_salti),
                                    "i_piu_grandi": [[round(a, 3), b, c] for a, b, c in elenco_salti[:12]]}

    # 3. monete ferme (volume zero, prezzo uguale) mentre sono tenute da K2 o da F5
    fermi = np.isfinite(C) & (np.nan_to_num(V) == 0)
    tenuti = np.zeros((T, S), bool)
    for w in sett:
        m = lun[w]
        tenuti[m: m + 7] |= (Wk2[w] != 0) | (Wf5[w] != 0)
    out["giorni_fermi_tenuti"] = int((fermi & tenuti).sum())

    # 4. funding: giorni tenuti senza il dato vero (stimato con la media dei 90 giorni o lasciato a zero)
    stimati, zero_in_mese, ore_reg, minuti_fuori, intervalli = Counter(), Counter(), Counter(), 0, Counter()
    duplicati, fuori_ordine, non_mezzanotte = {}, {}, {}
    for j in np.flatnonzero(tenute):
        s = ps["simboli"][j]
        righe = []
        for p in sorted((sc.DATI / s / "funding").glob("*.zip")):
            righe += funding_da_zip(p)
        df = pd.DataFrame(righe, columns=["ts", "ore", "tasso"]).drop_duplicates("ts")
        df = df[df["ts"] >= DAL * 86_400_000]
        sec = (df["ts"] // 1000) % 3600
        minuti_fuori += int(((sec > 60) & (sec < 3540)).sum())
        ore_reg.update(((df["ts"] // 3_600_000) % 24).tolist())
        intervalli.update(df["ore"].tolist())
        reali = set(((df["ts"].to_numpy() // 60_000 - 1) // 1440).tolist())
        giorni_t = np.flatnonzero(tenuti[:, j]) + t0
        for g in giorni_t:
            if g not in reali and np.isfinite(C[g - t0, j]):
                if pan["funding"][g - t0, j] != 0:
                    stimati[sc.data(int(g))[:7]] += 1
                else:
                    zero_in_mese[sc.data(int(g))[:7]] += 1
        # 5. candele grezze: duplicati, ordine, orario UTC (sulle monete tenute)
        file = sorted((sc.DATI / s / "giorni").glob("*.zip"))
        api = [pd.read_csv(p) for p in sorted((sc.DATI / s / "giorni_api").glob("*.csv"))]
        grezzo = pd.concat(api + [m5._csv_da_zip(p, m5.KLINE) for p in file], ignore_index=True)
        ms = m5._ms(grezzo["open_time"])
        nm = int((ms % 86_400_000 != 0).sum())
        if nm:
            non_mezzanotte[s] = nm
        d = grezzo.assign(ms=ms).loc[ms >= DAL * 86_400_000]
        dup = d[d.duplicated("ms", keep=False)]
        if len(dup):
            diversi = dup.groupby("ms")[["open", "high", "low", "close"]].nunique().max(axis=1)
            if (diversi > 1).any():
                duplicati[s] = int((diversi > 1).sum())
        for p in file:
            x = m5._ms(m5._csv_da_zip(p, m5.KLINE)["open_time"])
            if not x.is_monotonic_increasing:
                fuori_ordine[s] = fuori_ordine.get(s, 0) + 1
    out["funding"] = {"giorni_tenuti_stimati_per_mese": dict(sorted(stimati.items())),
                      "giorni_tenuti_a_zero_senza_dato_per_mese": dict(sorted(zero_in_mese.items())),
                      "regolamenti_oltre_il_minuto": minuti_fuori,
                      "ore_dei_regolamenti": dict(sorted(ore_reg.items())), "intervalli_dichiarati_ore": dict(sorted(intervalli.items()))}
    out["candele_grezze"] = {"monete_con_orari_non_a_mezzanotte": non_mezzanotte,
                             "monete_con_duplicati_diversi_dal_2021_12": duplicati, "file_fuori_ordine": fuori_ordine}

    # 6. interesse aperto (P2) mancante fra le monete dell'universo
    p2 = un.p2(pm, lun)
    u = ps["U"][sett]
    out["interesse_aperto_mancante_nell_universo"] = float(1 - np.isfinite(p2[sett])[u].mean())
    (QUI / "prova28_dati_2026-11-11_esito.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


if __name__ == "__main__":
    o = main()
    print(json.dumps({k: v for k, v in o.items() if k not in ("candele_grezze",)}, ensure_ascii=False)[:3000])
    print(json.dumps(o["candele_grezze"], ensure_ascii=False)[:1500])
