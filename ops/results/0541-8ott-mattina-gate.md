# 0541-8ott-mattina-gate.req

_eseguito: 2026-10-08 03:47 UTC_

**richiesta:** `gate`
**eseguito:** `.venv/bin/python -m scripts.gate_progress`
**esito:** codice 0 in 2.4s

```
[firebase] connesso (Firestore + RTDB)
[gate] 2340 coppie nel registro · 2339 ancora valutate · soglia 3 pass · un pass ogni 168h di dati nuovi
  distribuzione pass (solo coppie vive): 0 pass: 336 su 96 coin · 1 pass: 851 su 138 coin · 2 pass: 855 su 147 coin · 3 pass: 216 su 77 coin · 4 pass: 71 su 34 coin · 5 pass: 10 su 6 coin
  CONGELATE: 1 coppie non piu' valutate da oltre 3 giorni (1 avevano gia' un passaggio).
  La coin e' uscita dall'universo — di solito per storia insufficiente o delisting.
  Non avanzano e non falliscono: sono escluse da tutti i conti qui sotto.
  COMPOSIZIONE (vive): 0 base · 2339 generate.  Nel registro intero: 1 base su 2340, tetto 3000.
  fallimenti accumulati: 1 fallimenti: 749
  VALIDATE ora: 279 su 84 coin distinte
  ready dichiarato dal registro: True (via copertura)
     copertura 42.0% su obiettivo 35% · via a conteggio: 10 coppie (0 = spenta) · minimi 10 coin nell'universo, 5 coperte
     deciso il 08 Oct 02:06 su 279 validate / 84 coin coperte / universo 200 · minimi ok: True · copertura ok: True · conteggio ok: True
  FINESTRE APERTE: 2003/2003 coppie con almeno un passaggio.
  E' QUESTO il numero da guardare: solo queste stanno contando i giorni verso la
  conferma successiva, e solo queste compaiono nel calendario qui sotto.
  Le altre 0 sono ferme: la finestra si apre solo quando la coppia RIPASSA
  il gate, quindi per loro la prossima conferma non ha una data — dipende da un
  evento che potrebbe non succedere.

  STATISTICA t DELLE VALIDATE: 137 con misura · 98 reggerebbero t >= 2 · mediana 2.23 · le piu' basse: AINUSDT|gen_ef115241 (1.25), AVAAIUSDT|gen_dbe19eb2 (1.26), AVAAIUSDT|gen_e50a9211 (1.26)
  (misurata, non usata per decidere: si decide dopo averla vista)

  A UN PASSO DALLA VALIDAZIONE: 855 coppie a 2/3.
  Di queste, 261 su 95 coin hanno GIA' la finestra scaduta: si
  validano al primo run in cui ripassano il gate, cioe' potenzialmente oggi.
  Le altre diventano idonee: 97 il 09 Oct 00:00 · 88 il 10 Oct 00:00 · 110 il 11 Oct 00:00 · 89 il 12 Oct 00:00 · 77 il 13 Oct 00:00 · 75 il 14 Oct 00:00 · 58 il 15 Oct 00:00
  spazio registro: 725 KiB su 879 (83%)  ATTENZIONE:
    317 byte a coppia · ci stanno ancora ~496 coppie oltre le 2340 di adesso
  oltre il limite Firestore rifiuta la scrittura e il run perde
  le conferme appena guadagnate. Va alzato il tetto o alleggerito il documento.
  spazio spec scoperte: 283 KiB su 879 (32%)

  TEMPO DELL'ULTIMO GIRO (discovery): 4h 47m · iniziato 07 Oct 21:18 UTC · finito 02:06 UTC  ← SFORA la finestra di 3h
  ULTIMO GIRO: 81788 valutazioni · 228 coppie passate · solo urgenti · 254 coin
  GIRO RIDOTTO: no, tutte le spec su tutte le coin (solo urgenti)
  IL CERVELLO NELL'ULTIMO GIRO: intorno 0 madri / 1 figlie passate / 0 promosse / 0 senza margine / 1 senza conferme retroattive o seconde figlie · varianti 0 create / 0 passate / 0 con conferme retroattive / 0 promosse / 0 scartate / sostituzioni nessuna
  KEEP DEL LOCK (scelto dal gate per coppia): 0.35 x36 · 0.5 x34 · 0.65 x44 · 0.75 x14 · non ancora rivalutate x151
  DECLASSATE: 182 validate a un quarto di size (bocciate 2 notti di fila) · tornate piene nel giro 0 · nuove nel giro 0 (contatori fermi: giro solo urgenti)
  FEATURE session: 0 validate su 279 usano la sessione oraria (fino al 27 set valutata con l'orologio del giro, non della candela: passaggi da rifare) · 347 azzerate il 27 set, ripassano da zero
  ESPLORATIVE: 38 attive · validate poi 4 · scartate 468
  IPOTESI PER TIPO: conferma_trend 3 nate / 1 varianti / 0 passate / 0 validate / 1 bocciate · controtrend_btc 1 nate / 0 varianti / 0 passate / 0 validate / 0 bocciate · ingresso_atr_pct 1 nate / 0 varianti / 0 passate / 0 validate / 0 bocciate · scala_stretta 2 nate / 0 varianti / 0 passate / 0 validate / 0 bocciate · solo_long 1 nate / 1 varianti / 0 passate / 0 validate / 1 bocciate · solo_short 3 nate / 2 varianti / 0 passate / 0 validate / 2 bocciate · tasso figlie 0% (0/4 spec) contro 0.3% delle candidate dell'ultimo giro (229/81788 coppie coin x spec, gate_autopsy/discover: unita' diverse)
  PASSATA A 1 ORA (30 coin): 14m · 15360 valutazioni · 328 passate
  ORIGINI (le idee AI servono? si contano le coppie, non l'R; fonte: registro + discovered_strategies/specs)
    AI: 116 nel registro / 3 validate / 1 declassate · casuali (e mutazioni): 2201 nel registro / 259 validate / 177 declassate · intorno: 22 nel registro / 17 validate / 4 declassate · base: 1 nel registro / 0 validate / 0 declassate
    candidate dell'ultimo giro: nuove ai 0 · casuali 40 · mutazioni 22 · varianti 0; note rivalutate casuali (e mutazioni) 254 · AI 5 · intorno 1
    candidate della passata a 1 ora: nuove ai 0 · casuali 39 · mutazioni 28 · varianti 0; note rivalutate casuali (e mutazioni) 398 · AI 47

  RI-VALUTAZIONE (ultimo run discovery, solo urgenti): 346 spec su 1225 note · cap 500 · 1166 con almeno una conferma
  879 spec restano fuori dal taglio: sono ferme, non in attesa.
  Quelle con conferme passano comunque, quindi il taglio tocca solo candidate a zero passaggi.

--- QUANDO ARRIVANO LE PROSSIME CONFERME (limite inferiore) ---
  1000BONKUSDT|gen_86a8b183          3/3 pass · GIA' VALIDATA · ultimo pass 05 Oct 00:00 · finestra chiusa il 12 Oct 00:00 · vista 08 Oct 02:06
  AINUSDT|gen_ef115241               3/3 pass · GIA' VALIDATA · ultimo pass 04 Oct 00:00 · finestra chiusa il 11 Oct 00:00 · vista 08 Oct 02:06
  AIOUSDT|gen_581d4a68               3/3 pass · GIA' VALIDATA · ultimo pass 28 Sep 00:00 · finestra chiusa il 12 Oct 00:00 · vista 08 Oct 02:06 · 1 fallimenti di fila
  AIOUSDT|gen_fc644cd2               3/3 pass · GIA' VALIDATA · ultimo pass 07 Oct 00:00 · finestra chiusa il 14 Oct 00:00 · vista 08 Oct 02:06
  ARCUSDT|gen_96c1ed1b               3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 08 Oct 00:00 · vista 08 Oct 02:06 · 1 fallimenti di fila
  ASTERUSDT|gen_96efce1b             3/3 pass · GIA' VALIDATA · ultimo pass 06 Oct 00:00 · finestra chiusa il 13 Oct 00:00 · vista 08 Oct 02:06
  ATOMUSDT|gen_eaa569ba              3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 08 Oct 00:00 · vista 08 Oct 02:06 · 1 fallimenti di fila
  AVAAIUSDT|gen_08c22b92             3/3 pass · GIA' VALIDATA · ultimo pass 05 Oct 00:00 · finestra chiusa il 12 Oct 00:00 · vista 08 Oct 02:21
  AVAAIUSDT|gen_14e1775b             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 08 Oct 00:00 · vista 08 Oct 02:21 · 1 fallimenti di fila
  AVAAIUSDT|gen_1eec02f5             3/3 pass · GIA' VALIDATA · ultimo pass 07 Oct 00:00 · finestra chiusa il 14 Oct 00:00 · vista 08 Oct 02:21
  AVAAIUSDT|gen_68ebd3b9             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 08 Oct 00:00 · vista 08 Oct 02:21 · 1 fallimenti di fila
  AVAAIUSDT|gen_dbe19eb2             3/3 pass · GIA' VALIDATA · ultimo pass 01 Oct 00:00 · finestra chiusa il 08 Oct 00:00 · vista 08 Oct 02:21
  AVAAIUSDT|gen_e50a9211             4/3 pass · GIA' VALIDATA · ultimo pass 04 Oct 00:00 · finestra chiusa il 11 Oct 00:00 · vista 08 Oct 02:21
  AXSUSDT|gen_b922252e               3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 08 Oct 00:00 · vista 08 Oct 02:06 · 1 fallimenti di fila
  B2USDT|gen_ddb3def9                3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 08 Oct 00:00 · vista 08 Oct 02:06 · 1 fallimenti di fila

--- QUANDO RIPARTE IL BOT ---
  Al piu' presto il — (fra -20734.2 giorni), quando la 10a coppia
  raggiungerebbe 3 pass.
  E' un LIMITE INFERIORE: assume che ognuna passi almeno una volta per
  finestra settimanale. Chi non passa per 2 finestre intere esce dal registro,
  quindi la data vera puo' essere piu' in la'. Serve anche coprire >= 5 coin distinte (10 coppie
  su coin diverse bastano).
```
