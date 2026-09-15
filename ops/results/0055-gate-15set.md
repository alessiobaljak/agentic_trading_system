# 0055-gate-15set.req

_eseguito: 2026-09-15 06:01 UTC_

**richiesta:** `gate`
**eseguito:** `.venv/bin/python -m scripts.gate_progress`
**esito:** codice 0 in 1.5s

```
[firebase] connesso (Firestore + RTDB)
[gate] 2398 coppie nel registro · 2142 ancora valutate · soglia 3 pass · un pass ogni 168h di dati nuovi
  distribuzione pass (solo coppie vive): 0 pass: 1728 su 216 coin · 1 pass: 299 su 92 coin · 2 pass: 104 su 41 coin · 3 pass: 11 su 4 coin
  CONGELATE: 256 coppie non piu' valutate da oltre 3 giorni (16 avevano gia' un passaggio).
  La coin e' uscita dall'universo — di solito per storia insufficiente o delisting.
  Non avanzano e non falliscono: sono escluse da tutti i conti qui sotto.
  COMPOSIZIONE (vive): 1728 base · 414 generate.  Nel registro intero: 1968 base su 2398, tetto 3000.
  fallimenti accumulati: 1 fallimenti: 992
  VALIDATE ora: 11 su 4 coin distinte
  ready dichiarato dal registro: False (via —)
  FINESTRE APERTE: 414/414 coppie con almeno un passaggio.
  E' QUESTO il numero da guardare: solo queste stanno contando i giorni verso la
  conferma successiva, e solo queste compaiono nel calendario qui sotto.
  Le altre 0 sono ferme: la finestra si apre solo quando la coppia RIPASSA
  il gate, quindi per loro la prossima conferma non ha una data — dipende da un
  evento che potrebbe non succedere.

  A UN PASSO DALLA VALIDAZIONE: 104 coppie a 2/3.
  Di queste, 53 su 24 coin hanno GIA' la finestra scaduta: si
  validano al primo run in cui ripassano il gate, cioe' potenzialmente oggi.
  Le altre diventano idonee: 2 il 16 Sep 00:00 · 14 il 17 Sep 00:00 · 2 il 18 Sep 00:00 · 11 il 19 Sep 00:00 · 4 il 20 Sep 00:00 · 18 il 21 Sep 00:00
  spazio registro: 651 KiB su 879 (74%)
  spazio spec scoperte: 76 KiB su 879 (9%)

  RI-VALUTAZIONE (ultimo run discovery): 349 spec su 349 note · cap 500 · 247 con almeno una conferma

--- QUANDO ARRIVANO LE PROSSIME CONFERME (limite inferiore) ---
  EGLDUSDT|gen_36b0e335              3/3 pass · GIA' VALIDATA · ultimo pass 15 Sep 00:00 · finestra chiusa il 22 Sep 00:00 · vista 15 Sep 05:27
  HEIUSDT|gen_e6ddc613               3/3 pass · GIA' VALIDATA · ultimo pass 15 Sep 00:00 · finestra chiusa il 22 Sep 00:00 · vista 15 Sep 05:27
  ORCAUSDT|gen_271ab7ec              3/3 pass · GIA' VALIDATA · ultimo pass 14 Sep 00:00 · finestra chiusa il 21 Sep 00:00 · vista 15 Sep 05:27
  ORCAUSDT|gen_5b847426              3/3 pass · GIA' VALIDATA · ultimo pass 14 Sep 00:00 · finestra chiusa il 21 Sep 00:00 · vista 15 Sep 05:27
  ORCAUSDT|gen_6d06dca0              3/3 pass · GIA' VALIDATA · ultimo pass 14 Sep 00:00 · finestra chiusa il 21 Sep 00:00 · vista 15 Sep 05:27
  ORCAUSDT|gen_7b4a474b              3/3 pass · GIA' VALIDATA · ultimo pass 14 Sep 00:00 · finestra chiusa il 21 Sep 00:00 · vista 15 Sep 05:27
  ORCAUSDT|gen_871647b8              3/3 pass · GIA' VALIDATA · ultimo pass 14 Sep 00:00 · finestra chiusa il 21 Sep 00:00 · vista 15 Sep 05:27
  ORCAUSDT|gen_9a383fff              3/3 pass · GIA' VALIDATA · ultimo pass 14 Sep 00:00 · finestra chiusa il 21 Sep 00:00 · vista 15 Sep 05:27
  ORCAUSDT|gen_bbe21d3f              3/3 pass · GIA' VALIDATA · ultimo pass 14 Sep 00:00 · finestra chiusa il 21 Sep 00:00 · vista 15 Sep 05:27
  ORCAUSDT|gen_e6ddc613              3/3 pass · GIA' VALIDATA · ultimo pass 14 Sep 00:00 · finestra chiusa il 21 Sep 00:00 · vista 15 Sep 05:27
  STXUSDT|gen_b9bf5d01               3/3 pass · GIA' VALIDATA · ultimo pass 15 Sep 00:00 · finestra chiusa il 22 Sep 00:00 · vista 15 Sep 05:27
  EGLDUSDT|gen_f238d283              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 15 Sep 05:27
  MOVRUSDT|gen_4f890271              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 15 Sep 05:27
  ZORAUSDT|gen_f4e37ccc              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 15 Sep 05:27
  ZORAUSDT|gen_fec39d1f              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 15 Sep 05:27

--- QUANDO RIPARTE IL BOT ---
  Al piu' presto il — (fra -20711.3 giorni), quando la 10a coppia
  raggiungerebbe 3 pass.
  E' un LIMITE INFERIORE: assume che ognuna passi almeno una volta per
  finestra settimanale. Chi non passa per 2 finestre intere esce dal registro,
  quindi la data vera puo' essere piu' in la'. Serve anche coprire >= 5 coin distinte (10 coppie
  su coin diverse bastano).
```
