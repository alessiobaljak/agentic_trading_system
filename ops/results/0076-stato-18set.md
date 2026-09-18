# 0076-stato-18set.req

_eseguito: 2026-09-18 05:15 UTC_

**richiesta:** `gate`
**eseguito:** `.venv/bin/python -m scripts.gate_progress`
**esito:** codice 0 in 1.5s

```
[firebase] connesso (Firestore + RTDB)
[gate] 2504 coppie nel registro · 2232 ancora valutate · soglia 3 pass · un pass ogni 168h di dati nuovi
  distribuzione pass (solo coppie vive): 0 pass: 1704 su 213 coin · 1 pass: 367 su 110 coin · 2 pass: 118 su 47 coin · 3 pass: 43 su 23 coin
  CONGELATE: 272 coppie non piu' valutate da oltre 3 giorni (0 avevano gia' un passaggio).
  La coin e' uscita dall'universo — di solito per storia insufficiente o delisting.
  Non avanzano e non falliscono: sono escluse da tutti i conti qui sotto.
  COMPOSIZIONE (vive): 1704 base · 528 generate.  Nel registro intero: 1976 base su 2504, tetto 3000.
  fallimenti accumulati: 1 fallimenti: 984
  VALIDATE ora: 43 su 23 coin distinte
  ready dichiarato dal registro: True (via numero coppie)
     copertura 14.8% su obiettivo 35% · via a conteggio: 10 coppie (0 = spenta) · minimi 10 coin nell'universo, 5 coperte
     deciso il 18 Sep 03:43 su 43 validate / 23 coin coperte / universo 155 · minimi ok: True · copertura ok: False · conteggio ok: True
  FINESTRE APERTE: 528/528 coppie con almeno un passaggio.
  E' QUESTO il numero da guardare: solo queste stanno contando i giorni verso la
  conferma successiva, e solo queste compaiono nel calendario qui sotto.
  Le altre 0 sono ferme: la finestra si apre solo quando la coppia RIPASSA
  il gate, quindi per loro la prossima conferma non ha una data — dipende da un
  evento che potrebbe non succedere.

  A UN PASSO DALLA VALIDAZIONE: 118 coppie a 2/3.
  Di queste, 39 su 19 coin hanno GIA' la finestra scaduta: si
  validano al primo run in cui ripassano il gate, cioe' potenzialmente oggi.
  Le altre diventano idonee: 11 il 19 Sep 00:00 · 4 il 20 Sep 00:00 · 18 il 21 Sep 00:00 · 1 il 22 Sep 00:00 · 15 il 23 Sep 00:00 · 3 il 24 Sep 00:00 · 27 il 25 Sep 00:00
  spazio registro: 720 KiB su 879 (82%)  ATTENZIONE:
  oltre il limite Firestore rifiuta la scrittura e il run perde
  le conferme appena guadagnate. Va alzato il tetto o alleggerito il documento.
  spazio spec scoperte: 82 KiB su 879 (9%)

  RI-VALUTAZIONE (ultimo run discovery): 379 spec su 379 note · cap 500 · 280 con almeno una conferma

--- QUANDO ARRIVANO LE PROSSIME CONFERME (limite inferiore) ---
  BICOUSDT|gen_f238d283              3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 18 Sep 02:35
  DEXEUSDT|gen_b31d8b93              3/3 pass · GIA' VALIDATA · ultimo pass 18 Sep 00:00 · finestra chiusa il 25 Sep 00:00 · vista 18 Sep 02:35
  DEXEUSDT|gen_fa304106              3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 18 Sep 02:35
  DOTUSDT|gen_919c110c               3/3 pass · GIA' VALIDATA · ultimo pass 18 Sep 00:00 · finestra chiusa il 25 Sep 00:00 · vista 18 Sep 02:35
  DOTUSDT|gen_d85b1f05               3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 18 Sep 02:35
  DOTUSDT|gen_da39a23a               3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 18 Sep 02:35
  EGLDUSDT|gen_36b0e335              3/3 pass · GIA' VALIDATA · ultimo pass 15 Sep 00:00 · finestra chiusa il 22 Sep 00:00 · vista 18 Sep 02:35
  GPSUSDT|gen_bf1e00d4               3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 18 Sep 02:35
  HEIUSDT|gen_e6ddc613               3/3 pass · GIA' VALIDATA · ultimo pass 15 Sep 00:00 · finestra chiusa il 22 Sep 00:00 · vista 18 Sep 02:35
  HEMIUSDT|gen_108c996b              3/3 pass · GIA' VALIDATA · ultimo pass 18 Sep 00:00 · finestra chiusa il 25 Sep 00:00 · vista 18 Sep 02:35
  HEMIUSDT|gen_93131ef1              3/3 pass · GIA' VALIDATA · ultimo pass 18 Sep 00:00 · finestra chiusa il 25 Sep 00:00 · vista 18 Sep 02:35
  JASMYUSDT|gen_b2f350ff             3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 18 Sep 02:35
  JTOUSDT|gen_f238d283               3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 18 Sep 02:35
  MUBARAKUSDT|gen_2053cba6           3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 18 Sep 02:35
  MUBARAKUSDT|gen_ff3e4154           3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 18 Sep 02:35

--- QUANDO RIPARTE IL BOT ---
  Al piu' presto il — (fra -20714.2 giorni), quando la 10a coppia
  raggiungerebbe 3 pass.
  E' un LIMITE INFERIORE: assume che ognuna passi almeno una volta per
  finestra settimanale. Chi non passa per 2 finestre intere esce dal registro,
  quindi la data vera puo' essere piu' in la'. Serve anche coprire >= 5 coin distinte (10 coppie
  su coin diverse bastano).
```
