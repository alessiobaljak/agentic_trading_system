"""Programma 7, prova 169 (CENTOSETTIMA_BIS.md, con la «Chiusura della verifica»): G1 o F5 secondo la direzione del Bitcoin (ER 30 giorni).
Varianti: A soglia 0,20, B soglia 0,30. Motori e pesi riusati da centosesta.py, senza toccarli. Nessun seme: tutto deterministico.
Uso: python3 -m research.programma7.centosettima_bis
"""
from __future__ import annotations

import json
import traceback

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import ventiquattresima as vq
from research.programma7 import centosesta as c6
from research.programma7 import prima as pr
from research.src.prove import registra

QUI = c6.QUI
RIS = QUI / "risultati_centosettima_bis"
ID = "centosettima_bis"
SCALA = "settimanale (somma dei giorni); stato giornaliero G1/F5"
SOGLIE = {"A": 0.20, "B": 0.30}
PARAMETRI = {"periodo": "2021-01-04..2026-10-04 (300 settimane)", "misura": "ER Kaufman BTC 30 giorni, chiusure fino a ieri",
             "esito": "esito_regole (0,80 famiglie, ogni anno, t 3)"}


def er_giorno(C: np.ndarray, i: int) -> float:
    """ER del giorno di riga i: usa solo C[i-31 .. i-1]. NaN se non calcolabile (chiusure mancanti o denominatore zero)."""
    if i - 31 < 0:
        return np.nan
    w = C[i - 31:i]
    if not np.isfinite(w).all():
        return np.nan
    den = np.abs(np.diff(w)).sum()
    if not den > 0:
        return np.nan
    return float(abs(w[-1] - w[0]) / den)


def anno_di(giorni):
    return pd.to_datetime(np.asarray(giorni) * 86400, unit="s").year.to_numpy()


def blocco(g: pd.DataFrame, giorni, mask=None) -> dict:
    m = np.ones(len(g), bool) if mask is None else mask
    return {"giorni": int(m.sum()), "netto_somma": float(g["netto"].to_numpy()[m].sum())}


def esegui(log=print) -> dict:
    RIS.mkdir(exist_ok=True)
    try:
        pan = sc.pannello()
        ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
        giorni = np.arange(se.INIZIO, pr.FINE, dtype=np.int64)
        idx = giorni - pan["t0"]
        Ud = pr.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
        sig = ot.sigma_30(pan, idx)
        R = sc.rendimenti(pan)[idx]
        F = np.nan_to_num(pan["funding"][idx])
        costo = sc.costi_moneta(pan["simboli"])
        jb = pan["simboli"].index("BTCUSDT")
        btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
        Cb = pan["close"][:, jb].astype(float)
        # 1. buchi del Bitcoin da INIZIO-31 a FINE-1
        a0 = int(se.INIZIO - 31 - pan["t0"])
        assert a0 >= 0, "il pannello non copre il 4 dicembre 2020"
        tratto = Cb[a0:int(pr.FINE - 1 - pan["t0"]) + 1]
        manc = [sc.data(int(a0 + pan["t0"] + k)) for k in np.flatnonzero(~np.isfinite(tratto))]
        log(f"[169] chiusure BTC mancanti da 2020-12-04: {manc}")
        if len(manc) > 5:
            raise RuntimeError(f"STOP: {len(manc)} chiusure BTC mancanti (piu' di 5)")
        buchi = c6.buchi_nel_periodo(pan, giorni)
        # ER e controllo senza sguardo avanti
        ER = np.array([er_giorno(Cb, int(i)) for i in idx])
        ER_alt = np.array([er_giorno(np.where(np.arange(len(Cb)) >= int(i), np.nan, Cb), int(i)) for i in idx])
        assert np.array_equal(np.nan_to_num(ER, nan=-1), np.nan_to_num(ER_alt, nan=-1)), "ER usa dati dal giorno stesso in poi"
        sguardo_avanti_ok = True
        # pesi interi (G1 e F5), come 168
        W1 = vq.pesi_banda(np.where(np.isfinite(sig), -se.funding_7(pan, idx), np.nan), Ud, sig)
        lun = ps["lunedi"] - pan["t0"]
        sg = ot.sigma_30(pan, lun)
        Wt = vq.pesi_banda(np.where(np.isfinite(sg), -se.funding_7(pan, lun), np.nan), ps["U"], sg)
        W5 = pr.universo_del_giorno(giorni, ps["lunedi"], Wt)
        stor = {"G1": pd.read_csv(QUI / "risultati_prima" / "settimane_G1.csv.gz", index_col=0),
                "F5": pd.read_csv(QUI.parent / "programma6" / "risultati_controllo_parita" / "settimane_F5.csv.gz", index_col=0)}
        stor = {n: d[(d.index >= se.INIZIO) & (d.index < pr.FINE)] for n, d in stor.items()}
        assert len(stor["G1"]) == 300 and stor["G1"].index.equals(stor["F5"].index) and int(stor["G1"].index[0]) == se.INIZIO
        gG1, sG1, ordG1, _ = c6.conto_giorni(W1, R, F, giorni, pan["simboli"], costo)
        d5 = te.conto(Wt, ps["R"], ps["F"], costo)
        d5.index = ps["lunedi"]
        d5 = d5[(d5.index >= se.INIZIO) & (d5.index < pr.FINE)]
        scarto = {"G1": float(np.abs(sG1["netto"].to_numpy() - stor["G1"]["netto"].to_numpy()).max()),
                  "F5": float(np.abs(d5["netto"].to_numpy() - stor["F5"]["netto"].to_numpy()).max())}
        log(f"[169] scarto motori: {scarto}")
        if scarto["G1"] > 0.01 or scarto["F5"] > 0.005:
            raise RuntimeError(f"STOP: scarto dei motori sopra la soglia {scarto}")
        g5, s5, ord5, _ = c6.conto_giorni(W5, R, F, giorni, pan["simboli"], costo)
    except Exception:  # noqa: BLE001
        err = traceback.format_exc()
        for v in SOGLIE:
            registra(ID, v, {**PARAMETRI, "variante": v, "soglia": SOGLIE[v]}, SCALA, 0, {}, "ERRORE",
                     note="errore nei preparativi: " + err[-400:], seme=0)
        raise
    anni = anno_di(giorni)
    out = {"buchi": buchi, "chiusure_BTC_mancanti_da_2020-12-04": manc, "controllo_sguardo_avanti": "ER identico con i dati dal giorno stesso in poi azzerati",
           "scarto_serie_rifatte": scarto, "ordini": {"G1": ordG1, "F5_giornaliera": ord5},
           "ER_giorni_calcolabili": int(np.isfinite(ER).sum()), "giorni": len(giorni)}
    es_ref = {n: te.esame(stor[n], btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI) for n in ("G1", "F5")}
    es_ref["solo_F5_nel_motore"] = te.esame(s5, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    es_ref["G1_rifatta"] = te.esame(sG1, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    out["riferimenti"] = {n: {"sharpe": e["intero"]["sharpe"], "annuo": e["intero"]["annuo"], "discesa_max": e["intero"]["discesa_max"],
                              "spese_annue": e["spese_annue"], "per_anno": e["per_anno"]} for n, e in es_ref.items()}
    out["controllo_solo_F5"] = {"correlazione_con_F5_settimanale": float(np.corrcoef(s5["netto"], stor["F5"]["netto"])[0, 1]),
                                "scarto_medio_netto_settimanale": float((s5["netto"].to_numpy() - stor["F5"]["netto"].to_numpy()).mean()),
                                "scarto_max": float(np.abs(s5["netto"].to_numpy() - stor["F5"]["netto"].to_numpy()).max())}
    sett_peggiori = {"G1": c6.peggiori(stor["G1"]["netto"]), "F5": c6.peggiori(stor["F5"]["netto"])}
    gp = {"G1": c6.peggiori(pd.Series(gG1["netto"].to_numpy(), index=giorni)),
          "F5_giornaliera": c6.peggiori(pd.Series(g5["netto"].to_numpy(), index=giorni))}
    nuove, cand, es, per_var = {}, {}, {}, {}
    for v, soglia in SOGLIE.items():
        nome = f"169 {v}"
        try:
            dir_ = np.isfinite(ER) & (ER >= soglia)
            Wv = np.where(dir_[:, None], W1, W5)
            gV, S, ordV, limV = c6.conto_giorni(Wv, R, F, giorni, pan["simboli"], costo)
            S.to_csv(RIS / f"settimane_{v}.csv.gz")
            gV.assign(giorno=giorni, direzione=dir_).to_csv(RIS / f"giorni_{v}.csv.gz", index=False)
            e = te.esame(S, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
            es[v] = e
            nuove[nome], cand[nome] = S["netto"], e["intero"]
            cambio = np.zeros(len(giorni), bool)
            cambio[1:] = dir_[1:] != dir_[:-1]
            cam_anno = {int(a): int(cambio[anni == a].sum()) for a in sorted(set(anni))}
            sp_cambi = gV["spese"].to_numpy()
            anni_tot = len(giorni) / 365.0
            quota = {int(a): float(dir_[anni == a].mean()) for a in sorted(set(anni))}
            con_dir = {a: q >= 0.5 for a, q in quota.items()}
            netto_g = gV["netto"].to_numpy()
            annuo_G1 = es_ref["G1"]["intero"]["annuo"]
            guad = e["intero"]["annuo"] - annuo_G1
            per_var[v] = {
                "soglia": soglia, "ordini": ordV, "ordini_a_limite": limV, "cambi_di_stato_totali": int(cambio.sum()),
                "cambi_di_stato_per_anno": cam_anno, "spese_dei_cambi_totali": float(sp_cambi[cambio].sum()),
                "spese_dei_cambi_annue": float(sp_cambi[cambio].sum() / anni_tot),
                "spese_normali_annue_totali": float(sp_cambi.sum() / anni_tot),
                "quota_giorni_con_direzione_per_anno": quota, "quota_totale": float(dir_.mean()),
                "anni_con_direzione": [a for a, c in con_dir.items() if c],
                "guadagno_su_G1_annuo": float(guad),
                "fallimento_utile_cambi": (bool(sp_cambi[cambio].sum() / anni_tot > guad / 2) if guad > 0 else "nessun guadagno su G1"),
                "netto_nei_giorni_con_direzione": {"variante": float(netto_g[dir_].sum()), "G1": float(gG1["netto"].to_numpy()[dir_].sum()),
                                                   "F5_giornaliera": float(g5["netto"].to_numpy()[dir_].sum()), "giorni": int(dir_.sum())},
                "netto_nei_giorni_senza_direzione": {"variante": float(netto_g[~dir_].sum()), "G1": float(gG1["netto"].to_numpy()[~dir_].sum()),
                                                     "F5_giornaliera": float(g5["netto"].to_numpy()[~dir_].sum()), "giorni": int((~dir_).sum())},
                "netto_per_anno_e_stato": {int(a): {"con": float(netto_g[(anni == a) & dir_].sum()), "senza": float(netto_g[(anni == a) & ~dir_].sum()),
                                                      "G1_anno": float(gG1["netto"].to_numpy()[anni == a].sum()),
                                                      "F5g_anno": float(g5["netto"].to_numpy()[anni == a].sum())} for a in sorted(set(anni))},
                "giorno_peggiore": c6.peggiori(pd.Series(netto_g, index=giorni)),
                "settimana_peggiore": c6.peggiori(S["netto"]), "stato": dir_}
        except Exception:  # noqa: BLE001
            registra(ID, v, {**PARAMETRI, "variante": v, "soglia": soglia}, SCALA, 0, {}, "ERRORE", note=traceback.format_exc()[-400:], seme=0)
            out[f"{v}_errore"] = traceback.format_exc()
    if nuove:
        fam = ast.corretto_famiglie(nuove, cand)
        out["famiglie"] = {k: val for k, val in fam.items() if k != "candidate"}
        for v in list(es):
            nome = f"169 {v}"
            r = fam["candidate"][nome]
            e = es[v]
            e["sharpe_corretto"], e["t"], e["gruppo"] = r["corretto"], r["t"], r["gruppo"]
            e["esito"] = c6.esito_regole(e, r["corretto"], r["t"])
            i = e["intero"]
            registra(ID, v, {**PARAMETRI, "variante": v, "soglia": SOGLIE[v]}, SCALA, i["settimane"],
                     {"sharpe": round(i["sharpe"], 4), "annuo": round(i["annuo"], 4), "discesa_max": round(i["discesa_max"], 4),
                      "spese_annue": round(e["spese_annue"], 4), "sharpe_corretto": round(r["corretto"], 4), "t": round(r["t"], 3),
                      "ordini": per_var[v]["ordini"], "cambi_di_stato": per_var[v]["cambi_di_stato_totali"],
                      "spese_cambi_annue": round(per_var[v]["spese_dei_cambi_annue"], 5)},
                     e["esito"], note="mazzo con F5 vecchia (backlog P35); famiglie=" + str(fam["famiglie"]) + "; codice non committato", seme=0)
    out["esame"] = es
    out["varianti"] = {v: {k: x for k, x in d.items() if k != "stato"} for v, d in per_var.items()}
    out["giorno_peggiore_riferimenti"] = gp
    out["settimana_peggiore_riferimenti"] = sett_peggiori
    # parte in avanti, fin dove arriva il pannello (nessuno scarico)
    try:
        ultimo = int(pan["t0"] + len(Cb) - 1)
        av = {"ultimo_giorno_pannello": sc.data(ultimo)}
        inizio_av = sc.giorno(2026, 11, 16)
        if ultimo < inizio_av:
            av["nota"] = "il pannello arriva prima del 16 novembre: parte in avanti non fatta"
        else:
            gg = np.arange(inizio_av, ultimo + 1)
            erv = np.array([er_giorno(Cb, int(g - pan["t0"])) for g in gg])
            av["ER_da_16_novembre"] = {sc.data(int(g)): (None if not np.isfinite(x) else round(float(x), 3)) for g, x in zip(gg, erv)}
            for v, s in SOGLIE.items():
                av[f"stato_{v}"] = {sc.data(int(g)): ("G1" if (np.isfinite(x) and x >= s) else "F5") for g, x in zip(gg, erv)}
        c6.RIS = RIS
        av["reale"] = c6.avanti()
        out["avanti"] = av
    except Exception:  # noqa: BLE001
        out["avanti_errore"] = traceback.format_exc()[-600:]
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return out


if __name__ == "__main__":
    o = esegui(log=lambda x: print(x[:300], flush=True))
    for v in SOGLIE:
        e = o["esame"].get(v)
        if e:
            i, d = e["intero"], o["varianti"][v]
            print(f"{v}: Sharpe {i['sharpe']:.2f} annuo {100 * i['annuo']:+.1f}% disc {100 * i['discesa_max']:.1f}% corr {e['sharpe_corretto']:.2f} "
                  f"t {e['t']:.2f} cambi {d['cambi_di_stato_totali']} spese cambi/anno {100 * d['spese_dei_cambi_annue']:.2f}% -> {e['esito']}", flush=True)
    for n, r in o["riferimenti"].items():
        print(f"{n}: Sharpe {r['sharpe']:.2f} annuo {100 * r['annuo']:+.1f}% disc {100 * r['discesa_max']:.1f}%", flush=True)
    print("CENTOSETTIMA_BIS FINITA", flush=True)
