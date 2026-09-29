# 0343-29set-gate.req

_eseguito: 2026-09-29 06:12 UTC_

**richiesta:** `gate`
**eseguito:** `.venv/bin/python -m scripts.gate_progress`
**esito:** codice 0 in 2.0s

```
[firebase] connesso (Firestore + RTDB)
[gate] 1472 coppie nel registro · 1471 ancora valutate · soglia 3 pass · un pass ogni 168h di dati nuovi
  distribuzione pass (solo coppie vive): 0 pass: 341 su 97 coin · 1 pass: 430 su 112 coin · 2 pass: 492 su 115 coin · 3 pass: 164 su 65 coin · 4 pass: 42 su 20 coin · 5 pass: 2 su 1 coin
  CONGELATE: 1 coppie non piu' valutate da oltre 3 giorni (1 avevano gia' un passaggio).
  La coin e' uscita dall'universo — di solito per storia insufficiente o delisting.
  Non avanzano e non falliscono: sono escluse da tutti i conti qui sotto.
  COMPOSIZIONE (vive): 0 base · 1471 generate.  Nel registro intero: 1 base su 1472, tetto 3000.
  fallimenti accumulati: 1 fallimenti: 50
  VALIDATE ora: 199 su 69 coin distinte
  ready dichiarato dal registro: True (via numero coppie)
     copertura 34.5% su obiettivo 35% · via a conteggio: 10 coppie (0 = spenta) · minimi 10 coin nell'universo, 5 coperte
     deciso il 29 Sep 06:01 su 199 validate / 69 coin coperte / universo 200 · minimi ok: True · copertura ok: False · conteggio ok: True
  FINESTRE APERTE: 1130/1130 coppie con almeno un passaggio.
  E' QUESTO il numero da guardare: solo queste stanno contando i giorni verso la
  conferma successiva, e solo queste compaiono nel calendario qui sotto.
  Le altre 0 sono ferme: la finestra si apre solo quando la coppia RIPASSA
  il gate, quindi per loro la prossima conferma non ha una data — dipende da un
  evento che potrebbe non succedere.

  STATISTICA t DELLE VALIDATE: 38 con misura · 25 reggerebbero t >= 2 · mediana 2.23 · le piu' basse: SAHARAUSDT|gen_95aff747 (1.21), MUBARAKUSDT|gen_1e2af031 (1.32), UBUSDT|gen_f3661202 (1.37)
  (misurata, non usata per decidere: si decide dopo averla vista)

  A UN PASSO DALLA VALIDAZIONE: 492 coppie a 2/3.
  Di queste, 1 su 1 coin hanno GIA' la finestra scaduta: si
  validano al primo run in cui ripassano il gate, cioe' potenzialmente oggi.
  Le altre diventano idonee: 181 il 01 Oct 00:00 · 42 il 02 Oct 00:00 · 31 il 03 Oct 00:00 · 85 il 04 Oct 00:00 · 89 il 05 Oct 00:00 · 58 il 06 Oct 00:00 · 5 il 30 Sep 00:00
  spazio registro: 399 KiB su 879 (45%)
    278 byte a coppia · ci stanno ancora ~1768 coppie oltre le 1472 di adesso
  spazio spec scoperte: 146 KiB su 879 (17%)

  TEMPO DELL'ULTIMO GIRO (discovery): 2h 03m · iniziato 29 Sep 03:05 UTC · finito 05:08 UTC
  ULTIMO GIRO: 25984 valutazioni · 57 coppie passate · solo urgenti · 232 coin
  GIRO RIDOTTO: no, tutte le spec su tutte le coin (solo urgenti)
  IL CERVELLO NELL'ULTIMO GIRO: intorno 0 madri / 0 figlie passate / 0 promosse / 0 senza margine · varianti 2 create / 1 passate / 0 con conferme retroattive / 0 promosse / 1 scartate / sostituzioni nessuna
  KEEP DEL LOCK (scelto dal gate per coppia): 0.35 x12 · 0.5 x7 · 0.65 x6 · 0.75 x14 · non ancora rivalutate x160
  DECLASSATE: 142 validate a un quarto di size (bocciate 2 notti di fila) · tornate piene nel giro 0 · nuove nel giro 0 (contatori fermi: giro solo urgenti)
  FEATURE session: 0 validate su 199 usano la sessione oraria (fino al 27 set valutata con l'orologio del giro, non della candela: passaggi da rifare) · 347 azzerate il 27 set, ripassano da zero
  ESPLORATIVE: 56 attive · validate poi 1 · scartate 168
  IPOTESI PER TIPO: conferma_trend 1 nate / 1 varianti / 0 passate / 0 validate / 1 bocciate · ingresso_atr_pct 1 nate / 0 varianti / 0 passate / 0 validate / 0 bocciate · solo_long 1 nate / 1 varianti / 0 passate / 0 validate / 1 bocciate · solo_short 1 nate / 1 varianti / 0 passate / 0 validate / 1 bocciate · tasso figlie 0% (0/3 spec) contro 1.2% delle candidate dell'ultimo giro (29/2520 coppie coin x spec, gate_autopsy/discover: unita' diverse)
  PASSATA A 1 ORA (21 coin): 5m · 2520 valutazioni · 29 passate

  RI-VALUTAZIONE (ultimo run discovery, solo urgenti): 34 spec su 629 note · cap 500 · 579 con almeno una conferma
  595 spec restano fuori dal taglio: sono ferme, non in attesa.
  Quelle con conferme passano comunque, quindi il taglio tocca solo candidate a zero passaggi.

--- QUANDO ARRIVANO LE PROSSIME CONFERME (limite inferiore) ---
  AIOUSDT|gen_581d4a68               3/3 pass · GIA' VALIDATA · ultimo pass 28 Sep 00:00 · finestra chiusa il 05 Oct 00:00 · vista 29 Sep 05:08
  ARCUSDT|gen_96c1ed1b               3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 29 Sep 05:08
  ATOMUSDT|gen_eaa569ba              3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 29 Sep 05:08
  AVAAIUSDT|gen_14e1775b             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 29 Sep 05:08
  AVAAIUSDT|gen_68ebd3b9             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 29 Sep 05:08
  AVAAIUSDT|gen_e50a9211             3/3 pass · GIA' VALIDATA · ultimo pass 27 Sep 00:00 · finestra chiusa il 04 Oct 00:00 · vista 29 Sep 05:08
  AXSUSDT|gen_b922252e               3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 29 Sep 05:08
  B2USDT|gen_ddb3def9                3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 29 Sep 05:08
  BANKUSDT|gen_1efbb088              3/3 pass · GIA' VALIDATA · ultimo pass 27 Sep 00:00 · finestra chiusa il 04 Oct 00:00 · vista 29 Sep 06:06
  BANKUSDT|gen_fb3d971f              3/3 pass · GIA' VALIDATA · ultimo pass 27 Sep 00:00 · finestra chiusa il 04 Oct 00:00 · vista 29 Sep 06:06
  BMTUSDT|gen_571cdda2               3/3 pass · GIA' VALIDATA · ultimo pass 28 Sep 00:00 · finestra chiusa il 05 Oct 00:00 · vista 29 Sep 06:06
  BMTUSDT|gen_cee79cdd               3/3 pass · GIA' VALIDATA · ultimo pass 28 Sep 00:00 · finestra chiusa il 05 Oct 00:00 · vista 29 Sep 06:06
  BTRUSDT|gen_8981d5f2               3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 29 Sep 05:08
  BULLAUSDT|gen_2e8fb80a             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 29 Sep 05:08
  BULLAUSDT|gen_3f1b628b             3/3 pass · GIA' VALIDATA · ultimo pass 24 Sep 00:00 · finestra chiusa il 01 Oct 00:00 · vista 29 Sep 05:08

--- QUANDO RIPARTE IL BOT ---
  Al piu' presto il — (fra -20725.3 giorni), quando la 10a coppia
  raggiungerebbe 3 pass.
  E' un LIMITE INFERIORE: assume che ognuna passi almeno una volta per
  finestra settimanale. Chi non passa per 2 finestre intere esce dal registro,
  quindi la data vera puo' essere piu' in la'. Serve anche coprire >= 5 coin distinte (10 coppie
  su coin diverse bastano).
```
