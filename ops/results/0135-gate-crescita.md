# 0135-gate-crescita.req

_eseguito: 2026-09-21 17:12 UTC_

**richiesta:** `gate`
**eseguito:** `.venv/bin/python -m scripts.gate_progress`
**esito:** codice 0 in 1.3s

```
[firebase] connesso (Firestore + RTDB)
[gate] 2695 coppie nel registro · 2375 ancora valutate · soglia 3 pass · un pass ogni 168h di dati nuovi
  distribuzione pass (solo coppie vive): 0 pass: 1647 su 206 coin · 1 pass: 476 su 120 coin · 2 pass: 196 su 74 coin · 3 pass: 56 su 26 coin
  CONGELATE: 320 coppie non piu' valutate da oltre 3 giorni (0 avevano gia' un passaggio).
  La coin e' uscita dall'universo — di solito per storia insufficiente o delisting.
  Non avanzano e non falliscono: sono escluse da tutti i conti qui sotto.
  COMPOSIZIONE (vive): 1648 base · 727 generate.  Nel registro intero: 1968 base su 2695, tetto 3000.
  fallimenti accumulati: 1 fallimenti: 1016
  VALIDATE ora: 56 su 26 coin distinte
  ready dichiarato dal registro: True (via numero coppie)
     copertura 15.8% su obiettivo 35% · via a conteggio: 10 coppie (0 = spenta) · minimi 10 coin nell'universo, 5 coperte
     deciso il 21 Sep 12:43 su 56 validate / 26 coin coperte / universo 165 · minimi ok: True · copertura ok: False · conteggio ok: True
  FINESTRE APERTE: 728/728 coppie con almeno un passaggio.
  E' QUESTO il numero da guardare: solo queste stanno contando i giorni verso la
  conferma successiva, e solo queste compaiono nel calendario qui sotto.
  Le altre 0 sono ferme: la finestra si apre solo quando la coppia RIPASSA
  il gate, quindi per loro la prossima conferma non ha una data — dipende da un
  evento che potrebbe non succedere.

  A UN PASSO DALLA VALIDAZIONE: 196 coppie a 2/3.
  Di queste, 59 su 31 coin hanno GIA' la finestra scaduta: si
  validano al primo run in cui ripassano il gate, cioe' potenzialmente oggi.
  Le altre diventano idonee: 1 il 22 Sep 00:00 · 15 il 23 Sep 00:00 · 3 il 24 Sep 00:00 · 31 il 25 Sep 00:00 · 21 il 26 Sep 00:00 · 24 il 27 Sep 00:00 · 42 il 28 Sep 00:00
  spazio registro: 298 KiB su 879 (34%)
    113 byte a coppia · ci stanno ancora ~5245 coppie oltre le 2695 di adesso
  spazio spec scoperte: 93 KiB su 879 (11%)

  RI-VALUTAZIONE (ultimo run discovery): 429 spec su 429 note · cap 500 · 341 con almeno una conferma

--- QUANDO ARRIVANO LE PROSSIME CONFERME (limite inferiore) ---
  BICOUSDT|gen_f238d283              3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 21 Sep 16:55
  DEXEUSDT|gen_b31d8b93              3/3 pass · GIA' VALIDATA · ultimo pass 18 Sep 00:00 · finestra chiusa il 25 Sep 00:00 · vista 21 Sep 16:55
  DEXEUSDT|gen_fa304106              3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 21 Sep 16:55
  DOTUSDT|gen_919c110c               3/3 pass · GIA' VALIDATA · ultimo pass 18 Sep 00:00 · finestra chiusa il 25 Sep 00:00 · vista 21 Sep 16:55
  DOTUSDT|gen_d85b1f05               3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 21 Sep 16:55
  DOTUSDT|gen_da39a23a               3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 21 Sep 16:55
  EGLDUSDT|gen_36b0e335              3/3 pass · GIA' VALIDATA · ultimo pass 15 Sep 00:00 · finestra chiusa il 22 Sep 00:00 · vista 21 Sep 16:55
  GPSUSDT|gen_871647b8               3/3 pass · GIA' VALIDATA · ultimo pass 20 Sep 00:00 · finestra chiusa il 27 Sep 00:00 · vista 21 Sep 16:55
  GPSUSDT|gen_bf1e00d4               3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 21 Sep 16:55
  HEIUSDT|gen_e6ddc613               3/3 pass · GIA' VALIDATA · ultimo pass 15 Sep 00:00 · finestra chiusa il 22 Sep 00:00 · vista 21 Sep 16:55
  HEMIUSDT|gen_108c996b              3/3 pass · GIA' VALIDATA · ultimo pass 18 Sep 00:00 · finestra chiusa il 25 Sep 00:00 · vista 21 Sep 16:55
  HEMIUSDT|gen_93131ef1              3/3 pass · GIA' VALIDATA · ultimo pass 18 Sep 00:00 · finestra chiusa il 25 Sep 00:00 · vista 21 Sep 16:55
  JASMYUSDT|gen_b2f350ff             3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 21 Sep 16:55
  JTOUSDT|gen_f238d283               3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 21 Sep 16:55
  MUBARAKUSDT|gen_1e2af031           3/3 pass · GIA' VALIDATA · ultimo pass 20 Sep 00:00 · finestra chiusa il 27 Sep 00:00 · vista 21 Sep 16:55

--- QUANDO RIPARTE IL BOT ---
  Al piu' presto il — (fra -20717.7 giorni), quando la 10a coppia
  raggiungerebbe 3 pass.
  E' un LIMITE INFERIORE: assume che ognuna passi almeno una volta per
  finestra settimanale. Chi non passa per 2 finestre intere esce dal registro,
  quindi la data vera puo' essere piu' in la'. Serve anche coprire >= 5 coin distinte (10 coppie
  su coin diverse bastano).
```
