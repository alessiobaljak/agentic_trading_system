# 0448-3ott-mattina-gate.req

_eseguito: 2026-10-03 06:04 UTC_

**richiesta:** `gate`
**eseguito:** `.venv/bin/python -m scripts.gate_progress`
**esito:** codice 0 in 1.8s

```
[firebase] connesso (Firestore + RTDB)
[gate] 1866 coppie nel registro · 1865 ancora valutate · soglia 3 pass · un pass ogni 168h di dati nuovi
  distribuzione pass (solo coppie vive): 0 pass: 339 su 97 coin · 1 pass: 579 su 109 coin · 2 pass: 720 su 139 coin · 3 pass: 177 su 66 coin · 4 pass: 43 su 23 coin · 5 pass: 7 su 4 coin
  CONGELATE: 1 coppie non piu' valutate da oltre 3 giorni (1 avevano gia' un passaggio).
  La coin e' uscita dall'universo — di solito per storia insufficiente o delisting.
  Non avanzano e non falliscono: sono escluse da tutti i conti qui sotto.
  COMPOSIZIONE (vive): 0 base · 1865 generate.  Nel registro intero: 1 base su 1866, tetto 3000.
  fallimenti accumulati: 1 fallimenti: 428
  VALIDATE ora: 216 su 72 coin distinte
  ready dichiarato dal registro: True (via copertura)
     copertura 36.0% su obiettivo 35% · via a conteggio: 10 coppie (0 = spenta) · minimi 10 coin nell'universo, 5 coperte
     deciso il 03 Oct 03:26 su 216 validate / 72 coin coperte / universo 200 · minimi ok: True · copertura ok: True · conteggio ok: True
  FINESTRE APERTE: 1526/1526 coppie con almeno un passaggio.
  E' QUESTO il numero da guardare: solo queste stanno contando i giorni verso la
  conferma successiva, e solo queste compaiono nel calendario qui sotto.
  Le altre 0 sono ferme: la finestra si apre solo quando la coppia RIPASSA
  il gate, quindi per loro la prossima conferma non ha una data — dipende da un
  evento che potrebbe non succedere.

  STATISTICA t DELLE VALIDATE: 61 con misura · 42 reggerebbero t >= 2 · mediana 2.26 · le piu' basse: SAHARAUSDT|gen_1eec02f5 (1.22), AVAAIUSDT|gen_dbe19eb2 (1.26), AVAAIUSDT|gen_e50a9211 (1.26)
  (misurata, non usata per decidere: si decide dopo averla vista)

  A UN PASSO DALLA VALIDAZIONE: 720 coppie a 2/3.
  Di queste, 1 su 1 coin hanno GIA' la finestra scaduta: si
  validano al primo run in cui ripassano il gate, cioe' potenzialmente oggi.
  Le altre diventano idonee: 85 il 04 Oct 00:00 · 89 il 05 Oct 00:00 · 58 il 06 Oct 00:00 · 73 il 07 Oct 00:00 · 231 il 08 Oct 00:00 · 97 il 09 Oct 00:00 · 86 il 10 Oct 00:00
  spazio registro: 543 KiB su 879 (62%)
    298 byte a coppia · ci stanno ancora ~1157 coppie oltre le 1866 di adesso
  spazio spec scoperte: 209 KiB su 879 (24%)

  TEMPO DELL'ULTIMO GIRO (discovery): 1h 56m · iniziato 03 Oct 03:35 UTC · finito 05:31 UTC
  ULTIMO GIRO: 22632 valutazioni · 44 coppie passate · solo urgenti · 246 coin
  GIRO RIDOTTO: no, tutte le spec su tutte le coin (solo urgenti)
  IL CERVELLO NELL'ULTIMO GIRO: intorno 0 madri / 0 figlie passate / 0 promosse / 0 senza margine · varianti 0 create / 0 passate / 0 con conferme retroattive / 0 promosse / 0 scartate / sostituzioni nessuna
  KEEP DEL LOCK (scelto dal gate per coppia): 0.35 x17 · 0.5 x14 · 0.65 x13 · 0.75 x14 · non ancora rivalutate x158
  DECLASSATE: 173 validate a un quarto di size (bocciate 2 notti di fila) · tornate piene nel giro 0 · nuove nel giro 0 (contatori fermi: giro solo urgenti)
  FEATURE session: 0 validate su 216 usano la sessione oraria (fino al 27 set valutata con l'orologio del giro, non della candela: passaggi da rifare) · 347 azzerate il 27 set, ripassano da zero
  ESPLORATIVE: 47 attive · validate poi 2 · scartate 294
  IPOTESI PER TIPO: conferma_trend 1 nate / 1 varianti / 0 passate / 0 validate / 1 bocciate · ingresso_atr_pct 1 nate / 0 varianti / 0 passate / 0 validate / 0 bocciate · solo_long 1 nate / 1 varianti / 0 passate / 0 validate / 1 bocciate · solo_short 2 nate / 2 varianti / 0 passate / 0 validate / 2 bocciate · tasso figlie 0% (0/4 spec) contro 0.2% delle candidate dell'ultimo giro (44/22632 coppie coin x spec, gate_autopsy/discover: unita' diverse)
  PASSATA A 1 ORA (30 coin): 8m · 8550 valutazioni · 193 passate
  ORIGINI (le idee AI servono? si contano le coppie, non l'R; fonte: registro + discovered_strategies/specs)
    AI: 113 nel registro / 1 validate / 0 declassate · casuali (e mutazioni): 1738 nel registro / 205 validate / 171 declassate · intorno: 14 nel registro / 10 validate / 2 declassate · base: 1 nel registro / 0 validate / 0 declassate
    candidate dell'ultimo giro: nuove ai 0 · casuali 39 · mutazioni 28 · varianti 0; note rivalutate casuali (e mutazioni) 22 · intorno 2 · AI 1
    candidate della passata a 1 ora: nuove ai 0 · casuali 40 · mutazioni 29 · varianti 0; note rivalutate casuali (e mutazioni) 168 · AI 48

  RI-VALUTAZIONE (ultimo run discovery, solo urgenti): 32 spec su 886 note · cap 500 · 834 con almeno una conferma
  854 spec restano fuori dal taglio: sono ferme, non in attesa.
  Quelle con conferme passano comunque, quindi il taglio tocca solo candidate a zero passaggi.

--- QUANDO ARRIVANO LE PROSSIME CONFERME (limite inferiore) ---
  AIOUSDT|gen_581d4a68               3/3 pass · GIA' VALIDATA · ultimo pass 28 Sep 00:00 · finestra chiusa il 05 Oct 00:00 · vista 03 Oct 05:31
  ARCUSDT|gen_96c1ed1b               3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 08 Oct 00:00 · vista 03 Oct 05:31 · 1 fallimenti di fila
  ATOMUSDT|gen_eaa569ba              3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 08 Oct 00:00 · vista 03 Oct 05:31 · 1 fallimenti di fila
  AVAAIUSDT|gen_14e1775b             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 08 Oct 00:00 · vista 03 Oct 05:31 · 1 fallimenti di fila
  AVAAIUSDT|gen_68ebd3b9             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 08 Oct 00:00 · vista 03 Oct 05:31 · 1 fallimenti di fila
  AVAAIUSDT|gen_dbe19eb2             3/3 pass · GIA' VALIDATA · ultimo pass 01 Oct 00:00 · finestra chiusa il 08 Oct 00:00 · vista 03 Oct 05:31
  AVAAIUSDT|gen_e50a9211             3/3 pass · GIA' VALIDATA · ultimo pass 27 Sep 00:00 · finestra chiusa il 04 Oct 00:00 · vista 03 Oct 05:31
  AXSUSDT|gen_b922252e               3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 08 Oct 00:00 · vista 03 Oct 05:31 · 1 fallimenti di fila
  B2USDT|gen_ddb3def9                3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 08 Oct 00:00 · vista 03 Oct 05:31 · 1 fallimenti di fila
  BANKUSDT|gen_1efbb088              3/3 pass · GIA' VALIDATA · ultimo pass 27 Sep 00:00 · finestra chiusa il 04 Oct 00:00 · vista 03 Oct 05:31
  BANKUSDT|gen_fb3d971f              3/3 pass · GIA' VALIDATA · ultimo pass 27 Sep 00:00 · finestra chiusa il 04 Oct 00:00 · vista 03 Oct 05:31
  BMTUSDT|gen_571cdda2               3/3 pass · GIA' VALIDATA · ultimo pass 28 Sep 00:00 · finestra chiusa il 05 Oct 00:00 · vista 03 Oct 05:31
  BMTUSDT|gen_cee79cdd               3/3 pass · GIA' VALIDATA · ultimo pass 28 Sep 00:00 · finestra chiusa il 05 Oct 00:00 · vista 03 Oct 05:31
  BRUSDT|gen_95fb50ce                3/3 pass · GIA' VALIDATA · ultimo pass 03 Oct 00:00 · finestra chiusa il 10 Oct 00:00 · vista 03 Oct 05:31
  BTRUSDT|gen_8981d5f2               3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 08 Oct 00:00 · vista 03 Oct 05:31 · 1 fallimenti di fila

--- QUANDO RIPARTE IL BOT ---
  Al piu' presto il — (fra -20729.3 giorni), quando la 10a coppia
  raggiungerebbe 3 pass.
  E' un LIMITE INFERIORE: assume che ognuna passi almeno una volta per
  finestra settimanale. Chi non passa per 2 finestre intere esce dal registro,
  quindi la data vera puo' essere piu' in la'. Serve anche coprire >= 5 coin distinte (10 coppie
  su coin diverse bastano).
```
