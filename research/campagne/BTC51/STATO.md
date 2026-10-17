# Stato della ricerca BTC51 (protocollo 3)

Protocollo: `research/PROTOCOLLO_3.md` (versione 5.1 su BTC, approvata dal proprietario il 16 ottobre 2026 alle
19:26 UTC).

- **Passo corrente:** Passo 1 eseguito il 17 ottobre 2026 dalla sessione di ricerca; in attesa della conferma
  dell'utente (STOP del Passo 1).
- **Passi completati:** Passo 0 (preparazione e collaudo del metodo, dal coordinamento sul branch principale);
  esiti approvati dal proprietario il 17 ottobre 2026 alle 07:15 UTC («Sì apri la sessione»). Strumenti e
  parametri congelati: impronte del **quarto giro** del collaudo, `research/collaudo_3/esiti/giro4/impronte.json`
  (dopo la correzione della sezione 9.6 e la tolleranza dei pareggi del p-value; non sono sul branch della
  ricerca, le controlla il coordinamento). Test del protocollo 3 su questa macchina il 17 ottobre: 628 passati.
- **Dati:** `fase0_dati.md` (prima candela 2020-01-01 00:00 UTC, buchi del mark, funding, volume 2023, impronte
  dei 912 file). A ogni nuova sessione: `python3 research/campagne/BTC51/codice/passo1_impronte.py verifica`.
- **Varianti usate:** 0 su 40.
- **Candidati:** nessuno.
- **Prossima azione:** Passo 2 (ipotesi in `ipotesi.md`, poi stime e test).
- **Problemi aperti:** nessuno. Chiusi il 17 ottobre: i buchi del mark (sezione 9.6 corretta, `fase0_dati.md`,
  sezione 3) e i pareggi del p-value (tolleranza di un miliardesimo di R in `statistica3.p_value`, collaudo
  rifatto con python 3.13.16 e numpy 2.5.3).
