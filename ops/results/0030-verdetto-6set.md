# 0030-verdetto-6set.req

_eseguito: 2026-09-06 12:56 UTC_

**richiesta:** `gate`
**eseguito:** `.venv/bin/python -m scripts.gate_progress`
**esito:** codice 0 in 1.1s

```
[firebase] connesso (Firestore + RTDB)
[gate] 2112 coppie nel registro · 1792 ancora valutate · soglia 3 pass · un pass ogni 168h di dati nuovi
  distribuzione pass (solo coppie vive): 0 pass: 1575 · 1 pass: 209 · 2 pass: 8
  CONGELATE: 320 coppie non piu' valutate da oltre 3 giorni (32 avevano gia' un passaggio).
  La coin e' uscita dall'universo — di solito per storia insufficiente o delisting.
  Non avanzano e non falliscono: sono escluse da tutti i conti qui sotto.
  COMPOSIZIONE (vive): 1576 base · 216 generate.  Nel registro intero: 1864 base su 2112, tetto 3000.
  fallimenti accumulati: 1 fallimenti: 257
  VALIDATE ora: 0 su 0 coin distinte
  ready dichiarato dal registro: False (via —)
  FINESTRE APERTE: 217/217 coppie con almeno un passaggio.
  E' QUESTO il numero da guardare: solo queste stanno contando i giorni verso la
  conferma successiva, e solo queste compaiono nel calendario qui sotto.
  Le altre 0 sono ferme: la finestra si apre solo quando la coppia RIPASSA
  il gate, quindi per loro la prossima conferma non ha una data — dipende da un
  evento che potrebbe non succedere.

--- QUANDO ARRIVANO LE PROSSIME CONFERME (limite inferiore) ---
  EGLDUSDT|gen_36b0e335              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 06 Sep 11:00
  EGLDUSDT|gen_f238d283              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 06 Sep 11:00
  MOVRUSDT|gen_4f890271              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 05 Sep 19:51
  MUSDT|mean_reversion               1/3 pass · validata il 13 Sep 00:00 · ultimo pass 13 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 03 Sep 18:41 · 1 fallimenti di fila
  ORCAUSDT|gen_271ab7ec              2/3 pass · validata il 13 Sep 00:00 · ultimo pass 06 Sep 00:00 · finestra chiusa il 13 Sep 00:00 · vista 06 Sep 11:00
  ORCAUSDT|gen_5b847426              2/3 pass · validata il 13 Sep 00:00 · ultimo pass 06 Sep 00:00 · finestra chiusa il 13 Sep 00:00 · vista 06 Sep 11:00
  ORCAUSDT|gen_6d06dca0              2/3 pass · validata il 13 Sep 00:00 · ultimo pass 06 Sep 00:00 · finestra chiusa il 13 Sep 00:00 · vista 06 Sep 11:00
  ORCAUSDT|gen_7b4a474b              2/3 pass · validata il 13 Sep 00:00 · ultimo pass 06 Sep 00:00 · finestra chiusa il 13 Sep 00:00 · vista 06 Sep 11:00
  ORCAUSDT|gen_871647b8              2/3 pass · validata il 13 Sep 00:00 · ultimo pass 06 Sep 00:00 · finestra chiusa il 13 Sep 00:00 · vista 06 Sep 11:00
  ORCAUSDT|gen_8a66a70b              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 06 Sep 11:00
  ORCAUSDT|gen_9a383fff              2/3 pass · validata il 13 Sep 00:00 · ultimo pass 06 Sep 00:00 · finestra chiusa il 13 Sep 00:00 · vista 06 Sep 11:00
  ORCAUSDT|gen_bbe21d3f              2/3 pass · validata il 13 Sep 00:00 · ultimo pass 06 Sep 00:00 · finestra chiusa il 13 Sep 00:00 · vista 06 Sep 11:00
  ORCAUSDT|gen_cb8176f2              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 06 Sep 11:00
  ORCAUSDT|gen_e6ddc613              2/3 pass · validata il 13 Sep 00:00 · ultimo pass 06 Sep 00:00 · finestra chiusa il 13 Sep 00:00 · vista 06 Sep 11:00
  STXUSDT|gen_14e1775b               1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 06 Sep 11:00

--- QUANDO RIPARTE IL BOT ---
  Al piu' presto il 13 Sep 00:00 (fra 6.5 giorni), quando la 10a coppia
  raggiungerebbe 3 pass.
  E' un LIMITE INFERIORE: assume che ognuna passi almeno una volta per
  finestra settimanale. Chi non passa per 2 finestre intere esce dal registro,
  quindi la data vera puo' essere piu' in la'. Serve anche coprire >= 5 coin distinte (10 coppie
  su coin diverse bastano).
```
