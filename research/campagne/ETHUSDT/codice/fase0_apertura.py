"""Fase 0, punto 1: note di apertura e calcolo delle date di costruzione e validazione.

Si esegue UNA volta, PRIMA di scaricare o caricare qualunque prezzo (regola del
protocollo: le date si scrivono nel log prima di caricare i prezzi). Legge solo
scheda_moneta.md e config/parametri.yaml.
"""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

import yaml

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
from log import aggiungi, leggi  # noqa: E402

RADICE = QUI.parent.parent.parent  # research/
PARAMETRI = yaml.safe_load((RADICE / "config" / "parametri.yaml").read_text(encoding="utf-8"))

# Dalla scheda della moneta (campagne/ETHUSDT/scheda_moneta.md): primo mese di dati 2020-01.
PRIMO_GIORNO_DATI = date(2020, 1, 1)
FINE_IN_SAMPLE = PARAMETRI["periodi"]["in_sample"]["fine"]
if not isinstance(FINE_IN_SAMPLE, date):
    FINE_IN_SAMPLE = date.fromisoformat(str(FINE_IN_SAMPLE))
QUOTA_COSTRUZIONE = float(PARAMETRI["regole_esame"]["divisione_costruzione_validazione"]["costruzione"])

ids = {v.get("id") for v in leggi()}

if "ETHUSDT-N001" not in ids:
    aggiungi({"id": "ETHUSDT-N001", "tipo": "nota", "oggetto": "apertura della campagna",
              "testo": ("Seconda sessione di campagna su ETHUSDT: la prima, aperta alle 08:43 UTC del 7 ott, "
                        "ha perso il lavoro per un problema di permessi del push e non ha lasciato nulla sul remoto. "
                        "Si riparte da zero dal branch principale. Marcatore research/.sessione scritto; test del "
                        "guardiano: 155 passati. Letti per intero PROTOCOLLO.md (4.3), config/parametri.yaml "
                        "(congelati il 7 ott), config/regole_dimensione.md, lezioni/metodo.md, CHANGELOG.md, "
                        "scheda_moneta.md e le docstring di src/dati.py, src/motore.py, src/statistica.py. "
                        "Esito atteso dichiarato prima di cominciare: nessuna strategia valida trovata per questa moneta.")})

if "ETHUSDT-N002" not in ids:
    aggiungi({"id": "ETHUSDT-N002", "tipo": "nota", "oggetto": "tre rifiuti del guardiano, causati da miei comandi",
              "testo": ("(1) Un comando di shell che cercava un interprete con pytest nominava la cartella .venv: "
                        "rifiutato, percorso fuori da quelli ammessi. (2) Un comando con python3 -c per verificare le "
                        "librerie installate: rifiutato, codice che il guardiano non puo' vedere. (3) Un heredoc di shell "
                        "che creava questo stesso aiutante del log: rifiutato perche' il testo con virgolette triple e' "
                        "espanso dalla shell in modo imprevedibile. Nessuno dei tre serviva alla campagna: le librerie "
                        "(pytest, pandas, numpy, pyyaml, requests) sono state installate con pip, e il codice della "
                        "campagna si scrive con lo strumento di scrittura file dentro campagne/ETHUSDT/codice/ e si "
                        "lancia per nome. Niente e' stato aggirato; segnalati all'utente nel riepilogo.")})

# --- Date di costruzione e validazione (70% / 30% dei giorni dell'in-sample) ---
giorni_totali = (FINE_IN_SAMPLE - PRIMO_GIORNO_DATI).days + 1
giorni_costruzione = round(giorni_totali * QUOTA_COSTRUZIONE)
fine_costruzione = PRIMO_GIORNO_DATI + timedelta(days=giorni_costruzione - 1)
inizio_validazione = fine_costruzione + timedelta(days=1)

if "ETHUSDT-N003" not in ids:
    aggiungi({"id": "ETHUSDT-N003", "tipo": "nota", "oggetto": "periodi di costruzione e validazione, scritti prima di caricare i prezzi",
              "fonte_date": "scheda_moneta.md (primo mese di dati 2020-01, listing 2019-11-27, archivio mensile da gennaio 2020); parametri.yaml (fine in-sample 2023-12-31, divisione 70/30)",
              "giorni_in_sample": giorni_totali,
              "costruzione": {"inizio": PRIMO_GIORNO_DATI.isoformat(), "fine": fine_costruzione.isoformat(), "giorni": giorni_costruzione},
              "validazione": {"inizio": inizio_validazione.isoformat(), "fine": FINE_IN_SAMPLE.isoformat(), "giorni": giorni_totali - giorni_costruzione},
              "testo": ("I giorni dell'in-sample si dividono 70/30 arrotondando al giorno. I mesi novembre-dicembre 2019 "
                        "(fra il listing e il primo file mensile) restano fuori, come deciso al Passo 0. Le date sono fissate "
                        "qui, prima di qualunque prezzo, e non cambiano piu'. Il periodo di validazione si tocca una sola volta, "
                        "dopo la Fase 5.")})

print("giorni in-sample:", giorni_totali)
print("costruzione:", PRIMO_GIORNO_DATI, "->", fine_costruzione, f"({giorni_costruzione} giorni)")
print("validazione:", inizio_validazione, "->", FINE_IN_SAMPLE, f"({giorni_totali - giorni_costruzione} giorni)")
