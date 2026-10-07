# 0526-7ott-mattina-gate.req

_eseguito: 2026-10-07 06:05 UTC_

**richiesta:** `gate`
**eseguito:** `.venv/bin/python -m scripts.gate_progress`
**esito:** codice 0 in 2.0s

```
[firebase] connesso (Firestore + RTDB)
[gate] 2233 coppie nel registro · 2232 ancora valutate · soglia 3 pass · un pass ogni 168h di dati nuovi
  distribuzione pass (solo coppie vive): 0 pass: 336 su 96 coin · 1 pass: 802 su 132 coin · 2 pass: 797 su 146 coin · 3 pass: 216 su 77 coin · 4 pass: 71 su 34 coin · 5 pass: 10 su 6 coin
  CONGELATE: 1 coppie non piu' valutate da oltre 3 giorni (1 avevano gia' un passaggio).
  La coin e' uscita dall'universo — di solito per storia insufficiente o delisting.
  Non avanzano e non falliscono: sono escluse da tutti i conti qui sotto.
  COMPOSIZIONE (vive): 0 base · 2232 generate.  Nel registro intero: 1 base su 2233, tetto 3000.
  fallimenti accumulati: 1 fallimenti: 736
  VALIDATE ora: 279 su 84 coin distinte
  ready dichiarato dal registro: True (via copertura)
     copertura 42.0% su obiettivo 35% · via a conteggio: 10 coppie (0 = spenta) · minimi 10 coin nell'universo, 5 coperte
     deciso il 07 Oct 04:51 su 279 validate / 84 coin coperte / universo 200 · minimi ok: True · copertura ok: True · conteggio ok: True
  FINESTRE APERTE: 1896/1896 coppie con almeno un passaggio.
  E' QUESTO il numero da guardare: solo queste stanno contando i giorni verso la
  conferma successiva, e solo queste compaiono nel calendario qui sotto.
  Le altre 0 sono ferme: la finestra si apre solo quando la coppia RIPASSA
  il gate, quindi per loro la prossima conferma non ha una data — dipende da un
  evento che potrebbe non succedere.

  STATISTICA t DELLE VALIDATE: 137 con misura · 98 reggerebbero t >= 2 · mediana 2.22 · le piu' basse: AINUSDT|gen_ef115241 (1.25), AVAAIUSDT|gen_dbe19eb2 (1.26), AVAAIUSDT|gen_e50a9211 (1.26)
  (misurata, non usata per decidere: si decide dopo averla vista)

  A UN PASSO DALLA VALIDAZIONE: 797 coppie a 2/3.
  Di queste, 30 su 17 coin hanno GIA' la finestra scaduta: si
  validano al primo run in cui ripassano il gate, cioe' potenzialmente oggi.
  Le altre diventano idonee: 231 il 08 Oct 00:00 · 97 il 09 Oct 00:00 · 88 il 10 Oct 00:00 · 110 il 11 Oct 00:00 · 89 il 12 Oct 00:00 · 77 il 13 Oct 00:00 · 75 il 14 Oct 00:00
  spazio registro: 692 KiB su 879 (79%)
    317 byte a coppia · ci stanno ancora ~603 coppie oltre le 2233 di adesso
  spazio spec scoperte: 270 KiB su 879 (31%)

  TEMPO DELL'ULTIMO GIRO (discovery): 3h 21m · iniziato 07 Oct 01:30 UTC · finito 04:51 UTC  ← SFORA la finestra di 3h
  ULTIMO GIRO: 45069 valutazioni · 456 coppie passate · completa · 256 coin
  GIRO RIDOTTO: 695 spec note su 201 coin proprie + fetta 7/7 · ~50264 valutazioni stimate contro 45069 fatte
  IL CERVELLO NELL'ULTIMO GIRO: intorno 40 madri / 42 figlie passate / 2 promosse (BULLAUSDT|gen_cec62f22, BULLAUSDT|gen_0eb59b31) / 7 senza margine / 1 con madre non valutata / 32 senza conferme retroattive o seconde figlie · varianti 0 create / 0 passate / 0 con conferme retroattive / 0 promosse / 0 scartate / sostituzioni nessuna
  KEEP DEL LOCK (scelto dal gate per coppia): 0.35 x36 · 0.5 x34 · 0.65 x44 · 0.75 x14 · non ancora rivalutate x151
  DECLASSATE: 182 validate a un quarto di size (bocciate 2 notti di fila) · tornate piene nel giro 1 · nuove nel giro 10
  FEATURE session: 0 validate su 279 usano la sessione oraria (fino al 27 set valutata con l'orologio del giro, non della candela: passaggi da rifare) · 347 azzerate il 27 set, ripassano da zero
  ESPLORATIVE: 36 attive · validate poi 4 · scartate 442
  IPOTESI PER TIPO: conferma_trend 3 nate / 1 varianti / 0 passate / 0 validate / 1 bocciate · controtrend_btc 1 nate / 0 varianti / 0 passate / 0 validate / 0 bocciate · ingresso_atr_pct 1 nate / 0 varianti / 0 passate / 0 validate / 0 bocciate · scala_stretta 2 nate / 0 varianti / 0 passate / 0 validate / 0 bocciate · solo_long 1 nate / 1 varianti / 0 passate / 0 validate / 1 bocciate · solo_short 3 nate / 2 varianti / 0 passate / 0 validate / 2 bocciate · tasso figlie 0% (0/4 spec) contro 1.1% delle candidate dell'ultimo giro (496/45069 coppie coin x spec, gate_autopsy/discover: unita' diverse)
  PASSATA A 1 ORA (30 coin): 15m · 14250 valutazioni · 317 passate
  ORIGINI (le idee AI servono? si contano le coppie, non l'R; fonte: registro + discovered_strategies/specs)
    AI: 115 nel registro / 3 validate / 1 declassate · casuali (e mutazioni): 2095 nel registro / 259 validate / 177 declassate · intorno: 22 nel registro / 17 validate / 4 declassate · base: 1 nel registro / 0 validate / 0 declassate
    candidate dell'ultimo giro: nuove ai 0 · casuali 40 · mutazioni 29 · varianti 0 · figlie dell'intorno 238; note rivalutate casuali (e mutazioni) 647 · AI 30 · intorno 18
    candidate della passata a 1 ora: nuove ai 0 · casuali 40 · mutazioni 30 · varianti 0; note rivalutate casuali (e mutazioni) 358 · AI 47

  RI-VALUTAZIONE (ultimo run discovery, completa): 1100 spec su 1159 note · cap 500 · 1100 con almeno una conferma
  59 spec restano fuori dal taglio: sono ferme, non in attesa.
  Quelle con conferme passano comunque, quindi il taglio tocca solo candidate a zero passaggi.

--- QUANDO ARRIVANO LE PROSSIME CONFERME (limite inferiore) ---
  1000BONKUSDT|gen_86a8b183          3/3 pass · GIA' VALIDATA · ultimo pass 05 Oct 00:00 · finestra chiusa il 12 Oct 00:00 · vista 07 Oct 04:51
  AINUSDT|gen_ef115241               3/3 pass · GIA' VALIDATA · ultimo pass 04 Oct 00:00 · finestra chiusa il 11 Oct 00:00 · vista 07 Oct 04:51
  AIOUSDT|gen_581d4a68               3/3 pass · GIA' VALIDATA · ultimo pass 28 Sep 00:00 · finestra chiusa il 12 Oct 00:00 · vista 07 Oct 04:51 · 1 fallimenti di fila
  AIOUSDT|gen_fc644cd2               3/3 pass · GIA' VALIDATA · ultimo pass 07 Oct 00:00 · finestra chiusa il 14 Oct 00:00 · vista 07 Oct 04:51
  ARCUSDT|gen_96c1ed1b               3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 08 Oct 00:00 · vista 07 Oct 04:51 · 1 fallimenti di fila
  ASTERUSDT|gen_96efce1b             3/3 pass · GIA' VALIDATA · ultimo pass 06 Oct 00:00 · finestra chiusa il 13 Oct 00:00 · vista 07 Oct 04:51
  ATOMUSDT|gen_eaa569ba              3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 08 Oct 00:00 · vista 07 Oct 04:51 · 1 fallimenti di fila
  AVAAIUSDT|gen_08c22b92             3/3 pass · GIA' VALIDATA · ultimo pass 05 Oct 00:00 · finestra chiusa il 12 Oct 00:00 · vista 07 Oct 05:06
  AVAAIUSDT|gen_14e1775b             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 08 Oct 00:00 · vista 07 Oct 05:06 · 1 fallimenti di fila
  AVAAIUSDT|gen_1eec02f5             3/3 pass · GIA' VALIDATA · ultimo pass 07 Oct 00:00 · finestra chiusa il 14 Oct 00:00 · vista 07 Oct 05:06
  AVAAIUSDT|gen_68ebd3b9             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 08 Oct 00:00 · vista 07 Oct 05:06 · 1 fallimenti di fila
  AVAAIUSDT|gen_dbe19eb2             3/3 pass · GIA' VALIDATA · ultimo pass 01 Oct 00:00 · finestra chiusa il 08 Oct 00:00 · vista 07 Oct 05:06
  AVAAIUSDT|gen_e50a9211             4/3 pass · GIA' VALIDATA · ultimo pass 04 Oct 00:00 · finestra chiusa il 11 Oct 00:00 · vista 07 Oct 05:06
  AXSUSDT|gen_b922252e               3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 08 Oct 00:00 · vista 07 Oct 04:51 · 1 fallimenti di fila
  B2USDT|gen_ddb3def9                3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 08 Oct 00:00 · vista 07 Oct 04:51 · 1 fallimenti di fila

--- QUANDO RIPARTE IL BOT ---
  Al piu' presto il — (fra -20733.3 giorni), quando la 10a coppia
  raggiungerebbe 3 pass.
  E' un LIMITE INFERIORE: assume che ognuna passi almeno una volta per
  finestra settimanale. Chi non passa per 2 finestre intere esce dal registro,
  quindi la data vera puo' essere piu' in la'. Serve anche coprire >= 5 coin distinte (10 coppie
  su coin diverse bastano).
```
