"""Programma 7, quarantunesima prova (QUARANTUNESIMA.md): LV, i tagli della leva massima annunciati da Binance sui perpetui: short la
moneta contro il Bitcoin dall'ora dopo l'annuncio a 72 ore dopo il cambio; gli aumenti accanto per confronto.

Uso: python3 -m research.programma7.quarantunesima
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import esecuzione as es
from research.programma6 import scarico_giorni as sg
from research.programma6 import quarta as qa
from research.programma6 import seconda as sc
from research.programma6 import trentesima as tr
from research.programma6 import ventunesima as vu

QUI = Path(__file__).parent
RIS = QUI / "risultati_quarantunesima"
DATI = QUI.parent / "data" / "annunci" / "margini"
LISTA = "https://www.binance.com/bapi/composite/v1/public/cms/article/list/query?type=1&catalogId=49&pageNo={p}&pageSize=50"
DETTAGLIO = "https://www.binance.com/bapi/composite/v1/public/cms/article/detail/query?articleCode={c}"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0"}
TITOLI = re.compile(r"leverage (and|&) margin tiers|adjust(s|ment)? .* leverage|margin tiers", re.I)
DATA_UTC = re.compile(r"(\d{4}-\d{2}-\d{2}) (\d{2}):(\d{2}) \(UTC\)")
CONTRATTI = re.compile(r"\(USDⓈ-M Perpetual Contracts?\)")
SIMBOLO = re.compile(r"\b[0-9A-Z]{2,20}USDT\b")
ORE_DOPO = 72
PROVE_A_EVENTI = 29


def _get(url: str):
    for k in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                d = json.load(r)
            if d.get("data"):
                return d
        except Exception:  # noqa: BLE001
            pass
        time.sleep(2 ** (k + 1))
    return None


def scarica(log=print) -> list:
    """Gli annunci sui margini (codice, titolo, ora) e il loro testo, salvati in DATI."""
    DATI.mkdir(parents=True, exist_ok=True)
    f = DATI / "elenco.json"
    if f.exists():
        elenco = json.loads(f.read_text())
    else:
        elenco, p, totale = [], 1, 1
        while (p - 1) * 50 < totale:
            d = _get(LISTA.format(p=p))
            cats = (d or {}).get("data", {}).get("catalogs") or []
            if not cats:
                raise RuntimeError(f"pagina {p} non scaricata")
            totale = int(cats[0]["total"])
            elenco += [{"id": a["id"], "code": a["code"], "titolo": a["title"], "ms": a["releaseDate"]} for a in cats[0]["articles"]
                       if TITOLI.search(a["title"])]
            p += 1
            time.sleep(0.3)
        f.write_text(json.dumps(elenco))

    def uno(a):
        g = DATI / f"{a['id']}.json"
        if g.exists():
            return True
        d = _get(DETTAGLIO.format(c=a["code"]))
        if not d:
            return False
        g.write_text(json.dumps({"id": a["id"], "body": d["data"].get("body") or ""}))
        return True
    with ThreadPoolExecutor(max_workers=4) as ex:
        ok = list(ex.map(uno, elenco))
    log(f"[quarantunesima] {len(elenco)} annunci sui margini, testi scaricati {sum(ok)}")
    return elenco


def _testi(nodo, acc: list) -> list:
    if isinstance(nodo, dict):
        if nodo.get("node") == "text":
            t = (nodo.get("text") or "").replace("&nbsp;", " ").replace("&lt;", "<").replace("&amp;", "&").strip()
            if t:
                acc.append(t)
        for ch in nodo.get("child") or []:
            _testi(ch, acc)
    elif isinstance(nodo, list):
        for x in nodo:
            _testi(x, acc)
    return acc


def frammenti(body: str) -> list:
    try:
        return _testi(json.loads(body), [])
    except Exception:  # noqa: BLE001
        return [x.strip() for x in re.split(r"<[^>]+>", body) if x.strip()]


def leva_massima(testo: str) -> float:
    """Il numero piu' alto in «21 - 50x», «5x», «1-3x»; NaN se non c'e'."""
    m = re.findall(r"(\d+)\s*x", testo.replace(" ", "")) if "x" in testo else []
    nums = [int(x) for x in re.findall(r"\d+", testo)] if re.search(r"\d+\s*x\b", testo) else []
    return float(max(nums)) if nums else float("nan")


def _ms(data: str, h: str, mi: str) -> int:
    return int(dt.datetime(*map(int, data.split("-")), int(h), int(mi), tzinfo=dt.timezone.utc).timestamp() * 1000)


def eventi_dell_annuncio(fr: list, ms_annuncio: int) -> list:
    """Le righe (simbolo, ora del cambio in ms, leva prima, leva dopo) lette dalle tabelle di un annuncio."""
    out = []
    prima_data = None
    for t in fr:
        m = DATA_UTC.search(t)
        if m:
            prima_data = _ms(*m.groups())
            break
    ultima_data = None
    k = 0
    while k < len(fr):
        t = fr[k]
        m = DATA_UTC.search(t)
        if m:
            ultima_data = _ms(*m.groups())
        if CONTRATTI.search(t) and SIMBOLO.search(t):
            simboli = sorted(set(SIMBOLO.findall(t)))
            # la tabella che segue: dopo l'intestazione «... After Change» (6 colonne) le prime 6 celle sono la prima riga
            j = k + 1
            while j < len(fr) and not fr[j].startswith("Leverage Before Change") and not CONTRATTI.search(fr[j]):
                j += 1
            if j < len(fr) and fr[j].startswith("Leverage Before Change"):
                h = j
                while h < len(fr) and "Maintenance Margin Rate After Change" not in fr[h]:
                    h += 1
                riga = fr[h + 1:h + 7]
                if len(riga) == 6:
                    lp, ld = leva_massima(riga[0]), leva_massima(riga[3])
                    ora = ultima_data or prima_data or ms_annuncio
                    for s in simboli:
                        out.append({"simbolo": s, "cambio_ms": int(ora), "leva_prima": lp, "leva_dopo": ld})
                k = h
        k += 1
    return out


def _mesi(h0: int, h1: int) -> list:
    return sorted({sc.data(g)[:7] for g in range(h0 // 24, h1 // 24 + 2)})


def scarica_ore(simbolo: str, h0: int, h1: int) -> None:
    for m in _mesi(h0, h1):
        try:
            sg._scarica(f"data/futures/um/monthly/klines/{simbolo}/1h/{simbolo}-1h-{m}.zip", qa.DATI / simbolo / "ore")
        except Exception:  # noqa: BLE001
            pass


def operazione(c: pd.DataFrame, cb: pd.DataFrame, f: pd.Series, fb: pd.Series, h0: int, h1: int) -> dict:
    """Short la moneta e long il Bitcoin dall'apertura dell'ora h0 all'apertura dell'ora h1 (o l'ultimo prezzo se la serie finisce)."""
    if h0 not in c.index or h0 not in cb.index:
        return {}
    p0, b0 = c.loc[h0, "open"], cb.loc[h0, "open"]
    if h1 in c.index:
        pc = c.loc[h1, "open"]
    else:
        tratto = c[(c.index >= h0) & (c.index < h1)]
        if not len(tratto):
            return {}
        pc, h1 = tratto["close"].iloc[-1], int(tratto.index[-1]) + 1
    pb = cb.loc[h1, "open"] if h1 in cb.index else cb[cb.index <= h1]["close"].iloc[-1]
    g0, g1 = h0 // 24, (h1 - 1) // 24
    fc = f[(f.index >= g0) & (f.index <= g1)].sum()
    fbb = fb[(fb.index >= g0) & (fb.index <= g1)].sum()
    return {"r": float((pb / b0 - 1) - (pc / p0 - 1) - vu.COSTO_MONETA - vu.COSTO_BTC + fc - fbb), "ore": int(h1 - h0)}


def esegui(log=print) -> dict:
    elenco = scarica(log)
    righe = []
    for a in elenco:
        g = DATI / f"{a['id']}.json"
        if not g.exists():
            continue
        fr = frammenti(json.loads(g.read_text())["body"])
        for e in eventi_dell_annuncio(fr, int(a["ms"])):
            righe.append({"annuncio": a["id"], "annuncio_ms": int(a["ms"]), "titolo": a["titolo"][:120],
                          "posizioni_esistenti_toccate": bool(re.search(r"will be affected", " ".join(fr), re.I)) and not re.search(r"will\s+not\s+be affected", " ".join(fr), re.I), **e})
    ev = pd.DataFrame(righe).drop_duplicates(["simbolo", "cambio_ms"]).reset_index(drop=True)
    ev = ev[np.isfinite(ev["leva_prima"]) & np.isfinite(ev["leva_dopo"])].reset_index(drop=True)
    ev["tipo"] = np.where(ev["leva_dopo"] < ev["leva_prima"], "taglio", np.where(ev["leva_dopo"] > ev["leva_prima"], "aumento", "uguale"))
    RIS.mkdir(exist_ok=True)
    ev.to_csv(RIS / "eventi_letti.csv", index=False)
    log(f"[quarantunesima] eventi letti: {len(ev)} (tagli {int((ev['tipo'] == 'taglio').sum())}, aumenti {int((ev['tipo'] == 'aumento').sum())})")
    pan = sc.pannello()
    giorni = np.arange(pan["close"].shape[0]) + pan["t0"]
    jb = pan["simboli"].index("BTCUSDT")
    fb = pd.Series(pan["funding"][:, jb], index=giorni)
    V = pan["quote_volume"]
    ev["h0"] = (ev["annuncio_ms"] // 3_600_000 + 1).astype(int)
    ev["h_cambio"] = (ev["cambio_ms"] // 3_600_000).astype(int)
    ev["h1"] = np.maximum(ev["h_cambio"], ev["h0"]) + ORE_DOPO
    ammessi = []
    for k, x in ev.iterrows():
        s = x["simbolo"]
        if s == "BTCUSDT" or s not in pan["simboli"]:
            continue
        j = pan["simboli"].index(s)
        kk = x["h0"] // 24 - 1 - pan["t0"]
        if 0 <= kk < V.shape[0] and np.nan_to_num(V[kk, j]) > 0:
            ammessi.append(k)
    ev = ev.loc[ammessi].reset_index(drop=True)
    log(f"[quarantunesima] ammessi (nel pannello, volume il giorno prima): {len(ev)}; scarico le candele orarie")
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(lambda x: scarica_ore(x[0], x[1], x[2]), zip(ev["simbolo"], ev["h0"], ev["h1"])))
    scarica_ore("BTCUSDT", int(ev["h0"].min()), int(ev["h1"].max()))
    cb = es.ore_di("BTCUSDT")
    out_r = []
    for _, x in ev.iterrows():
        j = pan["simboli"].index(x["simbolo"])
        f = pd.Series(pan["funding"][:, j], index=giorni)
        op = operazione(es.ore_di(x["simbolo"]), cb, f, fb, int(x["h0"]), int(x["h1"]))
        out_r.append(op.get("r", np.nan))
    ev["r"] = out_r
    ev["data"] = ev["h0"].map(lambda h: sc.data(int(h) // 24))
    ev.to_csv(RIS / "eventi_LV.csv", index=False)
    tagli = ev[(ev["tipo"] == "taglio") & np.isfinite(ev["r"])].reset_index(drop=True)
    aumenti = ev[(ev["tipo"] == "aumento") & np.isfinite(ev["r"])].reset_index(drop=True)
    e_t = tr.esame(tagli, "r")
    e_a = tr.esame(aumenti, "r") if len(aumenti) > 10 else None
    soglia = 0.01 / PROVE_A_EVENTI
    out = {"eventi_letti": int(len(righe)), "ammessi": int(len(ev)), "tagli": e_t, "aumenti": e_a, "soglia_tutte": soglia,
           "rapporto_medio_taglio": float((tagli["leva_dopo"] / tagli["leva_prima"]).mean()) if len(tagli) else None,
           "tagli_con_posizioni_esistenti": {"n": int(tagli["posizioni_esistenti_toccate"].sum()),
                                             "media": float(tagli.loc[tagli["posizioni_esistenti_toccate"], "r"].mean()) if tagli["posizioni_esistenti_toccate"].any() else None,
                                             "altri_media": float(tagli.loc[~tagli["posizioni_esistenti_toccate"], "r"].mean()) if (~tagli["posizioni_esistenti_toccate"]).any() else None},
           "senza_candele": int((~np.isfinite(ev["r"])).sum()),
           "impronta_eventi": hashlib.sha256(ev[["simbolo", "cambio_ms", "leva_prima", "leva_dopo"]].to_csv(index=False).encode()).hexdigest()}
    out["esito"] = ("VALIDA" if e_t["esito"] == "VALIDA" and e_t["boot"]["p"] <= soglia else
                    "passa l'esame scritto ma non la soglia di tutte le prove a eventi" if e_t["esito"] == "VALIDA" else e_t["esito"])
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda v: "—" if v is None else f"{100 * v:+.2f}%"  # noqa: E731
    b = e_t["boot"]
    righe_t = ["# Programma 7 — risultati della quarantunesima prova (LV: i tagli della leva massima annunciati da Binance)", "",
               "Regole in `QUARANTUNESIMA.md` (scritte prima). Short la moneta e long il Bitcoin dall'ora dopo l'annuncio a 72 ore dopo il cambio.", "",
               f"* Righe lette dalle tabelle {out['eventi_letti']}; eventi ammessi {out['ammessi']} (senza candele {out['senza_candele']}).",
               f"* **Tagli: {b['eventi']} in {b['annunci']} annunci, {pc(b['media'])} a operazione** (intervallo {pc(b['basso'])}; {pc(b['alto'])}, p {b['p']:.4f}); "
               f"mediana {pc(e_t['mediana'])}, vinte {100 * e_t['vinti']:.0f}%; metà {pc(e_t['prima_meta'])} e {pc(e_t['seconda_meta'])}; senza le 5 migliori "
               f"{pc(e_t['senza_5_migliori'])}; leva dopo / prima in media {out['rapporto_medio_taglio']:.2f}.",
               "* Per anno: " + ", ".join(f"{a} {pc(v['media'])} ({v['eventi']})" for a, v in e_t["per_anno"].items()) + ".",
               f"* Tagli che toccano anche le posizioni esistenti: {out['tagli_con_posizioni_esistenti']['n']}, media {pc(out['tagli_con_posizioni_esistenti']['media'])}; "
               f"gli altri {pc(out['tagli_con_posizioni_esistenti']['altri_media'])}.",
               (f"* Aumenti (per confronto, la stessa operazione): {e_a['boot']['eventi']} eventi, {pc(e_a['boot']['media'])} (p {e_a['boot']['p']:.3f})." if e_a else "* Aumenti: troppo pochi."),
               "", f"**Esito: {out['esito']}** (soglia contando le {PROVE_A_EVENTI} prove a eventi: {soglia:.5f})."]
    testo = "\n".join(righe_t) + "\n"
    (QUI / "RISULTATI_QUARANTUNESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("QUARANTUNESIMA FINITA", flush=True)
