# Programma 7 — ottantaseiesima prova: G1 con 250 euro (voce 8 di `MIGLIORARE_G1.md`)

Scritto il 6 novembre 2026 alle 06:05 UTC, **prima di qualunque calcolo**: dei dati si sono letti solo i filtri del listino di
Binance e il cambio. Nasce dal messaggio del proprietario dello stesso giorno: «voglio partire con 250 euro».

**Questa prova non porta niente sui soldi veri.** `DRY_RUN` resta vero. Il passaggio ai soldi veri resta quello di sempre: una richiesta
esplicita, ripetuta e consapevole del proprietario, dopo che ha visto i numeri di questa prova e ha accettato lo Sharpe corretto di G1
(0,86, sotto lo 0,90 della sua regola: `docs/backlog.md` P26).

## 1. Perché

* Con poco capitale molti ordini di G1 sono **sotto il minimo di Binance**. Con 1.000 USDT è il 76% degli ordini, il 20% del giro
  (`REVISIONE_G1N.md`, sezione 5). Il paper non arrotonda niente; il conto vero sì. Il bot salta ogni ordine che resta sotto la quantità
  minima o il valore minimo (`bot/portafoglio/demo_binance.py`, `ordini_del_giorno`), **anche quando l'ordine chiude una posizione**.
* **Il capitale**: 250 euro × 1,1209 (cambio euro contro USDT su Binance, 6 novembre 2026 alle 06:00 UTC circa) = 280,2 USDT. La prova
  usa **280 USDT**. Per capire, anche 1.000 e 5.000 USDT.
* **I filtri veri del listino** (`/fapi/v1/exchangeInfo` dello stesso momento, salvati in
  `risultati_ottantaseiesima/filtri_binance_2026-11-06.json`). Sui 522 perpetui in USDT:
  * valore minimo di 5 USDT per 516 perpetui;
  * 20 USDT per ETH, BCH, LTC, ETC e LINK;
  * 50 USDT per BTC.

  Il passo della quantità conta per le monete care. Per il Bitcoin è 0,001: a 75.600 dollari fanno 75,6 USDT.

## 2. Cosa si calcola (fissato qui)

**Le basi sono quelle della revisione di G1N** (`revisione_g1n/nucleo.py`):
* stessi giorni, dal 4 gennaio 2021 al 4 ottobre 2026;
* stesso universo delle 100;
* banda 20/40 e pesi secondo l'inverso della volatilità;
* stesse spese: ordine limite all'apertura per un'ora, poi a mercato (`nucleo.spese_limite`);
* stesso funding, esposizione 2.

**Il conto vero simulato** (nuovo, `ottantaseiesima.py`):
* **Capitale fisso**: ogni giorno l'obiettivo è il peso × il capitale. Guadagni e perdite non cambiano la base. È una scelta di misura,
  così il vincolo dei minimi non sparisce perché il conto cresce.
* **La posizione** in USDT di ogni moneta segue il prezzo fra un giorno e l'altro.
* **L'ordine del giorno** è la differenza fra obiettivo e posizione, arrotondata verso zero al passo della quantità (passo di oggi × il
  prezzo di apertura del giorno).
* **Le monete che oggi non sono nel listino** (chiuse): valore minimo 5 USDT, nessun passo.
* **Senza un prezzo di apertura** non si scambia.

Le spese e i rendimenti si calcolano sugli ordini **eseguiti davvero**. Le posizioni sono quelle **tenute davvero**.

**I conti** (tutti con lo stesso simulatore):
* **G1 senza minimi**: il paper, il riferimento. Deve tornare uguale, a meno di un soffio, al conto di `nucleo.variazioni`: è il
  controllo del simulatore.
* **A, G1 come lo fa il bot oggi**: si salta ogni ordine sotto la quantità minima o sotto il valore minimo, anche quando chiude o riduce
  una posizione.
* **A2, G1 con le chiusure permesse**: un ordine che riduce o chiude una posizione (con «solo riduzione») parte se raggiunge la quantità
  minima, anche sotto il valore minimo. Binance esenta da quel minimo gli ordini «solo riduzione»: il messaggio di errore dice «Order's
  notional must be no smaller than 5 (unless you choose reduce only)». Va verificato sul demo prima di contarci. È una correzione
  dell'esecuzione, **non delle regole di G1**.
* **B, G1 con meno monete** (l'unica regola nuova). Per lato si tengono le **10 monete con il peso più grande** fra quelle che G1 sceglie,
  con i pesi riscalati al totale del lato; poi come A2. Il 10 è fissato qui, non scelto sui risultati: 280 USDT diviso 10 fa 28 USDT a
  posizione, più di cinque volte il minimo.
* **Per capire** (non contano): A e A2 con 1.000 e 5.000 USDT.

**Una variante** (B): nel conto delle prove diventano **246**. A e A2 non cambiano le regole: sono la misura di G1 con i vincoli del
conto vero.

## 3. L'esame (scritto prima)

**Le misure** sono settimanali, come nelle altre prove di G1 (`analisi.sintesi`): Sharpe, rendimento l'anno, discesa più grande, ogni
anno.

**G1 può partire con 280 USDT così com'è** se A2 rispetto a G1 senza minimi, negli stessi giorni, soddisfa tutte e tre:
* ha lo Sharpe di almeno il **90%**;
* ha una discesa peggiore **al massimo di 5 punti**;
* ha **ogni anno positivo**.

Se A2 soddisfa le tre, serve anche la correzione del bot per le chiusure. Se le soddisfa anche A, non serve nemmeno quella.

**Se A2 non le soddisfa** si guarda B, con le stesse tre condizioni. B cambia le regole, quindi si giudica come G1 (backlog P26):
* va nel paper e sul demo, se il proprietario la accetta;
* prima, un revisore separato.

**Se non le soddisfa nessuna delle due**, G1 con 250 euro non segue il paper: lo si dice, con il capitale da cui invece lo segue (da A
e A2 con 1.000 e 5.000 USDT).

**Si riportano anche**:
* quanta parte dell'esposizione di G1 il conto tiene davvero;
* l'oscillazione della differenza giornaliera con G1 senza minimi;
* gli ordini al giorno;
* le posizioni rimaste sotto il minimo che non si chiudono;
* le spese.

## 4. Cosa questa prova non vede

* **I filtri del passato.** Si usano quelli di oggi: il minimo di 50 USDT del Bitcoin e i passi non erano gli stessi nel 2021-2024. Per
  partire adesso contano quelli di oggi.
* **Gli ordini veri.** Gli ordini limite e il funding sono quelli del modello di G1. Il demo li ha confermati con 5.000 USDT
  (`MIGLIORARE_G1.md`, voci 1-3), non con 280.
* **Le operazioni a eventi** (short la moneta e long il Bitcoin al 5% del conto). Con 280 USDT il 5% è 14 USDT, sotto il minimo del
  Bitcoin: con 250 euro non si possono fare. Qui non si provano.
