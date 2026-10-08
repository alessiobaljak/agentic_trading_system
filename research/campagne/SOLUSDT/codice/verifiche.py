"""Fase 4: verifiche dei candidati sui dati di costruzione (PROTOCOLLO.md, Passo 3, Fase 4).

  python verifiche.py <ID> [<ID> ...]

Per ogni candidato e per ogni caso: conta_trade (una volta, sulle regole del caso), voce
'registrazione' con tipo_test 'verifica' e verifica_di, test con le baseline (a) e (b) ricalcolate
nelle stesse condizioni, voce 'risultato'. In serie (le voci del log sono progressive).

Casi (regole scritte prima dei risultati, uguali per tutti i candidati della famiglia di 015):
* robustezza: ogni parametro numerico a 0,8 e 1,2 volte, uno alla volta (interi: round con le meta'
  verso l'alto; se resta uguale, -1 e +1): moltiplicatore dello stop, periodo dell'ATR (14 barre),
  periodo della SMA (200 barre, solo con il filtro). Non si spostano: la tenuta di 1 barra e i confini
  orari (prima mezz'ora dalle 00:00, ingresso alle 23:30): sono la definizione del meccanismo
  («ultima mezz'ora», «prima mezz'ora»), parametri di scelta; si dichiara.
* timeframe adiacenti: 15m e 1h, parametri in barre convertiti per tenere la stessa durata.
* ritardo di una barra, costi doppi, regola intra-barra opposta (target prima: senza target non cambia
  nulla, si dichiara).
"""
import json
import math
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune  # noqa: E402
import registro  # noqa: E402
import schede  # noqa: E402
from varianti import i09_generale  # noqa: E402

CANDIDATI = {
    "SOLUSDT-023": {"filtro_sma200": True, "filtro_giorno": False, "k_stop": 2.0},
    "SOLUSDT-024": {"filtro_sma200": False, "filtro_giorno": True, "k_stop": 2.0},
    "SOLUSDT-026": {"filtro_sma200": True, "filtro_giorno": False, "k_stop": 3.0},
    "SOLUSDT-027": {"filtro_sma200": False, "filtro_giorno": True, "k_stop": 3.0},
}


def arrotonda(x):
    return int(math.floor(x + 0.5))


def casi(vid):
    p = CANDIDATI[vid]
    base = dict(p, n_atr_min=420, n_sma_min=6000, tenuta_min=30)
    out = []
    k = p["k_stop"]
    for f, nome in ((0.8, "giu"), (1.2, "su")):
        out.append((f"robustezza_stop_{nome}", "30m", dict(base, k_stop=round(k * f, 4)), comune.PARAMETRI,
                    f"moltiplicatore dello stop {k} -> {round(k * f, 4)}"))
    for nuovo, nome in ((arrotonda(14 * 0.8), "giu"), (arrotonda(14 * 1.2), "su")):
        out.append((f"robustezza_atr_{nome}", "30m", dict(base, n_atr_min=nuovo * 30), comune.PARAMETRI,
                    f"periodo dell'ATR 14 -> {nuovo} barre"))
    if p["filtro_sma200"]:
        for nuovo, nome in ((arrotonda(200 * 0.8), "giu"), (arrotonda(200 * 1.2), "su")):
            out.append((f"robustezza_sma_{nome}", "30m", dict(base, n_sma_min=nuovo * 30), comune.PARAMETRI,
                        f"periodo della SMA 200 -> {nuovo} barre"))
    out.append(("timeframe_15m", "15m", base, comune.PARAMETRI, "timeframe adiacente 15m: ATR 28 barre, SMA 400 barre, tenuta 2 barre"))
    out.append(("timeframe_1h", "1h", base, comune.PARAMETRI, "timeframe adiacente 1h: ATR 7 barre, SMA 100 barre, tenuta 1 barra (la prima ora e l'ultima ora)"))
    out.append(("ritardo", "30m", base, replace(comune.PARAMETRI, ritardo_barre=1), "esecuzione ritardata di una barra (b ricalcolata col ritardo)"))
    out.append(("costi_doppi", "30m", base, replace(comune.PARAMETRI, moltiplicatore_costi=2.0), "costi doppi (b ricalcolata a costi doppi)"))
    out.append(("intrabarra_opposta", "30m", base, replace(comune.PARAMETRI, riempimento_intrabarra="target_prima"), "regola intra-barra opposta (target prima)"))
    return out


def esegui_verifica(vid, nome, tf, regola, parametri, descrizione):
    costr = i09_generale("short", **regola)
    vidv = f"{vid}-V-{nome}"
    stima = comune.conta(tf, costr, parametri)["trade"]
    voce = {"id": vidv, "tipo": "registrazione", "tipo_test": "verifica", "verifica_di": vid, "caso": nome,
            "descrizione": descrizione, "timeframe": tf, "direzione": "short", "parametri": regola,
            "parametri_motore": {"ritardo_barre": parametri.ritardo_barre, "moltiplicatore_costi": parametri.moltiplicatore_costi,
                                 "riempimento_intrabarra": parametri.riempimento_intrabarra},
            "periodo": "costruzione", "trade_stimati": stima,
            "previsione": "costi doppi: R medio negativo e (b) non battuta nettamente; ritardo: t contro la (b) crolla (un ritardo di 30 minuti sposta l'ingresso fuori dall'ultima mezz'ora); robustezza e timeframe adiacenti: t contro la (b) positivo ma spesso sotto la soglia",
            "criterio_successo": "regole della Fase 4 (PROTOCOLLO.md): vedi la nota di sintesi del candidato"}
    registro.aggiungi(voce)
    if stima < comune.TRADE_MINIMI_COSTRUZIONE:
        registro.aggiungi({"id": vidv, "tipo": "risultato", "metriche": {"trade": stima}, "baseline_a": {}, "baseline_b": {},
                           "commento": f"caso sotto i trade minimi di costruzione ({stima}): si dichiara e non conta"})
        print(vidv, "sotto i trade minimi", stima, flush=True)
        return
    ris = comune.valuta(tf, costr, "costruzione", parametri)
    met = ris.get("metriche", {})
    voce_r = {"id": vidv, "tipo": "risultato", "metriche": met, "blocco": ris.get("blocco"),
              "baseline_a": ris.get("baseline_a"), "baseline_b": ris.get("baseline_b"),
              "percentile_caso": ris.get("percentile_caso"), "candidato_nelle_stesse_condizioni": ris.get("candidato"),
              "trade_uguali_alla_stima": met.get("trade") == stima,
              "commento": f"R medio {met.get('r_medio')}, t contro la (b) {ris.get('baseline_b', {}).get('t')} (netta {ris.get('baseline_b', {}).get('netta')})"}
    registro.aggiungi(voce_r)
    (schede.BOZZE / f"ver_{vidv}.json").write_text(json.dumps(comune.pulito(ris), ensure_ascii=False, default=str))
    print(vidv, "trade", met.get("trade"), "R", met.get("r_medio"), "t_b", ris.get("baseline_b", {}).get("t"),
          "netta_b", ris.get("baseline_b", {}).get("netta"), flush=True)


def placebo(vid):
    """Fase 5: la stessa regola con l'ingresso a un'ora qualunque (11:30 UTC, uscita alle 12:00)."""
    base = dict(CANDIDATI[vid], n_atr_min=420, n_sma_min=6000, tenuta_min=30, uscita_min=720)
    return ("placebo_ora_11_30", "30m", base, comune.PARAMETRI,
            "Fase 5, prova dello scettico: stessa regola ma ingresso alle 11:30 UTC e uscita alle 12:00 (ora placebo); "
            "se il t contro la (b) e' simile, l'effetto non e' dell'ultima mezz'ora ma del momentum generico a 30 minuti")


if __name__ == "__main__":
    if sys.argv[1] == "placebo":
        for vid in sys.argv[2:]:
            esegui_verifica(vid, *placebo(vid))
        sys.exit(0)
    for vid in sys.argv[1:]:
        for caso in casi(vid):
            esegui_verifica(vid, *caso)
