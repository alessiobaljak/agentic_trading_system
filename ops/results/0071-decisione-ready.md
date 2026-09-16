# 0071-decisione-ready.req

_eseguito: 2026-09-16 16:08 UTC_

**richiesta:** `gate`
**eseguito:** `.venv/bin/python -m scripts.gate_progress`
**esito:** codice 0 in 1.7s

```
[firebase] connesso (Firestore + RTDB)
[gate] 2429 coppie nel registro · 2163 ancora valutate · soglia 3 pass · un pass ogni 168h di dati nuovi
  distribuzione pass (solo coppie vive): 0 pass: 1712 su 214 coin · 1 pass: 322 su 95 coin · 2 pass: 94 su 41 coin · 3 pass: 35 su 19 coin
  CONGELATE: 266 coppie non piu' valutate da oltre 3 giorni (18 avevano gia' un passaggio).
  La coin e' uscita dall'universo — di solito per storia insufficiente o delisting.
  Non avanzano e non falliscono: sono escluse da tutti i conti qui sotto.
  COMPOSIZIONE (vive): 1712 base · 451 generate.  Nel registro intero: 1960 base su 2429, tetto 3000.
  fallimenti accumulati: 1 fallimenti: 1000
  VALIDATE ora: 35 su 19 coin distinte
  ready dichiarato dal registro: True (via numero coppie)
     copertura 12.2% su obiettivo 35% · via a conteggio: 10 coppie (0 = spenta) · minimi 10 coin nell'universo, 5 coperte
     deciso il 16 Sep 15:44 su 35 validate / 19 coin coperte / universo 156 · minimi ok: True · copertura ok: False · conteggio ok: True
  FINESTRE APERTE: 451/451 coppie con almeno un passaggio.
  E' QUESTO il numero da guardare: solo queste stanno contando i giorni verso la
  conferma successiva, e solo queste compaiono nel calendario qui sotto.
  Le altre 0 sono ferme: la finestra si apre solo quando la coppia RIPASSA
  il gate, quindi per loro la prossima conferma non ha una data — dipende da un
  evento che potrebbe non succedere.

  A UN PASSO DALLA VALIDAZIONE: 94 coppie a 2/3.
  Di queste, 31 su 15 coin hanno GIA' la finestra scaduta: si
  validano al primo run in cui ripassano il gate, cioe' potenzialmente oggi.
  Le altre diventano idonee: 14 il 17 Sep 00:00 · 2 il 18 Sep 00:00 · 11 il 19 Sep 00:00 · 4 il 20 Sep 00:00 · 18 il 21 Sep 00:00 · 1 il 22 Sep 00:00 · 13 il 23 Sep 00:00
  spazio registro: 677 KiB su 879 (77%)
  spazio spec scoperte: 78 KiB su 879 (9%)

  RI-VALUTAZIONE (ultimo run discovery): 360 spec su 360 note · cap 500 · 260 con almeno una conferma

--- QUANDO ARRIVANO LE PROSSIME CONFERME (limite inferiore) ---
  BICOUSDT|gen_f238d283              3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 16 Sep 14:29
  DEXEUSDT|gen_fa304106              3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 16 Sep 14:29
  DOTUSDT|gen_d85b1f05               3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 16 Sep 14:29
  DOTUSDT|gen_da39a23a               3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 16 Sep 14:29
  EGLDUSDT|gen_36b0e335              3/3 pass · GIA' VALIDATA · ultimo pass 15 Sep 00:00 · finestra chiusa il 22 Sep 00:00 · vista 16 Sep 14:29
  GPSUSDT|gen_bf1e00d4               3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 16 Sep 14:29
  HEIUSDT|gen_e6ddc613               3/3 pass · GIA' VALIDATA · ultimo pass 15 Sep 00:00 · finestra chiusa il 22 Sep 00:00 · vista 16 Sep 14:29
  JASMYUSDT|gen_b2f350ff             3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 16 Sep 14:29
  JTOUSDT|gen_f238d283               3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 16 Sep 14:29
  MUBARAKUSDT|gen_2053cba6           3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 16 Sep 14:29
  MUBARAKUSDT|gen_ff3e4154           3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 16 Sep 14:29
  NEIROUSDT|gen_d53c153b             3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 16 Sep 14:29
  NEIROUSDT|gen_f3124a14             3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 16 Sep 14:29
  ORCAUSDT|gen_271ab7ec              3/3 pass · GIA' VALIDATA · ultimo pass 14 Sep 00:00 · finestra chiusa il 21 Sep 00:00 · vista 16 Sep 14:29
  ORCAUSDT|gen_5b847426              3/3 pass · GIA' VALIDATA · ultimo pass 14 Sep 00:00 · finestra chiusa il 21 Sep 00:00 · vista 16 Sep 14:29

--- QUANDO RIPARTE IL BOT ---
  Al piu' presto il — (fra -20712.7 giorni), quando la 10a coppia
  raggiungerebbe 3 pass.
  E' un LIMITE INFERIORE: assume che ognuna passi almeno una volta per
  finestra settimanale. Chi non passa per 2 finestre intere esce dal registro,
  quindi la data vera puo' essere piu' in la'. Serve anche coprire >= 5 coin distinte (10 coppie
  su coin diverse bastano).
```
