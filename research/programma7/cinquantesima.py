"""Programma 7, cinquantesima prova (CINQUANTESIMA.md): LQ, comprare dopo le cascate di vendite forzate in giornata. Segnale alla
fine dell'ora t: la chiusura almeno il 5% sotto quella dell'ora prima e l'interesse aperto in monete (rilevazioni a 5 minuti
dell'archivio di Binance, minuto 60·t + 55 contro 60·t − 5) almeno il 5% sotto; long all'apertura del minuto 60·(t + 1) + 5,
uscita dopo 4 ore, protezione −15%. Controlli C1 (posizioni in salita), C2 (solo il prezzo), il caso.

Uso: python3 -m research.programma7.cinquantesima [--conta]
"""
from __future__ import annotations

import hashlib
import io
import json
import sys
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma5.strumenti.scarico import BASE, _prendi
from research.programma6 import asticella as ast
from research.programma6 import esecuzione as es
from research.programma6 import quarantunesima as qu
from research.programma6 import seconda as sc
from research.programma6 import terza as te
from research.programma6 import trentesima as tr
from research.src.dati import leggi_checksum
from research.trader_copiati.analisi_trader2 import minuti

QUI = Path(__file__).parent
RADICE = QUI.parents[1]
RIS = QUI / "risultati_cinquantesima"
P5 = RADICE / "research" / "data" / "p5"
METRICS = RADICE / "research" / "data" / "p7_cascate" / "metrics"
DA, A = sc.giorno(2021, 12, 1), sc.giorno(2026, 10, 24)
CALO_PREZZO, CALO_POSIZIONI = 0.95, 0.95
RITARDO, ORE, PROTEZIONE, SCARTO = 5, 240, 0.15, 0.01
ORIZZONTI = (60, 240, 1440)
MERCATO = 0.97
PROVE_A_EVENTI = 33
INIZIO_PORTAFOGLIO = sc.giorno(2021, 12, 6)


# --- i dati sulle posizioni a 5 minuti ---------------------------------------------------------------------------------------

def _metrics_grezzo(s: str, data: str) -> bytes | None:
    nome = f"{s}-metrics-{data}.zip"
    locale = P5 / s / "metrics" / nome
    if locale.exists() and locale.with_suffix(".zip.ok").exists():
        return locale.read_bytes()
    cache = METRICS / s / nome
    if cache.exists():
        return cache.read_bytes()
    chiave = f"data/futures/um/daily/metrics/{s}/{nome}"
    grezzo = _prendi(BASE + chiave)
    if grezzo is None:
        return None
    somma = _prendi(BASE + chiave + ".CHECKSUM")
    if somma is not None and leggi_checksum(somma, chiave) != hashlib.sha256(grezzo).hexdigest():
        raise RuntimeError(f"CHECKSUM diverso per {chiave}")
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_bytes(grezzo)
    return grezzo


def posizioni(s: str, g: int) -> pd.Series:
    """L'interesse aperto in monete del giorno g, indicizzato dal minuto dall'epoca (vuota se il file manca o e' rotto)."""
    grezzo = _metrics_grezzo(s, sc.data(g))
    if grezzo is None:
        return pd.Series(dtype=float)
    try:
        with zipfile.ZipFile(io.BytesIO(grezzo)) as z:
            df = pd.read_csv(io.BytesIO(z.read(z.namelist()[0])))
        t = pd.to_datetime(df["create_time"], utc=True)
        minuto = (t.astype("int64") // 60_000_000_000).to_numpy()
        return pd.Series(pd.to_numeric(df["sum_open_interest"], errors="coerce").to_numpy(), index=minuto).dropna()
    except Exception:  # noqa: BLE001
        return pd.Series(dtype=float)


# --- i candidati (a), sulle candele orarie ------------------------------------------------------------------------------------

def candidati(log=print) -> tuple[list, dict]:
    """[(simbolo, ora t)] con la condizione (a) nelle settimane in cui la moneta e' nell'universo; e le ore del Bitcoin."""
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    lun = ps["lunedi"]
    settimane: dict = {}
    for k in range(len(lun)):
        if lun[k] + 7 <= DA or lun[k] > A:
            continue
        for j in np.flatnonzero(ps["U"][k]):
            settimane.setdefault(ps["simboli"][j], []).append(int(lun[k]))
    out = []
    for s, ls in sorted(settimane.items()):
        o = es.ore_di(s)
        if o.empty:
            continue
        c = o["close"]
        r = c / c.shift(1)
        ammesse = np.concatenate([np.arange(l * 24, l * 24 + 168) for l in ls])
        ammesse = ammesse[(ammesse >= DA * 24) & (ammesse < (A + 1) * 24)]
        rr = r.reindex(ammesse).to_numpy()
        for t in ammesse[np.nan_to_num(rr, nan=9.0) <= CALO_PREZZO]:
            out.append((s, int(t)))
    btc = es.ore_di("BTCUSDT")
    log(f"[cinquantesima] {len(out)} ore con la condizione sul prezzo su {len({s for s, _ in out})} monete "
        f"({len(settimane)} monete passate per l'universo)")
    return out, {"btc": btc, "pan": pan, "ps": ps}


def giorni_posizioni(cand: list) -> set:
    return {(s, g) for s, t in cand for g in {(60 * t - 5) // 1440, (60 * t + 55) // 1440}}


def classifica(cand: list, log=print) -> pd.DataFrame:
    """Per ogni candidato le due rilevazioni dell'interesse aperto e il gruppo (LQ, C1, o nessuno dei due)."""
    servono = sorted(giorni_posizioni(cand))
    log(f"[cinquantesima] {len(servono)} giorni-moneta di dati sulle posizioni da leggere")
    with ThreadPoolExecutor(max_workers=8) as ex:
        serie = dict(zip(servono, ex.map(lambda x: posizioni(*x), servono)))
    righe = []
    for s, t in cand:
        a0, a1 = 60 * t - 5, 60 * t + 55
        p0 = serie.get((s, a0 // 1440), pd.Series(dtype=float)).get(a0, np.nan)
        p1 = serie.get((s, a1 // 1440), pd.Series(dtype=float)).get(a1, np.nan)
        righe.append({"simbolo": s, "ora": t, "oi_inizio": p0, "oi_fine": p1})
    d = pd.DataFrame(righe)
    ok = np.isfinite(d["oi_inizio"]) & np.isfinite(d["oi_fine"]) & (d["oi_inizio"] > 0)
    d["con_posizioni"] = ok
    d["variazione_oi"] = np.where(ok, d["oi_fine"] / d["oi_inizio"] - 1, np.nan)
    d["LQ"] = ok & (d["oi_fine"] <= CALO_POSIZIONI * d["oi_inizio"])
    d["C1"] = ok & (d["oi_fine"] >= d["oi_inizio"])
    d["C2"] = ok
    mancano = int((~ok).sum())
    log(f"[cinquantesima] con i dati sulle posizioni {int(ok.sum())}, senza {mancano}; LQ {int(d['LQ'].sum())}, "
        f"C1 {int(d['C1'].sum())}")
    return d


# --- le operazioni sulle candele a 1 minuto -----------------------------------------------------------------------------------

def finestra(s: str, e: int) -> pd.DataFrame:
    parti = [minuti(s, sc.data(g)) for g in range(e // 1440, (e + max(ORIZZONTI)) // 1440 + 1)]
    parti = [p for p in parti if not p.empty]
    return pd.concat(parti).sort_index() if parti else pd.DataFrame()


def operazione(w: pd.DataFrame, e: int, durata: int) -> dict | None:
    """Long all'apertura del minuto e; protezione −15% (uscita al livello meno l'1%); uscita all'apertura di e + durata."""
    if w.empty or e not in w.index:
        return None
    p0 = float(w.loc[e, "open"])
    if not p0 > 0:
        return None
    tratto = w.loc[e:e + durata - 1]
    lo, mm = tratto["low"].to_numpy(), tratto.index.to_numpy()
    giu = np.flatnonzero(lo <= p0 * (1 - PROTEZIONE))
    if len(giu):
        return {"uscita_min": int(mm[giu[0]]), "px": p0 * (1 - PROTEZIONE) * (1 - SCARTO), "motivo": "protezione", "p0": p0}
    fine = e + durata
    if fine in w.index:
        return {"uscita_min": fine, "px": float(w.loc[fine, "open"]), "motivo": "tempo", "p0": p0}
    ultimo = int(mm[-1]) if len(mm) else e
    return {"uscita_min": ultimo, "px": float(w.loc[ultimo, "close"]), "motivo": "dati finiti", "p0": p0}


def gruppo(d: pd.DataFrame, col: str, costo: dict, fund: dict, btc: pd.DataFrame, cache: dict, durata: int = ORE) -> pd.DataFrame:
    """Le operazioni del gruppo: una posizione per moneta, il segnale seguente conta solo dopo l'uscita."""
    righe = []
    for s, g in d[d[col]].sort_values("ora").groupby("simbolo"):
        libero = -1
        for t in g["ora"]:
            e = 60 * (t + 1) + RITARDO
            if e < libero:
                continue
            if (s, e) not in cache:
                cache[(s, e)] = finestra(s, e)
            op = operazione(cache[(s, e)], e, durata)
            if op is None:
                continue
            libero = op["uscita_min"]
            minuti_tenuti = op["uscita_min"] - e
            f = fund.get((s, e // 1440), 0.0) * minuti_tenuti / 1440.0
            r_prezzo = op["px"] / op["p0"] - 1
            h0, h1 = t + 1, (op["uscita_min"]) // 60
            b0 = btc["open"].get(h0, np.nan)
            b1 = btc["open"].get(h1, np.nan)
            rb = b1 / b0 - 1 if np.isfinite(b0) and np.isfinite(b1) and b0 > 0 else np.nan
            bt = btc["close"].get(t, np.nan) / btc["close"].get(t - 1, np.nan)
            righe.append({"data": sc.data(e // 1440), "annuncio": int((e // 1440 + 3) // 7), "simbolo": s, "ora": t,
                          "entrata_min": e, "uscita_min": op["uscita_min"], "minuti": minuti_tenuti, "motivo": op["motivo"],
                          "r_prezzo": r_prezzo, "costi": 2 * costo[s], "funding": f,
                          "r": r_prezzo - 2 * costo[s] - f, "r_btc": rb, "mercato": bool(np.nan_to_num(bt, nan=1.0) <= MERCATO)})
    return pd.DataFrame(righe)


def caso(lq: pd.DataFrame, costo: dict, fund: dict, cache: dict, seme: int = 2026) -> pd.DataFrame:
    """Lo stesso numero di entrate a ore prese a caso negli stessi giorni-moneta, con la stessa uscita."""
    rng = np.random.default_rng(seme)
    righe = []
    for (s, giorno), g in lq.groupby(["simbolo", lq["entrata_min"] // 1440]):
        for h in rng.integers(0, 24, size=len(g)):
            e = int(giorno) * 1440 + 60 * int(h) + RITARDO
            if (s, e) not in cache:
                cache[(s, e)] = finestra(s, e)
            op = operazione(cache[(s, e)], e, ORE)
            if op is None:
                continue
            f = fund.get((s, e // 1440), 0.0) * (op["uscita_min"] - e) / 1440.0
            righe.append({"data": sc.data(e // 1440), "annuncio": int((e // 1440 + 3) // 7), "simbolo": s,
                          "r": op["px"] / op["p0"] - 1 - 2 * costo[s] - f, "motivo": op["motivo"]})
    return pd.DataFrame(righe)


def _breve(df: pd.DataFrame) -> dict:
    if not len(df):
        return {"operazioni": 0}
    return {"operazioni": int(len(df)), "media": float(df["r"].mean()), "mediana": float(df["r"].median()),
            "vinte": float((df["r"] > 0).mean())}


def esegui(log=print, solo_conta: bool = False) -> dict:
    cand, extra = candidati(log)
    if solo_conta:
        return {"candidati": len(cand)}
    d = classifica(cand, log)
    pan, btc = extra["pan"], extra["btc"]
    simboli = pan["simboli"]
    costo = dict(zip(simboli, sc.costi_moneta(simboli)))
    t0 = pan["t0"]
    fund = {}
    for s in d["simbolo"].unique():
        j = simboli.index(s)
        for g in range(DA, A + 2):
            v = pan["funding"][g - t0, j] if 0 <= g - t0 < pan["funding"].shape[0] else np.nan
            fund[(s, g)] = float(np.nan_to_num(v))
    cache: dict = {}
    # le candele a 1 minuto di tutti i giorni che servono (C2 contiene LQ e C1; il caso usa i giorni di LQ), scaricate in parallelo
    file = sorted({(s, g) for s, t in d.loc[d["C2"], ["simbolo", "ora"]].itertuples(index=False)
                   for g in range((60 * (t + 1) + RITARDO) // 1440, (60 * (t + 1) + RITARDO + max(ORIZZONTI)) // 1440 + 1)})
    log(f"[cinquantesima] {len(file)} giorni-moneta di candele a 1 minuto")
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(lambda x: minuti(x[0], sc.data(x[1])), file))
    log("[cinquantesima] operazioni LQ")
    lq = gruppo(d, "LQ", costo, fund, btc, cache)
    RIS.mkdir(exist_ok=True)
    lq.to_csv(RIS / "eventi_LQ.csv", index=False)
    log(f"[cinquantesima] {len(lq)} operazioni LQ; controlli")
    c1 = gruppo(d, "C1", costo, fund, btc, cache)
    c2 = gruppo(d, "C2", costo, fund, btc, cache)
    cs = caso(lq, costo, fund, cache)
    c1.to_csv(RIS / "eventi_C1.csv", index=False)
    c2.to_csv(RIS / "eventi_C2.csv", index=False)
    cs.to_csv(RIS / "caso.csv", index=False)
    orizzonti = {}
    for h in ORIZZONTI:
        if h == ORE:
            continue
        x = gruppo(d, "LQ", costo, fund, btc, cache, durata=h)
        orizzonti[f"{h // 60} ore"] = _breve(x)
    ex_ = tr.esame(lq, "r")
    doppi = lq.assign(r2=lq["r"] - lq["costi"])
    coperta = lq.assign(rc=lq["r"] - lq["r_btc"].fillna(0.0) - 2 * costo.get("BTCUSDT", 0.0006))
    giorni = lq.groupby("data")["r"].sum().sort_values(ascending=False)
    out = {"candidati": len(cand), "con_posizioni": int(d["con_posizioni"].sum()), "senza_posizioni": int((~d["con_posizioni"]).sum()),
           "segnali": {"LQ": int(d["LQ"].sum()), "C1": int(d["C1"].sum()), "C2": int(d["C2"].sum())},
           "eventi": ex_, "operazioni": len(lq), "monete": int(lq["simbolo"].nunique()), "giorni": int(lq["data"].nunique()),
           "motivi": lq["motivo"].value_counts(normalize=True).round(4).to_dict(),
           "r_prezzo_medio": float(lq["r_prezzo"].mean()), "costi_medi": float(lq["costi"].mean()),
           "funding_medio": float(lq["funding"].mean()),
           "costi_doppi": float(doppi["r2"].mean()), "coperta_btc": float(coperta["rc"].mean()),
           "mercato": _breve(lq[lq["mercato"]]), "da_sola": _breve(lq[~lq["mercato"]]),
           "C1": _breve(c1), "C2": _breve(c2), "caso": _breve(cs), "orizzonti": orizzonti,
           "quota_5_giorni_migliori": float(giorni.iloc[:5].sum() / lq["r"].sum()) if lq["r"].sum() != 0 else None,
           "giorni_migliori": {k: float(v) for k, v in giorni.iloc[:5].items()},
           "variazione_oi_LQ_mediana": float(d.loc[d["LQ"], "variazione_oi"].median()) if d["LQ"].any() else None,
           "soglia_tutte": 0.01 / PROVE_A_EVENTI}
    ev = pd.DataFrame({"simbolo": lq["simbolo"], "ora": lq["entrata_min"] // 60, "uscita_h": lq["uscita_min"] // 60 + 1, "r": lq["r"]})
    port = qu.portafoglio(ev)
    port.to_csv(RIS / "settimane_LQ.csv.gz")
    ps = extra["ps"]
    rb = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    port_p = port[(port.index >= INIZIO_PORTAFOGLIO) & (port.index <= A)]
    p = te.esame(port_p, rb, inizio=INIZIO_PORTAFOGLIO, anni_pieni=(2022, 2023, 2024, 2025))
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), "112 LQ": port["netto"]}, {"112 LQ": p["intero"]})
    rr = rivisto["candidate"]["112 LQ"]
    p["sharpe_corretto"], p["t"], p["gruppi"] = rr["corretto_con_aggiunta"], rr["t"], rivisto["gruppi"]
    p["esito"] = te.esito(p, p["sharpe_corretto"])
    out["portafoglio"] = p
    passa = ex_["esito"] == "VALIDA" and out["costi_doppi"] > 0
    out["esito"] = ("VALIDA" if passa and ex_["boot"]["p"] <= out["soglia_tutte"] else
                    "passa l'esame scritto (p ≤ 0,01) ma non la soglia di tutte le prove a eventi" if passa else
                    ex_["esito"] if ex_["esito"] != "VALIDA" else "non positiva con i costi doppi")
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    scrivi(out)
    return out


def scrivi(out: dict) -> None:
    ex_, p = out["eventi"], out["portafoglio"]
    b, i = ex_["boot"], p["intero"]

    def br(x: dict) -> str:
        return (f"{x['operazioni']} operazioni, {100 * x['media']:+.2f}% a operazione, mediana {100 * x['mediana']:+.2f}%, vinte "
                f"{100 * x['vinte']:.0f}%") if x.get("operazioni") else "nessuna operazione"

    testo = "\n".join([
        "# Programma 7 — risultati della cinquantesima prova (LQ: comprare dopo le cascate di vendite forzate, in giornata)", "",
        "Regole in `CINQUANTESIMA.md` (scritte prima). Periodo 1° dicembre 2021 – 24 ottobre 2026, le 100 monete più scambiate di "
        "ogni settimana, candele a 1 ora e a 1 minuto e interesse aperto a 5 minuti dell'archivio di Binance.", "",
        f"* **I segnali**: {out['candidati']} ore con il prezzo giù almeno del 5%; di queste {out['con_posizioni']} con i dati sulle "
        f"posizioni ({out['senza_posizioni']} senza, saltate). Con le posizioni giù almeno del 5% (LQ): {out['segnali']['LQ']}; con le "
        f"posizioni in salita (C1): {out['segnali']['C1']}.",
        f"* **LQ: {out['operazioni']} operazioni** su {out['monete']} monete in {out['giorni']} giorni; uscite: " +
        ", ".join(f"{k} {100 * v:.0f}%" for k, v in out["motivi"].items()) + ".",
        f"* **{100 * b['media']:+.2f}% a operazione** dopo i costi (intervallo {100 * b['basso']:+.2f}%; {100 * b['alto']:+.2f}%, p "
        f"{b['p']:.4f}); mediana {100 * ex_['mediana']:+.2f}%, vinte {100 * ex_['vinti']:.0f}%; metà {100 * ex_['prima_meta']:+.2f}% e "
        f"{100 * ex_['seconda_meta']:+.2f}%; senza le 5 migliori {100 * ex_['senza_5_migliori']:+.2f}%. Prezzo "
        f"{100 * out['r_prezzo_medio']:+.2f}%, costi {100 * out['costi_medi']:.2f}%, funding {100 * out['funding_medio']:+.3f}%; "
        f"con i costi doppi {100 * out['costi_doppi']:+.2f}%; coperta con il Bitcoin {100 * out['coperta_btc']:+.2f}%.",
        "* Per anno: " + ", ".join(f"{a} {100 * v['media']:+.2f}% ({v['eventi']})" for a, v in ex_["per_anno"].items()) + ".",
        f"* I 5 giorni migliori fanno il {100 * (out['quota_5_giorni_migliori'] or 0):.0f}% della somma: " +
        ", ".join(f"{k} {100 * v:+.1f}" for k, v in out["giorni_migliori"].items()) + " (somme delle operazioni, in punti).",
        f"* **Tutto il mercato** (il Bitcoin giù almeno del 3% nella stessa ora): {br(out['mercato'])}. **La moneta da sola**: "
        f"{br(out['da_sola'])}.",
        f"* **C1, il crollo con le posizioni in salita**: {br(out['C1'])}. **C2, il crollo senza condizione sulle posizioni**: "
        f"{br(out['C2'])}. **Il caso** (ore a caso negli stessi giorni-moneta): {br(out['caso'])}.",
        "* Altre uscite: " + "; ".join(f"dopo {k} {br(v)}" for k, v in out["orizzonti"].items()) + ".",
        f"* Portafoglio (5% a operazione, al massimo 20 aperte), dal 6 dicembre 2021: Sharpe {i['sharpe']:.2f}, "
        f"{100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, discesa {100 * i['discesa_max']:.1f}%; Sharpe "
        f"corretto {p['sharpe_corretto']:.2f} ({p['gruppi']} gruppi), t {p['t']:.2f}.", "",
        f"**Esito delle operazioni: {out['esito']}** (soglia contando le {PROVE_A_EVENTI} prove a eventi: {out['soglia_tutte']:.5f}). "
        f"**Portafoglio: {p['esito']}**."]) + "\n"
    (QUI / "RISULTATI_CINQUANTESIMA.md").write_text(testo, encoding="utf-8")
    print(testo, flush=True)


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True), solo_conta="--conta" in sys.argv)
    print("CINQUANTESIMA FINITA", flush=True)
