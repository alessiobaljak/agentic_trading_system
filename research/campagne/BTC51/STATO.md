# Stato della ricerca BTC51 (protocollo 3)

Protocollo: `research/PROTOCOLLO_3.md` (versione 5.1 su BTC, approvata dal proprietario il 16 ottobre 2026 alle
19:26 UTC).

- **Passo corrente:** Passo 1 eseguito il 17 ottobre 2026 dalla sessione di ricerca; in attesa della conferma
  dell'utente (STOP del Passo 1).
- **Passi completati:** Passo 0 (preparazione e collaudo del metodo, dal coordinamento sul branch principale);
  esiti approvati dal proprietario il 17 ottobre 2026 alle 07:15 UTC («Sì apri la sessione»). Strumenti e
  parametri congelati: impronte in `research/collaudo_3/esiti/giro2/impronte.json` (non sono sul branch della
  ricerca; il coordinamento le controlla).
- **Dati:** `fase0_dati.md` (prima candela 2020-01-01 00:00 UTC, buchi del mark, funding, volume 2023, impronte
  dei 912 file). A ogni nuova sessione: `python3 research/campagne/BTC51/codice/passo1_impronte.py verifica`.
- **Varianti usate:** 0 su 40.
- **Candidati:** nessuno.
- **Prossima azione:** dopo la conferma dell'utente, Passo 2 (ipotesi in `ipotesi.md`, poi stime e test).
- **Problemi aperti:** nessuno. Da sapere: i buchi del mark in costruzione fanno ripartire il riscaldamento e
  tolgono gran parte della costruzione agli indicatori lenti sulle candele lunghe (`fase0_dati.md`, sezione 3).
