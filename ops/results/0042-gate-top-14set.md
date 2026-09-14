# 0042-gate-top-14set.req

_eseguito: 2026-09-14 05:14 UTC_

**richiesta:** `gate-top`
**eseguito:** `.venv/bin/python -m scripts.gate_progress --top 40`
**esito:** codice 0 in 1.3s

```
[firebase] connesso (Firestore + RTDB)
[gate] 2380 coppie nel registro · 2133 ancora valutate · soglia 3 pass · un pass ogni 168h di dati nuovi
  distribuzione pass (solo coppie vive): 0 pass: 1752 su 219 coin · 1 pass: 277 su 89 coin · 2 pass: 104 su 40 coin
  CONGELATE: 247 coppie non piu' valutate da oltre 3 giorni (23 avevano gia' un passaggio).
  La coin e' uscita dall'universo — di solito per storia insufficiente o delisting.
  Non avanzano e non falliscono: sono escluse da tutti i conti qui sotto.
  COMPOSIZIONE (vive): 1752 base · 381 generate.  Nel registro intero: 1976 base su 2380, tetto 3000.
  fallimenti accumulati: 1 fallimenti: 968
  VALIDATE ora: 0 su 0 coin distinte
  ready dichiarato dal registro: False (via —)
  FINESTRE APERTE: 381/381 coppie con almeno un passaggio.
  E' QUESTO il numero da guardare: solo queste stanno contando i giorni verso la
  conferma successiva, e solo queste compaiono nel calendario qui sotto.
  Le altre 0 sono ferme: la finestra si apre solo quando la coppia RIPASSA
  il gate, quindi per loro la prossima conferma non ha una data — dipende da un
  evento che potrebbe non succedere.

  RI-VALUTAZIONE (ultimo run discovery): 339 spec su 339 note · cap 500 · 236 con almeno una conferma

--- QUANDO ARRIVANO LE PROSSIME CONFERME (limite inferiore) ---
  EGLDUSDT|gen_f238d283              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 14 Sep 02:24
  MOVRUSDT|gen_4f890271              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 14 Sep 02:24
  ORCAUSDT|gen_271ab7ec              2/3 pass · validata il 13 Sep 00:00 · ultimo pass 06 Sep 00:00 · finestra chiusa il 13 Sep 00:00 · vista 13 Sep 08:36
  ORCAUSDT|gen_5b847426              2/3 pass · validata il 13 Sep 00:00 · ultimo pass 06 Sep 00:00 · finestra chiusa il 13 Sep 00:00 · vista 13 Sep 08:36
  ORCAUSDT|gen_6d06dca0              2/3 pass · validata il 13 Sep 00:00 · ultimo pass 06 Sep 00:00 · finestra chiusa il 13 Sep 00:00 · vista 13 Sep 08:36
  ORCAUSDT|gen_7b4a474b              2/3 pass · validata il 13 Sep 00:00 · ultimo pass 06 Sep 00:00 · finestra chiusa il 13 Sep 00:00 · vista 13 Sep 08:36
  ORCAUSDT|gen_871647b8              2/3 pass · validata il 13 Sep 00:00 · ultimo pass 06 Sep 00:00 · finestra chiusa il 13 Sep 00:00 · vista 13 Sep 08:36
  ORCAUSDT|gen_9a383fff              2/3 pass · validata il 13 Sep 00:00 · ultimo pass 06 Sep 00:00 · finestra chiusa il 13 Sep 00:00 · vista 13 Sep 08:36
  ORCAUSDT|gen_bbe21d3f              2/3 pass · validata il 13 Sep 00:00 · ultimo pass 06 Sep 00:00 · finestra chiusa il 13 Sep 00:00 · vista 13 Sep 08:36
  ORCAUSDT|gen_e6ddc613              2/3 pass · validata il 13 Sep 00:00 · ultimo pass 06 Sep 00:00 · finestra chiusa il 13 Sep 00:00 · vista 13 Sep 08:36
  ZORAUSDT|gen_f4e37ccc              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 14 Sep 02:24
  ZORAUSDT|gen_fec39d1f              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 14 Sep 02:24
  AXSUSDT|gen_b922252e               2/3 pass · validata il 14 Sep 00:00 · ultimo pass 07 Sep 00:00 · finestra chiusa il 14 Sep 00:00 · vista 14 Sep 02:24
  BTRUSDT|gen_46f0717f               1/3 pass · validata il 14 Sep 00:00 · ultimo pass 31 Aug 00:00 · finestra chiusa il 07 Sep 00:00 · vista 14 Sep 02:24
  DOTUSDT|gen_282e8a0f               1/3 pass · validata il 14 Sep 00:00 · ultimo pass 31 Aug 00:00 · finestra chiusa il 07 Sep 00:00 · vista 14 Sep 02:24
  DOTUSDT|gen_36b0e335               1/3 pass · validata il 14 Sep 00:00 · ultimo pass 31 Aug 00:00 · finestra chiusa il 07 Sep 00:00 · vista 14 Sep 02:24
  DOTUSDT|gen_cb22084e               1/3 pass · validata il 14 Sep 00:00 · ultimo pass 31 Aug 00:00 · finestra chiusa il 07 Sep 00:00 · vista 14 Sep 02:24
  EGLDUSDT|gen_36b0e335              2/3 pass · validata il 14 Sep 00:00 · ultimo pass 07 Sep 00:00 · finestra chiusa il 14 Sep 00:00 · vista 14 Sep 02:24
  EIGENUSDT|gen_820b01f4             1/3 pass · validata il 14 Sep 00:00 · ultimo pass 31 Aug 00:00 · finestra chiusa il 07 Sep 00:00 · vista 14 Sep 02:24
  ENAUSDT|gen_bb762669               1/3 pass · validata il 14 Sep 00:00 · ultimo pass 31 Aug 00:00 · finestra chiusa il 07 Sep 00:00 · vista 14 Sep 02:24
  HEIUSDT|gen_871647b8               1/3 pass · validata il 14 Sep 00:00 · ultimo pass 31 Aug 00:00 · finestra chiusa il 07 Sep 00:00 · vista 11 Sep 14:09
  HEIUSDT|gen_9a383fff               1/3 pass · validata il 14 Sep 00:00 · ultimo pass 31 Aug 00:00 · finestra chiusa il 07 Sep 00:00 · vista 11 Sep 14:09
  KAITOUSDT|gen_d2dc954d             1/3 pass · validata il 14 Sep 00:00 · ultimo pass 31 Aug 00:00 · finestra chiusa il 07 Sep 00:00 · vista 14 Sep 02:24
  PLUMEUSDT|gen_1c0d9942             1/3 pass · validata il 14 Sep 00:00 · ultimo pass 31 Aug 00:00 · finestra chiusa il 07 Sep 00:00 · vista 12 Sep 08:11
  PLUMEUSDT|gen_a32bee42             1/3 pass · validata il 14 Sep 00:00 · ultimo pass 31 Aug 00:00 · finestra chiusa il 07 Sep 00:00 · vista 12 Sep 08:11
  SCRUSDT|gen_452d4511               1/3 pass · validata il 14 Sep 00:00 · ultimo pass 31 Aug 00:00 · finestra chiusa il 07 Sep 00:00 · vista 14 Sep 02:24
  SPXUSDT|gen_b8abf2b0               1/3 pass · validata il 14 Sep 00:00 · ultimo pass 31 Aug 00:00 · finestra chiusa il 07 Sep 00:00 · vista 13 Sep 05:11
  STXUSDT|gen_14e1775b               2/3 pass · validata il 14 Sep 00:00 · ultimo pass 07 Sep 00:00 · finestra chiusa il 14 Sep 00:00 · vista 14 Sep 02:24
  STXUSDT|gen_acfd527a               2/3 pass · validata il 14 Sep 00:00 · ultimo pass 07 Sep 00:00 · finestra chiusa il 14 Sep 00:00 · vista 14 Sep 02:24
  STXUSDT|gen_b9bf5d01               2/3 pass · validata il 14 Sep 00:00 · ultimo pass 07 Sep 00:00 · finestra chiusa il 14 Sep 00:00 · vista 14 Sep 02:24
  USELESSUSDT|gen_98837ec2           1/3 pass · validata il 14 Sep 00:00 · ultimo pass 31 Aug 00:00 · finestra chiusa il 07 Sep 00:00 · vista 14 Sep 02:24
  USELESSUSDT|gen_c61d9322           1/3 pass · validata il 14 Sep 00:00 · ultimo pass 31 Aug 00:00 · finestra chiusa il 07 Sep 00:00 · vista 14 Sep 02:24
  USELESSUSDT|gen_e09c5203           1/3 pass · validata il 14 Sep 00:00 · ultimo pass 31 Aug 00:00 · finestra chiusa il 07 Sep 00:00 · vista 14 Sep 02:24
  XMRUSDT|gen_2f405402               1/3 pass · validata il 14 Sep 00:00 · ultimo pass 31 Aug 00:00 · finestra chiusa il 07 Sep 00:00 · vista 14 Sep 02:24
  XMRUSDT|gen_a220b439               1/3 pass · validata il 14 Sep 00:00 · ultimo pass 31 Aug 00:00 · finestra chiusa il 07 Sep 00:00 · vista 14 Sep 02:24
  XPLUSDT|gen_b437a671               1/3 pass · validata il 14 Sep 00:00 · ultimo pass 31 Aug 00:00 · finestra chiusa il 07 Sep 00:00 · vista 14 Sep 02:24
  BICOUSDT|gen_f238d283              2/3 pass · validata il 15 Sep 00:00 · ultimo pass 08 Sep 00:00 · finestra chiusa il 15 Sep 00:00 · vista 14 Sep 02:24
  DEXEUSDT|gen_fa304106              2/3 pass · validata il 15 Sep 00:00 · ultimo pass 08 Sep 00:00 · finestra chiusa il 15 Sep 00:00 · vista 14 Sep 02:24
  DOTUSDT|gen_1623b4cb               2/3 pass · validata il 15 Sep 00:00 · ultimo pass 08 Sep 00:00 · finestra chiusa il 15 Sep 00:00 · vista 14 Sep 02:24
  DOTUSDT|gen_48ffc057               2/3 pass · validata il 15 Sep 00:00 · ultimo pass 08 Sep 00:00 · finestra chiusa il 15 Sep 00:00 · vista 14 Sep 02:24

--- QUANDO RIPARTE IL BOT ---
  Al piu' presto il 13 Sep 00:00 (fra -1.2 giorni), quando la 10a coppia
  raggiungerebbe 3 pass.
  E' un LIMITE INFERIORE: assume che ognuna passi almeno una volta per
  finestra settimanale. Chi non passa per 2 finestre intere esce dal registro,
  quindi la data vera puo' essere piu' in la'. Serve anche coprire >= 5 coin distinte (10 coppie
  su coin diverse bastano).
```
