"""Esecuzione delle varianti nell'ordine del protocollo (sezioni 6 e 8, Fase 1 punto 7, Fase 2).

Per ogni variante, in quest'ordine e in serie (mai due lotti in parallelo: gli id del log):
1. ``conta_trade`` una volta sola sulle regole esatte della variante;
2. sotto 70 trade: voce ``scarto`` nel log (nessun budget consumato), fine;
3. altrimenti voce ``registrazione`` (con ``trade_stimati`` e ``variante_n``) PRIMA del test;
4. il test (``quadro.valuta``) sui dati di costruzione;
5. voce ``risultato`` con i nomi della sezione 6.

Uso: python campagna.py <modulo> <ID> [<ID> ...]
Il modulo (nella cartella codice/) definisce ``VARIANTI``: {id: (classe, meta)}.
I risultati completi vanno anche in data/insample/MASKUSDT/risultati/<id>.json (fuori da git).
"""
from __future__ import annotations

import importlib
import json
import sys
import time
from pathlib import Path

CODICE = Path(__file__).resolve().parent
sys.path.insert(0, str(CODICE))

import quadro  # noqa: E402
import registro  # noqa: E402

USCITE = quadro.RADICE_REPO / "research" / "data" / "insample" / "MASKUSDT" / "risultati"


def _scrivi_esito(nome, dato):
    USCITE.mkdir(parents=True, exist_ok=True)
    (USCITE / f"{nome}.json").write_text(json.dumps(registro._pulisci(dato), indent=1, ensure_ascii=False))


def stampa(*a):
    USCITE.mkdir(parents=True, exist_ok=True)
    with open(USCITE / "avanzamento.txt", "a") as f:
        f.write(" ".join(str(x) for x in a) + "\n")


def variante_n_successiva():
    return 1 + sum(1 for v in registro.voci() if v["tipo"] == "registrazione" and v.get("tipo_test") == "variante")


def gia_fatta(vid):
    return any(v.get("id") == vid and v["tipo"] in ("registrazione", "scarto") for v in registro.voci())


def esegui_variante(vid, classe, meta):
    if gia_fatta(vid):
        stampa(vid, "gia' nel log: salto")
        return
    var = classe()
    t0 = time.time()
    conteggio = quadro.conta(var)
    n = conteggio["trade"]
    stampa(vid, "conta_trade", conteggio, f"{time.time() - t0:.0f}s")
    base = {"idea": meta["idea"], "famiglia": meta.get("famiglia", vid), "ritocco_di": meta.get("ritocco_di"),
            "fonte": meta["fonte"], "meccanismo": meta["meccanismo"], "timeframe": var.tf,
            "direzione": var.direzione, "parametri": meta["parametri"], "periodo": "costruzione"}
    if n < quadro.TRADE_MINIMI_COSTRUZIONE:
        registro.aggiungi(dict(id=vid, tipo="scarto", **base, trade_stimati=n, conteggio=conteggio,
                               motivo=f"trade stimati {n} sotto il minimo di costruzione (70)"))
        stampa(vid, "SCARTO", n)
        return
    registro.aggiungi(dict(id=vid, tipo="registrazione", tipo_test="variante", **base,
                           previsione=meta["previsione"], criterio_successo=meta.get(
                               "criterio_successo",
                               "batte nettamente la (a) e la (b) (contro_baseline) con R medio dopo i costi positivo"),
                           trade_stimati=n, conteggio=conteggio, variante_n=variante_n_successiva()))
    t0 = time.time()
    esito = quadro.valuta(var)
    stampa(vid, "test", f"{time.time() - t0:.0f}s")
    _scrivi_esito(vid, esito)
    m = esito["metriche"]
    voce = {
        "id": vid, "tipo": "risultato",
        "metriche": {k: m[k] for k in ["profit_factor", "trade", "r_medio", "r_medio_per_anno", "trade_per_anno",
                                        "r_medio_senza_3_migliori", "drawdown_max", "rendimento_totale",
                                        "rendimento_per_anno", "win_rate", "esiti", "n_ridotti",
                                        "n_violazioni_liquidazione", "n_buchi_dati", "n_funding_in_buco",
                                        "funding_totale", "stop_pct_mediana", "stop_oltre_6pct"]},
        "blocco": esito.get("blocco"), "baseline_a": esito.get("baseline_a"), "baseline_b": esito.get("baseline_b"),
        "percentile_caso": esito.get("percentile_caso"), "buy_and_hold_per_anno": esito.get("buy_and_hold_per_anno"),
        "valutabile": esito.get("valutabile"), "candidato": esito.get("candidato"),
        "trade_uguali_alla_stima": m["trade"] == n,
    }
    if "previsione_r" in meta:
        lo, hi = meta["previsione_r"]
        voce["previsione_corretta"] = bool(lo <= m["r_medio"] <= hi)
        voce["commento"] = f"previsione R medio fra {lo} e {hi}; osservato {m['r_medio']:.3f}"
    registro.aggiungi(voce)
    stampa(vid, "candidato" if esito.get("candidato") else "non candidato",
           "t_b", esito.get("baseline_b", {}).get("t"), "t_a", esito.get("baseline_a", {}).get("t"),
           "r", m["r_medio"])


def main():
    modulo = importlib.import_module(sys.argv[1])
    for vid in sys.argv[2:]:
        classe, meta = modulo.VARIANTI[vid]
        esegui_variante(vid, classe, meta)
    stampa("fine lotto", sys.argv[1:])


if __name__ == "__main__":
    main()
