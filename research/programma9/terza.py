"""Programma 9, terza prova (TERZA.md): la regola P9C identica dal 1° gennaio 2023 al 26 giugno 2026 (i due tratti delle prove 76 e
75, con le 30 monete piu' grandi tolte in ciascuno).

Uso: python3 -m research.programma9.terza
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import quarantunesima as qu
from research.programma6 import seconda as sc
from research.programma6 import terza as te
from research.programma6 import trentesima as tr
from research.programma9 import seconda as p9c

QUI = Path(__file__).parent
RIS = QUI / "risultati_terza"
TRATTI = ((sc.giorno(2023, 1, 1), sc.giorno(2024, 12, 31)), (sc.giorno(2025, 1, 1), sc.giorno(2026, 6, 26)))
PROVE_A_EVENTI = 22


def esegui(log=print) -> dict:
    pan = sc.pannello()
    df = pd.concat([p9c.operazioni(pan, da, a, log) for da, a in TRATTI], ignore_index=True)
    df = df.sort_values(["data", "segnale_min"]).reset_index(drop=True)
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "eventi_P9C_lunga.csv", index=False)
    noto = df["funding_8h"].notna()
    aff = df[noto & (df["funding_8h"] >= p9c.SOGLIA_8H)].reset_index(drop=True)
    alt = df[noto & (df["funding_8h"] < p9c.SOGLIA_8H)]
    ex_ = tr.esame(aff, "r")
    per_anno = {}
    for anno in sorted(df["data"].str[:4].unique()):
        a_, b_ = aff[aff["data"].str[:4] == anno], alt[alt["data"].str[:4] == anno]
        per_anno[anno] = {"affollati_n": len(a_), "affollati": float(a_["r"].mean()) if len(a_) else None,
                          "funding_basso_n": len(b_), "funding_basso": float(b_["r"].mean()) if len(b_) else None}
    ev = pd.DataFrame({"simbolo": aff["simbolo"], "ora": aff["entrata_min"] // 60, "uscita_h": aff["uscita_min"] // 60 + 1, "r": aff["r"]})
    port = qu.portafoglio(ev)
    inizio = sc.giorno(2023, 1, 2)
    port_p = port[(port.index >= inizio) & (port.index <= TRATTI[-1][1])]
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    p = te.esame(port_p, btc, inizio=inizio, anni_pieni=(2023, 2024, 2025))
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), "82 P9C": port["netto"]}, {"82 P9C": p["intero"]})
    rr = rivisto["candidate"]["82 P9C"]
    p["sharpe_corretto"], p["t"], p["gruppi"] = rr["corretto_con_aggiunta"], rr["t"], rivisto["gruppi"]
    p["esito"] = te.esito(p, p["sharpe_corretto"])
    ogni_anno = all((v["affollati"] or -1) > 0 for v in per_anno.values())
    soglia = 0.01 / PROVE_A_EVENTI
    esito = ("VALIDA" if ex_["esito"] == "VALIDA" and ex_["boot"]["p"] <= soglia and ogni_anno else
             f"non valida (operazioni: {ex_['esito']}; ogni anno positiva: {'sì' if ogni_anno else 'no'})")
    out = {"operazioni": len(df), "affollati": len(aff), "funding_basso": len(alt), "senza_funding": int((~noto).sum()),
           "esame": ex_, "per_anno": per_anno, "portafoglio": p, "esito": esito, "soglia_tutte": soglia,
           "media_funding_basso": float(alt["r"].mean()) if len(alt) else None,
           "protezione_affollati": float((aff["motivo"] == "protezione").mean()),
           "protezione_funding_basso": float((alt["motivo"] == "protezione").mean()) if len(alt) else None}
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    b, i = ex_["boot"], p["intero"]
    pc = lambda x: "—" if x is None else f"{100 * x:+.2f}%"  # noqa: E731
    righe = ["# Programma 9 — risultati della terza prova (P9C sulla regola identica, 2023 – giugno 2026)", "",
             "Regole in `TERZA.md` (scritte prima).", "",
             f"* {len(df)} operazioni della regola delle fiammate (senza il funding noto: {out['senza_funding']}); **con i long affollati "
             f"{len(aff)}: {pc(b['media'])} a operazione** (intervallo {pc(b['basso'])}; {pc(b['alto'])}, p {b['p']:.4f}), vinte "
             f"{100 * ex_['vinti']:.0f}%, alla protezione {100 * out['protezione_affollati']:.1f}%; metà {pc(ex_['prima_meta'])} e "
             f"{pc(ex_['seconda_meta'])}; senza le 5 migliori {pc(ex_['senza_5_migliori'])}.",
             f"* Con il funding basso: {len(alt)} operazioni, {pc(out['media_funding_basso'])} a operazione, alla protezione "
             f"{100 * (out['protezione_funding_basso'] or 0):.1f}%.",
             "* Per anno (long affollati / funding basso): " + "; ".join(
                 f"{a} {pc(v['affollati'])} ({v['affollati_n']}) / {pc(v['funding_basso'])} ({v['funding_basso_n']})" for a, v in per_anno.items()) + ".",
             f"* Portafoglio (5% a operazione, al massimo 20 aperte), dal 2 gennaio 2023: Sharpe {i['sharpe']:.2f}, {100 * i['annuo']:+.1f}% "
             f"l'anno, discesa {100 * i['discesa_max']:.1f}%; Sharpe corretto {p['sharpe_corretto']:.2f} ({p['gruppi']} gruppi), t {p['t']:.2f}.", "",
             f"**Esito: {esito}** (soglia contando le {PROVE_A_EVENTI} prove a eventi: {soglia:.5f}). **Portafoglio: {p['esito']}**."]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_TERZA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("P9C LUNGA FINITA", flush=True)
