"""Programma 6, trentaquattresima prova (TRENTAQUATTRESIMA.md): rottura di Donchian a 20 candele da 4 ore, stop a 2 ATR e
uscita mobile a 3 ATR dalla chiusura migliore, al massimo 42 candele; T1 senza filtro, T2 con il filtro del funding (long nel
40% piu' basso, short nel 40% piu' alto). Monete dell'universo settimanale delle 100, dal 4 gennaio 2021.

Uso: python3 -m research.programma6.trentaquattresima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from numba import njit

from research.programma5.strumenti import motore5 as m5
from research.programma6 import esecuzione as es
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import ventunesima as vu
from research.programma6.motore import TAKER

QUI = Path(__file__).parent
RIS = QUI / "risultati_trentaquattresima"
N_DON, N_ATR, K_STOP, K_TRAIL, MAX_BARRE = 20, 14, 2.0, 3.0, 42
FILTRO, QUOTA, MAX_APERTE, P_SOGLIA = 0.40, 0.05, 20, 0.005
DA, A = sc.giorno(2021, 1, 4), sc.giorno(2026, 10, 10)


def quattro_ore(h: pd.DataFrame) -> pd.DataFrame:
    """Candele a 4 ore (00, 04, ... UTC) dalle candele a 1 ora; indice = blocco di 4 ore dall'epoca."""
    h = h.dropna(subset=["open", "close"])
    g = h.groupby(h.index.to_numpy() // 4)
    return pd.DataFrame({"open": g["open"].first(), "high": g["high"].max(), "low": g["low"].min(), "close": g["close"].last()})


@njit(cache=True)
def _simula(o, h, l, c, segnali_long, segnali_short, atr):
    """Le operazioni: (barra del segnale, barra d'entrata, barra d'uscita, verso, prezzo d'entrata, d'uscita, motivo)."""
    n = len(c)
    out = []
    i = 0
    while i < n - 1:
        verso = 1 if segnali_long[i] else (-1 if segnali_short[i] else 0)
        if verso == 0 or not atr[i] > 0:
            i += 1
            continue
        e = i + 1
        p0 = o[e]
        a = atr[i]
        migliore = p0
        uscita, prezzo, motivo = -1, 0.0, 0
        j = e
        while j < n:
            if verso > 0:
                livello = max(p0 - K_STOP * a, migliore - K_TRAIL * a)
                if o[j] <= livello:
                    uscita, prezzo = j, o[j]
                elif l[j] <= livello:
                    uscita, prezzo = j, livello
            else:
                livello = min(p0 + K_STOP * a, migliore + K_TRAIL * a)
                if o[j] >= livello:
                    uscita, prezzo = j, o[j]
                elif h[j] >= livello:
                    uscita, prezzo = j, livello
            if uscita >= 0:
                motivo = 1 if abs(livello - (p0 - verso * K_STOP * a)) < 1e-12 else 2
                break
            migliore = max(migliore, c[j]) if verso > 0 else min(migliore, c[j])
            if j - e + 1 >= MAX_BARRE and j + 1 < n:
                uscita, prezzo, motivo = j + 1, o[j + 1], 3
                break
            j += 1
        if uscita < 0:
            break
        out.append((i, e, uscita, verso, p0, prezzo, motivo))
        i = uscita
    return out


def rango_funding(pan: dict, ps: dict) -> tuple:
    """(giorni × monete: rango del funding dei 7 giorni prima fra le monete dell'universo della settimana; maschera
    giornaliera dell'universo)."""
    T, S = pan["close"].shape
    Ud = np.zeros((T, S), bool)
    for k, m in enumerate(ps["lunedi"] - pan["t0"]):
        Ud[m: min(T, m + 7)] = ps["U"][k]
    Fc = np.vstack([np.zeros((1, S)), np.cumsum(pan["funding"], axis=0)])
    f7 = Fc[np.arange(T)] - Fc[np.maximum(np.arange(T) - 7, 0)]
    R = np.full((T, S), np.nan)
    for d in range(T):
        idx = np.flatnonzero(Ud[d])
        if len(idx) >= 20:
            R[d, idx] = pd.Series(f7[d, idx]).rank(pct=True).to_numpy()
    return R, Ud


def operazioni(pan: dict, ps: dict, filtro: bool, R: np.ndarray, Ud: np.ndarray) -> pd.DataFrame:
    sim = pan["simboli"]
    righe = []
    for j in np.flatnonzero(Ud.any(axis=0)):
        s = sim[j]
        b = quattro_ore(es.ore_di(s))
        if len(b) < N_DON + N_ATR + 2:
            continue
        o, h, l, c = (b[k].to_numpy(float) for k in ("open", "high", "low", "close"))
        blocco = b.index.to_numpy()
        giorno = blocco * 4 // 24 - pan["t0"]
        hh = pd.Series(h).rolling(N_DON).max().shift(1).to_numpy()
        ll = pd.Series(l).rolling(N_DON).min().shift(1).to_numpy()
        cp = np.r_[np.nan, c[:-1]]
        tr_ = np.nanmax(np.vstack([h - l, np.abs(h - cp), np.abs(l - cp)]), axis=0)
        atr = pd.Series(tr_).rolling(N_ATR).mean().to_numpy()
        dentro = (giorno >= 0) & (giorno < Ud.shape[0])
        g = np.clip(giorno, 0, Ud.shape[0] - 1)
        nel = dentro & Ud[g, j] & (giorno + pan["t0"] >= DA) & (giorno + pan["t0"] <= A)
        lungo, corto = nel & (c > hh), nel & (c < ll)
        if filtro:
            rk = R[g, j]
            lungo &= rk <= FILTRO
            corto &= rk >= 1 - FILTRO
        for i, e, u, verso, p0, p1, motivo in _simula(o, h, l, c, lungo, corto, atr):
            ore_tenuta = (blocco[u] - blocco[e]) * 4
            gi = int(giorno[e])
            ge = int(min(giorno[u], pan["funding"].shape[0] - 1))
            f = float(pan["funding"][gi: ge + 1, j].sum()) * ore_tenuta / max(1, (ge - gi + 1) * 24)
            costo = 2 * (TAKER + m5.scarto(s))
            r = verso * (p1 / p0 - 1) - costo - verso * f
            righe.append({"simbolo": s, "data": sc.data(gi + pan["t0"]), "uscita": sc.data(int(giorno[u]) + pan["t0"]),
                          "annuncio": int((gi + pan["t0"] + 3) // 7), "verso": verso, "r": r, "ore": ore_tenuta,
                          "motivo": {1: "stop", 2: "uscita mobile", 3: "tempo"}[motivo]})
    return pd.DataFrame(righe)


def portafoglio(df: pd.DataFrame) -> pd.DataFrame:
    """5% a operazione, al massimo 20 aperte; la settimana somma le operazioni chiuse (dal lunedi')."""
    d = df.sort_values(["data", "simbolo"]).reset_index(drop=True)
    aperte, tenute = [], []
    for k, x in d.iterrows():
        ini = sc.giorno(*map(int, x["data"].split("-")))
        aperte = [u for u in aperte if u > ini]
        if len(aperte) >= MAX_APERTE:
            continue
        aperte.append(sc.giorno(*map(int, x["uscita"].split("-"))))
        tenute.append(k)
    t = d.loc[tenute]
    usc = np.array([sc.giorno(*map(int, u.split("-"))) for u in t["uscita"]])
    lun = ((usc + 3) // 7) * 7 - 3
    costo = 2 * (TAKER + 0.0002)
    sett = pd.Series(QUOTA * t["r"].to_numpy(), index=lun).groupby(level=0).sum()
    sett_d = pd.Series(QUOTA * (t["r"].to_numpy() - costo), index=lun).groupby(level=0).sum()
    tutte = np.arange(DA, A + 7, 7)
    out = pd.DataFrame({"netto": sett.reindex(tutte).fillna(0.0), "netto_doppio": sett_d.reindex(tutte).fillna(0.0)})
    for k in ("lordo", "spese", "funding", "giro", "long", "short"):
        out[k] = 0.0
    out["monete"] = 1
    return out


def prove_fino_alla_trentatreesima() -> list:
    from research.programma6 import venticinquesima as v25
    sr = v25.prove_fino_alla_ventiquattresima()
    for f, chiavi in (("risultati_venticinquesima", ("M7", "F5 + M7")), ("risultati_ventottesima", ("K2", "F5 + M7 + K2")),
                      ("risultati_trentatreesima", ("N3 a portafoglio", "F5 + N3"))):
        e_ = json.loads((QUI / f / "esame.json").read_text())
        sr += [e_[k]["intero"]["sharpe"] for k in chiavi]
    sr += [json.loads((QUI / f / "esame.json").read_text())["intero"]["sharpe"]
           for f in ("risultati_ventinovesima", "risultati_trentunesima")]
    return sr


def esame_operazioni(df: pd.DataFrame) -> dict:
    d = df.sort_values("data")
    e = {"boot": vu.bootstrap_annunci(d, "r")}
    meta = len(d) // 2
    e["prima_meta"], e["seconda_meta"] = float(d["r"].iloc[:meta].mean()), float(d["r"].iloc[meta:].mean())
    e["senza_5_migliori"] = float(d["r"].sort_values(ascending=False).iloc[5:].mean())
    e["vinte"], e["ore_medie"] = float((d["r"] > 0).mean()), float(d["ore"].mean())
    e["motivi"] = d["motivo"].value_counts(normalize=True).round(3).to_dict()
    e["long_short"] = {int(v): float(g["r"].mean()) for v, g in d.groupby("verso")}
    e["passa"] = bool(e["boot"]["p"] <= P_SOGLIA and e["prima_meta"] > 0 and e["seconda_meta"] > 0 and e["senza_5_migliori"] > 0)
    return e


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    R, Ud = rango_funding(pan, ps)
    jb = ps["simboli"].index("BTCUSDT")
    btc = pd.Series(ps["R"][:, jb], index=ps["lunedi"])
    sr = prove_fino_alla_trentatreesima()
    RIS.mkdir(exist_ok=True)
    esami = {}
    for nome, filtro in (("T1", False), ("T2", True)):
        df = operazioni(pan, ps, filtro, R, Ud)
        df.to_csv(RIS / f"operazioni_{nome}.csv.gz", index=False)
        po = portafoglio(df)
        e = {"operazioni": esame_operazioni(df), "numero": int(len(df))}
        e["portafoglio"] = te.esame(po, btc, inizio=DA, anni_pieni=se.ANNI_PIENI)
        sr.append(e["portafoglio"]["intero"]["sharpe"])
        esami[nome] = e
        log(f"[trentaquattresima] {nome}: {len(df)} operazioni, media {100 * df['r'].mean():+.3f}%")
    for nome, e in esami.items():
        i = e["portafoglio"]["intero"]
        e["portafoglio"]["sharpe_corretto"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr, 52)
        e["portafoglio"]["prove_nel_conto"] = len(sr)
        e["portafoglio"]["esito"] = te.esito(e["portafoglio"], e["portafoglio"]["sharpe_corretto"])
        e["esito"] = "VALIDA" if e["operazioni"]["passa"] and e["portafoglio"]["esito"] == "VALIDA" else "non valida"
    (RIS / "esame.json").write_text(json.dumps(esami, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    righe = ["# Programma 6 — risultati della trentaquattresima prova (indicatori tecnici a 4 ore con il contesto del funding)", "",
             "Regole in `TRENTAQUATTRESIMA.md` (scritte prima). Rottura di Donchian a 20 candele da 4 ore, stop a 2 ATR, uscita "
             "mobile a 3 ATR, al massimo 7 giorni; monete dell'universo settimanale delle 100, dal 4 gennaio 2021.", "",
             "| Variante | Operazioni | Media netta | p | Vinte | Tenuta media | Long, short | Uscite: stop, mobile, tempo | "
             "Portafoglio: Sharpe, rendimento/anno, discesa | Sharpe corretto | Esito |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for nome, e in esami.items():
        o, p = e["operazioni"], e["portafoglio"]
        m = o["motivi"]
        righe.append(f"| {nome} ({'con il filtro del funding' if nome == 'T2' else 'senza filtro'}) | {e['numero']} | "
                     f"{100 * o['boot']['media']:+.3f}% | {o['boot']['p']:.4f} | {100 * o['vinte']:.0f}% | {o['ore_medie']:.0f} ore | "
                     f"{100 * o['long_short'].get(1, float('nan')):+.2f}%, {100 * o['long_short'].get(-1, float('nan')):+.2f}% | "
                     f"{100 * m.get('stop', 0):.0f}%, {100 * m.get('uscita mobile', 0):.0f}%, {100 * m.get('tempo', 0):.0f}% | "
                     f"{p['intero']['sharpe']:.2f}, {100 * p['intero']['annuo']:+.1f}%, {100 * p['intero']['discesa_max']:.1f}% | "
                     f"{p['sharpe_corretto']:.2f} | {e['esito']} |")
    for nome, e in esami.items():
        righe += ["", f"**{nome}, portafoglio per anno**: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in e["portafoglio"]["per_anno"].items())]
    righe += ["", f"Sharpe corretto con {len(sr)} prove."]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_TRENTAQUATTRESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return esami


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("TRENTAQUATTRESIMA FINITA", flush=True)
