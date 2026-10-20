# Programma 6 — ventiduesima prova: la leva che entra continua, conferma sulle monete 101-200 (L1, L2)

Scritto il 20 ottobre 2026, pomeriggio, **prima di scaricare i dati a pronti delle 115 monete che mancano e di qualunque
calcolo sulle monete 101-200 con questi segnali**.

## 1. Perché

* Tre volte, con tre dati diversi, sulle 100 monete più scambiate il verso è risultato **opposto** a quello scritto, e sempre
  lo stesso: quando la leva entra in una moneta, la moneta continua per una settimana rispetto alle altre.
  * acquisti a mercato dei 7 giorni (prova 9, G1): la regola «contro» fa Sharpe −1,17;
  * crescita dell'interesse aperto dei 7 giorni (prova 11, P2): −0,94;
  * quota del volume a pronti che scende rispetto ai 90 giorni, cioè quella del perpetuo che sale (prova 20, S2): −0,82.
* Viste dopo il calcolo, sulle 100 non valgono come prova. Qui si prova l'**ipotesi**, scritta ora, su monete dove questi
  segnali non sono mai stati guardati per la scelta: le **101-200**. Per gli acquisti a mercato le 101-200 sono già state
  guardate nella nona prova (G1 lì fa Sharpe −0,75: lo stesso verso), quindi la conferma vera è sulla quota a pronti.

## 2. La regola

* **Universo**: le monete 101-200 per volume (terza prova con `da=100, a=200`), dati corretti del 20 ottobre.
* **L1**: il cambio della quota a pronti (S2 della prova 20) **con il verso nuovo**: long il quinto con la quota a pronti
  scesa di più (la leva che entra), short il quinto con la quota salita di più.
* **L2**: la media dei ranghi di **+ acquisti a mercato dei 7 giorni** (quota del volume comprato a mercato, come G1) e
  **− cambio della quota a pronti**; long il quinto più alto, short il più basso.
* Pesi secondo l'inverso della volatilità dei 30 giorni; costi 0,05% di commissione più **0,10%** di scarto (le monete
  101-200, come le prove 7 e 8); funding con il segno.
* Dati a pronti: `scarico_spot.py` per le 115 monete passate dalle 101-200 che non li hanno ancora.

## 3. L'esame

L'esame di conferma della settima prova (`settima.esito`), con la soglia divisa per due perché le varianti sono due: media
settimanale netta sopra zero con **p ≤ 0,005** a una coda (bootstrap a blocchi di 4 settimane) e intervallo sopra zero,
positiva in almeno tre quarti degli anni con almeno 26 settimane, positiva nell'ultimo anno, a costi doppi e senza le 5
settimane migliori; dal 4 gennaio 2021. Non vale la condizione sul funding di `settima.esito` (è per le strategie del
funding). Si riportano anche la correlazione con K1 e con le stesse regole
sulle 100 (descrittive). Due prove di conferma: nel registro si contano come 2.
