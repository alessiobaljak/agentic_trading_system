# Programma 6 — ventesima prova: il volume a pronti contro quello del perpetuo (S1, S2)

Scritto il 20 ottobre 2026, **prima di scaricare i dati a pronti e di qualunque calcolo**. Idea 10 della coda di
`research/REGISTRO.md`. Vale `OTTAVA.md` (F3) dove qui non si dice altro.

## 1. Perché

* Una moneta può essere scambiata soprattutto a pronti (chi compra la moneta vera, con il denaro intero) o soprattutto sul
  perpetuo (chi scommette con la leva). Nessuna prova del programma 5 o 6 ha mai usato i dati a pronti.
* **S1, il livello**: le monete mosse dalla leva (quota a pronti bassa) sono quelle dove si concentra la domanda «da
  lotteria» con la leva, che di solito paga meno nel tempo (lo stesso motivo del funding alto di F3); le monete mosse dal
  denaro a pronti no.
* **S2, il cambio**: quando la quota a pronti sale rispetto ai mesi prima, entra denaro vero; le prove 9 e 11 dicono che fra
  monete i flussi di denaro **continuano** (gli acquisti a mercato e l'interesse aperto che cresce vanno nel verso della
  moneta). Qui il flusso è quello a pronti.

## 2. La regola

* **Dati**: candele giornaliere a pronti contro USDT dell'archivio pubblico (`scarico_spot.py`, con il CHECKSUM), per le monete
  passate almeno una volta dall'universo delle 100; il nome a pronti è quello del perpetuo o senza il prefisso dei multipli
  (1000PEPEUSDT → PEPEUSDT). Le monete senza coppia a pronti quella settimana non entrano.
* **Quota a pronti** di una moneta in un periodo: volume a pronti in dollari diviso (volume a pronti + volume del perpetuo).
* **S1**: la quota dei 7 giorni prima del lunedì; long il quinto con la quota più alta, short il più basso.
* **S2**: il logaritmo della quota dei 7 giorni prima diviso la quota dei 90 giorni prima (servono almeno 60 giorni con
  tutti e due i volumi); long il quinto con il cambio più alto, short il più basso.
* Universo, pesi (inverso della volatilità dei 30 giorni), costi e funding come F3, con le correzioni del controllo dei dati
  del 20 ottobre (`controllo_zombi.py`).
* Due prove: nel conto del programma 6 diventano **46**.

## 3. L'esame

Come F3: dal **4 gennaio 2021**, `terza.esame` e `terza.esito` con lo Sharpe corretto sulle **46** prove. Si riportano anche
(senza decidere niente): quante monete-settimana non hanno la coppia a pronti, la quota a pronti media, la correlazione con
F3 e M1.
