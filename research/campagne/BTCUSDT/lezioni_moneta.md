# Lezioni sulla moneta BTCUSDT (idee provate, risultati)

Dati di costruzione 2020-01-01 → 2022-10-18. «t (b)» è il t contro l'entrata casuale con la
stessa uscita: sopra circa 2 è «netto». R medio dopo i costi. Fonte di ogni numero: il
log, voce con lo stesso identificativo.

| Variante | Idea (fonte) | Tf | Verso | Trade | R medio | t (b) | Esito |
|---|---|---|---|---|---|---|---|
| V01 | momentum di 7 giorni (Moskowitz e altri 2012; Liu-Tsyvinski 2018) | 1d | long | 114 | +0,044 | 0,19 | nessun vantaggio; 2022 −0,50 |
| V02 | idem | 1d | short | 100 | +0,023 | 0,49 | nessun vantaggio |
| V03 | rottura del canale di 20 barre (Faith 2007) | 4h | long | 85 | +0,438 | 0,65 | grande R ma come il caso long (la (b) +0,27): è il trend 2020-2021 |
| V04 | idem | 4h | short | 75 | +0,173 | 1,00 | nessun vantaggio netto |
| V05 | barra anomala in rialzo → long (Caporale-Plastun 2019) | 4h | long | 145 | −0,098 | −1,41 | peggio del caso |
| V06 | barra anomala in ribasso → long | 4h | long | 139 | −0,073 | −0,79 | nessun rimbalzo |
| V07 | RSI(2) sopra la media di 200 (Connors-Alvarez 2008) | 4h | long | 121 | −0,047 | −0,81 | nessun vantaggio |
| V08 | idem, specchio | 4h | short | 120 | +0,003 | 0,82 | nessun vantaggio |
| V09 | il lunedì (Caporale-Plastun 2019) | 1d | long | 143 | +0,063 | 1,13 | quasi tutto dal 2020 (+0,19; 2021 −0,03; 2022 +0,01) |
| V10 | rottura di volatilità dall'apertura (Williams 1999) | 1h | long | 300 | +0,149 | 2,35 | **candidato**; regge lo stop fisso (t 3,10); in validazione R +0,048 |
| V11 | idem | 1h | short | 304 | +0,056 | 3,01 | candidato in Fase 2, cade allo scettico: con lo stop fisso t 1,01 |
| V12, V13 | compressione delle bande di Bollinger (2001) | 4h | long, short | 26, 28 | — | — | scarti: pochi trade |
| V14 | funding ≥ 0,05% → short (He e altri 2022) | 8h | short | 119 | +0,069 | 1,47 | non netto; niente segnali nel 2022 |
| V15 | funding negativo → long | 8h | long | 194 | +0,053 | 1,28 | non netto |
| V16 | squilibrio taker alto → long (Chordia-Subrahmanyam 2004) | 4h | long | 194 | +0,073 | 1,16 | non netto |
| V17 | squilibrio taker basso → short | 4h | short | 198 | +0,008 | 0,78 | nessun vantaggio |
| V18 | prima mezz'ora su → ultima mezz'ora long (Gao e altri 2018) | 30m | long | 524 | −0,194 | −3,08 | peggio del caso |
| V19 | prima mezz'ora giù → ultima mezz'ora short | 30m | short | 491 | −0,075 | 2,20 | lordo +0,045 R ma costi 0,12 R; famiglia dei ritocchi V31-V35 |
| V20 | superamento al rialzo dei multipli di 1.000 (Osler 2003) | 1h | long | 1452 | −0,120 | −2,69 | peggio del caso |
| V21 | idem al ribasso | 1h | short | 1413 | −0,098 | −1,50 | nessun vantaggio |
| V22 | martello dopo un ribasso (Nison 1991) | 4h | long | 71 | +0,533 | 1,66 | non netto; senza i 3 migliori −0,03 |
| V23, V24 | stella cadente; vicino al massimo di un anno (George-Hwang 2004) | 4h, 1d | short, long | 60, 12 | — | — | scarti: pochi trade |
| V25 | NR7 (Crabel 1990) | 1h | long | 74 | +0,207 | 1,11 | non netto |
| V26 | NR7 short | 1h | short | 67 | — | — | scarto |
| V27 | «molla» di Wyckoff (Pruden 2007) | 4h | long | 281 | −0,177 | −0,58 | nessun vantaggio |
| V28 | «spinta» di Wyckoff | 4h | short | 331 | +0,002 | 1,84 | non netto; famiglia dei ritocchi V36-V37 |
| V29 | media mobile di 50 con banda (Brock e altri 1992) | 4h | long | 97 | +0,355 | −0,06 | come il caso long: trend |
| V30 | volume più alto di 50 barre (Gervais e altri 2001) | 4h | long | 111 | −0,036 | −0,49 | nessun vantaggio |
| V31 | V19 + giornata in calo | 30m | short | 263 | −0,034 | 2,98 | netto ma R negativo |
| V32 | V31 + volatilità bassa (mediana) | 30m | short | 98 | +0,004 | 2,25 | candidato; cade in Fase 4 (costi doppi, ritardo) |
| V33 | V31 + solo fine settimana | 30m | short | 75 | +0,065 | 3,11 | candidato (filtro visto nei dati); cade in Fase 4 |
| V34 | V31 + i due filtri | 30m | short | 28 | — | — | scarto |
| V35 | V31 + volatilità sotto il 75° percentile | 30m | short | 141 | +0,045 | 3,58 | candidato; cade in Fase 4 |
| V36, V37 | V28 + volatilità alta | 4h | short | 67, 134 | —, −0,246 | —, −0,01 | scarto; fallita |

## Cosa ho capito

1. **Su BTC le idee «di trend» a 4 ore e 1 giorno guadagnano molto in R, ma non più di
   un'entrata a caso nella stessa direzione** (V03, V29): nel 2020-2021 bastava essere
   long. Il confronto con la (b) lo smaschera.
2. **Le idee di ritorno alla media di breve (V05-V07, V27) perdono contro il caso**: nel
   2020-2022 BTC a 4 ore non rimbalza dopo gli eccessi.
3. **La rottura di giornata (Williams) è l'unica idea che regge nei due periodi**, ma in
   validazione molto più debole che in costruzione.
4. **Gli stop agganciati a un livello di prezzo (apertura del giorno, estremo della
   barra) gonfiano il confronto con le baseline**: gli ingressi a caso hanno stop
   vicinissimi e costi enormi in R. È così che V11 sembrava un candidato. Va sempre
   controllato con uno stop fisso.
5. **L'ultima mezz'ora short (Gao e altri) ha un piccolo vantaggio lordo (+0,045 R), ma
   vale un terzo dei costi**: i ritocchi lo hanno reso «netto» contro il caso, ma non
   reggono costi doppi né il ritardo. È un esempio da manuale di salita a tentativi su
   una sola famiglia.
6. **Il funding estremo (V14, V15) e lo squilibrio degli ordini aggressivi (V16)** danno R
   positivi ma non netti: segnali deboli, da non buttare se un giorno si potranno contare
   più monete insieme.
