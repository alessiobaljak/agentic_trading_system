"""Programma 7, prima prova (PRIMA.md): G1, F5 decisa ogni giorno alle 00:00 UTC con gli ordini limite.

Uso: python3 -m research.programma7.prima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import cinquantaseiesima as cs
from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import ventiquattresima as vq

QUI = Path(__file__).parent
RIS = QUI / "risultati_prima"
P6 = QUI.parent / "programma6"
FINE = sc.giorno(2026, 10, 5)
COLONNE = ("lordo", "spese", "funding", "netto", "netto_doppio", "giro", "long", "short")


def lunedi_del_giorno(giorni: np.ndarray) -> np.ndarray:
    g = np.asarray(giorni, dtype=np.int64)
    return g - ((g + 3) % 7)


def universo_del_giorno(giorni: np.ndarray, lunedi: np.ndarray, U: np.ndarray) -> np.ndarray:
    """L'universo della settimana per ogni giorno (le 100 del lunedi' di quella settimana)."""
    pos = np.searchsorted(lunedi, lunedi_del_giorno(giorni))
    assert (lunedi[pos] == lunedi_del_giorno(giorni)).all()
    return U[pos]


def per_settimana(df: pd.DataFrame, giorni: np.ndarray) -> pd.DataFrame:
    """I conti giornalieri sommati per settimana (dal lunedi' alla domenica)."""
    d = df[list(COLONNE)].copy()
    d["monete"] = df["monete"]
    d["settimana"] = lunedi_del_giorno(giorni)
    agg = {c: "sum" for c in COLONNE} | {"monete": "max"}
    return d.groupby("settimana").agg(agg)


def movimenti(W: np.ndarray) -> dict:
    """Entrate, uscite e durata media delle posizioni (in giorni) dai pesi giornalieri."""
    dentro = W != 0
    entrate = int((dentro[1:] & ~dentro[:-1]).sum() + dentro[0].sum())
    uscite = int((~dentro[1:] & dentro[:-1]).sum())
    return {"entrate": entrate, "uscite": uscite, "giorni": int(W.shape[0]),
            "entrate_al_giorno": entrate / W.shape[0], "uscite_al_giorno": uscite / W.shape[0],
            "durata_media_giorni": float(dentro.sum() / max(1, entrate)),
            "giorni_con_operazioni": int(((dentro[1:] != dentro[:-1]).any(axis=1)).sum())}


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    giorni = np.arange(se.INIZIO, FINE, dtype=np.int64)
    idx = giorni - pan["t0"]
    Ud = universo_del_giorno(giorni, ps["lunedi"], ps["U"])
    sig = ot.sigma_30(pan, idx)
    W = vq.pesi_banda(np.where(np.isfinite(sig), -se.funding_7(pan, idx), np.nan), Ud, sig)
    R = sc.rendimenti(pan)[idx]
    F = np.nan_to_num(pan["funding"][idx])
    costo = sc.costi_moneta(pan["simboli"])
    mercato = te.conto(W, R, F, costo)
    limite = mercato.copy()
    spese, n_tot, n_lim, n_senza = cs.spese_a_limite(W, R, giorni, pan["simboli"], costo)
    limite["spese"] = spese
    limite["netto"] = limite["lordo"] - limite["spese"] - limite["funding"]
    limite["netto_doppio"] = limite["lordo"] - 2 * limite["spese"] - limite["funding"]
    sett_lim, sett_mer = per_settimana(limite, giorni), per_settimana(mercato, giorni)
    RIS.mkdir(exist_ok=True)
    sett_lim.to_csv(RIS / "settimane_G1.csv.gz")
    sett_mer.to_csv(RIS / "settimane_G1_mercato.csv.gz")
    limite.assign(giorno=giorni).to_csv(RIS / "giorni_G1.csv.gz", index=False)
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    e = te.esame(sett_lim, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    em = te.esame(sett_mer, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    f5 = pd.read_csv(P6 / "risultati_controllo_parita" / "settimane_F5.csv.gz", index_col=0)
    f5 = f5[(f5.index >= se.INIZIO) & (f5.index < FINE)]
    e5 = te.esame(f5, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    e["a_mercato"] = {k: em["intero"][k] for k in ("sharpe", "annuo", "discesa_max")} | {"spese_annue": em["spese_annue"]}
    e["F5_settimanale"] = {k: e5["intero"][k] for k in ("sharpe", "annuo", "discesa_max")} | {"spese_annue": e5["spese_annue"]}
    e["ordini"] = {"variazioni": n_tot, "eseguite_con_il_limite": n_lim, "senza_candele_a_1_ora": n_senza}
    e["movimenti"] = movimenti(W)
    c = sett_lim.index.intersection(f5.index)
    e["correlazione_F5"] = float(np.corrcoef(sett_lim.loc[c, "netto"], f5.loc[c, "netto"])[0, 1])
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), "57 G1": sett_lim["netto"]}, {"57 G1": e["intero"]})
    r = rivisto["candidate"]["57 G1"]
    e["sharpe_corretto"], e["sharpe_corretto_sezione_3"] = r["corretto_con_aggiunta"], r["corretto"]
    e["t"], e["gruppo"], e["gruppi"] = r["t"], r["gruppo"], rivisto["gruppi"]
    e["esito"] = te.esito(e, e["sharpe_corretto"])
    (RIS / "esame.json").write_text(json.dumps(e, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    i, o, mv, m, q = e["intero"], e["ordini"], e["movimenti"], e["a_mercato"], e["F5_settimanale"]
    testo = "\n".join([
        "# Programma 7 — risultati della prima prova (G1: F5 decisa ogni giorno)", "",
        "Regole in `PRIMA.md` (scritte prima).", "",
        f"* Operazioni: {mv['entrate_al_giorno']:.1f} entrate e {mv['uscite_al_giorno']:.1f} uscite al giorno in media; operazioni in "
        f"{mv['giorni_con_operazioni']} giorni su {mv['giorni']}; una posizione dura in media {mv['durata_media_giorni']:.1f} giorni.",
        f"* Variazioni di peso {o['variazioni']}: eseguite con il limite {o['eseguite_con_il_limite']} "
        f"({100 * o['eseguite_con_il_limite'] / max(1, o['variazioni'] - o['senza_candele_a_1_ora']):.0f}% di quelle con le candele).",
        f"* G1 con gli ordini limite: Sharpe {i['sharpe']:.2f}, {100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, "
        f"discesa {100 * i['discesa_max']:.1f}%; spese {100 * e['spese_annue']:.1f}% l'anno.",
        f"* G1 tutto a mercato: Sharpe {m['sharpe']:.2f}, {100 * m['annuo']:+.1f}% l'anno, spese {100 * m['spese_annue']:.1f}%.",
        f"* F5 settimanale (parità corrette) sulle stesse settimane: Sharpe {q['sharpe']:.2f}, {100 * q['annuo']:+.1f}% l'anno, discesa "
        f"{100 * q['discesa_max']:.1f}%, spese {100 * q['spese_annue']:.1f}%; correlazione con G1 {e['correlazione_F5']:.2f}.",
        "* Per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in e["per_anno"].items()) + ".",
        f"* Sharpe corretto con l'aggiunta {e['sharpe_corretto']:.2f} (sezione 3: {e['sharpe_corretto_sezione_3']:.2f}; "
        f"{e['gruppi']} gruppi); t dello Sharpe {e['t']:.2f}.", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_PRIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return e


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("PRIMA FINITA", flush=True)
