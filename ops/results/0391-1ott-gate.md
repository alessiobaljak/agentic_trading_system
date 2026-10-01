# 0391-1ott-gate.req

_eseguito: 2026-10-01 06:13 UTC_

**richiesta:** `gate`
**eseguito:** `.venv/bin/python -m scripts.gate_progress`
**esito:** codice 0 in 1.8s

```
[firebase] connesso (Firestore + RTDB)
[gate] 1631 coppie nel registro · 1630 ancora valutate · soglia 3 pass · un pass ogni 168h di dati nuovi
  distribuzione pass (solo coppie vive): 0 pass: 341 su 97 coin · 1 pass: 457 su 111 coin · 2 pass: 613 su 129 coin · 3 pass: 175 su 67 coin · 4 pass: 42 su 20 coin · 5 pass: 2 su 1 coin
  CONGELATE: 1 coppie non piu' valutate da oltre 3 giorni (1 avevano gia' un passaggio).
  La coin e' uscita dall'universo — di solito per storia insufficiente o delisting.
  Non avanzano e non falliscono: sono escluse da tutti i conti qui sotto.
  COMPOSIZIONE (vive): 0 base · 1630 generate.  Nel registro intero: 1 base su 1631, tetto 3000.
  fallimenti accumulati: 1 fallimenti: 311
  VALIDATE ora: 208 su 71 coin distinte
  ready dichiarato dal registro: True (via copertura)
     copertura 35.5% su obiettivo 35% · via a conteggio: 10 coppie (0 = spenta) · minimi 10 coin nell'universo, 5 coperte
     deciso il 01 Oct 04:52 su 208 validate / 71 coin coperte / universo 200 · minimi ok: True · copertura ok: True · conteggio ok: True
  FINESTRE APERTE: 1289/1289 coppie con almeno un passaggio.
  E' QUESTO il numero da guardare: solo queste stanno contando i giorni verso la
  conferma successiva, e solo queste compaiono nel calendario qui sotto.
  Le altre 0 sono ferme: la finestra si apre solo quando la coppia RIPASSA
  il gate, quindi per loro la prossima conferma non ha una data — dipende da un
  evento che potrebbe non succedere.

  STATISTICA t DELLE VALIDATE: 51 con misura · 35 reggerebbero t >= 2 · mediana 2.26 · le piu' basse: SAHARAUSDT|gen_95aff747 (1.24), AVAAIUSDT|gen_e50a9211 (1.26), MUBARAKUSDT|gen_1e2af031 (1.32)
  (misurata, non usata per decidere: si decide dopo averla vista)

  A UN PASSO DALLA VALIDAZIONE: 613 coppie a 2/3.
  Di queste, 4 su 4 coin hanno GIA' la finestra scaduta: si
  validano al primo run in cui ripassano il gate, cioe' potenzialmente oggi.
  Le altre diventano idonee: 42 il 02 Oct 00:00 · 31 il 03 Oct 00:00 · 85 il 04 Oct 00:00 · 89 il 05 Oct 00:00 · 58 il 06 Oct 00:00 · 73 il 07 Oct 00:00 · 231 il 08 Oct 00:00
  spazio registro: 476 KiB su 879 (54%)
    299 byte a coppia · ci stanno ancora ~1380 coppie oltre le 1631 di adesso
  spazio spec scoperte: 171 KiB su 879 (19%)

  TEMPO DELL'ULTIMO GIRO (discovery): 2h 58m · iniziato 01 Oct 01:53 UTC · finito 04:52 UTC
  ULTIMO GIRO: 41419 valutazioni · 356 coppie passate · completa · 242 coin
  GIRO RIDOTTO: 575 spec note su 183 coin proprie + fetta 1/7 · ~46599 valutazioni stimate contro 41419 fatte
  IL CERVELLO NELL'ULTIMO GIRO: intorno 3 madri / 3 figlie passate / 0 promosse / 1 senza margine / 2 senza conferme retroattive o seconde figlie · varianti 3 create / 3 passate / 0 con conferme retroattive / 0 promosse / 3 scartate / sostituzioni nessuna
  KEEP DEL LOCK (scelto dal gate per coppia): 0.35 x14 · 0.5 x11 · 0.65 x10 · 0.75 x14 · non ancora rivalutate x159
  DECLASSATE: 162 validate a un quarto di size (bocciate 2 notti di fila) · tornate piene nel giro 0 · nuove nel giro 2
  FEATURE session: 0 validate su 208 usano la sessione oraria (fino al 27 set valutata con l'orologio del giro, non della candela: passaggi da rifare) · 347 azzerate il 27 set, ripassano da zero
  ESPLORATIVE: 35 attive · validate poi 0 · scartate 200
  IPOTESI PER TIPO: conferma_trend 1 nate / 1 varianti / 0 passate / 0 validate / 1 bocciate · ingresso_atr_pct 1 nate / 0 varianti / 0 passate / 0 validate / 0 bocciate · solo_long 1 nate / 1 varianti / 0 passate / 0 validate / 1 bocciate · solo_short 2 nate / 2 varianti / 0 passate / 0 validate / 2 bocciate · tasso figlie 0% (0/4 spec) contro 1.8% delle candidate dell'ultimo giro (98/5550 coppie coin x spec, gate_autopsy/discover: unita' diverse)
  PASSATA A 1 ORA (30 coin): 7m · 5550 valutazioni · 98 passate

  RI-VALUTAZIONE (ultimo run discovery, completa): 671 spec su 721 note · cap 500 · 671 con almeno una conferma
  50 spec restano fuori dal taglio: sono ferme, non in attesa.
  Quelle con conferme passano comunque, quindi il taglio tocca solo candidate a zero passaggi.

--- QUANDO ARRIVANO LE PROSSIME CONFERME (limite inferiore) ---
  AIOUSDT|gen_581d4a68               3/3 pass · GIA' VALIDATA · ultimo pass 28 Sep 00:00 · finestra chiusa il 05 Oct 00:00 · vista 01 Oct 04:52
  ARCUSDT|gen_96c1ed1b               3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 08 Oct 00:00 · vista 01 Oct 04:52 · 1 fallimenti di fila
  ATOMUSDT|gen_eaa569ba              3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 08 Oct 00:00 · vista 01 Oct 04:52 · 1 fallimenti di fila
  AVAAIUSDT|gen_14e1775b             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 08 Oct 00:00 · vista 01 Oct 05:00 · 1 fallimenti di fila
  AVAAIUSDT|gen_68ebd3b9             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 08 Oct 00:00 · vista 01 Oct 05:00 · 1 fallimenti di fila
  AVAAIUSDT|gen_e50a9211             3/3 pass · GIA' VALIDATA · ultimo pass 27 Sep 00:00 · finestra chiusa il 04 Oct 00:00 · vista 01 Oct 05:00
  AXSUSDT|gen_b922252e               3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 08 Oct 00:00 · vista 01 Oct 04:52 · 1 fallimenti di fila
  B2USDT|gen_ddb3def9                3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 08 Oct 00:00 · vista 01 Oct 04:52 · 1 fallimenti di fila
  BANKUSDT|gen_1efbb088              3/3 pass · GIA' VALIDATA · ultimo pass 27 Sep 00:00 · finestra chiusa il 04 Oct 00:00 · vista 01 Oct 05:00
  BANKUSDT|gen_fb3d971f              3/3 pass · GIA' VALIDATA · ultimo pass 27 Sep 00:00 · finestra chiusa il 04 Oct 00:00 · vista 01 Oct 05:00
  BMTUSDT|gen_571cdda2               3/3 pass · GIA' VALIDATA · ultimo pass 28 Sep 00:00 · finestra chiusa il 05 Oct 00:00 · vista 01 Oct 04:52
  BMTUSDT|gen_cee79cdd               3/3 pass · GIA' VALIDATA · ultimo pass 28 Sep 00:00 · finestra chiusa il 05 Oct 00:00 · vista 01 Oct 04:52
  BTRUSDT|gen_8981d5f2               3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 08 Oct 00:00 · vista 01 Oct 04:52 · 1 fallimenti di fila
  BULLAUSDT|gen_2e8fb80a             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 08 Oct 00:00 · vista 01 Oct 05:00 · 1 fallimenti di fila
  BULLAUSDT|gen_3f1b628b             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 08 Oct 00:00 · vista 01 Oct 05:00 · 1 fallimenti di fila

--- QUANDO RIPARTE IL BOT ---
  Al piu' presto il — (fra -20727.3 giorni), quando la 10a coppia
  raggiungerebbe 3 pass.
  E' un LIMITE INFERIORE: assume che ognuna passi almeno una volta per
  finestra settimanale. Chi non passa per 2 finestre intere esce dal registro,
  quindi la data vera puo' essere piu' in la'. Serve anche coprire >= 5 coin distinte (10 coppie
  su coin diverse bastano).
```
