# Prova 149 — la 1:1:1: una moneta, un intervallo, una strategia (idea 136)

Regole scritte l'11 novembre 2026, **prima di ogni calcolo**, dalla sessione principale; la prova la esegue strategy-researcher,
il giudizio su ciò che passa lo dà backtest-auditor. Idea del proprietario (8 novembre: «una nuova strategia regola 1:1:1 (1 crypto,
1 timeframe e 1 strategia)»), approvata nella forma: intervalli lunghi, monete grandi, un filtro veloce sul passato, poi in avanti
nel paper con l'elenco e il criterio scritti prima. Perché intervalli lunghi: a ottobre la ricerca per moneta aveva guardato
soprattutto da 15 minuti a un'ora, dove gli effetti valevano meno del costo di un giro (`docs/storia/05_ricerca_per_moneta_e_gruppo.md`).

## Le monete
Le 10 monete con il volume medio giornaliero in USDT più alto sui perpetui di Binance **nell'anno 2023** (scelte con dati vecchi, per
non scegliere chi è andato bene dopo), esclusi gli stablecoin e i contratti che non sono monete. L'elenco si scrive nel risultato
prima di calcolare le strategie.

## Gli intervalli
4 ore e 1 giorno (candele del perpetuo di Binance, ora UTC).

## Le strategie (tre, con i parametri fissi: nessuna ricerca dei parametri)
* **A, tendenza**: sempre in posizione; comprato se la chiusura è sopra la media semplice delle ultime 50 chiusure, venduto se sotto.
* **B, rottura**: comprato quando la chiusura supera il massimo delle 20 barre prima, venduto quando scende sotto il minimo delle 20
  barre prima; si esce dal comprato sotto il minimo delle 10 barre prima e dal venduto sopra il massimo delle 10 barre prima; fuori
  mercato altrimenti.
* **C, ritorno alla media**: comprato quando l'RSI a 14 barre scende sotto 30, chiuso quando torna sopra 50; venduto quando sale sopra
  70, chiuso quando torna sotto 50.

## L'esecuzione e i costi
* Il segnale si calcola alla chiusura di una barra; l'ordine si esegue all'apertura della barra dopo (nessuno sguardo nel futuro).
* Una posizione vale il capitale (leva 1); i rendimenti si sommano barra per barra.
* Costi confermati dal proprietario il 7 novembre: 0,05% a mercato per ogni lato; scarto di prezzo 0,01% su BTC, ETH e SOL, 0,02%
  sulle altre; il funding vero del perpetuo per le ore in posizione.

## Il periodo e il conto delle prove
* Dal 1° gennaio 2021 al 31 ottobre 2026 (o dalla prima candela della moneta, se dopo), con il risultato di ogni anno separato.
* Le combinazioni sono 10 × 2 × 3 = **60**, e contano **tutte** nel conto delle prove (oggi 246 → 306): lo Sharpe corretto si calcola
  con il conto aggiornato, come per le altre prove (`research/programma6/finestre.py`, `sharpe_corretto`).

## L'esame (regole approvate dal proprietario il 9 novembre)
Una combinazione passa il filtro se: netto dopo i costi positivo; ogni anno positivo; t almeno 3; Sharpe corretto almeno 0,80. Chi
passa va a backtest-auditor; se l'auditor dà PASS, la sessione principale la mette nel paper in avanti, con l'elenco fisso delle
combinazioni passate. Nessuna combinazione si aggiusta dopo aver visto i risultati: una variante nuova è una prova nuova, nel conto.

## Cosa si consegna
Una tabella delle 60 combinazioni (moneta, intervallo, strategia: rendimento l'anno, Sharpe, anni positivi su totale, t, Sharpe
corretto, numero di operazioni, esito del filtro) in `RISULTATI_OTTANTASETTESIMA.md`; il codice in `ottantasettesima.py`; ogni
combinazione registrata in `research/trials/` (anche quelle che non passano).
