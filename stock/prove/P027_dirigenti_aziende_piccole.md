# Prova 27 — gli acquisti dei dirigenti nelle aziende fuori dall'S&P 500

Regole scritte il 12 novembre 2026 **prima di qualsiasi calcolo** e prima di scaricare i prezzi di queste aziende, committate prima di
lanciare il programma (idea I29 di `REGISTRO.md`; il proprietario, 12 novembre: «voglio che continui a trovarne e provarne di nuove»).
Si conoscevano le prove 1-26. In particolare la prova 18 (stessa regola sulle aziende dell'S&P 500: bocciata, il mercato reagisce già
nella notte dopo il deposito, +0,42% rispetto allo SPY, poi niente) e la 19. Contano come **2 prove** (la strategia, e la miscela con
la parte nuova): 69 nel conto.

## Perché dovrebbe funzionare qui e non nelle 500 grandi

Chi guida un'azienda sa di lei più del mercato, e un acquisto con i suoi soldi è un segnale costoso. Negli studi il guadagno dopo gli
acquisti dei dirigenti sta quasi tutto nelle **aziende piccole**, poco seguite dagli analisti e dai fondi veloci: Lakonishok, Lee, «Are
insider trades informative?», *Review of Financial Studies* 14 (2001); Jeng, Metrick, Zeckhauser, «Estimating the returns to insider
trading», *Review of Economics and Statistics* 85 (2003). **Sospetti scritti prima:** nelle aziende piccole lo scarto fra acquisto e
vendita è largo e non l'abbiamo misurato; le aziende piccole hanno avuto anni cattivi (2022) e una regola che compra solo porta tutto
quel rischio; le aziende sparite dal listino (fallite o comprate) possono mancare dai prezzi, e questo abbellisce il risultato; i
servizi che pubblicano i moduli in pochi minuti esistono anche qui.

## I dati

* **Gli acquisti:** i dati trimestrali della SEC già usati dalla prova 18 (`stock/dati/dirigenti.py`): moduli 4, codice P (acquisto sul
  mercato), di un dirigente o di un consigliere; vale la **data di deposito**. Stessa pulizia: si scarta un'operazione il cui prezzo
  dista più del 50% dalla chiusura del titolo quel giorno (o il giorno di borsa prima).
* **I prezzi:** al giorno di Alpaca, non rettificati, con dividendi e frazionamenti (come le altre prove), scaricati da un lavoro di
  GitHub (le chiavi stanno lì); nel repository entrano solo i risultati.
* **Controllo dei dati:** si contano e si dichiarano gli eventi senza prezzi su Alpaca, e i titoli che spariscono dal listino mentre
  sono in mano (restano valutati all'ultima chiusura: se sono tanti, il risultato va letto con sospetto).

## La regola (la stessa della prova 18, con un filtro perché il titolo si possa davvero comprare)

* **Evento:** per ogni azienda e giorno di deposito, la somma degli acquisti puliti, se è almeno **100'000 dollari** (come la prova 18).
* **Quali aziende:** quelle che il giorno del deposito **non** sono nell'S&P 500 (composizione storica) e che quel giorno hanno: chiusura
  di almeno **5 dollari**, e mediana dei dollari scambiati nelle 20 sedute prima di almeno **2 milioni** (numeri fissati qui: sotto,
  un ordine da 5'000 dollari non è realistico).
* **Ingresso:** a mercato all'apertura del primo giorno di borsa **dopo** il deposito, con il **5%** del conto, azioni intere; al
  massimo 20 titoli insieme; se i posti non bastano, prima gli acquisti di valore più alto. Titolo già in mano: niente.
* **Uscita:** a mercato all'apertura del 21° giorno di borsa dopo l'ingresso (20 sedute).
* **Periodo:** depositi dal 1° gennaio 2016 al 30 novembre 2024.

## I costi (fissati prima)

Metà scarto **15 punti base** e slittamento **5 punti base** per tutti (lo scarto vero delle aziende piccole non è misurato: è una stima
prudente, tre volte quella usata per le azioni non misurate dell'S&P 500); commissioni Interactive Brokers «fisso»; versione con i
costi raddoppiati. Se la prova passa, prima di ogni altro passo si misura lo scarto vero su un campione di eventi.

## L'esame

**Da sola:** (1) Sharpe annuo con i costi più alto del tenere lo SPY e del tenere l'IWM (il fondo sulle aziende piccole) sugli stessi
giorni; (2) Sharpe corretto ≥ 0,95 con tutte le serie del conto; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei
trimestri in guadagno.

**Per entrare nella miscela** (idea I30): Sharpe con i costi sopra zero, anche con i costi doppi; correlazione dei rendimenti
giornalieri con la miscela della prova 25 sotto 0,3; la miscela nuova (tre quarti la miscela, un quarto la parte nuova) con lo Sharpe
più alto della miscela e del tenere lo SPY.

Da leggere accanto: il guadagno medio per evento rispetto all'IWM e allo SPY e il suo t; il risultato anno per anno; quanti eventi
dopo ogni filtro. La famiglia «dirigenti» ha già usato il periodo chiuso (prova 19): se la prova passa uno dei due esami, revisore
separato e poi la conferma **in avanti** sul demo.
