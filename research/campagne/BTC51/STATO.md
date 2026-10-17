# Stato della ricerca BTC51 (protocollo 3)

Protocollo: `research/PROTOCOLLO_3.md` (versione 5.1 su BTC, approvata dal proprietario il 16 ottobre 2026 alle
19:26 UTC; correzioni del 17 ottobre nell'appendice 3).

- **Passo corrente:** Passo 3 (validazione) eseguito il 17 ottobre 2026; **STOP del Passo 3**: in attesa dell'utente.
  Poi Passo 4 (consegna, `consegna.md`); il vault si apre solo con «APRI IL VAULT 3».
- **Passi completati:** Passo 0 (coordinamento; impronte del quarto giro del collaudo in
  `research/collaudo_3/esiti/giro4/impronte.json`, non su questo branch); Passo 1 (`fase0_dati.md`); Passo 2;
  Passo 3 (`validazione.md`): **V-020 supera la validazione** (80 trade, R medio +0,167, profit factor 1,29, costi
  doppi +0,064).
- **Dati:** a ogni nuova sessione `python3 research/campagne/BTC51/codice/passo1_impronte.py verifica` (deve
  stampare «IMPRONTE UGUALI»; ultimo controllo 17 ottobre: uguali).
- **Varianti usate:** 40 su 40 (V-001 … V-040). Il limite è raggiunto: nessuna variante nuova.
- **Candidati:** uno, **V-020** (`candidati/V-020/regole.md`): 1h, long, solo giorni feriali, funding sotto 0,00%,
  stop 2 × ATR, uscita dopo 24 candele. Costruzione: 180 trade, R medio +0,223, p-value 0,017; Fase 4 superata.
  Debole: senza i 9 trade migliori +0,012; la scelta dei feriali nasce dai dati di V-012; con 40 varianti il caso da
  solo darebbe circa 0,9 candidati.
- **Superano la Fase 2 ma non la Fase 4:** V-030 (verifiche 2, 3 e 4).
- **Prossima azione:** Passo 4, scrivere `consegna.md` per V-020 (specifica, metriche affiancate, verifiche, previsione
  per il vault, trade al mese attesi in paper). Nessun nuovo candidato (regola 9).
- **Problemi aperti:** nessuno. Da riportare: la verifica di robustezza non può spostare una soglia del funding pari
  a 0,00% (±20% di zero è zero), quindi su V-020 non ha messo alla prova il segnale d'ingresso.
- **Strumenti della campagna:** `codice/lotto.py` (stime, Fase 2, Fase 4, tutto registrato nel log),
  `codice/fase3_analisi.py`, `codice/registro.py`.
