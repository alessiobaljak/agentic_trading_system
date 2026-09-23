# 0157-tempo-giro-mattina.req

_eseguito: 2026-09-23 04:56 UTC_

**richiesta:** `gate`
**eseguito:** `.venv/bin/python -m scripts.gate_progress`
**esito:** codice 0 in 1.8s

```
[firebase] connesso (Firestore + RTDB)
[gate] 2884 coppie nel registro · 2556 ancora valutate · soglia 3 pass · un pass ogni 168h di dati nuovi
  distribuzione pass (solo coppie vive): 0 pass: 1535 su 192 coin · 1 pass: 755 su 139 coin · 2 pass: 207 su 79 coin · 3 pass: 57 su 27 coin · 4 pass: 2 su 1 coin
  CONGELATE: 328 coppie non piu' valutate da oltre 3 giorni (0 avevano gia' un passaggio).
  La coin e' uscita dall'universo — di solito per storia insufficiente o delisting.
  Non avanzano e non falliscono: sono escluse da tutti i conti qui sotto.
  COMPOSIZIONE (vive): 1536 base · 1020 generate.  Nel registro intero: 1864 base su 2884, tetto 3000.
  fallimenti accumulati: 1 fallimenti: 976
  VALIDATE ora: 59 su 27 coin distinte
  ready dichiarato dal registro: True (via numero coppie)
     copertura 13.5% su obiettivo 35% · via a conteggio: 10 coppie (0 = spenta) · minimi 10 coin nell'universo, 5 coperte
     deciso il 23 Sep 03:07 su 59 validate / 27 coin coperte / universo 200 · minimi ok: True · copertura ok: False · conteggio ok: True
  FINESTRE APERTE: 1021/1021 coppie con almeno un passaggio.
  E' QUESTO il numero da guardare: solo queste stanno contando i giorni verso la
  conferma successiva, e solo queste compaiono nel calendario qui sotto.
  Le altre 0 sono ferme: la finestra si apre solo quando la coppia RIPASSA
  il gate, quindi per loro la prossima conferma non ha una data — dipende da un
  evento che potrebbe non succedere.

  A UN PASSO DALLA VALIDAZIONE: 207 coppie a 2/3.
  Di queste, 72 su 37 coin hanno GIA' la finestra scaduta: si
  validano al primo run in cui ripassano il gate, cioe' potenzialmente oggi.
  Le altre diventano idonee: 3 il 24 Sep 00:00 · 31 il 25 Sep 00:00 · 21 il 26 Sep 00:00 · 28 il 27 Sep 00:00 · 43 il 28 Sep 00:00 · 5 il 29 Sep 00:00 · 4 il 30 Sep 00:00
  spazio registro: 352 KiB su 879 (40%)
    125 byte a coppia · ci stanno ancora ~4324 coppie oltre le 2884 di adesso
  spazio spec scoperte: 104 KiB su 879 (12%)

  TEMPO DELL'ULTIMO GIRO (discovery): 2h 29m · iniziato 23 Sep 00:10 UTC · finito 02:40 UTC
  PASSATA A 1 ORA (1 coin): 2m · 89 valutazioni · 0 passate

  RI-VALUTAZIONE (ultimo run discovery): 471 spec su 471 note · cap 500 · 412 con almeno una conferma

--- QUANDO ARRIVANO LE PROSSIME CONFERME (limite inferiore) ---
  BICOUSDT|gen_f238d283              3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 23 Sep 02:40
  BULLAUSDT|gen_7ac562e3             3/3 pass · GIA' VALIDATA · ultimo pass 22 Sep 00:00 · finestra chiusa il 29 Sep 00:00 · vista 23 Sep 02:40
  DEXEUSDT|gen_b31d8b93              3/3 pass · GIA' VALIDATA · ultimo pass 18 Sep 00:00 · finestra chiusa il 25 Sep 00:00 · vista 23 Sep 02:40
  DEXEUSDT|gen_fa304106              3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 23 Sep 02:40
  DOTUSDT|gen_919c110c               3/3 pass · GIA' VALIDATA · ultimo pass 18 Sep 00:00 · finestra chiusa il 25 Sep 00:00 · vista 23 Sep 02:40
  DOTUSDT|gen_d85b1f05               3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 23 Sep 02:40
  DOTUSDT|gen_da39a23a               3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 23 Sep 02:40
  EGLDUSDT|gen_36b0e335              3/3 pass · GIA' VALIDATA · ultimo pass 15 Sep 00:00 · finestra chiusa il 22 Sep 00:00 · vista 23 Sep 02:40
  GPSUSDT|gen_871647b8               3/3 pass · GIA' VALIDATA · ultimo pass 20 Sep 00:00 · finestra chiusa il 27 Sep 00:00 · vista 23 Sep 02:40
  GPSUSDT|gen_bf1e00d4               3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 23 Sep 02:40
  HEIUSDT|gen_e6ddc613               3/3 pass · GIA' VALIDATA · ultimo pass 15 Sep 00:00 · finestra chiusa il 22 Sep 00:00 · vista 23 Sep 02:40
  HEMIUSDT|gen_108c996b              3/3 pass · GIA' VALIDATA · ultimo pass 18 Sep 00:00 · finestra chiusa il 25 Sep 00:00 · vista 23 Sep 02:40
  HEMIUSDT|gen_93131ef1              3/3 pass · GIA' VALIDATA · ultimo pass 18 Sep 00:00 · finestra chiusa il 25 Sep 00:00 · vista 23 Sep 02:40
  JASMYUSDT|gen_b2f350ff             3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 23 Sep 02:40
  JTOUSDT|gen_35632db9               3/3 pass · GIA' VALIDATA · ultimo pass 22 Sep 00:00 · finestra chiusa il 29 Sep 00:00 · vista 23 Sep 02:40

--- QUANDO RIPARTE IL BOT ---
  Al piu' presto il — (fra -20719.2 giorni), quando la 10a coppia
  raggiungerebbe 3 pass.
  E' un LIMITE INFERIORE: assume che ognuna passi almeno una volta per
  finestra settimanale. Chi non passa per 2 finestre intere esce dal registro,
  quindi la data vera puo' essere piu' in la'. Serve anche coprire >= 5 coin distinte (10 coppie
  su coin diverse bastano).
```
