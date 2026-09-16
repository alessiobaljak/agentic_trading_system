# 0064-paper-partito.req

_eseguito: 2026-09-16 08:16 UTC_

**richiesta:** `gate`
**eseguito:** `.venv/bin/python -m scripts.gate_progress`
**esito:** codice 0 in 1.4s

```
[firebase] connesso (Firestore + RTDB)
[gate] 2410 coppie nel registro · 2150 ancora valutate · soglia 3 pass · un pass ogni 168h di dati nuovi
  distribuzione pass (solo coppie vive): 0 pass: 1704 su 213 coin · 1 pass: 321 su 96 coin · 2 pass: 94 su 42 coin · 3 pass: 31 su 16 coin
  CONGELATE: 260 coppie non piu' valutate da oltre 3 giorni (12 avevano gia' un passaggio).
  La coin e' uscita dall'universo — di solito per storia insufficiente o delisting.
  Non avanzano e non falliscono: sono escluse da tutti i conti qui sotto.
  COMPOSIZIONE (vive): 1704 base · 446 generate.  Nel registro intero: 1952 base su 2410, tetto 3000.
  fallimenti accumulati: 1 fallimenti: 1008
  VALIDATE ora: 31 su 16 coin distinte
  ready dichiarato dal registro: False (via —)
  FINESTRE APERTE: 446/446 coppie con almeno un passaggio.
  E' QUESTO il numero da guardare: solo queste stanno contando i giorni verso la
  conferma successiva, e solo queste compaiono nel calendario qui sotto.
  Le altre 0 sono ferme: la finestra si apre solo quando la coppia RIPASSA
  il gate, quindi per loro la prossima conferma non ha una data — dipende da un
  evento che potrebbe non succedere.

  A UN PASSO DALLA VALIDAZIONE: 94 coppie a 2/3.
  Di queste, 35 su 18 coin hanno GIA' la finestra scaduta: si
  validano al primo run in cui ripassano il gate, cioe' potenzialmente oggi.
  Le altre diventano idonee: 14 il 17 Sep 00:00 · 2 il 18 Sep 00:00 · 11 il 19 Sep 00:00 · 4 il 20 Sep 00:00 · 18 il 21 Sep 00:00 · 1 il 22 Sep 00:00 · 9 il 23 Sep 00:00
  spazio registro: 669 KiB su 879 (76%)
  spazio spec scoperte: 78 KiB su 879 (9%)

  RI-VALUTAZIONE (ultimo run discovery): 359 spec su 359 note · cap 500 · 257 con almeno una conferma

--- QUANDO ARRIVANO LE PROSSIME CONFERME (limite inferiore) ---
  DEXEUSDT|gen_fa304106              3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 16 Sep 02:29
  DOTUSDT|gen_d85b1f05               3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 16 Sep 02:29
  DOTUSDT|gen_da39a23a               3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 16 Sep 02:29
  EGLDUSDT|gen_36b0e335              3/3 pass · GIA' VALIDATA · ultimo pass 15 Sep 00:00 · finestra chiusa il 22 Sep 00:00 · vista 16 Sep 02:29
  GPSUSDT|gen_bf1e00d4               3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 16 Sep 02:29
  HEIUSDT|gen_e6ddc613               3/3 pass · GIA' VALIDATA · ultimo pass 15 Sep 00:00 · finestra chiusa il 22 Sep 00:00 · vista 16 Sep 02:29
  JASMYUSDT|gen_b2f350ff             3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 16 Sep 02:29
  MUBARAKUSDT|gen_2053cba6           3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 16 Sep 02:29
  MUBARAKUSDT|gen_ff3e4154           3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 16 Sep 02:29
  NEIROUSDT|gen_d53c153b             3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 16 Sep 02:29
  NEIROUSDT|gen_f3124a14             3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 16 Sep 02:29
  ORCAUSDT|gen_271ab7ec              3/3 pass · GIA' VALIDATA · ultimo pass 14 Sep 00:00 · finestra chiusa il 21 Sep 00:00 · vista 16 Sep 02:29
  ORCAUSDT|gen_5b847426              3/3 pass · GIA' VALIDATA · ultimo pass 14 Sep 00:00 · finestra chiusa il 21 Sep 00:00 · vista 16 Sep 02:29
  ORCAUSDT|gen_6d06dca0              3/3 pass · GIA' VALIDATA · ultimo pass 14 Sep 00:00 · finestra chiusa il 21 Sep 00:00 · vista 16 Sep 02:29
  ORCAUSDT|gen_7b4a474b              3/3 pass · GIA' VALIDATA · ultimo pass 14 Sep 00:00 · finestra chiusa il 21 Sep 00:00 · vista 16 Sep 02:29

--- QUANDO RIPARTE IL BOT ---
  Al piu' presto il — (fra -20712.3 giorni), quando la 10a coppia
  raggiungerebbe 3 pass.
  E' un LIMITE INFERIORE: assume che ognuna passi almeno una volta per
  finestra settimanale. Chi non passa per 2 finestre intere esce dal registro,
  quindi la data vera puo' essere piu' in la'. Serve anche coprire >= 5 coin distinte (10 coppie
  su coin diverse bastano).
```
