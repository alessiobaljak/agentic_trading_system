# Stato della ricerca BTC51 (protocollo 3)

Protocollo: `research/PROTOCOLLO_3.md` (versione 5.1 su BTC, approvata dal proprietario il 16 ottobre 2026 alle
19:26 UTC).

- **Passo corrente:** STOP del Passo 4. Il vault si apre solo con la frase esatta del proprietario «APRI IL VAULT 3»;
  poi il Passo 5 lo fa il coordinamento sul branch principale.
- **Passi completati:** Passo 0 (coordinamento; impronte degli strumenti in
  `research/collaudo_3/esiti/giro4/impronte.json`); Passi 1-4 (sessione di ricerca sul branch
  `research/campagna/BTC51`, consegna nel commit 1b222fb5 del 17 ottobre 2026, 15:44 UTC).
- **Varianti usate:** 40 su 40.
- **Candidati:** uno, V-020 (1h, long nei giorni feriali quando il funding regolato e' sotto zero, stop a 2 ATR,
  uscita dopo 24 candele). Validazione superata: 80 trade, +0,167 R, profit factor 1,29, +0,064 R a costi doppi
  (`research/campagne/BTC51/validazione.md` sul branch della ricerca).
- **Previsione della sessione per il vault, scritta prima dell'apertura** (`consegna.md`, sezione 6): circa 175 trade
  (110-230), +0,08 R a trade (da -0,10 a +0,20), probabilita' di superarlo circa 1 su 4.
- **Verifica del coordinamento allo STOP (17 ottobre, 15:46 UTC):** gli strumenti, il protocollo, i parametri e il
  collaudo sul branch della ricerca hanno le 9 impronte del quarto giro; una sola esecuzione di validazione nel log.
- **Prossima azione:** decisione del proprietario sul vault.
- **Problemi aperti:** nessuno.
