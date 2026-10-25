"""Programma 7, trentaduesima prova (TRENTADUESIMA.md): G1N-S, G1 neutra al mercato (prova 88) con l'interruttore sulle perdite del
conto (prova 93): le due protezioni insieme; controllo con le pause messe a caso.

Uso: python3 -m research.programma7.trentaduesima
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
from research.programma7 import prima as pr
from research.programma7 import trentunesima as tu
from research.programma7 import ventiquattresima as f5n

QUI = Path(__file__).parent
RIS = QUI / "risultati_trentaduesima"


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    giorni = np.arange(se.INIZIO, pr.FINE, dtype=np.int64)
    idx = giorni - pan["t0"]
    Ud = pr.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
    sig = ot.sigma_30(pan, idx)
    W = vq.pesi_banda(np.where(np.isfinite(sig), -se.funding_7(pan, idx), np.nan), Ud, sig)
    beta = f5n.beta_delle_monete(pan, Ud, idx)
    WN = f5n.scala_neutra(W, beta)[0]
    R, F = sc.rendimenti(pan)[idx], np.nan_to_num(pan["funding"][idx])
    costo = sc.costi_moneta(pan["simboli"])
    WS, _, inizi_s = tu.con_interruttore(W, R, F, costo)            # G1-S (prova 93), per il confronto
    WNS, netti_ns, inizi = tu.con_interruttore(WN, R, F, costo)      # G1N-S
    log(f"[trentaduesima] pesi fatti: G1N-S {len(inizi)} pause, G1-S {len(inizi_s)}")
    conti, giorni_conti, ordini = {}, {}, {}
    for nome, Wx in (("G1", W), ("G1N", WN), ("G1-S", WS), ("G1N-S", WNS)):
        conti[nome], giorni_conti[nome], ordini[nome] = tu._conto_limite(Wx, R, F, giorni, pan["simboli"], costo)
        log(f"[trentaduesima] {nome}: conto con gli ordini limite fatto")
    g1n_m, g1ns_m = te.conto(WN, R, F, costo), te.conto(WNS, R, F, costo)
    assert np.allclose(g1ns_m["netto"].to_numpy(), netti_ns)
    rng = np.random.default_rng(tu.SEME)
    caso = pd.DataFrame([{k: v for k, v in te.numeri_settimana(pr.per_settimana(te.conto(tu.pause_a_caso(WN, len(inizi), rng), R, F, costo), giorni)["netto"]).items()
                          if k in ("sharpe", "annuo", "discesa_max")} for _ in range(tu.ESTRAZIONI)]) if inizi else pd.DataFrame(columns=["sharpe", "annuo", "discesa_max"])
    a_mercato = {n: te.numeri_settimana(pr.per_settimana(d, giorni)["netto"]) for n, d in (("G1N", g1n_m), ("G1N-S", g1ns_m))}
    RIS.mkdir(exist_ok=True)
    for nome, d in conti.items():
        d.to_csv(RIS / f"settimane_{nome}.csv.gz")
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    out = {n: te.esame(d, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI) for n, d in conti.items()}
    dg = giorni_conti["G1N"]
    pause = []
    for d0 in inizi:
        fine = min(d0 + tu.PAUSA, len(giorni))
        pause.append({"da": sc.data(int(giorni[d0])), "a": sc.data(int(giorni[fine - 1])), "G1N_nei_giorni_fermi": float(dg["netto"].iloc[d0:fine].sum()),
                      "G1N_nei_30_giorni_prima": float(dg["netto"].iloc[max(0, d0 - 30):d0].sum()),
                      "coincide_con_G1S": bool(any(abs(d0 - e) <= 7 for e in inizi_s))})
    out["pause"] = pause
    out["pause_G1S"] = [sc.data(int(giorni[d0])) for d0 in inizi_s]
    out["giorni_fermi"] = int(sum(min(d0 + tu.PAUSA, len(giorni)) - d0 for d0 in inizi))
    out["G1N_nei_giorni_fermi_totale"] = float(sum(p["G1N_nei_giorni_fermi"] for p in pause))
    peggiori = conti["G1"].nsmallest(15, "netto").index
    out["quindici_peggiori"] = {n: float(conti[n].loc[peggiori, "netto"].mean()) for n in conti}
    out["a_mercato"] = a_mercato
    out["pause_a_caso"] = ({"estrazioni": int(len(caso)), "sharpe_medio": float(caso["sharpe"].mean()), "annuo_medio": float(caso["annuo"].mean()),
                            "discesa_media": float(caso["discesa_max"].mean()), "discesa_minima": float(caso["discesa_max"].max()),
                            "quota_con_discesa_minore_di_G1NS": float((caso["discesa_max"] >= a_mercato["G1N-S"]["discesa_max"]).mean())}
                           if len(caso) else None)
    out["correlazioni"] = {"G1N-S/G1N": float(np.corrcoef(conti["G1N-S"]["netto"], conti["G1N"]["netto"])[0, 1]),
                           "G1N-S/G1": float(np.corrcoef(conti["G1N-S"]["netto"], conti["G1"]["netto"])[0, 1])}
    out["ordini"] = ordini
    serie = {**ast.serie_nuove(), "94 G1N-S": conti["G1N-S"]["netto"]}
    rivisto = ast.corretto_rivisto(serie, {"94 G1N-S": out["G1N-S"]["intero"]})
    r = rivisto["candidate"]["94 G1N-S"]
    e = out["G1N-S"]
    e["sharpe_corretto"], e["t"], e["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
    e["esito"] = te.esito(e, e["sharpe_corretto"])
    e["regola_del_proprietario"] = bool(e["sharpe_corretto"] >= 0.90 and all(v > 0 for v in e["per_anno"].values()) and e["t"] > 3)
    iN, iS, iNS = out["G1N"]["intero"], out["G1-S"]["intero"], e["intero"]
    pz = out["pause_a_caso"]
    out["aggiunge_a_G1N"] = bool(inizi and iNS["discesa_max"] > iN["discesa_max"] and iNS["sharpe"] >= iN["sharpe"]
                                 and a_mercato["G1N-S"]["discesa_max"] > pz["discesa_media"])
    out["le_due_protezioni_si_sommano"] = bool(iNS["discesa_max"] > iN["discesa_max"] and iNS["discesa_max"] > iS["discesa_max"])
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda x: f"{100 * x:+.1f}%"  # noqa: E731
    righe = ["# Programma 7 — risultati della trentaduesima prova (G1N-S: la neutralità al mercato e l'interruttore insieme)", "",
             "Regole in `TRENTADUESIMA.md` (scritte prima). Dal 4 gennaio 2021 al 5 ottobre 2026, con gli ordini limite.", "",
             "| | Sharpe | l'anno | volatilità | discesa | spese l'anno | per anno |", "|---|---|---|---|---|---|---|"]
    for n in ("G1", "G1N", "G1-S", "G1N-S"):
        i = out[n]["intero"]
        righe.append(f"| {n} | {i['sharpe']:.2f} | {pc(i['annuo'])} | {100 * i['volatilita']:.1f}% | {100 * i['discesa_max']:.1f}% | "
                     f"{100 * out[n]['spese_annue']:.1f}% | " + ", ".join(f"{y} {pc(v)}" for y, v in out[n]["per_anno"].items()) + " |")
    righe += ["",
              f"* **{len(pause)} pause** di G1N-S, {out['giorni_fermi']} giorni fermi: " + ("; ".join(
                  f"{p['da']} → {p['a']} (G1N nei giorni fermi {pc(p['G1N_nei_giorni_fermi'])}, nei 30 prima {pc(p['G1N_nei_30_giorni_prima'])}"
                  f"{', come G1-S' if p['coincide_con_G1S'] else ''})" for p in pause) if pause else "nessuna") + f". Le pause di G1-S: {', '.join(out['pause_G1S'])}.",
              f"* Nei giorni fermi G1N avrebbe fatto in totale **{pc(out['G1N_nei_giorni_fermi_totale'])}**.",
              "* Le 15 settimane peggiori di G1, rifatte: " + ", ".join(f"{n} {100 * v:+.2f}%" for n, v in out["quindici_peggiori"].items())
              + f". Correlazione G1N-S/G1N {out['correlazioni']['G1N-S/G1N']:.3f}, G1N-S/G1 {out['correlazioni']['G1N-S/G1']:.3f}.",
              (f"* A mercato: G1N Sharpe {a_mercato['G1N']['sharpe']:.2f}, discesa {100 * a_mercato['G1N']['discesa_max']:.1f}%; G1N-S Sharpe "
               f"{a_mercato['G1N-S']['sharpe']:.2f}, discesa {100 * a_mercato['G1N-S']['discesa_max']:.1f}%. **Pause a caso** su G1N ({pz['estrazioni']} estrazioni): "
               f"Sharpe medio {pz['sharpe_medio']:.2f}, discesa media {100 * pz['discesa_media']:.1f}% (la meno profonda {100 * pz['discesa_minima']:.1f}%); nel "
               f"{100 * pz['quota_con_discesa_minore_di_G1NS']:.0f}% delle estrazioni la discesa è minore o uguale a quella di G1N-S.") if pz else "* Nessuna pausa: nessun controllo.",
              f"* **G1N-S**: Sharpe corretto {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi), t {e['t']:.2f}; esito {e['esito']}; regola del "
              f"proprietario: {'sì' if e['regola_del_proprietario'] else 'no'}.", "",
              f"**Aggiunge qualcosa a G1N: {'sì' if out['aggiunge_a_G1N'] else 'no'}. Le due protezioni si sommano (discesa sotto quella di G1N e di G1-S): "
              f"{'sì' if out['le_due_protezioni_si_sommano'] else 'no'}.**"]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_TRENTADUESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("TRENTADUESIMA FINITA", flush=True)
