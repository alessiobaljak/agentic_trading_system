# Lezioni su SOLUSDT (idee provate e fallite, risultati)

Campagna del 7 ottobre 2026 (prova di processo, terza moneta). Tutti i numeri vengono dal
log `log.jsonl` e sono sui dati di costruzione (2021-01-01 → 2023-01-04, 734 giorni); il
periodo di validazione (2023-01-05 → 2023-12-31) non è mai stato usato perché nessuna
variante è arrivata alla validazione. Costi: commissione 0,05% e slippage 0,01% per lato,
funding vero. R = guadagno diviso il rischio iniziale (1% del capitale).

## L'ambiente di SOLUSDT nel periodo di costruzione (osservato)

* 2021: da 1,50 a 170 (per 113); 2022 (fino al 4 gennaio 2023): da 170 a 10 (diviso 17).
  Due anni, due regimi opposti e violenti. Il buy and hold a leva 1 del 2021 vale +11.192%,
  quello del 2022 −94%. Qualunque strategia direzionale con R per anno «segue l'anno» non
  ha dimostrato niente: lo si vede in quasi tutte le righe della tabella.
* Funding: nel 2021 positivo nel 95% dei settlement (circa +0,08% al giorno a carico dei
  long); nel novembre 2022 fino a −2% per settlement, a intervalli ridotti a 4 e 2 ore.
* Beta di SOL su BTC a 1 ora: 1,21-1,23 nel periodo di costruzione.
* Buchi nei file dell'archivio (non del mercato): 5 giorni nel last, 7 nel mark.

## Le 17 varianti e come sono andate

| n | Variante | Idea | TF | Dir. | Trade | PF | R medio | R mediano | Win | R medio per anno (trade) | Percentile vs caso | Diff. vs caso ± margine | p | R residuo BTC | R senza 3 migliori |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | I-01-4h-long | I-01 | 4h | long | 160 | 1.64 | +0.263 | -0.154 | 0.32 | 2021: +0.49 (90) / 2022: -0.08 (69) | 100.0 | +0.153 ± 0.551 | 0.2924 | +0.280 | +0.017 |
| 2 | I-01-4h-short | I-01 | 4h | short | 160 | 1.056 | +0.024 | -0.177 | 0.29 | 2021: -0.23 (90) / 2022: +0.32 (69) | 69.0 | +0.022 ± 0.303 | 0.4413 | +0.032 | -0.106 |
| 3 | I-03-1h-long | I-03 | 1h | long | 518 | 0.92 | -0.023 | -0.055 | 0.45 | 2021: +0.04 (257) / 2022: -0.09 (258) | 32.5 | -0.015 ± 0.106 | 0.5972 | -0.016 | -0.042 |
| 4 | I-04-4h-segno-long | I-04 | 4h | long | 103 | 1.37 | +0.119 | +0.011 | 0.52 | 2021: +0.33 (51) / 2022: -0.09 (51) | 89.5 | +0.115 ± 0.340 | 0.2419 | +0.137 | +0.017 |
| 5 | I-05-1h-long | I-05 | 1h | long | 139 | 1.35 | +0.238 | -0.988 | 0.42 | 2021: +0.56 (70) / 2022: -0.13 (67) | 99.5 | +0.275 ± 0.382 | 0.0695 | +0.359 | +0.093 |
| 6 | I-05-1h-short | I-05 | 1h | short | 109 | 1.02 | +0.022 | -1.011 | 0.39 | 2021: -0.34 (40) / 2022: +0.23 (69) | 70.0 | +0.069 ± 0.370 | 0.3628 | -0.212 | -0.104 |
| 7 | I-06-1h-short-2.5s | I-06 | 1h | short | 148 | 0.649 | -0.100 | +0.098 | 0.64 | 2021: -0.06 (76) / 2022: -0.12 (71) | 18.0 | -0.054 ± 0.183 | 0.7236 | -0.063 | -0.146 |
| 8 | I-07-1h-long | I-07 | 1h | long | 278 | 0.984 | +0.006 | -0.726 | 0.31 | 2021: +0.27 (147) / 2022: -0.33 (130) | 57.5 | +0.013 ± 0.307 | 0.4693 | +0.127 | -0.107 |
| 9 | I-07-1h-short | I-07 | 1h | short | 271 | 0.815 | -0.080 | -0.515 | 0.33 | 2021: -0.25 (130) / 2022: +0.08 (140) | 39.5 | -0.021 ± 0.223 | 0.5727 | -0.118 | -0.149 |
| 10 | I-08-1h-long | I-08 | 1h | long | 534 | 0.726 | -0.171 | -1.012 | 0.42 | 2021: -0.08 (242) / 2022: -0.25 (290) | 0.5 | -0.086 ± 0.125 | 0.915 | -0.139 | -0.185 |
| 11 | I-08-1h-short | I-08 | 1h | short | 549 | 0.741 | -0.127 | -1.009 | 0.43 | 2021: -0.22 (311) / 2022: +0.00 (234) | 12.0 | -0.046 ± 0.134 | 0.7486 | -0.135 | -0.141 |
| 12 | I-09-1h-long | I-09 | 1h | long | 213 | 1.08 | +0.053 | -0.371 | 0.42 | 2021: +0.20 (128) / 2022: -0.19 (83) | 97.5 | +0.134 ± 0.269 | 0.1594 | +0.046 | +0.025 |
| 13 | I-09-1h-short | I-09 | 1h | short | 228 | 1.3 | +0.144 | -0.285 | 0.47 | 2021: +0.03 (86) / 2022: +0.23 (140) | 100.0 | +0.171 ± 0.244 | 0.085 | +0.095 | +0.119 |
| 14 | I-10-1h-long | I-10 | 1h | long | 138 | 1.211 | +0.075 | +0.024 | 0.54 | 2021: +0.17 (79) / 2022: -0.05 (57) | 94.0 | +0.122 ± 0.222 | 0.1479 | +0.011 | -0.017 |
| 15 | I-10-1h-short | I-10 | 1h | short | 114 | 0.61 | -0.185 | -0.387 | 0.39 | 2021: -0.23 (69) / 2022: -0.11 (43) | 3.5 | -0.143 ± 0.233 | 0.8911 | -0.167 | -0.247 |
| 16 | I-13-1h-long | I-13 | 1h | long | 465 | 1.006 | +0.009 | -0.172 | 0.44 | 2021: +0.04 (231) / 2022: -0.05 (233) | 90.0 | +0.050 ± 0.148 | 0.2504 | -0.029 | -0.033 |
| 17 | I-13-1h-short | I-13 | 1h | short | 459 | 0.966 | -0.008 | -0.108 | 0.46 | 2021: -0.09 (226) / 2022: +0.07 (232) | 75.5 | +0.032 ± 0.135 | 0.3208 | -0.052 | -0.043 |

Le colonne «Percentile vs caso» e «Diff. vs caso ± margine» sono contro 200 entrate
casuali con la stessa uscita (percentile dell'R medio del candidato fra gli R medi casuali;
differenza dalla simulazione mediana con 2 errori standard del bootstrap a blocchi).
«R residuo BTC» è l'R medio tolta la parte spiegata da beta × movimento di BTC nella stessa
finestra. Nessuna variante ha violazioni del margine di liquidazione né trade ridotti dal
tetto di leva (stop fra 1,5 e 3 ATR: con rischio 1% il nozionale resta sempre sotto 2 volte
il capitale).

## Cosa ho imparato, idea per idea

1. **Momentum di serie temporale (I-01, 4h).** Il long ha R medio 0,26 ma mediana −0,15 e
   win rate 32%: senza i 3 trade migliori l'R medio è 0,02. Tre entrate del 2021 (agosto-
   settembre, il rialzo da 40 a 200) fanno tutto il risultato. Non è un vantaggio
   misurabile: è aver preso il treno una volta. Lo short è zero.
2. **Sessione americana (I-03).** Nessun effetto: R −0,02, al 32° percentile delle entrate
   casuali. Su SOLUSDT 2021-2022 l'ora del giorno non ha segno.
3. **Fine settimana (I-04).** Il long del fine settimana ha R 0,12 ma senza i 3 migliori
   0,02: tre fine settimana del 2021. Il ritraccio del lunedì non ha abbastanza segnali
   (20-33 in due anni) per essere giudicato.
4. **Continuazione dopo una barra estrema (I-05).** La variante prevista buona (short dopo
   shock negativo) è zero e l'R residuo dopo BTC è −0,21: lo shock era di BTC, e SOL non ha
   aggiunto niente. Quella prevista nulla (long dopo shock positivo) ha R 0,24 al 99,5°
   percentile ma non netto (p 0,07): 2021 +0,56, 2022 −0,13, mediana −0,99. Dopo uno shock
   positivo lo stop a 1,5 ATR scatta nel 50% dei casi; quando non scatta, il 2021 regala.
5. **Ritorno dopo una barra estrema (I-06).** Perdente: win rate 64% con target al punto
   medio della barra dello shock, ma gli stop (36%) costano più di quanto rendono le
   vincite. Comprare o vendere contro uno shock su SOLUSDT, in questi anni, non ha pagato.
6. **Rottura di canale (I-07, 1h).** Profit factor 0,98 long e 0,82 short: i falsi segnali
   mangiano tutto. Il long segue l'anno (+0,27 nel 2021, −0,33 nel 2022).
7. **Bande di Bollinger (I-08).** La peggiore famiglia: comprare sotto la banda inferiore
   ha R −0,17 ed è nettamente peggio delle barre qualsiasi; vendere sopra la superiore
   −0,13. Su una moneta che trenda come SOL, «cavalcare la banda» è la norma, non
   l'eccezione.
8. **Ritracciamento nella tendenza (I-09).** Il long è 0,05 e segue l'anno. Lo **short sui
   ritracciamenti in tendenza ribassista** è il risultato più solido della campagna: R 0,14,
   profit factor 1,30, positivo nel 2021 (+0,03) e nel 2022 (+0,23), sopra tutte le 200
   entrate casuali condizionate alla stessa tendenza, R residuo dopo BTC 0,10, regge senza i
   3 migliori (0,12). Fallisce la sola condizione «netta» contro la simulazione casuale
   mediana (differenza 0,17, margine 0,24, p 0,085). Il criterio era scritto prima del
   test e vale così com'è: non è un candidato. È l'unica idea che varrebbe la pena riprovare
   in una campagna futura con una regola scritta meglio PRIMA (vedi lezioni di metodo).
9. **Ritardo da BTC (I-10).** Il long ha R 0,08 ma R residuo dopo BTC 0,01: è BTC. Lo
   short perde. Nessun ritardo sfruttabile a 1 ora: SOL si muove insieme a BTC.
10. **Sbilanciamento degli ordini taker (I-13).** Zero in entrambe le direzioni (R 0,01 e
    −0,01 su 460 trade). Il flusso degli ordini a mercato di un'ora non predice l'ora dopo.
11. **Funding estremo (I-02), volume alto (I-11), compressione (I-12), ritraccio del fine
    settimana (I-04)**: scartate prima del test perché in due anni di costruzione non
    producono 100 segnali. Il funding estremo in particolare (54-57 segnali al 95°
    percentile, 91-96 al 90°) resta un'idea con meccanismo chiaro che questa moneta non ha
    abbastanza storia per giudicare.

## Conclusione per la moneta

Nessuna strategia valida trovata per SOLUSDT. Le baseline dicono perché: la stessa regola
di uscita applicata a barre qualsiasi perde fra −0,04 e −0,09 R (costi e stop), e nessun
ingresso provato aggiunge abbastanza da superare quel costo in modo distinguibile dal caso
su due anni di dati così diversi fra loro.
