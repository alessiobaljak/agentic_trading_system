"""Programma 7, diciottesima prova (DICIOTTESIMA.md): G16, short delle fiammate delle monete piccole in giornata, con le candele a
1 minuto: segnale (+50% in 24 ore, +4% nei 15 minuti, volume 5 volte), obiettivo −5% a limite, protezione +30%, al massimo 24 ore.

Uso: python3 -m research.programma7.diciottesima
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
from research.trader_copiati.analisi_trader2 import minuti

QUI = Path(__file__).parent
RIS = QUI / "risultati_diciottesima"
DA, A = sc.giorno(2025, 1, 1), sc.giorno(2026, 6, 26)
GRANDI = 30
SALITA_24H, SALITA_15M, VOLUME_X = 1.5, 1.04, 5.0
OBIETTIVO, PROTEZIONE, SCARTO, MAX_MIN, SENZA_MAX_MIN = 0.05, 0.30, 0.01, 1440, 7 * 1440
PAUSA, MAKER = 15, 0.0002
PROVE_A_EVENTI = 18
INIZIO_PORTAFOGLIO = sc.giorno(2025, 1, 6)


def candidati(pan: dict) -> list:
    """[(colonna, indice del giorno)]: massimo del giorno almeno 1,5 volte l'apertura del giorno prima, tolte le 30 piu' grandi."""
    t0 = pan["t0"]
    a, b = DA - t0, A - t0 + 1
    vm = np.nanmean(np.where(np.isfinite(pan["quote_volume"][a:b]), pan["quote_volume"][a:b], np.nan), axis=0)
    grandi = set(np.argsort(-np.nan_to_num(vm))[:GRANDI].tolist())
    out = []
    for k in range(a, b):
        r = pan["high"][k] / pan["open"][k - 1]
        for j in np.flatnonzero(np.nan_to_num(r) >= SALITA_24H):
            if j not in grandi and np.nan_to_num(pan["quote_volume"][k, j]) > 0:
                out.append((int(j), int(k)))
    return out


def blocco(simbolo: str, giorni: list) -> pd.DataFrame:
    """Le candele a 1 minuto dei giorni (numeri di giorno UTC), indicizzate dal minuto."""
    parti = [minuti(simbolo, sc.data(g)) for g in sorted(set(giorni))]
    parti = [p for p in parti if not p.empty]
    return pd.concat(parti).sort_index() if parti else pd.DataFrame()


def segnali(w: pd.DataFrame, minuti_ammessi: np.ndarray) -> list:
    """I minuti t (fra quelli ammessi) con il segnale della regola (sezione 3)."""
    idx = w.index.to_numpy()
    pos = {m: i for i, m in enumerate(idx)}
    o, c, v = w["open"].to_numpy(), w["close"].to_numpy(), w["dollari"].to_numpy()
    out = []
    for t in minuti_ammessi:
        i = pos.get(int(t))
        j24, j15 = pos.get(int(t) - 1440), pos.get(int(t) - 14)
        if i is None or j24 is None or j15 is None:
            continue
        if not (c[i] >= SALITA_24H * o[j24] and c[i] >= SALITA_15M * o[j15]):
            continue
        prima = v[j24:j15]
        med = np.median(prima) if len(prima) else 0.0
        if med > 0 and v[j15:i + 1].mean() >= VOLUME_X * med:
            out.append(int(t))
    return out


def operazione(w: pd.DataFrame, t: int, costo: float, protezione: bool = True, max_min: int = MAX_MIN) -> dict | None:
    """Short all'apertura del minuto t + 1; obiettivo −5% a limite, protezione +30% (se c'e'), uscita a tempo."""
    e = t + 1
    if e not in w.index:
        return None
    tratto = w.loc[e:e + max_min]
    p0 = float(w.loc[e, "open"])
    if not p0 > 0:
        return None
    ob, pr = p0 * (1 - OBIETTIVO), p0 * (1 + PROTEZIONE)
    hi, lo, mm = tratto["high"].to_numpy(), tratto["low"].to_numpy(), tratto.index.to_numpy()
    su = np.flatnonzero(hi >= pr) if protezione else np.array([], dtype=int)
    giu = np.flatnonzero(lo <= ob)
    i_su = su[0] if len(su) else 10**9
    i_giu = giu[0] if len(giu) else 10**9
    if i_su <= i_giu and i_su < 10**9:
        uscita, px, motivo, c_out = int(mm[i_su]), pr * (1 + SCARTO), "protezione", costo
    elif i_giu < 10**9:
        uscita, px, motivo, c_out = int(mm[i_giu]), ob, "obiettivo", MAKER
    else:
        ultimo = int(mm[-1])
        completo = ultimo >= e + max_min
        uscita = e + max_min if completo and (e + max_min) in w.index else ultimo
        px = float(w.loc[uscita, "open"]) if completo and uscita in w.index else float(w.loc[ultimo, "close"])
        motivo, c_out = ("tempo" if completo else "dati finiti"), costo
    return {"entrata_min": e, "uscita_min": uscita, "minuti": uscita - e, "p0": p0, "px": px, "motivo": motivo,
            "r_prezzo": (p0 - px) / p0, "costi": costo + c_out}


def esegui(log=print) -> dict:
    pan = sc.pannello()
    t0, simboli = pan["t0"], pan["simboli"]
    cand = candidati(pan)
    log(f"[diciottesima] {len(cand)} giorni-moneta candidati su {len({j for j, _ in cand})} monete; scarico le candele a 1 minuto")
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
        g = sorted({k + t0 + d for k in giorni_k for d in (-1, 0, 1)})
        w = blocco(s, g)
        if w.empty:
            continue
        ammessi = np.concatenate([np.arange((k + t0) * 1440, (k + t0 + 1) * 1440) for k in sorted(giorni_k)])
        libero_da = -1
        segn = segnali(w, ammessi)
        for t in segn:
            if t < libero_da:
                continue
            op = operazione(w, t, costo[s])
            if op is None:
                continue
            k = t // 1440 - t0
            f = float(np.nan_to_num(pan["funding"][k, j])) * op["minuti"] / 1440.0
            righe.append({"data": sc.data(t // 1440), "annuncio": int((t // 1440 + 3) // 7), "simbolo": s, "segnale_min": t,
                          **op, "funding": f, "r": op["r_prezzo"] - op["costi"] + f})
            libero_da = op["uscita_min"] + PAUSA
            # lo stile del trader: senza protezione, solo l'obiettivo, al massimo 7 giorni (scarica i giorni che servono)
            fine = (op["entrata_min"] + SENZA_MAX_MIN) // 1440
            w7 = blocco(s, list(range(t // 1440 - 1, fine + 1)))
            o7 = operazione(w7, t, costo[s], protezione=False, max_min=SENZA_MAX_MIN) if not w7.empty else None
            if o7:
                senza.append({"data": sc.data(t // 1440), "annuncio": int((t // 1440 + 3) // 7), "simbolo": s,
                              "r": o7["r_prezzo"] - o7["costi"], "minuti": o7["minuti"], "motivo": o7["motivo"]})
        # il caso: lo stesso numero di entrate a minuti presi a caso negli stessi giorni-moneta, stesse uscite
        n_giorno = pd.Series([t // 1440 for t in segn]).value_counts().to_dict() if segn else {}
        for gg, n in n_giorno.items():
            for t in rng.integers(gg * 1440, gg * 1440 + 1440, size=int(n)):
                op = operazione(w, int(t), costo[s])
                if op:
                    caso.append({"data": sc.data(int(t) // 1440), "annuncio": int((int(t) // 1440 + 3) // 7), "simbolo": s,
                                 "r": op["r_prezzo"] - op["costi"], "motivo": op["motivo"]})
    df = pd.DataFrame(righe).sort_values(["data", "segnale_min"]).reset_index(drop=True)
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "eventi_G16.csv", index=False)
    dsenza, dcaso = pd.DataFrame(senza), pd.DataFrame(caso)
    dsenza.to_csv(RIS / "senza_protezione.csv", index=False)
    dcaso.to_csv(RIS / "caso.csv", index=False)
    ex_ = tr.esame(df, "r")
    out = {"eventi": ex_, "candidati": len(cand), "operazioni": len(df), "monete": int(df["simbolo"].nunique()),
           "motivi": df["motivo"].value_counts(normalize=True).round(4).to_dict(), "minuti_mediana": float(df["minuti"].median()),
           "al_giorno": len(df) / max(1, (A - DA)), "funding_medio": float(df["funding"].mean()),
           "costi_medi": float(df["costi"].mean()), "r_prezzo_medio": float(df["r_prezzo"].mean()),
           "senza_protezione": tr.esame(dsenza, "r") if len(dsenza) > 10 else None,
           "senza_protezione_motivi": dsenza["motivo"].value_counts(normalize=True).round(4).to_dict() if len(dsenza) else {},
           "caso": {"operazioni": len(dcaso), "media": float(dcaso["r"].mean()) if len(dcaso) else None,
                    "motivi": dcaso["motivo"].value_counts(normalize=True).round(4).to_dict() if len(dcaso) else {}},
           "per_mese": {m: {"operazioni": int(len(g)), "media": float(g["r"].mean())} for m, g in df.groupby(df["data"].str[:7])},
           "soglia_tutte": 0.01 / PROVE_A_EVENTI}
    ev = pd.DataFrame({"simbolo": df["simbolo"], "ora": df["entrata_min"] // 60, "uscita_h": df["uscita_min"] // 60 + 1, "r": df["r"]})
    port = qu.portafoglio(ev)
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    port_p = port[(port.index >= INIZIO_PORTAFOGLIO) & (port.index <= A)]
    p = te.esame(port_p, btc, inizio=INIZIO_PORTAFOGLIO, anni_pieni=(2025,))
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), "75 G16": port["netto"]}, {"75 G16": p["intero"]})
    rr = rivisto["candidate"]["75 G16"]
    p["sharpe_corretto"], p["t"], p["gruppi"] = rr["corretto_con_aggiunta"], rr["t"], rivisto["gruppi"]
    p["esito"] = te.esito(p, p["sharpe_corretto"])
    out["portafoglio"] = p
    passa = ex_["esito"] == "VALIDA"
    out["esito"] = ("VALIDA" if passa and ex_["boot"]["p"] <= out["soglia_tutte"] else
                    "passa l'esame scritto (p ≤ 0,01) ma non la soglia di tutte le prove a eventi" if passa else ex_["esito"])
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    b, i, sp = ex_["boot"], p["intero"], out["senza_protezione"]
    testo = "\n".join([
        "# Programma 7 — risultati della diciottesima prova (G16: vendere le fiammate delle monete piccole in giornata)", "",
        "Regole in `DICIOTTESIMA.md` (scritte prima). Periodo 1° gennaio 2025 – 26 giugno 2026, candele a 1 minuto di Binance.", "",
        f"* {len(cand)} giorni-moneta candidati; **{len(df)} operazioni** su {out['monete']} monete ({out['al_giorno']:.1f} al giorno); "
        f"durata mediana {out['minuti_mediana']:.0f} minuti; uscite: " + ", ".join(f"{k} {100 * v:.0f}%" for k, v in out["motivi"].items()) + ".",
        f"* **{100 * b['media']:+.2f}% a operazione** dopo i costi (intervallo {100 * b['basso']:+.2f}%; {100 * b['alto']:+.2f}%, p {b['p']:.4f}); "
        f"mediana {100 * ex_['mediana']:+.2f}%, vinte {100 * ex_['vinti']:.0f}%; metà {100 * ex_['prima_meta']:+.2f}% e "
        f"{100 * ex_['seconda_meta']:+.2f}%; senza le 5 migliori {100 * ex_['senza_5_migliori']:+.2f}%. Prezzo {100 * out['r_prezzo_medio']:+.2f}%, "
        f"costi {100 * out['costi_medi']:.2f}%, funding {100 * out['funding_medio']:+.3f}%.",
        "* Per anno: " + ", ".join(f"{a} {100 * v['media']:+.2f}% ({v['eventi']})" for a, v in ex_["per_anno"].items()) + ".",
        "* Per mese: " + ", ".join(f"{m} {100 * v['media']:+.2f}% ({v['operazioni']})" for m, v in out["per_mese"].items()) + ".",
        (f"* **Senza protezione** (lo stile del trader, al massimo 7 giorni): {100 * sp['boot']['media']:+.2f}% a operazione (p "
         f"{sp['boot']['p']:.4f}), vinte {100 * sp['vinti']:.0f}%, mediana {100 * sp['mediana']:+.2f}%; uscite " +
         ", ".join(f"{k} {100 * v:.0f}%" for k, v in out["senza_protezione_motivi"].items()) + ".") if sp else "* Senza protezione: troppo poche.",
        f"* **Il caso** (stesse regole, entrate a minuti presi a caso negli stessi giorni-moneta): {out['caso']['operazioni']} operazioni, "
        f"{100 * (out['caso']['media'] or 0):+.2f}% a operazione; uscite " + ", ".join(f"{k} {100 * v:.0f}%" for k, v in out["caso"]["motivi"].items()) + ".",
        f"* Portafoglio (5% a operazione, al massimo 20 aperte), dal 6 gennaio 2025: Sharpe {i['sharpe']:.2f}, {100 * i['annuo']:+.1f}% l'anno, "
        f"volatilità {100 * i['volatilita']:.1f}%, discesa {100 * i['discesa_max']:.1f}%; Sharpe corretto {p['sharpe_corretto']:.2f} "
        f"({p['gruppi']} gruppi), t {p['t']:.2f}.", "",
        f"**Esito delle operazioni: {out['esito']}** (soglia contando le {PROVE_A_EVENTI} prove a eventi: {out['soglia_tutte']:.5f}). "
        f"**Portafoglio: {p['esito']}**."]) + "\n"
    (QUI / "RISULTATI_DICIOTTESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("DICIOTTESIMA FINITA", flush=True)
