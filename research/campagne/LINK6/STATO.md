# Stato della ricerca LINK6 (protocollo 4)

Protocollo: `research/PROTOCOLLO_4.md` (versione 6, approvata dal proprietario il 17 ottobre 2026 alle 20:12 UTC).

- **Passo corrente:** Passo 1 (dati di LINKUSDT) eseguito; in attesa della conferma del proprietario allo STOP del
  Passo 1.
- **Passi completati:** Passo 0 (preparazione e collaudo del metodo, dal coordinamento sul branch principale), esiti
  approvati con la delega del proprietario del 17 ottobre 2026 (21:10 UTC). Strumenti e parametri congelati: impronte
  in `research/collaudo_4/esiti/giro1/impronte.json` (non sono sul branch della ricerca; il coordinamento le controlla).
  Passo 1 eseguito il 17 ottobre 2026 (fatti in `fase0_dati.md`, voce N-002 del log), da confermare.
- **Varianti usate:** 0 su 40.
- **Candidati:** nessuno.
- **Prossima azione:** dopo la conferma del Passo 1, Passo 2 (Fase 1: prime ipotesi in `ipotesi.md`).
- **Problemi aperti:**
  - le prime candele last a 6h (06:00), 12h e 1d (00:00) del 2020-01-17 aprono prima dell'inizio della costruzione
    scritto in `parametri_4.yaml` (08:00); domanda posta al proprietario;
  - la guida pratica (sezione 2, punto 4) indica `python3 -c` per la versione di numpy, che il guardiano rifiuta;
    le versioni si leggono con `codice/versioni.py` (voce N-001 del log). Da segnalare al coordinamento.
