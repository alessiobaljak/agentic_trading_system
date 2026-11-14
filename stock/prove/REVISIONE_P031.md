# Prova 31 — la revisione separata (14 novembre 2026, prima del periodo chiuso)

**Chi ha fatto cosa.** Regole, programma, dati e risultato: la sessione «trading stock» (commit `d3dce4c`, `31adeb3`, `bdd43f3`).
Questa revisione: un agente che non ha scritto il codice, in sola lettura sul repository (unico file scritto: questo). Nessun
rendimento dopo il 31 dicembre 2024 usato (gli script del revisore si fermano con un errore se la serie va oltre). I conti sono stati
riscaricati dalla SEC (`companyfacts`, 519 aziende, 4 richieste al secondo al massimo). I prezzi usati per rifare il calcolo sono quelli
locali, con il difetto noto (circa il 2-3% dei simboli ha la storia dell'azienda di oggi): con i dati committati il calcolo locale
rifà quello ufficiale molto da vicino (correlazione giornaliera 0,9975 fra le due serie; tabella più sotto).

## Esito: **FAIL** per il criterio «entrare nella miscela»; confermata la bocciatura da sola

* **Da sola: bocciata**, confermato in tutte le varianti rifatte (Sharpe da 0,03 a 0,20 contro 0,87 dello SPY).
* **Entrare nella miscela:** il criterio è eseguito come scritto, ma passa **solo con conti che alla data della decisione non si
  conoscevano**. Con i valori dei bilanci com'erano al giorno della decisione la miscela nuova **non** batte la miscela (da 1,070 a
  1,082 contro 1,082, in tre ricostruzioni diverse), e in due ricostruzioni lo Sharpe con i costi doppi va sotto zero. In più, 17
  posizioni scelte usano conti che nessun bilancio annuale aveva ancora depositato al giorno della decisione (spesso di un'altra
  azienda: quella che ha preso il simbolo dopo). Anche senza questi problemi la differenza è un lancio di moneta: nel campionamento a
  blocchi la miscela nuova vince nel **52%** dei casi.

## 1. L'ordine dei commit

| File | Commit | Ora (UTC) |
|---|---|---|
| `P031_redditivita_lorda.md` (regole) | `d3dce4c` | 2026-11-14 02:35:46 |
| `p031.py`, `dati/conti.py`, `P031_redditivita.csv.gz`, `test_conti.py` | `31adeb3` | 02:41:47 |
| `P031_risultati.md`, `serie/P031_redditivita.csv`, `serie/P031_miscela.csv` | `bdd43f3` (lavoro su GitHub) | 02:42:57 |

Le regole vengono prima del programma, dei dati e del risultato. **OK.** Test delle azioni: 104 verdi (`python -m pytest stock/tests -q`).

## 2. Sguardo nel futuro

| Controllo | Esito |
|---|---|
| Composizione dell'indice al giorno della decisione (`P028_membri.csv.gz`) | OK. Controlli a campione: TSLA assente a giugno 2020 e presente a giugno 2021; META al posto di FB a giugno 2022; DWDP a giugno 2018, DD e DOW a giugno 2019 |
| Regola dei 120 giorni (`redditivita_al`, `p031.py:64-67`) | OK sul conto dei giorni: l'esercizio usato ha sempre almeno 120 giorni (minimo 120). **Ma** usa anche esercizi vecchi di anni: problema Alto 1 |
| Cornici «CY» con esercizi che finiscono l'anno dopo | OK: il programma usa la data vera di fine esercizio (`end`), non l'etichetta CY. Esempio: General Mills, esercizio chiuso il 26 maggio 2019 (nella cornice CY2018), è usato solo dalla decisione del 30 giugno 2020 |
| Valori «ultimi depositati» delle cornici (bilanci rifatti dopo) | **Non è piccolo** come scritto nelle regole: decide l'esito del criterio della miscela. Problema Bloccante 1 |
| Conti di un'altra azienda o non ancora depositati | **17 posizioni scelte**: problema Alto 2 |
| Settore (finanziarie escluse) | OK come regola (SIC 6000-6999, 95-105 aziende fuori ogni anno); il SIC è quello di oggi, non di allora (Basso 3) |
| Ordini all'apertura del giorno dopo | OK (`simula_conto`: decisione alla chiusura, ordine eseguito all'apertura della barra dopo; il primo rendimento è il 1° luglio 2016) |
| Nessun dato dopo il 31 dicembre 2024 | OK: `prepara_titolo` taglia a `FINO`; i prezzi si scaricano fino al 1° gennaio 2025 alle 05:00 UTC; le serie finiscono il 31 dicembre 2024 |

## 3. I dati

**Il file** `P031_redditivita.csv.gz`: 5.273 righe, 661 aziende, 5.030 esercizi con la redditività; **nessun doppione** (azienda +
fine dell'esercizio); 46 valori sotto 0 e 15 sopra 1,5; il massimo è **153.304** (FTI, esercizio 2015: beni di 74.100 dollari).
Nelle decisioni le coppie (giorno, azienda) con un valore sono 2.906 (senza contare due volte le aziende con due classi di azioni) e
le posizioni scelte 892: **141 (16%) hanno almeno un problema** (66 esercizio vecchio, 17 conti non ancora depositati, 41 valore
sotto 0 o sopra 1,5, 39 diverso di più del 20% dal valore di allora sullo stesso esercizio). Per anno: 15, 17, 12, 8, 10, 19, 22,
18, 20.

**Rifatto a mano per 16 aziende e 3 esercizi (2015, 2019, 2023)** dal bilancio annuale originale (`companyfacts`), con le voci e
l'ordine delle regole: 37 coppie calcolabili (11 senza le voci: per esempio Exxon in tutti e tre gli anni), **32 uguali entro il
2%**, 4 diverse di più del 10%:

| Azienda, esercizio | Dal bilancio di allora | Nel file | Perché |
|---|---|---|---|
| Johnson & Johnson, chiuso il 1° gen 2023 | 0,341 | 0,296 (−13%) | bilancio rifatto dopo la separazione di Kenvue (2023) |
| Pfizer 2019 | 0,248 | 0,196 (−21%) | rifatto dopo l'uscita di Upjohn (2020) |
| 3M 2023 | 0,281 | 0,190 (−32%) | rifatto dopo l'uscita di Solventum (2024) |
| General Mills, chiuso il 26 mag 2019 | +0,191 | **−0,301** | nei bilanci successivi compare una voce `Revenues` di circa 2 miliardi (non i ricavi totali, che sono 17-20 miliardi): la regola la prende per prima |

Uguali al file ma **sbagliati nella sostanza** (la regola applicata alla lettera): C.H. Robinson 2015 **3,80** (il costo
`CostOfGoodsSold` è solo quello di una parte: con i ricavi netti di 2,27 miliardi sarebbe circa 0,7); General Mills 2023 −0,37; Intuit
2015 0,82 (il costo è solo quello dei prodotti, manca quello dei servizi).

**Su tutto il campione** (2.613 coppie presenti in tutte e due): stesso esercizio in 2.585; differenza sotto l'1% nell'88%, sotto il
5% nel 92%, sopra il 20% in 85; correlazione dei ranghi 0,985. I titoli scelti cambiano: comprati in comune 41-48 su 50 per anno,
venduti 34-44 su 50.

**Voci di ripiego e beni:** l'ordine delle voci è rispettato (`conti.py:78-91`: la prima voce dei ricavi con un costo nella stessa data,
equivalente alla regola); i beni sono presi alla fine dell'esercizio o nei 31 giorni prima (`conti.py:94-98`, test verde).

## 4. Il codice

| Controllo | Esito |
|---|---|
| Pesi 50% comprati, 50% venduti, a pesi uguali | OK (`p031.py:87-88`, `verso_pesi` con il 98% investito) |
| Un anno senza ribilanciare | OK (la strategia ordina solo nei giorni di giugno; in mezzo solo le chiusure dei titoli spariti) |
| Limite del conto 2 volte, come scritto | OK (`LEVA_PER_IL_CAMBIO`, 0 ordini rifiutati) |
| Prestito 0,5% solo sui venduti | OK (`portafoglio.py:207-211`: solo quantità negative; con i costi doppi 1%) |
| Costi e costi doppi | OK (`costi_per` come le prove 11-30; `raddoppiati` raddoppia anche il prestito) |
| Titoli spariti | OK (chiusi all'ultima chiusura dopo 5 giorni senza barra, senza costi: 16) |
| Sharpe annuo | OK (media / deviazione giornaliera × √252) |
| Sharpe corretto | OK (66 serie, 22 gruppi, t 0,27) |
| Trimestri | 32 dal 2017; il 3° e 4° trimestre 2016 non entrano (come le prove 28 e 30): Basso 2 |
| Miscela nuova | OK: esattamente ¾ P025_miscela + ¼ la parte su 2.054 giorni in comune (scarto massimo 1,5·10⁻¹⁶); SPY sugli stessi giorni |

## 5. Quanto è solido «entrare nella miscela» (serie committate)

| Misura | Valore |
|---|---|
| Sharpe miscela nuova / miscela | **1,0850 / 1,0818** (differenza +0,0032) |
| Campionamento a blocchi di 20 giorni, 5.000 ripetizioni: quota in cui la nuova ha lo Sharpe più alto | **52,1%** (differenza dal 5° al 95° percentile: −0,097 / +0,102) |
| Stesso con blocchi di 5 e di 60 giorni (2.000 ripetizioni) | 53,1% e 51,2% |
| Sharpe della parte sui giorni in comune; il suo t | 0,094; **t 0,27** (sulla serie intera, 2.139 giorni, t 0,27) |
| Nei blocchi, quota con lo Sharpe della parte sopra zero | 61% (dal 5° al 95° percentile: −0,50 / +0,69) |
| Sharpe minimo della parte perché la miscela migliori (con le sue oscillazioni e la correlazione −0,01) | 0,074: il margine è 0,02 |
| Togliendo un anno | la differenza va sotto zero senza il 2018 (−0,026), senza il 2020 (−0,029), senza il 2024 (−0,0003) |
| Togliendo i giorni migliori della parte | senza il migliore −0,002; senza i 5 migliori −0,023 |
| Sharpe della parte anno per anno | sopra zero solo nel 2018 (1,34), 2020 (1,28) e 2024 (0,54); 2016 −2,40, 2022 −0,95 |
| Miscela nuova senza ribilanciare ogni giorno / ribilanciata ogni luglio | 1,072 / 1,0785: tutte e due **sotto** 1,0818 |

**Il calcolo rifatto con i prezzi locali**, cambiando solo la redditività (`p031.calcola` con `--finta`, senza mescolamento):

| Variante | Sharpe con i costi | Costi doppi | Parte, giorni in comune | Miscela nuova (miscela 1,082) | Entra? | Blocchi: nuova più alta |
|---|---|---|---|---|---|---|
| Ufficiale (prezzi di allora, GitHub) | 0,09 | 0,03 | 0,094 | 1,085 | sì | 52% |
| A — dati committati, prezzi locali | 0,090 | 0,020 | 0,109 | 1,088 | sì | — |
| B — senza esercizi vecchi (più di 495 giorni) | 0,203 | 0,138 | 0,225 | 1,100 | sì | 62% |
| E — come B, e senza i conti non ancora depositati | 0,161 | 0,098 | 0,184 | 1,091 | sì | 56% |
| G — come E, ma con i valori com'erano alla decisione (2.587 su 2.687 sostituiti) | 0,107 | 0,020 | 0,138 | 1,0818 (−0,0001) | **no** (pari) | 50% |
| C — ricostruzione completa com'era alla decisione, voci della regola | 0,038 | **−0,034** | 0,069 | **1,071** | **no** | 43% |
| D — come C, con la voce dei ricavi e del costo più grandi | 0,032 | **−0,036** | 0,060 | **1,070** | **no** | 42% |

Ricostruzione «com'era alla decisione»: per ogni giugno, solo i bilanci annuali (10-K) depositati prima di quel giorno, il valore
dell'ultimo deposito prima della decisione, l'esercizio più recente chiuso da almeno 120 giorni, i beni a quella data. Script e numeri
nella cartella del revisore (`scratchpad/lav/`: `ricostruisci.py`, `simula.py`, `robustezza.py`, `tabella10.py`).

## Problemi

### Bloccante

1. **Il criterio «entrare nella miscela» passa solo con i conti rifatti dopo.** `stock/dati/conti.py:5-8, 23, 60-75`: le cornici della
   SEC danno l'ultimo valore depositato (bilanci rifatti dopo separazioni e vendite, voci aggiunte negli anni dopo). Le regole lo
   chiamano «un piccolo sguardo nel futuro»; misurato, è quello che decide: con i valori di allora (varianti C, D, G) la miscela nuova
   fa 1,070-1,082 contro 1,082, e nelle varianti C e D anche lo Sharpe con i costi doppi è sotto zero (−0,03), quindi cadono due
   condizioni su tre. Il periodo chiuso non va aperto su questo risultato.

### Alti

1. **Esercizi vecchi di anni.** `p031.py:52` (le righe senza redditività si buttano prima) e `p031.py:64-67` (`redditivita_al` prende
   l'ultimo esercizio *con un valore*): quando un'azienda cambia le voci del bilancio, il programma continua a usare l'ultimo esercizio
   calcolabile, anche di 9 anni prima. Le regole dicono «l'esercizio più recente chiuso almeno 120 giorni prima». 190 casi oltre i
   495 giorni, **66 posizioni scelte** (7%): C.H. Robinson comprata dal 2018 al 2024 con l'esercizio 2017 (3,22, anche sbagliato); RTX
   venduta dal 2018 al 2024 con l'esercizio 2017 (−0,014, sbagliato); Intuit comprata nel 2023 e 2024 con il 2017; AT&T nel 2021-2024
   con il 2014. Correggerlo da solo migliora il risultato (variante B: 0,20 e 1,100).
2. **Un solo codice SEC per simbolo per tutto il 2016-2024** (`stock/universo/codici_sec.csv`, costruito in
   `stock/dati/eventi_minuti.py:39-56`): per i simboli passati a un'altra azienda si usano i conti dell'azienda di dopo, depositati
   dopo la decisione. 17 posizioni scelte (29 candidati) usano un esercizio che nessun 10-K aveva ancora depositato: FTI 2016 (conti di
   TechnipFMC depositati nel 2017-2018; beni di 74.100 dollari, redditività 153.304), LLL 2016, BHGE, DD, EQT, VLO e WRK 2017, ARNC,
   EQT, WRK e YUM 2018, CTVA e DOW 2019, GEV 2024 (per alcune, come GEV, DOW e CTVA, i numeri erano forse in un documento di
   registrazione, non in un 10-K: non verificato). È uno sguardo nel futuro non scritto nelle regole. Da solo pesa poco (da B a E: 1,100
   → 1,091).

### Medi

1. **Voci accoppiate male, applicando la regola alla lettera** (`conti.py:78-91`, nessun controllo di buon senso): C.H. Robinson fra i
   comprati in tutti e 9 gli anni con 3,2-3,8 (circa 0,7 con i ricavi netti); Eaton venduta nel 2016-2017 (voce `Revenues` = 0);
   General Mills venduta dal 2020 al 2024 (`Revenues` di 2 miliardi); RTX/UTX, ConAgra, Freeport (svalutazioni nel costo). 41 usi con
   valori sotto 0 o sopra 1,5, tutti finiti fra i comprati o i venduti. Con i valori di allora la scelta delle voci conta poco (C contro
   D), il grosso viene dai valori rifatti.
2. **La miscela nuova è ribilanciata ogni giorno, senza costi** (`p031.py:171`, come scritto e come le prove 25, 28 e 30): senza
   ribilanciare fa 1,072, ribilanciata ogni luglio 1,0785, tutte e due sotto la miscela (1,0818). Per tenere un quarto fisso ogni
   giorno bisognerebbe comprare e vendere ogni giorno un po' di 100 titoli.
3. **Il criterio non distingue dal caso:** 52% nel campionamento a blocchi, t della parte 0,27, l'esito cambia togliendo un giorno o un
   anno (2018, 2020, 2024).

### Bassi

1. Due classi di azioni della stessa azienda contano come due titoli: UA e UAA comprate insieme dal 2016 al 2020 (peso doppio su Under
   Armour) (`p031.py:117-129`).
2. Trimestri: il 3° e 4° del 2016 non entrano (`p031.py:175-176`, come le prove 28 e 30): non cambia nulla, la prova da sola è
   bocciata comunque.
3. Il settore è il SIC di oggi (`conti.py:101-111`), non quello di allora.
4. Copertura: dal 18 al 30% delle aziende non finanziarie resta fuori ogni anno per voci mancanti (118 nel 2016, 62 nel 2024), detto
   nelle regole; per esempio Exxon non è mai calcolabile.
5. I test (`stock/tests/test_conti.py`) non coprono gli esercizi vecchi né lo stesso simbolo con aziende diverse.

## Cosa resta da sapere

* I numeri delle varianti B-G sono con i prezzi locali (difetto noto), non con i prezzi «di allora» di Alpaca: la direzione è
  affidabile (la variante A rifà l'ufficiale: 0,090 contro 0,09; 1,088 contro 1,085), il valore esatto no. Per saperlo serve il lavoro
  di GitHub con le chiavi.
* La ricostruzione «com'era alla decisione» è del revisore (solo 10-K, durata di 350-380 giorni, ultimo deposito prima del giorno):
  altre scelte ragionevoli possono spostare i numeri di qualche centesimo, ma in tre costruzioni diverse il criterio non passa.
* Se si vuole riprovare con i conti di allora, esercizi non più vecchi di un anno e il codice SEC giusto per periodo, è una prova
  nuova: regole da scrivere prima e da contare nel registro.
