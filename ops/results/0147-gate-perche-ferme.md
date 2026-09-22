# 0147-gate-perche-ferme.req

_eseguito: 2026-09-22 06:12 UTC_

**richiesta:** `gate`
**eseguito:** `.venv/bin/python -m scripts.gate_progress`
**esito:** codice 0 in 1.4s

```
[firebase] connesso (Firestore + RTDB)
[gate] 2852 coppie nel registro · 2516 ancora valutate · soglia 3 pass · un pass ogni 168h di dati nuovi
  distribuzione pass (solo coppie vive): 0 pass: 1607 su 201 coin · 1 pass: 652 su 131 coin · 2 pass: 201 su 76 coin · 3 pass: 56 su 26 coin
  CONGELATE: 336 coppie non piu' valutate da oltre 3 giorni (0 avevano gia' un passaggio).
  La coin e' uscita dall'universo — di solito per storia insufficiente o delisting.
  Non avanzano e non falliscono: sono escluse da tutti i conti qui sotto.
  COMPOSIZIONE (vive): 1608 base · 908 generate.  Nel registro intero: 1944 base su 2852, tetto 3000.
  fallimenti accumulati: 1 fallimenti: 1000
  VALIDATE ora: 56 su 26 coin distinte
  ready dichiarato dal registro: True (via copertura)
     copertura 100.0% su obiettivo 35% · via a conteggio: 10 coppie (0 = spenta) · minimi 10 coin nell'universo, 5 coperte
     deciso il 22 Sep 02:52 su 56 validate / 26 coin coperte / universo 26 · minimi ok: True · copertura ok: True · conteggio ok: True
  FINESTRE APERTE: 909/909 coppie con almeno un passaggio.
  E' QUESTO il numero da guardare: solo queste stanno contando i giorni verso la
  conferma successiva, e solo queste compaiono nel calendario qui sotto.
  Le altre 0 sono ferme: la finestra si apre solo quando la coppia RIPASSA
  il gate, quindi per loro la prossima conferma non ha una data — dipende da un
  evento che potrebbe non succedere.

  A UN PASSO DALLA VALIDAZIONE: 201 coppie a 2/3.
  Di queste, 60 su 32 coin hanno GIA' la finestra scaduta: si
  validano al primo run in cui ripassano il gate, cioe' potenzialmente oggi.
  Le altre diventano idonee: 15 il 23 Sep 00:00 · 3 il 24 Sep 00:00 · 31 il 25 Sep 00:00 · 21 il 26 Sep 00:00 · 28 il 27 Sep 00:00 · 43 il 28 Sep 00:00
  spazio registro: 333 KiB su 879 (38%)
    120 byte a coppia · ci stanno ancora ~4664 coppie oltre le 2852 di adesso
  spazio spec scoperte: 95 KiB su 879 (11%)

  RI-VALUTAZIONE (ultimo run discovery): 434 spec su 434 note · cap 500 · 370 con almeno una conferma

--- QUANDO ARRIVANO LE PROSSIME CONFERME (limite inferiore) ---
  BICOUSDT|gen_f238d283              3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 22 Sep 02:52
  DEXEUSDT|gen_b31d8b93              3/3 pass · GIA' VALIDATA · ultimo pass 18 Sep 00:00 · finestra chiusa il 25 Sep 00:00 · vista 22 Sep 02:52
  DEXEUSDT|gen_fa304106              3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 22 Sep 02:52
  DOTUSDT|gen_919c110c               3/3 pass · GIA' VALIDATA · ultimo pass 18 Sep 00:00 · finestra chiusa il 25 Sep 00:00 · vista 22 Sep 02:52
  DOTUSDT|gen_d85b1f05               3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 22 Sep 02:52
  DOTUSDT|gen_da39a23a               3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 22 Sep 02:52
  EGLDUSDT|gen_36b0e335              3/3 pass · GIA' VALIDATA · ultimo pass 15 Sep 00:00 · finestra chiusa il 22 Sep 00:00 · vista 22 Sep 02:52
  GPSUSDT|gen_871647b8               3/3 pass · GIA' VALIDATA · ultimo pass 20 Sep 00:00 · finestra chiusa il 27 Sep 00:00 · vista 22 Sep 02:52
  GPSUSDT|gen_bf1e00d4               3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 22 Sep 02:52
  HEIUSDT|gen_e6ddc613               3/3 pass · GIA' VALIDATA · ultimo pass 15 Sep 00:00 · finestra chiusa il 22 Sep 00:00 · vista 22 Sep 02:52
  HEMIUSDT|gen_108c996b              3/3 pass · GIA' VALIDATA · ultimo pass 18 Sep 00:00 · finestra chiusa il 25 Sep 00:00 · vista 22 Sep 02:52
  HEMIUSDT|gen_93131ef1              3/3 pass · GIA' VALIDATA · ultimo pass 18 Sep 00:00 · finestra chiusa il 25 Sep 00:00 · vista 22 Sep 02:52
  JASMYUSDT|gen_b2f350ff             3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 22 Sep 02:52
  JTOUSDT|gen_f238d283               3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 22 Sep 02:52
  MUBARAKUSDT|gen_1e2af031           3/3 pass · GIA' VALIDATA · ultimo pass 20 Sep 00:00 · finestra chiusa il 27 Sep 00:00 · vista 22 Sep 02:52

--- QUANDO RIPARTE IL BOT ---
  Al piu' presto il — (fra -20718.3 giorni), quando la 10a coppia
  raggiungerebbe 3 pass.
  E' un LIMITE INFERIORE: assume che ognuna passi almeno una volta per
  finestra settimanale. Chi non passa per 2 finestre intere esce dal registro,
  quindi la data vera puo' essere piu' in la'. Serve anche coprire >= 5 coin distinte (10 coppie
  su coin diverse bastano).
```
