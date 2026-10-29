"""Programma 7, sessantaquattresima prova (SESSANTAQUATTRESIMA.md): GT, vendere alla fine delle gare di trading di Binance: short il
perpetuo contro il Bitcoin dal giorno dopo la fine della gara, uscita a +30% o dopo 7 giorni (come la prova 105); controllo sulle stesse
monete lontano dalle gare.

Uso: python3 -m research.programma7.sessantaquattresima
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
from research.programma7 import quarantatreesima as cb_
from research.programma7 import quarantunesima as lv

QUI = Path(__file__).parent
RIS = QUI / "risultati_sessantaquattresima"
DATI = QUI.parent / "data" / "annunci" / "gare"
GARE = re.compile(r"Trading Competition|Trading Tournament|Trading Challenge", re.I)
_D = r"(\d{4})[-/](\d{2})[-/](\d{2})\s+(\d{1,2}):(\d{2})(?:\s*(AM|PM))?"
PERIODO = re.compile(r"Period\s*:?\s*" + _D + r"\s*(?:\(UTC\))?\s*(?:to|-|–|~)\s*" + _D + r"\s*(?:\(UTC\))?", re.I)
ESCLUSE = {"UTC", "USDT", "BNB", "USD", "BUSD", "USDC", "BTC", "ETH"}
GIORNI, DOPPIONE, LONTANO, CONTROLLI, SEME = 7, 14, 30, 20, 2026
PROVE_A_EVENTI = 36


def _ora(g: tuple, k: int) -> pd.Timestamp:
    a, m, d, h, mi, ap = g[k:k + 6]
    h = int(h)
    if ap and ap.upper() == "PM" and h < 12:
        h += 12
    if ap and ap.upper() == "AM" and h == 12:
        h = 0
    return pd.Timestamp(f"{a}-{m}-{d} {h:02d}:{mi}", tz="UTC")


def moneta(titolo: str) -> str | None:
    """La sigla della moneta dal titolo (sezione 2 delle regole), o None."""
    t = titolo.replace("​", "").strip()
    for reg in (r"\(([0-9A-Z]{2,15})\)", r"^([0-9A-Z]{2,15})\b", r"USDⓈ-M ([0-9A-Z]{2,15}) ", r"\bin ([0-9A-Z]{2,15})\b"):
        tk = [x for x in re.findall(reg, t) if x not in ESCLUSE]
        if tk:
            return tk[0]
    return None


def gare() -> list:
    """Tutte le gare con periodo e moneta: (sigla, inizio, fine, titolo, ms dell'annuncio)."""
    out = []
    for f in sorted((DATI / "testi").glob("*.json")):
        d = json.loads(f.read_text())
        if not GARE.search(d["titolo"] or ""):
            continue
        m = PERIODO.search(" ".join(lv.frammenti(d["body"])))
        tk = moneta(d["titolo"])
        if m and tk:
            g = m.groups()
            out.append((tk, _ora(g, 0), _ora(g, 6), d["titolo"], d["ms"]))
    return out


def scarica(simbolo: str, h0: int, h1: int) -> None:
    """Le candele orarie dei mesi chiusi dall'archivio mensile; per il mese in corso (non ancora nell'archivio) i file giornalieri."""
    lv.scarica_ore(simbolo, h0, h1)
    for g in range(h0 // 24, h1 // 24 + 1):
        d = sc.data(g)
        if d >= "2026-10-01":
            try:
                lv.sg._scarica(f"data/futures/um/daily/klines/{simbolo}/1h/{simbolo}-1h-{d}.zip", lv.qa.DATI / simbolo / "ore")
            except Exception:  # noqa: BLE001
                pass


def esegui(log=print) -> dict:
    pan = sc.pannello()
    t0, S = pan["t0"], list(pan["simboli"])
    C, V = pan["close"], pan["quote_volume"]
    T = C.shape[0]
    ultimo_dato = t0 + T - 1
    giorni = np.arange(T) + t0
    ok = np.isfinite(C)
    primo = {s: t0 + int(ok[:, j].argmax()) for j, s in enumerate(S) if ok[:, j].any()}
    tutte = gare()
    conto = {"gare con periodo e moneta": len(tutte)}

    def perpetuo(tk):
        for s in (tk + "USDT", "1000" + tk + "USDT"):
            if s in primo:
                return s
        return None
    # tutte le date delle gare per moneta (per il controllo), anche quelle che non entrano
    date_gare: dict = {}
    for tk, ini, fine, _, _ in tutte:
        s = perpetuo(tk)
        if s:
            date_gare.setdefault(s, []).extend([int(ini.timestamp() // 86400), int(fine.timestamp() // 86400)])
    eventi, scarti = [], {"senza perpetuo": 0, "perpetuo dopo la fine": 0, "senza scambi il giorno dopo o senza 8 giorni di dati": 0,
                          "doppione entro 14 giorni": 0}
    visti: dict = {}
    for tk, ini, fine, titolo, ms in sorted(tutte, key=lambda x: x[2]):
        s = perpetuo(tk)
        if not s:
            scarti["senza perpetuo"] += 1
            continue
        gf, gi = int(fine.timestamp() // 86400), int(ini.timestamp() // 86400)
        if primo[s] > gf:
            scarti["perpetuo dopo la fine"] += 1
            continue
        j = S.index(s)
        if gf + 8 > ultimo_dato or not np.nan_to_num(V[gf + 1 - t0, j]) > 0:
            scarti["senza scambi il giorno dopo o senza 8 giorni di dati"] += 1
            continue
        if s in visti and gf - visti[s] < DOPPIONE:
            scarti["doppione entro 14 giorni"] += 1
            continue
        visti[s] = gf
        eventi.append({"s": s, "gi": gi, "gf": gf, "titolo": titolo, "alpha": "Alpha" in titolo, "eta": gf - primo[s],
                       "riuso": cb_.nascita_vera(np.nan_to_num(V[:, j]), t0, primo[s], gf) != primo[s]})
    conto.update(scarti)
    conto["eventi"] = len(eventi)
    log(f"[sessantaquattresima] {conto}")
    rng = np.random.default_rng(SEME)
    controlli = []
    for e in eventi:
        s, gf = e["s"], e["gf"]
        dg = np.array(date_gare[s])
        cand = np.r_[np.arange(gf - 365, gf - LONTANO + 1), np.arange(gf + LONTANO, gf + 366)]
        cand = cand[(cand >= primo[s]) & (cand + 8 <= ultimo_dato)]
        cand = np.array([g for g in cand if np.abs(dg - g).min() >= LONTANO], dtype=int)
        if len(cand):
            for g in rng.choice(cand, size=min(CONTROLLI, len(cand)), replace=False):
                controlli.append((s, int(g)))
    serve = sorted({(e["s"], e["gf"] + 1) for e in eventi} | {(e["s"], e["gi"]) for e in eventi} | set(controlli))
    log(f"[sessantaquattresima] {len(controlli)} controlli; scarico le candele orarie di {len(serve)} finestre")
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(lambda x: scarica(x[0], (x[1] - 1) * 24, (x[1] + 15) * 24), serve))
    scarica("BTCUSDT", (sc.giorno(2020, 1, 1)) * 24, (ultimo_dato + 1) * 24)
    cb = es.ore_di("BTCUSDT")
    jb = S.index("BTCUSDT")
    fb = pd.Series(pan["funding"][:, jb], index=giorni)
    ore: dict = {}

    def candele(s):
        if s not in ore:
            ore[s] = es.ore_di(s)
        return ore[s]
    O = pan["open"]
    righe, mancanti = [], 0
    for e in eventi:
        s, gf, gi = e["s"], e["gf"], e["gi"]
        j = S.index(s)
        f = pd.Series(pan["funding"][:, j], index=giorni)
        c = candele(s)
        op = cb_.operazione(c, cb, f, fb, gf + 1)
        if not op:
            mancanti += 1
            continue
        o3, o14 = cb_.operazione(c, cb, f, fb, gf + 1, 3), cb_.operazione(c, cb, f, fb, gf + 1, 14)
        oi = cb_.operazione(c, cb, f, fb, gi)
        k0, k1 = gi - t0, gf + 1 - t0
        durante = float((O[k1, j] / O[k0, j]) / (O[k1, jb] / O[k0, jb]) - 1) if k0 >= 0 and np.isfinite(O[k0, j]) else np.nan
        righe.append({"data": sc.data(gf + 1), "annuncio": int((gf + 1 + 3) // 7), "simbolo": s, "fine_gara": sc.data(gf), **op,
                      "r3": o3.get("r", np.nan), "r14": o14.get("r", np.nan), "r_inizio": oi.get("r", np.nan),
                      "durante_contro_btc": durante, "eta": e["eta"], "alpha": e["alpha"], "riuso": e["riuso"], "titolo": e["titolo"][:80]})
    ev = pd.DataFrame(righe)
    RIS.mkdir(exist_ok=True)
    ev.to_csv(RIS / "eventi_GT.csv", index=False)
    cr = []
    for s, g in controlli:
        j = S.index(s)
        op = cb_.operazione(candele(s), cb, pd.Series(pan["funding"][:, j], index=giorni), fb, g)
        if op:
            cr.append({"data": sc.data(g), "annuncio": int((g + 3) // 7), "simbolo": s, "r": op["r"]})
    co = pd.DataFrame(cr)
    co.to_csv(RIS / "controllo_GT.csv", index=False)
    e = tr.esame(ev, "r")
    soglia = 0.01 / PROVE_A_EVENTI
    per_moneta = co.groupby("simbolo")["r"].mean() if len(co) else pd.Series(dtype=float)
    diff = ev.set_index("simbolo")["r"] - per_moneta.reindex(ev["simbolo"]).to_numpy()
    diff = diff[np.isfinite(diff)].to_numpy()
    b = np.random.default_rng(SEME).choice(diff, size=(10000, len(diff)), replace=True).mean(axis=1) if len(diff) else np.array([np.nan])
    giovani = ev["eta"] < 60
    out = {"conto": conto, "senza_candele_orarie": mancanti, "eventi": int(len(ev)), "esame": e,
           "controllo": {"operazioni": int(len(co)), "media": float(co["r"].mean()) if len(co) else None},
           "differenza_con_controllo": {"media": float(diff.mean()) if len(diff) else None, "eventi": int(len(diff)),
                                        "basso": float(np.quantile(b, 0.025)), "alto": float(np.quantile(b, 0.975)), "p": float((b <= 0).mean())},
           "tre_giorni": float(ev["r3"].mean()), "quattordici_giorni": float(ev["r14"].mean()),
           "dall_inizio": float(ev["r_inizio"].mean()), "durante_mediana": float(ev["durante_contro_btc"].median()),
           "durante_media": float(ev["durante_contro_btc"].mean()), "fermate": float(ev["fermata"].mean()),
           "giovani": {"eventi": int(giovani.sum()), "media": float(ev.loc[giovani, "r"].mean())},
           "altre": {"eventi": int((~giovani).sum()), "media": float(ev.loc[~giovani, "r"].mean())},
           "alpha": {"eventi": int(ev["alpha"].sum()), "media": float(ev.loc[ev["alpha"], "r"].mean())},
           "non_alpha": {"eventi": int((~ev["alpha"]).sum()), "media": float(ev.loc[~ev["alpha"], "r"].mean())},
           "simboli_riusati": int(ev["riuso"].sum()), "soglia_tutte": soglia}
    valida = e["esito"] == "VALIDA" and out["differenza_con_controllo"]["p"] <= 0.05
    out["esito"] = ("VALIDA" if valida and e["boot"]["p"] <= soglia else
                    "passa l'esame scritto ma non la soglia di tutte le prove a eventi" if valida else
                    e["esito"] if e["esito"] != "VALIDA" else "non sopra il controllo sulle stesse monete")
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda v: "—" if v is None or v != v else f"{100 * v:+.2f}%"  # noqa: E731
    bb, d = e["boot"], out["differenza_con_controllo"]
    righe_t = ["# Programma 7 — risultati della sessantaquattresima prova (GT: vendere alla fine delle gare di trading di Binance)", "",
               "Regole in `SESSANTAQUATTRESIMA.md` (scritte prima). Short il perpetuo contro il Bitcoin dall'apertura del giorno dopo la fine "
               "della gara, uscita a +30% o dopo 7 giorni.", "",
               "* **Gli abbinamenti**: " + ", ".join(f"{k} {v}" for k, v in conto.items()) + f"; senza candele orarie {mancanti}.",
               f"* **{bb['eventi']} eventi: {pc(bb['media'])} a operazione** (intervallo {pc(bb['basso'])}; {pc(bb['alto'])}, p {bb['p']:.4f}); mediana "
               f"{pc(e['mediana'])}, vinte {100 * e['vinti']:.0f}%; metà {pc(e['prima_meta'])} e {pc(e['seconda_meta'])}; senza le 5 migliori "
               f"{pc(e['senza_5_migliori'])}; uscita a +30% nel {100 * out['fermate']:.0f}%.",
               "* Per anno: " + ", ".join(f"{a} {pc(v['media'])} ({v['eventi']})" for a, v in e["per_anno"].items()) + ".",
               f"* **Controllo** (le stesse monete in {out['controllo']['operazioni']} giorni lontani dalle gare): {pc(out['controllo']['media'])}; "
               f"differenza evento − controllo {pc(d['media'])} su {d['eventi']} eventi (intervallo {pc(d['basso'])}; {pc(d['alto'])}, p {d['p']:.3f}).",
               f"* Per capire: tenute di 3 giorni {pc(out['tre_giorni'])}, di 14 giorni {pc(out['quattordici_giorni'])}; la stessa operazione "
               f"aperta il giorno dell'inizio della gara {pc(out['dall_inizio'])}; la moneta contro il Bitcoin durante la gara, mediana "
               f"{pc(out['durante_mediana'])} (media {pc(out['durante_media'])}); perpetuo da meno di 60 giorni {pc(out['giovani']['media'])} "
               f"({out['giovani']['eventi']}), gli altri {pc(out['altre']['media'])} ({out['altre']['eventi']}); Binance Alpha "
               f"{pc(out['alpha']['media'])} ({out['alpha']['eventi']}), le altre {pc(out['non_alpha']['media'])} ({out['non_alpha']['eventi']}); "
               f"simboli che sembrano riusati (volume a zero per 7 giorni prima della fine) {out['simboli_riusati']}.", "",
               f"**Esito: {out['esito']}** (soglia contando le {PROVE_A_EVENTI} prove a eventi: {soglia:.5f})."]
    testo = "\n".join(righe_t) + "\n"
    (QUI / "RISULTATI_SESSANTAQUATTRESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("SESSANTAQUATTRESIMA FINITA", flush=True)
