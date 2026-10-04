# 0468-4ott-mattina-gate.req

_eseguito: 2026-10-04 06:05 UTC_

**richiesta:** `gate`
**eseguito:** `.venv/bin/python -m scripts.gate_progress`
**esito:** codice 0 in 1.9s

```
[firebase] connesso (Firestore + RTDB)
[gate] 1947 coppie nel registro · 1946 ancora valutate · soglia 3 pass · un pass ogni 168h di dati nuovi
  distribuzione pass (solo coppie vive): 0 pass: 339 su 97 coin · 1 pass: 625 su 112 coin · 2 pass: 747 su 140 coin · 3 pass: 174 su 70 coin · 4 pass: 53 su 26 coin · 5 pass: 8 su 5 coin
  CONGELATE: 1 coppie non piu' valutate da oltre 3 giorni (1 avevano gia' un passaggio).
  La coin e' uscita dall'universo — di solito per storia insufficiente o delisting.
  Non avanzano e non falliscono: sono escluse da tutti i conti qui sotto.
  COMPOSIZIONE (vive): 0 base · 1946 generate.  Nel registro intero: 1 base su 1947, tetto 3000.
  fallimenti accumulati: 1 fallimenti: 512
  VALIDATE ora: 223 su 76 coin distinte
  ready dichiarato dal registro: True (via copertura)
     copertura 38.0% su obiettivo 35% · via a conteggio: 10 coppie (0 = spenta) · minimi 10 coin nell'universo, 5 coperte
     deciso il 04 Oct 06:04 su 223 validate / 76 coin coperte / universo 200 · minimi ok: True · copertura ok: True · conteggio ok: True
  FINESTRE APERTE: 1607/1607 coppie con almeno un passaggio.
  E' QUESTO il numero da guardare: solo queste stanno contando i giorni verso la
  conferma successiva, e solo queste compaiono nel calendario qui sotto.
  Le altre 0 sono ferme: la finestra si apre solo quando la coppia RIPASSA
  il gate, quindi per loro la prossima conferma non ha una data — dipende da un
  evento che potrebbe non succedere.

  STATISTICA t DELLE VALIDATE: 71 con misura · 48 reggerebbero t >= 2 · mediana 2.19 · le piu' basse: AVAAIUSDT|gen_dbe19eb2 (1.26), AVAAIUSDT|gen_e50a9211 (1.26), AINUSDT|gen_ef115241 (1.29)
  (misurata, non usata per decidere: si decide dopo averla vista)

  A UN PASSO DALLA VALIDAZIONE: 747 coppie a 2/3.
  Di queste, 1 su 1 coin hanno GIA' la finestra scaduta: si
  validano al primo run in cui ripassano il gate, cioe' potenzialmente oggi.
  Le altre diventano idonee: 89 il 05 Oct 00:00 · 58 il 06 Oct 00:00 · 73 il 07 Oct 00:00 · 231 il 08 Oct 00:00 · 97 il 09 Oct 00:00 · 88 il 10 Oct 00:00 · 110 il 11 Oct 00:00
  spazio registro: 576 KiB su 879 (66%)
    303 byte a coppia · ci stanno ancora ~1021 coppie oltre le 1947 di adesso
  spazio spec scoperte: 223 KiB su 879 (25%)

  TEMPO DELL'ULTIMO GIRO (discovery): 1h 45m · iniziato 04 Oct 03:53 UTC · finito 05:38 UTC
  ULTIMO GIRO: 20667 valutazioni · 25 coppie passate · solo urgenti · 249 coin
  GIRO RIDOTTO: no, tutte le spec su tutte le coin (solo urgenti)
  IL CERVELLO NELL'ULTIMO GIRO: intorno 0 madri / 0 figlie passate / 0 promosse / 0 senza margine · varianti 0 create / 0 passate / 0 con conferme retroattive / 0 promosse / 0 scartate / sostituzioni nessuna
  KEEP DEL LOCK (scelto dal gate per coppia): 0.35 x23 · 0.5 x16 · 0.65 x15 · 0.75 x14 · non ancora rivalutate x155
  DECLASSATE: 169 validate a un quarto di size (bocciate 2 notti di fila) · tornate piene nel giro 0 · nuove nel giro 0 (contatori fermi: giro solo urgenti)
  FEATURE session: 0 validate su 223 usano la sessione oraria (fino al 27 set valutata con l'orologio del giro, non della candela: passaggi da rifare) · 347 azzerate il 27 set, ripassano da zero
  ESPLORATIVE: 48 attive · validate poi 3 · scartate 327
  IPOTESI PER TIPO: conferma_trend 1 nate / 1 varianti / 0 passate / 0 validate / 1 bocciate · ingresso_atr_pct 1 nate / 0 varianti / 0 passate / 0 validate / 0 bocciate · scala_stretta 1 nate / 0 varianti / 0 passate / 0 validate / 0 bocciate · solo_long 1 nate / 1 varianti / 0 passate / 0 validate / 1 bocciate · solo_short 3 nate / 2 varianti / 0 passate / 0 validate / 2 bocciate · tasso figlie 0% (0/4 spec) contro 0.1% delle candidate dell'ultimo giro (25/20667 coppie coin x spec, gate_autopsy/discover: unita' diverse)
  PASSATA A 1 ORA (30 coin): 9m · 9840 valutazioni · 218 passate
  ORIGINI (le idee AI servono? si contano le coppie, non l'R; fonte: registro + discovered_strategies/specs)
    AI: 115 nel registro / 1 validate / 0 declassate · casuali (e mutazioni): 1817 nel registro / 211 validate / 167 declassate · intorno: 14 nel registro / 11 validate / 2 declassate · base: 1 nel registro / 0 validate / 0 declassate
    candidate dell'ultimo giro: nuove ai 0 · casuali 40 · mutazioni 30 · varianti 0; note rivalutate casuali (e mutazioni) 11 · AI 2
    candidate della passata a 1 ora: nuove ai 0 · casuali 40 · mutazioni 29 · varianti 0; note rivalutate casuali (e mutazioni) 211 · AI 48

  RI-VALUTAZIONE (ultimo run discovery, solo urgenti): 16 spec su 950 note · cap 500 · 894 con almeno una conferma
  934 spec restano fuori dal taglio: sono ferme, non in attesa.
  Quelle con conferme passano comunque, quindi il taglio tocca solo candidate a zero passaggi.

--- QUANDO ARRIVANO LE PROSSIME CONFERME (limite inferiore) ---
  AINUSDT|gen_ef115241               3/3 pass · GIA' VALIDATA · ultimo pass 04 Oct 00:00 · finestra chiusa il 11 Oct 00:00 · vista 04 Oct 05:38
  AIOUSDT|gen_581d4a68               3/3 pass · GIA' VALIDATA · ultimo pass 28 Sep 00:00 · finestra chiusa il 05 Oct 00:00 · vista 04 Oct 05:38
  ARCUSDT|gen_96c1ed1b               3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 08 Oct 00:00 · vista 04 Oct 05:38 · 1 fallimenti di fila
  ATOMUSDT|gen_eaa569ba              3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 08 Oct 00:00 · vista 04 Oct 05:38 · 1 fallimenti di fila
  AVAAIUSDT|gen_14e1775b             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 08 Oct 00:00 · vista 04 Oct 05:38 · 1 fallimenti di fila
  AVAAIUSDT|gen_68ebd3b9             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 08 Oct 00:00 · vista 04 Oct 05:38 · 1 fallimenti di fila
  AVAAIUSDT|gen_dbe19eb2             3/3 pass · GIA' VALIDATA · ultimo pass 01 Oct 00:00 · finestra chiusa il 08 Oct 00:00 · vista 04 Oct 05:38
  AVAAIUSDT|gen_e50a9211             4/3 pass · GIA' VALIDATA · ultimo pass 04 Oct 00:00 · finestra chiusa il 11 Oct 00:00 · vista 04 Oct 05:38
  AXSUSDT|gen_b922252e               3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 08 Oct 00:00 · vista 04 Oct 05:38 · 1 fallimenti di fila
  B2USDT|gen_ddb3def9                3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 08 Oct 00:00 · vista 04 Oct 05:38 · 1 fallimenti di fila
  BANKUSDT|gen_1efbb088              3/3 pass · GIA' VALIDATA · ultimo pass 27 Sep 00:00 · finestra chiusa il 11 Oct 00:00 · vista 04 Oct 05:38 · 1 fallimenti di fila
  BANKUSDT|gen_fb3d971f              3/3 pass · GIA' VALIDATA · ultimo pass 27 Sep 00:00 · finestra chiusa il 11 Oct 00:00 · vista 04 Oct 05:38 · 1 fallimenti di fila
  BMTUSDT|gen_571cdda2               3/3 pass · GIA' VALIDATA · ultimo pass 28 Sep 00:00 · finestra chiusa il 05 Oct 00:00 · vista 04 Oct 05:38
  BMTUSDT|gen_cee79cdd               3/3 pass · GIA' VALIDATA · ultimo pass 28 Sep 00:00 · finestra chiusa il 05 Oct 00:00 · vista 04 Oct 05:38
  BRUSDT|gen_95fb50ce                3/3 pass · GIA' VALIDATA · ultimo pass 03 Oct 00:00 · finestra chiusa il 10 Oct 00:00 · vista 04 Oct 05:38

--- QUANDO RIPARTE IL BOT ---
  Al piu' presto il — (fra -20730.3 giorni), quando la 10a coppia
  raggiungerebbe 3 pass.
  E' un LIMITE INFERIORE: assume che ognuna passi almeno una volta per
  finestra settimanale. Chi non passa per 2 finestre intere esce dal registro,
  quindi la data vera puo' essere piu' in la'. Serve anche coprire >= 5 coin distinte (10 coppie
  su coin diverse bastano).
```
