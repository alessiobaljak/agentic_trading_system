# 0013-gate-21ago.req

_eseguito: 2026-08-21 04:58 UTC_

**richiesta:** `gate`
**eseguito:** `.venv/bin/python -m scripts.gate_progress`
**esito:** codice 0 in 1.2s

```
[firebase] connesso (Firestore + RTDB)
[gate] 2807 coppie tracciate · soglia 3 pass · un pass ogni 168h di dati nuovi
  distribuzione pass: 0 pass: 2558 · 1 pass: 249
  VALIDATE ora: 0 su 0 coin distinte
  ready dichiarato dal registro: False (via —)

--- QUANDO ARRIVANO LE PROSSIME CONFERME (limite inferiore) ---
  4USDT|gen_d8656ab7                 1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta
  AEROUSDT|gen_7648d4ee              1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta
  ATUSDT|gen_309b987e                1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta
  BTRUSDT|gen_46f0717f               1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta
  COOKIEUSDT|gen_74b74d76            1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta
  CYSUSDT|gen_52c3545f               1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta
  GPSUSDT|gen_9a383fff               1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta
  GUAUSDT|gen_17eca3cf               1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta
  GUAUSDT|gen_6eb91e3e               1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta
  GWEIUSDT|gen_a18d9a95              1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta
  KITEUSDT|gen_bb304862              1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta
  MUSDT|mean_reversion               1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra chiusa il 20 Aug 00:00
  UBUSDT|gen_9a383fff                1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta
  USUSDT|gen_d8656ab7                1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta
  ZAMAUSDT|gen_655a47f5              1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta

--- QUANDO RIPARTE IL BOT ---
  Al piu' presto il 27 Aug 00:00 (fra 5.8 giorni), quando la 10a coppia
  raggiungerebbe 3 pass.
  E' un LIMITE INFERIORE: assume che ognuna passi almeno una volta per
  finestra settimanale. Chi non passa per 2 finestre intere esce dal registro,
  quindi la data vera puo' essere piu' in la'. Serve anche coprire >= 5 coin distinte (10 coppie
  su coin diverse bastano).
```
