# 0051-conferma-riaggiunta.req

_eseguito: 2026-09-14 07:50 UTC_

**richiesta:** `gate`
**eseguito:** `.venv/bin/python -m scripts.gate_progress`
**esito:** codice 0 in 1.3s

```
[firebase] connesso (Firestore + RTDB)
[gate] 2390 coppie nel registro · 2128 ancora valutate · soglia 3 pass · un pass ogni 168h di dati nuovi
  distribuzione pass (solo coppie vive): 0 pass: 1744 su 218 coin · 1 pass: 280 su 89 coin · 2 pass: 104 su 40 coin
  CONGELATE: 262 coppie non piu' valutate da oltre 3 giorni (22 avevano gia' un passaggio).
  La coin e' uscita dall'universo — di solito per storia insufficiente o delisting.
  Non avanzano e non falliscono: sono escluse da tutti i conti qui sotto.
  COMPOSIZIONE (vive): 1744 base · 384 generate.  Nel registro intero: 1984 base su 2390, tetto 3000.
  fallimenti accumulati: 1 fallimenti: 968
  VALIDATE ora: 0 su 0 coin distinte
  ready dichiarato dal registro: False (via —)
  FINESTRE APERTE: 384/384 coppie con almeno un passaggio.
  E' QUESTO il numero da guardare: solo queste stanno contando i giorni verso la
  conferma successiva, e solo queste compaiono nel calendario qui sotto.
  Le altre 0 sono ferme: la finestra si apre solo quando la coppia RIPASSA
  il gate, quindi per loro la prossima conferma non ha una data — dipende da un
  evento che potrebbe non succedere.

  A UN PASSO DALLA VALIDAZIONE: 104 coppie a 2/3.
  Di queste, 13 su 4 coin hanno GIA' la finestra scaduta: si
  validano al primo run in cui ripassano il gate, cioe' potenzialmente oggi.
  Le altre diventano idonee: 46 il 15 Sep 00:00 · 2 il 16 Sep 00:00 · 14 il 17 Sep 00:00 · 2 il 18 Sep 00:00 · 11 il 19 Sep 00:00 · 4 il 20 Sep 00:00 · 12 il 21 Sep 00:00
  spazio registro: 636 KiB su 879 (72%)
  spazio spec scoperte: 74 KiB su 879 (8%)

  RI-VALUTAZIONE (ultimo run discovery): 341 spec su 341 note · cap 500 · 238 con almeno una conferma

--- QUANDO ARRIVANO LE PROSSIME CONFERME (limite inferiore) ---
  EGLDUSDT|gen_f238d283              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 14 Sep 05:20
  MOVRUSDT|gen_4f890271              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 14 Sep 05:20
  ORCAUSDT|gen_271ab7ec              2/3 pass · validata il 13 Sep 00:00 · ultimo pass 06 Sep 00:00 · finestra chiusa il 13 Sep 00:00 · vista 13 Sep 08:36
  ORCAUSDT|gen_5b847426              2/3 pass · validata il 13 Sep 00:00 · ultimo pass 06 Sep 00:00 · finestra chiusa il 13 Sep 00:00 · vista 13 Sep 08:36
  ORCAUSDT|gen_6d06dca0              2/3 pass · validata il 13 Sep 00:00 · ultimo pass 06 Sep 00:00 · finestra chiusa il 13 Sep 00:00 · vista 13 Sep 08:36
  ORCAUSDT|gen_7b4a474b              2/3 pass · validata il 13 Sep 00:00 · ultimo pass 06 Sep 00:00 · finestra chiusa il 13 Sep 00:00 · vista 13 Sep 08:36
  ORCAUSDT|gen_871647b8              2/3 pass · validata il 13 Sep 00:00 · ultimo pass 06 Sep 00:00 · finestra chiusa il 13 Sep 00:00 · vista 13 Sep 08:36
  ORCAUSDT|gen_9a383fff              2/3 pass · validata il 13 Sep 00:00 · ultimo pass 06 Sep 00:00 · finestra chiusa il 13 Sep 00:00 · vista 13 Sep 08:36
  ORCAUSDT|gen_bbe21d3f              2/3 pass · validata il 13 Sep 00:00 · ultimo pass 06 Sep 00:00 · finestra chiusa il 13 Sep 00:00 · vista 13 Sep 08:36
  ORCAUSDT|gen_e6ddc613              2/3 pass · validata il 13 Sep 00:00 · ultimo pass 06 Sep 00:00 · finestra chiusa il 13 Sep 00:00 · vista 13 Sep 08:36
  ZORAUSDT|gen_f4e37ccc              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 14 Sep 05:20
  ZORAUSDT|gen_fec39d1f              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 14 Sep 05:20
  AXSUSDT|gen_b922252e               2/3 pass · validata il 14 Sep 00:00 · ultimo pass 07 Sep 00:00 · finestra chiusa il 14 Sep 00:00 · vista 14 Sep 05:20
  BTRUSDT|gen_46f0717f               1/3 pass · validata il 14 Sep 00:00 · ultimo pass 31 Aug 00:00 · finestra chiusa il 07 Sep 00:00 · vista 14 Sep 05:20
  DOTUSDT|gen_282e8a0f               1/3 pass · validata il 14 Sep 00:00 · ultimo pass 31 Aug 00:00 · finestra chiusa il 07 Sep 00:00 · vista 14 Sep 05:20

--- QUANDO RIPARTE IL BOT ---
  Al piu' presto il 13 Sep 00:00 (fra -1.3 giorni), quando la 10a coppia
  raggiungerebbe 3 pass.
  E' un LIMITE INFERIORE: assume che ognuna passi almeno una volta per
  finestra settimanale. Chi non passa per 2 finestre intere esce dal registro,
  quindi la data vera puo' essere piu' in la'. Serve anche coprire >= 5 coin distinte (10 coppie
  su coin diverse bastano).
```
