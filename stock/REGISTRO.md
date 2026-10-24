# Il registro delle prove sulle azioni

Come `research/REGISTRO.md` per le crypto: si guarda prima di ogni idea nuova, ogni prova ha la sua riga **prima** del calcolo (con
il file delle regole) e il risultato dopo; il conto delle prove serve all'asticella (lo Sharpe corretto per i tentativi).

## 1. Le prove

| # | Idea (file delle regole) | Prove | Risultato | Esito |
|---|---|---|---|---|
| 1 | L'ultima mezz'ora segue il resto della giornata, SPY e QQQ (`prove/P001_ultima_mezzora.md`, scritto il 24 ott 2026 prima del calcolo) | 2 | Sharpe annuo con i costi SPY −0,60, QQQ −0,30 (comprare e tenere lo SPY 0,87); senza costi 0,31 e 0,67; trimestri in guadagno 28% e 38% (`prove/P001_risultati.md`) | **bocciata** su tutti e due |
| 2 | Uscita dalla «zona di rumore» dell'apertura, SPY e QQQ (`prove/P002_zona_di_rumore.md`, scritto il 24 ott 2026 prima del calcolo) | 2 | Sharpe annuo con i costi SPY 0,41, QQQ 1,05 (tenere SPY 0,87, tenere QQQ 0,92); Sharpe corretto 0,77 e 1,00; costi doppi −0,19 e 0,48; trimestri in guadagno 53% e 78% (`prove/P002_risultati.md`) | SPY **bocciata**; QQQ passa la ricerca e la revisione (`prove/REVISIONE_P002.md`), poi **bocciata nel periodo chiuso** (2025-01-02 → 2026-09-30: Sharpe con i costi 0,64 contro 1,09 del tenere QQQ e 1,04 del tenere lo SPY; +10,1% con i costi; 6 trimestri su 7 in guadagno; `prove/P002_chiuso.md`) |

| 3 | Il rimbalzo dopo le cadute della settimana, le 10 azioni di allora, i 3 peggiori comprati ogni settimana (`prove/P003_rimbalzo.md`, scritto il 24 ott 2026 prima del calcolo) | 1 | (in corso) | (in corso) |
| 4 | Tenere solo di notte, SPY e QQQ (`prove/P004_notte.md`, scritto il 24 ott 2026 prima del calcolo) | 2 | Sharpe con i costi SPY 0,54, QQQ 0,60 (tenere 0,87 e 0,92); senza costi 0,90 e 0,98; trimestri in guadagno 75%; costi pagati circa 45'000 e 60'000 dollari su 100'000 (`prove/P004_risultati.md`) | **bocciata** su tutti e due |
Totale nel conto: **8** (le 7 prove più l'apertura del periodo chiuso per la prova 2 su QQQ, che conta come una prova: decisione del 24 ottobre).

## 2. Idee in coda

Scritte il 24 ottobre 2026, prima di qualsiasi calcolo (`METODO.md`, sezione 6). Ogni idea o si prova o si scrive qui perché no.
L'ordine dice da dove partire: prima le idee con molte operazioni (più prove statistiche) e i dati che avremo per primi.

| # | Idea | Perché dovrebbe funzionare (fonte) | Titoli, durata | Priorità |
|---|---|---|---|---|
| I1 | **L'ultima mezz'ora segue il resto della giornata** sull'indice (**provata: prova 1, bocciata**) | Chi vende opzioni e i fondi a leva devono comprare quando il prezzo sale e vendere quando scende, soprattutto verso la chiusura: Gao, Han, Li, Zhou, «Market intraday momentum», Journal of Financial Economics 129 (2018); Baltussen, Da, Lammers, Martens, «Hedging demand and market intraday momentum», Journal of Financial Economics 142 (2021). Sospetto: l'effetto spiega poco (circa il 2% dei movimenti nel lavoro del 2018) e gli studi non contano i costi | SPY, QQQ; in giornata | 1 |
| I2 | **Uscita dalla «zona di rumore»** dell'apertura, con stop che segue il prezzo (**provata: prova 2, bocciata; QQQ bocciata nel periodo chiuso**) | Un movimento che esce dalla fascia normale dei giorni precedenti indica uno squilibrio fra domanda e offerta che dura nella giornata: Zarattini, Aziz, Barbon, «Beat the Market: An Effective Intraday Momentum Strategy for S&P500 ETF (SPY)», Swiss Finance Institute 24-97 (2024). Sospetto alto: dichiarano Sharpe 1,33 dal 2007, è un lavoro recente, molto diffuso e non ancora pubblicato su rivista | SPY, QQQ, poi le 10 azioni; in giornata | 1 |
| I3 | **Ritorno dopo le forti cadute** di pochi giorni (**prova 3**) | Chi compra dopo una vendita forzata viene pagato per dare liquidità: Nagel, «Evaporating liquidity», Review of Financial Studies (2012) (da verificare la pagina) | le 10 azioni; da 1 a 10 giorni | 2 |
| I4 | **Notte contro giorno** (**provata: prova 4, bocciata**): tenere solo da chiusura ad apertura (o il contrario) | Il guadagno delle azioni arriva quasi tutto di notte, con clienti diversi di notte e di giorno: Lou, Polk, Skouras, «A tug of war: overnight versus intraday expected returns», Journal of Financial Economics 134 (2019). Sospetto: due operazioni al giorno, i costi possono mangiare tutto | SPY, QQQ, le 10 azioni; una notte | 2 |
| I5 | **Seguire la tendenza dell'indice** (dentro sopra la media lunga, fuori sotto) | Effetto studiato su molti mercati: Moskowitz, Ooi, Pedersen, «Time series momentum», Journal of Financial Economics (2012). Sospetto: di solito riduce le perdite più che aumentare il guadagno; poche operazioni | SPY, QQQ; settimane | 3 |
| I6 | **Deriva dopo i bilanci** | Martineau, «Rest in peace post-earnings announcement drift», Critical Finance Review 11 (2022): nelle grandi aziende non c'è più dal 2006 circa; due lavori del 2025 dicono il contrario. Si prova solo per ultima, perché sulle grandi aziende è probabilmente sparita | le 10 azioni; giorni | 4 |
| I7 | **Effetti del calendario** (inizio del mese, giorni prima delle riunioni della banca centrale americana) | Pochi eventi l'anno, quindi poca forza statistica; sulle crypto il «giorno migliore del mese» non reggeva | SPY; giorni | 4 |
| I8 | **L'ultima mezz'ora con costi più bassi**: uscita con l'ordine all'asta di chiusura invece che a mercato, ingresso a ordine limite | La prova 1 ha un vantaggio prima dei costi (circa 0,5 punti base al giorno sullo SPY) ma paga circa 1,7 punti base a operazione. Sospetto alto: è una variante di un'idea bocciata, e anche senza lo slittamento i costi (circa 0,7 punti base) superano il vantaggio. Va contata come prova nuova | SPY, QQQ; in giornata | 3 |
| I9 | **Tenere solo di notte con gli ordini d'asta** (chiusura e apertura, senza scarto) | Prova 4: senza costi lo Sharpe è 0,90-0,98, vicino al tenere sempre; i costi (circa 2 punti base al giorno) lo portano a 0,54-0,60. Con gli ordini d'asta resta la commissione (circa 0,3 punti base a giro). Sospetto: variante di un'idea bocciata, e anche senza costi non batte di molto il tenere sempre: al massimo pareggia | SPY, QQQ; una notte | 4 |
