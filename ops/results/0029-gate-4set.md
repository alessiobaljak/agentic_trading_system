# 0029-gate-4set.req

_eseguito: 2026-09-04 23:47 UTC_

**richiesta:** `gate`
**eseguito:** `.venv/bin/python -m scripts.gate_progress`
**esito:** codice 0 in 1.0s

```
[firebase] connesso (Firestore + RTDB)
[gate] 2109 coppie nel registro · 1791 ancora valutate · soglia 3 pass · un pass ogni 168h di dati nuovi
  distribuzione pass (solo coppie vive): 0 pass: 1598 · 1 pass: 193
  CONGELATE: 318 coppie non piu' valutate da oltre 3 giorni (30 avevano gia' un passaggio).
  La coin e' uscita dall'universo — di solito per storia insufficiente o delisting.
  Non avanzano e non falliscono: sono escluse da tutti i conti qui sotto.
  COMPOSIZIONE (vive): 1600 base · 191 generate.  Nel registro intero: 1888 base su 2109, tetto 3000.
  fallimenti accumulati: 1 fallimenti: 961
  VALIDATE ora: 0 su 0 coin distinte
  ready dichiarato dal registro: False (via —)
  FINESTRE APERTE: 193/193 coppie con almeno un passaggio.
  E' QUESTO il numero da guardare: solo queste stanno contando i giorni verso la
  conferma successiva, e solo queste compaiono nel calendario qui sotto.
  Le altre 0 sono ferme: la finestra si apre solo quando la coppia RIPASSA
  il gate, quindi per loro la prossima conferma non ha una data — dipende da un
  evento che potrebbe non succedere.

--- QUANDO ARRIVANO LE PROSSIME CONFERME (limite inferiore) ---
  MUBARAKUSDT|mean_reversion         1/3 pass · validata il 12 Sep 00:00 · ultimo pass 21 Aug 00:00 · finestra chiusa il 05 Sep 00:00 · vista 04 Sep 21:42 · 1 fallimenti di fila
  EGLDUSDT|gen_36b0e335              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 04 Sep 22:52
  EGLDUSDT|gen_f238d283              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 04 Sep 22:52
  MOVRUSDT|gen_4f890271              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 04 Sep 22:52
  MUSDT|mean_reversion               1/3 pass · validata il 13 Sep 00:00 · ultimo pass 13 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 03 Sep 18:41 · 1 fallimenti di fila
  STXUSDT|gen_14e1775b               1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 04 Sep 22:52
  STXUSDT|gen_acfd527a               1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 04 Sep 22:52
  STXUSDT|gen_b9bf5d01               1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 04 Sep 22:52
  ZORAUSDT|gen_f4e37ccc              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 04 Sep 22:52
  ZORAUSDT|gen_fec39d1f              1/3 pass · validata il 13 Sep 00:00 · ultimo pass 30 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 04 Sep 22:52
  AGTUSDT|gen_08664b28               1/3 pass · validata il 14 Sep 00:00 · ultimo pass 31 Aug 00:00 · finestra chiusa il 07 Sep 00:00 · vista 02 Sep 04:58
  AGTUSDT|gen_ba3a671f               1/3 pass · validata il 14 Sep 00:00 · ultimo pass 31 Aug 00:00 · finestra chiusa il 07 Sep 00:00 · vista 02 Sep 04:58
  AXSUSDT|gen_b922252e               1/3 pass · validata il 14 Sep 00:00 · ultimo pass 31 Aug 00:00 · finestra chiusa il 07 Sep 00:00 · vista 04 Sep 22:52
  BERAUSDT|gen_9d63c7b4              1/3 pass · validata il 14 Sep 00:00 · ultimo pass 31 Aug 00:00 · finestra chiusa il 07 Sep 00:00 · vista 04 Sep 19:49
  BICOUSDT|gen_f238d283              1/3 pass · validata il 14 Sep 00:00 · ultimo pass 31 Aug 00:00 · finestra chiusa il 07 Sep 00:00 · vista 04 Sep 22:52

--- QUANDO RIPARTE IL BOT ---
  Al piu' presto il 13 Sep 00:00 (fra 8.0 giorni), quando la 10a coppia
  raggiungerebbe 3 pass.
  E' un LIMITE INFERIORE: assume che ognuna passi almeno una volta per
  finestra settimanale. Chi non passa per 2 finestre intere esce dal registro,
  quindi la data vera puo' essere piu' in la'. Serve anche coprire >= 5 coin distinte (10 coppie
  su coin diverse bastano).
```
