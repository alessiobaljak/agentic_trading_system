"""Programma 7, diciassettesima prova (DICIASSETTESIMA.md): G15, short (contro il Bitcoin) dei perpetui dal 30° giorno prima di
uno sblocco a gradino di squadra o investitori (almeno l'1% dell'offerta in circolazione) fino al giorno dopo, uscita a +30%.

Uso: python3 -m research.programma7.diciassettesima
"""
from __future__ import annotations

import gzip
import hashlib
import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from research.programma6 import annunci as an
from research.programma6 import asticella as ast
from research.programma6 import quarantunesima as qu
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import trentesima as tr
from research.programma6 import ventunesima as vu

QUI = Path(__file__).parent
RIS = QUI / "risultati_diciassettesima"
DATI = QUI.parents[1] / "research" / "data" / "sblocchi"
FILE = DATI / "sblocchi.json.gz"
ELENCO = "https://defillama-datasets.llama.fi/emissionsProtocolsList"
PROTOCOLLO = "https://defillama-datasets.llama.fi/emissions/{}"
PREZZI = "https://coins.llama.fi/prices/{}"
CATEGORIE = ("insiders", "privateSale")
MINIMO, PRIMA, ETA_MIN, VOLUME_MIN, TOLLERANZA = 0.01, 30, 30, 2e6, 0.20
PROVE_A_EVENTI = 17


def _get(url: str, prove: int = 4):
    for k in range(prove):
        try:
            r = requests.get(url, timeout=40)
            r.raise_for_status()
            return r.json()
        except Exception:  # noqa: BLE001
            if k == prove - 1:
                raise
            time.sleep(2 ** k)


def compatta(nome: str, d: dict) -> dict:
    """Del calendario di un protocollo tiene: il token, gli sblocchi a gradino (giorno, categoria, quantita') e l'offerta in
    circolazione giorno per giorno (le sezioni gia' sbloccate, tolte quelle `noncirculating`)."""
    m = d.get("metadata") or {}
    fuori = set((d.get("categories") or {}).get("noncirculating", []))
    serie: dict = {}
    for s in (d.get("documentedData") or {}).get("data", []):
        if s.get("label") in fuori:
            continue
        for x in s.get("data", []):
            g = int(x["timestamp"]) // 86_400
            serie[g] = serie.get(g, 0.0) + float(x.get("unlocked") or 0.0)
    gradini = []
    for e in m.get("unlockEvents") or []:
        for a in e.get("cliffAllocations") or []:
            if a.get("unlockType") == "cliff":
                gradini.append([int(e["timestamp"]) // 86_400, a.get("category"), float(a.get("amount") or 0.0), a.get("recipient")])
    return {"protocollo": nome, "nome": d.get("name"), "token": m.get("token"), "gradini": gradini,
            "circolante": sorted(serie.items())}


def scarica(log=print) -> list:
    if FILE.exists():
        return json.loads(gzip.decompress(FILE.read_bytes()))
    elenco = _get(ELENCO)
    log(f"[diciassettesima] {len(elenco)} protocolli nei calendari di DefiLlama")

    def uno(p):
        try:
            return compatta(p, _get(PROTOCOLLO.format(p)))
        except Exception as exc:  # noqa: BLE001
            return {"protocollo": p, "errore": str(exc)[:200]}

    with ThreadPoolExecutor(max_workers=6) as ex:
        out = list(ex.map(uno, elenco))
    simboli = sorted({x["token"] for x in out if x.get("token")})
    sig = {}
    for k in range(0, len(simboli), 60):
        r = _get(PREZZI.format("current/" + ",".join(simboli[k:k + 60])))
        sig.update({t: v.get("symbol") for t, v in (r.get("coins") or {}).items()})
    for x in out:
        x["sigla"] = sig.get(x.get("token"))
    DATI.mkdir(parents=True, exist_ok=True)
    FILE.write_bytes(gzip.compress(json.dumps(out).encode(), mtime=0))
    return out


def prefisso(simbolo: str, sigla: str) -> float:
    """Il multiplo del perpetuo (1000PEPEUSDT vale 1000 PEPE)."""
    return {"": 1.0, "1000": 1e3, "1000000": 1e6, "1M": 1e6}.get(simbolo[: len(simbolo) - len(sigla) - 4], float("nan"))


def eventi_del_protocollo(x: dict) -> list:
    """Gli sblocchi di squadra e investitori dello stesso giorno sommati, con la dimensione sull'offerta del giorno prima."""
    circ = dict((int(g), float(v)) for g, v in x["circolante"])
    per_giorno: dict = {}
    for g, cat, q, _ in x["gradini"]:
        if cat in CATEGORIE and q > 0:
            v = per_giorno.setdefault(g, {"quantita": 0.0, "categorie": set()})
            v["quantita"] += q
            v["categorie"].add(cat)
    out = []
    for g in sorted(per_giorno):
        prima = circ.get(g - 1, 0.0)
        if prima > 0:
            out.append({"giorno": g, "dimensione": per_giorno[g]["quantita"] / prima,
                        "categorie": "+".join(sorted(per_giorno[g]["categorie"]))})
    return out


def operazione(pan: dict, j: int, jb: int, e: int, u: int, protezione: bool = True) -> dict:
    """Short la moneta ``j`` e long il Bitcoin dall'apertura del giorno ``e`` all'apertura del giorno ``u`` (indici del pannello),
    o prima all'uscita a +30% con le candele giornaliere."""
    O, H, C, F = pan["open"], pan["high"], pan["close"], pan["funding"]
    p0, b0 = O[e, j], O[e, jb]
    livello = p0 * (1 + tr.STOP)
    uscita, pc, pb, fermata, fino = u, O[u, j], O[u, jb], False, u - 1
    if protezione:
        for d in range(e, u):
            if d > e and O[d, j] >= livello:
                uscita, pc, pb, fermata, fino = d, O[d, j] * (1 + tr.SCARTO_STOP), O[d, jb], True, d - 1
                break
            if H[d, j] >= livello:
                uscita, pc, pb, fermata, fino = d, livello * (1 + tr.SCARTO_STOP), C[d, jb], True, d
                break
    fc, fb = np.nansum(F[e:fino + 1, j]), np.nansum(F[e:fino + 1, jb])
    r = (pb / b0 - 1) - (pc / p0 - 1) - vu.COSTO_MONETA - vu.COSTO_BTC + fc - fb
    return {"r": float(r), "fermata": fermata, "giorni": int(uscita - e), "funding": float(fc)}


def ammessa(pan: dict, j: int, e: int, u: int) -> str:
    """'' se la moneta si puo' operare dal giorno ``e`` al giorno ``u``, altrimenti il motivo."""
    C, V = pan["close"], pan["quote_volume"]
    if e - ETA_MIN < 0 or u >= C.shape[0]:
        return "fuori dal pannello"
    vive = np.flatnonzero(np.isfinite(C[:, j]))
    if not len(vive) or vive[0] > e - ETA_MIN:
        return "perpetuo con meno di 30 giorni"
    if not np.nan_to_num(V[e - 1, j]) >= VOLUME_MIN:
        return "volume sotto 2 milioni"
    tratto = V[e:u, j]
    if not np.isfinite(pan["open"][u, j]) or not np.all(np.isfinite(C[e:u, j])) or np.any(np.nan_to_num(tratto) <= 0):
        return "contratto chiuso o fermo prima dell'uscita"
    return ""


def esegui(log=print) -> dict:
    dati = scarica(log)
    impronta = hashlib.sha256(FILE.read_bytes()).hexdigest()[:16]
    pan = sc.pannello()
    t0, simboli = pan["t0"], pan["simboli"]
    jb = simboli.index("BTCUSDT")
    conti = {"protocolli": len(dati), "con_errore": sum(1 for x in dati if "errore" in x), "senza_sigla": 0, "senza_perpetuo": 0,
             "prezzo_diverso": 0, "senza_eventi_usabili": 0, "token_usati": 0}
    scarti: dict = {}
    righe, controlli = [], []
    for x in dati:
        if "errore" in x:
            continue
        if not x.get("sigla"):
            conti["senza_sigla"] += 1
            continue
        s = an.perpetuo(x["sigla"].upper(), simboli)
        if not s or s == "BTCUSDT":
            conti["senza_perpetuo"] += 1
            continue
        j = simboli.index(s)
        candidati, fine_prec = [], -10**9
        for ev in eventi_del_protocollo(x):
            if ev["dimensione"] < MINIMO:
                continue
            e, u = ev["giorno"] - PRIMA - t0, ev["giorno"] + 1 - t0
            motivo = ammessa(pan, j, e, u)
            if not motivo and e < fine_prec:
                motivo = "sovrapposto al precedente"
            if motivo:
                scarti[motivo] = scarti.get(motivo, 0) + 1
                continue
            candidati.append((ev, e, u))
            fine_prec = u
        if not candidati:
            conti["senza_eventi_usabili"] += 1
            continue
        g_c = candidati[0][1] + t0
        try:
            r = _get(PREZZI.format(f"historical/{g_c * 86_400 + 3_600}/{x['token']}"))
            pz = float(next(iter((r.get("coins") or {}).values()))["price"])
        except Exception:  # noqa: BLE001
            pz = float("nan")
        rapporto = pan["open"][candidati[0][1], j] / prefisso(s, x["sigla"].upper()) / pz if pz > 0 else float("nan")
        controlli.append({"protocollo": x["protocollo"], "sigla": x["sigla"], "perpetuo": s, "giorno": sc.data(g_c),
                          "prezzo_defillama": pz, "rapporto": rapporto})
        if not (abs(rapporto - 1) <= TOLLERANZA):
            conti["prezzo_diverso"] += 1
            continue
        conti["token_usati"] += 1
        for ev, e, u in candidati:
            con, senza = operazione(pan, j, jb, e, u, True), operazione(pan, j, jb, e, u, False)
            prima = operazione(pan, j, jb, e, u - 1, False)
            righe.append({"data": sc.data(e + t0), "annuncio": int((e + t0 + 3) // 7), "simbolo": s, "protocollo": x["protocollo"],
                          "sblocco": sc.data(ev["giorno"]), "dimensione": ev["dimensione"], "categorie": ev["categorie"],
                          "r": con["r"], "fermata": con["fermata"], "giorni": con["giorni"], "funding": con["funding"],
                          "r_senza": senza["r"], "r_prima": prima["r"], "r_giorno": senza["r"] - prima["r"]})
    df = pd.DataFrame(righe).sort_values(["data", "simbolo"]).reset_index(drop=True)
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "eventi_G15.csv", index=False)
    pd.DataFrame(controlli).to_csv(RIS / "controllo_sigle.csv", index=False)
    ex = tr.esame(df, "r")
    out = {"eventi": ex, "senza_uscita": tr.esame(df, "r_senza"), "conti": conti, "scarti": scarti,
           "fermate": float(df["fermata"].mean()), "funding_medio": float(df["funding"].mean()),
           "prima_dello_sblocco": float(df["r_prima"].mean()), "giorno_dello_sblocco": float(df["r_giorno"].mean()),
           "soglia_tutte": 0.01 / PROVE_A_EVENTI, "impronta_dati": impronta}
    out["per_categoria"] = {c: {"eventi": int(len(g)), "media": float(g["r"].mean())} for c, g in df.groupby("categorie")}
    fasce = pd.cut(df["dimensione"], [0.01, 0.03, 0.10, np.inf], right=False, labels=["1-3%", "3-10%", "oltre 10%"])
    out["per_dimensione"] = {str(c): {"eventi": int(len(g)), "media": float(g["r"].mean())} for c, g in df.groupby(fasce, observed=True)}
    ev = pd.DataFrame({"simbolo": df["simbolo"], "ora": [sc.giorno(*map(int, d.split("-"))) * 24 for d in df["data"]],
                       "r": df["r"]})
    ev["uscita_h"] = ev["ora"] + df["giorni"].to_numpy() * 24
    port = qu.portafoglio(ev)
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    p = te.esame(port, btc, inizio=qu.PRIMO_LUNEDI, anni_pieni=se.ANNI_PIENI)
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), "74 G15": port["netto"]}, {"74 G15": p["intero"]})
    rr = rivisto["candidate"]["74 G15"]
    p["sharpe_corretto"], p["t"], p["gruppi"] = rr["corretto_con_aggiunta"], rr["t"], rivisto["gruppi"]
    p["esito"] = te.esito(p, p["sharpe_corretto"])
    out["portafoglio"] = p
    passa = ex["esito"] == "VALIDA"
    out["esito"] = ("VALIDA" if passa and ex["boot"]["p"] <= out["soglia_tutte"] else
                    "passa l'esame scritto (p ≤ 0,01) ma non la soglia di tutte le prove a eventi" if passa else ex["esito"])
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    b, i = ex["boot"], p["intero"]
    righe_t = [
        "# Programma 7 — risultati della diciassettesima prova (G15: vendere prima degli sblocchi dei token)", "",
        "Regole in `DICIASSETTESIMA.md` (scritte prima).", "",
        f"* Dati: {conti['protocolli']} protocolli nei calendari di DefiLlama (impronta {impronta}); con errore {conti['con_errore']}, "
        f"senza sigla {conti['senza_sigla']}, senza perpetuo su Binance {conti['senza_perpetuo']}, senza eventi usabili "
        f"{conti['senza_eventi_usabili']}, prezzo diverso da quello del perpetuo {conti['prezzo_diverso']}; token usati "
        f"{conti['token_usati']}.",
        "* Eventi non usati: " + ", ".join(f"{k} {v}" for k, v in sorted(scarti.items())) + ".",
        f"* **{b['eventi']} eventi in {b['annunci']} settimane: {100 * b['media']:+.2f}% a evento** (intervallo {100 * b['basso']:+.2f}%; "
        f"{100 * b['alto']:+.2f}%, p {b['p']:.4f}); mediana {100 * ex['mediana']:+.2f}%, vinti {100 * ex['vinti']:.0f}%; metà "
        f"{100 * ex['prima_meta']:+.2f}% e {100 * ex['seconda_meta']:+.2f}%; senza i 5 migliori {100 * ex['senza_5_migliori']:+.2f}%.",
        "* Per anno: " + ", ".join(f"{a} {100 * v['media']:+.2f}% ({v['eventi']})" for a, v in ex["per_anno"].items()) + ".",
        f"* L'uscita a +30% scatta nel {100 * out['fermate']:.0f}% degli eventi; senza l'uscita {100 * out['senza_uscita']['boot']['media']:+.2f}% "
        f"(p {out['senza_uscita']['boot']['p']:.4f}). Funding incassato dallo short in media {100 * out['funding_medio']:+.2f}% a evento.",
        f"* Senza l'uscita, il tratto prima dello sblocco (30 giorni) {100 * out['prima_dello_sblocco']:+.2f}% e il giorno dello sblocco "
        f"{100 * out['giorno_dello_sblocco']:+.2f}% (contro il Bitcoin, costi nel primo).",
        "* Per categoria: " + ", ".join(f"{c} {100 * v['media']:+.2f}% ({v['eventi']})" for c, v in out["per_categoria"].items()) + ".",
        "* Per dimensione: " + ", ".join(f"{c} {100 * v['media']:+.2f}% ({v['eventi']})" for c, v in out["per_dimensione"].items()) + ".",
        f"* Portafoglio (5% a operazione, al massimo 20): Sharpe {i['sharpe']:.2f}, {100 * i['annuo']:+.1f}% l'anno, volatilità "
        f"{100 * i['volatilita']:.1f}%, discesa {100 * i['discesa_max']:.1f}%; Sharpe corretto {p['sharpe_corretto']:.2f} "
        f"({p['gruppi']} gruppi), t {p['t']:.2f}.", "",
        f"**Esito degli eventi: {out['esito']}** (soglia contando le {PROVE_A_EVENTI} prove a eventi: {out['soglia_tutte']:.5f}). "
        f"**Portafoglio: {p['esito']}**."]
    testo = "\n".join(righe_t) + "\n"
    (QUI / "RISULTATI_DICIASSETTESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("DICIASSETTESIMA FINITA", flush=True)
