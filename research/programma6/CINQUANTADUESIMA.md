# Programma 6 — cinquantaduesima prova: scommettere contro il beta (B1)

Scritto il 22 ottobre 2026, pomeriggio, **prima del calcolo**. Idea nuova (in coda dal 22 ottobre): nel programma 5 i fattori
fra monete, beta compreso, erano stati provati solo a ore (E-114, bruciati); a settimane con la banda mai.

## 1. Perché

Frazzini e Pedersen («Betting Against Beta», *Journal of Financial Economics* 2014) trovano in 20 mercati diversi (azioni,
obbligazioni, valute, materie prime) che i titoli con il beta basso rendono più di quanto il loro rischio giustifica e quelli con
il beta alto meno: chi non può usare la leva compra i titoli più mossi per avere più rendimento, e li paga troppo. Fra le
criptovalute vale lo stesso meccanismo: le monete che si muovono più del Bitcoin attirano chi vuole la «leva senza leva».
Si tiene il portafoglio neutro rispetto al Bitcoin: long le monete con il beta basso con più capitale, short quelle con il beta
alto con meno, così che le due gambe abbiano lo stesso beta.

## 2. La regola (valori fissati qui)

* **Monete**: l'universo della settimana (le 100 più scambiate, dati corretti).
* **Beta** di ogni moneta: la pendenza dei rendimenti giornalieri sui rendimenti del Bitcoin nei **90 giorni** prima del lunedì
  (almeno 60 giorni con il dato).
* **Scelta** con la banda di F5 (`ventiquattresima.pesi_banda`, entrata nel 20%, uscita oltre il 40%) sul segnale −beta: long le
  monete con il beta più basso, short quelle con il beta più alto; dentro ogni lato pesi secondo l'inverso della volatilità.
* **Neutro al Bitcoin**: il lato long si moltiplica per 1 / (beta medio pesato del lato long), il lato short per 1 / (beta medio
  pesato del lato short), ciascuno al massimo **2** volte.
* Costi e funding come F5 (`terza.conto`). Dal 4 gennaio 2021 al 5 ottobre 2026. Una prova: nel conto diventano **111**.

## 3. L'esame

`terza.esame` e `terza.esito` con lo Sharpe corretto rivisto (`asticella.py`), soglia 0,95; si riportano anche il beta verso il
Bitcoin del portafoglio, la leva media dei due lati e la correlazione con F5.
