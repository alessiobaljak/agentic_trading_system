"""Programma 6: i giorni della settimana (CALENDARIO.md, descrittivo). Il mercato, F5 giorno per giorno e lo scalping della
prova 54 per giorno della settimana UTC.

Uso: python3 -m research.programma6.calendario
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import ventiquattresima as vq

QUI = Path(__file__).parent
RIS = QUI / "risultati_calendario"
GIORNI = ("lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica")
FINE = sc.giorno(2026, 10, 5)


def giorno_settimana(giorno) -> np.ndarray:
    """0 = lunedi' ... 6 = domenica, per i giorni dall'epoca (il 1 gennaio 1970 era giovedi')."""
    return (np.asarray(giorno, dtype=np.int64) + 3) % 7


def f5_giorno_per_giorno(W: np.ndarray, r: np.ndarray, fund: np.ndarray, lun_idx: np.ndarray) -> np.ndarray:
    """(settimane × 7) il guadagno di ogni giorno con i pesi del lunedi' tenuti: il movimento del giorno sul valore d'entrata
    meno il funding del giorno (il long paga se e' positivo, come `terza.conto`). La somma dei 7 giorni di prezzo rifa'
    ``W * R`` della settimana."""
    out = np.zeros((W.shape[0], 7))
    r0 = np.nan_to_num(r)
    f0 = np.nan_to_num(fund)
    for k, t in enumerate(lun_idx):
        x = W[k]
        if not np.any(x):
            continue
        val = np.ones(W.shape[1])
        for d in range(7):
            out[k, d] = float((x * val * r0[t + d]).sum() - (x * f0[t + d]).sum())
            val = val * (1 + r0[t + d])
    return out


def riga(x: np.ndarray) -> dict:
    x = x[np.isfinite(x)]
    sd = float(x.std(ddof=1)) if len(x) > 2 else float("nan")
    return {"n": int(len(x)), "media": float(x.mean()), "deviazione": sd,
            "t": float(x.mean() / sd * math.sqrt(len(x))) if sd and sd > 0 else float("nan")}


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    tieni = (ps["lunedi"] >= se.INIZIO) & (ps["lunedi"] + 7 <= FINE)
    lun_idx = ps["lunedi"] - pan["t0"]
    r = sc.rendimenti(pan)
    out = {"mercato": {}, "F5": {}, "scalping": {}}
    # 1. il mercato: Bitcoin e la media delle 100 della settimana, giorno per giorno
    jb = pan["simboli"].index("BTCUSDT")
    V = pan["quote_volume"]
    mercato = {g: {"btc": [], "cento": [], "volume": []} for g in range(7)}
    for k in np.flatnonzero(tieni):
        t = lun_idx[k]
        u = ps["U"][k]
        vol_sett = np.nanmean(V[t:t + 7][:, u], axis=0)
        for d in range(7):
            mercato[d]["btc"].append(r[t + d, jb])
            mercato[d]["cento"].append(np.nanmean(r[t + d, u]))
            with np.errstate(invalid="ignore", divide="ignore"):
                mercato[d]["volume"].append(np.nanmedian(V[t + d, u] / vol_sett))
    for d in range(7):
        out["mercato"][GIORNI[d]] = {"btc": riga(np.array(mercato[d]["btc"])), "cento": riga(np.array(mercato[d]["cento"])),
                                     "volume_su_media": float(np.nanmean(mercato[d]["volume"]))}
    # 2. F5 con le parita' corrette, giorno per giorno
    sig = ot.sigma_30(pan, lun_idx)
    W = vq.pesi_banda(np.where(np.isfinite(sig), -se.funding_7(pan, lun_idx), np.nan), ps["U"], sig)
    G = f5_giorno_per_giorno(W[tieni], r, pan["funding"], lun_idx[tieni])
    tot = G.sum()
    for d in range(7):
        out["F5"][GIORNI[d]] = riga(G[:, d]) | {"quota": float(G[:, d].sum() / tot)}
    out["F5"]["fine settimana"] = riga(G[:, 5] + G[:, 6]) | {"quota": float((G[:, 5] + G[:, 6]).sum() / tot)}
    out["F5"]["controllo"] = {"settimana_da_giorni": float(G.sum(axis=1).mean()),
                              "settimana_dal_conto": float((te.conto(W, ps["R"], ps["F"], np.zeros(len(ps["simboli"])))
                                                            ["lordo"] - te.conto(W, ps["R"], ps["F"], np.zeros(len(ps["simboli"])))
                                                            ["funding"]).to_numpy()[tieni].mean())}
    # 3. lo scalping della prova 54 per giorno d'entrata
    z = QUI / "risultati_cinquantaquattresima"
    for f in sorted(z.glob("operazioni_*.csv.gz")):
        nome = f.name[len("operazioni_"):-len(".csv.gz")]
        o = pd.read_csv(f, usecols=["entrata", "R"])
        g = giorno_settimana(o["entrata"].to_numpy() // 1440)
        giorno = o["entrata"].to_numpy() // 1440
        x = {}
        for d in range(7):
            m = g == d
            x[GIORNI[d]] = {"n": int(m.sum()), "media_R": float(o["R"][m].mean()) if m.any() else float("nan"),
                            "vinte": float((o["R"][m] > 0).mean()) if m.any() else float("nan")}
        for nome_g, m in (("feriali", g < 5), ("fine settimana", g >= 5)):
            # p del bootstrap sui giorni (come la prova 54): media delle medie giornaliere ricampionate
            per_giorno = o[m].groupby(giorno[m])["R"].sum()
            n_op = int(m.sum())
            rng = np.random.default_rng(54)
            gi = per_giorno.to_numpy()
            conte = o[m].groupby(giorno[m])["R"].size().to_numpy()
            medie = np.empty(5000)
            for b in range(5000):
                i = rng.integers(0, len(gi), len(gi))
                medie[b] = gi[i].sum() / conte[i].sum()
            x[nome_g] = {"n": n_op, "media_R": float(o["R"][m].mean()), "vinte": float((o["R"][m] > 0).mean()),
                         "p": float((medie <= 0).mean())}
        out["scalping"][nome] = x
    RIS.mkdir(exist_ok=True)
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    fs = out["F5"]["fine settimana"]
    scatta_f5 = fs["media"] < 0 and fs["t"] <= -2
    scatta_z = [n for n, x in out["scalping"].items() if x["feriali"]["media_R"] > 0 and x["feriali"]["p"] <= 0.002]
    righe = ["# Programma 6 — i giorni della settimana: i risultati (descrittivo)", "",
             "Regole in `CALENDARIO.md` (scritte prima). Dal 4 gennaio 2021 al 4 ottobre 2026, giorni UTC.", "",
             "## Il mercato", "",
             "| Giorno | Bitcoin: media | Bitcoin: deviazione | 100 monete: media | 100 monete: deviazione | Volume sulla media della settimana |",
             "|---|---|---|---|---|---|"]
    for g in GIORNI:
        m = out["mercato"][g]
        righe.append(f"| {g} | {100 * m['btc']['media']:+.3f}% | {100 * m['btc']['deviazione']:.2f}% | "
                     f"{100 * m['cento']['media']:+.3f}% | {100 * m['cento']['deviazione']:.2f}% | {m['volume_su_media']:.2f} |")
    righe += ["", "## F5 giorno per giorno (parità corrette, senza i costi del lunedì; «fine settimana» = sabato più domenica)", "",
              "| Giorno | Media | Deviazione | t | Quota del guadagno |", "|---|---|---|---|---|"]
    for g in GIORNI + ("fine settimana",):
        m = out["F5"][g]
        righe.append(f"| {g} | {100 * m['media']:+.3f}% | {100 * m['deviazione']:.2f}% | {m['t']:+.2f} | {100 * m['quota']:.0f}% |")
    c = out["F5"]["controllo"]
    righe += ["", f"Controllo: la settimana dai giorni {100 * c['settimana_da_giorni']:+.3f}%, dal conto {100 * c['settimana_dal_conto']:+.3f}%.",
              "", "## Lo scalping della prova 54 per giorno d'entrata (R netto a operazione)", "",
              "| Schema | " + " | ".join(GIORNI) + " | feriali | fine settimana |", "|---|" + "---|" * 9]
    for n, x in out["scalping"].items():
        righe.append(f"| {n} | " + " | ".join(f"{x[g]['media_R']:+.3f} ({x[g]['n']})" for g in GIORNI)
                     + f" | {x['feriali']['media_R']:+.3f} (p {x['feriali']['p']:.3f}) | {x['fine settimana']['media_R']:+.3f} |")
    righe += ["", f"**F5 ferma nel fine settimana: {'si scrive la prova' if scatta_f5 else 'non si prova'}** (regola: media negativa con t ≤ −2; "
              f"qui {100 * fs['media']:+.3f}% a fine settimana, sabato e domenica insieme, t {fs['t']:+.2f}).",
              f"**Scalping solo nei giorni feriali: {'ipotesi per ' + ', '.join(scatta_z) if scatta_z else 'nessuno schema'}** "
              "(regola: media netta sopra zero con p ≤ 0,002)."]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_CALENDARIO.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
