"""Strumento di lavoro del Passo 2 della campagna BTC51 (PROTOCOLLO_3.md, sezioni 8, 10 e 13).

Uso (un file JSON con una lista di voci, in research/campagne/BTC51/codice/):

    python3 research/campagne/BTC51/codice/lotto.py prova <file.json>
        prova del codice su una serie FINTA (passeggiata casuale, nessun prezzo vero): compila ogni
        specifica, stima, Fase 2 con 50 simulazioni; stampa solo «ok» o l'errore e il tempo.

    python3 research/campagne/BTC51/codice/lotto.py stima <file.json>
        stima dei trade (8.4) sul periodo di costruzione: solo conteggi, nessun risultato. Ogni stima
        entra nel log; una voce con ``id`` che resta sotto 150 trade e' uno ``scarto``, le altre ``nota``.

    python3 research/campagne/BTC51/codice/lotto.py fase2 <file.json>
        per ogni voce, in serie: registrazione nel log (con la previsione scritta nel file), Fase 2
        completa sulla costruzione, risultato nel log e dettaglio in risultati/<id>.json.

    python3 research/campagne/BTC51/codice/lotto.py fase4 <file.json>
        per ogni voce gia' superata in Fase 2: registrazione della verifica, le undici verifiche della
        Fase 4, risultato nel log e dettaglio in risultati/<id>_fase4.json.

Voce: {"id": "V-001", "ipotesi": "I-01", "fonte": "...", "specifica": {variante}, "previsione": "...",
       "motivo": "..."} (per ``stima`` bastano ``specifica`` e un'etichetta ``nome`` o ``id``).
Avanzamento in data/insample/BTCUSDT/lotto_avanzamento.txt.
"""

from __future__ import annotations

import json
import math
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

RADICE_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RADICE_REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402

from research.src import dati  # noqa: E402
from research.src import catalogo3 as cat  # noqa: E402
from research.src import motore3 as mot  # noqa: E402
from research.src import statistica3 as st  # noqa: E402
import registro  # noqa: E402

CARTELLA = Path(__file__).resolve().parent.parent
RISULTATI = CARTELLA / "risultati"
AVANZAMENTO = dati.RADICE_DEFAULT / "data" / "insample" / "BTCUSDT" / "lotto_avanzamento.txt"
INIZIO = date(2020, 1, 1)
FINE_COSTR = date(2022, 9, 30)
MINIMO_TRADE = 150

_SERIE: dict = {}


def avanza(testo: str) -> None:
    AVANZAMENTO.parent.mkdir(parents=True, exist_ok=True)
    with open(AVANZAMENTO, "a", encoding="utf-8") as f:
        f.write(f"{registro.adesso()} {testo}\n")


def serie_costruzione(tf: str):
    """(serie, inizio, fine) del periodo di costruzione per il timeframe."""
    if tf not in _SERIE:
        s = dati.serie_3("BTCUSDT", tf, INIZIO, FINE_COSTR)
        ts = np.asarray(s.ts)
        a = int(np.searchsorted(ts, dati.ms_da_data(INIZIO)))
        b = int(np.searchsorted(ts, dati.ms_da_data(date(2022, 10, 1)))) - 1
        _SERIE[tf] = (s, a, b)
    return _SERIE[tf]


def serie_finta(tf: str, n: int = 6000):
    """Passeggiata casuale con la griglia di tempo vera: solo per provare il codice."""
    vera, _, _ = serie_costruzione(tf)
    rng = np.random.default_rng(1)
    n = min(n, len(vera.ts))
    r = rng.normal(0, 0.006, n)
    close = 10000 * np.exp(np.cumsum(r))
    open_ = np.concatenate([[10000], close[:-1]])
    high = np.maximum(open_, close) * (1 + np.abs(rng.normal(0, 0.003, n)))
    low = np.minimum(open_, close) * (1 - np.abs(rng.normal(0, 0.003, n)))
    vol = np.abs(rng.normal(100, 30, n))
    ts = list(vera.ts[:n])
    fts = [t for t in vera.funding_ts if t <= ts[-1]]
    ftass = list(rng.normal(0.0001, 0.0002, len(fts)))
    s = cat.Serie(timeframe=tf, ts=ts, open=list(open_), high=list(high), low=list(low), close=list(close),
                  volume=list(vol), mark_open=list(open_), mark_high=list(high), mark_low=list(low),
                  mark_close=list(close), funding_ts=fts, funding_tasso=ftass)
    return s, 0, n - 1


def leggi_voci(nome: str) -> list:
    p = Path(nome)
    if not p.is_absolute():
        p = RADICE_REPO / p
    return json.loads(p.read_text(encoding="utf-8"))


def etichetta(v: dict) -> str:
    return v.get("id") or v.get("nome") or "?"


def cmd_prova(voci: list) -> None:
    t0 = time.time()
    for v in voci:
        spec = cat.normalizza(v["specifica"])
        s, a, b = serie_finta(spec["timeframe"])
        c = cat.compila(spec, s)
        mot.stima_trade(c, mot.Regole(), a, b)
        out = st.fase2(spec, s, a, b, n_simulazioni=50, compilata=c)
        assert "supera" in out
    print(f"ok ({len(voci)} specifiche, {time.time() - t0:.1f} s)")


def cmd_stima(voci: list) -> None:
    righe = []
    for v in voci:
        spec = cat.normalizza(v["specifica"])
        s, a, b = serie_costruzione(spec["timeframe"])
        c = cat.compila(spec, s)
        conto = mot.stima_trade(c, mot.Regole(), a, b)
        sotto = conto["trade"] < MINIMO_TRADE
        voce = {"tipo": "scarto" if (sotto and "id" in v) else "nota", "stima_trade": conto,
                "specifica": spec, "periodo": "costruzione"}
        if "id" in v:
            voce["id"] = v["id"]
            voce["motivo"] = ("stima dei trade sotto 150 (8.4): scarto, non consuma tentativi" if sotto
                              else "stima dei trade (8.4)")
        else:
            voce["testo"] = f"stima dei trade (8.4) per l'etichetta {etichetta(v)}: solo conteggi"
        registro.aggiungi(voce)
        righe.append(f"{etichetta(v)}: {conto['trade']} trade"
                     + (f" (ordini {conto['ordini_eseguiti']}/{conto['ordini_inseriti']})" if conto["ordini_inseriti"] else ""))
    print("\n".join(righe))


def _pulisci(x):
    if isinstance(x, dict):
        return {str(k): _pulisci(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_pulisci(v) for v in x]
    if isinstance(x, (np.floating, float)):
        f = float(x)
        return None if math.isnan(f) else (f if math.isfinite(f) else str(f))
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.bool_,)):
        return bool(x)
    return x


def _arrot(m: dict) -> dict:
    out = {}
    for k, v in m.items():
        if isinstance(v, float) and math.isfinite(v):
            out[k] = round(v, 3)
        else:
            out[k] = v
    return out


def cmd_fase2(voci: list) -> None:
    RISULTATI.mkdir(exist_ok=True)
    gia = {x.get("id") for x in registro.voci() if x.get("tipo") == "registrazione"}
    usate = sum(1 for x in registro.voci() if x.get("tipo") == "registrazione" and x.get("tipo_test") == "variante")
    for v in voci:
        if v["id"] in gia:
            raise SystemExit(f"{v['id']} e' gia' registrata: non si ripete un test")
        spec = cat.normalizza(v["specifica"])
        s, a, b = serie_costruzione(spec["timeframe"])
        c = cat.compila(spec, s)
        conto = mot.stima_trade(c, mot.Regole(), a, b)
        if conto["trade"] < MINIMO_TRADE:
            raise SystemExit(f"{v['id']}: stima {conto['trade']} sotto 150, non si registra (8.4)")
        usate += 1
        if usate > 40:
            raise SystemExit("limite di 40 varianti raggiunto (8.3)")
        registro.aggiungi({"id": v["id"], "tipo": "registrazione", "tipo_test": "variante", "ipotesi": v["ipotesi"],
                           "fonte": v["fonte"], "specifica": spec, "periodo": "costruzione",
                           "trade_stimati": conto["trade"], "variante_n": usate, "previsione": v["previsione"],
                           "criterio_successo": "sezione 10.3, costruzione"})
        avanza(f"{v['id']} registrata, Fase 2 in corso")
        t0 = time.time()
        out = st.fase2(spec, s, a, b, compilata=c)
        m = out["metriche"]
        sintesi = {k: m.get(k) for k in ("trade", "trade_al_mese", "r_medio", "profit_factor", "vincenti",
                                         "r_medio_vincenti", "r_medio_perdenti", "drawdown_max_r",
                                         "tempo_in_posizione", "ridotti", "violazioni_liquidazione",
                                         "esecuzione")}
        sintesi["p_value"] = out["p_value"]
        sintesi["r_medio_casuali"] = None if out["casuali"] is None else out["casuali"]["media"]
        dettaglio = {"id": v["id"], "specifica": spec, "metriche": m, "p_value": out["p_value"],
                     "casuali": out["casuali"], "esiti": out["esiti"], "buy_and_hold": out["buy_and_hold"],
                     "secondi": round(time.time() - t0, 1),
                     "trade": [{"ingresso": datetime.fromtimestamp(t.ts_ingresso / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M"),
                                "uscita": datetime.fromtimestamp(t.ts_uscita / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M"),
                                "motivo": t.motivo, "r": round(t.r, 4),
                                "larghezza_stop": round(st.larghezza_stop(t), 5)} for t in out["risultato"].trade]}
        (RISULTATI / f"{v['id']}.json").write_text(json.dumps(_pulisci(dettaglio), indent=1, ensure_ascii=False) + "\n",
                                                  encoding="utf-8")
        registro.aggiungi({"id": v["id"], "tipo": "risultato", "metriche": _pulisci(_arrot(sintesi)),
                           "r_per_anno": _pulisci({k: round(x, 3) for k, x in m["r_per_anno"].items()}),
                           "buy_and_hold": round(out["buy_and_hold"], 4),
                           "esiti": _pulisci(out["esiti"]), "esito": "supera" if out["supera"] else "non supera",
                           "dettaglio": f"risultati/{v['id']}.json"})
        avanza(f"{v['id']} fatta: {'supera' if out['supera'] else 'non supera'}")
        print(f"{v['id']}: trade {m['trade']}, R medio {m['r_medio']:.3f}, PF {m['profit_factor']:.2f}, "
              f"p {out['p_value']:.3f}, casuali {sintesi['r_medio_casuali']:.3f} -> "
              f"{'SUPERA' if out['supera'] else 'non supera'}")
    avanza("FINE")


def cmd_fase4(voci: list) -> None:
    RISULTATI.mkdir(exist_ok=True)
    for v in voci:
        vid = v["id"]
        ris = [x for x in registro.voci() if x.get("id") == vid and x.get("tipo") == "risultato"]
        if not ris or ris[0].get("esito") != "supera":
            raise SystemExit(f"{vid}: non ha superato la Fase 2")
        spec = cat.normalizza(v["specifica"])
        s, a, b = serie_costruzione(spec["timeframe"])
        idv = f"{vid}-F4"
        registro.aggiungi({"id": idv, "tipo": "registrazione", "tipo_test": "verifica", "verifica_di": vid,
                           "periodo": "costruzione", "previsione": v.get("previsione_fase4", ""),
                           "criterio_successo": "Fase 4, verifiche da 1 a 8"})
        avanza(f"{idv} in corso")
        out = st.fase4(spec, s, a, b, serie_costruzione)
        (RISULTATI / f"{vid}_fase4.json").write_text(json.dumps(_pulisci(out), indent=1, ensure_ascii=False) + "\n",
                                                    encoding="utf-8")
        esiti = {k: out[k].get("supera") for k in out if isinstance(out[k], dict)}
        registro.aggiungi({"id": idv, "tipo": "risultato", "esiti": _pulisci(esiti),
                           "esito": "candidato" if out["candidato"] else "non candidato",
                           "dettaglio": f"risultati/{vid}_fase4.json"})
        avanza(f"{idv} fatta")
        print(f"{idv}: {json.dumps(_pulisci(esiti))} -> {'CANDIDATO' if out['candidato'] else 'non candidato'}")
    avanza("FINE")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("prova", "stima", "fase2", "fase4"):
        raise SystemExit(__doc__)
    {"prova": cmd_prova, "stima": cmd_stima, "fase2": cmd_fase2, "fase4": cmd_fase4}[sys.argv[1]](leggi_voci(sys.argv[2]))
