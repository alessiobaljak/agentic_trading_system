# Prova 161 — il funding coperto su Bitcoin ed Ether con il margine vero (la prova 157 rifatta)

Regole scritte il 15 novembre 2026 dalla sessione principale, su richiesta del proprietario («rifai la prova del funding coperto con il
margine giusto»), **prima di ogni calcolo di questa prova**. È la prova 157 (`NOVANTACINQUESIMA.md`) rifatta dopo il FAIL di
backtest-auditor (`audits/reports/2026-11-15-PROVA157.md`, problema 1: il margine del perpetuo non era modellato). Il numero 160 è
riservato alla miscela con G1 (`NOVANTOTTESIMA.md`), che userà le serie di questa prova.

## Avviso onesto: la prova non è del tutto alla cieca
La revisione ha già calcolato, solo per capire, una regola di margine (sotto un terzo del nozionale si riporta a metà) e due sue varianti
(leva 2,5 e 4): +7,1-7,7% l'anno, nessuna liquidazione, ogni anno positivo. Quindi sappiamo già che la soglia cambia poco. Per non
sceglierla sui risultati, **la soglia qui viene dai rialzi peggiori visti, non dai rendimenti**: il margine deve reggere due giorni del
rialzo peggiore del periodo (sezione 3). Tutto il resto resta come nella 157: stesse monete, stessi N, stessi costi.

## 1. Cosa resta uguale alla prova 157
Bitcoin ed Ether, metà del capitale ciascuno, ognuno per conto suo; si compra a pronti e si vende il perpetuo della stessa quantità; dentro se
la media del funding degli ultimi N giorni è sopra zero, fuori altrimenti (A: N = 30, B: N = 90); il segnale del giorno D−1 si esegue
all'apertura di D; dal 4 gennaio 2021 al 4 ottobre 2026 (uscita all'apertura del 5 ottobre); costi del programma 7 (perpetuo 0,05% a
mercato più lo scarto 0,01%) e a pronti 0,15% per lato; nessun interesse sui contanti; i prezzi a pronti già scaricati con le impronte
(`risultati_novantacinquesima/impronte_pronti.json`). Le letture chiuse dopo la verifica della 157 valgono anche qui, salvo dove questa
pagina le cambia.

## 2. Due portafogli, come su Binance
* **Pronti**: la quantità Q della moneta. Non fa da margine per il perpetuo.
* **Future**: il margine in USDT. Si muove con la perdita o il guadagno del perpetuo venduto (al prezzo mark), con il funding incassato o
  pagato **a ogni regolamento** (00, 08 e 16 UTC) sul valore Q × prezzo mark di quell'ora, con le commissioni del perpetuo e con le perdite
  già chiuse quando il perpetuo si riduce. Il margine vero di un giorno è tutto questo, non solo la perdita aperta della parte rimasta.
* Prezzo mark: le candele orarie del prezzo mark dell'archivio di Binance; dove mancano, il prezzo scambiato (più severo, come nella
  revisione).

## 3. La regola del margine (fissata qui)
* **Il rialzo peggiore del periodo** (dato misurato nella revisione, non un rendimento): in una giornata Bitcoin +36,2% (26 luglio 2021),
  Ether +27,6%; in due giorni +40,7% e +37,4%. Il margine deve reggere due giorni del rialzo peggiore senza che nessuno lo rifornisca,
  perché il bot controlla una volta al giorno e un giorno può saltare.
* **Ingresso**: margine = **60% del valore del perpetuo**; il capitale della moneta è quindi Q × prezzo × 1,6 (pronti più margine).
* **Ogni giorno all'apertura (00:00 UTC)**, con il margine vero: se è **sotto il 45% del valore del perpetuo** (sotto i due giorni peggiori
  più il margine di mantenimento), si vende a pronti quanto serve, lo si trasferisce nei future e si riduce il perpetuo della stessa
  quantità, fino a riportare il margine al **60%**. Costi: 0,15% sul pronti venduto e 0,06% sul perpetuo ridotto. Q cala e lo si scrive.
* Se il margine è sopra il 60% (il perpetuo ha guadagnato), non si fa niente: i contanti in più restano nei future, senza interesse.
* Il limite fisso della leva (5, `bot/risk/hard_limits.py`) chiede un margine di almeno il 20%: il 45% lo rispetta sempre.

## 4. La liquidazione (si modella, non si esclude)
* Dentro la giornata, con il massimo orario del prezzo mark: se il margine vero scende sotto il **mantenimento dello 0,5%** del valore
  del perpetuo (valore da verificare, scritto come tale), il perpetuo è liquidato: il margine rimasto è perso, il pronti resta scoperto
  fino all'apertura dopo, poi si ricopre da capo con il capitale rimasto, pagando i costi d'ingresso, se il segnale è dentro.
* Si contano le liquidazioni; l'esame chiede che non ce ne siano (sezione 6).

## 5. Il capitale e i conti
* Il conto della moneta in USDT: valore del pronti + margine dei future. Rendimento giornaliero sul capitale della moneta, composto; la
  strategia è la media delle due monete (metà del capitale ciascuna, riequilibrate solo quando una delle due rientra).
* All'uscita si chiude tutto (pronti e perpetuo) con le spese; al rientro Q si ricalcola dal capitale della moneta di quel giorno.
* **Controllo descrittivo a 1.000 USDT**: con i passi e i minimi veri delle quantità di Binance (exchangeInfo pubblico di oggi), quanto
  cambia il risultato; e sotto quale capitale la gamba del Bitcoin non si apre.

## 6. L'esame
Le quattro condizioni approvate, e solo quelle: netto positivo; ogni anno di calendario positivo (2021 e 2026 parziali contano); t almeno 3
(Sharpe settimanale per la radice di settimane/52); Sharpe corretto almeno 0,80 con `corretto_famiglie` di `research/programma6/asticella.py`
e il mazzo completo, serie «161 A» e «161 B» insieme. **In più, per i soldi veri: nessuna liquidazione.** Conto delle prove da 326 a 328.
Controlli descrittivi: discesa massima, mesi positivi, ogni anno con la parte di funding, base, spese e rifornimenti del margine; quante
volte si rifornisce il margine; il guadagno dal 2022 da solo; la correlazione con G1 e con la 157; **i rischi che la prova non misura**
(borsa unica, USDT, chiusura forzata delle posizioni in guadagno nei crolli, il tasso di base del funding che Binance può cambiare, il bot
che oggi non ha una gamba a pronti né i trasferimenti fra portafogli).

## 7. Cosa si consegna
`RISULTATI_NOVANTANOVESIMA.md`, `novantanovesima.py`, `risultati_novantanovesima/` con `settimane_A.csv.gz` e `settimane_B.csv.gz`
(colonna `netto`, indice il lunedì in giorni dall'epoca) e i giorni, il registro delle varianti `research/trials/novantanovesima.csv`. Si
riusano i caricatori e i prezzi a pronti della 157; il codice della 157 non si modifica.

## Testo della riga del registro
| 161 | CM: il funding coperto su Bitcoin ed Ether con il margine vero (la 157 rifatta dopo il FAIL di backtest-auditor): due portafogli come su Binance, margine al 60% del perpetuo, rifornito a pronti all'apertura quando scende sotto il 45% (due giorni del rialzo peggiore visto), liquidazione modellata con il massimo orario del prezzo mark; N = 30 (A) e 90 (B); esame + nessuna liquidazione (`programma7/NOVANTANOVESIMA.md`); richiesta del proprietario del 15 novembre; non alla cieca (la revisione ha già misurato soglie simili) | 2 | in corso | in corso |

## Regole corrette il 15 novembre 2026 dopo la verifica, prima di ogni calcolo (sessione principale)
La verifica di strategy-researcher (`VERIFICA_NOVANTANOVESIMA.md`) ha trovato ambiguità; nessun numero è stato calcolato (solo lo scarico
del prezzo mark e del prezzo scambiato orari, `novantanovesima_dati.py`, impronte e buchi in `risultati_novantanovesima/impronte_mark.json`:
il mark manca per 216 ore su BTC e 72 su ETH, il prezzo scambiato non ha buchi). Valgono le letture proposte nella verifica:
1. **Il patrimonio (A1)**: la strategia è il patrimonio totale composto (non la media dei rendimenti delle due monete); le settimane si
   compongono dai giorni. Al rientro una moneta riparte da metà del patrimonio totale solo se l'altra è fuori; se l'altra è dentro, riparte
   dal proprio conto.
2. **Il prezzo del conto dei future (A2)**: l'apertura oraria del prezzo mark delle 00:00 UTC (dove manca, il prezzo scambiato).
3. **L'ingresso (A3)**: Q = capitale / (S × 1,0015 + 0,6 × M), con la commissione del perpetuo presa dal margine.
4. **La quantità da vendere (A5)**: x = (0,6 × Q × M − MB) / (S × 0,9985 − 0,0006 × M + 0,6 × M), così che dopo la riduzione il margine è
   esattamente il 60%.
5. **L'ordine all'apertura (A4, A6)**: regolamento delle 00:00, controllo della liquidazione, uscita, riduzione. Con la liquidazione si
   perde tutto il margine, si vende il pronti e si rientra da capo con le spese d'ingresso.
6. **I passi delle quantità a 1.000 USDT (A7)**: dal file dei filtri del repository (`bot/portafoglio/filtri_conto_vero.json`), dichiarato
   come tale; la soglia di capitale per la gamba del Bitcoin al prezzo del 4 ottobre 2026 e al massimo del periodo.
