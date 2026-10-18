# Stato della ricerca LINK6 (protocollo 4)

Protocollo: `research/PROTOCOLLO_4.md` (versione 6, approvata dal proprietario il 17 ottobre 2026 alle 20:12 UTC).

- **Passo corrente:** Passo 2 (ricerca sul periodo di costruzione), in corso.
- **Passi completati:**
  - Passo 0 (preparazione e collaudo del metodo, dal coordinamento sul branch principale), esiti approvati con la
    delega del proprietario del 17 ottobre 2026 (21:10 UTC). Strumenti e parametri congelati: impronte in
    `research/collaudo_4/esiti/giro1/impronte.json` (non sono sul branch della ricerca; il coordinamento le controlla).
  - Passo 1 (dati di LINKUSDT), confermato dal coordinamento il 17 ottobre e dal proprietario in questa sessione il
    18 ottobre 2026 (voce N-004 del log). Fatti in `fase0_dati.md`.
  - Delega: il proprietario ha scritto il 18 ottobre 2026 che il coordinamento puo' confermare gli STOP della
    ricerca al posto suo, tranne il vault (voce N-004).
- **Varianti usate:** 26 su 40 (V-001 ... V-018, V-020 ... V-027), piu' V-019 in attesa.
- **Candidati:** nessuno. Nessuna delle 26 varianti supera la Fase 2 (riepilogo: `codice/riepilogo.py`).
- **In attesa:** risposta del coordinamento alla richiesta R-001 (`richieste/R-001.json`): controllo sulle monete di
  controllo di V-019, nata dalla Fase 3 da V-004 (uscita a tempo 48 candele invece di 24). Se il controllo passa,
  V-019 va in Fase 2; se no, e' uno scarto che consuma il tentativo.
- **Prossima azione:** dopo la risposta su R-001, Fase 5 (sfida alla conclusione) e STOP del Passo 2 con il riepilogo.
- **Come si lavora:** ipotesi in `ipotesi.md`; varianti in `codice/lotto_*.json`; stima dei trade con
  `codice/stima.py`; Fase 2 con `codice/fase2.py` (registra nel log prima del test); trade di ogni variante in
  `risultati/`; analisi della Fase 3 con `codice/fase3_analisi.py`; richieste al coordinamento con `codice/richiesta.py`.
- **Problemi aperti:**
  - la guida pratica e' stata corretta dal coordinamento sul `python3 -c` (commit a0f5b8a); chiuso.
  - nessun altro.
