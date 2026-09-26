# 0282-giro-completo-gate-4.req

_eseguito: 2026-09-26 13:10 UTC_

**richiesta:** `gate`
**eseguito:** `.venv/bin/python -m scripts.gate_progress`
**esito:** codice 0 in 2.3s

```
[firebase] connesso (Firestore + RTDB)
[gate] 2783 coppie nel registro · 1343 ancora valutate · soglia 3 pass · un pass ogni 168h di dati nuovi
  distribuzione pass (solo coppie vive): 1 pass: 739 su 142 coin · 2 pass: 421 su 113 coin · 3 pass: 137 su 57 coin · 4 pass: 46 su 23 coin
  CONGELATE: 1440 coppie non piu' valutate da oltre 3 giorni (1 avevano gia' un passaggio).
  La coin e' uscita dall'universo — di solito per storia insufficiente o delisting.
  Non avanzano e non falliscono: sono escluse da tutti i conti qui sotto.
  COMPOSIZIONE (vive): 0 base · 1343 generate.  Nel registro intero: 1440 base su 2783, tetto 3000.
  fallimenti accumulati: 1 fallimenti: 4
  VALIDATE ora: 182 su 62 coin distinte
  ready dichiarato dal registro: True (via numero coppie)
     copertura 31.0% su obiettivo 35% · via a conteggio: 10 coppie (0 = spenta) · minimi 10 coin nell'universo, 5 coperte
     deciso il 26 Sep 12:55 su 182 validate / 62 coin coperte / universo 200 · minimi ok: True · copertura ok: False · conteggio ok: True
  FINESTRE APERTE: 1343/1343 coppie con almeno un passaggio.
  E' QUESTO il numero da guardare: solo queste stanno contando i giorni verso la
  conferma successiva, e solo queste compaiono nel calendario qui sotto.
  Le altre 0 sono ferme: la finestra si apre solo quando la coppia RIPASSA
  il gate, quindi per loro la prossima conferma non ha una data — dipende da un
  evento che potrebbe non succedere.

  STATISTICA t DELLE VALIDATE: 18 con misura · 8 reggerebbero t >= 2 · mediana 1.97 · le piu' basse: NEIROUSDT|gen_e132204b (1.02), JTOUSDT|gen_35632db9 (1.16), SAHARAUSDT|gen_95aff747 (1.28)
  (misurata, non usata per decidere: si decide dopo averla vista)

  A UN PASSO DALLA VALIDAZIONE: 421 coppie a 2/3.
  Di queste, 4 su 2 coin hanno GIA' la finestra scaduta: si
  validano al primo run in cui ripassano il gate, cioe' potenzialmente oggi.
  Le altre diventano idonee: 244 il 01 Oct 00:00 · 50 il 02 Oct 00:00 · 39 il 03 Oct 00:00 · 28 il 27 Sep 00:00 · 43 il 28 Sep 00:00 · 7 il 29 Sep 00:00 · 6 il 30 Sep 00:00
  spazio registro: 419 KiB su 879 (48%)
    154 byte a coppia · ci stanno ancora ~3048 coppie oltre le 2783 di adesso
  spazio spec scoperte: 123 KiB su 879 (14%)

  TEMPO DELL'ULTIMO GIRO (discovery): 3h 48m · iniziato 26 Sep 09:06 UTC · finito 12:55 UTC  ← SFORA la finestra di 3h
  IL CERVELLO NELL'ULTIMO GIRO: intorno 40 madri / 5 figlie passate / 0 promosse / 1 senza margine / 4 senza conferme retroattive o seconde figlie · varianti 2 create / 0 passate / 0 con conferme retroattive / 0 promosse / 0 scartate / sostituzioni nessuna
  KEEP DEL LOCK (scelto dal gate per coppia): 0.35 x6 · 0.5 x1 · 0.65 x2 · 0.75 x6 · non ancora rivalutate x167
  ESPLORATIVE: 34 attive · validate poi 0 · scartate 31
  IPOTESI PER TIPO: solo_long 1 nate / 1 varianti / 0 passate / 0 validate / 1 bocciate · solo_short 1 nate / 1 varianti / 0 passate / 0 validate / 1 bocciate · tasso figlie 0% (0/2 spec) contro 0.2% delle candidate dell'ultimo giro (1/460 coppie coin x spec, gate_autopsy/discover: unita' diverse)
  PASSATA A 1 ORA (5 coin): 2m · 460 valutazioni · 1 passate

  RI-VALUTAZIONE (ultimo run discovery, completa): 502 spec su 552 note · cap 500 · 502 con almeno una conferma
  50 spec restano fuori dal taglio: sono ferme, non in attesa.
  Quelle con conferme passano comunque, quindi il taglio tocca solo candidate a zero passaggi.

--- QUANDO ARRIVANO LE PROSSIME CONFERME (limite inferiore) ---
  ARCUSDT|gen_96c1ed1b               3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 26 Sep 12:55
  ATOMUSDT|gen_eaa569ba              3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 26 Sep 12:55
  AVAAIUSDT|gen_14e1775b             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 26 Sep 12:55
  AVAAIUSDT|gen_68ebd3b9             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 26 Sep 12:55
  AXSUSDT|gen_b922252e               3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 26 Sep 12:55
  B2USDT|gen_ddb3def9                3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 26 Sep 12:55
  BICOUSDT|gen_2e6776ad              3/3 pass · GIA' VALIDATA · ultimo pass 25 Sep 00:00 · finestra chiusa il 02 Oct 00:00 · vista 26 Sep 12:55
  BICOUSDT|gen_35632db9              3/3 pass · GIA' VALIDATA · ultimo pass 25 Sep 00:00 · finestra chiusa il 02 Oct 00:00 · vista 26 Sep 12:55
  BICOUSDT|gen_f238d283              4/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 26 Sep 12:55
  BTRUSDT|gen_8981d5f2               3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 26 Sep 12:55
  BULLAUSDT|gen_2e8fb80a             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 26 Sep 12:55
  BULLAUSDT|gen_3f1b628b             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 26 Sep 12:55
  BULLAUSDT|gen_6df6961d             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 26 Sep 12:55
  BULLAUSDT|gen_7ac562e3             3/3 pass · GIA' VALIDATA · ultimo pass 22 Sep 00:00 · finestra chiusa il 29 Sep 00:00 · vista 26 Sep 12:55
  BULLAUSDT|gen_c8aa0d13             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 26 Sep 12:55

--- QUANDO RIPARTE IL BOT ---
  Al piu' presto il — (fra -20722.5 giorni), quando la 10a coppia
  raggiungerebbe 3 pass.
  E' un LIMITE INFERIORE: assume che ognuna passi almeno una volta per
  finestra settimanale. Chi non passa per 2 finestre intere esce dal registro,
  quindi la data vera puo' essere piu' in la'. Serve anche coprire >= 5 coin distinte (10 coppie
  su coin diverse bastano).
```
