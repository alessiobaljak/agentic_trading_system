"""Programma 7, trentunesima prova (TRENTUNESIMA.md): G1-S, G1 con l'interruttore sulle perdite del conto: dopo una discesa del 15%
dal massimo si chiude tutto per 7 giorni, poi si riparte e il massimo di riferimento si azzera; controllo con le pause messe a caso.

Uso: python3 -m research.programma7.trentunesima
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
from research.programma7 import prima as pr

QUI = Path(__file__).parent
RIS = QUI / "risultati_trentunesima"
SOGLIA = 0.15            # la discesa dal massimo che fa scattare la pausa
PAUSA = 7                # giorni fermi
ESTRAZIONI, SEME = 20, 2026


def con_interruttore(W: np.ndarray, R: np.ndarray, F: np.ndarray, costo: np.ndarray, soglia: float = SOGLIA, pausa: int = PAUSA) -> tuple:
    """I pesi giornalieri con l'interruttore (il conto a mercato come in ``terza.conto``): il giorno d, se il conto alla fine di d-1 e'
    sceso di almeno ``soglia`` dal massimo, pesi a zero per ``pausa`` giorni; alla fine della pausa il massimo si azzera al conto.
    Ritorna (pesi, netto giornaliero a mercato, giorni d'inizio delle pause)."""
    T, S = W.shape
    R0 = np.nan_to_num(R)
    Wn = W.copy()
    netti = np.zeros(T)
    deriva = np.zeros(S)
    conto, massimo, fermo_fino, inizi = 1.0, 1.0, -1, []
    for d in range(T):
        if d > fermo_fino and conto / massimo - 1 <= -soglia:
            fermo_fino = d + pausa - 1
            inizi.append(d)
        if d <= fermo_fino:
            Wn[d] = 0.0
        x = Wn[d]
        netto = float((x * R0[d]).sum() - (np.abs(x - deriva) * costo).sum() - (x * F[d]).sum())
        netti[d] = netto
        conto *= 1 + netto
        deriva = x * (1 + R0[d]) / (1 + netto) if 1 + netto > 0 else np.zeros(S)
        massimo = conto if d == fermo_fino else max(massimo, conto)
    return Wn, netti, inizi


def pause_a_caso(W: np.ndarray, n_pause: int, rng: np.random.Generator, pausa: int = PAUSA) -> np.ndarray:
    """Gli stessi pesi con ``n_pause`` pause di ``pausa`` giorni messe a caso, senza sovrapposizioni."""
    T = W.shape[0]
    while True:
        inizi = np.sort(rng.choice(T - pausa + 1, size=n_pause, replace=False))
        if n_pause < 2 or (np.diff(inizi) >= pausa).all():
            break
    Wn = W.copy()
    for d in inizi:
        Wn[d:d + pausa] = 0.0
    return Wn


def _conto_limite(Wx: np.ndarray, R: np.ndarray, F: np.ndarray, giorni: np.ndarray, simboli: list, costo: np.ndarray) -> tuple:
    mercato = te.conto(Wx, R, F, costo)
    spese, n_tot, n_lim, _ = cs.spese_a_limite(Wx, R, giorni, simboli, costo)
    d = mercato.copy()
    d["spese"] = spese
    d["netto"] = d["lordo"] - d["spese"] - d["funding"]
    d["netto_doppio"] = d["lordo"] - 2 * d["spese"] - d["funding"]
    return pr.per_settimana(d, giorni), d, {"variazioni": n_tot, "a_limite": n_lim}


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    giorni = np.arange(se.INIZIO, pr.FINE, dtype=np.int64)
    idx = giorni - pan["t0"]
    Ud = pr.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
    sig = ot.sigma_30(pan, idx)
    W = vq.pesi_banda(np.where(np.isfinite(sig), -se.funding_7(pan, idx), np.nan), Ud, sig)
    R, F = sc.rendimenti(pan)[idx], np.nan_to_num(pan["funding"][idx])
    costo = sc.costi_moneta(pan["simboli"])
    WS, netti_s, inizi = con_interruttore(W, R, F, costo)
    log(f"[trentunesima] pesi fatti: {len(inizi)} pause, {int((WS == 0).all(axis=1).sum() - (W == 0).all(axis=1).sum())} giorni fermi in piu'")
    conti, giorni_conti, ordini = {}, {}, {}
    for nome, Wx in (("G1", W), ("G1-S", WS)):
        conti[nome], giorni_conti[nome], ordini[nome] = _conto_limite(Wx, R, F, giorni, pan["simboli"], costo)
        log(f"[trentunesima] {nome}: conto con gli ordini limite fatto")
    # il controllo: le pause a caso, a mercato (anche G1 e G1-S a mercato per il confronto)
    g1_m = te.conto(W, R, F, costo)
    g1s_m = te.conto(WS, R, F, costo)
    assert np.allclose(g1s_m["netto"].to_numpy(), netti_s), "il conto a mercato dell'interruttore non torna"
    rng = np.random.default_rng(SEME)
    caso = []
    for _ in range(ESTRAZIONI):
        d = pr.per_settimana(te.conto(pause_a_caso(W, len(inizi), rng), R, F, costo), giorni)
        n = te.numeri_settimana(d["netto"])
        caso.append({"sharpe": n["sharpe"], "annuo": n["annuo"], "discesa_max": n["discesa_max"]})
    caso = pd.DataFrame(caso)
    a_mercato = {n: te.numeri_settimana(pr.per_settimana(d, giorni)["netto"]) for n, d in (("G1", g1_m), ("G1-S", g1s_m))}
    RIS.mkdir(exist_ok=True)
    for nome, d in conti.items():
        d.to_csv(RIS / f"settimane_{nome}.csv.gz")
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    out = {n: te.esame(d, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI) for n, d in conti.items()}
    # le pause: quando, e cosa avrebbe fatto G1 nei giorni fermi
    dg = giorni_conti["G1"]
    pause = []
    for d0 in inizi:
        fine = min(d0 + PAUSA, len(giorni))
        pause.append({"da": sc.data(int(giorni[d0])), "a": sc.data(int(giorni[fine - 1])),
                      "G1_nei_giorni_fermi": float(dg["netto"].iloc[d0:fine].sum()),
                      "G1_nei_30_giorni_prima": float(dg["netto"].iloc[max(0, d0 - 30):d0].sum())})
    out["pause"] = pause
    out["giorni_fermi"] = int(sum(min(d0 + PAUSA, len(giorni)) - d0 for d0 in inizi))
    out["G1_nei_giorni_fermi_totale"] = float(sum(p["G1_nei_giorni_fermi"] for p in pause))
    peggiori = conti["G1"].nsmallest(15, "netto").index
    out["quindici_peggiori"] = {n: float(conti[n].loc[peggiori, "netto"].mean()) for n in conti}
    out["a_mercato"] = a_mercato
    out["pause_a_caso"] = {"estrazioni": ESTRAZIONI, "sharpe_medio": float(caso["sharpe"].mean()), "annuo_medio": float(caso["annuo"].mean()),
                           "discesa_media": float(caso["discesa_max"].mean()), "discesa_minima": float(caso["discesa_max"].max()),
                           "quota_con_discesa_minore_di_G1S": float((caso["discesa_max"] >= a_mercato["G1-S"]["discesa_max"]).mean())}
    out["correlazione_G1S_G1"] = float(np.corrcoef(conti["G1-S"]["netto"], conti["G1"]["netto"])[0, 1])
    out["ordini"] = ordini
    serie = {**ast.serie_nuove(), "93 G1-S": conti["G1-S"]["netto"]}
    rivisto = ast.corretto_rivisto(serie, {"93 G1-S": out["G1-S"]["intero"]})
    r = rivisto["candidate"]["93 G1-S"]
    out["G1-S"]["sharpe_corretto"], out["G1-S"]["t"], out["G1-S"]["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
    out["G1-S"]["esito"] = te.esito(out["G1-S"], out["G1-S"]["sharpe_corretto"])
    out["G1-S"]["regola_del_proprietario"] = bool(out["G1-S"]["sharpe_corretto"] >= 0.90 and all(v > 0 for v in out["G1-S"]["per_anno"].values())
                                                   and out["G1-S"]["t"] > 3)
    i1, i2 = out["G1"]["intero"], out["G1-S"]["intero"]
    out["aggiunge_qualcosa"] = bool(i2["discesa_max"] > i1["discesa_max"] and i2["sharpe"] >= i1["sharpe"]
                                    and a_mercato["G1-S"]["discesa_max"] > out["pause_a_caso"]["discesa_media"])
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda x: f"{100 * x:+.1f}%"  # noqa: E731
    righe = ["# Programma 7 — risultati della trentunesima prova (G1-S: G1 con l'interruttore sulle perdite del conto)", "",
             "Regole in `TRENTUNESIMA.md` (scritte prima). Dal 4 gennaio 2021 al 5 ottobre 2026, con gli ordini limite.", "",
             "| | Sharpe | l'anno | volatilità | discesa | spese l'anno | per anno |", "|---|---|---|---|---|---|---|"]
    for n in ("G1", "G1-S"):
        i = out[n]["intero"]
        righe.append(f"| {n} | {i['sharpe']:.2f} | {pc(i['annuo'])} | {100 * i['volatilita']:.1f}% | {100 * i['discesa_max']:.1f}% | "
                     f"{100 * out[n]['spese_annue']:.1f}% | " + ", ".join(f"{y} {pc(v)}" for y, v in out[n]["per_anno"].items()) + " |")
    pz = out["pause_a_caso"]
    righe += ["",
              f"* **{len(pause)} pause**, {out['giorni_fermi']} giorni fermi: " + "; ".join(f"{p['da']} → {p['a']} (G1 nei giorni fermi {pc(p['G1_nei_giorni_fermi'])}, "
                                                                                       f"nei 30 prima {pc(p['G1_nei_30_giorni_prima'])})" for p in pause) + ".",
              f"* Nei giorni fermi G1 avrebbe fatto in totale **{pc(out['G1_nei_giorni_fermi_totale'])}** (positivo = la pausa ha saltato il recupero).",
              "* Le 15 settimane peggiori di G1, rifatte: " + ", ".join(f"{n} {100 * v:+.2f}%" for n, v in out["quindici_peggiori"].items())
              + f". Correlazione G1-S/G1 {out['correlazione_G1S_G1']:.3f}.",
              f"* A mercato: G1 Sharpe {a_mercato['G1']['sharpe']:.2f}, discesa {100 * a_mercato['G1']['discesa_max']:.1f}%; G1-S Sharpe "
              f"{a_mercato['G1-S']['sharpe']:.2f}, discesa {100 * a_mercato['G1-S']['discesa_max']:.1f}%. **Pause a caso** ({pz['estrazioni']} estrazioni, "
              f"stesso numero di pause): Sharpe medio {pz['sharpe_medio']:.2f}, discesa media {100 * pz['discesa_media']:.1f}% (la meno profonda "
              f"{100 * pz['discesa_minima']:.1f}%); nel {100 * pz['quota_con_discesa_minore_di_G1S']:.0f}% delle estrazioni la discesa è minore o uguale a quella di G1-S.",
              f"* **G1-S**: Sharpe corretto {out['G1-S']['sharpe_corretto']:.2f} ({out['G1-S']['gruppi']} gruppi), t {out['G1-S']['t']:.2f}; esito "
              f"{out['G1-S']['esito']}; regola del proprietario: {'sì' if out['G1-S']['regola_del_proprietario'] else 'no'}.", "",
              f"**Aggiunge qualcosa a G1 (discesa minore senza perdere Sharpe, e meglio delle pause a caso): {'sì' if out['aggiunge_qualcosa'] else 'no'}.**"]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_TRENTUNESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("TRENTUNESIMA FINITA", flush=True)
