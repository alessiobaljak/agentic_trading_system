"""Programma 7, venticinquesima prova (VENTICINQUESIMA.md): PC, il premio di Coinbase fra le monete (media dei 7 giorni del prezzo
Coinbase su quello Binance), long il quinto con il premio piu' alto e short il piu' basso con la banda di F5, dal 2 gennaio 2023.

Uso: python3 -m research.programma7.venticinquesima   (dopo `research.programma7.coinbase`)
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import annunci as an
from research.programma6 import asticella as ast
from research.programma6 import esecuzione as es
from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import terza as te
from research.programma6 import ventiquattresima as vq
from research.programma7 import coinbase as cb
from research.programma7 import prima as pr

QUI = Path(__file__).parent
RIS = QUI / "risultati_venticinquesima"
P6 = QUI.parent / "programma6"
INIZIO, FINE = sc.giorno(2023, 1, 2), pr.FINE
ORE_MIN, MONETE_MIN = 100, 20


def multiplo(perpetuo: str, base: str) -> float:
    return {"": 1.0, "1000": 1e3, "1000000": 1e6, "1M": 1e6}.get(perpetuo[: len(perpetuo) - len(base) - 4], 1.0)


def premio_orario(base: str, perpetuo: str) -> pd.Series:
    """Coinbase / Binance − 1 per ora (indice: l'ora dall'epoca), vuota se mancano i dati."""
    c = cb.scarica(f"{base}-USD")
    b = es.ore_di(perpetuo)
    if c.empty or b.empty:
        return pd.Series(dtype=float)
    idx = c.index.intersection(b.index)
    with np.errstate(all="ignore"):
        p = c.loc[idx, "close"].astype(float) / (b.loc[idx, "close"].astype(float) / multiplo(perpetuo, base)) - 1
    return p.replace([np.inf, -np.inf], np.nan).dropna()


def segnale_settimanale(premi: dict, simboli: list, lunedi: np.ndarray) -> np.ndarray:
    """(settimane × monete) la media del premio delle 168 ore prima del lunedi' (NaN con meno di ORE_MIN ore)."""
    out = np.full((len(lunedi), len(simboli)), np.nan)
    pos = {s: j for j, s in enumerate(simboli)}
    for perpetuo, p in premi.items():
        if p.empty:
            continue
        j = pos[perpetuo]
        ore = p.index.to_numpy()
        val = p.to_numpy()
        for k, m in enumerate(lunedi):
            a, b = np.searchsorted(ore, (m - 7) * 24), np.searchsorted(ore, m * 24)
            if b - a >= ORE_MIN:
                out[k, j] = float(val[a:b].mean())
    return out


def esegui(log=print) -> dict:
    pan = sc.pannello()
    simboli = pan["simboli"]
    basi = cb.monete_in_comune(pan)
    coppie = {}
    for b in basi:
        perp = an.perpetuo(b, simboli)
        if perp and perp != "BTCUSDT":
            coppie[perp] = b
    log(f"[venticinquesima] {len(coppie)} monete con il mercato su Coinbase e il perpetuo su Binance")
    premi = {perp: premio_orario(b, perp) for perp, b in coppie.items()}
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    lun = ps["lunedi"] - pan["t0"]
    sig = ot.sigma_30(pan, lun)
    S = segnale_settimanale(premi, simboli, ps["lunedi"])
    U = ps["U"] & np.isfinite(S)
    monete = U.sum(axis=1)
    U[monete < MONETE_MIN] = False
    dentro = (ps["lunedi"] >= INIZIO) & (ps["lunedi"] < FINE)
    costo = sc.costi_moneta(simboli)
    W = vq.pesi_banda(np.where(np.isfinite(sig), S, np.nan), U, sig)
    W_opp = -W
    conti = {}
    for nome, Wx in (("PC", W), ("PC verso opposto", W_opp)):
        d = te.conto(Wx, ps["R"], ps["F"], costo)
        d.index = ps["lunedi"]
        conti[nome] = d
    RIS.mkdir(exist_ok=True)
    conti["PC"].to_csv(RIS / "settimane_PC.csv.gz")
    pd.DataFrame(S, index=ps["lunedi"], columns=simboli).loc[:, list(coppie)].to_csv(RIS / "premio_settimanale.csv.gz")
    btc = pd.Series(ps["R"][:, simboli.index("BTCUSDT")], index=ps["lunedi"])
    anni = (2023, 2024, 2025)
    e = te.esame(conti["PC"], btc, inizio=INIZIO, anni_pieni=anni)
    eo = te.esame(conti["PC verso opposto"], btc, inizio=INIZIO, anni_pieni=anni)
    e["verso_opposto"] = {k: eo["intero"][k] for k in ("sharpe", "annuo")}
    e["monete_per_settimana"] = float(monete[dentro].mean())
    e["settimane_fuori"] = int((monete[dentro] < MONETE_MIN).sum())
    e["premio_medio"] = float(np.nanmean(S[dentro]))
    e["premio_dispersione"] = float(np.nanmean(np.nanstd(np.where(U, S, np.nan)[dentro], axis=1)))
    f5 = pd.read_csv(P6 / "risultati_controllo_parita" / "settimane_F5.csv.gz", index_col=0)
    c = conti["PC"].index[dentro].intersection(f5.index)
    e["correlazione_F5"] = float(np.corrcoef(conti["PC"].loc[c, "netto"], f5.loc[c, "netto"])[0, 1])
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), "87 PC": conti["PC"]["netto"]}, {"87 PC": e["intero"]})
    r = rivisto["candidate"]["87 PC"]
    e["sharpe_corretto"], e["t"], e["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
    e["esito"] = te.esito(e, e["sharpe_corretto"])
    e["regola_del_proprietario"] = bool(e["sharpe_corretto"] >= 0.90 and all(v > 0 for v in e["per_anno"].values()) and e["t"] > 3)
    (RIS / "esame.json").write_text(json.dumps(e, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    i, o = e["intero"], e["verso_opposto"]
    testo = "\n".join([
        "# Programma 7 — risultati della venticinquesima prova (PC: il premio di Coinbase fra le monete)", "",
        "Regole in `VENTICINQUESIMA.md` (scritte prima). Dal 2 gennaio 2023 al 5 ottobre 2026.", "",
        f"* {len(coppie)} monete con tutti e due i mercati; in media {e['monete_per_settimana']:.0f} monete con il segnale per settimana "
        f"(settimane fuori per meno di {MONETE_MIN}: {e['settimane_fuori']}); premio medio {100 * e['premio_medio']:+.3f}%, dispersione fra "
        f"le monete {100 * e['premio_dispersione']:.3f}%.",
        f"* **PC: Sharpe {i['sharpe']:.2f}**, {100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, discesa "
        f"{100 * i['discesa_max']:.1f}%; spese {100 * e['spese_annue']:.1f}% l'anno; correlazione con F5 {e['correlazione_F5']:.2f}.",
        f"* Il verso opposto (solo per capire): Sharpe {o['sharpe']:.2f}, {100 * o['annuo']:+.1f}% l'anno.",
        "* Per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in e["per_anno"].items()) + ".",
        f"* Sharpe corretto {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi); t {e['t']:.2f}; regola del proprietario del 24 ottobre: "
        f"{'sì' if e['regola_del_proprietario'] else 'no'}.", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_VENTICINQUESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return e


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("VENTICINQUESIMA FINITA", flush=True)
