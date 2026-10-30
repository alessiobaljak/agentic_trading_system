"""Programma 7, settantesima prova (SETTANTESIMA.md): FM, il funding in USDT contro quello dei perpetui in moneta, deciso ogni giorno come
G1: short il quinto con lo scarto dei 7 giorni piu' alto, long il piu' basso; deve battere G1 sulle stesse monete.

Uso: python3 -m research.programma7.settantesima
"""
from __future__ import annotations

import json
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import ottava as ot
from research.programma6 import scarico_giorni as sg
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import ventiquattresima as vq
from research.programma7 import cinquantaduesima as kp
from research.programma7 import prima as g1
from research.src.dati import funding_da_zip

QUI = Path(__file__).parent
RIS = QUI / "risultati_settantesima"
DATI = QUI.parent / "data" / "cm_funding"
ELENCO = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?delimiter=/&prefix=data/futures/cm/monthly/fundingRate/"


def contratti() -> list:
    with urllib.request.urlopen(urllib.request.Request(ELENCO, headers={"User-Agent": "ricerca/1.0"}), timeout=60) as r:
        t = r.read().decode()
    return re.findall(r"<Prefix>data/futures/cm/monthly/fundingRate/([^/]+)/</Prefix>", t)


def funding_moneta(pan: dict, log=print) -> np.ndarray:
    """Il funding dei perpetui in moneta per giorno di tenuta (stessa convenzione del pannello), allineato alle monete del pannello
    (NaN dove la moneta non ha il contratto in moneta o il giorno manca)."""
    simboli, t0 = pan["simboli"], pan["t0"]
    T = pan["close"].shape[0]
    mesi = sorted({sc.data(g)[:7] for g in range(t0, t0 + T)})
    lista = contratti()
    lavori = [(c, m) for c in lista for m in mesi]
    log(f"[settantesima] {len(lista)} contratti in moneta, {len(lavori)} file mensili")

    def uno(x):
        c, m = x
        try:
            sg._scarica(f"data/futures/cm/monthly/fundingRate/{c}/{c}-fundingRate-{m}.zip", DATI / c)
        except Exception:  # noqa: BLE001
            pass
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(uno, lavori))
    Fm = np.full((T, len(simboli)), np.nan)
    abbinati = {}
    for c in lista:
        base = c.split("USD_PERP")[0]
        s = next((p for p in (f"{base}USDT", f"1000{base}USDT") if p in simboli), None)
        if not s:
            continue
        righe = []
        for f in sorted((DATI / c).glob("*.zip")):
            righe += funding_da_zip(f)
        if not righe:
            continue
        df = pd.DataFrame(righe, columns=["ts", "ore", "tasso"]).drop_duplicates("ts")
        tenuta = (df["ts"].to_numpy() // 60_000 - 1) // 1440
        g = pd.Series(df["tasso"].to_numpy(float), index=tenuta).groupby(level=0).sum()
        g = g[(g.index >= t0) & (g.index < t0 + T)]
        Fm[g.index.to_numpy() - t0, simboli.index(s)] = g.to_numpy()
        abbinati[c] = s
    return Fm, abbinati


def somma_7(F: np.ndarray, idx: np.ndarray) -> np.ndarray:
    """La somma dei 7 giorni prima (idx-7 .. idx-1), NaN se manca uno dei giorni."""
    ok = np.isfinite(F)
    Fc = np.vstack([np.zeros((1, F.shape[1])), np.cumsum(np.nan_to_num(F), axis=0)])
    Nc = np.vstack([np.zeros((1, F.shape[1])), np.cumsum(ok, axis=0)])
    s = np.round(Fc[idx] - Fc[idx - 7], 12)
    return np.where(Nc[idx] - Nc[idx - 7] == 7, s, np.nan)


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    Fm, abbinati = funding_moneta(pan, log)
    log(f"[settantesima] abbinati al perpetuo in USDT: {len(abbinati)}")
    giorni = np.arange(se.INIZIO, g1.FINE, dtype=np.int64)
    idx = giorni - pan["t0"]
    Ud = g1.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
    sig = ot.sigma_30(pan, idx)
    fu = se.funding_7(pan, idx)
    fm = somma_7(Fm, idx)
    scarto = np.round(fu - fm, 12)
    Ur = Ud & np.isfinite(scarto)
    R = sc.rendimenti(pan)[idx]
    F = np.nan_to_num(pan["funding"][idx])
    costo = sc.costi_moneta(pan["simboli"])
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    rango = lambda M: pd.DataFrame(np.where(Ur, M, np.nan)).rank(axis=1, pct=True).to_numpy()  # noqa: E731
    varianti = {"FM": -scarto, "G1 sulle stesse monete": -fu, "media dei ranghi": -(rango(fu) + rango(scarto)) / 2}
    out, sett = {}, {}
    RIS.mkdir(exist_ok=True)
    for nome, ct in varianti.items():
        W = vq.pesi_banda(np.where(np.isfinite(sig) & Ur, ct, np.nan), Ur, sig)
        lim, ordini = kp.conto(W, R, F, costo, giorni, pan["simboli"])
        s = g1.per_settimana(lim, giorni)
        s.to_csv(RIS / f"settimane_{nome.replace(' ', '_')}.csv.gz")
        e = te.esame(s, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
        e["ordini"], e["movimenti"] = ordini, g1.movimenti(W)
        e["giorni_con_posizioni"] = int((np.abs(W).sum(axis=1) > 0).sum())
        out[nome], sett[nome] = e, s
    e = out["FM"]
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), "132 FM": sett["FM"]["netto"]}, {"132 FM": e["intero"]})
    r = rivisto["candidate"]["132 FM"]
    e["sharpe_corretto"], e["t"], e["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
    e["esito_scritto"] = te.esito(e, e["sharpe_corretto"])
    e["sopra_G1_stesse_monete"] = bool(e["intero"]["sharpe"] > out["G1 sulle stesse monete"]["intero"]["sharpe"])
    e["esito"] = (e["esito_scritto"] if e["esito_scritto"] != "VALIDA" else
                  "VALIDA" if e["sopra_G1_stesse_monete"] else "non sopra G1 sulle stesse monete")
    anni = e.get("per_anno", {})
    e["regola_proprietario"] = bool(e["sharpe_corretto"] >= 0.90 and e["t"] > 3 and anni and all(v > 0 for v in anni.values()))
    g1s = pd.read_csv(QUI / "risultati_prima" / "settimane_G1.csv.gz", index_col=0)
    c = sett["FM"].index.intersection(g1s.index)
    e["correlazione_G1"] = float(np.corrcoef(sett["FM"].loc[c, "netto"], g1s.loc[c, "netto"])[0, 1])
    e["monete_con_segnale_mediana"] = float(np.median(Ur.sum(axis=1)))
    cc = [np.corrcoef(fu[k, Ur[k]], scarto[k, Ur[k]])[0, 1] for k in range(len(giorni)) if Ur[k].sum() >= 10]
    e["correlazione_scarto_funding_mediana"] = float(np.nanmedian(cc)) if cc else None
    e["scarto_medio_annuo"] = float(np.nanmean(np.where(Ur, scarto, np.nan)) * 365 / 7)
    (RIS / "esame.json").write_text(json.dumps({"abbinati": abbinati, **out}, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda v: f"{100 * v:+.1f}%"  # noqa: E731
    i = e["intero"]
    altre = "; ".join(f"{n}: Sharpe {out[n]['intero']['sharpe']:.2f}, {pc(out[n]['intero']['annuo'])} l'anno, discesa "
                      f"{100 * out[n]['intero']['discesa_max']:.1f}%" for n in varianti if n != "FM")
    testo = "\n".join([
        "# Programma 7 — risultati della settantesima prova (FM: il funding in USDT contro quello in moneta, ogni giorno)", "",
        "Regole in `SETTANTESIMA.md` (scritte prima). Dal 4 gennaio 2021 al 5 ottobre 2026, universo di G1 ristretto alle monete con il "
        "perpetuo in moneta, ordini limite.", "",
        f"* {len(abbinati)} contratti in moneta abbinati; monete con il segnale ogni giorno, mediana {e['monete_con_segnale_mediana']:.0f}; "
        f"giorni con le posizioni {e['giorni_con_posizioni']} su {len(giorni)} (almeno 20 monete).",
        f"* Lo scarto medio fra il funding in USDT e quello in moneta: {pc(e['scarto_medio_annuo'])} l'anno; correlazione con il funding in "
        f"USDT fra le monete dello stesso giorno, mediana {e['correlazione_scarto_funding_mediana']:.2f}.",
        f"* **FM: Sharpe {i['sharpe']:.2f}**, {pc(i['annuo'])} l'anno, volatilità {100 * i['volatilita']:.1f}%, discesa "
        f"{100 * i['discesa_max']:.1f}%; spese {100 * e['spese_annue']:.1f}% l'anno; lato long {pc(e['long_annuo'])}, short "
        f"{pc(e['short_annuo'])} l'anno.",
        "* Per anno: " + ", ".join(f"{a} {pc(v)}" for a, v in e["per_anno"].items()) + ".",
        f"* Per confronto: {altre}.",
        f"* Correlazione con G1: {e['correlazione_G1']:.2f}.",
        f"* Sharpe corretto con l'aggiunta {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi); t {e['t']:.2f}; sopra G1 sulle stesse monete: "
        f"{'sì' if e['sopra_G1_stesse_monete'] else 'no'}; regola del proprietario: {'sì' if e['regola_proprietario'] else 'no'}.", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_SETTANTESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("SETTANTESIMA FINITA", flush=True)
