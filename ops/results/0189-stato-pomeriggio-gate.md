# 0189-stato-pomeriggio-gate.req

_eseguito: 2026-09-24 12:18 UTC_

**richiesta:** `gate`
**eseguito:** `.venv/bin/python -m scripts.gate_progress`
**esito:** codice 0 in 2.1s

```
[firebase] connesso (Firestore + RTDB)
[gate] 2850 coppie nel registro · 2506 ancora valutate · soglia 3 pass · un pass ogni 168h di dati nuovi
  distribuzione pass (solo coppie vive): 0 pass: 1303 su 163 coin · 1 pass: 931 su 153 coin · 2 pass: 213 su 79 coin · 3 pass: 55 su 27 coin · 4 pass: 4 su 3 coin
  CONGELATE: 344 coppie non piu' valutate da oltre 3 giorni (0 avevano gia' un passaggio).
  La coin e' uscita dall'universo — di solito per storia insufficiente o delisting.
  Non avanzano e non falliscono: sono escluse da tutti i conti qui sotto.
  COMPOSIZIONE (vive): 1304 base · 1202 generate.  Nel registro intero: 1648 base su 2850, tetto 3000.
  fallimenti accumulati: 1 fallimenti: 864
  VALIDATE ora: 59 su 27 coin distinte
  ready dichiarato dal registro: True (via numero coppie)
     copertura 13.5% su obiettivo 35% · via a conteggio: 10 coppie (0 = spenta) · minimi 10 coin nell'universo, 5 coperte
     deciso il 24 Sep 12:03 su 59 validate / 27 coin coperte / universo 200 · minimi ok: True · copertura ok: False · conteggio ok: True
  FINESTRE APERTE: 1203/1203 coppie con almeno un passaggio.
  E' QUESTO il numero da guardare: solo queste stanno contando i giorni verso la
  conferma successiva, e solo queste compaiono nel calendario qui sotto.
  Le altre 0 sono ferme: la finestra si apre solo quando la coppia RIPASSA
  il gate, quindi per loro la prossima conferma non ha una data — dipende da un
  evento che potrebbe non succedere.

  STATISTICA t DELLE VALIDATE: 3 con misura · 1 reggerebbero t >= 2 · mediana 1.27 · le piu' basse: NEIROUSDT|gen_e132204b (1.02), JTOUSDT|gen_35632db9 (1.27), SKYAIUSDT|gen_c61d9322 (2.27)
  (misurata, non usata per decidere: si decide dopo averla vista)

  A UN PASSO DALLA VALIDAZIONE: 213 coppie a 2/3.
  Di queste, 75 su 40 coin hanno GIA' la finestra scaduta: si
  validano al primo run in cui ripassano il gate, cioe' potenzialmente oggi.
  Le altre diventano idonee: 2 il 01 Oct 00:00 · 31 il 25 Sep 00:00 · 21 il 26 Sep 00:00 · 28 il 27 Sep 00:00 · 43 il 28 Sep 00:00 · 7 il 29 Sep 00:00 · 6 il 30 Sep 00:00
  spazio registro: 372 KiB su 879 (42%)
    134 byte a coppia · ci stanno ancora ~3890 coppie oltre le 2850 di adesso
  spazio spec scoperte: 115 KiB su 879 (13%)

  TEMPO DELL'ULTIMO GIRO (discovery): 1h 45m · iniziato 24 Sep 06:59 UTC · finito 08:45 UTC
  PASSATA A 1 ORA (5 coin): 2m · 445 valutazioni · 1 passate

  RI-VALUTAZIONE (ultimo run discovery, solo urgenti): 223 spec su 522 note · cap 500 · 470 con almeno una conferma
  299 spec restano fuori dal taglio: sono ferme, non in attesa.
  Quelle con conferme passano comunque, quindi il taglio tocca solo candidate a zero passaggi.

--- QUANDO ARRIVANO LE PROSSIME CONFERME (limite inferiore) ---
  BICOUSDT|gen_f238d283              3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 24 Sep 08:45
  BULLAUSDT|gen_7ac562e3             3/3 pass · GIA' VALIDATA · ultimo pass 22 Sep 00:00 · finestra chiusa il 29 Sep 00:00 · vista 24 Sep 08:45
  DEXEUSDT|gen_b31d8b93              3/3 pass · GIA' VALIDATA · ultimo pass 18 Sep 00:00 · finestra chiusa il 25 Sep 00:00 · vista 24 Sep 08:45
  DEXEUSDT|gen_fa304106              3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 24 Sep 08:45
  DOTUSDT|gen_919c110c               3/3 pass · GIA' VALIDATA · ultimo pass 18 Sep 00:00 · finestra chiusa il 25 Sep 00:00 · vista 24 Sep 08:45
  DOTUSDT|gen_d85b1f05               3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 24 Sep 08:45
  DOTUSDT|gen_da39a23a               3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 24 Sep 08:45
  EGLDUSDT|gen_36b0e335              3/3 pass · GIA' VALIDATA · ultimo pass 15 Sep 00:00 · finestra chiusa il 22 Sep 00:00 · vista 24 Sep 08:45
  GPSUSDT|gen_871647b8               3/3 pass · GIA' VALIDATA · ultimo pass 20 Sep 00:00 · finestra chiusa il 27 Sep 00:00 · vista 24 Sep 08:45
  GPSUSDT|gen_bf1e00d4               3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 24 Sep 08:45
  HEIUSDT|gen_e6ddc613               3/3 pass · GIA' VALIDATA · ultimo pass 15 Sep 00:00 · finestra chiusa il 22 Sep 00:00 · vista 24 Sep 08:45
  HEMIUSDT|gen_108c996b              3/3 pass · GIA' VALIDATA · ultimo pass 18 Sep 00:00 · finestra chiusa il 25 Sep 00:00 · vista 24 Sep 08:45
  HEMIUSDT|gen_93131ef1              3/3 pass · GIA' VALIDATA · ultimo pass 18 Sep 00:00 · finestra chiusa il 25 Sep 00:00 · vista 24 Sep 08:45
  JASMYUSDT|gen_b2f350ff             3/3 pass · GIA' VALIDATA · ultimo pass 16 Sep 00:00 · finestra chiusa il 23 Sep 00:00 · vista 24 Sep 08:45
  JTOUSDT|gen_35632db9               3/3 pass · GIA' VALIDATA · ultimo pass 22 Sep 00:00 · finestra chiusa il 29 Sep 00:00 · vista 24 Sep 08:45

--- QUANDO RIPARTE IL BOT ---
  Al piu' presto il — (fra -20720.5 giorni), quando la 10a coppia
  raggiungerebbe 3 pass.
  E' un LIMITE INFERIORE: assume che ognuna passi almeno una volta per
  finestra settimanale. Chi non passa per 2 finestre intere esce dal registro,
  quindi la data vera puo' essere piu' in la'. Serve anche coprire >= 5 coin distinte (10 coppie
  su coin diverse bastano).
```
