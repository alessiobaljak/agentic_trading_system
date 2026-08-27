# 0021-gate-27ago.req

_eseguito: 2026-08-27 01:20 UTC_

**richiesta:** `gate`
**eseguito:** `.venv/bin/python -m scripts.gate_progress`
**esito:** codice 0 in 1.1s

```
[firebase] connesso (Firestore + RTDB)
[gate] 2992 coppie nel registro · 1720 ancora valutate · soglia 3 pass · un pass ogni 168h di dati nuovi
  distribuzione pass (solo coppie vive): 0 pass: 1583 · 1 pass: 137
  CONGELATE: 1272 coppie non piu' valutate da oltre 3 giorni (1 avevano gia' un passaggio).
  La coin e' uscita dall'universo — di solito per storia insufficiente o delisting.
  Non avanzano e non falliscono: sono escluse da tutti i conti qui sotto.
  VALIDATE ora: 0 su 0 coin distinte
  ready dichiarato dal registro: False (via —)
  FINESTRE: 42/137 coppie con almeno un passaggio hanno la finestra aperta.
  Le altre 95 non stanno maturando: la finestra si apre solo quando la coppia
  ripassa il gate, e finche' non si apre non arriva ne' una conferma ne' un fallimento.

--- QUANDO ARRIVANO LE PROSSIME CONFERME (limite inferiore) ---
  AEROUSDT|gen_7648d4ee              1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta · vista 26 Aug 22:33
  CYSUSDT|gen_52c3545f               1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta · vista 26 Aug 22:33
  GPSUSDT|gen_9a383fff               1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta · vista 26 Aug 22:33
  UBUSDT|gen_9a383fff                1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta · vista 26 Aug 22:33
  USUSDT|gen_d8656ab7                1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta · vista 26 Aug 22:33
  ZAMAUSDT|gen_655a47f5              1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta · vista 26 Aug 22:33
  ZAMAUSDT|gen_9a383fff              1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta · vista 26 Aug 22:33
  ZAMAUSDT|gen_9e4a3c48              1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta · vista 26 Aug 22:33
  AKEUSDT|gen_84fdca78               1/3 pass · validata il 29 Aug 00:00 · ultimo pass 15 Aug 00:00 · finestra non ancora aperta · vista 26 Aug 22:33
  BEATUSDT|gen_7b17b6ef              1/3 pass · validata il 29 Aug 00:00 · ultimo pass 15 Aug 00:00 · finestra non ancora aperta · vista 26 Aug 22:33
  BLESSUSDT|gen_18450442             1/3 pass · validata il 29 Aug 00:00 · ultimo pass 15 Aug 00:00 · finestra non ancora aperta · vista 26 Aug 22:33
  BLESSUSDT|gen_b0e86c70             1/3 pass · validata il 29 Aug 00:00 · ultimo pass 15 Aug 00:00 · finestra non ancora aperta · vista 26 Aug 22:33
  BLESSUSDT|gen_f2897958             1/3 pass · validata il 29 Aug 00:00 · ultimo pass 15 Aug 00:00 · finestra non ancora aperta · vista 26 Aug 22:33
  BLESSUSDT|gen_f3b97917             1/3 pass · validata il 29 Aug 00:00 · ultimo pass 15 Aug 00:00 · finestra non ancora aperta · vista 26 Aug 22:33
  CYSUSDT|gen_00d07a5d               1/3 pass · validata il 29 Aug 00:00 · ultimo pass 15 Aug 00:00 · finestra non ancora aperta · vista 26 Aug 22:33

--- QUANDO RIPARTE IL BOT ---
  Al piu' presto il 29 Aug 00:00 (fra 1.9 giorni), quando la 10a coppia
  raggiungerebbe 3 pass.
  E' un LIMITE INFERIORE: assume che ognuna passi almeno una volta per
  finestra settimanale. Chi non passa per 2 finestre intere esce dal registro,
  quindi la data vera puo' essere piu' in la'. Serve anche coprire >= 5 coin distinte (10 coppie
  su coin diverse bastano).
```
