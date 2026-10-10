# 0571-10ott-mattina-gate.req

_eseguito: 2026-10-10 03:47 UTC_

**richiesta:** `gate`
**eseguito:** `.venv/bin/python -m scripts.gate_progress`
**esito:** codice 0 in 2.0s

```
[firebase] connesso (Firestore + RTDB)
[gate] 2232 coppie nel registro · 2231 ancora valutate · soglia 3 pass · un pass ogni 168h di dati nuovi
  distribuzione pass (solo coppie vive): 0 pass: 336 su 96 coin · 1 pass: 906 su 144 coin · 2 pass: 731 su 136 coin · 3 pass: 199 su 70 coin · 4 pass: 47 su 21 coin · 5 pass: 12 su 8 coin
  CONGELATE: 1 coppie non piu' valutate da oltre 3 giorni (1 avevano gia' un passaggio).
  La coin e' uscita dall'universo — di solito per storia insufficiente o delisting.
  Non avanzano e non falliscono: sono escluse da tutti i conti qui sotto.
  COMPOSIZIONE (vive): 0 base · 2231 generate.  Nel registro intero: 1 base su 2232, tetto 3000.
  fallimenti accumulati: 1 fallimenti: 587 · 2 fallimenti: 5
  VALIDATE ora: 236 su 77 coin distinte
  ready dichiarato dal registro: True (via copertura)
     copertura 38.5% su obiettivo 35% · via a conteggio: 10 coppie (0 = spenta) · minimi 10 coin nell'universo, 5 coperte
     deciso il 10 Oct 01:10 su 236 validate / 77 coin coperte / universo 200 · minimi ok: True · copertura ok: True · conteggio ok: True
  FINESTRE APERTE: 1895/1895 coppie con almeno un passaggio.
  E' QUESTO il numero da guardare: solo queste stanno contando i giorni verso la
  conferma successiva, e solo queste compaiono nel calendario qui sotto.
  Le altre 0 sono ferme: la finestra si apre solo quando la coppia RIPASSA
  il gate, quindi per loro la prossima conferma non ha una data — dipende da un
  evento che potrebbe non succedere.

  STATISTICA t DELLE VALIDATE: 191 con misura · 135 reggerebbero t >= 2 · mediana 2.23 · le piu' basse: MUBARAKUSDT|gen_2053cba6 (1.12), AINUSDT|gen_ef115241 (1.25), 0GUSDT|gen_aa6bb820 (1.25)
  (misurata, non usata per decidere: si decide dopo averla vista)

  A UN PASSO DALLA VALIDAZIONE: 731 coppie a 2/3.
  Di queste, 98 su 52 coin hanno GIA' la finestra scaduta: si
  validano al primo run in cui ripassano il gate, cioe' potenzialmente oggi.
  Le altre diventano idonee: 110 il 11 Oct 00:00 · 89 il 12 Oct 00:00 · 77 il 13 Oct 00:00 · 75 il 14 Oct 00:00 · 133 il 15 Oct 00:00 · 103 il 16 Oct 00:00 · 46 il 17 Oct 00:00
  spazio registro: 733 KiB su 879 (83%)  ATTENZIONE:
    336 byte a coppia · ci stanno ancora ~444 coppie oltre le 2232 di adesso
  oltre il limite Firestore rifiuta la scrittura e il run perde
  le conferme appena guadagnate. Va alzato il tetto o alleggerito il documento.
  spazio spec scoperte: 310 KiB su 879 (35%)

  TEMPO DELL'ULTIMO GIRO (discovery): 3h 47m · iniziato 09 Oct 21:23 UTC · finito 01:10 UTC  ← SFORA la finestra di 3h
  ULTIMO GIRO: 57311 valutazioni · 185 coppie passate · solo urgenti · 257 coin
  GIRO RIDOTTO: no, tutte le spec su tutte le coin (solo urgenti)
  IL CERVELLO NELL'ULTIMO GIRO: intorno 0 madri / 0 figlie passate / 0 promosse / 0 senza margine · varianti 0 create / 0 passate / 0 con conferme retroattive / 0 promosse / 0 scartate / sostituzioni nessuna
  KEEP DEL LOCK (scelto dal gate per coppia): 0.35 x43 · 0.5 x45 · 0.65 x76 · 0.75 x14 · non ancora rivalutate x58
  DECLASSATE: 105 validate a un quarto di size (bocciate 2 notti di fila) · tornate piene nel giro 0 · nuove nel giro 0 (contatori fermi: giro solo urgenti)
  FEATURE session: 0 validate su 236 usano la sessione oraria (fino al 27 set valutata con l'orologio del giro, non della candela: passaggi da rifare) · 347 azzerate il 27 set, ripassano da zero
  ESPLORATIVE: 38 attive · validate poi 4 · scartate 540
  IPOTESI PER TIPO: conferma_trend 3 nate / 1 varianti / 0 passate / 0 validate / 1 bocciate · controtrend_btc 1 nate / 0 varianti / 0 passate / 0 validate / 0 bocciate · ingresso_atr_pct 1 nate / 0 varianti / 0 passate / 0 validate / 0 bocciate · ingresso_vol_ratio 1 nate / 0 varianti / 0 passate / 0 validate / 0 bocciate · scala_stretta 3 nate / 0 varianti / 0 passate / 0 validate / 0 bocciate · solo_long 1 nate / 1 varianti / 0 passate / 0 validate / 1 bocciate · solo_short 3 nate / 2 varianti / 0 passate / 0 validate / 2 bocciate · tasso figlie 0% (0/4 spec) contro 0.3% delle candidate dell'ultimo giro (185/57311 coppie coin x spec, gate_autopsy/discover: unita' diverse)
  PASSATA A 1 ORA (30 coin): 17m · 17790 valutazioni · 359 passate
  ORIGINI (le idee AI servono? si contano le coppie, non l'R; fonte: registro + discovered_strategies/specs)
    AI: 118 nel registro / 5 validate / 2 declassate · casuali (e mutazioni): 2087 nel registro / 209 validate / 98 declassate · intorno: 26 nel registro / 22 validate / 5 declassate · base: 1 nel registro / 0 validate / 0 declassate
    candidate dell'ultimo giro: nuove ai 0 · casuali 39 · mutazioni 24 · varianti 0; note rivalutate casuali (e mutazioni) 151 · AI 8 · intorno 1
    candidate della passata a 1 ora: nuove ai 0 · casuali 40 · mutazioni 28 · varianti 0; note rivalutate casuali (e mutazioni) 478 · AI 47

  RI-VALUTAZIONE (ultimo run discovery, solo urgenti): 235 spec su 1349 note · cap 500 · 1242 con almeno una conferma
  1114 spec restano fuori dal taglio: sono ferme, non in attesa.
  Quelle con conferme passano comunque, quindi il taglio tocca solo candidate a zero passaggi.

--- QUANDO ARRIVANO LE PROSSIME CONFERME (limite inferiore) ---
  0GUSDT|gen_aa6bb820                3/3 pass · GIA' VALIDATA · ultimo pass 08 Oct 00:00 · finestra chiusa il 15 Oct 00:00 · vista 10 Oct 01:10
  1000BONKUSDT|gen_86a8b183          3/3 pass · GIA' VALIDATA · ultimo pass 05 Oct 00:00 · finestra chiusa il 12 Oct 00:00 · vista 10 Oct 01:10
  1000PEPEUSDT|gen_f9d90376          3/3 pass · GIA' VALIDATA · ultimo pass 08 Oct 00:00 · finestra chiusa il 15 Oct 00:00 · vista 10 Oct 01:10
  AINUSDT|gen_057ea246               3/3 pass · GIA' VALIDATA · ultimo pass 08 Oct 00:00 · finestra chiusa il 15 Oct 00:00 · vista 10 Oct 01:10
  AINUSDT|gen_d8656ab7               3/3 pass · GIA' VALIDATA · ultimo pass 09 Oct 00:00 · finestra chiusa il 16 Oct 00:00 · vista 10 Oct 01:10
  AINUSDT|gen_ef115241               3/3 pass · GIA' VALIDATA · ultimo pass 04 Oct 00:00 · finestra chiusa il 11 Oct 00:00 · vista 10 Oct 01:10
  AIOUSDT|gen_581d4a68               3/3 pass · GIA' VALIDATA · ultimo pass 28 Sep 00:00 · finestra chiusa il 12 Oct 00:00 · vista 10 Oct 01:10 · 1 fallimenti di fila
  AIOUSDT|gen_fc644cd2               3/3 pass · GIA' VALIDATA · ultimo pass 07 Oct 00:00 · finestra chiusa il 14 Oct 00:00 · vista 10 Oct 01:10
  AKTUSDT|gen_f4c1300a               3/3 pass · GIA' VALIDATA · ultimo pass 09 Oct 00:00 · finestra chiusa il 16 Oct 00:00 · vista 10 Oct 01:10
  ARKMUSDT|gen_96ed157e              3/3 pass · GIA' VALIDATA · ultimo pass 09 Oct 00:00 · finestra chiusa il 16 Oct 00:00 · vista 10 Oct 01:10
  ASTERUSDT|gen_049a08f7             3/3 pass · GIA' VALIDATA · ultimo pass 08 Oct 00:00 · finestra chiusa il 15 Oct 00:00 · vista 10 Oct 01:10
  ASTERUSDT|gen_37836d3c             3/3 pass · GIA' VALIDATA · ultimo pass 08 Oct 00:00 · finestra chiusa il 15 Oct 00:00 · vista 10 Oct 01:10
  ASTERUSDT|gen_96efce1b             3/3 pass · GIA' VALIDATA · ultimo pass 06 Oct 00:00 · finestra chiusa il 13 Oct 00:00 · vista 10 Oct 01:10
  ASTERUSDT|gen_d74845a5             3/3 pass · GIA' VALIDATA · ultimo pass 08 Oct 00:00 · finestra chiusa il 15 Oct 00:00 · vista 10 Oct 01:10
  AVAAIUSDT|gen_08c22b92             3/3 pass · GIA' VALIDATA · ultimo pass 05 Oct 00:00 · finestra chiusa il 12 Oct 00:00 · vista 10 Oct 01:27

--- QUANDO RIPARTE IL BOT ---
  Al piu' presto il — (fra -20736.2 giorni), quando la 10a coppia
  raggiungerebbe 3 pass.
  E' un LIMITE INFERIORE: assume che ognuna passi almeno una volta per
  finestra settimanale. Chi non passa per 2 finestre intere esce dal registro,
  quindi la data vera puo' essere piu' in la'. Serve anche coprire >= 5 coin distinte (10 coppie
  su coin diverse bastano).
```
