"""Programma 7, quarantacinquesima prova (QUARANTACINQUESIMA.md): G13C, vendere i perpetui annunciati in chiusura con le date vere lette
dal testo degli annunci: short contro il Bitcoin dall'ora dopo l'annuncio a un'ora prima della chiusura, uscita a +30%; controllo prima.

Uso: python3 -m research.programma7.quarantacinquesima
"""
from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import esecuzione as es
from research.programma6 import seconda as sc
from research.programma6 import trentesima as tr
from research.programma7 import quarantunesima as lv
from research.programma7 import quindicesima as g13

QUI = Path(__file__).parent
RIS = QUI / "risultati_quarantacinquesima"
DATI = QUI.parent / "data" / "annunci" / "chiusure"
DATA = re.compile(r"(\d{4}-\d{2}-\d{2}) (\d{2}):(\d{2}) \(UTC\)")
FUORI = {"BTCUSDT", "ETHUSDT"}
MIN_ORE, CONTROLLI, SEME = 3, 20, 2026
PROVE_A_EVENTI = 32


def eventi(simboli_pannello: set) -> list:
    """[(simbolo, ms dell'annuncio, ms della chiusura, id)] dal testo degli annunci; un contratto vale una volta (il primo annuncio)."""
    elenco = json.loads((DATI / "elenco.json").read_text())
    visti, out = set(), []
    for a in sorted(elenco, key=lambda x: x["ms"]):
        f = DATI / f"{a['id']}.json"
        if not f.exists():
            continue
        testo = " ".join(lv.frammenti(json.loads(f.read_text())["body"]))
        ore = [lv._ms(*m.groups()) for m in DATA.finditer(testo)]
        dopo = [h for h in ore if h > int(a["ms"])]
        if not dopo:
            continue
        chiusura = max(dopo)
        for s in sorted(set(re.findall(r"\b[0-9A-Z]{2,20}USDT\b", testo + " " + a["titolo"]))):
            if s in FUORI or s not in simboli_pannello or s in visti:
                continue
            visti.add(s)
            out.append((s, int(a["ms"]), int(chiusura), a["id"]))
    return out


def esegui(log=print) -> dict:
    pan = sc.pannello()
    t0 = pan["t0"]
    giorni = np.arange(pan["close"].shape[0]) + t0
    jb = pan["simboli"].index("BTCUSDT")
    fb = pd.Series(pan["funding"][:, jb], index=giorni)
    ev = eventi(set(pan["simboli"]))
    log(f"[quarantacinquesima] {len(ev)} contratti con l'ora della chiusura; scarico le candele orarie")
    rng = np.random.default_rng(SEME)
    righe_ev, controlli = [], []
    for s, ms_a, ms_c, ida in ev:
        h_e, h_u = ms_a // 3_600_000 + 1, ms_c // 3_600_000 - 1
        if h_u - h_e < MIN_ORE:
            continue
        righe_ev.append((s, h_e, h_u, ida, ms_a))
        durata = h_u - h_e
        cand = np.arange(h_e - 365 * 24, h_e - 30 * 24 - durata)
        for h in rng.choice(cand, size=CONTROLLI, replace=False):
            controlli.append((s, int(h), int(h) + durata))
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(lambda x: lv.scarica_ore(x[0], x[1] - 24, x[2] + 24), [(s, a, b) for s, a, b, _, _ in righe_ev] + controlli))
    lv.scarica_ore("BTCUSDT", min(r[1] for r in righe_ev) - 400 * 24, max(r[2] for r in righe_ev) + 24)
    cb = es.ore_di("BTCUSDT")
    ore = {}

    def candele(s):
        if s not in ore:
            ore[s] = es.ore_di(s)
        return ore[s]
    righe = []
    for s, h_e, h_u, ida, ms_a in righe_ev:
        j = pan["simboli"].index(s)
        f = pd.Series(pan["funding"][:, j], index=giorni)
        con = g13.operazione(candele(s), cb, f, fb, h_e, h_u, True)
        senza = g13.operazione(candele(s), cb, f, fb, h_e, h_u, False)
        if con and senza:
            righe.append({"data": sc.data(h_e // 24), "annuncio": int((h_e // 24 + 3) // 7), "simbolo": s, "id_annuncio": ida,
                          "ore": con["ore"], "r": con["r"], "fermata": con["fermata"], "r_senza": senza["r"]})
    df = pd.DataFrame(righe)
    cr = []
    for s, a, b in controlli:
        j = pan["simboli"].index(s)
        op = g13.operazione(candele(s), cb, pd.Series(pan["funding"][:, j], index=giorni), fb, a, b, True)
        if op:
            cr.append({"simbolo": s, "r": op["r"]})
    co = pd.DataFrame(cr)
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "eventi_G13C.csv", index=False)
    co.to_csv(RIS / "controllo_G13C.csv", index=False)
    e_con, e_senza = tr.esame(df, "r"), tr.esame(df, "r_senza")
    per_moneta = co.groupby("simbolo")["r"].mean() if len(co) else pd.Series(dtype=float)
    diff = (df.set_index("simbolo")["r"] - per_moneta.reindex(df["simbolo"]).to_numpy()).dropna().to_numpy()
    bd = np.random.default_rng(SEME).choice(diff, size=(10000, len(diff)), replace=True).mean(axis=1) if len(diff) else np.array([np.nan])
    soglia = 0.01 / PROVE_A_EVENTI
    out = {"contratti": len(ev), "usati": int(len(df)), "con_uscita": e_con, "senza_uscita": e_senza, "fermate": float(df["fermata"].mean()),
           "ore_mediana": float(df["ore"].median()), "controllo_media": float(co["r"].mean()) if len(co) else None,
           "differenza": {"media": float(diff.mean()) if len(diff) else None, "p": float((bd <= 0).mean())}, "soglia_tutte": soglia}
    valida = e_con["esito"] == "VALIDA" and out["differenza"]["p"] <= 0.05
    out["esito"] = ("VALIDA" if valida and e_con["boot"]["p"] <= soglia else
                    "passa l'esame scritto ma non la soglia di tutte le prove a eventi" if valida else
                    e_con["esito"] if e_con["esito"] != "VALIDA" else "non sopra il controllo")
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda v: "—" if v is None else f"{100 * v:+.2f}%"  # noqa: E731
    b, bs = e_con["boot"], e_senza["boot"]
    testo = "\n".join([
        "# Programma 7 — risultati della quarantacinquesima prova (G13C: i perpetui annunciati in chiusura, con le date vere)", "",
        "Regole in `QUARANTACINQUESIMA.md` (scritte prima). Short contro il Bitcoin dall'ora dopo l'annuncio a un'ora prima della chiusura.", "",
        f"* {out['contratti']} contratti con l'ora della chiusura; **{b['eventi']} usati** (durata mediana {out['ore_mediana']:.0f} ore).",
        f"* **Con l'uscita a +30%: {pc(b['media'])} a evento** (intervallo {pc(b['basso'])}; {pc(b['alto'])}, p {b['p']:.4f}); mediana {pc(e_con['mediana'])}, "
        f"vinte {100 * e_con['vinti']:.0f}%; metà {pc(e_con['prima_meta'])} e {pc(e_con['seconda_meta'])}; senza i 5 migliori {pc(e_con['senza_5_migliori'])}; "
        f"uscita a +30% nel {100 * out['fermate']:.0f}%.",
        f"* Senza l'uscita: {pc(bs['media'])} (p {bs['p']:.4f}), senza i 5 migliori {pc(e_senza['senza_5_migliori'])}.",
        "* Per anno: " + ", ".join(f"{a} {pc(v['media'])} ({v['eventi']})" for a, v in e_con["per_anno"].items()) + ".",
        f"* Controllo (le stesse monete, stessa durata, 30-365 giorni prima): {pc(out['controllo_media'])}; differenza {pc(out['differenza']['media'])} "
        f"(p {out['differenza']['p']:.3f}).", "",
        f"**Esito: {out['esito']}** (soglia contando le {PROVE_A_EVENTI} prove a eventi: {soglia:.5f})."]) + "\n"
    (QUI / "RISULTATI_QUARANTACINQUESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("QUARANTACINQUESIMA FINITA", flush=True)
