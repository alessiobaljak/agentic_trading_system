"""Fase 1, punto 7: registra nel log la correzione sulla stima e gli scarti per stima sotto il minimo."""
from __future__ import annotations

import json
import sys
from pathlib import Path

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
import strategie  # noqa: E402
from log import aggiungi, leggi  # noqa: E402

stime: dict = {}
for nome_file in sorted(QUI.parent.glob("fase1_stime*.json")):
    stime.update(json.loads(nome_file.read_text(encoding="utf-8")))
ids = {v.get("id") for v in leggi()}

if "ETHUSDT-C001" not in ids:
    aggiungi({"id": "ETHUSDT-C001", "tipo": "correzione", "corregge": "la regola di stima dei trade scritta in ipotesi.md (ultima sezione)",
              "testo": ("ipotesi.md dichiarava una sola regola di stima: un segnale conta se dista dal precedente contato almeno H barre. "
                        "Dopo aver visto i conteggi (I-01 short 99, I-02 66/48, I-06 28/31) mi sono accorto che per le idee con uscita su "
                        "segnale (I-01 esce al cambio di segno, I-02 alla rottura opposta del canale a 15 barre, I-06 al rientro di z a 0) "
                        "quella regola assume che ogni posizione duri H barre, mentre la regola dell'idea la chiude prima. Aggiunta una "
                        "seconda stima che simula SOLO entrate e uscite da segnale (nessun prezzo di uscita, nessun rendimento, stop "
                        "ignorati: prudente). Per le idee con uscita su segnale decide la seconda; per le altre resta la prima. "
                        "Dichiaro che la modifica e' avvenuta dopo aver visto i conteggi dei segnali, mai un rendimento. Effetto: I-01 "
                        "short passa da 99 a 230 e si testa; I-02 e I-06 restano sotto 100 con entrambe le stime e si scartano. "
                        "Testare una variante in piu' consuma budget e aumenta m nell'asticella: non favorisce il risultato."),
              "stime": {k: {"distanza_h": v["trade_stimati_distanza_h"], "uscita_segnale": v["trade_stimati_uscita_segnale"]} for k, v in stime.items()}})

MOTIVI = {
    "I-02": "rotture del canale a 30 barre da 4h: pochi episodi in 1.023 giorni",
    "I-04": "candele da 4h oltre 2,5 deviazioni standard: circa 100 segnali per direzione, raggruppati in pochi giorni",
    "I-06": "scostamenti del rapporto ETH/BTC oltre 2 deviazioni standard con uscita a 0: circa 30 episodi per direzione",
    "I-07": "un ingresso a settimana diviso per direzione: al massimo 73 segnali in 143 settimane",
    "I-08": "fine settimana oltre l'1 % divisi per direzione: 56 e 63 segnali in 143 settimane",
    "I-10": "funding sotto il 10° percentile mobile: 111 segnali ma raggruppati, 94 trade stimati",
    "I-11": "compressione sotto 0,5 seguita da rottura: 8 segnali per direzione in tutto",
    "I-12": "volume sopra il 90° percentile a 12h con tenuta di 6 barre: 98 trade stimati, appena sotto il minimo",
    "I-13": "quota di compratori aggressivi oltre le soglie: pochi segnali",
    "I-14": "premio del perpetuo oltre i percentili estremi: pochi segnali indipendenti",
    "I-15": "rotture del range d'apertura: pochi giorni oltre mezzo ATR",
    "I-16": "una barra al giorno: non puo' essere sotto 100",
    "I-17": "un segnale al giorno per direzione: sotto 100 solo se i giorni sono pochi",
    "I-18": "attraversamenti di livelli tondi: pochi con il passo scelto",
    "I-19": "chiusure entro il 2 % del massimo o del minimo a 30 giorni: poche per questa direzione",
}

for chiave, v in stime.items():
    if not v["sotto_minimo"]:
        continue
    id_scarto = f"ETHUSDT-S-{chiave}"
    if id_scarto in ids:
        continue
    aggiungi({"id": id_scarto, "tipo": "scarto", "idea": v["idea"], "nome_idea": strategie.IDEE[v["idea"]].nome,
              "fonte": strategie.FONTI[v["idea"]], "timeframe": v["timeframe"], "direzione": v["direzione"],
              "motivo": f"stima dei trade in costruzione sotto il minimo di 100: {v['trade_stimati']} ({MOTIVI[v['idea']]})",
              "stima": {k: v[k] for k in ("segnali", "trade_stimati_distanza_h", "trade_stimati_uscita_segnale", "trade_stimati", "h_barre")},
              "budget_consumato": 0,
              "nota": ("Per I-07 e I-08 le due direzioni insieme supererebbero i 100 (73+71 e 56+63): il protocollo conta le varianti per "
                       "direzione e chiede i risultati separati per direzione, quindi si scartano; l'ambiguita' va in lezioni_metodo_proposte.md."
                       if v["idea"] in ("I-07", "I-08") else None)})
    print("scarto", id_scarto, v["trade_stimati"])
