# 0178-check-24set-gate.req

_eseguito: 2026-09-24 06:13 UTC_

**richiesta:** `gate`
**eseguito:** `.venv/bin/python -m scripts.gate_progress`
**esito:** codice 0 in 1.4s

```
[firebase] connesso (Firestore + RTDB)
[gate] 2922 coppie nel registro · 2538 ancora valutate · soglia 3 pass · un pass ogni 168h di dati nuovi
  distribuzione pass (solo coppie vive): 0 pass: 1343 su 168 coin · 1 pass: 923 su 152 coin · 2 pass: 213 su 79 coin · 3 pass: 55 su 27 coin · 4 pass: 4 su 3 coin
  CONGELATE: 384 coppie non piu' valutate da oltre 3 giorni (0 avevano gia' un passaggio).
  La coin e' uscita dall'universo — di solito per storia insufficiente o delisting.
  Non avanzano e non falliscono: sono escluse da tutti i conti qui sotto.
  COMPOSIZIONE (vive): 1344 base · 1194 generate.  Nel registro intero: 1728 base su 2922, tetto 3000.
  fallimenti accumulati: 1 fallimenti: 880
  VALIDATE ora: 59 su 27 coin distinte
  ready dichiarato dal registro: True (via numero coppie)
     copertura 13.5% su obiettivo 35% · via a conteggio: 10 coppie (0 = spenta) · minimi 10 coin nell'universo, 5 coperte
     deciso il 24 Sep 06:02 su 59 validate / 27 coin coperte / universo 200 · minimi ok: True · copertura ok: False · conteggio ok: True
  FINESTRE APERTE: 1195/1195 coppie con almeno un passaggio.
  E' QUESTO il numero da guardare: solo queste stanno contando i giorni verso la
  conferma successiva, e solo queste compaiono nel calendario qui sotto.
  Le altre 0 sono ferme: la finestra si apre solo quando la coppia RIPASSA
  il gate, quindi per loro la prossima conferma non ha una data — dipende da un
  evento che potrebbe non succedere.

  A UN PASSO DALLA VALIDAZIONE: 213 coppie a 2/3.
  Di queste, 75 su 40 coin hanno GIA' la finestra scaduta: si
  validano al primo run in cui ripassano il gate, cioe' potenzialmente oggi.
  Le altre diventano idonee: 2 il 01 Oct 00:00 · 31 il 25 Sep 00:00 · 21 il 26 Sep 00:00 · 28 il 27 Sep 00:00 · 43 il 28 Sep 00:00 · 7 il 29 Sep 00:00 · 6 il 30 Sep 00:00
  spazio registro: 376 KiB su 879 (43%)
    132 byte a coppia · ci stanno ancora ~3908 coppie oltre le 2922 di adesso
  spazio spec scoperte: 114 KiB su 879 (13%)

  TEMPO DELL'ULTIMO GIRO (discovery): 1h 54m · iniziato 24 Sep 03:11 UTC · finito 05:05 UTC
  PASSATA A 1 ORA (5 coin): 1m · 445 valutazioni · 1 passate

  RI-VALUTAZIONE (ultimo run discovery, solo urgenti): 223 spec su 516 note · cap 500 · 464 con almeno una conferma
  293 spec restano fuori dal taglio: sono ferme, non in attesa.
  Quelle con conferme passano comunque, quindi il taglio tocca solo candidate a zero passaggi.

--- QUANDO ARRIVANO LE PROSSIME CONFERME (limite inferiore) ---
  BICOUSDT|gen_f238d283              3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 24 Sep 05:05
  BULLAUSDT|gen_7ac562e3             3/3 pass · GIA' VALIDATA · ultimo pass 22 Sep 00:00 · finestra chiusa il 29 Sep 00:00 · vista 24 Sep 05:05
  DEXEUSDT|gen_b31d8b93              3/3 pass · GIA' VALIDATA · ultimo pass 18 Sep 00:00 · finestra chiusa il 25 Sep 00:00 · vista 24 Sep 05:05
  DEXEUSDT|gen_fa304106              3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 24 Sep 05:05
  DOTUSDT|gen_919c110c               3/3 pass · GIA' VALIDATA · ultimo pass 18 Sep 00:00 · finestra chiusa il 25 Sep 00:00 · vista 24 Sep 05:05
  DOTUSDT|gen_d85b1f05               3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 24 Sep 05:05
  DOTUSDT|gen_da39a23a               3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 24 Sep 05:05
  EGLDUSDT|gen_36b0e335              3/3 pass · GIA' VALIDATA · ultimo pass 15 Sep 00:00 · finestra chiusa il 22 Sep 00:00 · vista 24 Sep 05:05
  GPSUSDT|gen_871647b8               3/3 pass · GIA' VALIDATA · ultimo pass 20 Sep 00:00 · finestra chiusa il 27 Sep 00:00 · vista 24 Sep 05:05
  GPSUSDT|gen_bf1e00d4               3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 24 Sep 05:05
  HEIUSDT|gen_e6ddc613               3/3 pass · GIA' VALIDATA · ultimo pass 15 Sep 00:00 · finestra chiusa il 22 Sep 00:00 · vista 24 Sep 05:05
  HEMIUSDT|gen_108c996b              3/3 pass · GIA' VALIDATA · ultimo pass 18 Sep 00:00 · finestra chiusa il 25 Sep 00:00 · vista 24 Sep 05:05
  HEMIUSDT|gen_93131ef1              3/3 pass · GIA' VALIDATA · ultimo pass 18 Sep 00:00 · finestra chiusa il 25 Sep 00:00 · vista 24 Sep 05:05
  JASMYUSDT|gen_b2f350ff             3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 24 Sep 05:05
  JTOUSDT|gen_35632db9               3/3 pass · GIA' VALIDATA · ultimo pass 22 Sep 00:00 · finestra chiusa il 29 Sep 00:00 · vista 24 Sep 05:05

--- QUANDO RIPARTE IL BOT ---
  Al piu' presto il — (fra -20720.3 giorni), quando la 10a coppia
  raggiungerebbe 3 pass.
  E' un LIMITE INFERIORE: assume che ognuna passi almeno una volta per
  finestra settimanale. Chi non passa per 2 finestre intere esce dal registro,
  quindi la data vera puo' essere piu' in la'. Serve anche coprire >= 5 coin distinte (10 coppie
  su coin diverse bastano).
```
