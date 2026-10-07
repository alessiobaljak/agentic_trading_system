"""Esegue una variante secondo il protocollo: stima -> (scarto | registrazione -> test -> risultato).

Uso: python esegui_variante.py <ID> [--sim N] [--senza-baseline]
Il log si scrive PRIMA del test (registrazione con previsione) e DOPO (risultato).
Il numero di variante (``variante_n``) e' il conteggio delle registrazioni di tipo
``variante`` gia' presenti nel log, piu' uno. L'esito completo va in
``codice/risultati/<ID>.json``.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dati_btc as d  # noqa: E402
import strumenti as s  # noqa: E402
from varianti import VARIANTI  # noqa: E402

TRADE_MINIMI_COSTRUZIONE = 100
LOG = Path(__file__).resolve().parent.parent / "log.jsonl"


def prossimo_numero_variante() -> int:
    n = 0
    if LOG.exists():
        for riga in LOG.read_text(encoding="utf-8").splitlines():
            if not riga.strip():
                continue
            v = json.loads(riga)
            if v.get("tipo") == "registrazione" and v.get("tipo_test") == "variante":
                n = max(n, int(v.get("variante_n", 0)))
    return n + 1


def main(argv):
    id_ = argv[1]
    n_sim = 100
    con_baseline = True
    if "--sim" in argv:
        n_sim = int(argv[argv.index("--sim") + 1])
    if "--senza-baseline" in argv:
        con_baseline = False
    v = VARIANTI[id_]
    serie = s.Serie(v["tf"])
    entra = v["entra"](serie)
    uscita = v["uscita"](serie)
    stima = s.stima_trade(serie, entra, d.COSTRUZIONE, int(v["occupazione"]))
    base = {"id": id_, "idea": v["idea"], "fonte": v["fonte"], "meccanismo": v["meccanismo"],
            "timeframe": v["tf"], "direzione": v["direzione"], "parametri": v["parametri"],
            "uscita": {k: val for k, val in uscita.items() if not callable(val)} | {k: "regola custom (vedi varianti.py)" for k, val in uscita.items() if callable(val)},
            "periodo": "costruzione", "stima_trade": stima}
    if stima["trade_stimati"] < TRADE_MINIMI_COSTRUZIONE:
        s.registra({**base, "tipo": "scarto", "motivo": f"stima dei trade {stima['trade_stimati']} sotto il minimo di {TRADE_MINIMI_COSTRUZIONE} in costruzione: non si testa, nessun budget consumato"})
        print("SCARTO", id_, stima)
        return
    n_var = prossimo_numero_variante()
    s.registra({**base, "tipo": "registrazione", "tipo_test": "variante", "variante_n": n_var,
                "previsione": v["previsione"], "previsione_pf": v["previsione_pf"],
                "criterio_successo": v["criterio_successo"], "trade_stimati": stima["trade_stimati"],
                "n_simulazioni_caso": n_sim if con_baseline else 0})
    out, ris = s.esamina(serie, entra, uscita, d.COSTRUZIONE, n_sim_caso=n_sim, con_baseline=con_baseline,
                         direzione_di=v["direzione_di"](serie), ammessa=(v["ammessa"](serie) if "ammessa" in v else None))
    m = out["metriche"]
    pf = m["profit_factor"]
    lo, hi = v["previsione_pf"]
    prev_ok = pf is not None and lo <= pf <= hi
    b = out.get("baseline_b_casuale", {})
    a = out.get("baseline_a_incondizionata", {})
    successo = (m["n_trade"] >= TRADE_MINIMI_COSTRUZIONE and m["r_medio"] > 0
                and (b.get("percentile_del_candidato") or 0) >= 90
                and b.get("confronto_con_sim_mediana", {}).get("netta") is True
                and (a.get("confronto", {}).get("netta") is True and a.get("confronto", {}).get("segno") == 1 if a else True))
    out["criterio_successo_superato"] = bool(successo)
    out["previsione_corretta"] = bool(prev_ok)
    s.salva_risultato(id_, {"variante": {k: val for k, val in v.items() if not callable(val)}, **out})
    s.registra({"id": id_, "tipo": "risultato", "periodo": "costruzione", "variante_n": n_var,
                "metriche": {k: m[k] for k in ("n_trade", "profit_factor", "win_rate", "r_medio", "r_mediano", "rendimento_totale", "drawdown_max", "rendimento_per_anno", "r_medio_per_anno", "n_trade_per_anno", "esiti", "n_ridotti", "n_violazioni_liquidazione", "funding_totale", "durata_barre", "stop_pct")},
                "baseline_a_incondizionata": a or None, "baseline_b_casuale": b or None, "baseline_c_buy_and_hold": out.get("baseline_c_buy_and_hold"),
                "blocco_bootstrap": out["blocco_bootstrap"],
                "previsione_corretta": bool(prev_ok), "criterio_successo_superato": bool(successo),
                "commento": "vedi la voce nota successiva per il commento del ricercatore"})
    print(json.dumps({"id": id_, "n_trade": m["n_trade"], "pf": pf, "r_medio": m["r_medio"], "r_mediano": m["r_mediano"], "win": m["win_rate"], "dd": m["drawdown_max"],
                      "per_anno": m["r_medio_per_anno"], "n_anno": m["n_trade_per_anno"], "esiti": m["esiti"], "stop_pct": m["stop_pct"],
                      "a": a, "b": b, "bh": out.get("baseline_c_buy_and_hold"), "blocco": out["blocco_bootstrap"], "successo": successo, "prev_ok": prev_ok}, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main(sys.argv)
