"""I TAKE PROFIT DELLE POSIZIONI APERTE SONO RAGGIUNGIBILI? (2 ott 2026, domanda del
proprietario: «guarda i trade aperti oggi … quale sarebbe la crescita percentuale
di quella crypto per raggiungere quel gradino, è davvero realizzabile?»).

Per ogni posizione aperta (RTDB `/positions`, gia' con la sua scala `tp_ladder`):
  * la distanza in % di stop e di ogni TP dall'ingresso;
  * sulla STORIA della moneta (ultimi GIORNI giorni, candele del timeframe della
    strategia, dalla cache del gate letta in SOLA LETTURA: nessun download,
    nessuna scrittura, cosi' si puo' lanciare anche col gate in corso), da OGNI
    candela come ingresso: quante volte il prezzo ha toccato quel TP entro
    l'orizzonte del trade (96 candele, come l'uscita a tempo del bot) PRIMA dello
    stop (stessa distanza in % dello stop vero; stop prima del TP se cadono nella
    stessa candela, come nel bot), e quante volte lo ha toccato comunque.
E' un ingresso CASUALE, non il segnale della strategia: dice quanto e' «lontano»
quel TP per quella moneta in quel tempo. Il paper finora non si distingue da un
prezzo casuale con le stesse uscite (backlog K4), quindi e' un metro onesto; se la
strategia avesse un vantaggio vero, la sua percentuale sarebbe piu' alta.
Tutto puro tranne `carica_cache` e `main`.
"""
from __future__ import annotations

import json
import os
import statistics
import time
from datetime import datetime, timezone

#: i giorni di storia su cui si misura
GIORNI = 90
#: l'orizzonte del trade in candele (uscita a tempo del bot: 96 barre)
ORIZZONTE = 96
_BARRE_GIORNO = {"15m": 96, "1h": 24, "4h": 6}


def livelli(pos: dict) -> dict | None:
    """Ingresso, verso, stop in % e i TP in % (con il loro R) di una posizione
    RTDB. Lo stop si ricava dalla scala: R = |TP1 - ingresso| / r1 (lo stop
    iniziale, quello che fissa i gradini). None se la posizione non ha una scala."""
    try:
        entry = float(pos.get("entry_price"))
        lado = str(pos.get("direction") or "").lower()
        scala = [x for x in (pos.get("tp_ladder") or []) if isinstance(x, dict)]
        if isinstance(pos.get("tp_ladder"), dict):
            scala = [pos["tp_ladder"][k] for k in sorted(pos["tp_ladder"], key=lambda k: int(k))]
        scala = [x for x in scala if x.get("price") is not None and x.get("r")]
        if entry <= 0 or lado not in ("long", "short") or not scala:
            return None
        r_prezzo = abs(float(scala[0]["price"]) - entry) / float(scala[0]["r"])
        tps = [{"r": float(x["r"]), "pct": abs(float(x["price"]) - entry) / entry,
                "preso": bool(x.get("hit"))} for x in scala]
        return {"symbol": pos.get("symbol"), "strategy": pos.get("strategy"), "lato": lado,
                "entry": entry, "stop_pct": r_prezzo / entry, "tps": tps,
                "timeframe": pos.get("timeframe") or "15m"}
    except (TypeError, ValueError, ZeroDivisionError):
        return None


def raggiungibilita(candele: list, lato: str, stop_pct: float, tp_pcts: list[float],
                    orizzonte: int = ORIZZONTE) -> dict:
    """Da ogni candela come ingresso (alla chiusura), sulle `orizzonte` successive:
    per ogni TP la quota di ingressi in cui il TP arriva PRIMA dello stop
    (`prima_dello_stop`) e quella in cui arriva comunque entro l'orizzonte
    (`comunque`). `candele`: liste/tuple (high, low, close) o oggetti con
    .high/.low/.close. Pura."""
    hl = [((c.high, c.low, c.close) if hasattr(c, "high") else (c[0], c[1], c[2]))
          for c in candele]
    n_ing = len(hl) - orizzonte
    if n_ing <= 0:
        return {"n": 0, "prima_dello_stop": [None] * len(tp_pcts),
                "comunque": [None] * len(tp_pcts), "mossa_max_mediana": None}
    prima = [0] * len(tp_pcts)
    comunque = [0] * len(tp_pcts)
    mosse = []
    for i in range(n_ing):
        e = hl[i][2]
        if e <= 0:
            continue
        if lato == "long":
            stop = e * (1 - stop_pct)
            tp = [e * (1 + d) for d in tp_pcts]
        else:
            stop = e * (1 + stop_pct)
            tp = [e * (1 - d) for d in tp_pcts]
        fermato = False
        presi_prima = [False] * len(tp_pcts)
        presi = [False] * len(tp_pcts)
        migliore = 0.0
        for h, l, _c in hl[i + 1:i + 1 + orizzonte]:
            fav = (h - e) / e if lato == "long" else (e - l) / e
            migliore = max(migliore, fav)
            toccato_stop = (l <= stop) if lato == "long" else (h >= stop)
            for k, p in enumerate(tp):
                arriva = (h >= p) if lato == "long" else (l <= p)
                if arriva:
                    presi[k] = True
                    # stop e TP nella stessa candela: prima lo stop (come il bot)
                    if not fermato and not toccato_stop:
                        presi_prima[k] = True
            if toccato_stop:
                fermato = True
        mosse.append(migliore)
        for k in range(len(tp_pcts)):
            prima[k] += presi_prima[k]
            comunque[k] += presi[k]
    n = len(mosse)
    return {"n": n, "prima_dello_stop": [x / n for x in prima],
            "comunque": [x / n for x in comunque],
            "mossa_max_mediana": statistics.median(mosse) if mosse else None}


def carica_cache(symbol: str, timeframe: str, giorni: int = GIORNI):
    """Le ultime `giorni` di candele dalla cache del gate, in SOLA LETTURA (il
    file piu' recente della serie, qualunque sia l'inizio). None se non c'e'."""
    from backtesting import data_loader as dl
    try:
        nomi = [n for n in os.listdir(dl._CACHE_DIR)
                if n.startswith(f"{symbol}_{timeframe}_") and n.endswith(".json")]
    except OSError:
        return None
    if not nomi:
        return None
    # prima i file che COPRONO i giorni chiesti, poi la fine piu' recente (2 ott
    # 2026): la sezione A5 di mfe_report scrive nella stessa cartella file corti
    # (da 3 giorni prima del primo ingresso a domani) con la fine piu' recente;
    # ops 0419: HEMIUSDT letto su 601 ingressi invece di 8640
    da = datetime.fromtimestamp(time.time() - giorni * 86400,
                                tz=timezone.utc).strftime("%Y-%m-%d")

    def _chiave(n: str) -> tuple:
        inizio, fine = n[:-len(".json")].rsplit("_", 2)[-2:]
        return (inizio <= da, fine)
    nomi.sort(key=_chiave, reverse=True)
    candele = dl._cache_read(os.path.join(dl._CACHE_DIR, nomi[0]))
    if not candele:
        return None
    per_giorno = _BARRE_GIORNO.get(timeframe, 96)
    return candele[-(giorni * per_giorno + ORIZZONTE):]


def quote_paper(trades: list[dict]) -> list[float | None]:
    """Nel paper (tutti i trade chiusi con la scala registrata): la quota che ha
    preso almeno 1, 2, 3 gradini (`scale_stage_reached`)."""
    con = [int(t.get("scale_stage_reached") or 0) for t in trades
           if t.get("scale_stage_reached") is not None]
    if not con:
        return [None, None, None]
    return [sum(1 for s in con if s >= k) / len(con) for k in (1, 2, 3)]


def _p(x) -> str:
    return "  —  " if x is None else f"{x * 100:4.0f}%"


def stampa(posizioni: dict | None, trades: list[dict] | None = None, carica=carica_cache) -> None:
    print("\n" + "=" * 78)
    print("I TAKE PROFIT DELLE POSIZIONI APERTE SONO RAGGIUNGIBILI? (2 ott 2026)")
    print("=" * 78)
    print(f"Per ogni posizione: distanza in % di stop e TP; poi, sulla storia della moneta "
          f"(ultimi {GIORNI} giorni, cache del gate in sola lettura), da OGNI candela come "
          f"ingresso casuale: quante volte quel TP e' arrivato entro {ORIZZONTE} candele PRIMA "
          f"dello stop (stessa distanza dello stop vero), e quante volte comunque.")
    pos = [v for v in (posizioni or {}).values() if isinstance(v, dict)]
    if not pos:
        print("  nessuna posizione aperta")
        return
    for p in sorted(pos, key=lambda x: str(x.get("symbol"))):
        lv = livelli(p)
        if lv is None:
            print(f"  {p.get('symbol')}: scala dei TP non leggibile, saltata")
            continue
        tp_txt = " · ".join(f"TP{k + 1} {t['r']:g}R = {t['pct'] * 100:.1f}%"
                            + (" (preso)" if t["preso"] else "") for k, t in enumerate(lv["tps"]))
        print(f"\n  {lv['symbol']} {lv['lato'].upper()} ({lv['strategy']}, {lv['timeframe']}): "
              f"stop {lv['stop_pct'] * 100:.1f}% · {tp_txt}")
        candele = carica(lv["symbol"], lv["timeframe"])
        if not candele:
            print("    storia non in cache: niente misura")
            continue
        r = raggiungibilita(candele, lv["lato"], lv["stop_pct"], [t["pct"] for t in lv["tps"]])
        if not r["n"]:
            print("    storia troppo corta")
            continue
        print(f"    su {r['n']} ingressi casuali: massimo a favore mediano in {ORIZZONTE} candele "
              f"{r['mossa_max_mediana'] * 100:.1f}%")
        print("    TP prima dello stop: " + " · ".join(
            f"TP{k + 1} {_p(x)}" for k, x in enumerate(r["prima_dello_stop"])))
        print("    TP comunque entro l'orizzonte: " + " · ".join(
            f"TP{k + 1} {_p(x)}" for k, x in enumerate(r["comunque"])))
    if trades is not None:
        q = quote_paper(trades)
        print(f"\n  Nel paper (trade chiusi): almeno 1 gradino {_p(q[0])} · almeno 2 {_p(q[1])} "
              f"· tutti e 3 {_p(q[2])}")
    print("  Lettura: ingresso casuale, non il segnale; se la strategia ha un vantaggio vero le "
          "sue quote sono piu' alte. Misura, nessuna regola cambia (le uscite non si toccano "
          "prima delle letture del 7-14 ott).")


def main() -> int:
    from bot.core.firebase_client import get_firebase
    fb = get_firebase()
    stampa(fb.get_rtdb("/positions"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
