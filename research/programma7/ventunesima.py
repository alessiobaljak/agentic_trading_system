"""Programma 7, ventunesima prova (VENTUNESIMA.md): G19, long sulle monete piccole crollate in giornata (−20% in 24 ore, −2% nei
15 minuti, volume 2 volte), obiettivo +3% a limite, protezione −15%, al massimo 24 ore.

Uso: python3 -m research.programma7.ventunesima
"""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import quarantunesima as qu
from research.programma6 import seconda as sc
from research.programma6 import terza as te
from research.programma6 import trentesima as tr
from research.programma7 import diciottesima as g16
from research.trader_copiati.analisi_trader2 import minuti

QUI = Path(__file__).parent
RIS = QUI / "risultati_ventunesima"
DA, A = sc.giorno(2025, 1, 1), sc.giorno(2026, 6, 26)
TRADER_DA, TRADER_A = sc.giorno(2026, 6, 27), sc.giorno(2026, 10, 21)
CALO_24H, CALO_15M, VOLUME_X = 0.80, 0.98, 2.0
OBIETTIVO, PROTEZIONE, SCARTO, MAX_MIN, SENZA_MAX_MIN = 0.03, 0.15, 0.01, 1440, 7 * 1440
PROVE_A_EVENTI = 20


def candidati(pan: dict, da: int, a: int) -> list:
    """[(colonna, indice del giorno)]: minimo del giorno almeno il 20% sotto l'apertura del giorno prima, tolte le 30 piu' grandi
    per volume medio nel periodo."""
    t0 = pan["t0"]
    i0, i1 = da - t0, min(a - t0 + 1, pan["close"].shape[0])
    v = pan["quote_volume"][i0:i1]
    vm = np.nanmean(np.where(np.isfinite(v), v, np.nan), axis=0)
    grandi = set(np.argsort(-np.nan_to_num(vm))[:g16.GRANDI].tolist())
    out = []
    for k in range(i0, i1):
        r = pan["low"][k] / pan["open"][k - 1]
        for j in np.flatnonzero(np.nan_to_num(r, nan=9.0) <= CALO_24H):
            if j not in grandi and np.nan_to_num(pan["quote_volume"][k, j]) > 0:
                out.append((int(j), int(k)))
    return out


def segnali(w: pd.DataFrame, minuti_ammessi: np.ndarray) -> list:
    idx = w.index.to_numpy()
    pos = {m: i for i, m in enumerate(idx)}
    o, c, v = w["open"].to_numpy(), w["close"].to_numpy(), w["dollari"].to_numpy()
    out = []
    for t in minuti_ammessi:
        i = pos.get(int(t))
        j24, j15 = pos.get(int(t) - 1440), pos.get(int(t) - 14)
        if i is None or j24 is None or j15 is None:
            continue
        if not (c[i] <= CALO_24H * o[j24] and c[i] <= CALO_15M * o[j15]):
            continue
        prima = v[j24:j15]
        med = np.median(prima) if len(prima) else 0.0
        if med > 0 and v[j15:i + 1].mean() >= VOLUME_X * med:
            out.append(int(t))
    return out


def operazione(w: pd.DataFrame, t: int, costo: float, protezione: bool = True, max_min: int = MAX_MIN) -> dict | None:
    """Long all'apertura del minuto t + 1; obiettivo +3% a limite, protezione −15% (se c'e'), uscita a tempo."""
    e = t + 1
    if e not in w.index:
        return None
    tratto = w.loc[e:e + max_min]
    p0 = float(w.loc[e, "open"])
    if not p0 > 0:
        return None
    ob, pr = p0 * (1 + OBIETTIVO), p0 * (1 - PROTEZIONE)
    hi, lo, mm = tratto["high"].to_numpy(), tratto["low"].to_numpy(), tratto.index.to_numpy()
    giu = np.flatnonzero(lo <= pr) if protezione else np.array([], dtype=int)
    su = np.flatnonzero(hi >= ob)
    i_giu = giu[0] if len(giu) else 10**9
    i_su = su[0] if len(su) else 10**9
    if i_giu <= i_su and i_giu < 10**9:
        uscita, px, motivo, c_out = int(mm[i_giu]), pr * (1 - SCARTO), "protezione", costo
    elif i_su < 10**9:
        uscita, px, motivo, c_out = int(mm[i_su]), ob, "obiettivo", g16.MAKER
    else:
        ultimo = int(mm[-1])
        completo = ultimo >= e + max_min
        uscita = e + max_min if completo and (e + max_min) in w.index else ultimo
        px = float(w.loc[uscita, "open"]) if completo and uscita in w.index else float(w.loc[ultimo, "close"])
        motivo, c_out = ("tempo" if completo else "dati finiti"), costo
    return {"entrata_min": e, "uscita_min": uscita, "minuti": uscita - e, "p0": p0, "px": px, "motivo": motivo,
            "r_prezzo": px / p0 - 1, "costi": costo + c_out}


def giro(pan: dict, da: int, a: int, log=print, caso_si: bool = True) -> tuple:
    t0, simboli = pan["t0"], pan["simboli"]
    cand = candidati(pan, da, a)
    log(f"[ventunesima] {sc.data(da)} – {sc.data(a)}: {len(cand)} giorni-moneta candidati su {len({j for j, _ in cand})} monete")
    file = sorted({(simboli[j], k + t0 + d) for j, k in cand for d in (-1, 0, 1)})
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(lambda x: minuti(x[0], sc.data(x[1])), file))
    costo = dict(zip(simboli, sc.costi_moneta(simboli)))
    per_moneta: dict = {}
    for j, k in cand:
        per_moneta.setdefault(j, set()).add(k)
    rng = np.random.default_rng(2026)
    righe, caso, senza = [], [], []
    for j, giorni_k in sorted(per_moneta.items()):
        s = simboli[j]
        w = g16.blocco(s, sorted({k + t0 + d for k in giorni_k for d in (-1, 0, 1)}))
        if w.empty:
            continue
        ammessi = np.concatenate([np.arange((k + t0) * 1440, (k + t0 + 1) * 1440) for k in sorted(giorni_k)])
        segn = segnali(w, ammessi)
        libero_da = -1
        for t in segn:
            if t < libero_da:
                continue
            op = operazione(w, t, costo[s])
            if op is None:
                continue
            k = t // 1440 - t0
            f = -float(np.nan_to_num(pan["funding"][k, j])) * op["minuti"] / 1440.0
            righe.append({"data": sc.data(t // 1440), "annuncio": int((t // 1440 + 3) // 7), "simbolo": s, "segnale_min": t,
                          **op, "funding": f, "r": op["r_prezzo"] - op["costi"] + f})
            libero_da = op["uscita_min"] + g16.PAUSA
            if caso_si:
                w7 = g16.blocco(s, list(range(t // 1440 - 1, (op["entrata_min"] + SENZA_MAX_MIN) // 1440 + 1)))
                o7 = operazione(w7, t, costo[s], protezione=False, max_min=SENZA_MAX_MIN) if not w7.empty else None
                if o7:
                    senza.append({"data": sc.data(t // 1440), "annuncio": int((t // 1440 + 3) // 7), "simbolo": s,
                                  "r": o7["r_prezzo"] - o7["costi"], "motivo": o7["motivo"]})
        if caso_si and segn:
            for gg, n in pd.Series([t // 1440 for t in segn]).value_counts().to_dict().items():
                for t in rng.integers(gg * 1440, gg * 1440 + 1440, size=int(n)):
                    op = operazione(w, int(t), costo[s])
                    if op:
                        caso.append({"r": op["r_prezzo"] - op["costi"], "motivo": op["motivo"]})
    df = pd.DataFrame(righe)
    if len(df):
        df = df.sort_values(["data", "segnale_min"]).reset_index(drop=True)
    return cand, df, pd.DataFrame(senza), pd.DataFrame(caso)


def esegui(log=print) -> dict:
    pan = sc.pannello()
    cand, df, dsenza, dcaso = giro(pan, DA, A, log)
    _, dtr, _, _ = giro(pan, TRADER_DA, TRADER_A, log, caso_si=False)
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "eventi_G19.csv", index=False)
    dsenza.to_csv(RIS / "senza_protezione.csv", index=False)
    ex_ = tr.esame(df, "r")
    out = {"eventi": ex_, "candidati": len(cand), "operazioni": len(df), "monete": int(df["simbolo"].nunique()),
           "motivi": df["motivo"].value_counts(normalize=True).round(4).to_dict(), "minuti_mediana": float(df["minuti"].median()),
           "r_prezzo_medio": float(df["r_prezzo"].mean()), "costi_medi": float(df["costi"].mean()),
           "funding_medio": float(df["funding"].mean()),
           "senza_protezione": tr.esame(dsenza, "r") if len(dsenza) > 10 else None,
           "senza_peggiori": dsenza.nsmallest(5, "r")[["data", "simbolo", "r"]].to_dict("records") if len(dsenza) else [],
           "caso": {"n": len(dcaso), "media": float(dcaso["r"].mean()) if len(dcaso) else None},
           "periodo_del_trader": {"n": len(dtr), "media": float(dtr["r"].mean()) if len(dtr) else None},
           "per_mese": {m: {"operazioni": int(len(g)), "media": float(g["r"].mean())} for m, g in df.groupby(df["data"].str[:7])},
           "soglia_tutte": 0.01 / PROVE_A_EVENTI}
    ev = pd.DataFrame({"simbolo": df["simbolo"], "ora": df["entrata_min"] // 60, "uscita_h": df["uscita_min"] // 60 + 1, "r": df["r"]})
    port = qu.portafoglio(ev)
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    port_p = port[(port.index >= g16.INIZIO_PORTAFOGLIO) & (port.index <= A)]
    p = te.esame(port_p, btc, inizio=g16.INIZIO_PORTAFOGLIO, anni_pieni=(2025,))
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), "78 G19": port["netto"]}, {"78 G19": p["intero"]})
    rr = rivisto["candidate"]["78 G19"]
    p["sharpe_corretto"], p["t"], p["gruppi"] = rr["corretto_con_aggiunta"], rr["t"], rivisto["gruppi"]
    p["esito"] = te.esito(p, p["sharpe_corretto"])
    out["portafoglio"] = p
    passa = ex_["esito"] == "VALIDA"
    out["esito"] = ("VALIDA" if passa and ex_["boot"]["p"] <= out["soglia_tutte"] else
                    "passa l'esame scritto (p ≤ 0,01) ma non la soglia di tutte le prove a eventi" if passa else ex_["esito"])
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    b, i, sp, q = ex_["boot"], p["intero"], out["senza_protezione"], out["periodo_del_trader"]
    testo = "\n".join([
        "# Programma 7 — risultati della ventunesima prova (G19: comprare le monete piccole crollate in giornata)", "",
        "Regole in `VENTUNESIMA.md` (scritte prima). Periodo 1° gennaio 2025 – 26 giugno 2026, candele a 1 minuto di Binance.", "",
        f"* {len(cand)} giorni-moneta candidati; **{len(df)} operazioni** su {out['monete']} monete; durata mediana "
        f"{out['minuti_mediana']:.0f} minuti; uscite: " + ", ".join(f"{k} {100 * v:.0f}%" for k, v in out["motivi"].items()) + ".",
        f"* **{100 * b['media']:+.2f}% a operazione** dopo i costi (intervallo {100 * b['basso']:+.2f}%; {100 * b['alto']:+.2f}%, p {b['p']:.4f}); "
        f"mediana {100 * ex_['mediana']:+.2f}%, vinte {100 * ex_['vinti']:.0f}%; metà {100 * ex_['prima_meta']:+.2f}% e "
        f"{100 * ex_['seconda_meta']:+.2f}%; senza le 5 migliori {100 * ex_['senza_5_migliori']:+.2f}%. Prezzo {100 * out['r_prezzo_medio']:+.2f}%, "
        f"costi {100 * out['costi_medi']:.2f}%, funding {100 * out['funding_medio']:+.3f}%.",
        "* Per anno: " + ", ".join(f"{a} {100 * v['media']:+.2f}% ({v['eventi']})" for a, v in ex_["per_anno"].items()) + ".",
        (f"* Senza protezione (al massimo 7 giorni): {100 * sp['boot']['media']:+.2f}% (p {sp['boot']['p']:.4f}), vinte "
         f"{100 * sp['vinti']:.0f}%; le peggiori " + ", ".join(f"{x['simbolo']} {100 * x['r']:+.0f}%" for x in out["senza_peggiori"]) + ".")
        if sp else "* Senza protezione: troppo poche.",
        f"* **Il caso** (minuti a caso negli stessi giorni-moneta, stesse uscite): {100 * (out['caso']['media'] or 0):+.2f}% su {out['caso']['n']}.",
        f"* Nel periodo del trader (27 giugno – 21 ottobre 2026, solo per confronto): {q['n']} operazioni, {100 * (q['media'] or 0):+.2f}% a operazione.",
        f"* Portafoglio (5% a operazione, al massimo 20 aperte), dal 6 gennaio 2025: Sharpe {i['sharpe']:.2f}, {100 * i['annuo']:+.1f}% l'anno, "
        f"discesa {100 * i['discesa_max']:.1f}%; Sharpe corretto {p['sharpe_corretto']:.2f} ({p['gruppi']} gruppi), t {p['t']:.2f}.", "",
        f"**Esito delle operazioni: {out['esito']}** (soglia contando le {PROVE_A_EVENTI} prove a eventi: {out['soglia_tutte']:.4f}). "
        f"**Portafoglio: {p['esito']}**."]) + "\n"
    (QUI / "RISULTATI_VENTUNESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("VENTUNESIMA FINITA", flush=True)
