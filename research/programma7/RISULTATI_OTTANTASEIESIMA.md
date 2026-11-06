# Risultati della ottantaseiesima prova (prova 148): G1 con 250 euro

Calcolo del 6 novembre 2026, 06:09 UTC (`python3 -m research.programma7.ottantaseiesima`, numeri in
`risultati_ottantaseiesima/risultati.json`, rendimenti dei giorni in `giorni.csv.gz`). Le regole sono in `OTTANTASEIESIMA.md`,
spinte prima del calcolo (commit f85e2ddd). Periodo: dal 4 gennaio 2021 al 4 ottobre 2026. Capitale fisso di 280 USDT, cioè 250 euro al
cambio di 1,1209.

## Il controllo del simulatore

G1 senza minimi, fatto con il simulatore nuovo, dà Sharpe 1,984, +54,5% l'anno e discesa −28,7%. Lo stesso conto con
`nucleo.variazioni` dà 1,981, +54,4% e −28,75%. La piccola differenza viene dal capitale fisso contro il capitale che si compone.

## I conti

| Conto | Sharpe | All'anno | Discesa | Esposizione tenuta | Ordini al giorno | Correlazione con G1 (settimane) |
|---|---|---|---|---|---|---|
| G1 senza minimi (il paper) | **1,98** | +54,5% | −28,7% | 100% | 55,7 | 1 |
| **A, come il bot oggi, 280 USDT** | **1,90** | +57,8% | −26,8% | 93% | 6,6 | 0,90 |
| A2, chiusure permesse sotto il minimo, 280 USDT | 1,83 | +49,9% | −26,1% | 81% | 12,9 | 0,91 |
| B, 10 monete per lato, 280 USDT | 1,72 | +55,7% | **−39,5%** | 92% | 8,5 | 0,76 |
| A, 1.000 USDT | 1,91 | +53,6% | −28,5% | 99% | 14,7 | 0,98 |
| A2, 1.000 USDT | 1,97 | +53,7% | −26,6% | 96% | 25,5 | 0,99 |
| A, 5.000 USDT | 1,97 | +54,1% | −28,6% | 100% | 38,3 | 1,00 |
| A2, 5.000 USDT | 1,98 | +54,4% | −28,4% | 100% | 44,8 | 1,00 |

**Ogni anno**, guadagno all'anno:

| Anno | G1 senza minimi | A con 280 USDT | B con 280 USDT |
|---|---|---|---|
| 2021 | +110,0% | +139,9% | +96,9% |
| 2022 | +31,8% | +27,7% | +45,4% |
| 2023 | +8,3% | +18,3% | **−5,4%** |
| 2024 | +68,2% | +68,1% | +69,1% |
| 2025 | +72,6% | +55,1% | +76,5% |
| 2026 | +29,5% | +30,4% | +50,1% |

**A con 280 USDT, nel dettaglio**:
* salta il 90% degli ordini che G1 vorrebbe (122.958 su 136.849);
* tiene in media 53 monete (G1 ne vuole 53);
* le posizioni che andrebbero chiuse ma restano sotto i 5 USDT valgono in media l'8,5% del capitale;
* spese 4,1% l'anno (G1 6,3%);
* la differenza giornaliera con G1 oscilla dello 0,73%.

## L'esame

| Conto | Sharpe rispetto a G1 | Discesa rispetto a G1 | Ogni anno positivo | Esito |
|---|---|---|---|---|
| **A** | **96%** (almeno 90%) | **1,9 punti meglio** | sì | **passa** |
| A2 | 92% | 2,6 punti meglio | sì | passa |
| B | 87% | **10,8 punti peggio** | no (2023) | non passa |

**Per la regola scritta prima, G1 può partire con 280 USDT così com'è.** Passa A, quindi non serve nemmeno la correzione delle
chiusure.

## Cosa abbiamo capito

**1. Con 280 USDT il conto segue G1, ma solo a grandi linee.** Fa un ordine ogni otto di quelli che G1 vorrebbe. Il minimo di 5 USDT
fa da banda: si scambia solo quando la differenza supera il minimo. Sul passato questo:
* costa poco Sharpe: 1,90 contro 1,98;
* aggiunge oscillazione: 30,4% l'anno contro 27,5%;
* toglie un po' di spese.

Settimana per settimana il conto è diverso dal paper (correlazione 0,90): nel confronto con il paper lo scarto sarà grande, ed è atteso.

**2. Permettere le chiusure sotto il minimo peggiora, non migliora.** Con A2:
* gli ordini che riducono partono sempre, quelli che aumentano solo sopra i 5 USDT;
* le posizioni scendono e non risalgono: l'esposizione cala all'81%;
* lo Sharpe cala a 1,83.

**La regola di oggi del bot, che salta tutti gli ordini sotto il minimo nei due versi, è la migliore delle due: il bot non va toccato.**

**3. Tenere meno monete non serve.** B, con 10 monete per lato, ha la discesa peggiore (−39,5%) e un anno in perdita (2023). Non si
mette.

**4. 280 USDT sono vicini al bordo** (questa parte è per capire, aggiunta dopo il primo calcolo, e non decide niente). A con capitali
diversi, Sharpe:

| 150 | 200 | 225 | 250 | 280 | 300 | 350 | 400 | 500 | 700 | 1.000 | 2.000 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1,49 | 1,66 | 1,89 | 1,83 | 1,90 | 1,87 | 1,88 | 1,83 | 1,90 | 1,92 | 1,91 | 1,98 |

Fra 225 e 1.000 USDT lo Sharpe sta fra 1,83 e 1,92, cioè fra il 92% e il 97% di G1. Sotto i 220 USDT circa cala in fretta: 1,66 con 200,
1,49 con 150. Ogni anno è positivo con tutti i capitali.

Con il capitale vero, che sale e scende, una discesa come la peggiore del passato (−27%) porterebbe 280 USDT a circa 205: nella zona
dove G1 rende meno. Lo stop sul conto (−35% dal massimo) chiuderebbe tutto a circa 182 USDT.

## Correzione fatta dopo il primo calcolo (scritta per trasparenza)

Il primo calcolo contava come tenute delle posizioni di meno di un centesimo di dollaro. Erano resti che il simulatore lasciava dopo i
giorni senza prezzo nei dati, e che restavano aperti per anni. Sul conto vero la quantità tenuta è un multiplo del passo e la chiusura è
sempre della posizione intera. Corretto in `conto_vero`, con un test.

Gli esiti non cambiano:

| | Primo calcolo | Dopo la correzione |
|---|---|---|
| A | 1,89 | 1,90 |
| A2 | 1,82 | 1,83 |
| B | 1,74 | 1,72 |

Cambiano l'esposizione tenuta e le monete tenute, che prima contavano anche i resti e i giorni senza prezzo.

## Cosa resta fuori

* **I filtri di oggi applicati al passato.** Il minimo di 50 USDT del Bitcoin e il passo di 0,001 non c'erano nel 2021.
* **Gli ordini veri con 280 USDT.** Il demo li ha confermati con 5.000 (`MIGLIORARE_G1.md`, voci 1-3), non con 280. I minimi del demo
  sono un po' diversi da quelli veri:
  * il passo del Bitcoin è 0,0001 invece di 0,001;
  * BCH, LTC, ETC e LINK hanno minimo 5 invece di 20.
* **Le operazioni a eventi.** Il 5% del conto sono 14 USDT, sotto il minimo del Bitcoin: con 250 euro non si fanno.
