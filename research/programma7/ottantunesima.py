"""Programma 7, ottantunesima prova (OTTANTUNESIMA.md): SM, il momento dei settori a settimana come F5. I settori della prova 142 (senza
«altro»), rendimento medio delle 4 settimane prima; long le monete del terzo dei settori saliti di più, short quelle del terzo saliti
di meno; controllo con le etichette dei settori mescolate a caso fra le monete.

Uso: python3 -m research.programma7.ottantunesima
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
from research.programma7 import ottantesima as gs

QUI = Path(__file__).parent
RIS = QUI / "risultati_ottantunesima"
FINE = sc.giorno(2026, 10, 1)
SETTIMANE, ETA_MIN, MIN_SETTORE, MIN_SETTORI, MESCOLATE, SEME = 4, 37, 5, 4, 20, 2026
NOME = "143 SM"


def rendimento_passato(pan: dict, idx: np.ndarray, settimane: int) -> np.ndarray:
    """Rendimento dalla chiusura del giorno l − 1 − 7·settimane a quella del giorno l − 1 (solo prezzi noti il lunedì alle 00:00)."""
    c = pan["close"]
    a, b = c[idx - 1], c[idx - 1 - 7 * settimane]
    with np.errstate(all="ignore"):
        return np.where((b > 0) & np.isfinite(a), a / b - 1, np.nan)


def pesi_settori(rp: np.ndarray, U: np.ndarray, sig: np.ndarray, sett: np.ndarray) -> tuple:
    """Pesi della regola (sezione 2) e, per ogni settimana, i settori dei due lati."""
    W, S = rp.shape
    out = np.zeros((W, S))
    lati = []
    for k in range(W):
        ok = U[k] & np.isfinite(rp[k]) & np.isfinite(sig[k]) & (sig[k] > 0) & (sett != "altro")
        nomi, conti = np.unique(sett[ok], return_counts=True)
        validi = [n for n, c in zip(nomi, conti) if c >= MIN_SETTORE]
        if len(validi) < MIN_SETTORI:
            lati.append(None)
            continue
        medie = sorted(((float(np.mean(rp[k, ok & (sett == n)])), n) for n in validi))
        q = max(1, len(validi) // 3)
        corti, lunghi = [n for _, n in medie[:q]], [n for _, n in medie[-q:]]
        for gruppo, segno in ((lunghi, 1.0), (corti, -1.0)):
            jj = np.flatnonzero(ok & np.isin(sett, gruppo))
            inv = 1.0 / sig[k, jj]
            out[k, jj] = segno * inv / inv.sum()
        lati.append({"long": lunghi, "short": corti, "settori": len(validi)})
    return out, lati


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    assert ps["simboli"] == pan["simboli"]
    S = list(pan["simboli"])
    sett = gs.settore_di(S)
    sett[S.index("BTCUSDT")] = "altro"
    lun = ps["lunedi"]
    idx = lun - pan["t0"]
    ok = np.isfinite(pan["close"])
    primo = np.where(ok.any(axis=0), ok.argmax(axis=0), 10 ** 9) + pan["t0"]
    eta = lun[:, None] - primo[None, :]
    Uv = ps["U"] & (eta >= ETA_MIN) & (lun[:, None] < FINE)
    sig = ot.sigma_30(pan, idx)
    costo = sc.costi_moneta(pan["simboli"])
    btc = pd.Series(ps["R"][:, S.index("BTCUSDT")], index=lun)
    tieni = (lun >= se.INIZIO) & (lun < FINE)

    def conto(W):
        df = te.conto(W, ps["R"], ps["F"], costo)
        df.index = lun
        return df[df.index < FINE]

    RIS.mkdir(exist_ok=True)
    out = {}
    rp = rendimento_passato(pan, idx, SETTIMANE)
    W, lati = pesi_settori(rp, Uv, sig, sett)
    df = conto(W)
    df.to_csv(RIS / "settimane_SM.csv.gz")
    e = te.esame(df, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), NOME: df["netto"]}, {NOME: e["intero"]})
    r = rivisto["candidate"][NOME]
    e["sharpe_corretto"], e["t"], e["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
    e["esito_esame"] = te.esito(e, e["sharpe_corretto"])
    anni = e.get("per_anno", {})
    e["regola_proprietario"] = bool(e["sharpe_corretto"] >= 0.90 and e["t"] > 3 and anni and all(v > 0 for v in anni.values()))
    # il controllo dei settori mescolati
    rng = np.random.default_rng(SEME)
    finti = []
    for _ in range(MESCOLATE):
        Wm, _l = pesi_settori(rp, Uv, sig, rng.permutation(sett))
        dm = conto(Wm)
        dm = dm[dm.index >= se.INIZIO]
        finti.append(te.numeri_settimana(dm["netto"])["sharpe"])
    vero = e["intero"]["sharpe"]
    e["mescolati"] = {"sharpe_medio": float(np.mean(finti)), "massimo": float(np.max(finti)),
                      "sopra_o_pari": int(sum(1 for v in finti if v >= vero)), "sharpe": [float(v) for v in finti]}
    regge_mescolati = e["mescolati"]["sopra_o_pari"] <= 1
    e["esito"] = e["esito_esame"] if regge_mescolati else f"no: i settori mescolati fanno come quelli veri ({e['esito_esame']})"
    # per capire
    lt = [x for x, t in zip(lati, tieni) if t]
    e["settimane_ferme"] = int(sum(1 for x in lt if x is None))
    e["settimane"] = int(tieni.sum())
    freq = {"long": {}, "short": {}}
    for x in lt:
        if x:
            for lato in ("long", "short"):
                for n in x[lato]:
                    freq[lato][n] = freq[lato].get(n, 0) + 1
    e["frequenza_lati"] = freq
    e["settori_mediana"] = float(np.median([x["settori"] for x in lt if x])) if any(lt) else None
    altre = {}
    for w in (1, 12):
        Wa, _l = pesi_settori(rendimento_passato(pan, idx, w), Uv, sig, sett)
        da = conto(Wa)
        ea = te.esame(da, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
        altre[w] = {"sharpe": ea["intero"]["sharpe"], "annuo": ea["intero"]["annuo"], "per_anno": ea["per_anno"]}
    e["altre_finestre"] = altre
    f5 = pd.read_csv(QUI.parent / "programma6" / "risultati_controllo_parita" / "settimane_F5.csv.gz", index_col=0)
    d = df[df.index >= se.INIZIO]
    c = d.index.intersection(f5.index)
    e["correlazione_F5"] = float(np.corrcoef(d.loc[c, "netto"], f5.loc[c, "netto"])[0, 1]) if len(c) > 10 else None
    g1 = pd.read_csv(QUI / "risultati_ottantesima" / "settimane_G1.csv.gz", index_col=0)
    c = d.index.intersection(g1.index)
    e["correlazione_G1"] = float(np.corrcoef(d.loc[c, "netto"], g1.loc[c, "netto"])[0, 1]) if len(c) > 10 else None
    e["settimane_comuni_G1"] = int(len(c))
    out["SM"] = e
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda x: "—" if x is None or x != x else f"{100 * x:+.1f}%"  # noqa: E731
    i = e["intero"]
    m = e["mescolati"]
    righe = ["# Programma 7 — risultati dell'ottantunesima prova (SM: il momento dei settori, a settimana)", "",
             "Regole in `OTTANTUNESIMA.md` (scritte prima). Dal 4 gennaio 2021 a fine settembre 2026, settori della prova 142, come F5.", "",
             f"* **SM: Sharpe {i['sharpe']:.2f}**, {pc(i['annuo'])} l'anno, volatilità {100 * i['volatilita']:.1f}%, discesa "
             f"{100 * i['discesa_max']:.1f}%; spese {100 * e['spese_annue']:.1f}% l'anno; lato long {pc(e['long_annuo'])}, short "
             f"{pc(e['short_annuo'])} l'anno.",
             "  * Per anno: " + ", ".join(f"{a} {pc(x)}" for a, x in e["per_anno"].items()) + ".",
             f"  * Settimane ferme (meno di 4 settori con almeno 5 monete): {e['settimane_ferme']} su {e['settimane']}; settori validi, "
             f"mediana {e['settori_mediana']}.",
             "  * Settimane da ciascun lato: long " + ", ".join(f"{k} {v}" for k, v in sorted(freq["long"].items(), key=lambda z: -z[1]))
             + "; short " + ", ".join(f"{k} {v}" for k, v in sorted(freq["short"].items(), key=lambda z: -z[1])) + ".",
             f"* **Settori mescolati a caso** ({MESCOLATE} volte): Sharpe medio {m['sharpe_medio']:.2f}, il più alto {m['massimo']:.2f}; "
             f"{m['sopra_o_pari']} su {MESCOLATE} pari o sopra quello vero.",
             f"* Per capire: con 1 settimana di formazione Sharpe {altre[1]['sharpe']:.2f} ({pc(altre[1]['annuo'])} l'anno), con 12 "
             f"settimane {altre[12]['sharpe']:.2f} ({pc(altre[12]['annuo'])}); correlazione con F5 "
             f"{'—' if e['correlazione_F5'] is None else format(e['correlazione_F5'], '.2f')}"
             f", con G1 {'—' if e['correlazione_G1'] is None else format(e['correlazione_G1'], '.2f')} ({e['settimane_comuni_G1']} settimane).",
             f"* Sharpe corretto con l'aggiunta {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi); t {e['t']:.2f}; regola del proprietario: "
             f"{'sì' if e['regola_proprietario'] else 'no'}.", "",
             f"**Esito: {e['esito']}**."]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_OTTANTUNESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("OTTANTUNESIMA FINITA", flush=True)
