# 0586-11ott-settimanale-gate.req

_eseguito: 2026-10-11 03:47 UTC_

**richiesta:** `gate`
**eseguito:** `.venv/bin/python -m scripts.gate_progress`
**esito:** codice 0 in 1.9s

```
[firebase] connesso (Firestore + RTDB)
[gate] 2319 coppie nel registro · 2317 ancora valutate · soglia 3 pass · un pass ogni 168h di dati nuovi
  distribuzione pass (solo coppie vive): 0 pass: 335 su 95 coin · 1 pass: 970 su 143 coin · 2 pass: 750 su 133 coin · 3 pass: 202 su 70 coin · 4 pass: 46 su 22 coin · 5 pass: 10 su 7 coin · 6 pass: 4 su 3 coin
  CONGELATE: 2 coppie non piu' valutate da oltre 3 giorni (1 avevano gia' un passaggio).
  La coin e' uscita dall'universo — di solito per storia insufficiente o delisting.
  Non avanzano e non falliscono: sono escluse da tutti i conti qui sotto.
  COMPOSIZIONE (vive): 0 base · 2317 generate.  Nel registro intero: 1 base su 2319, tetto 3000.
  fallimenti accumulati: 1 fallimenti: 627 · 2 fallimenti: 2
  VALIDATE ora: 239 su 77 coin distinte
  ready dichiarato dal registro: True (via copertura)
     copertura 38.5% su obiettivo 35% · via a conteggio: 10 coppie (0 = spenta) · minimi 10 coin nell'universo, 5 coperte
     deciso il 11 Oct 01:40 su 238 validate / 77 coin coperte / universo 200 · minimi ok: True · copertura ok: True · conteggio ok: True
  FINESTRE APERTE: 1982/1982 coppie con almeno un passaggio.
  E' QUESTO il numero da guardare: solo queste stanno contando i giorni verso la
  conferma successiva, e solo queste compaiono nel calendario qui sotto.
  Le altre 0 sono ferme: la finestra si apre solo quando la coppia RIPASSA
  il gate, quindi per loro la prossima conferma non ha una data — dipende da un
  evento che potrebbe non succedere.

  STATISTICA t DELLE VALIDATE: 210 con misura · 147 reggerebbero t >= 2 · mediana 2.28 · le piu' basse: MUBARAKUSDT|gen_2053cba6 (1.12), SKYAIUSDT|gen_bd109329 (1.22), AINUSDT|gen_ef115241 (1.25)
  (misurata, non usata per decidere: si decide dopo averla vista)

  A UN PASSO DALLA VALIDAZIONE: 750 coppie a 2/3.
  Di queste, 114 su 50 coin hanno GIA' la finestra scaduta: si
  validano al primo run in cui ripassano il gate, cioe' potenzialmente oggi.
  Le altre diventano idonee: 89 il 12 Oct 00:00 · 77 il 13 Oct 00:00 · 75 il 14 Oct 00:00 · 133 il 15 Oct 00:00 · 103 il 16 Oct 00:00 · 120 il 17 Oct 00:00 · 39 il 18 Oct 00:00
  spazio registro: 771 KiB su 879 (88%)  ATTENZIONE:
    340 byte a coppia · ci stanno ancora ~325 coppie oltre le 2319 di adesso
  oltre il limite Firestore rifiuta la scrittura e il run perde
  le conferme appena guadagnate. Va alzato il tetto o alleggerito il documento.
  spazio spec scoperte: 331 KiB su 879 (38%)

  TEMPO DELL'ULTIMO GIRO (discovery): 4h 18m · iniziato 10 Oct 21:22 UTC · finito 01:40 UTC  ← SFORA la finestra di 3h
  ULTIMO GIRO: 66750 valutazioni · 194 coppie passate · solo urgenti · 267 coin
  GIRO RIDOTTO: no, tutte le spec su tutte le coin (solo urgenti)
  IL CERVELLO NELL'ULTIMO GIRO: intorno 0 madri / 6 figlie passate / 0 promosse / 1 senza margine / 1 con madre non valutata / 4 senza conferme retroattive o seconde figlie · varianti 0 create / 0 passate / 0 con conferme retroattive / 0 promosse / 0 scartate / sostituzioni nessuna
  KEEP DEL LOCK (scelto dal gate per coppia): 0.35 x44 · 0.5 x52 · 0.65 x85 · 0.75 x14 · non ancora rivalutate x44
  DECLASSATE: 101 validate a un quarto di size (bocciate 2 notti di fila) · tornate piene nel giro 0 · nuove nel giro 0 (contatori fermi: giro solo urgenti)
  FEATURE session: 1 validate su 239 usano la sessione oraria (fino al 27 set valutata con l'orologio del giro, non della candela: passaggi da rifare) · 347 azzerate il 27 set, ripassano da zero (1 gia' ripassate)
  ESPLORATIVE: 36 attive · validate poi 4 · scartate 587
  IPOTESI PER TIPO: conferma_trend 3 nate / 1 varianti / 0 passate / 0 validate / 1 bocciate · controtrend_btc 1 nate / 0 varianti / 0 passate / 0 validate / 0 bocciate · ingresso_atr_pct 1 nate / 0 varianti / 0 passate / 0 validate / 0 bocciate · ingresso_vol_ratio 1 nate / 0 varianti / 0 passate / 0 validate / 0 bocciate · scala_stretta 3 nate / 0 varianti / 0 passate / 0 validate / 0 bocciate · solo_long 1 nate / 1 varianti / 0 passate / 0 validate / 1 bocciate · solo_short 3 nate / 2 varianti / 0 passate / 0 validate / 2 bocciate · tasso figlie 0% (0/4 spec) contro 0.3% delle candidate dell'ultimo giro (200/66750 coppie coin x spec, gate_autopsy/discover: unita' diverse)
  PASSATA A 1 ORA (30 coin): 16m · 19290 valutazioni · 417 passate
  ORIGINI (le idee AI servono? si contano le coppie, non l'R; fonte: registro + discovered_strategies/specs)
    AI: 117 nel registro / 4 validate / 2 declassate · casuali (e mutazioni): 2165 nel registro / 207 validate / 91 declassate · intorno: 36 nel registro / 28 validate / 8 declassate · base: 1 nel registro / 0 validate / 0 declassate
    candidate dell'ultimo giro: nuove ai 0 · casuali 40 · mutazioni 17 · varianti 0; note rivalutate casuali (e mutazioni) 179 · intorno 8 · AI 6
    candidate della passata a 1 ora: nuove ai 0 · casuali 40 · mutazioni 30 · varianti 0; note rivalutate casuali (e mutazioni) 528 · AI 45

  RI-VALUTAZIONE (ultimo run discovery, solo urgenti): 287 spec su 1437 note · cap 500 · 1319 con almeno una conferma
  1150 spec restano fuori dal taglio: sono ferme, non in attesa.
  Quelle con conferme passano comunque, quindi il taglio tocca solo candidate a zero passaggi.

--- QUANDO ARRIVANO LE PROSSIME CONFERME (limite inferiore) ---
  0GUSDT|gen_aa6bb820                3/3 pass · GIA' VALIDATA · ultimo pass 08 Oct 00:00 · finestra chiusa il 15 Oct 00:00 · vista 11 Oct 01:40
  1000BONKUSDT|gen_86a8b183          3/3 pass · GIA' VALIDATA · ultimo pass 05 Oct 00:00 · finestra chiusa il 12 Oct 00:00 · vista 11 Oct 01:40
  1000PEPEUSDT|gen_f9d90376          3/3 pass · GIA' VALIDATA · ultimo pass 08 Oct 00:00 · finestra chiusa il 15 Oct 00:00 · vista 11 Oct 01:40
  AINUSDT|gen_057ea246               3/3 pass · GIA' VALIDATA · ultimo pass 08 Oct 00:00 · finestra chiusa il 15 Oct 00:00 · vista 11 Oct 01:40
  AINUSDT|gen_b0e86c70               3/3 pass · GIA' VALIDATA · ultimo pass 10 Oct 00:00 · finestra chiusa il 17 Oct 00:00 · vista 11 Oct 01:40
  AINUSDT|gen_d8656ab7               3/3 pass · GIA' VALIDATA · ultimo pass 09 Oct 00:00 · finestra chiusa il 16 Oct 00:00 · vista 11 Oct 01:40
  AINUSDT|gen_d926b0fd               3/3 pass · GIA' VALIDATA · ultimo pass 10 Oct 00:00 · finestra chiusa il 17 Oct 00:00 · vista 11 Oct 01:40
  AINUSDT|gen_e3f3663c               3/3 pass · GIA' VALIDATA · ultimo pass 10 Oct 00:00 · finestra chiusa il 17 Oct 00:00 · vista 11 Oct 01:40
  AINUSDT|gen_ef115241               3/3 pass · GIA' VALIDATA · ultimo pass 04 Oct 00:00 · finestra chiusa il 11 Oct 00:00 · vista 11 Oct 01:40
  AIOUSDT|gen_581d4a68               3/3 pass · GIA' VALIDATA · ultimo pass 28 Sep 00:00 · finestra chiusa il 12 Oct 00:00 · vista 11 Oct 01:40 · 1 fallimenti di fila
  AIOUSDT|gen_fc644cd2               3/3 pass · GIA' VALIDATA · ultimo pass 07 Oct 00:00 · finestra chiusa il 14 Oct 00:00 · vista 11 Oct 01:40
  AKTUSDT|gen_f4c1300a               3/3 pass · GIA' VALIDATA · ultimo pass 09 Oct 00:00 · finestra chiusa il 16 Oct 00:00 · vista 11 Oct 01:40
  ARKMUSDT|gen_96ed157e              3/3 pass · GIA' VALIDATA · ultimo pass 09 Oct 00:00 · finestra chiusa il 16 Oct 00:00 · vista 11 Oct 01:40
  ASTERUSDT|gen_049a08f7             3/3 pass · GIA' VALIDATA · ultimo pass 08 Oct 00:00 · finestra chiusa il 15 Oct 00:00 · vista 11 Oct 01:40
  ASTERUSDT|gen_1390f7aa             3/3 pass · GIA' VALIDATA · ultimo pass 10 Oct 00:00 · finestra chiusa il 17 Oct 00:00 · vista 11 Oct 01:40

--- QUANDO RIPARTE IL BOT ---
  Al piu' presto il — (fra -20737.2 giorni), quando la 10a coppia
  raggiungerebbe 3 pass.
  E' un LIMITE INFERIORE: assume che ognuna passi almeno una volta per
  finestra settimanale. Chi non passa per 2 finestre intere esce dal registro,
  quindi la data vera puo' essere piu' in la'. Serve anche coprire >= 5 coin distinte (10 coppie
  su coin diverse bastano).
```
