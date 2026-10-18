# Via libera alla validazione (protocollo 3, regola 2 e Passo 3)

Scritto dal coordinamento il 17 ottobre 2026 alle 13:39 UTC, dopo il sì del proprietario in chat: «sì procedi con la
validazione». Toglie il blocco della regola 2 al caricatore (`research/src/dati.py`, `controlla_validazione`).

- **Candidati da validare, tutti insieme e una volta sola:** V-020 (l'unico; V-030 ha superato la Fase 2 ma non la
  Fase 4).
- **Varianti usate:** 40 su 40. Da qui non si costruiscono nuovi candidati (regola 9).
- **Verifica del coordinamento prima del via libera** (sul branch al commit `be5c28e0`): strumenti identici al quarto
  giro del collaudo (`research/collaudo_3/esiti/giro4/impronte.json`); nel registro 40 varianti numerate senza salti,
  ognuna registrata prima del suo risultato, con fonte e ipotesi; tutte le prove sul periodo di costruzione; nessun
  uso di dati della validazione oltre ai conteggi del Passo 1.
- **Impronte SHA-256 dei file del candidato al momento del via libera** (il Passo 3 le riscrive in `validazione.md`:
  devono coincidere):
  - `candidati/V-020/regole.md`: `7eb2cc234a8dc6a64d09bb310c46968309e3b6b0532559cb95a0f28b39d129f7`
  - `codice/lotto_2.json`: `dfb3695b8b2d0aebe3236beab610f07f7bc394df00a2c86fed49f5e4fdfa8232`
  - `codice/lotto.py`: `455b5ca3a16e9c308b0de5625ea1943cf31abb342de3f063f1c5bf13d714a91f`
  - `codice/registro.py`: `fe3d7a140092fc887e0abd8042c40896c4402cc1ead5c15606f5bd72dc08b1ab`
- **Periodo:** dal 2022-10-01 00:00 al 2023-12-31 23:59 UTC. Il vault resta chiuso.
