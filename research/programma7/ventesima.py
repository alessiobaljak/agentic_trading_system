"""Programma 7, ventesima prova (VENTESIMA.md): G18, sul Bitcoin contro gli estremi dell'intervallo delle 4 ore, obiettivo 0,3% a
limite, protezione 1,8%, al massimo 24 ore, con le candele a 1 minuto (2021 – 25 giugno 2026; il periodo del trader a parte).

Uso: python3 -m research.programma7.ventesima
"""
from __future__ import annotations

import csv
import io
import json
import time
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from research.programma6 import asticella as ast
from research.programma6 import seconda as sc
from research.programma6 import terza as te
from research.programma6 import trentesima as tr

QUI = Path(__file__).parent
RIS = QUI / "risultati_ventesima"
DATI = QUI.parents[1] / "research" / "data" / "minuti_btc"
URL_MESE = "https://data.binance.vision/data/futures/um/monthly/klines/BTCUSDT/1m/BTCUSDT-1m-{m}.zip"
URL_GIORNO = "https://data.binance.vision/data/futures/um/daily/klines/BTCUSDT/1m/BTCUSDT-1m-{d}.zip"
DA, A = sc.giorno(2021, 1, 1), sc.giorno(2026, 6, 25)
TRADER_DA, TRADER_A = sc.giorno(2026, 6, 26), sc.giorno(2026, 10, 21)
FINESTRA, POS, R4H = 240, 0.80, 0.005
OBIETTIVO, PROTEZIONE, MAX_MIN, PAUSA = 0.003, 0.018, 1440, 15
TAKER, SCARTO, MAKER = 0.0005, 0.0001, 0.0002


def _zip_righe(contenuto: bytes) -> list:
    z = zipfile.ZipFile(io.BytesIO(contenuto))
    righe = list(csv.reader(io.TextIOWrapper(z.open(z.namelist()[0]))))
    return righe[1:] if righe and not righe[0][0].isdigit() else righe


def _scarica(url: str) -> list:
    for k in range(4):
        r = requests.get(url, timeout=60)
        if r.status_code == 404:
            return []
        if r.ok:
            return _zip_righe(r.content)
        time.sleep(2 ** k)
    return []


def candele() -> pd.DataFrame:
    """Le candele a 1 minuto del perpetuo BTCUSDT dal 2021 al 21 ottobre 2026 (in cache)."""
    f = DATI / "BTCUSDT_1m.npz"
    if f.exists():
        z = np.load(f)
        return pd.DataFrame({k: z[k] for k in ("open", "high", "low", "close")}, index=z["minuto"])
    righe = []
    for anno in range(2021, 2027):
        for mese in range(1, 13):
            if (anno, mese) > (2026, 9):
                break
            righe += _scarica(URL_MESE.format(m=f"{anno}-{mese:02d}"))
    for g in range(sc.giorno(2026, 10, 1), TRADER_A + 1):
        righe += _scarica(URL_GIORNO.format(d=sc.data(g)))
    d = pd.DataFrame([[int(x[0]) // 60000, *map(float, x[1:5])] for x in righe],
                     columns=["minuto", "open", "high", "low", "close"]).drop_duplicates("minuto").set_index("minuto").sort_index()
    DATI.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(f, minuto=d.index.to_numpy(), **{k: d[k].to_numpy() for k in ("open", "high", "low", "close")})
    return d


def segnali(w: pd.DataFrame) -> pd.Series:
    """+1 (long) o −1 (short) nei minuti con il segnale, 0 altrove."""
    hi = w["high"].rolling(FINESTRA, min_periods=FINESTRA).max()
    lo = w["low"].rolling(FINESTRA, min_periods=FINESTRA).min()
    pos = (w["close"] - lo) / (hi - lo)
    r4 = w["close"] / w["open"].shift(FINESTRA - 1) - 1
    s = pd.Series(0, index=w.index)
    s[(pos >= POS) & (r4 >= R4H)] = -1
    s[(pos <= 1 - POS) & (r4 <= -R4H)] = 1
    return s


def operazione(o, h, l, i: int, verso: int) -> dict | None:
    """Entrata all'apertura della riga i + 1 (minuti consecutivi), obiettivo, protezione, uscita a tempo."""
    e = i + 1
    if e + 1 >= len(o):
        return None
    p0 = o[e]
    fine = min(len(o) - 1, e + MAX_MIN)
    hh, ll = h[e:fine], l[e:fine]
    if verso > 0:
        ob, pr = p0 * (1 + OBIETTIVO), p0 * (1 - PROTEZIONE)
        i_ob, i_pr = np.flatnonzero(hh >= ob), np.flatnonzero(ll <= pr)
    else:
        ob, pr = p0 * (1 - OBIETTIVO), p0 * (1 + PROTEZIONE)
        i_ob, i_pr = np.flatnonzero(ll <= ob), np.flatnonzero(hh >= pr)
    a = i_ob[0] if len(i_ob) else 10**9
    b = i_pr[0] if len(i_pr) else 10**9
    if b <= a and b < 10**9:
        uscita, px, motivo, c_out = e + int(b), pr, "protezione", TAKER + SCARTO
    elif a < 10**9:
        uscita, px, motivo, c_out = e + int(a), ob, "obiettivo", MAKER
    else:
        uscita, px, motivo, c_out = fine, o[fine], "tempo", TAKER + SCARTO
    return {"e": e, "u": uscita, "minuti": uscita - e, "p0": p0, "px": px, "motivo": motivo,
            "r_prezzo": verso * (px / p0 - 1), "costi": TAKER + SCARTO + c_out}


def simula(w: pd.DataFrame, s: pd.Series, fund: pd.Series) -> pd.DataFrame:
    o, h, l = w["open"].to_numpy(), w["high"].to_numpy(), w["low"].to_numpy()
    minuti = w.index.to_numpy()
    sv = s.to_numpy()
    righe, libero = [], -1
    for i in np.flatnonzero(sv != 0):
        if i < libero:
            continue
        op = operazione(o, h, l, int(i), int(sv[i]))
        if op is None:
            continue
        g = int(minuti[op["e"]]) // 1440
        f = float(fund.get(g, 0.0)) * op["minuti"] / 1440.0 * (-int(sv[i]))
        righe.append({"data": sc.data(g), "annuncio": int((g + 3) // 7), "minuto": int(minuti[op["e"]]), "verso": int(sv[i]),
                      **{k: op[k] for k in ("minuti", "motivo", "r_prezzo", "costi")}, "funding": f,
                      "r": op["r_prezzo"] - op["costi"] + f})
        libero = op["u"] + PAUSA
    return pd.DataFrame(righe)


def settimane(df: pd.DataFrame, da: int, a: int) -> pd.DataFrame:
    lun = df["annuncio"].to_numpy() * 7 - 3
    sett = pd.Series(df["r"].to_numpy(), index=lun).groupby(level=0).sum()
    tutte = np.arange(((da + 3) // 7) * 7 - 3, a + 7, 7)
    out = pd.DataFrame({"netto": sett.reindex(tutte).fillna(0.0)})
    out["netto_doppio"] = out["netto"] - pd.Series(df["costi"].to_numpy(), index=lun).groupby(level=0).sum().reindex(tutte).fillna(0.0)
    for c in ("lordo", "spese", "funding", "giro", "long", "short"):
        out[c] = 0.0
    out["monete"] = 1
    return out


def esegui(log=print) -> dict:
    w = candele()
    log(f"[ventesima] {len(w)} minuti di BTCUSDT")
    pan = sc.pannello()
    jb = pan["simboli"].index("BTCUSDT")
    giorni = np.arange(pan["close"].shape[0]) + pan["t0"]
    fund = pd.Series(np.nan_to_num(pan["funding"][:, jb]), index=giorni)
    s = segnali(w)
    prova = w[(w.index >= DA * 1440) & (w.index < (A + 1) * 1440)]
    df = simula(prova, s.loc[prova.index], fund)
    trader = w[(w.index >= (TRADER_DA - 1) * 1440) & (w.index < (TRADER_A + 1) * 1440)]
    dt_ = simula(trader, s.loc[trader.index], fund)
    dt_ = dt_[dt_["minuto"] >= TRADER_DA * 1440] if len(dt_) else dt_
    # il caso: per ogni operazione, un'entrata a un minuto a caso dello stesso giorno, stesso verso, stesse uscite
    rng = np.random.default_rng(2026)
    o, h, l = prova["open"].to_numpy(), prova["high"].to_numpy(), prova["low"].to_numpy()
    pos = {m: k for k, m in enumerate(prova.index.to_numpy())}
    caso = []
    for _, x in df.iterrows():
        g = x["minuto"] // 1440
        for _ in range(5):
            k = pos.get(int(rng.integers(g * 1440, g * 1440 + 1440)))
            if k is not None:
                op = operazione(o, h, l, k, int(x["verso"]))
                if op:
                    caso.append(op["r_prezzo"] - op["costi"])
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "operazioni_G18.csv.gz", index=False)
    ex_ = tr.esame(df, "r")
    sett = settimane(df, DA, A)
    sett.to_csv(RIS / "settimane_G18.csv.gz")
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    p = te.esame(sett, btc, inizio=int(sett.index.min()), anni_pieni=(2021, 2022, 2023, 2024, 2025))
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), "77 G18": sett["netto"]}, {"77 G18": p["intero"]})
    rr = rivisto["candidate"]["77 G18"]
    p["sharpe_corretto"], p["t"], p["gruppi"] = rr["corretto_con_aggiunta"], rr["t"], rivisto["gruppi"]
    p["esito"] = te.esito(p, p["sharpe_corretto"])
    out = {"operazioni": len(df), "al_giorno": len(df) / (A - DA + 1), "eventi": ex_, "portafoglio": p,
           "motivi": df["motivo"].value_counts(normalize=True).round(4).to_dict(), "minuti_mediana": float(df["minuti"].median()),
           "long": {"n": int((df["verso"] > 0).sum()), "media": float(df.loc[df["verso"] > 0, "r"].mean())},
           "short": {"n": int((df["verso"] < 0).sum()), "media": float(df.loc[df["verso"] < 0, "r"].mean())},
           "caso": {"n": len(caso), "media": float(np.mean(caso)) if caso else None},
           "costi_medi": float(df["costi"].mean()), "r_prezzo_medio": float(df["r_prezzo"].mean()),
           "periodo_del_trader": {"n": len(dt_), "media": float(dt_["r"].mean()) if len(dt_) else None,
                                  "obiettivi": float((dt_["motivo"] == "obiettivo").mean()) if len(dt_) else None}}
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    b, i, q = ex_["boot"], p["intero"], out["periodo_del_trader"]
    testo = "\n".join([
        "# Programma 7 — risultati della ventesima prova (G18: sul Bitcoin contro gli estremi delle 4 ore)", "",
        "Regole in `VENTESIMA.md` (scritte prima). Candele a 1 minuto, 1° gennaio 2021 – 25 giugno 2026.", "",
        f"* **{len(df)} operazioni** ({out['al_giorno']:.1f} al giorno), durata mediana {out['minuti_mediana']:.0f} minuti; uscite: " +
        ", ".join(f"{k} {100 * v:.0f}%" for k, v in out["motivi"].items()) + ".",
        f"* **{100 * b['media']:+.3f}% a operazione** dopo i costi (intervallo {100 * b['basso']:+.3f}%; {100 * b['alto']:+.3f}%, p {b['p']:.4f}); "
        f"vinte {100 * ex_['vinti']:.0f}%; metà {100 * ex_['prima_meta']:+.3f}% e {100 * ex_['seconda_meta']:+.3f}%; prezzo "
        f"{100 * out['r_prezzo_medio']:+.3f}%, costi {100 * out['costi_medi']:.3f}%.",
        f"* Long {out['long']['n']} ({100 * out['long']['media']:+.3f}%), short {out['short']['n']} ({100 * out['short']['media']:+.3f}%). "
        f"**Il caso** (stesso giorno e verso, minuto a caso): {100 * (out['caso']['media'] or 0):+.3f}% su {out['caso']['n']}.",
        "* Per anno: " + ", ".join(f"{a} {100 * v['media']:+.3f}% ({v['eventi']})" for a, v in ex_["per_anno"].items()) + ".",
        f"* Il conto (leva 1, tutto il capitale a operazione): Sharpe {i['sharpe']:.2f}, {100 * i['annuo']:+.1f}% l'anno, discesa "
        f"{100 * i['discesa_max']:.1f}%; per anno " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in p["per_anno"].items()) +
        f"; Sharpe corretto {p['sharpe_corretto']:.2f} ({p['gruppi']} gruppi), t {p['t']:.2f}.",
        f"* Nel periodo del trader (26 giugno – 21 ottobre 2026, solo per confronto): {q['n']} operazioni, "
        f"{100 * (q['media'] or 0):+.3f}% a operazione, obiettivi {100 * (q['obiettivi'] or 0):.0f}%.", "",
        f"**Esito: operazioni {ex_['esito']}; conto {p['esito']}**"]) + "\n"
    (QUI / "RISULTATI_VENTESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("VENTESIMA FINITA", flush=True)
