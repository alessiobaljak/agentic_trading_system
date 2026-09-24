# 0217-gate-fine-giro.req

_eseguito: 2026-09-24 21:21 UTC_

**richiesta:** `gate`
**eseguito:** `.venv/bin/python -m scripts.gate_progress`
**esito:** codice 0 in 1.2s

```
[firebase] connesso (Firestore + RTDB)
[gate] 2854 coppie nel registro · 1206 ancora valutate · soglia 3 pass · un pass ogni 168h di dati nuovi
  distribuzione pass (solo coppie vive): 1 pass: 692 su 134 coin · 2 pass: 380 su 107 coin · 3 pass: 99 su 45 coin · 4 pass: 35 su 19 coin
  CONGELATE: 1648 coppie non piu' valutate da oltre 3 giorni (1 avevano gia' un passaggio).
  La coin e' uscita dall'universo — di solito per storia insufficiente o delisting.
  Non avanzano e non falliscono: sono escluse da tutti i conti qui sotto.
  COMPOSIZIONE (vive): 0 base · 1206 generate.  Nel registro intero: 1648 base su 2854, tetto 3000.
  fallimenti accumulati: 1 fallimenti: 3
  VALIDATE ora: 134 su 50 coin distinte
  ready dichiarato dal registro: True (via numero coppie)
     copertura 25.0% su obiettivo 35% · via a conteggio: 10 coppie (0 = spenta) · minimi 10 coin nell'universo, 5 coperte
     deciso il 24 Sep 19:11 su 59 validate / 27 coin coperte / universo 200 · minimi ok: True · copertura ok: False · conteggio ok: True
  FINESTRE APERTE: 1206/1206 coppie con almeno un passaggio.
  E' QUESTO il numero da guardare: solo queste stanno contando i giorni verso la
  conferma successiva, e solo queste compaiono nel calendario qui sotto.
  Le altre 0 sono ferme: la finestra si apre solo quando la coppia RIPASSA
  il gate, quindi per loro la prossima conferma non ha una data — dipende da un
  evento che potrebbe non succedere.

  STATISTICA t DELLE VALIDATE: 5 con misura · 1 reggerebbero t >= 2 · mediana 1.47 · le piu' basse: NEIROUSDT|gen_e132204b (1.02), JTOUSDT|gen_35632db9 (1.27), JTOUSDT|gen_f238d283 (1.47)
  (misurata, non usata per decidere: si decide dopo averla vista)

  A UN PASSO DALLA VALIDAZIONE: 380 coppie a 2/3.
  Di queste, 0 su 0 coin hanno GIA' la finestra scaduta: si
  validano al primo run in cui ripassano il gate, cioe' potenzialmente oggi.
  Le altre diventano idonee: 244 il 01 Oct 00:00 · 31 il 25 Sep 00:00 · 21 il 26 Sep 00:00 · 28 il 27 Sep 00:00 · 43 il 28 Sep 00:00 · 7 il 29 Sep 00:00 · 6 il 30 Sep 00:00
  spazio registro: 376 KiB su 879 (43%)
    135 byte a coppia · ci stanno ancora ~3817 coppie oltre le 2854 di adesso
  spazio spec scoperte: 116 KiB su 879 (13%)

  TEMPO DELL'ULTIMO GIRO (discovery): 2h 06m · iniziato 24 Sep 19:13 UTC · finito 21:20 UTC
  PASSATA A 1 ORA (5 coin): 2m · 450 valutazioni · 1 passate

  RI-VALUTAZIONE (ultimo run discovery, solo urgenti): 223 spec su 525 note · cap 500 · 473 con almeno una conferma
  302 spec restano fuori dal taglio: sono ferme, non in attesa.
  Quelle con conferme passano comunque, quindi il taglio tocca solo candidate a zero passaggi.

--- QUANDO ARRIVANO LE PROSSIME CONFERME (limite inferiore) ---
  ARCUSDT|gen_96c1ed1b               3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 24 Sep 21:20
  ATOMUSDT|gen_eaa569ba              3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 24 Sep 21:20
  AVAAIUSDT|gen_14e1775b             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 24 Sep 21:20
  AVAAIUSDT|gen_68ebd3b9             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 24 Sep 21:20
  AXSUSDT|gen_b922252e               3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 24 Sep 21:20
  B2USDT|gen_ddb3def9                3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 24 Sep 21:20
  BICOUSDT|gen_f238d283              4/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 24 Sep 21:20
  BTRUSDT|gen_8981d5f2               3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 24 Sep 21:20
  BULLAUSDT|gen_2e8fb80a             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 24 Sep 21:20
  BULLAUSDT|gen_3f1b628b             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 24 Sep 21:20
  BULLAUSDT|gen_6df6961d             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 24 Sep 21:20
  BULLAUSDT|gen_7ac562e3             3/3 pass · GIA' VALIDATA · ultimo pass 22 Sep 00:00 · finestra chiusa il 29 Sep 00:00 · vista 24 Sep 21:20
  BULLAUSDT|gen_c8aa0d13             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 24 Sep 21:20
  DEXEUSDT|gen_887d87df              3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 24 Sep 21:20
  DEXEUSDT|gen_b31d8b93              3/3 pass · GIA' VALIDATA · ultimo pass 18 Sep 00:00 · finestra chiusa il 25 Sep 00:00 · vista 24 Sep 21:20

--- QUANDO RIPARTE IL BOT ---
  Al piu' presto il — (fra -20720.9 giorni), quando la 10a coppia
  raggiungerebbe 3 pass.
  E' un LIMITE INFERIORE: assume che ognuna passi almeno una volta per
  finestra settimanale. Chi non passa per 2 finestre intere esce dal registro,
  quindi la data vera puo' essere piu' in la'. Serve anche coprire >= 5 coin distinte (10 coppie
  su coin diverse bastano).
```
