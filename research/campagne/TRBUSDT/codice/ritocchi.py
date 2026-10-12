"""Ritocchi (regola 6): l'ordine dal log e l'esecuzione di un ritocco registrato prima del test.

``python -m ...ritocchi ordine``  stampa la lista ordinata per t contro la (b) (dal piu' alto; a
parita' la variante registrata prima) delle varianti testate valutabili, non candidate, la cui
famiglia ha meno di 5 ritocchi.
``python -m ...ritocchi esegui <ID>``  esegue il ritocco definito in RITOCCHI.
"""

import json
import math
import sys

from research.campagne.TRBUSDT.codice import banco, registro
from research.campagne.TRBUSDT.codice import varianti as V
from research.campagne.TRBUSDT.codice.esegui_variante import esegui

MASSIMO = 5

RITOCCHI = {
    "I-13-S-R1": {
        "ritocco_di": "I-13-S", "famiglia": "I-13-S", "idea": "I-13",
        "parametri": {"range": "00:00-01:00 UTC", "ultima_ora_segnale": 22, "ora_minima_rottura": 4,
                      "stop": "massimo del range", "uscita": "chiusura 23:45-24:00"},
        "motivo": ("cambia: la prima rottura del giorno vale solo se la barra del segnale e' dalle 04:00 UTC in poi "
                   "(se la prima rottura arriva prima, quel giorno niente trade). Perche': studio dei fallimenti "
                   "(data/insample/TRBUSDT/fallimenti_I-13-S.json, solo costruzione): 288 trade su 474 entrati fra "
                   "le 00 e le 04 UTC con R medio -0,23 (lordo -0,19), contro -0,01 / +0,12 / -0,09 / +0,23 / -0,07 "
                   "nelle fasce successive; una rottura subito dopo la formazione del range e' piu' spesso rumore."),
        "previsione": ((-0.10, 0.10), "non batte nettamente la (b): il filtro toglie i trade peggiori ma ne lascia circa 190, "
                                      "e la selezione fatta sui dati di costruzione gonfia il risultato"),
    },
    "I-13-S-R2": {
        "ritocco_di": "I-13-S", "famiglia": "I-13-S", "idea": "I-13",
        "parametri": {"range": "00:00-01:00 UTC", "ultima_ora_segnale": 22, "ora_minima_rottura": 8,
                      "stop": "massimo del range", "uscita": "chiusura 23:45-24:00"},
        "motivo": ("cambia: la prima rottura del giorno vale solo se la barra del segnale e' dalle 08:00 UTC in poi. "
                   "Perche': nello studio dei fallimenti di I-13-S (fallimenti_I-13-S.json, solo costruzione) la fascia "
                   "d'ingresso 04-08 UTC ha R medio -0,01 (76 trade), le fasce dalle 08 in poi in media positive "
                   "(+0,12, -0,09, +0,23, -0,07 su 110 trade). Il ritocco 1 (dalle 04) e' gia' nel log con t 1,25 contro la (b)."),
        "previsione": ((-0.05, 0.15), "non batte nettamente la (b): restano circa 110 trade, l'errore cresce"),
    },
    "I-13-S-R3": {
        "ritocco_di": "I-13-S", "famiglia": "I-13-S", "idea": "I-13",
        "parametri": {"range": "00:00-01:00 UTC", "ultima_ora_segnale": 22, "ora_minima_rottura": 0,
                      "stop": "massimo del range + 0,5 ATR(14) a 15m", "uscita": "chiusura 23:45-24:00"},
        "motivo": ("cambia: lo stop si allarga di 0,5 ATR oltre il massimo del range (nessun filtro orario). Perche': "
                   "in I-13-S 290 trade su 474 escono in stop (R medio -1,04) e 184 a fine giornata (+1,31); la Fase 0 "
                   "mostra ombre estreme sul 15m (fase0_anomalie.json): uno stop appena oltre il range viene preso dal "
                   "rumore prima che la giornata scelga la direzione."),
        "previsione": ((-0.15, 0.05), "non batte nettamente la (b): lo stop piu' largo riduce gli stop ma anche l'R dei vincenti"),
    },
}


def ordine():
    voci = registro.voci()
    reg = {v["id"]: v for v in voci if v.get("tipo") == "registrazione" and v.get("tipo_test") == "variante"}
    ris = {v["id"]: v for v in voci if v.get("tipo") == "risultato"}
    ritocchi_per_famiglia = {}
    for v in voci:
        if v.get("tipo") in ("registrazione", "scarto") and v.get("ritocco_di"):
            ritocchi_per_famiglia[v["famiglia"]] = ritocchi_per_famiglia.get(v["famiglia"], 0) + 1
    lista = []
    for id_, r in reg.items():
        if id_ not in ris:
            continue
        x = ris[id_]
        t = x.get("t_b")
        t = -math.inf if t in (None, "-inf") else float(t)
        if not x.get("valutabile") or x.get("candidato"):
            continue
        if ritocchi_per_famiglia.get(r["famiglia"], 0) >= MASSIMO:
            continue
        lista.append((t, r["variante_n"], id_, r["famiglia"], ritocchi_per_famiglia.get(r["famiglia"], 0)))
    lista.sort(key=lambda z: (-z[0], z[1]))
    return [{"id": i, "t_b": t, "variante_n": n, "famiglia": f, "ritocchi_famiglia": k} for t, n, i, f, k in lista]


if __name__ == "__main__":
    if sys.argv[1] == "ordine":
        print(json.dumps(ordine()[:8], indent=1))
    else:
        id_ = sys.argv[2]
        d = RITOCCHI[id_]
        primo = ordine()[0]["id"]
        if primo != d["ritocco_di"]:
            raise SystemExit(f"il primo della lista e' {primo}, non {d['ritocco_di']}")
        out = esegui(id_, variante=V.VARIANTI[id_](), ritocco_di=d["ritocco_di"], famiglia=d["famiglia"],
                     previsione=d["previsione"], parametri=d["parametri"], idea=d["idea"], motivo=d["motivo"])
        print(json.dumps(banco._json_ok(out), indent=1, ensure_ascii=False))
