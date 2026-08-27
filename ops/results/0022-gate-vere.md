# 0022-gate-vere.req

_eseguito: 2026-08-27 01:23 UTC_

**richiesta:** `gate`
**eseguito:** `.venv/bin/python -m scripts.gate_progress`
**esito:** codice 0 in 1.2s

```
[firebase] connesso (Firestore + RTDB)
[gate] 2992 coppie nel registro · 1720 ancora valutate · soglia 3 pass · un pass ogni 168h di dati nuovi
  distribuzione pass (solo coppie vive): 0 pass: 1583 · 1 pass: 137
  CONGELATE: 1272 coppie non piu' valutate da oltre 3 giorni (1 avevano gia' un passaggio).
  La coin e' uscita dall'universo — di solito per storia insufficiente o delisting.
  Non avanzano e non falliscono: sono escluse da tutti i conti qui sotto.
  VALIDATE ora: 0 su 0 coin distinte
  ready dichiarato dal registro: False (via —)
  FINESTRE APERTE: 42/137 coppie con almeno un passaggio.
  E' QUESTO il numero da guardare: solo queste stanno contando i giorni verso la
  conferma successiva, e solo queste compaiono nel calendario qui sotto.
  Le altre 95 sono ferme: la finestra si apre solo quando la coppia RIPASSA
  il gate, quindi per loro la prossima conferma non ha una data — dipende da un
  evento che potrebbe non succedere.

--- QUANDO ARRIVANO LE PROSSIME CONFERME (limite inferiore) ---
  MORPHOUSDT|gen_13cc61f2            1/3 pass · validata il 01 Sep 00:00 · ultimo pass 18 Aug 00:00 · finestra chiusa il 25 Aug 00:00 · vista 26 Aug 22:33
  APTUSDT|gen_3ec4804d               1/3 pass · validata il 02 Sep 00:00 · ultimo pass 15 Aug 00:00 · finestra chiusa il 26 Aug 00:00 · vista 26 Aug 22:33
  DOTUSDT|gen_837621e3               1/3 pass · validata il 02 Sep 00:00 · ultimo pass 17 Aug 00:00 · finestra chiusa il 26 Aug 00:00 · vista 26 Aug 22:33
  EIGENUSDT|gen_82d2c2da             1/3 pass · validata il 02 Sep 00:00 · ultimo pass 17 Aug 00:00 · finestra chiusa il 26 Aug 00:00 · vista 26 Aug 22:33
  GPSUSDT|gen_5b7f8f78               1/3 pass · validata il 02 Sep 00:00 · ultimo pass 19 Aug 00:00 · finestra chiusa il 26 Aug 00:00 · vista 26 Aug 22:33
  GPSUSDT|gen_7b4a474b               1/3 pass · validata il 02 Sep 00:00 · ultimo pass 17 Aug 00:00 · finestra chiusa il 26 Aug 00:00 · vista 26 Aug 22:33
  GPSUSDT|gen_8a66a70b               1/3 pass · validata il 02 Sep 00:00 · ultimo pass 19 Aug 00:00 · finestra chiusa il 26 Aug 00:00 · vista 26 Aug 22:33
  HBARUSDT|gen_03632d45              1/3 pass · validata il 02 Sep 00:00 · ultimo pass 19 Aug 00:00 · finestra chiusa il 26 Aug 00:00 · vista 26 Aug 22:33
  JTOUSDT|gen_f238d283               1/3 pass · validata il 02 Sep 00:00 · ultimo pass 19 Aug 00:00 · finestra chiusa il 26 Aug 00:00 · vista 26 Aug 22:33
  MOVEUSDT|gen_764205c3              1/3 pass · validata il 02 Sep 00:00 · ultimo pass 19 Aug 00:00 · finestra chiusa il 26 Aug 00:00 · vista 26 Aug 22:33
  MOVEUSDT|gen_7efb659e              1/3 pass · validata il 02 Sep 00:00 · ultimo pass 19 Aug 00:00 · finestra chiusa il 26 Aug 00:00 · vista 26 Aug 22:33
  ORDIUSDT|gen_2bb283ca              1/3 pass · validata il 02 Sep 00:00 · ultimo pass 19 Aug 00:00 · finestra chiusa il 26 Aug 00:00 · vista 26 Aug 22:33
  PORTALUSDT|gen_1837e26a            1/3 pass · validata il 02 Sep 00:00 · ultimo pass 19 Aug 00:00 · finestra chiusa il 26 Aug 00:00 · vista 26 Aug 22:33
  PORTALUSDT|gen_1d308e90            1/3 pass · validata il 02 Sep 00:00 · ultimo pass 19 Aug 00:00 · finestra chiusa il 26 Aug 00:00 · vista 26 Aug 22:33
  PROMUSDT|gen_cd5c842f              1/3 pass · validata il 02 Sep 00:00 · ultimo pass 19 Aug 00:00 · finestra chiusa il 26 Aug 00:00 · vista 26 Aug 22:33

--- QUANDO RIPARTE IL BOT ---
  Al piu' presto il 02 Sep 00:00 (fra 5.9 giorni), quando la 10a coppia
  raggiungerebbe 3 pass.
  E' un LIMITE INFERIORE: assume che ognuna passi almeno una volta per
  finestra settimanale. Chi non passa per 2 finestre intere esce dal registro,
  quindi la data vera puo' essere piu' in la'. Serve anche coprire >= 5 coin distinte (10 coppie
  su coin diverse bastano).
```
