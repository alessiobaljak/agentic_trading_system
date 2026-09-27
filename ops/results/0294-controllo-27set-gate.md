# 0294-controllo-27set-gate.req

_eseguito: 2026-09-27 06:12 UTC_

**richiesta:** `gate`
**eseguito:** `.venv/bin/python -m scripts.gate_progress`
**esito:** codice 0 in 1.7s

```
[firebase] connesso (Firestore + RTDB)
[gate] 2715 coppie nel registro · 1371 ancora valutate · soglia 3 pass · un pass ogni 168h di dati nuovi
  distribuzione pass (solo coppie vive): 1 pass: 649 su 132 coin · 2 pass: 508 su 124 coin · 3 pass: 162 su 63 coin · 4 pass: 52 su 25 coin
  CONGELATE: 1344 coppie non piu' valutate da oltre 3 giorni (1 avevano gia' un passaggio).
  La coin e' uscita dall'universo — di solito per storia insufficiente o delisting.
  Non avanzano e non falliscono: sono escluse da tutti i conti qui sotto.
  COMPOSIZIONE (vive): 0 base · 1371 generate.  Nel registro intero: 1344 base su 2715, tetto 3000.
  fallimenti accumulati: 1 fallimenti: 36
  VALIDATE ora: 212 su 68 coin distinte
  ready dichiarato dal registro: True (via numero coppie)
     copertura 34.0% su obiettivo 35% · via a conteggio: 10 coppie (0 = spenta) · minimi 10 coin nell'universo, 5 coperte
     deciso il 27 Sep 06:03 su 212 validate / 68 coin coperte / universo 200 · minimi ok: True · copertura ok: False · conteggio ok: True
  FINESTRE APERTE: 1371/1371 coppie con almeno un passaggio.
  E' QUESTO il numero da guardare: solo queste stanno contando i giorni verso la
  conferma successiva, e solo queste compaiono nel calendario qui sotto.
  Le altre 0 sono ferme: la finestra si apre solo quando la coppia RIPASSA
  il gate, quindi per loro la prossima conferma non ha una data — dipende da un
  evento che potrebbe non succedere.

  STATISTICA t DELLE VALIDATE: 29 con misura · 15 reggerebbero t >= 2 · mediana 2.12 · le piu' basse: NEIROUSDT|gen_e132204b (1.02), JTOUSDT|gen_35632db9 (1.16), MUBARAKUSDT|gen_1e2af031 (1.24)
  (misurata, non usata per decidere: si decide dopo averla vista)

  A UN PASSO DALLA VALIDAZIONE: 508 coppie a 2/3.
  Di queste, 1 su 1 coin hanno GIA' la finestra scaduta: si
  validano al primo run in cui ripassano il gate, cioe' potenzialmente oggi.
  Le altre diventano idonee: 244 il 01 Oct 00:00 · 50 il 02 Oct 00:00 · 39 il 03 Oct 00:00 · 118 il 04 Oct 00:00 · 43 il 28 Sep 00:00 · 7 il 29 Sep 00:00 · 6 il 30 Sep 00:00
  spazio registro: 429 KiB su 879 (49%)
    162 byte a coppia · ci stanno ancora ~2846 coppie oltre le 2715 di adesso
  spazio spec scoperte: 128 KiB su 879 (15%)

  TEMPO DELL'ULTIMO GIRO (discovery): 1h 13m · iniziato 27 Sep 03:06 UTC · finito 04:19 UTC
  ULTIMO GIRO: 22560 valutazioni · 59 coppie passate · solo urgenti · 240 coin
  GIRO RIDOTTO: no, tutte le spec su tutte le coin (solo urgenti)
  IL CERVELLO NELL'ULTIMO GIRO: intorno 0 madri / 0 figlie passate / 0 promosse / 0 senza margine · varianti 2 create / 0 passate / 0 con conferme retroattive / 0 promosse / 0 scartate / sostituzioni nessuna
  KEEP DEL LOCK (scelto dal gate per coppia): 0.35 x10 · 0.5 x2 · 0.65 x2 · 0.75 x13 · non ancora rivalutate x185
  DECLASSATE: 0 validate a un quarto di size (bocciate 2 notti di fila) · tornate piene nel giro 0 · nuove nel giro 0 (contatori fermi: giro solo urgenti)
  ESPLORATIVE: 55 attive · validate poi 1 · scartate 64
  IPOTESI PER TIPO: conferma_trend 1 nate / 1 varianti / 0 passate / 0 validate / 1 bocciate · ingresso_atr_pct 1 nate / 0 varianti / 0 passate / 0 validate / 0 bocciate · solo_long 1 nate / 1 varianti / 0 passate / 0 validate / 1 bocciate · solo_short 1 nate / 1 varianti / 0 passate / 0 validate / 1 bocciate · tasso figlie 0% (0/3 spec) contro 0.3% delle candidate dell'ultimo giro (5/1577 coppie coin x spec, gate_autopsy/discover: unita' diverse)
  PASSATA A 1 ORA (19 coin): 5m · 1577 valutazioni · 5 passate

  RI-VALUTAZIONE (ultimo run discovery, solo urgenti): 31 spec su 567 note · cap 500 · 517 con almeno una conferma
  536 spec restano fuori dal taglio: sono ferme, non in attesa.
  Quelle con conferme passano comunque, quindi il taglio tocca solo candidate a zero passaggi.

--- QUANDO ARRIVANO LE PROSSIME CONFERME (limite inferiore) ---
  ARCUSDT|gen_96c1ed1b               3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 27 Sep 04:19
  ATOMUSDT|gen_eaa569ba              3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 27 Sep 04:19
  AVAAIUSDT|gen_14e1775b             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 27 Sep 04:19
  AVAAIUSDT|gen_68ebd3b9             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 27 Sep 04:19
  AVAAIUSDT|gen_e50a9211             3/3 pass · GIA' VALIDATA · ultimo pass 27 Sep 00:00 · finestra chiusa il 04 Oct 00:00 · vista 27 Sep 04:19
  AXSUSDT|gen_b922252e               3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 27 Sep 04:19
  B2USDT|gen_ddb3def9                3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 27 Sep 04:19
  BANKUSDT|gen_1efbb088              3/3 pass · GIA' VALIDATA · ultimo pass 27 Sep 00:00 · finestra chiusa il 04 Oct 00:00 · vista 27 Sep 04:19
  BANKUSDT|gen_fb3d971f              3/3 pass · GIA' VALIDATA · ultimo pass 27 Sep 00:00 · finestra chiusa il 04 Oct 00:00 · vista 27 Sep 04:19
  BICOUSDT|gen_2e6776ad              3/3 pass · GIA' VALIDATA · ultimo pass 25 Sep 00:00 · finestra chiusa il 02 Oct 00:00 · vista 27 Sep 06:09
  BICOUSDT|gen_35632db9              3/3 pass · GIA' VALIDATA · ultimo pass 25 Sep 00:00 · finestra chiusa il 02 Oct 00:00 · vista 27 Sep 06:09
  BICOUSDT|gen_f238d283              4/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 27 Sep 06:09
  BTRUSDT|gen_8981d5f2               3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 27 Sep 04:19
  BULLAUSDT|gen_2e8fb80a             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 27 Sep 04:19
  BULLAUSDT|gen_3f1b628b             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 27 Sep 04:19

--- QUANDO RIPARTE IL BOT ---
  Al piu' presto il — (fra -20723.3 giorni), quando la 10a coppia
  raggiungerebbe 3 pass.
  E' un LIMITE INFERIORE: assume che ognuna passi almeno una volta per
  finestra settimanale. Chi non passa per 2 finestre intere esce dal registro,
  quindi la data vera puo' essere piu' in la'. Serve anche coprire >= 5 coin distinte (10 coppie
  su coin diverse bastano).
```
