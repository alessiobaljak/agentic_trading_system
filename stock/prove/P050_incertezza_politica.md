# Prova 50 — l'incertezza sulla politica economica (Baker, Bloom e Davis): più investiti nello SPY quando è alta

Regole scritte il 25 novembre 2026 **prima di qualsiasi calcolo sui prezzi** (idea I58 di `REGISTRO.md`). Del dato nuovo si sono visti
solo la forma e i conteggi: `policyuncertainty.com/media/All_Daily_Policy_Data.csv`, colonne giorno, mese, anno e `daily_policy_index`,
un valore per ogni giorno del calendario dal 1° gennaio 1985 al 24 novembre 2026, nessuno vuoto. Si conoscevano le prove 1-49, in
particolare la 49 (la stessa forma di regola, con il DIX: bocciata, il dato non separava le settimane), la 16 (98% o 49%) e la 15 (meno
investiti con il mercato agitato, nella miscela). Contano come **2 prove** (la strategia da sola, e la miscela con lei): 116 e 117 nel
conto.

## Perché dovrebbe funzionare

Brogaard e Detzel, «The Asset-Pricing Implications of Government Economic Policy Uncertainty», Management Science 61 (2015), 3-18:
l'indice di Baker, Bloom e Davis (quanto i giornali americani parlano di incertezza sulla politica economica) **prevede i rendimenti
del mercato con il segno più**. Una deviazione standard in più dell'indice vale circa **+1,5 punti di rendimento nei tre mesi dopo**
(circa il 6% l'anno): chi tiene azioni quando la politica è incerta chiede un premio, e lo incassa dopo. Il loro campione finisce prima
del 2016: il nostro 2016-2024 è fuori.

**Sospetti scritti prima:**

* **non è lo stesso indice dello studio**: lo studio usa l'indice mensile costruito su 10 grandi giornali; qui la media del mese
  dell'indice giornaliero (circa 1'000 giornali, stessi autori), perché si conosce subito a fine mese senza aspettare la pubblicazione;
* **il dato può essere stato rifatto**: l'indice giornaliero si ricalcola sull'archivio dei giornali, che cambia; non si sa se i
  valori di allora erano quelli di oggi;
* **va contro la regola della calma della miscela** (meno investiti con il mercato agitato): l'incertezza alta arriva spesso con il
  mercato agitato. Può essere un vantaggio (diversifica) o un doppione con il segno al contrario;
* **pochi casi**: 108 decisioni mensili in 9 anni; con un effetto di 1,5 punti in tre mesi, la prova ha poca forza;
* **lo studio è uno solo** e l'effetto sul mercato intero è la parte meno forte del suo lavoro (la parte principale è fra le azioni).

## I dati

* **L'incertezza:** `daily_policy_index` del file giornaliero, scaricato dal programma, mai nel repository. Il valore di un giorno si
  conosce il giorno dopo.
* **Lo SPY:** chiusure giornaliere rettificate per i dividendi (Yahoo, in locale, mai nel repository), come le prove 15, 16, 48 e 49.

## La regola

* **La decisione, una volta al mese** (la cadenza dello studio e della prova 16): la media dell'indice di tutti i giorni del mese appena
  finito si confronta con la media dei **12 mesi prima** (tutti i giorni dei 12 mesi prima di quello appena finito). Se la media del mese
  è **più alta**: lo SPY al **98%** del conto; se è più bassa o uguale: al **49%**.
* **Quando si esegue:** alla **chiusura del primo giorno di borsa del mese dopo** (asta di chiusura): il valore dell'ultimo giorno del
  mese si conosce solo il giorno dopo.
* **La partenza:** la prima decisione con 12 mesi prima nel file (il file parte nel 1985: dal 2016 sempre).
* **Il resto del conto** non rende niente (come le prove 15, 16 e 49).
* **Periodo:** dal 4 gennaio 2016 al 31 dicembre 2024. Il periodo chiuso non si usa.

## I costi (come le prove 48 e 49)

A ogni cambio di quota: slittamento di 0,5 punti base sulla parte comprata o venduta (all'asta di chiusura, nessuno scarto) e la
commissione di Interactive Brokers «fisso» sulle azioni comprate o vendute. Versione con tutti i costi raddoppiati.

## L'esame (uguale alle prove 28 e 30-49)

**Da sola:** (1) Sharpe annuo con i costi più alto del tenere lo SPY sugli stessi giorni; (2) Sharpe corretto ≥ 0,95 con tutte le serie
del conto; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei trimestri in guadagno.

**Per entrare nella miscela** (la parte è la regola intera, come nelle prove 30-49): Sharpe con i costi sopra zero, anche con i costi
doppi; correlazione con la miscela della prova 25 sotto 0,3; la miscela nuova (tre quarti la miscela, un quarto la parte nuova) con lo
Sharpe più alto della miscela e del tenere lo SPY; il t dello Sharpe della parte almeno 1,3, anche senza marzo 2020; la miscela nuova più
alta in almeno l'80% di 2000 campionamenti a blocchi di 20 giorni. (La regola sta sempre almeno per metà nello SPY: la correlazione con la
miscela sarà probabilmente alta, ed è giusto che l'esame lo conti.)

Da leggere accanto (non cambiano l'esito): **lo SPY tenuto sempre alla quota media della regola** (se rende come la regola, l'incertezza
non aggiunge niente); la regola al contrario (98% con l'incertezza bassa); il rendimento medio dello SPY nel mese e nei 3 mesi dopo le
decisioni con l'incertezza alta e con quella bassa, con il t (la misura dello studio); la correlazione fra la decisione e il rendimento
dello SPY del mese prima (se è forte, l'incertezza ripete il «comprare dopo le cadute»); quante volte cambia la quota per anno; l'anno per
anno.

**Se passa uno dei due esami:** revisore separato, poi il periodo chiuso (dal 2 gennaio 2025 al 30 settembre 2026) **una volta**: la
famiglia «incertezza politica» non l'ha mai usato.
