# 0010-gate-contabilita-unificata.req

_eseguito: 2026-08-19 19:37 UTC_

**richiesta:** `gate`
**eseguito:** `.venv/bin/python -m scripts.gate_progress`
**esito:** codice 0 in 1.1s

```
[firebase] connesso (Firestore + RTDB)
[gate] 2688 coppie tracciate · soglia 3 pass · un pass ogni 168h di dati nuovi
  distribuzione pass: 0 pass: 2455 · 1 pass: 233
  VALIDATE ora: 0 su 0 coin distinte
  ready dichiarato dal registro: False (via —)

--- QUANDO ARRIVANO LE PROSSIME CONFERME (limite inferiore) ---
  4USDT|gen_d8656ab7                 1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta
  AEROUSDT|gen_7648d4ee              1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta
  AKEUSDT|gen_81d3b955               1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta
  ATUSDT|gen_309b987e                1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta
  BLESSUSDT|gen_25d9f35f             1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta
  BTRUSDT|gen_46f0717f               1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta
  COOKIEUSDT|gen_74b74d76            1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta
  CYSUSDT|gen_52c3545f               1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta
  GPSUSDT|gen_9a383fff               1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta
  GUAUSDT|gen_17eca3cf               1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta
  GUAUSDT|gen_6eb91e3e               1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta
  GWEIUSDT|gen_9db57cb3              1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta
  GWEIUSDT|gen_a18d9a95              1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta
  KITEUSDT|gen_bb304862              1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta
  MUSDT|mean_reversion               1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra chiusa il 20 Aug 00:00

--- QUANDO RIPARTE IL BOT ---
  Al piu' presto il 27 Aug 00:00 (fra 7.2 giorni), quando la 10a coppia
  raggiungerebbe 3 pass.
  E' un LIMITE INFERIORE: assume che ognuna passi almeno una volta per
  finestra settimanale. Chi non passa per 2 finestre intere esce dal registro,
  quindi la data vera puo' essere piu' in la'. Serve anche coprire >= 5 coin distinte (10 coppie
  su coin diverse bastano).
```
