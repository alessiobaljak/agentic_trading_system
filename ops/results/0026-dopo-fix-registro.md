# 0026-dopo-fix-registro.req

_eseguito: 2026-08-31 11:01 UTC_

**richiesta:** `gate`
**eseguito:** `.venv/bin/python -m scripts.gate_progress`
**esito:** codice 0 in 1.0s

```
[firebase] connesso (Firestore + RTDB)
[gate] 3041 coppie nel registro · 1609 ancora valutate · soglia 3 pass · un pass ogni 168h di dati nuovi
  distribuzione pass (solo coppie vive): 0 pass: 1607 · 1 pass: 2
  CONGELATE: 1432 coppie non piu' valutate da oltre 3 giorni (0 avevano gia' un passaggio).
  La coin e' uscita dall'universo — di solito per storia insufficiente o delisting.
  Non avanzano e non falliscono: sono escluse da tutti i conti qui sotto.
  COMPOSIZIONE (vive): 1609 base · 0 generate.  Nel registro intero: 3041 base su 3041, tetto 3000.
  ATTENZIONE: le coppie base occupano quasi tutto il tetto. Non vengono mai potate,
  quindi lo spazio che resta alle generate — le uniche che passano il gate — si
  riduce a 0.
  fallimenti accumulati: 1 fallimenti: 1177
  VALIDATE ora: 0 su 0 coin distinte
  ready dichiarato dal registro: False (via —)
  FINESTRE APERTE: 2/2 coppie con almeno un passaggio.
  E' QUESTO il numero da guardare: solo queste stanno contando i giorni verso la
  conferma successiva, e solo queste compaiono nel calendario qui sotto.
  Le altre 0 sono ferme: la finestra si apre solo quando la coppia RIPASSA
  il gate, quindi per loro la prossima conferma non ha una data — dipende da un
  evento che potrebbe non succedere.

--- QUANDO ARRIVANO LE PROSSIME CONFERME (limite inferiore) ---
  MUBARAKUSDT|mean_reversion         1/3 pass · validata il 12 Sep 00:00 · ultimo pass 21 Aug 00:00 · finestra chiusa il 05 Sep 00:00 · vista 31 Aug 09:43 · 1 fallimenti di fila
  MUSDT|mean_reversion               1/3 pass · validata il 13 Sep 00:00 · ultimo pass 13 Aug 00:00 · finestra chiusa il 06 Sep 00:00 · vista 30 Aug 09:33 · 1 fallimenti di fila

--- QUANDO RIPARTE IL BOT ---
  Coppie con almeno una conferma: 2. Ne servono 10.
  Finche' non ce ne sono abbastanza NON esiste una data: prima devono passare
  il gate, poi si conta il tempo.
```
