# G1 sul demo a 1.000 USDT: funding e commissioni (8-11 novembre 2026)

Due misure chieste dalla revisione di G1 (`audits/reports/2026-11-12-G1_CONTO_VERO.md`, problemi 1 e 4). Soglie non approvate: solo misure, nessun verdetto.

## Riepilogo e verdetto
- Verdetto: nessuno (soglie non approvate da Alessio).
- Funding: il demo ha incassato +0,828% in 4 giorni contro +1,181% del paper (differenza 0,353 punti, il demo fa il 70% del paper). La differenza cresce: 0,019 / 0,033 / 0,146 / 0,155 punti al giorno. Nessuna causa è dimostrata per intero. Dimostrati: l'allineamento dei giorni e delle basi; il 9 novembre quasi tutta la differenza (0,032 su 0,033) sta nel regolamento delle 00:00; il 10 e l'11 la differenza non può stare solo nel regolamento delle 00:00. Solo probabili: le monete assenti sul demo (se avevano funding estremo); i tassi del demo diversi (contro: 08:00 e 16:00 del 9 novembre combaciano).
- Commissioni: 0,89 USDT in 4 giorni (0,089% dell'equity). La quota di ordini a mercato NON è stimabile in modo affidabile: l'8 novembre la commissione media implicita è 0,037-0,039% del valore (a metà fra 0,02% e 0,05%), ma il valore scambiato non è nei dati; dal 9 all'11 manca del tutto.

## Oggetto
G1 sul demo (`bot/portafoglio/demo_binance.py`) contro G1 del paper (`bot/portafoglio/f5.py`), 8-11 novembre 2026 (4 giorni interi, conto ridotto a 1.000 USDT). Fonti: `ops/results/0720..0735` (sezioni «G1 sul conto demo di Binance», «G1: il demo contro il paper, giorno per giorno», tabella «Funding e spese veri»); codice dei due motori. Commit/regole: nessun cambio ai pesi dal confronto del 9 novembre (non riverificato in questo giro).

## Limiti del confronto
- Il demo di Binance non ha i prezzi, la liquidità e (forse) i tassi di funding del mercato vero: ogni numero sul demo vale per il demo.
- Da questa macchina Binance non risponde (errore «Service unavailable from a restricted location»): non ho potuto leggere i tassi di funding del mercato vero né del demo.
- `research/data/` non è leggibile e il pannello `p6g_pannello.pkl` arriva al 7 novembre con il funding dopo il 31 ottobre riempito, non vero: la ricerca non può ricalcolare il funding dell'8-11 novembre. Le candele a 1 ora non danno il funding. Quindi niente ricalcolo di ricerca in questo giro.
- Quattro giorni sono pochi; le percentuali delle tabelle hanno tre decimali (±0,0005 punti, cioè ±0,005 USDT al giorno sul demo).
- Dati per moneta, per regolamento e per esecuzione NON sono nelle risposte della macchina: da qui i limiti sotto.

## Confronto (funding, % dell'equity del giorno; fonte 0735)
| giorno | demo | paper | paper meno demo | demo/paper |
|---|---|---|---|---|
| 8 nov | +0,155 | +0,174 | 0,019 | 0,89 |
| 9 nov | +0,198 | +0,231 | 0,033 | 0,86 |
| 10 nov | +0,272 | +0,418 | 0,146 | 0,65 |
| 11 nov | +0,203 | +0,358 | 0,155 | 0,57 |
| somma | +0,828 | +1,181 | 0,353 | 0,70 |
In USDT sul demo (percentuale per equity di fine giorno 995,2 / 1.004,0 / 1.002,7 / 990,1): 1,54 + 1,99 + 2,73 + 2,01 = 8,27. Il totale scritto dal rapporto (5 giorni dal 7 novembre) è 8,64: il 7 novembre (conto a 280) vale quindi circa 0,37 USDT (circa +0,13% su 280, come il paper +0,112%).

## 1. Funding: cosa è dimostrato
D1. **Stessa etichetta del giorno**. Paper: `_funding_regolati` (f5.py:546) somma i regolamenti dopo l'ultimo controllo e al ribilancio delle 00:09 usa ancora le quantità vecchie; il diario del giorno è la differenza fra due scritture, quindi il giorno D contiene i regolamenti 00:00, 08:00, 16:00 di D. Demo: `entrate_del_conto` (demo_binance.py:345) legge `/fapi/v1/income` dalle 00:00 alle 23:59 del giorno: stessi tre regolamenti, con le posizioni del giorno prima alle 00:00. Lo scarto di ora non c'è (a parte il 8 novembre, dove il demo è ripartito da zero alle 00:18 e le posizioni sono finite entro le 04:18).
D2. **Stessa base**: entrambe in % dell'equity del proprio conto (demo ridotto ~1.000, paper ~10.400): lo scarto non nasce dalla scala.
D3. **9 novembre: la differenza è tutta alle 00:00.** Il rapporto 0729 (9 nov 06:25 UTC, quindi solo il regolamento delle 00:00): demo +0,049%, paper +0,081% (differenza 0,032). A fine giorno: demo +0,198%, paper +0,231%. Quindi alle 08:00 e 16:00 insieme: demo 0,149, paper 0,150 (stessa cosa entro 0,001). Conseguenza: in quel giorno i tassi del demo, su quelle posizioni, rendono come il mercato (argomento contro la causa «tassi diversi», limitato a un giorno e ai tre regolamenti insieme).
D4. **10 e 11 novembre: non può essere solo la 00:00.** Il paper alle 00:00 incassa solo 0,055% (10 nov, rapporto 0731) e 0,044% (11 nov, rapporto 0733), mentre la differenza è 0,146 e 0,155: almeno 0,091 e 0,111 punti stanno nei regolamenti 08:00/16:00, cioè su posizioni scelte dopo il ribilancio delle 00:18 (demo con il 9-10% del conto in variazioni sotto il minimo).
D5. **Monete assenti** (rapporti 0720-0735): ICPUSDT (peso paper -3,96% il 6 nov; scarto vero +4,2/+4,8% fino al 10 nov, poi non più elencata), 龙虾USDT (rifiutata ogni giorno, peso -1,41% il 6 nov, -1,86% il 12 nov), IRYSUSDT (dal 9 nov, +0,42%). Esposizione assente ≈ 6-7% del conto l'8-10 nov, ≈ 2,4% dall'11 (più ICP alle 00:00 dell'11, che ha ancora le posizioni del 10). La loro perdita di funding = peso × tasso, quindi per spiegare da sole 0,146 il 10 nov servirebbe un tasso medio di circa 2,2% al giorno (0,7% a regolamento) su quel 6,7%; l'11 nov, con 2,4% fuori, circa 6% al giorno (2% a regolamento: il tetto tipico, non verificato qui). I tassi normali sono 0,01% a regolamento. Le monete assenti sono scelte proprio perché hanno funding estremo (short sui più alti), quindi NON si esclude per il 10 nov; per l'11 serve che 龙虾 stia al tetto: improbabile ma non escluso. **Da confermare con i tassi veri di queste tre monete.**
D6. **Variazioni sotto il minimo / scarto di posizione** (scarto totale 8,9 / 13,7 / 13,9 / 15,8% del conto, di cui ICP ~4,5% e 龙虾 ~2%): il resto, ~11% al massimo, anche se fosse tutto esposizione persa al funding medio del paper (0,418%/2 = 0,21% per unità e per giorno il 10 nov) varrebbe al massimo ~0,023 punti: non basta, salvo che le monete interessate abbiano funding oltre 6 volte la media. Stima con ipotesi, non misura.
D7. **Ora dei regolamenti**: nessuno scarto (D1). **Capitale diverso**: solo via minimi/arrotondamenti (D6).
Non dimostrabili: tassi del demo diversi da quelli del mercato (D3 è un indizio contrario, non una prova); quota di D5 e D6 sulla differenza; l'effetto dei regolamenti a 1 o 4 ore (le monete nuove possono averli: il paper li somma tutti dalla storia dei tassi, il demo li incassa; nessuna differenza attesa, ma non verificato).

## 2. Commissioni
Dati (0735 e precedenti): demo in % dell'equity: 0,074 / 0,008 / 0,004 / 0,003 → 0,736 / 0,080 / 0,040 / 0,030 USDT = 0,886 (il totale scritto 0,89 include il 7 novembre a ~0,00). Ordini: 8 nov 48 (45 a limite, 3 a mercato), 9 nov 19 (16, 2, 1 rifiutato), 10 nov 8 a limite, 11 nov 7 a limite (contatori cumulativi 531/560 → 607/642). Per conteggio: 76 a limite su 82 (93%).
- **8 nov (partenza da zero)**: valore scambiato stimato = esposizione di G1 (2 volte il conto) meno monete assenti (≈57 USDT) e minimi (≈8) ≈ 1.900-2.000 USDT. Commissione media implicita = 0,736/1.935 = 0,038% (0,037-0,039). Con solo 0,02% e 0,05%, vuol dire ~60% del valore a mercato (57-63%), contro il 6% degli ordini per conteggio. Per tornare al 6% servirebbe un valore scambiato di ~3.400 USDT (1,7 volte l'esposizione).
- **Perché non basta**: (a) l'ordine «a limite» è un limite GTC al prezzo di mark (demo_binance.py:283, 1332), non post-only: se il mercato lo attraversa, si esegue subito come ordine a mercato e paga 0,05%, ma conta come «a limite»; (b) il valore scambiato non è registrato; (c) la commissione vera del conto demo non è mai stata letta (le 0,02%/0,05% sono nel paper, f5.py:51; il codice del demo legge solo il totale); (d) il primo giorno del 24 ottobre (0,043% su ~5.000, MIGLIORARE_G1.md) darebbe 0,0215% se il valore fosse 2 volte il conto, quindi quasi tutto a limite, ma quel giorno ci furono più riavvii: indizio debole.
- **9-11 nov**: stimabile solo come intervallo: se tutto a limite il valore è 400 / 200 / 150 USDT (40 / 20 / 15% del conto); se tutto a mercato 160 / 80 / 60. Il paper, senza minimi, spende 0,010 / 0,004 / 0,007% con costi quasi tutti a limite: demo e paper hanno lo stesso ordine di grandezza (rapporto 0,8 / 1,0 / 0,4), coerente con il demo che scambia meno per i minimi, ma niente di più.
- **Affidabilità**: bassa sull'8 novembre (il risultato dipende dal valore scambiato, che non è nei dati: fra 1.900 e 3.400 USDT la quota a mercato va da 60% a 6%), nulla dal 9 all'11. Il confronto con la ricerca (0,02% a limite, 0,05% a mercato): la commissione media 0,038% del 8 novembre è sopra 0,02% ma dentro la coppia assunta; i costi osservati NON superano ancora quelli assunti in modo dimostrabile (su 4 giorni 0,089% dell'equity, circa 8% annuo se fosse costante: ma il giorno di partenza pesa 83% del totale, il regime è 0,004-0,008% al giorno, circa 1,5-3% annuo; ricerca: 6,5% annuo con spread, MIGLIORARE_G1.md).

## Decisioni per Alessio
Nessuna su soglie in questo giro. Resta: approvare le soglie proposte in `gate2/THRESHOLDS.md` (la differenza giornaliera del funding oggi è fuori da ogni tolleranza ragionevole: 0,146-0,155 punti su 4 giorni).

## Domande aperte (estratti da chiedere alla macchina)
1. Funding, estratto A: per ogni regolamento dell'8-12 novembre e per ogni moneta tenuta, la riga `FUNDING_FEE` del demo (`/fapi/v1/income`, con simbolo e ora) accanto alla quantità tenuta in quel momento (dalle esecuzioni, o dalle posizioni lette ogni ora) e al tasso del mercato vero (`fapi.binance.com/fapi/v1/fundingRate`) e del demo (`demo-fapi`, stessa chiamata). Dice se i tassi del demo sono diversi e in quali monete.
2. Funding, estratto B: i tassi veri 8-12 novembre di ICPUSDT, 龙虾USDT e IRYSUSDT (chiamata pubblica, leggera) e se ICPUSDT sul demo è sospesa: chiude D5.
3. Funding, estratto C: dal paper G1 le quantità volute per moneta e giorno (`/paper_g1/ribilanciamenti/{data}`, pesi) per sommare il funding paper moneta per moneta e confrontarlo con A.
4. Commissioni, estratto D: le esecuzioni del demo (`/fapi/v1/userTrades`, 8-12 novembre) con moneta, lato, prezzo, quantità, valore, commissione, valuta della commissione e `maker` (vero/falso: chi ha tolto liquidità); più `/fapi/v1/commissionRate` per due monete. Dà valore scambiato, quota a mercato e commissione reale esatti.
5. Il 7 novembre il demo risulta con commissioni ~0,00 USDT nonostante il primo ribilancio a 280 (0712): c'è un buco nelle entrate del 7 novembre?
6. Quanto vale il conto vero con ICPUSDT assente: il conto vero la ha? (La risposta cambia la causa D5 per i soldi veri.)
