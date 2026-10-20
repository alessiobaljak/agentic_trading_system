# Programma 6 — il paper delle candidate (misura sui dati nuovi)

Scritto il 19 ottobre 2026, sera, **prima di qualunque dato dopo il 17 ottobre 2026**, su delega del proprietario («se
pensi serva misurare in paper procedi hai campo libero fino a che non trovi cosa funziona», 19 ottobre 2026). `DRY_RUN`
resta vero: niente soldi veri, niente chiavi, il bot sulla macchina non cambia.

## 1. Cosa si misura

Le candidate del programma 6, con le regole **già scritte e già calcolate sul passato**, senza cambiare niente:

| Nome | Regola | Da | Sul passato |
|---|---|---|---|
| **F2** | il funding fra monete, pesi uguali: ogni lunedì, fra le 100 monete più scambiate, long il quinto con il funding dei 7 giorni prima più basso, short il quinto più alto (`SESTA.md`) | `sesta.py` | +47,5% l'anno, Sharpe 1,03 dal 2021 |
| **C1** | CTREND: 28 indicatori combinati, long il quinto più forte, short il più debole delle 100 più scambiate, ogni lunedì (`TERZA.md`) | `terza.py` | Sharpe 0,39 dal 2022; 1,49 dopo l'aprile 2025 |
| **A1** | la regola pubblicata di tendenza: 9 canali di Donchian, volatilità al 25%, 20 monete più liquide, ogni giorno (`SECONDA.md`) | `seconda.py` | Sharpe 0,53 dal 2021 |

F2 è la candidata principale. C1 e A1 si misurano perché costano poco e la loro correlazione con F2 è bassa.

**Aggiunta del 19 ottobre 2026, sera, ancora prima di qualunque dato nuovo** (i dati nell'archivio arrivano al 18 ottobre, il
periodo P comincia il 20 per i giorni e il 26 per le settimane): **F3**, il funding fra monete con i pesi secondo la
volatilità (`OTTAVA.md`, `ottava.py`; sul passato +50,6% l'anno, Sharpe 1,28 dal 2021, positiva in ogni anno), diventa la
candidata principale insieme a F2. Il verdetto di F3 segue la sezione 3 come le altre.

**Seconda aggiunta, stessa sera, ancora prima di qualunque dato nuovo**: **K1** (`DODICESIMA.md`, `dodicesima.py`): denaro
che entra e leva che costa poco (la media dei ranghi di −funding, +acquisti a mercato e +crescita dell'interesse aperto
dei 7 giorni prima). Sul passato è **costruzione** (due versi visti dopo il calcolo: +37,6% l'anno dal 2022, Sharpe 1,27):
per K1 il paper è l'unica prova. Ogni mattina si scaricano anche i dati sulle posizioni dei giorni nuovi
(`scarico_metrics.py`). Verdetto come le altre (sezione 3).

**Terza aggiunta, 20 ottobre 2026, ancora prima di qualunque dato della prima settimana misurata** (quella dal 26
ottobre): **M1** (`QUATTORDICESIMA.md`, `quattordicesima.py`), il modello ad alberi che impara ogni 4 settimane, solo dal
passato, come unire tutti gli ingredienti (28 indicatori, rendimenti, volatilità, funding, acquisti a mercato, volume,
legame col Bitcoin, posizioni, stato del mercato). Sul passato, dal 2022 e sempre fuori dal campione del modello: +50,9%
l'anno, Sharpe 1,35, sopra il caso (`caso_M1.json`); non passa lo Sharpe corretto (0,59 con 36 prove). Correlazione con F3
0,17 e con K1 0,03: è quasi indipendente dalle altre. Nel paper il modello si riallena con la stessa cadenza (ogni 4
settimane dal 3 gennaio 2022). Verdetto come le altre (sezione 3).

**Quarta aggiunta, 20 ottobre 2026, ancora prima della prima settimana misurata**: **F3 + M1 a rischio uguale**
(`QUINDICESIMA.md`): il capitale diviso fra le due in parti inversamente proporzionali alla volatilità delle 26 settimane
prima. Sul passato dal 2022: +44,8% l'anno, Sharpe 1,69, positiva in ogni anno; non passa lo Sharpe corretto (0,76 con 37
prove). Verdetto come le altre (sezione 3).

## 2. Come

* Ogni mattina (con l'aggiornamento della prova in avanti del programma 5) si scaricano le candele giornaliere nuove di
  tutti i perpetui e l'indice del premio orario del mese in corso; si ricostruisce la tabella; si ricalcolano le tre regole
  **con lo stesso codice**; si tengono i giorni (A1) e le settimane (F2, C1) **dal 20 ottobre 2026** in poi: il **periodo P**.
* Il **funding** del mese in corso non è ancora nell'archivio (esce a fine mese): fino ad allora si stima dall'indice del
  premio orario con la formula di Binance (premio medio dell'intervallo più l'interesse dello 0,01% riportato entro
  ±0,05%), tre intervalli al giorno. Quando esce il file del mese si ricalcola tutto con il funding vero: il risultato che
  conta è quello col funding vero. Nel rapporto si dice quali giorni sono ancora stimati.
* Il rapporto (`PAPER.md`, `paper.json`) dice per ogni candidata: il rendimento del periodo P, settimana per settimana o
  giorno per giorno, lo Sharpe da quando è partito, il confronto col Bitcoin, e **le posizioni di adesso** (cosa terrebbe la
  regola nella settimana o nel giorno in corso).

## 3. Quando e come si giudica

* Il verdetto si dà a **52 settimane** (il lunedì 25 ottobre 2027) e a **104 settimane** (23 ottobre 2028), mai prima.
* Una candidata **passa** se il rendimento netto medio del periodo P è positivo con **p ≤ 0,025** a una coda (bootstrap a
  blocchi di 4 settimane per F2 e C1, di 20 giorni per A1), è positiva a costi doppi e il suo Sharpe nel periodo P non è
  sotto la metà di quello sul passato. Due sguardi (52 e 104 settimane) con 0,025 l'uno: la soglia d'insieme resta il 5%.
* Prima del verdetto i numeri si leggono come informazione, non come prova: con uno Sharpe vero di 1, un anno di dati dà
  un intervallo che passa lo zero quasi sempre.

## 4. Controllo della stima del funding (19 ottobre 2026, prima di usarla)

Sui tre mesi luglio-settembre 2026, dove il funding vero è nell'archivio, la stima dall'indice del premio orario (programma
5, `research/data/p5/<SIMBOLO>/premium`) dà la **stessa media** e una correlazione giorno per giorno di 0,775 (BTC), 0,683
(ETH), 0,910 (SOL), 0,846 (DOGE), 0,908 (XRP), 0,719 (LINK), su 92 giorni ciascuna. Il segnale di F2 è la somma di 7 giorni:
la stima basta fino all'arrivo del file vero.

## 5. Correzione dei dati prima della prima settimana misurata (20 ottobre 2026)

Le monete tolte dal listino restano nei file dell'archivio con il prezzo fermo e il volume zero, e il loro funding era
riempito con la media dei 90 giorni prima (`research/programma6/controllo_zombi.py`). Da oggi, **prima della prima
settimana misurata (26 ottobre)**, per tutte le candidate: funding zero nei giorni a volume zero e fuori dall'universo le
monete con volume zero la domenica. Effetto sul passato (`controllo_zombi.json`): F3 Sharpe 1,296 → 1,295, K1 1,269 →
1,262, **M1 1,35 → 0,79**. Le regole del giudizio (sezione 3) non cambiano; per M1 e per F3 + M1 il confronto «Sharpe del
periodo P non sotto la metà di quello sul passato» usa il numero sul passato con i dati corretti.

## 6. M6 come informazione (20 ottobre 2026, prima della prima settimana misurata)

La ventitreesima prova (`research/programma6/VENTITREESIMA.md`, regole scritte prima) dà a M6 (il modello di M1 con la media
dei ranghi di cinque semi) Sharpe 1,02 dal 2022 sui dati corretti, positivo in tutti gli anni, ma Sharpe corretto 0,16. Come
scritto nella sezione 3 di quelle regole, entra nel paper **come informazione accanto a M1** (non come candidata con il suo
verdetto), dalla settimana del 26 ottobre.

## 7. F5 come informazione (20 ottobre 2026, prima della prima settimana misurata)

La ventiquattresima prova (`research/programma6/VENTIQUATTRESIMA.md`, regole scritte prima) dà a F5 (il segnale di F3 con la
banda: entrata nel 20%, uscita sotto il 40%) Sharpe 1,93 dal 2021, contro 1,28 di F3 sugli stessi dati, con spese del 4,9%
invece del 7,7%; contro il caso media −0,11 e massimo 0,79 su 200 (`F5_caso.json`); Sharpe corretto 0,81 con 48 prove. Come
scritto nella sezione 4 di quelle regole, entra nel paper **come informazione accanto a F3** dalla settimana del 26 ottobre.

## 8. M7 e F5 + M7 come informazione (20 ottobre 2026, prima della prima settimana misurata)

La venticinquesima prova (`research/programma6/VENTICINQUESIMA.md`, regole scritte prima) dà dal 2022: M7 (M6 con la banda)
Sharpe 1,25 contro 1,08 di M6 sugli stessi anni; F5 + M7 a rischio uguale Sharpe 1,83 contro 1,69 di F5 da sola, volatilità
24,2%, ogni anno positivo; Sharpe corretti 0,20 e 0,65 con 50 prove. Come scritto nella sezione 4 di quelle regole, entrano
nel paper **come informazione** dalla settimana del 26 ottobre.
