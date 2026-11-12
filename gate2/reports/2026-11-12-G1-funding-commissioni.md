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

---
# Aggiornamento del 12 novembre (sera): letture vere di Binance (`ops/results/0736-12nov-stato-esecuzioni-demo.md`, righe 98-140)
Sostituisce, dove li contraddice, i numeri stimati sopra. Soglie ancora non approvate: solo misure. Tutto vale per il demo (commissione del conto demo: maker 0,02%, taker 0,04%; il conto vero può avere taker 0,05%, la tariffa standard dei perpetui, non verificata qui).

## A. Commissione vera (esecuzioni `userTrades` lette per 63 monete; commissioni dagli incassi e dalle esecuzioni combaciano: 0,9163 USDT)
| periodo | valore scambiato | commissione | in % del valore | a commissione bassa (maker) | esecuzioni |
|---|---|---|---|---|---|
| 7 nov (conto a 280, prima) | 53,13 | 0,0106 | 0,0200% | 100% | 11 |
| 8 nov (da vuoto) | 2.288,77 | 0,7320 | 0,0320% | 47% (per valore ~40%: 0,0320 = 0,02+0,02×q dà q=60% a mercato) | 195 |
| 9-12 nov (regime, dopo la partenza) | 684,07 | 0,1737 | 0,0254% | ~73% (0,77/0,43/0,83/0,80 per giorno) | 95 |
| 6 giorni | 3.025,97 | 0,9163 | 0,0303% | 54% | 301 |
Fonte dei giorni: tabella 0736; la riga «9-12» è la mia somma (quota maker pesata sul valore: 497,8/684,1; coerente con 0,0254% = 0,02 + 0,02×27%).
- **Contro il paper e la ricerca** (0,02% a limite, 0,05% a mercato per il resto): il paper spende in media circa 0,024% del valore (stima mia: costi 25,27 su un valore ~105.000 ricavato dal «tutto a mercato 65,44», con scarto di prezzo incluso). Il demo a regime è a 0,0254%: praticamente uguale; la partenza da vuoto è stata più cara (0,032%, quota a mercato circa 60%). La ricerca assume ordini quasi tutti a limite (nessun ordine non eseguito su 99,6%): nel demo a regime il 27% del valore è a commissione da mercato, nella partenza il 60%.
- **Cosa cambia con taker 0,04%**: un'esecuzione a mercato costa 0,04% e non 0,05%: a regime 0,0254% (contro 0,0281% con 0,05%); partenza 0,032% (contro 0,038%, che è esattamente la mia stima di prima con 0,05%: quella stima era giusta nel tasso, sbagliata nel valore scambiato, 1.935 contro 2.289 vero). Sul conto vero con 0,05% la commissione a regime sale di circa 0,003 punti sul valore, cioè ~0,0005% del conto al giorno (circa 0,2% l'anno, con il valore scambiato di regime di ~170 USDT al giorno): piccolo. Il «tutto a mercato» della ricerca (0,05%) resta cautelativo per il demo e giusto per il conto vero se la tariffa è 0,05%.
- La quota «a limite» del rapporto di stato (607 su 642) NON era la quota a commissione bassa: il 46% del valore (27% a regime) paga la commissione da mercato anche se l'ordine è «eseguito a limite»: conferma che il limite GTC al mark attraversa il libro (`demo_binance.py:1332`).
- Chiusa la domanda 5 del primo rapporto: il 7 novembre il valore scambiato fu solo 53 USDT (commissione 0,0106): nessun buco.

## B. Funding: demo contro paper giorno per giorno (0736, tabelle e rapporto)
| giorno | demo | paper | paper meno demo | regolamenti del demo (USDT): 00 / 08 / 16 / altre ore |
|---|---|---|---|---|
| 8 nov | 0,155 | 0,174 | 0,019 | 0,113 / 0,597 / 0,532 / 0,301 |
| 9 nov | 0,198 | 0,231 | 0,033 | 0,400 / 0,796 / 0,624 / 0,174 |
| 10 nov | 0,272 | 0,418 | 0,146 | 1,054 / 0,835 / 0,708 / 0,133 |
| 11 nov | 0,203 | 0,358 | 0,155 | 0,661 / 0,613 / 0,461 / 0,278 |
| 12 nov (parziale) | 0,127 | 0,099 | -0,028 (demo sopra) | 0,553 / 0,567 / 0,602 / 0,152 (alle 16:48) |
Il demo tiene 48-51 monete contro 52-56 del paper. Il 7 novembre: 0,358 USDT, come stimato.
- **Correzione a quanto scrissi in D4**: al regolamento delle 00:00 il demo incassa PIÙ del paper il 10 (0,105% contro 0,055%), l'11 (0,066% contro 0,044%) e il 12 (0,056% contro 0,020%); solo il 9 incassa meno (0,049 contro 0,081, ore diverse incluse). Quindi la differenza dei giorni 10 e 11 sta tutta negli altri regolamenti: circa 0,20 e 0,18 punti sulle 08:00, 16:00 e altre ore (paper ~0,36 e ~0,31, demo ~0,17 e ~0,14). È un fatto misurato, non una causa. Resta da spiegare perché il paper, alle 00:00, incassi meno del demo e poi molto di più: **da confermare** (candidato da controllare nel codice: `f5.py:449` rimette `funding_fino_ms` all'ora del ribilancio, quindi un regolamento delle 00:00 non ancora pubblicato da Binance alle 00:09 andrebbe perso; spiegherebbe il paper basso alle 00:00, NON il paper alto dopo).
- **Monete mancanti**: nel paper di oggi senza funding sul demo: 龙虾USDT -1,86%, IRYSUSDT +0,42%, QUSDT -0,34%, JCTUSDT -0,26% (peso lordo 2,88%); ICPUSDT mancante 3 giorni dall'8 novembre (fino al 10; peso circa -4,5%). Per moneta, il paper non è nell'estratto: posso solo stimare. Tassi giornalieri per unità di peso delle monete forti del demo (funding 5 giorni diviso peso di oggi, stima grossolana): ERA, HUMA, LSK circa 0,65-0,75% al giorno, AERO 0,36%, INIT 2,8%. Con 0,7% al giorno su 6,7% di esposizione mancante il 10 novembre: ~0,05 punti, cioè circa un terzo di 0,146; l'11 novembre (2,4% mancante, più ICP solo alla 00:00): ~0,02 punti, cioè circa un decimo di 0,155. Il 12 il demo supera il paper anche con le stesse monete assenti. **Le monete mancanti spiegano al più un terzo, probabilmente meno; il resto non è spiegato.** Per essere precisi servono i tassi di 龙虾, ICP, IRYS, Q e JCT e il funding del paper moneta per moneta (non presenti in 0736).
- Divergenze, per categoria: **segnale**: nessuna prova. **Tempo**: nessuno scarto di giorno (D1); resta l'anomalia delle 00:00 del paper (sopra). **Prezzo/tassi**: la differenza 10-11 novembre resta non spiegata; contro «tassi del demo diversi»: 9 novembre 08-16 combaciano e il 12 il demo è sopra (non ancora una prova). **Dimensione**: ≤0,023 punti/giorno (D6). **Monete mancanti**: ≤ un terzo (stima). **Dati**: paper per moneta mancante.

## C. L'ipotesi della revisione di G1 (`audits/reports/2026-11-12-G1_CONTO_VERO.md`): a 280 USDT passa solo con l'ordine limite come la ricerca
Dalla revisione: Sharpe corretto 0,81 con limite come la ricerca, 0,77 tutto a mercato, 0,73 con limite solo oltre lo 0,05%; soglia 0,80.
- I dati veri **non sono né l'ipotesi della ricerca né il caso peggiore**: a regime il 27% del valore paga da mercato (46% con la partenza). Interpolando in modo lineare fra 0,81 (0% a mercato) e 0,77 (100%): a regime ~0,80, sull'intero periodo ~0,79. Cioè esattamente sulla soglia: **l'ipotesi è sostenuta nel senso che l'esito dipende da quanto valore va a mercato e il conto vero ne manda una parte non piccola; non è né confermata né smentita nel risultato** (la linearità è una mia ipotesi; la scala 0,04 per 100 punti non permette di decidere un margine di 0,01).
- Differenze che spostano il risultato: il taker del demo è 0,04% (la ricerca assume 0,05%: leggermente meglio); le esecuzioni a mercato del demo avvengono subito a 00:18, non alle 01:00 come nel caso «tutto a mercato» della ricerca; la partenza da vuoto (60% a mercato) non si ripete.
- **Quanti giorni servono**: dipende dalla precisione voluta. La quota a mercato varia molto da un giorno all'altro (17%, 20%, 23%, 57% per valore; scarto tipico ~18 punti, con 8 esecuzioni il 10 novembre). Per conoscerla a ±5 punti (un errore standard) servono circa 13 giorni di regime; per ±5 punti con il 95% circa 50 giorni. Oggi ci sono 4 giorni di regime e 95 esecuzioni (±9 punti al 95%, se indipendenti: non lo sono, perché dentro lo stesso ordine). Conclusione onesta: in 2-3 settimane si saprà se sta sotto o sopra circa il 25%, ma una differenza di 0,01 sullo Sharpe corretto non si vedrà con questi volumi. Con il conto vero (0,05%) e la soglia scesa da 0,95 a 0,80 dopo il risultato, la decisione è comunque di Alessio.

## Estratti ancora utili
1. Funding veri 8-12 novembre di 龙虾USDT, ICPUSDT, IRYSUSDT, QUSDT, JCTUSDT (pubblico, leggero).
2. Funding del paper G1 per moneta e regolamento (quantità del paper e tassi usati), almeno per 10-11 novembre.
3. L'ora in cui il paper ha scritto il funding della 00:00 (`/paper_g1/diario`, scritture del 10 e 11 novembre) per chiudere l'anomalia della 00:00.
