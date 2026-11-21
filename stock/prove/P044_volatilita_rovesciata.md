# Prova 44 — la volatilità rovesciata: tenere VIXY solo quando il VIX supera il VIX a tre mesi

Regole scritte il 21 novembre 2026 **prima di qualsiasi calcolo sui prezzi di VIXY** (idea I50 di `REGISTRO.md`). Visti prima solo i
dati degli indici (CBOE e Yahoo): dal dicembre 2015 al dicembre 2024 il VIX ha chiuso sopra il VIX a tre mesi in **163 giorni su
2'286**, con **104 cambi di stato** (circa 52 volte dentro); nessun rendimento di VIXY. Si conoscevano le prove 1-43, in particolare la
15 (più investiti in SPY e QQQ quando il mercato è calmo: è nella miscela del demo), la 26 e la 43 (non entrano nella miscela perché si
muovono con le azioni). Contano come **2 prove** (la strategia da sola, e la miscela con lei).

## Perché dovrebbe funzionare

VIXY tiene i future sul VIX del primo e del secondo mese. Di solito i future costano più del VIX di oggi (la curva sale) e chi li tiene
perde ogni mese (è il premio che si paga per assicurarsi). Quando la curva si **rovescia** (il VIX di oggi sopra quello atteso), il
premio cambia segno: Johnson, «Risk Premia and the VIX Term Structure», Journal of Financial and Quantitative Analysis 52 (2017): la
forma della curva del VIX prevede i rendimenti dei future sul VIX (e degli swap sulla varianza), e con la curva rovesciata i rendimenti
attesi di chi compra la volatilità sono positivi; Simon e Campasano, Journal of Derivatives 21 (2014): la differenza fra i future e il
VIX prevede i rendimenti dei future, non i movimenti del VIX. **Per la miscela** è una parte che guadagna quando le azioni crollano:
la sua correlazione con la miscela dovrebbe essere bassa o negativa, al contrario delle prove 26 e 43.

**Sospetti scritti prima:**

* **si entra dopo il salto**: la curva si rovescia quando il VIX è già salito; se il crollo è di un giorno (5 febbraio 2018, 5 agosto
  2024) si compra in cima e si perde, si guadagna solo nelle crisi che durano (marzo 2020);
* **pochi episodi** (circa 52, e pochi grandi): il t può restare basso anche con un vantaggio vero, e un solo episodio (il 2020) può
  fare tutto il risultato;
* **VIXY è un prodotto cattivo da tenere a lungo** (perde quasi sempre); qui si tiene solo nei giorni rovesciati, ma l'uscita arriva
  quando la curva torna normale, spesso dopo che il VIX è già sceso;
* **la famiglia «volatilità»** ha già aperto il periodo chiuso con la prova 15 (anche lì si guarda la volatilità): se questa passa, la
  conferma indipendente è solo in avanti.

## I dati

* **VIX e VIX a tre mesi:** le chiusure di ogni giorno di CBOE (`cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv` e
  `VIX3M_History.csv`, pubbliche), scaricate dal lavoro di GitHub, mai nel repository.
* **VIXY:** barre al giorno di Alpaca con i raggruppamenti delle azioni (`prepara_titolo`, come le altre prove), su GitHub.

## La regola

* **Il segnale:** alla chiusura di ogni giorno di borsa, **rovesciata** se la chiusura del VIX è **maggiore o uguale** a quella del
  VIX a tre mesi.
* **Dentro e fuori:** quando il segnale passa a «rovesciata», si compra VIXY con tutto il conto della parte, a mercato all'apertura del
  giorno di borsa dopo; quando torna normale, si vende tutto all'apertura del giorno dopo. Nessun altro ordine (niente ribilanciamenti
  mentre si è dentro). Solo acquisti, niente leva.
* **Periodo:** dal 4 gennaio 2016 al 31 dicembre 2024 (il segnale del 31 dicembre 2015 vale per il primo giorno). Il periodo chiuso
  non si usa.

## I costi (fissati prima, come la prova 43)

Metà dello scarto **5 punti base** per lato (VIXY non è nelle misure di `dati/ESITO_CONTROLLI_UNIVERSO.md`), slittamento 1 punto base,
commissioni Interactive Brokers «fisso». Versione con tutti i costi raddoppiati.

## L'esame (uguale alle prove 28 e 30-43)

**Da sola:** (1) Sharpe annuo con i costi più alto del tenere lo SPY sugli stessi giorni; (2) Sharpe corretto ≥ 0,95 con tutte le
serie del conto; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei trimestri in guadagno.

**Per entrare nella miscela** (idea I30 rafforzata): Sharpe con i costi sopra zero, anche con i costi doppi; correlazione con la
miscela della prova 25 sotto 0,3; la miscela nuova (tre quarti la miscela, un quarto la parte nuova) con lo Sharpe più alto della
miscela e del tenere lo SPY; il t dello Sharpe della parte almeno 1,3; la miscela nuova più alta in almeno l'80% di 2000 campionamenti a
blocchi di 20 giorni.

Da leggere accanto (non cambiano l'esito): quante volte dentro e quanti giorni; il guadagno di ogni episodio (i 5 più grandi e i 5
peggiori, con le date); quanto del totale viene dal 2020; la correlazione con lo SPY e con la miscela; l'anno per anno.

**Se passa uno dei due esami:** revisore separato; poi, poiché la famiglia ha già usato il periodo chiuso (prova 15), la conferma
è solo in avanti, sul demo, e la decide il proprietario.
