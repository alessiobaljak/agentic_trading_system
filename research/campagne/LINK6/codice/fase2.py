"""Fase 2 (sezione 13, Passo 2): registra nel log, poi esegue la variante sul periodo di costruzione con le
entrate casuali (statistica4.fase2_4), poi scrive il risultato. Una variante alla volta, in serie.

Uso: python3 research/campagne/LINK6/codice/fase2.py <lotto.json> <id> [<id> ...] [--riprendi]

Ogni voce del lotto ha: id, ipotesi, fonte, specifica, previsione. L'avanzamento va in
data/insample/LINKUSDT/fase2_avanzamento.txt (ultima riga: FINE o ERRORE). I trade di ogni variante vanno
in campagne/LINK6/risultati/<id>.json, per la Fase 3.
"""
import json
import math
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comune  # noqa: E402
from research.src.catalogo3 import compila, normalizza  # noqa: E402
from research.src.motore3 import stima_trade  # noqa: E402
from research.src.statistica3 import larghezza_stop  # noqa: E402
from research.src.statistica4 import REGOLE_LINK, fase2_4  # noqa: E402

AVANZAMENTO = "fase2_avanzamento.txt"
RISULTATI = comune.CAMPAGNA / "risultati"


def _r3(x):
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return None if x is None else str(x)
    return round(float(x), 3)


def _utc(ms):
    return datetime.fromtimestamp(int(ms) / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def esegui_una(voce, riprendi=False):
    """Con ``riprendi`` la variante deve essere gia' registrata, senza risultato, con una voce `correzione`
    che spiega perche' il risultato manca: si riesegue la stessa specifica registrata, senza nuova
    registrazione (stesso seme: stesso risultato)."""
    vid = voce["id"]
    gia = [v for v in comune.voci() if v.get("id") == vid]
    v = normalizza(voce["specifica"])
    if riprendi:
        reg = [x for x in gia if x.get("tipo") == "registrazione"]
        if not reg or any(x.get("tipo") == "risultato" for x in gia) or not any(x.get("tipo") == "correzione" for x in gia):
            raise SystemExit(f"{vid}: si riprende solo una variante registrata, senza risultato, con una correzione")
        if reg[0]["specifica"] != v:
            raise SystemExit(f"{vid}: la specifica del lotto non e' quella registrata")
        n = reg[0]["variante_n"]
        s, a, b = comune.serie_costruzione(v["timeframe"])
        c = compila(v, s)
        comune.scrivi_avanzamento(AVANZAMENTO, f"{vid}: ripresa (variante {n}), inizio {comune.ora()}")
    else:
        if any(x.get("tipo") in ("registrazione", "scarto") for x in gia):
            raise SystemExit(f"{vid}: gia' registrata o scartata nel log")
        n = len(comune.varianti_registrate()) + 1
        if n > comune.VARIANTI_MASSIME:
            raise SystemExit(f"limite di {comune.VARIANTI_MASSIME} varianti raggiunto")
        s, a, b = comune.serie_costruzione(v["timeframe"])
        c = compila(v, s)
        stimati = stima_trade(c, REGOLE_LINK, a, b)["trade"]
        if stimati < comune.TRADE_MINIMI:
            raise SystemExit(f"{vid}: stima {stimati} sotto i minimi: va registrata come scarto, non testata")
        comune.aggiungi({"id": vid, "tipo": "registrazione", "tipo_test": "variante", "ipotesi": voce["ipotesi"],
                         "fonte": voce["fonte"], "specifica": v, "periodo": "costruzione",
                         "trade_stimati": stimati, "variante_n": n, "previsione": voce["previsione"],
                         "criterio_successo": "sezione 10.3, costruzione"})
        comune.scrivi_avanzamento(AVANZAMENTO, f"{vid}: registrata come variante {n}, inizio {comune.ora()}")
    t0 = time.time()
    f2 = fase2_4(v, s, a, b, compilata=c)
    m = f2["metriche"]
    metr = {"trade": m["trade"], "trade_al_mese": _r3(m.get("trade_al_mese")), "r_medio": _r3(m["r_medio"]),
            "profit_factor": _r3(m["profit_factor"]), "vincenti": _r3(m["vincenti"]),
            "r_medio_vincenti": _r3(m["r_medio_vincenti"]), "r_medio_perdenti": _r3(m["r_medio_perdenti"]),
            "drawdown_max_r": _r3(m["drawdown_max_r"]), "tempo_in_posizione": _r3(m.get("tempo_in_posizione")),
            "r_per_anno": {str(k): _r3(x) for k, x in m["r_per_anno"].items()},
            "ridotti": m["ridotti"], "violazioni_liquidazione": m["violazioni_liquidazione"],
            "motivi": m["motivi"], "p_value": _r3(f2["p_value"])}
    for k in ("ordini_inseriti", "ordini_eseguiti", "ordini_cancellati", "esecuzione"):
        if k in m:
            metr[k] = _r3(m[k]) if k == "esecuzione" else m[k]
    casuali = f2["casuali"] or {}
    r_casuali = [] if f2["valori_casuali"] is None else [float(x) for x in f2["valori_casuali"]]
    risultato = {"id": vid, "tipo": "risultato", "metriche": metr,
                 "esiti": {k: bool(x) for k, x in f2["esiti"].items()},
                 "esito": "supera" if f2["supera"] else "non supera",
                 "r_medio_entrate_casuali": _r3(sum(r_casuali) / len(r_casuali)) if r_casuali else None,
                 "buy_and_hold": _r3(f2["buy_and_hold"]),
                 "secondi_di_calcolo": round(time.time() - t0)}
    risultato["casuali_info"] = {k: x for k, x in casuali.items() if isinstance(x, (int, float, str))}
    comune.aggiungi(risultato)
    RISULTATI.mkdir(exist_ok=True)
    trade = [{"ingresso": _utc(t.ts_ingresso), "uscita": _utc(t.ts_uscita), "r": _r3(t.r), "motivo": t.motivo,
              "larghezza_stop": round(larghezza_stop(t), 5)} for t in f2["risultato"].trade]
    (RISULTATI / f"{vid}.json").write_text(json.dumps({"id": vid, "trade": trade}, ensure_ascii=False, indent=0),
                                           encoding="utf-8")
    comune.scrivi_avanzamento(AVANZAMENTO, f"{vid}: fatto in {risultato['secondi_di_calcolo']} s")


def main():
    lotto = comune.leggi_lotto(sys.argv[1])
    riprendi = "--riprendi" in sys.argv[2:]
    for vid in [x for x in sys.argv[2:] if x != "--riprendi"]:
        esegui_una(lotto[vid], riprendi)
    comune.scrivi_avanzamento(AVANZAMENTO, "FINE")


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        comune.scrivi_avanzamento(AVANZAMENTO, traceback.format_exc())
        comune.scrivi_avanzamento(AVANZAMENTO, "ERRORE")
        raise
