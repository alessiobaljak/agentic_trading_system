"""Programma 7, ventisettesima prova (VENTISETTESIMA.md): F5C, F5 con l'esposizione secondo il carry atteso (la differenza di
funding fra i due lati, nota prima), fattore fra 0,5 e 1,5 rispetto alla mediana delle 26 settimane prima; controllo con il fattore
mescolato fra le settimane.

Uso: python3 -m research.programma7.ventisettesima
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

QUI = Path(__file__).parent
RIS = QUI / "risultati_ventisettesima"
FINESTRA, MIN_SETT = 26, 8
LIMITI = (0.5, 1.5)
SEME = 2026


def carry_atteso(W: np.ndarray, f7: np.ndarray) -> np.ndarray:
    """Per settimana: Σ_short |w|·f7 − Σ_long w·f7 (il funding che lo short incassa meno quello che il long paga)."""
    f = np.nan_to_num(f7)
    return (np.where(W < 0, -W, 0.0) * f).sum(axis=1) - (np.where(W > 0, W, 0.0) * f).sum(axis=1)


def fattore(carry: np.ndarray, finestra: int = FINESTRA, minimo: int = MIN_SETT, limiti: tuple = LIMITI) -> np.ndarray:
    """Il carry atteso diviso la mediana delle ``finestra`` settimane precedenti (almeno ``minimo``; prima vale 1), entro ``limiti``."""
    out = np.ones(len(carry))
    for k in range(len(carry)):
        prima = carry[max(0, k - finestra):k]
        if len(prima) >= minimo:
            med = float(np.median(prima))
            if med > 0:
                out[k] = float(np.clip(carry[k] / med, *limiti))
    return out


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    lun = ps["lunedi"] - pan["t0"]
    sig = ot.sigma_30(pan, lun)
    costo = sc.costi_moneta(ps["simboli"])
    f7 = se.funding_7(pan, lun)
    W = vq.pesi_banda(np.where(np.isfinite(sig), -f7, np.nan), ps["U"], sig)
    carry = carry_atteso(W, f7)
    fat = fattore(carry)
    rng = np.random.default_rng(SEME)
    fat_mescolato = fat.copy()
    dentro = ps["lunedi"] >= se.INIZIO
    fat_mescolato[dentro] = rng.permutation(fat[dentro])
    conti = {}
    for nome, Wx in (("F5", W), ("F5C", W * fat[:, None]), ("F5 fattore mescolato", W * fat_mescolato[:, None])):
        d = te.conto(Wx, ps["R"], ps["F"], costo)
        d.index = ps["lunedi"]
        conti[nome] = d
    RIS.mkdir(exist_ok=True)
    for nome, d in conti.items():
        d.to_csv(RIS / f"settimane_{nome.replace(' ', '_')}.csv.gz")
    pd.DataFrame({"carry_atteso": carry, "fattore": fat, "fattore_mescolato": fat_mescolato}, index=ps["lunedi"]).to_csv(RIS / "carry.csv.gz")
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    out = {n: te.esame(d, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI) for n, d in conti.items()}
    f5 = conti["F5"][dentro]
    out["carry"] = {"medio_settimana": float(carry[dentro].mean()), "fattore_medio": float(fat[dentro].mean()),
                    "settimane_al_limite": int(((fat[dentro] <= LIMITI[0]) | (fat[dentro] >= LIMITI[1])).sum()),
                    "quota_funding_su_netto": float(-f5["funding"].sum() / f5["netto"].sum()) if f5["netto"].sum() else None,
                    "correlazione_carry_netto_F5": float(np.corrcoef(carry[dentro], f5["netto"].to_numpy())[0, 1]),
                    "correlazione_carry_funding_F5": float(np.corrcoef(carry[dentro], -f5["funding"].to_numpy())[0, 1])}
    serie = {**ast.serie_nuove(), "89 F5C": conti["F5C"]["netto"], "89 F5 mescolato": conti["F5 fattore mescolato"]["netto"]}
    rivisto = ast.corretto_rivisto(serie, {"89 F5C": out["F5C"]["intero"], "89 F5 mescolato": out["F5 fattore mescolato"]["intero"]})
    for n, chiave in (("F5C", "89 F5C"), ("F5 fattore mescolato", "89 F5 mescolato")):
        r = rivisto["candidate"][chiave]
        out[n]["sharpe_corretto"], out[n]["t"], out[n]["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
        out[n]["esito"] = te.esito(out[n], out[n]["sharpe_corretto"])
        out[n]["regola_del_proprietario"] = bool(out[n]["sharpe_corretto"] >= 0.90 and all(v > 0 for v in out[n]["per_anno"].values())
                                                 and out[n]["t"] > 3)
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    c = out["carry"]
    righe = ["# Programma 7 — risultati della ventisettesima prova (F5C: l'esposizione secondo il carry atteso)", "",
             "Regole in `VENTISETTESIMA.md` (scritte prima). Dal 4 gennaio 2021.", "",
             "| | Sharpe | l'anno | volatilità | discesa | spese l'anno | per anno |", "|---|---|---|---|---|---|---|"]
    for n in ("F5", "F5C", "F5 fattore mescolato"):
        i = out[n]["intero"]
        righe.append(f"| {n} | {i['sharpe']:.2f} | {100 * i['annuo']:+.1f}% | {100 * i['volatilita']:.1f}% | {100 * i['discesa_max']:.1f}% | "
                     f"{100 * out[n]['spese_annue']:.1f}% | " + ", ".join(f"{y} {100 * v:+.1f}%" for y, v in out[n]["per_anno"].items()) + " |")
    righe += ["",
              f"* Carry atteso medio {100 * c['medio_settimana']:+.2f}% a settimana; fattore medio {c['fattore_medio']:.2f}, settimane al limite "
              f"{c['settimane_al_limite']}; quota del netto di F5 che viene dal funding {100 * (c['quota_funding_su_netto'] or 0):.0f}%.",
              f"* Correlazione del carry atteso con il netto di F5 della settimana {c['correlazione_carry_netto_F5']:.2f}, con il funding "
              f"incassato {c['correlazione_carry_funding_F5']:.2f}.",
              *(f"* **{n}**: Sharpe corretto {out[n]['sharpe_corretto']:.2f} ({out[n]['gruppi']} gruppi), t {out[n]['t']:.2f}; esito "
                f"{out[n]['esito']}; regola del proprietario: {'sì' if out[n]['regola_del_proprietario'] else 'no'}."
                for n in ("F5C", "F5 fattore mescolato"))]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_VENTISETTESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("VENTISETTESIMA FINITA", flush=True)
