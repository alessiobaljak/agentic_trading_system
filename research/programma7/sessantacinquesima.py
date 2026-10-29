"""Programma 7, sessantacinquesima prova (SESSANTACINQUESIMA.md): RA, la rotazione fra le altcoin e il Bitcoin decisa ogni giorno: long
l'indice a pesi uguali delle altcoin dell'universo di G1 e short il Bitcoin (o il contrario) secondo la tendenza dello scarto a 20, 60 e
120 giorni; ordini limite come G1.

Uso: python3 -m research.programma7.sessantacinquesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma7 import cinquantaduesima as kp
from research.programma7 import prima as g1

QUI = Path(__file__).parent
RIS = QUI / "risultati_sessantacinquesima"
FINESTRE = (20, 60, 120)


def scarti(pan: dict, giorni: np.ndarray, Ud: np.ndarray, jb: int) -> np.ndarray:
    """Lo scarto di ogni giorno: media dei rendimenti delle altcoin dell'universo del giorno meno il Bitcoin."""
    R = sc.rendimenti(pan)[giorni - pan["t0"]]
    alt = Ud.copy()
    alt[:, jb] = False
    n = alt.sum(axis=1)
    media = np.where(n > 0, (R * alt).sum(axis=1) / np.maximum(n, 1), 0.0)
    return media - R[:, jb]


def segnali(s: np.ndarray) -> dict:
    """Per ogni finestra il segno della somma dei log(1 + scarto) dei giorni prima (il giorno stesso escluso); e il peso medio."""
    ls = np.log1p(s)
    c = np.r_[0.0, np.cumsum(ls)]                    # c[k] = somma dei giorni < k
    out = {}
    for L in FINESTRE:
        v = np.full(len(s), np.nan)
        k = np.arange(L, len(s))
        v[k] = np.sign(c[k] - c[k - L])
        out[L] = v
    tre = np.vstack([out[L] for L in FINESTRE])
    out["w"] = np.where(np.isfinite(tre).all(axis=0), np.nan_to_num(tre).mean(axis=0), np.nan)
    return out


def pesi(w: np.ndarray, Ud: np.ndarray, jb: int) -> np.ndarray:
    alt = Ud.copy()
    alt[:, jb] = False
    n = np.maximum(alt.sum(axis=1), 1)
    W = alt * (np.nan_to_num(w) / n)[:, None]
    W[:, jb] = -np.nan_to_num(w)
    return W


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    S = list(pan["simboli"])
    jb = S.index("BTCUSDT")
    tutti = np.arange(int(ps["lunedi"][0]), g1.FINE, dtype=np.int64)
    Ut = g1.universo_del_giorno(tutti, ps["lunedi"], ps["U"])
    s_tutti = scarti(pan, tutti, Ut, jb)
    sg_tutti = segnali(s_tutti)
    k0 = int(np.searchsorted(tutti, se.INIZIO))
    giorni = tutti[k0:]
    idx = giorni - pan["t0"]
    Ud = Ut[k0:]
    assert np.isfinite(sg_tutti["w"][k0:]).all(), "il segnale manca in qualche giorno del periodo"
    R = sc.rendimenti(pan)[idx]
    F = np.nan_to_num(pan["funding"][idx])
    costo = sc.costi_moneta(pan["simboli"])
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    varianti = {"RA": sg_tutti["w"][k0:], "sempre venduta": np.full(len(giorni), -1.0), "sempre comprata": np.full(len(giorni), 1.0)}
    for L in FINESTRE:
        varianti[f"solo {L} giorni"] = sg_tutti[L][k0:]
    RIS.mkdir(exist_ok=True)
    out, sett_ra = {}, None
    for nome, w in varianti.items():
        W = pesi(w, Ud, jb)
        lim, ordini = kp.conto(W, R, F, costo, giorni, pan["simboli"])
        sett = g1.per_settimana(lim, giorni)
        sett.to_csv(RIS / f"settimane_{nome.replace(' ', '_')}.csv.gz")
        e = te.esame(sett, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
        e["ordini"] = ordini
        out[nome] = e
        if nome == "RA":
            sett_ra = sett
    e = out["RA"]
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), "127 RA": sett_ra["netto"]}, {"127 RA": e["intero"]})
    r = rivisto["candidate"]["127 RA"]
    e["sharpe_corretto"], e["t"], e["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
    e["esito_scritto"] = te.esito(e, e["sharpe_corretto"])
    sv = out["sempre venduta"]["intero"]["sharpe"]
    e["sopra_sempre_venduta"] = bool(e["intero"]["sharpe"] > sv)
    e["esito"] = (e["esito_scritto"] if e["esito_scritto"] != "VALIDA" else
                  "VALIDA" if e["sopra_sempre_venduta"] else "non sopra «sempre venduta sulle altcoin»")
    anni = e.get("per_anno", {})
    e["regola_proprietario"] = bool(e["sharpe_corretto"] >= 0.90 and e["t"] > 3 and anni and all(v > 0 for v in anni.values()))
    g1s = pd.read_csv(QUI / "risultati_prima" / "settimane_G1.csv.gz", index_col=0)
    c = sett_ra.index.intersection(g1s.index)
    e["correlazione_G1"] = float(np.corrcoef(sett_ra.loc[c, "netto"], g1s.loc[c, "netto"])[0, 1])
    w = varianti["RA"]
    e["giorni_per_peso"] = {f"{v:+.2f}": int(np.isclose(w, v).sum()) for v in (1.0, 1 / 3, -1 / 3, -1.0)}
    anni_g = pd.to_datetime(giorni * 86400, unit="s").year
    e["cambi_per_anno"] = {int(a): int((np.diff(w[anni_g == a]) != 0).sum()) for a in sorted(set(anni_g))}
    s = s_tutti[k0:]
    e["scarto_per_anno"] = {int(a): float(np.expm1(np.log1p(s[anni_g == a]).sum())) for a in sorted(set(anni_g))}
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    i = e["intero"]
    pc = lambda v: f"{100 * v:+.1f}%"  # noqa: E731
    altre = "; ".join(f"{n}: Sharpe {out[n]['intero']['sharpe']:.2f}, {pc(out[n]['intero']['annuo'])} l'anno, discesa "
                      f"{100 * out[n]['intero']['discesa_max']:.1f}%" for n in varianti if n != "RA")
    testo = "\n".join([
        "# Programma 7 — risultati della sessantacinquesima prova (RA: la rotazione fra le altcoin e il Bitcoin, ogni giorno)", "",
        "Regole in `SESSANTACINQUESIMA.md` (scritte prima). Dal 4 gennaio 2021 al 5 ottobre 2026, universo di G1, ordini limite.", "",
        f"* **RA: Sharpe {i['sharpe']:.2f}**, {pc(i['annuo'])} l'anno, volatilità {100 * i['volatilita']:.1f}%, discesa "
        f"{100 * i['discesa_max']:.1f}%; spese {100 * e['spese_annue']:.1f}% l'anno, funding {100 * e['funding_annuo']:+.1f}% l'anno (pagato).",
        "* Per anno: " + ", ".join(f"{a} {pc(v)}" for a, v in e["per_anno"].items()) + ".",
        "* Lo scarto dell'indice delle altcoin contro il Bitcoin, per anno: " + ", ".join(f"{a} {pc(v)}" for a, v in e["scarto_per_anno"].items()) + ".",
        "* Giorni per peso: " + ", ".join(f"{k} {v}" for k, v in e["giorni_per_peso"].items()) + "; cambi del peso per anno: "
        + ", ".join(f"{a} {v}" for a, v in e["cambi_per_anno"].items()) + ".",
        f"* Per confronto: {altre}.",
        f"* Correlazione con G1: {e['correlazione_G1']:.2f}.",
        f"* Sharpe corretto con l'aggiunta {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi); t dello Sharpe {e['t']:.2f}; sopra «sempre "
        f"venduta»: {'sì' if e['sopra_sempre_venduta'] else 'no'}; regola del proprietario (corretto ≥ 0,90, ogni anno positivo, t > 3): "
        f"{'sì' if e['regola_proprietario'] else 'no'}.", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_SESSANTACINQUESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("SESSANTACINQUESIMA FINITA", flush=True)
