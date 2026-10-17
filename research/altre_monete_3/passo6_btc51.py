"""Passo 6 del protocollo 3 (prova su altre monete) per V-020 della campagna BTC51, dal coordinamento.

    python3 research/altre_monete_3/passo6_btc51.py seleziona
        le 9 monete con il volume medio giornaliero in USDT piu' alto nel 2023, escluso BTCUSDT, dalla tabella del
        7 ottobre (``research/universo/candidate.csv``: 895 contratti perpetui in USDT dell'archivio di Binance,
        delistati compresi). Il volume delle prime 12 si ricalcola dalle candele giornaliere del 2023 scaricate con
        il CHECKSUM, per controllare la tabella. Solo dati del 2023.

    python3 research/altre_monete_3/passo6_btc51.py scarica
        candele last e mark a 1h e funding delle 9 monete dal 2023-12 al 2026-09, con il CHECKSUM.

    python3 research/altre_monete_3/passo6_btc51.py esegui
        V-020 senza modifiche su ogni moneta, una volta, sul solo periodo del vault, con lo slippage della fascia di
        volume 2023 della moneta; entrate casuali (1.000, seme 2026) e p-value; condizioni del punto 4; correlazioni
        dei rendimenti giornalieri (punto 5) ed esito del trasferimento (punto 6). Si rifiuta se l'esito esiste gia'.

SCELTE dichiarate (prima di eseguire):
1. La serie di ogni moneta si carica dal 2023-12-01: l'ATR(14) dello stop arriva calcolato al 2024-01-01 (744
   candele prima, l'effetto dell'inizio e' sotto 1e-20). Le decisioni si prendono solo alle chiusure delle candele
   dal 2024-01-01 00:00; nessun dato oltre il 2026-09-30.
2. Moneta delistata = l'ultima candela della serie e' prima del 2026-09-30 23:00. La posizione aperta all'ultima
   candela si chiude al suo prezzo di chiusura (motivo «fine_dati» del motore) e il test finisce li'.
3. Regole del motore come nel vault di BTC (``Regole()``: leva 2, rischio 1%, margine di mantenimento 0,004). Con
   la leva a 2 la liquidazione e' a circa il 40% dal prezzo: il margine di ogni moneta non cambia i trade (le
   violazioni di liquidazione si contano lo stesso).
4. Rendimento giornaliero del candidato su una moneta: la somma degli R dei trade che si chiudono in quel giorno
   UTC, zero nei giorni senza chiusure, dal 2024-01-01 all'ultimo giorno della moneta. La correlazione fra due
   monete si calcola sui giorni comuni. Le monete che reggono e hanno fra loro correlazione sopra 0,5 formano un
   gruppo (componenti connesse): ogni gruppo conta come una moneta.
6. Volume medio giornaliero nel 2023 = volume in USDT di tutto il 2023 diviso 365 (un giorno senza contratto conta
   zero). La media sui soli giorni presenti metterebbe fra le prime 9 contratti quotati a fine 2023 con 20-68 giorni
   di vita nell'anno; con la regola del 7 ottobre (almeno 350 giorni di dati nel 2023) le 9 sarebbero le stesse di
   questa scelta. Scelta fatta prima di scaricare qualunque dato del vault delle altre monete.
5. Commissioni come in BTC (taker 0,05%, maker 0,02%); funding vero della moneta.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
from pathlib import Path

RADICE_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RADICE_REPO))
sys.path.insert(0, str(RADICE_REPO / "research" / "vault"))

import numpy as np  # noqa: E402

import passo5_btc51 as p5  # noqa: E402
from research.src import dati  # noqa: E402
from research.src import selezione  # noqa: E402
from research.src import catalogo3 as cat  # noqa: E402
from research.src import motore3 as mot  # noqa: E402
from research.src import statistica3 as st  # noqa: E402

CARTELLA = Path(__file__).resolve().parent
TABELLA = RADICE_REPO / "research" / "universo" / "candidate.csv"
SELEZIONE = CARTELLA / "selezione.json"
ESITO = CARTELLA / "esito.json"
GIRO_INIZIATO = CARTELLA / "giro_iniziato.json"
N_MONETE = 9
INIZIO_SERIE = date(2023, 12, 1)
FASCE = ((1_000_000_000, 0.0001), (200_000_000, 0.0002), (50_000_000, 0.0005), (0, 0.0010))
SOGLIA_CORRELAZIONE = 0.5
MONETE_PER_TRASFERIRSI = 3


def _fascia(volume: float) -> float:
    return next(slippage for soglia, slippage in FASCE if volume >= soglia)


def _volume_2023(simbolo: str) -> dict:
    giorni = []
    for anno, mese in dati.mesi_del_periodo(date(2023, 1, 1), date(2023, 12, 31)):
        p = dati.scarica_mese(simbolo, "klines", "1d", anno, mese, verifica_checksum=True)
        if p is not None:
            giorni += selezione.volume_quote_giornaliero(dati.righe_csv_da_zip(p))
    media, n, _ = selezione.volume_medio_nella_finestra(giorni, date(2023, 1, 1), date(2023, 12, 31))
    return {"volume_medio_2023_usdt": media, "giorni_2023": n}


def _base() -> list:
    """I contratti perpetui in USDT della tabella con almeno un mese di dati nell'archivio nel 2023."""
    righe = [r for r in csv.DictReader(TABELLA.open(encoding="utf-8")) if selezione.e_perpetuo_usdt(r["simbolo"])]
    return [r for r in righe if r["simbolo"] != "BTCUSDT" and r["primo_mese_archivio"]
            and r["primo_mese_archivio"] <= "2023-12-31" and r["ultimo_mese_archivio"] >= "2023-01-01"]


def seleziona() -> dict:
    if SELEZIONE.exists():
        return json.loads(SELEZIONE.read_text(encoding="utf-8"))
    base = _base()
    volumi = {}
    da_calcolare = [r["simbolo"] for r in base if not r["volume_medio_2023_usdt"]]
    for r in base:
        if r["volume_medio_2023_usdt"]:
            volumi[r["simbolo"]] = {"volume_medio_2023_usdt": float(r["volume_medio_2023_usdt"]),
                                    "giorni_2023": int(r["giorni_2023"]), "fonte": "tabella"}
    with ThreadPoolExecutor(max_workers=8) as pool:
        for s, v in zip(da_calcolare, pool.map(_volume_2023, da_calcolare)):
            volumi[s] = {**v, "fonte": "calcolato"}
    con = [s for s in volumi if volumi[s]["volume_medio_2023_usdt"] is not None]
    for s in con:
        volumi[s]["volume_giornaliero_sull_anno"] = volumi[s]["volume_medio_2023_usdt"] * volumi[s]["giorni_2023"] / 365
    ordine = sorted(con, key=lambda s: (-volumi[s]["volume_giornaliero_sull_anno"], s))
    sui_giorni_presenti = sorted(con, key=lambda s: (-volumi[s]["volume_medio_2023_usdt"], s))
    controllo = {}
    for s in ordine[:N_MONETE + 3]:
        v = _volume_2023(s)
        controllo[s] = {"prima": volumi[s], **v,
                        "volume_giornaliero_sull_anno": v["volume_medio_2023_usdt"] * v["giorni_2023"] / 365}
    ordine12 = sorted(controllo, key=lambda s: (-controllo[s]["volume_giornaliero_sull_anno"], s))
    if ordine12 != ordine[:N_MONETE + 3]:
        raise SystemExit(f"il ricalcolo cambia l'ordine delle prime {N_MONETE + 3}: {ordine12}")
    monete = [{"simbolo": s, "volume_giornaliero_sull_anno": controllo[s]["volume_giornaliero_sull_anno"],
               "volume_medio_2023_usdt": controllo[s]["volume_medio_2023_usdt"], "giorni_2023": controllo[s]["giorni_2023"],
               "slippage_per_lato": _fascia(controllo[s]["volume_giornaliero_sull_anno"])} for s in ordine[:N_MONETE]]
    out = {"fonte": "contratti di research/universo/candidate.csv (indice dell'archivio del 7 ottobre 2026) con dati "
                    "nel 2023; volume dalla tabella o calcolato dalle candele 1d del 2023 con il CHECKSUM; prime 12 "
                    "ricalcolate",
           "contratti_con_dati_nel_2023": len(base), "con_volume": len(con), "calcolati_ora": len(da_calcolare),
           "monete": monete, "controllo_prime_12": controllo,
           "classifica_prime_30": [{"simbolo": s, **volumi[s]} for s in ordine[:30]],
           "scartata_media_sui_soli_giorni_presenti_prime_15": [{"simbolo": s, **volumi[s]}
                                                                 for s in sui_giorni_presenti[:15]]}
    SELEZIONE.write_text(json.dumps(p5._pulisci(out), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return out


def scarica() -> dict:
    dati.azzera_checksum_mancanti()
    fatti = {}
    for m in seleziona()["monete"]:
        s = m["simbolo"]
        for tipo, tf in (("klines", "1h"), ("markPriceKlines", "1h"), ("fundingRate", None)):
            p = dati.scarica_periodo(s, tipo, tf, INIZIO_SERIE, dati.FINE_VAULT, verifica_checksum=True)
            fatti[f"{s}/{tipo}"] = {"mesi": len(p), "primo": p[0].name if p else None, "ultimo": p[-1].name if p else None}
    fatti["checksum_mancanti"] = sorted(getattr(dati, "CHECKSUM_MANCANTI", []))
    return fatti


def _giorno(ms: int) -> int:
    return int(ms) // dati.MS_GIORNO


def _una_moneta(spec: dict, moneta: dict) -> dict:
    s, conteggi = dati.serie_3_con_conteggi(moneta["simbolo"], "1h", INIZIO_SERIE, dati.FINE_VAULT)
    ts = np.asarray(s.ts)
    a = int(np.searchsorted(ts, dati.ms_da_data(dati.INIZIO_VAULT)))
    b = len(ts) - 1
    costi = mot.Costi(slippage=moneta["slippage_per_lato"])
    c = cat.compila(spec, s)
    ris = mot.esegui(c, mot.Regole(), costi, a, b)
    m = mot.metriche(ris, s)
    p = None
    cas = None
    if m["trade"] > 0:
        cas = st.entrate_casuali(c, m["trade"], a, b, mot.Regole(), costi, st.N_SIMULAZIONI, st.SEME,
                                 larghezze_candidato=[st.larghezza_stop(t) for t in ris.trade])
        p = st.p_value(m["r_medio"], cas["valori"], st.N_SIMULAZIONI)
    esiti = st.regge_altra_moneta(m, p)
    ultima = int(ts[b])
    delistata = ultima < dati.ms_da_data(dati.FINE_VAULT) + 23 * dati.MS_ORA
    primo, ultimo = _giorno(ts[a]), _giorno(ultima)
    giornaliero = [0.0] * (ultimo - primo + 1)
    for t in ris.trade:
        giornaliero[_giorno(t.ts_uscita) - primo] += t.r
    return {"simbolo": moneta["simbolo"], "slippage_per_lato": moneta["slippage_per_lato"],
            "periodo_candele": [p5._ora(ts[a]), p5._ora(ultima)], "candele": b - a + 1, "delistata": delistata,
            "conteggi_serie": conteggi, "metriche": m, "p_value": p,
            "media_casuali": None if cas is None else float(np.mean(cas["valori"])),
            "casuali": None if cas is None else {k: v for k, v in cas.items() if k != "valori"},
            "esiti": esiti, "primo_giorno": primo, "rendimenti_giornalieri": giornaliero,
            "trade": [{"ingresso": p5._ora(t.ts_ingresso), "uscita": p5._ora(t.ts_uscita), "motivo": t.motivo,
                       "r": round(t.r, 4)} for t in ris.trade]}


def _correlazione(x: dict, y: dict):
    da = max(x["primo_giorno"], y["primo_giorno"])
    a = min(x["primo_giorno"] + len(x["rendimenti_giornalieri"]), y["primo_giorno"] + len(y["rendimenti_giornalieri"]))
    if a - da < 30:
        return None
    u = np.asarray(x["rendimenti_giornalieri"][da - x["primo_giorno"]:a - x["primo_giorno"]])
    v = np.asarray(y["rendimenti_giornalieri"][da - y["primo_giorno"]:a - y["primo_giorno"]])
    if u.std() == 0 or v.std() == 0:
        return None
    return float(np.corrcoef(u, v)[0, 1])


def _gruppi(nomi: list, corr: dict) -> list:
    padre = {n: n for n in nomi}

    def radice(n):
        while padre[n] != n:
            n = padre[n]
        return n
    for i, x in enumerate(nomi):
        for y in nomi[i + 1:]:
            r = corr.get(f"{x}|{y}")
            if r is not None and r > SOGLIA_CORRELAZIONE:
                padre[radice(y)] = radice(x)
    gruppi = {}
    for n in nomi:
        gruppi.setdefault(radice(n), []).append(n)
    return sorted(gruppi.values())


def esegui() -> dict:
    if ESITO.exists() or GIRO_INIZIATO.exists():
        raise SystemExit("la prova su altre monete di V-020 e' gia' stata eseguita: si esegue una volta sola")
    v = p5.verifica()
    if not v["tutto_uguale"]:
        raise SystemExit("impronte diverse dal Passo 3 o dal collaudo")
    spec = v["specifica"]
    sel = seleziona()
    GIRO_INIZIATO.write_text(json.dumps({"iniziato": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                         "monete": [m["simbolo"] for m in sel["monete"]]}, indent=1) + "\n",
                             encoding="utf-8")
    monete = [_una_moneta(spec, m) for m in sel["monete"]]
    nomi = [m["simbolo"] for m in monete]
    per_nome = {m["simbolo"]: m for m in monete}
    corr = {}
    for i, x in enumerate(nomi):
        for y in nomi[i + 1:]:
            corr[f"{x}|{y}"] = _correlazione(per_nome[x], per_nome[y])
    reggono = [m["simbolo"] for m in monete if m["esiti"]["regge"]]
    gruppi = _gruppi(reggono, corr)
    out = {"specifica": spec, "selezione": sel, "monete": monete, "correlazioni": corr, "reggono": reggono,
           "gruppi_indipendenti": gruppi, "monete_indipendenti_che_reggono": len(gruppi),
           "si_trasferisce": len(gruppi) >= MONETE_PER_TRASFERIRSI,
           "finito": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    ESITO.write_text(json.dumps(p5._pulisci(out), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"reggono": reggono, "gruppi": gruppi, "si_trasferisce": out["si_trasferisce"],
            "monete": [{"simbolo": m["simbolo"], "delistata": m["delistata"], "periodo": m["periodo_candele"],
                        "trade": m["metriche"]["trade"], "r_medio": m["metriche"]["r_medio"],
                        "profit_factor": m["metriche"]["profit_factor"], "p_value": m["p_value"],
                        "media_casuali": m["media_casuali"], "violazioni": m["metriche"]["violazioni_liquidazione"],
                        "regge": m["esiti"]["regge"]} for m in monete]}


if __name__ == "__main__":
    comando = {"seleziona": seleziona, "scarica": scarica, "esegui": esegui}[sys.argv[1]]
    print(json.dumps(p5._pulisci(comando()), indent=1, ensure_ascii=False))
