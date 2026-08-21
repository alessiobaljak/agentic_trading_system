# 0016-finestre-aperte.req

_eseguito: 2026-08-21 05:07 UTC_

**richiesta:** `gate`
**eseguito:** `.venv/bin/python -m scripts.gate_progress`
**esito:** codice 0 in 1.2s

```
[firebase] connesso (Firestore + RTDB)
[gate] 2807 coppie nel registro · 2246 ancora valutate · soglia 3 pass · un pass ogni 168h di dati nuovi
  distribuzione pass (solo coppie vive): 0 pass: 2046 · 1 pass: 200
  CONGELATE: 561 coppie non piu' valutate da oltre 3 giorni (49 avevano gia' un passaggio).
  La coin e' uscita dall'universo — di solito per storia insufficiente o delisting.
  Non avanzano e non falliscono: sono escluse da tutti i conti qui sotto.
  VALIDATE ora: 0 su 0 coin distinte
  ready dichiarato dal registro: False (via —)
  FINESTRE: 46/200 coppie con almeno un passaggio hanno la finestra aperta.
  Le altre 154 non stanno maturando: la finestra si apre solo quando la coppia
  ripassa il gate, e finche' non si apre non arriva ne' una conferma ne' un fallimento.

--- QUANDO ARRIVANO LE PROSSIME CONFERME (limite inferiore) ---
  4USDT|gen_d8656ab7                 1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta · vista 18 Aug 16:18
  CYSUSDT|gen_52c3545f               1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta · vista 19 Aug 19:29
  GWEIUSDT|gen_a18d9a95              1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta · vista 19 Aug 19:29
  MUSDT|mean_reversion               1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra chiusa il 20 Aug 00:00 · vista 20 Aug 12:34
  UBUSDT|gen_9a383fff                1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta · vista 19 Aug 19:29
  USUSDT|gen_d8656ab7                1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta · vista 19 Aug 19:29
  ZAMAUSDT|gen_655a47f5              1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta · vista 18 Aug 22:15
  ZAMAUSDT|gen_9a383fff              1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta · vista 19 Aug 19:29
  ZAMAUSDT|gen_9e4a3c48              1/3 pass · validata il 27 Aug 00:00 · ultimo pass 13 Aug 00:00 · finestra non ancora aperta · vista 19 Aug 19:29
  BULLAUSDT|gen_f179761a             1/3 pass · validata il 28 Aug 00:00 · ultimo pass 14 Aug 00:00 · finestra non ancora aperta · vista 18 Aug 22:15
  METUSDT|gen_b0e86c70               1/3 pass · validata il 28 Aug 00:00 · ultimo pass 14 Aug 00:00 · finestra non ancora aperta · vista 19 Aug 19:29
  PIEVERSEUSDT|gen_871647b8          1/3 pass · validata il 28 Aug 00:00 · ultimo pass 14 Aug 00:00 · finestra non ancora aperta · vista 19 Aug 19:29
  PIEVERSEUSDT|gen_9a383fff          1/3 pass · validata il 28 Aug 00:00 · ultimo pass 14 Aug 00:00 · finestra non ancora aperta · vista 19 Aug 19:29
  PIEVERSEUSDT|gen_d8656ab7          1/3 pass · validata il 28 Aug 00:00 · ultimo pass 14 Aug 00:00 · finestra non ancora aperta · vista 19 Aug 19:29
  PIEVERSEUSDT|gen_eeab48bf          1/3 pass · validata il 28 Aug 00:00 · ultimo pass 14 Aug 00:00 · finestra non ancora aperta · vista 19 Aug 19:29

--- QUANDO RIPARTE IL BOT ---
  Al piu' presto il 28 Aug 00:00 (fra 6.8 giorni), quando la 10a coppia
  raggiungerebbe 3 pass.
  E' un LIMITE INFERIORE: assume che ognuna passi almeno una volta per
  finestra settimanale. Chi non passa per 2 finestre intere esce dal registro,
  quindi la data vera puo' essere piu' in la'. Serve anche coprire >= 5 coin distinte (10 coppie
  su coin diverse bastano).
```
