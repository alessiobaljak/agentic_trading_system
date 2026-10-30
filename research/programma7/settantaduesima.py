"""Programma 7, settantaduesima prova (SETTANTADUESIMA.md): PM, la pompa del pronti con i long intrappolati. Giorni di picco con la bandiera
della manipolazione nelle 6 ore prima del picco; short contro il Bitcoin il giorno dopo per 24 ore, uscita a +30%; controllo sui picchi
senza bandiera.

Uso: python3 -m research.programma7.settantaduesima
"""
from __future__ import annotations

import csv
import io
import json
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import esecuzione as es
from research.programma6 import scarico_giorni as sg
from research.programma6 import seconda as sc
from research.programma6 import trentesima as tr
from research.programma7 import buco_perpetuo as bp
from research.programma7 import quarantatreesima as cb_
from research.programma7 import sessantaquattresima as gt

QUI = Path(__file__).parent
RIS = QUI / "risultati_settantaduesima"
METRICHE = QUI.parent / "data" / "metrics5"
DAL, AL = sc.giorno(2021, 12, 6), sc.giorno(2026, 10, 1)
SOGLIA, ETA_MIN, VOLUME_MIN, ORE_PRIMA = 1.2, 30, 2e6, 6
PROVE_A_EVENTI = 41


def picchi(pan: dict) -> list:
    t0 = pan["t0"]
    giorni = np.arange(DAL, AL)
    idx = giorni - t0
    H, O, C, V = pan["high"][idx], pan["open"][idx], pan["close"][idx], pan["quote_volume"]
    ok = np.isfinite(pan["close"])
    primo = ok.argmax(axis=0)
    eta = idx[:, None] - primo[None, :]
    Vc = np.vstack([np.zeros((1, V.shape[1])), np.cumsum(np.nan_to_num(V), axis=0)])
    Nc = np.vstack([np.zeros((1, V.shape[1])), np.cumsum(np.isfinite(V), axis=0)])
    with np.errstate(all="ignore"):
        v30 = (Vc[idx] - Vc[idx - 30]) / (Nc[idx] - Nc[idx - 30])
        p = (H >= SOGLIA * np.maximum(O, C)) & (eta >= ETA_MIN) & (v30 >= VOLUME_MIN)
    p[:, pan["simboli"].index("BTCUSDT")] = False
    k, j = np.nonzero(p)
    return [(pan["simboli"][jj], int(giorni[kk])) for kk, jj in zip(k, j)]


def metriche(s: str, g: int) -> pd.DataFrame:
    """I dati a 5 minuti di un giorno (interesse aperto in dollari, rapporto long/short dei conti grandi), indice = minuto dall'epoca."""
    d = sc.data(g)
    try:
        sg._scarica(f"data/futures/um/daily/metrics/{s}/{s}-metrics-{d}.zip", METRICHE / s)
    except Exception:  # noqa: BLE001
        return pd.DataFrame()
    f = METRICHE / s / f"{s}-metrics-{d}.zip"
    if not f.exists():
        return pd.DataFrame()
    z = zipfile.ZipFile(f)
    righe = list(csv.reader(io.TextIOWrapper(z.open(z.namelist()[0]))))
    if not righe:
        return pd.DataFrame()
    testa = righe[0]
    df = pd.DataFrame(righe[1:], columns=testa)
    df["minuto"] = (pd.to_datetime(df["create_time"]).astype("int64") // 60_000_000_000).astype(int)
    for c in ("sum_open_interest_value", "sum_toptrader_long_short_ratio"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df.set_index("minuto")[["sum_open_interest_value", "sum_toptrader_long_short_ratio"]].sort_index()


def valore_a(df: pd.DataFrame, col: str, minuto: int) -> float:
    x = df[df.index <= minuto][col].dropna()
    return float(x.iloc[-1]) if len(x) and minuto - x.index[-1] <= 15 else np.nan


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ev = picchi(pan)
    log(f"[settantaduesima] {len(ev)} giorni di picco")
    serve_ore = sorted({(s, g) for s, g in ev})
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(lambda x: gt.scarica(x[0], (x[1] - 1) * 24, (x[1] + 5) * 24), serve_ore))
        list(ex.map(lambda x: [sg._scarica(f"data/futures/um/monthly/premiumIndexKlines/{x[0]}/1h/{x[0]}-1h-{m}.zip", bp.DATI / x[0])
                               for m in bp.mesi(x[1] - 1, x[1] + 1)], serve_ore))
        list(ex.map(lambda x: (metriche(x[0], x[1]), metriche(x[0], x[1] - 1)), serve_ore))
    gt.scarica("BTCUSDT", DAL * 24, (AL + 5) * 24)
    cb = es.ore_di("BTCUSDT")
    S = list(pan["simboli"])
    giorni = np.arange(pan["close"].shape[0]) + pan["t0"]
    fb = pd.Series(np.nan_to_num(pan["funding"][:, S.index("BTCUSDT")]), index=giorni)
    ore_c, premi = {}, {}
    righe, conti = [], {"picchi": len(ev), "senza_ore": 0, "senza_premio": 0, "senza_posizioni": 0, "senza_operazione": 0}
    for s, g in ev:
        if s not in ore_c:
            ore_c[s], premi[s] = es.ore_di(s), bp.premio_ore(s)
        c, p = ore_c[s], premi[s]
        giorno = c[(c.index >= g * 24) & (c.index < (g + 1) * 24)].dropna()
        if len(giorno) < 20:
            conti["senza_ore"] += 1
            continue
        hp = int(giorno["high"].idxmax())
        p_prima, p_dopo = p.get(hp - 1 - ORE_PRIMA, np.nan), p.get(hp - 1, np.nan)
        m = pd.concat([metriche(s, g - 1), metriche(s, g)]).sort_index()
        m = m[~m.index.duplicated()]
        oi0, oi1 = valore_a(m, "sum_open_interest_value", (hp - ORE_PRIMA) * 60), valore_a(m, "sum_open_interest_value", hp * 60)
        ls0, ls1 = valore_a(m, "sum_toptrader_long_short_ratio", (hp - ORE_PRIMA) * 60), valore_a(m, "sum_toptrader_long_short_ratio", hp * 60)
        if not (np.isfinite(p_prima) and np.isfinite(p_dopo)):
            conti["senza_premio"] += 1
            continue
        if not all(np.isfinite([oi0, oi1, ls0, ls1])):
            conti["senza_posizioni"] += 1
            continue
        a, b_, cc = p_dopo < p_prima, oi1 > oi0, ls1 < ls0
        f = pd.Series(np.nan_to_num(pan["funding"][:, S.index(s)]), index=giorni)
        op = cb_.operazione(c, cb, f, fb, g + 1, 1)
        if not op:
            conti["senza_operazione"] += 1
            continue
        o3 = cb_.operazione(c, cb, f, fb, g + 1, 3)
        righe.append({"data": sc.data(g + 1), "annuncio": int((g + 1 + 3) // 7), "simbolo": s, "picco": sc.data(g), "ora_picco": hp % 24,
                      "premio_scende": a, "posizioni_salgono": b_, "grandi_riducono": cc, "bandiera": bool(a and b_ and cc), **op,
                      "r3": o3.get("r", np.nan)})
    d = pd.DataFrame(righe)
    RIS.mkdir(exist_ok=True)
    d.to_csv(RIS / "picchi_PM.csv", index=False)
    ev_b, co = d[d["bandiera"]], d[~d["bandiera"]]
    e = tr.esame(ev_b, "r")
    rng = np.random.default_rng(2026)
    b = rng.choice(ev_b["r"].to_numpy(), size=(10000, len(ev_b)), replace=True).mean(axis=1) - co["r"].mean()
    diff = {"media": float(ev_b["r"].mean() - co["r"].mean()), "basso": float(np.quantile(b, 0.025)), "alto": float(np.quantile(b, 0.975)),
            "p": float((b <= 0).mean())}
    soglia = 0.01 / PROVE_A_EVENTI
    valida = e["esito"] == "VALIDA" and diff["p"] <= 0.05
    esito = ("VALIDA" if valida and e["boot"]["p"] <= soglia else
             "passa l'esame scritto ma non la soglia di tutte le prove a eventi" if valida else
             e["esito"] if e["esito"] != "VALIDA" else "non sopra i picchi senza bandiera")
    sole = {k: float(d.loc[d[k], "r"].mean()) - float(d.loc[~d[k], "r"].mean()) for k in ("premio_scende", "posizioni_salgono", "grandi_riducono")}
    out = {"conti": conti, "picchi_con_i_dati": int(len(d)), "con_bandiera": int(len(ev_b)), "esame": e, "controllo": {"picchi": int(len(co)),
           "media": float(co["r"].mean())}, "differenza": diff, "condizioni_sole": sole, "tutti_i_picchi": float(d["r"].mean()),
           "tre_giorni_bandiera": float(ev_b["r3"].mean()), "fermate_bandiera": float(ev_b["fermata"].mean()), "esito": esito}
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda v: "—" if v is None or v != v else f"{100 * v:+.2f}%"  # noqa: E731
    bb = e["boot"]
    testo = "\n".join([
        "# Programma 7 — risultati della settantaduesima prova (PM: la pompa del pronti con i long intrappolati)", "",
        "Regole in `SETTANTADUESIMA.md` (scritte prima). Short contro il Bitcoin dall'apertura del giorno dopo un picco con la bandiera "
        "della manipolazione, 24 ore, uscita a +30%; dal dicembre 2021 al settembre 2026.", "",
        "* **I picchi**: " + ", ".join(f"{k} {v}" for k, v in conti.items()) + f"; con tutti i dati {len(d)}, **con la bandiera {len(ev_b)}**.",
        f"* **Con la bandiera: {pc(bb['media'])} a operazione** (intervallo {pc(bb['basso'])}; {pc(bb['alto'])}, p {bb['p']:.4f}); mediana "
        f"{pc(e['mediana'])}, vinte {100 * e['vinti']:.0f}%; metà {pc(e['prima_meta'])} e {pc(e['seconda_meta'])}; senza le 5 migliori "
        f"{pc(e['senza_5_migliori'])}; uscita a +30% nel {100 * out['fermate_bandiera']:.0f}%.",
        "* Per anno: " + ", ".join(f"{a} {pc(v['media'])} ({v['eventi']})" for a, v in e["per_anno"].items()) + ".",
        f"* **Controllo, i picchi senza bandiera** ({len(co)}): {pc(out['controllo']['media'])}; differenza {pc(diff['media'])} (intervallo "
        f"{pc(diff['basso'])}; {pc(diff['alto'])}, p {diff['p']:.3f}). Tutti i picchi insieme {pc(out['tutti_i_picchi'])}.",
        "* Per capire, ogni condizione da sola (con meno senza): " + ", ".join(f"{k.replace('_', ' ')} {pc(v)}" for k, v in sole.items())
        + f"; tenuta di 3 giorni con la bandiera {pc(out['tre_giorni_bandiera'])}.", "",
        f"**Esito: {esito}** (soglia contando le {PROVE_A_EVENTI} prove a eventi: {soglia:.5f})."]) + "\n"
    (QUI / "RISULTATI_SETTANTADUESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("SETTANTADUESIMA FINITA", flush=True)
