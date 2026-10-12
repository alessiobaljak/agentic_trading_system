"""Scrive nel log la voce ``risultato`` di un test, dai numeri dell'esito e da un commento.

Uso: python risultato.py commenti.jsonl
Ogni riga del file: {"id": ..., "etichetta": "test", "previsione_corretta": true/false, "commento": "..."}
(per una verifica anche "tipo_test": "verifica" e "verifica_di"). I numeri vengono dal file
data/insample/FILUSDT/esiti/<id o nome>_<etichetta>.json, senza ritoccarli.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import comune
import registro


def voce_risultato(riga: dict) -> dict:
    nome = riga.get("nome", riga["id"])
    e = json.loads((comune.CARTELLA_DATI / "esiti" / f"{nome}_{riga.get('etichetta', 'test')}.json").read_text())
    m = e.get("metriche", {})
    metriche = {k: m.get(k) for k in (
        "profit_factor", "trade", "r_medio", "r_mediano", "win_rate", "r_medio_per_anno", "trade_per_anno",
        "r_medio_senza_3_migliori", "drawdown_max", "rendimento_totale", "rendimento_per_anno", "costi_medi_r",
        "funding_totale_r", "stop_medio_pct", "quota_stop_oltre_6pct", "n_ridotti", "n_violazioni_liquidazione",
        "esiti", "n_buchi_dati")}
    if not m:
        metriche = {"trade": e.get("trade", 0)}
    voce = {"id": riga["id"], "tipo": "risultato"}
    for k in ("tipo_test", "verifica_di", "etichetta"):
        if k in riga:
            voce[k] = riga[k]
    voce.update({
        "periodo": e.get("periodo"),
        "metriche": metriche,
        "blocco": e.get("blocco"),
        "durata_media_barre": e.get("durata_media_barre"),
        "baseline_a": e.get("baseline_a"),
        "baseline_b": e.get("baseline_b"),
        "percentile_caso": e.get("percentile_caso"),
        "buy_and_hold_per_anno": e.get("buy_and_hold_per_anno"),
        "valutabile": e.get("valutabile"),
        "candidato": e.get("candidato"),
        "previsione_corretta": riga["previsione_corretta"],
        "commento": riga["commento"],
    })
    return voce


if __name__ == "__main__":
    for r in Path(sys.argv[1]).read_text().splitlines():
        if r.strip():
            print(registro.aggiungi(voce_risultato(json.loads(r)))["id"])
