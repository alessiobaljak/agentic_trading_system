# Programma 6 — cinquantaquattresima prova: lo scalping sul serio (Z1-Z4)

Scritto il 22 ottobre 2026, sera, **prima di qualunque calcolo**, su richiesta del proprietario: «approfondisci davvero lo
scalping [...] seguivo su un canale Telegram una persona che apriva max 5 posizioni al giorno [...] win rate quasi del 100%,
tutte almeno prendevo il TP1 [...] non darti per vinto».

## 1. Perché, e cosa c'è già

Lo scalping guadagna poco a operazione, quindi decidono i costi: con gli ordini a mercato un giro costa 0,12-0,14%, con gli
ordini limite 0,04%. Finora: lo «scalping sulla volatilità» del 18 ottobre (`research/scalping/`: dopo un'esplosione il prezzo
non sa dove andare), le reti con gli ordini limite del programma 5 (I-020, bruciate), gli indicatori a 4 ore (prove 34-39) e le
strategie di TradingView a 4 ore (prova 46). **Mai** provati: gli schemi classici dello scalping a 5 e 15 minuti con **entrate e
prese di profitto a ordine limite** (commissione 0,02%) e la scala di prese di profitto che il proprietario descrive. Uno dei
quattro schemi è proprio quello: alta quota di operazioni vinte per costruzione (primo obiettivo vicino, stop lontano). La prova
misura se, oltre a vincere spesso, **guadagna**.

## 2. Dati, costi, esecuzione (uguali per tutti gli schemi)

* **Monete**: ogni mese le **30** più scambiate (mediana del volume giornaliero dei 30 giorni prima) fra le 100 con le candele a
  1 minuto (`research/data/p5`). **Periodo**: dal 1 gennaio 2024 al 15 ottobre 2026.
* **Candele**: a 1 minuto per l'esecuzione; a 5 e 15 minuti (costruite dalle 1 minuto) per i segnali; segnale alla chiusura
  della candela, niente dati futuri.
* **Ordine limite** (entrate dove indicato e prese di profitto): eseguito solo se il prezzo **passa oltre** il livello in una
  candela da 1 minuto (minimo sotto per chi compra, massimo sopra per chi vende), al livello; commissione **0,02%**.
* **Stop e uscite a tempo**: a mercato, commissione **0,05%** più lo scarto (0,01% BTC, ETH, SOL; 0,02% le altre), al livello o
  all'apertura del minuto se il prezzo ci salta oltre. Se nello stesso minuto si toccano stop e obiettivo, vale lo **stop**.
* **Funding**: si paga o si incassa se la posizione attraversa un regolamento (00, 08, 16 UTC), con il tasso vero.
* **Dimensione**: ogni operazione rischia l'**1%** del capitale fra entrata e stop; al massimo 5 aperte insieme, una per moneta.

## 3. I quattro schemi (valori fissati qui)

* **Z1 — lo stile del canale.** Candele da 15 minuti. Tendenza: media esponenziale 50 sopra la 200 → solo long (sotto → solo
  short). Entrata: la chiusura torna sotto (sopra, per lo short) la media esponenziale 20 → **ordine limite** alla chiusura,
  valido 1 ora. Obiettivi a limite: **TP1 +0,6%** (un terzo), **TP2 +1,2%** (un terzo), **TP3 +2,0%** (un terzo); **stop −1,5%**;
  dopo il TP1 lo stop va al prezzo d'entrata. Al massimo **24 ore**. Al massimo **5 operazioni al giorno** in tutto (le prime 5
  dei segnali del giorno UTC).
* **Z2 — ritorno alla VWAP.** Candele da 5 minuti. VWAP del giorno UTC dalle 00:00 e deviazione dello scarto prezzo − VWAP
  dall'inizio del giorno (almeno 24 candele). Chiusura sotto VWAP − 2 deviazioni → **limite** alla chiusura per comprare
  (sopra +2 → vendere), valido 15 minuti; obiettivo a limite alla VWAP del momento dell'entrata; stop alla stessa distanza
  dall'altra parte; al massimo 2 ore.
* **Z3 — rottura della prima ora americana.** Il massimo e il minimo dalle 13:30 alle 14:30 UTC (candele da 1 minuto); dopo le
  14:30 la prima chiusura a 5 minuti sopra il massimo (sotto il minimo) → **a mercato** all'apertura dopo; stop a metà del
  range; TP1 a +1 range (metà), TP2 a +2 range (metà), a limite; dopo il TP1 stop all'entrata; uscita alle 20:00 UTC. Una per
  moneta al giorno.
* **Z4 — la spinta del volume.** Candela da 1 minuto con volume oltre **10 volte** la mediana dei 60 minuti prima, rendimento
  oltre **+0,5%** (sotto −0,5%) e acquisti a mercato oltre il **70%** del volume (sotto il 30%) → **a mercato** nel verso della
  spinta all'apertura del minuto dopo; obiettivo a limite **+1%**, stop **−0,5%**, al massimo 30 minuti.

### 3bis. Aggiunta del 22 ottobre, sera, prima di qualunque risultato

Il proprietario: «puoi anche farne più di 5, quello era solo un'idea». Si aggiunge **Z1b**: identico a Z1 **senza il limite
di 5 operazioni al giorno** (restano al massimo 5 aperte insieme, una per moneta). Gli schemi diventano cinque.

## 4. L'esame (per ogni schema)

* **Per operazione**: media netta in multipli del rischio sopra zero con **p ≤ 0,002** (0,01 diviso i 5 schemi; bootstrap sui
  giorni), positiva nelle due metà e senza i 5 giorni migliori.
* **Come portafoglio** (rendimento giornaliero con l'1% di rischio a operazione): `terza.esito` su settimane con lo Sharpe
  corretto rivisto (`asticella.py`), soglia 0,95. Cinque prove: nel conto diventano **117**.
* Si riportano anche, per capire la differenza fra «vincere spesso» e «guadagnare»: la quota di operazioni vinte, la quota che
  arriva almeno al TP1, il guadagno medio delle vinte e la perdita media delle perse, i costi, per anno.
