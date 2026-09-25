# 0224-gate-notturno.req

_eseguito: 2026-09-25 04:57 UTC_

**richiesta:** `gate`
**eseguito:** `.venv/bin/python -m scripts.gate_progress`
**esito:** codice 0 in 1.4s

```
[firebase] connesso (Firestore + RTDB)
[gate] 2860 coppie nel registro · 1236 ancora valutate · soglia 3 pass · un pass ogni 168h di dati nuovi
  distribuzione pass (solo coppie vive): 1 pass: 673 su 130 coin · 2 pass: 403 su 114 coin · 3 pass: 116 su 46 coin · 4 pass: 44 su 23 coin
  CONGELATE: 1624 coppie non piu' valutate da oltre 3 giorni (1 avevano gia' un passaggio).
  La coin e' uscita dall'universo — di solito per storia insufficiente o delisting.
  Non avanzano e non falliscono: sono escluse da tutti i conti qui sotto.
  COMPOSIZIONE (vive): 0 base · 1236 generate.  Nel registro intero: 1624 base su 2860, tetto 3000.
  fallimenti accumulati: 1 fallimenti: 4
  VALIDATE ora: 160 su 52 coin distinte
  ready dichiarato dal registro: True (via numero coppie)
     copertura 26.0% su obiettivo 35% · via a conteggio: 10 coppie (0 = spenta) · minimi 10 coin nell'universo, 5 coperte
     deciso il 25 Sep 03:28 su 160 validate / 52 coin coperte / universo 200 · minimi ok: True · copertura ok: False · conteggio ok: True
  FINESTRE APERTE: 1236/1236 coppie con almeno un passaggio.
  E' QUESTO il numero da guardare: solo queste stanno contando i giorni verso la
  conferma successiva, e solo queste compaiono nel calendario qui sotto.
  Le altre 0 sono ferme: la finestra si apre solo quando la coppia RIPASSA
  il gate, quindi per loro la prossima conferma non ha una data — dipende da un
  evento che potrebbe non succedere.

  STATISTICA t DELLE VALIDATE: 9 con misura · 3 reggerebbero t >= 2 · mediana 1.47 · le piu' basse: NEIROUSDT|gen_e132204b (1.02), JTOUSDT|gen_35632db9 (1.27), BULLAUSDT|gen_7ac562e3 (1.46)
  (misurata, non usata per decidere: si decide dopo averla vista)

  A UN PASSO DALLA VALIDAZIONE: 403 coppie a 2/3.
  Di queste, 5 su 3 coin hanno GIA' la finestra scaduta: si
  validano al primo run in cui ripassano il gate, cioe' potenzialmente oggi.
  Le altre diventano idonee: 244 il 01 Oct 00:00 · 49 il 02 Oct 00:00 · 21 il 26 Sep 00:00 · 28 il 27 Sep 00:00 · 43 il 28 Sep 00:00 · 7 il 29 Sep 00:00 · 6 il 30 Sep 00:00
  spazio registro: 386 KiB su 879 (44%)
    138 byte a coppia · ci stanno ancora ~3658 coppie oltre le 2860 di adesso
  spazio spec scoperte: 117 KiB su 879 (13%)

  TEMPO DELL'ULTIMO GIRO (discovery): 1h 09m · iniziato 25 Sep 03:30 UTC · finito 04:40 UTC
  PASSATA A 1 ORA (5 coin): 2m · 440 valutazioni · 0 passate

  RI-VALUTAZIONE (ultimo run discovery, solo urgenti): 8 spec su 529 note · cap 500 · 479 con almeno una conferma
  521 spec restano fuori dal taglio: sono ferme, non in attesa.
  Quelle con conferme passano comunque, quindi il taglio tocca solo candidate a zero passaggi.

--- QUANDO ARRIVANO LE PROSSIME CONFERME (limite inferiore) ---
  ARCUSDT|gen_96c1ed1b               3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 25 Sep 04:40
  ATOMUSDT|gen_eaa569ba              3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 25 Sep 04:40
  AVAAIUSDT|gen_14e1775b             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 25 Sep 04:40
  AVAAIUSDT|gen_68ebd3b9             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 25 Sep 04:40
  AXSUSDT|gen_b922252e               3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 25 Sep 04:40
  B2USDT|gen_ddb3def9                3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 25 Sep 04:40
  BICOUSDT|gen_2e6776ad              3/3 pass · GIA' VALIDATA · ultimo pass 25 Sep 00:00 · finestra chiusa il 02 Oct 00:00 · vista 25 Sep 04:40
  BICOUSDT|gen_35632db9              3/3 pass · GIA' VALIDATA · ultimo pass 25 Sep 00:00 · finestra chiusa il 02 Oct 00:00 · vista 25 Sep 04:40
  BICOUSDT|gen_f238d283              4/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 25 Sep 04:40
  BTRUSDT|gen_8981d5f2               3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 25 Sep 04:40
  BULLAUSDT|gen_2e8fb80a             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 25 Sep 04:40
  BULLAUSDT|gen_3f1b628b             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 25 Sep 04:40
  BULLAUSDT|gen_6df6961d             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 25 Sep 04:40
  BULLAUSDT|gen_7ac562e3             3/3 pass · GIA' VALIDATA · ultimo pass 22 Sep 00:00 · finestra chiusa il 29 Sep 00:00 · vista 25 Sep 04:40
  BULLAUSDT|gen_c8aa0d13             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 25 Sep 04:40

--- QUANDO RIPARTE IL BOT ---
  Al piu' presto il — (fra -20721.2 giorni), quando la 10a coppia
  raggiungerebbe 3 pass.
  E' un LIMITE INFERIORE: assume che ognuna passi almeno una volta per
  finestra settimanale. Chi non passa per 2 finestre intere esce dal registro,
  quindi la data vera puo' essere piu' in la'. Serve anche coprire >= 5 coin distinte (10 coppie
  su coin diverse bastano).
```
