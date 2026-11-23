# Prova 48 — la settimana della scadenza delle opzioni: tenere lo SPY solo dalla chiusura del venerdì prima alla chiusura della scadenza

Regole scritte il 23 novembre 2026 **prima di qualsiasi calcolo** (idea I56 di `REGISTRO.md`). Si conoscevano le prove 1-47, in
particolare le 9 e 14 (giorni speciali del calendario, bocciate nel periodo chiuso) e la 45 (la copertura delle opzioni cambia il modo in
cui si muove il mercato). Contano come **2 prove** (la strategia da sola, e la miscela con lei).

## Perché dovrebbe funzionare

Stivers e Sun, «Returns and option activity over the option-expiration week for S&P 100 stocks», Journal of Banking & Finance 37
(2013): nella settimana che finisce con la scadenza mensile delle opzioni (il terzo venerdì) le grandi azioni con molte opzioni rendono
di più (nella versione di lavoro: 0,45% a settimana contro 0,12% nelle altre, 28 grandi azioni, 1996-2008), e nella settimana dopo meno
(−0,03%); gli autori lo legano al calo della paura misurata dalle opzioni durante quella settimana. Il meccanismo è lo stesso della
prova 45: chi vende opzioni si copre, e verso la scadenza la sua copertura cambia in modo prevedibile.

**Sospetti scritti prima:** (1) l'idea è molto diffusa (siti di strategie, programmi di prova pubblici): può essere consumata; (2) dal
2016 esistono le scadenze settimanali e giornaliere, che hanno tolto peso alla scadenza mensile; (3) è un effetto di calendario: la
famiglia «calendario» ha già usato il periodo chiuso (prove 9 e 14), quindi **se passa, la conferma è solo il demo**; (4) investita
circa un quarto del tempo, si muove con lo SPY in quei giorni: la correlazione con la miscela può superare 0,3.

## I dati

Le chiusure giornaliere dello SPY di Yahoo con i dividendi (`stock/dati/yahoo.py`), scaricate da qui e mai nel repository.

## La regola

* **Il giorno della scadenza:** il terzo venerdì di ogni mese; se quel venerdì la borsa è chiusa, l'ultimo giorno di borsa prima.
* **La settimana:** dalla **chiusura** dell'ultimo giorno di borsa prima del lunedì di quella settimana (di solito il venerdì prima)
  alla **chiusura** del giorno della scadenza. In quei giorni si tiene lo SPY con il 98% del conto, negli altri si sta fuori (contanti
  senza interessi, come le altre prove).
* **Gli ordini:** alle aste di chiusura (entrata e uscita), nessuno scarto.
* **Periodo:** dal 4 gennaio 2016 al 31 dicembre 2024. Il periodo chiuso non si usa.

## I costi (fissati prima)

Slittamento 0,5 punti base per ordine (come le prove 1 e 45), commissioni Interactive Brokers «fisso». Versione con i costi raddoppiati.

## L'esame (uguale alle prove 28 e 30-47)

**Da sola:** (1) Sharpe annuo con i costi più alto del tenere lo SPY sugli stessi giorni; (2) Sharpe corretto ≥ 0,95 con tutte le
serie del conto; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei trimestri in guadagno.

**Per entrare nella miscela:** Sharpe con i costi sopra zero, anche con i costi doppi; correlazione con la miscela della prova 25 sotto
0,3; la miscela nuova (tre quarti la miscela, un quarto la parte nuova) con lo Sharpe più alto della miscela e del tenere lo SPY; il t
dello Sharpe della parte almeno 1,3; la miscela nuova più alta in almeno l'80% di 2000 campionamenti a blocchi di 20 giorni; **e senza
marzo 2020 il t della parte resta almeno 1,3** (come la prova 47).

Da leggere accanto: il rendimento medio dello SPY nelle settimane della scadenza, nella settimana dopo e nelle altre, con il t; prima e
dopo il 2020; l'anno per anno.
