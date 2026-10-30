"""Programma 7, settantacinquesima prova (SETTANTACINQUESIMA.md): HLI, il funding di Hyperliquid al contrario sulle monete 101-200 che la
prova 135 non ha usato: long il quinto dove Hyperliquid paga piu' di Binance, short il piu' basso, deciso ogni giorno come G1.

Uso: python3 -m research.programma7.settantacinquesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import ventiquattresima as vq
from research.programma7 import cinquantaduesima as kp
from research.programma7 import prima as g1
from research.programma7 import settantatreesima as hl
from research.programma7 import settantesima as fm

QUI = Path(__file__).parent
RIS = QUI / "risultati_settantacinquesima"


def esegui(log=print) -> dict:
    pan = sc.pannello()
    Fh, abbinati = hl.funding_hl(pan, log)
    giorni = np.arange(hl.DAL, g1.FINE, dtype=np.int64)
    idx = giorni - pan["t0"]
    sig = ot.sigma_30(pan, idx)
    fb = se.funding_7(pan, idx)
    scarto = np.round(fm.somma_7(Fh, idx) - fb, 12)
    R = sc.rendimenti(pan)[idx]
    F = np.nan_to_num(pan["funding"][idx])
    costo = sc.costi_moneta(pan["simboli"])
    ps100 = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    ps200 = te.pannello_settimane(pan, log=lambda x: None, da=100, a=200, indicatori_si=False)
    btc = pd.Series(ps100["R"][:, ps100["simboli"].index("BTCUSDT")], index=ps100["lunedi"])
    U200 = g1.universo_del_giorno(giorni, ps200["lunedi"], ps200["U"]) & np.isfinite(scarto)
    U100 = g1.universo_del_giorno(giorni, ps100["lunedi"], ps100["U"]) & np.isfinite(scarto)
    varianti = {"HLI 101-200": (scarto, U200), "G1 101-200 sulle stesse monete": (-fb, U200), "HLI prime 100": (scarto, U100)}
    out, sett = {}, {}
    RIS.mkdir(exist_ok=True)
    for nome, (ct, U) in varianti.items():
        W = vq.pesi_banda(np.where(np.isfinite(sig) & U, ct, np.nan), U, sig)
        lim, ordini = kp.conto(W, R, F, costo, giorni, pan["simboli"])
        s = g1.per_settimana(lim, giorni)
        s.to_csv(RIS / f"settimane_{nome.replace(' ', '_')}.csv.gz")
        e = te.esame(s, btc, inizio=hl.DAL, anni_pieni=(2024, 2025))
        e["ordini"], e["movimenti"] = ordini, g1.movimenti(W)
        e["giorni_con_posizioni"] = int((np.abs(W).sum(axis=1) > 0).sum())
        e["monete_con_segnale_mediana"] = float(np.median(U.sum(axis=1)))
        out[nome], sett[nome] = e, s
    e = out["HLI 101-200"]
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), "137 HLI": sett["HLI 101-200"]["netto"]}, {"137 HLI": e["intero"]})
    r = rivisto["candidate"]["137 HLI"]
    e["sharpe_corretto"], e["t"], e["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
    e["esito_scritto"] = te.esito(e, e["sharpe_corretto"])
    e["sopra_G1_stesse_monete"] = bool(e["intero"]["sharpe"] > out["G1 101-200 sulle stesse monete"]["intero"]["sharpe"])
    e["esito"] = (e["esito_scritto"] if e["esito_scritto"] != "VALIDA" else
                  "CONFERMATA" if e["sopra_G1_stesse_monete"] else "non sopra G1 sulle stesse monete")
    anni = e.get("per_anno", {})
    e["regola_proprietario"] = bool(e["sharpe_corretto"] >= 0.90 and e["t"] > 3 and anni and all(v > 0 for v in anni.values()))
    g1s = pd.read_csv(QUI / "risultati_prima" / "settimane_G1.csv.gz", index_col=0)
    c = sett["HLI 101-200"].index.intersection(g1s.index)
    e["correlazione_G1"] = float(np.corrcoef(sett["HLI 101-200"].loc[c, "netto"], g1s.loc[c, "netto"])[0, 1])
    c2 = sett["HLI 101-200"].index.intersection(sett["HLI prime 100"].index)
    e["correlazione_prime_100"] = float(np.corrcoef(sett["HLI 101-200"].loc[c2, "netto"], sett["HLI prime 100"].loc[c2, "netto"])[0, 1])
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda v: f"{100 * v:+.1f}%"  # noqa: E731
    i = e["intero"]
    altre = "; ".join(f"{n}: Sharpe {out[n]['intero']['sharpe']:.2f}, {pc(out[n]['intero']['annuo'])} l'anno, discesa "
                      f"{100 * out[n]['intero']['discesa_max']:.1f}%, spese {100 * out[n]['spese_annue']:.1f}%" for n in varianti if n != "HLI 101-200")
    testo = "\n".join([
        "# Programma 7 — risultati della settantacinquesima prova (HLI: il funding di Hyperliquid al contrario, monete 101-200)", "",
        "Regole in `SETTANTACINQUESIMA.md` (scritte prima). Dal 5 giugno 2023 al 5 ottobre 2026, monete dalla 101ª alla 200ª per volume con il "
        "segnale, ordini limite.", "",
        f"* Monete con il segnale ogni giorno, mediana {e['monete_con_segnale_mediana']:.0f}; giorni con le posizioni "
        f"{e['giorni_con_posizioni']} su {len(giorni)} (almeno 20 monete).",
        f"* **HLI 101-200: Sharpe {i['sharpe']:.2f}**, {pc(i['annuo'])} l'anno, volatilità {100 * i['volatilita']:.1f}%, discesa "
        f"{100 * i['discesa_max']:.1f}%; spese {100 * e['spese_annue']:.1f}% l'anno; a costi doppi {pc(e['costi_doppi'] * 52)} l'anno; lato "
        f"long {pc(e['long_annuo'])}, short {pc(e['short_annuo'])} l'anno.",
        "* Per anno: " + ", ".join(f"{a} {pc(v)}" for a, v in e["per_anno"].items()) + ".",
        f"* Per confronto: {altre}.",
        f"* Correlazione con G1 {e['correlazione_G1']:.2f}; con la stessa regola sulle prime 100 {e['correlazione_prime_100']:.2f}.",
        f"* Sharpe corretto con l'aggiunta {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi); t {e['t']:.2f}; sopra G1 sulle stesse monete: "
        f"{'sì' if e['sopra_G1_stesse_monete'] else 'no'}; regola del proprietario: {'sì' if e['regola_proprietario'] else 'no'}.", "",
        f"**Esito: {e['esito']}** (esame scritto: {e['esito_scritto']})"]) + "\n"
    (QUI / "RISULTATI_SETTANTACINQUESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("SETTANTACINQUESIMA FINITA", flush=True)
