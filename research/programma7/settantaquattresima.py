"""Programma 7, settantaquattresima prova (SETTANTAQUATTRESIMA.md): NT, il Bitcoin e l'Ether che passano un numero tondo. Al primo
passaggio delle 24 ore di un multiplo di 1.000 dollari (Bitcoin) o di 100 (Ether), nel verso del passaggio per 60 minuti; controllo con i
livelli spostati a meta'.

Uso: python3 -m research.programma7.settantaquattresima
"""
from __future__ import annotations

import csv
import io
import json
import time
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import seconda as sc
from research.programma6 import trentesima as tr
from research.programma6 import ventunesima as vu
from research.programma7 import ventesima as v20

QUI = Path(__file__).parent
RIS = QUI / "risultati_settantaquattresima"
DATI_ETH = QUI.parent / "data" / "minuti_eth"
URL = "https://data.binance.vision/data/futures/um/monthly/klines/ETHUSDT/1m/ETHUSDT-1m-{m}.zip"
DAL, AL = sc.giorno(2021, 1, 1) * 1440, sc.giorno(2026, 10, 1) * 1440
LIVELLI = {"BTCUSDT": 1000.0, "ETHUSDT": 100.0}
GIORNO, PAUSA, TENUTA, SEME = 1440, 60, 60, 2026
PROVE_A_EVENTI = 42


def _mese(m: str) -> list:
    for k in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(URL.format(m=m), headers={"User-Agent": "ricerca/1.0"}), timeout=120) as r:
                z = zipfile.ZipFile(io.BytesIO(r.read()))
            return [(int(x[0]) // 60000, float(x[1]), float(x[4])) for x in csv.reader(io.TextIOWrapper(z.open(z.namelist()[0])))
                    if x and x[0].isdigit()]
        except Exception:  # noqa: BLE001
            time.sleep(2 ** (k + 1))
    return []


def ether() -> pd.DataFrame:
    f = DATI_ETH / "ETHUSDT_1m.npz"
    if not f.exists():
        mesi = [f"{a}-{m:02d}" for a in range(2021, 2027) for m in range(1, 13) if (a, m) <= (2026, 9)]
        with ThreadPoolExecutor(max_workers=6) as ex:
            parti = list(ex.map(_mese, mesi))
        righe = [x for p in parti for x in p]
        d = pd.DataFrame(righe, columns=["minuto", "open", "close"]).drop_duplicates("minuto").set_index("minuto").sort_index()
        DATI_ETH.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(f, minuto=d.index.to_numpy(), open=d["open"].to_numpy(), close=d["close"].to_numpy())
    z = np.load(f)
    return pd.DataFrame({"open": z["open"], "close": z["close"]}, index=z["minuto"])


def eventi(d: pd.DataFrame, passo: float, spostamento: float) -> pd.DataFrame:
    d = d[(d.index >= DAL - GIORNO) & (d.index < AL + 300)]
    d = d.reindex(np.arange(d.index.min(), d.index.max() + 1))
    c, o = d["close"].to_numpy(), d["open"].to_numpy()
    mins = d.index.to_numpy()
    k = np.floor((c - spostamento) / passo)
    prima = np.r_[np.nan, k[:-1]]
    massimo = pd.Series(c).shift(1).rolling(GIORNO, min_periods=GIORNO - 60).max().to_numpy()
    minimo = pd.Series(c).shift(1).rolling(GIORNO, min_periods=GIORNO - 60).min().to_numpy()
    righe, ultimo = [], -10 ** 9
    for t in np.flatnonzero(np.isfinite(k) & np.isfinite(prima) & (k != prima)):
        if not (DAL <= mins[t] < AL) or t - ultimo < PAUSA or t + 1 + 240 >= len(c):
            continue
        if k[t] > prima[t]:
            verso, livello = 1, spostamento + passo * k[t]
            primo = massimo[t] < livello
        else:
            verso, livello = -1, spostamento + passo * prima[t]
            primo = minimo[t] > livello
        if not primo:
            continue
        e = o[t + 1]
        if not np.isfinite(e):
            continue
        uscite = {h: o[t + 1 + h] for h in (5, 15, 60, 240)}
        if not np.isfinite(uscite[TENUTA]):
            continue
        ultimo = t
        g = int(mins[t] // GIORNO)
        righe.append({"data": sc.data(g), "annuncio": int((g + 3) // 7), "minuto": int(mins[t]), "verso": verso, "livello": livello,
                      "lordo": verso * (uscite[TENUTA] / e - 1), **{f"lordo_{h}": verso * (x / e - 1) for h, x in uscite.items()}})
    df = pd.DataFrame(righe)
    if len(df):
        df["r"] = df["lordo"] - vu.COSTO_BTC
    return df


def esegui(log=print) -> dict:
    dati = {"BTCUSDT": v20.candele()[["open", "close"]], "ETHUSDT": ether()}
    tutti = {}
    for nome, sp in (("tondi", 0.0), ("controllo", 0.5)):
        parti = []
        for s, d in dati.items():
            x = eventi(d, LIVELLI[s], sp * LIVELLI[s])
            x["moneta"] = s
            parti.append(x)
        tutti[nome] = pd.concat(parti).sort_values("minuto").reset_index(drop=True)
    RIS.mkdir(exist_ok=True)
    for nome, x in tutti.items():
        x.to_csv(RIS / f"eventi_{nome}.csv.gz", index=False)
    ev, co = tutti["tondi"], tutti["controllo"]
    e = tr.esame(ev, "r")
    b = np.random.default_rng(SEME).choice(ev["r"].to_numpy(), size=(10000, len(ev)), replace=True).mean(axis=1) - co["r"].mean()
    diff = {"media": float(ev["r"].mean() - co["r"].mean()), "basso": float(np.quantile(b, 0.025)), "alto": float(np.quantile(b, 0.975)),
            "p": float((b <= 0).mean())}
    soglia = 0.01 / PROVE_A_EVENTI
    valida = e["esito"] == "VALIDA" and diff["p"] <= 0.05
    esito = ("VALIDA" if valida and e["boot"]["p"] <= soglia else
             "passa l'esame scritto ma non la soglia di tutte le prove a eventi" if valida else
             e["esito"] if e["esito"] != "VALIDA" else "non sopra il controllo dei livelli spostati")
    out = {"eventi": int(len(ev)), "esame": e, "controllo": {"eventi": int(len(co)), "media": float(co["r"].mean()),
           "lordo": float(co["lordo"].mean())}, "differenza": diff, "lordo": float(ev["lordo"].mean()),
           "tenute_lorde": {h: float(ev[f"lordo_{h}"].mean()) for h in (5, 15, 60, 240)},
           "per_moneta": {m: float(x["r"].mean()) for m, x in ev.groupby("moneta")},
           "su": float(ev.loc[ev["verso"] == 1, "r"].mean()), "giu": float(ev.loc[ev["verso"] == -1, "r"].mean()), "esito": esito}
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda v: "—" if v is None or v != v else f"{100 * v:+.3f}%"  # noqa: E731
    bb = e["boot"]
    testo = "\n".join([
        "# Programma 7 — risultati della settantaquattresima prova (NT: il Bitcoin e l'Ether che passano un numero tondo)", "",
        "Regole in `SETTANTAQUATTRESIMA.md` (scritte prima). Al primo passaggio delle 24 ore di un multiplo di 1.000 dollari (Bitcoin) o di "
        "100 (Ether), nel verso del passaggio per 60 minuti, costi a mercato; dal 2021 al settembre 2026.", "",
        f"* **{bb['eventi']} passaggi: {pc(bb['media'])} a operazione** (intervallo {pc(bb['basso'])}; {pc(bb['alto'])}, p {bb['p']:.4f}); "
        f"prima dei costi {pc(out['lordo'])}; mediana {pc(e['mediana'])}, vinte {100 * e['vinti']:.0f}%; metà {pc(e['prima_meta'])} e "
        f"{pc(e['seconda_meta'])}; senza le 5 migliori {pc(e['senza_5_migliori'])}.",
        "* Per anno: " + ", ".join(f"{a} {pc(v['media'])} ({v['eventi']})" for a, v in e["per_anno"].items()) + ".",
        "* Per moneta: " + ", ".join(f"{m[:-4]} {pc(v)}" for m, v in out["per_moneta"].items()) + f"; verso l'alto {pc(out['su'])}, verso il "
        f"basso {pc(out['giu'])}.",
        f"* **Controllo, i livelli spostati a metà** ({out['controllo']['eventi']} passaggi): {pc(out['controllo']['media'])} a operazione "
        f"(prima dei costi {pc(out['controllo']['lordo'])}); differenza {pc(diff['media'])} (intervallo {pc(diff['basso'])}; "
        f"{pc(diff['alto'])}, p {diff['p']:.3f}).",
        "* Per capire, prima dei costi: " + ", ".join(f"{h} minuti {pc(v)}" for h, v in out["tenute_lorde"].items()) + ".", "",
        f"**Esito: {esito}** (soglia contando le {PROVE_A_EVENTI} prove a eventi: {soglia:.5f})."]) + "\n"
    (QUI / "RISULTATI_SETTANTAQUATTRESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("SETTANTAQUATTRESIMA FINITA", flush=True)
