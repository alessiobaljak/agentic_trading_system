# Quando e perché F5 perde (controllo descrittivo, 25 ottobre 2026)

Non è una prova: è la lettura delle 302 settimane di F5 (parità corrette, `risultati_controllo_parita/settimane_F5.csv.gz`, dal 4
gennaio 2021) accanto al contesto di ogni settimana. Netto medio +1,06% a settimana.

## Le 15 settimane peggiori

| lunedì | netto | lato long | lato short | universo nella settimana | Bitcoin |
|---|---|---|---|---|---|
| 2024-02-26 | −14,7% | +15,0% | −29,7% | +21,7% | +22,1% |
| 2021-02-08 | −13,1% | +44,3% | −57,4% | +50,4% | +25,2% |
| 2026-06-01 | −10,6% | −10,8% | +0,2% | −8,2% | −14,1% |
| 2023-12-18 | −10,5% | +6,7% | −17,2% | +14,4% | +3,9% |
| 2026-06-22 | −8,2% | −6,2% | −2,0% | −2,7% | −5,9% |
| 2025-05-05 | −7,9% | +23,8% | −31,7% | +27,6% | +10,5% |
| 2024-09-02 | −7,0% | +1,0% | −8,0% | +3,7% | −4,2% |
| 2024-08-12 | −6,4% | +0,8% | −7,2% | +3,7% | −0,5% |
| 2021-06-07 | −6,2% | −13,7% | +7,5% | −12,1% | +8,9% |
| 2021-12-20 | −6,1% | +15,3% | −21,4% | +18,7% | +8,8% |
| 2026-08-10 | −5,8% | −3,3% | −2,4% | −2,6% | −3,1% |
| 2022-10-24 | −5,7% | +5,2% | −10,8% | +7,0% | +5,4% |
| 2021-02-15 | −5,6% | +8,4% | −13,9% | +11,5% | +18,1% |
| 2022-06-13 | −5,5% | −8,6% | +3,1% | −6,3% | −22,6% |
| 2023-12-04 | −5,2% | +9,1% | −14,3% | +12,4% | +9,6% |

Nelle 15 peggiori: lato long +5,8%, **lato short −13,7%**, universo +9,3% (in una settimana normale +0,5%). Nelle 15 migliori:
long +8,7%, short +2,1%, universo +5,1%.

## Cosa dicono

1. **F5 perde soprattutto nelle settimane in cui tutte le altcoin volano** (10 delle 15 peggiori): il lato long guadagna, ma le
   monete vendute (quelle con il funding più alto, i long affollati) salgono **più** della media, e lo short perde più di quanto il
   long guadagna. È lo schiacciamento degli short, lo stesso rischio visto nelle prove 21, 62, 75-76: il lato venduto ha il beta
   più alto nei rally.
2. Le altre 5 sono settimane di crollo con il lato long che perde più di quanto lo short guadagna (giugno 2026, due volte).
3. **Negli estremi F5 guadagna comunque in media**: per quintile del rendimento dell'universo nella stessa settimana, +2,6% quando
   l'universo crolla (lo short rende +16%), +1,7% quando vola (il long +16%), e +0,3% nelle settimane in mezzo. Le perdite grosse
   sono una minoranza delle settimane estreme: F5 non è una strategia «da mercato calmo».
4. **Una cosa nota prima della settimana**: il funding medio dell'universo nei 7 giorni prima. Per quintile: **+0,25% a settimana
   quando il funding medio è molto negativo** (sotto −11% l'anno: gli short affollati su tutto il mercato), +1,16%, +0,67%, +1,12%,
   **+2,10% quando è alto** (sopra +10% l'anno). Coerente con il meccanismo (F5 guadagna da chi paga la leva); con 61 settimane per
   quintile la differenza fra il primo e gli altri è circa 2 errori standard: suggestiva, non dimostrata. Il Bitcoin dei 30 giorni
   prima non dice niente di ordinato.

## Cosa NON si fa

Non si cambia F5 su questi numeri: sono stati visti su tutti gli anni usati. Il punto 4 va in coda (idea 45) e si può provare solo
in avanti (nel paper) o su dati non usati.

## Aggiunta del 25 ottobre: da dove viene il beta più alto del lato venduto (idea 51, descrittivo)

Sulle 302 settimane: beta medio 0,97 del lato long e 1,03 dello short. Fra le monete dell'universo, il beta non segue il momento
(correlazione di rango con il rendimento dei 7 giorni prima −0,04) né il volume (−0,10): segue la **volatilità** (0,52). Le monete
vendute sono le più agitate (volatilità dei 30 giorni 0,060 contro 0,057 del lato long, pur con i pesi 1/volatilità dentro ogni
lato) e per questo salgono di più nei rally. Quindi la neutralità al beta (prove 86 e 88) è in buona parte una neutralità alla
volatilità fra i due lati: è una protezione strutturale, non una scommessa sul momento.
