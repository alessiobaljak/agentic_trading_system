"""Programma 7, ventottesima prova (VENTOTTESIMA.md): N3V, le 613 vendite delle monete nuove al 7° giorno (prova 32) divise fra
«davvero nuove» (nate su Binance entro 3 giorni dal contratto di Gate.io, o mai su Gate) e «già scoperte» (su Gate da almeno 30
giorni prima), dal 2023.

Uso: python3 -m research.programma7.ventottesima
"""
from __future__ import annotations

import gzip
import json
from pathlib import Path

import pandas as pd

from research.programma6 import seconda as sc
from research.programma6 import trentesima as tr
from research.programma6 import ventisettesima as vt
from research.programma9.quarta import differenza

QUI = Path(__file__).parent
RIS = QUI / "risultati_ventottesima"
EVENTI = QUI.parent / "programma6" / "risultati_trentaduesima" / "eventi_N3B.csv"
DA = "2023-01-01"
PROVE_A_EVENTI = 24


def primo_giorno_gate() -> dict:
    """{nome del contratto di Gate: (primo giorno, mese del primo file)} dai file giornalieri gia' scaricati."""
    primi = {}
    for f in (vt.DATI / "candlesticks_1d").glob("*/*.csv.gz"):
        nome = f.name.rsplit("-", 1)[0]
        if nome not in primi or f.parent.name < primi[nome][0]:
            primi[nome] = (f.parent.name, f)
    out = {}
    for nome, (mese, f) in primi.items():
        try:
            righe = [r.split(",") for r in gzip.decompress(f.read_bytes()).decode().split() if r]
            out[nome] = (min(int(r[0]) // 86400 for r in righe), mese)
        except Exception:  # noqa: BLE001
            continue
    return out


def base(simbolo: str) -> str:
    for pre in ("1000000", "1000", "1M"):
        if simbolo.startswith(pre):
            return simbolo[len(pre):-4]
    return simbolo[:-4]


def gruppo(simbolo: str, g_perp: int, gate: dict) -> str:
    g = gate.get(f"{base(simbolo)}_USDT")
    if g is None:
        return "A davvero nuove"
    g0, mese = g
    if mese <= "202301":
        return "fuori: copertura di Gate mancante"
    d = g_perp - g0
    if d >= 30:
        return "B gia' scoperte"
    if d >= 4:
        return "fuori: Gate da 4-29 giorni prima"
    if d >= -3:
        return "A davvero nuove"
    return "fuori: Gate dopo"


def esegui(log=print) -> dict:
    ev = pd.read_csv(EVENTI)
    ev = ev[ev["data"] >= DA].reset_index(drop=True)
    gate = primo_giorno_gate()
    ev["g_perp"] = ev["data"].map(lambda d: sc.giorno(*map(int, d.split("-")))) - tr.ETA
    ev["gruppo"] = [gruppo(s, g, gate) for s, g in zip(ev["simbolo"], ev["g_perp"])]
    RIS.mkdir(exist_ok=True)
    ev.to_csv(RIS / "eventi_N3V.csv", index=False)
    A = ev[ev["gruppo"] == "A davvero nuove"].reset_index(drop=True)
    B = ev[ev["gruppo"] == "B gia' scoperte"].reset_index(drop=True)
    ex_a, ex_b = tr.esame(A, "r"), tr.esame(B, "r")
    dif = differenza(A, B)
    fuori = {g: {"n": int(len(x)), "media": float(x["r"].mean())} for g, x in ev.groupby("gruppo") if g.startswith("fuori")}
    per_anno = {}
    for anno in sorted(ev["data"].str[:4].unique()):
        a_, b_ = A[A["data"].str[:4] == anno], B[B["data"].str[:4] == anno]
        per_anno[anno] = {"A": (len(a_), float(a_["r"].mean()) if len(a_) else None), "B": (len(b_), float(b_["r"].mean()) if len(b_) else None)}
    soglia = 0.01 / PROVE_A_EVENTI
    migliore = dif["p"] <= 0.05 and dif["differenza"] > 0
    esito = ("VALIDA: le davvero nuove rendono di più" if ex_a["esito"] == "VALIDA" and migliore else
             f"non migliore (A: {ex_a['esito']}; differenza {100 * dif['differenza']:+.2f} punti, p {dif['p']:.3f})")
    out = {"eventi_dal_2023": len(ev), "A": ex_a, "B": ex_b, "differenza": dif, "fuori": fuori, "per_anno": per_anno, "esito": esito,
           "soglia_tutte": soglia, "uscite_A": float(A["fermata"].mean()), "uscite_B": float(B["fermata"].mean())}
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda x: "—" if x is None else f"{100 * x:+.2f}%"  # noqa: E731
    a, b = ex_a["boot"], ex_b["boot"]
    righe = ["# Programma 7 — risultati della ventottesima prova (N3V: le monete davvero nuove contro quelle già scoperte)", "",
             "Regole in `VENTOTTESIMA.md` (scritte prima). Le operazioni della prova 32 dal 2023.", "",
             f"* **A, davvero nuove**: {a['eventi']} operazioni, **{pc(a['media'])} a operazione** (p {a['p']:.4f}), mediana {pc(ex_a['mediana'])}, "
             f"vinte {100 * ex_a['vinti']:.0f}%, uscita a +30% nel {100 * out['uscite_A']:.0f}%; metà {pc(ex_a['prima_meta'])} e "
             f"{pc(ex_a['seconda_meta'])}; senza le 5 migliori {pc(ex_a['senza_5_migliori'])}.",
             f"* **B, già scoperte** (su Gate da almeno 30 giorni): {b['eventi']} operazioni, {pc(b['media'])} a operazione (p {b['p']:.4f}), "
             f"uscita a +30% nel {100 * out['uscite_B']:.0f}%.",
             f"* Differenza A − B: {100 * dif['differenza']:+.2f} punti (intervallo {100 * dif['basso']:+.2f}; {100 * dif['alto']:+.2f}, p {dif['p']:.3f}).",
             "* Fuori dai gruppi (solo per capire): " + "; ".join(f"{g} {v['n']} ({pc(v['media'])})" for g, v in fuori.items()) + ".",
             "* Per anno (A / B): " + "; ".join(f"{y} {pc(v['A'][1])} ({v['A'][0]}) / {pc(v['B'][1])} ({v['B'][0]})" for y, v in per_anno.items()) + ".",
             "", f"**Esito: {esito}** (soglia contando le {PROVE_A_EVENTI} prove a eventi: {soglia:.5f})."]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_VENTOTTESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("VENTOTTESIMA FINITA", flush=True)
