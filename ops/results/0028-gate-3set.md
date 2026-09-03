# 0028-gate-3set.req

_eseguito: 2026-09-03 09:45 UTC_

**richiesta:** `gate`
**eseguito:** `.venv/bin/python -m scripts.gate_progress`
**esito:** codice 0 in 1.3s

```
[firebase] connesso (Firestore + RTDB)
[gate] 2064 coppie nel registro · 1736 ancora valutate · soglia 3 pass · un pass ogni 168h di dati nuovi
  distribuzione pass (solo coppie vive): 0 pass: 1558 · 1 pass: 178
  CONGELATE: 328 coppie non piu' valutate da oltre 3 giorni (0 avevano gia' un passaggio).
  La coin e' uscita dall'universo — di solito per storia insufficiente o delisting.
  Non avanzano e non falliscono: sono escluse da tutti i conti qui sotto.
  COMPOSIZIONE (vive): 1560 base · 176 generate.  Nel registro intero: 1888 base su 2064, tetto 3000.
  fallimenti accumulati: 1 fallimenti: 985
  VALIDATE ora: 0 su 0 coin distinte
  ready dichiarato dal registro: False (via —)
  FINESTRE APERTE: 178/178 coppie con almeno un passaggio.
  E' QUESTO il numero da guardare: solo queste stanno contando i giorni verso la
  conferma successiva, e solo queste compaiono nel calendario qui sotto.
  Le altre 0 sono ferme: la finestra si apre solo quando la coppia RIPASSA
  il gate, quindi per loro la prossima conferma non ha una data — dipende da un
  evento che potrebbe non succedere.

--- QUANDO ARRIVANO LE PROSSIME CONFERME (limite inferiore) ---
  MUBARAKUSDT|mean_reversion         1/3 pass · validata il 12 Sep 00:00 · ultimo pass 21 Aug 00:00 · finestra chiusa il 05 Sep 00:00 · vista 03 Sep 09:41 · 1 fallimenti di fila
  EGLDUSDT|gen_36b0e335              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 03 Sep 08:30
  EGLDUSDT|gen_f238d283              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 03 Sep 08:30
  HUMAUSDT|gen_282e8a0f              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 01 Sep 22:53
  HUMAUSDT|gen_36b0e335              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 01 Sep 22:53
  HUMAUSDT|gen_4c4dac5f              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 01 Sep 22:53
  HUMAUSDT|gen_4d7f7bd3              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 01 Sep 22:53
  HUMAUSDT|gen_6d06dca0              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 01 Sep 22:53
  HUMAUSDT|gen_771790b1              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 01 Sep 22:53
  HUMAUSDT|gen_919c110c              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 01 Sep 22:53
  HUMAUSDT|gen_a32bee42              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 01 Sep 22:53
  HUMAUSDT|gen_b2f350ff              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 01 Sep 22:53
  HUMAUSDT|gen_b9c251a1              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 01 Sep 22:53
  HUMAUSDT|gen_cb22084e              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 01 Sep 22:53
  HUMAUSDT|gen_cbcb5ac9              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 01 Sep 22:53

--- QUANDO RIPARTE IL BOT ---
  Al piu' presto il 13 Sep 00:00 (fra 9.6 giorni), quando la 10a coppia
  raggiungerebbe 3 pass.
  E' un LIMITE INFERIORE: assume che ognuna passi almeno una volta per
  finestra settimanale. Chi non passa per 2 finestre intere esce dal registro,
  quindi la data vera puo' essere piu' in la'. Serve anche coprire >= 5 coin distinte (10 coppie
  su coin diverse bastano).
```
