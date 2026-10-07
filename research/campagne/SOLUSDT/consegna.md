# Consegna della campagna SOLUSDT

Data: 2026-10-07. Sessione di campagna (Passo 3 del protocollo, versione 4.3), terza moneta
della prova di processo. Branch `research/campagna/SOLUSDT`. Una sola sessione di lavoro.

## Esito

**Nessuna strategia valida trovata per questa moneta.**

Nessun candidato è stato costruito, quindi nessuno è stato validato: il periodo di
validazione (2023-01-05 → 2023-12-31) non è mai stato toccato da un test. Il vault non è
stato aperto. Nessun candidato va al vault o al trasferimento.

Era l'esito atteso più probabile, scritto prima di cominciare, e i numeri lo confermano con
un margine ampio: delle 17 varianti testate, 9 hanno R medio negativo e nessuna supera il
criterio di Fase 2 registrato prima del test.

## Cosa è stato fatto

| Passo | Cosa | Dove |
|---|---|---|
| Fase 0 | 760 file scaricati e verificati col checksum; impronte registrate; buchi, funding, volumi documentati; 2020 escluso per liquidità; periodi scritti prima dei prezzi | `fase0_dati.md`, log SOLUSDT-001 e 002 |
| Fase 1 | 13 idee con fonte prima del 2024, affermazione falsificabile, 12 spiegazioni concorrenti comuni più le specifiche; stima dei trade per 32 combinazioni | `ipotesi.md`, log SOLUSDT-003..013 (scarti) e 014..031 (registrazioni) |
| Fase 2 | 17 varianti eseguite sui dati di costruzione con le tre baseline, il controllo «è solo BTC» e il controllo «senza i 3 trade migliori» | log, risultati con lo stesso id della registrazione |
| Fase 3-4 | non eseguite: nessuna idea ha superato la Fase 2 | — |
| Fase 5 | tre quasi-passaggi riprovati contro 500 entrate casuali con altro seme (prova informativa, non può promuovere) | log SOLUSDT-033..035 |
| Validazione | nessun candidato | — |

Budget: **17 varianti su 30**. Le altre 13 non sono state spese perché ogni famiglia
disponibile con una fonte valida è stata provata almeno una volta (10 famiglie), le idee
scartate per pochi trade lo restano anche con una soglia più larga, e il protocollo non
chiede di esaurire il budget. Scarti senza budget: 11 combinazioni (I-02 funding estremo,
I-04 ritraccio del fine settimana, I-06 long, I-07 a 4h, I-11 volume alto, I-12
compressione), tutte sotto i 100 segnali in costruzione.

## Le 17 varianti (dati di costruzione 2021-01-01 → 2023-01-04)

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

Criterio di Fase 2, registrato prima di ogni test: almeno 100 trade; profit factor dopo
costi sopra 1; R medio sopra il 90° percentile degli R medi di 200 entrate casuali con la
stessa uscita; differenza dalla simulazione casuale mediana oltre 2 errori standard
(bootstrap a blocchi); R residuo dopo beta × BTC positivo. Nessuna variante le soddisfa
tutte.

## I tre quasi-passaggi, e perché non passano

* **I-09 short (short sul ritracciamento alla media a 20 ore con prezzo sotto la media a
  200 ore).** Soddisfa quattro condizioni su cinque: R 0,14, profit factor 1,30, sopra
  tutte le 200 entrate casuali condizionate alla stessa tendenza, R residuo dopo BTC 0,10,
  positivo nel 2021 e nel 2022, regge senza i 3 migliori. Fallisce la condizione «netta»
  (differenza 0,17, margine 0,24, p 0,085). Fase 5 (500 entrate casuali, altro seme): percentile 99,6; con il giudizio «netta» a un campione (errore standard del solo candidato contro la media del caso) la differenza è 0,17 con margine 0,16: netta per un soffio. Resta fallita per il criterio registrato.
* **I-05 long (continuazione dopo una barra oltre 3 deviazioni al rialzo).** R 0,24 al
  99,5° percentile, p 0,07, ma mediana −0,99 (metà dei trade finisce sullo stop), 2021
  +0,56 e 2022 −0,13: è un'idea che vive nel rialzo del 2021. Fase 5: percentile 98,8; «netta» a un campione falsa (0,28 contro margine 0,31).
* **I-01 long (momentum a 5 giorni su candele 4h).** R 0,26 e profit factor 1,64, ma
  mediana −0,15 e senza i 3 trade migliori R 0,02: tre ingressi dell'estate 2021. Fase 5: percentile 99,4; «netta» a un campione falsa (0,16 contro margine 0,39): la varianza di 3 trade.

Regola 4 e 5 del protocollo: il criterio non si reinterpreta dopo aver visto i numeri. Le
tre varianti sono fallite. L'osservazione sulla condizione «netta» è una proposta di metodo
(`lezioni_metodo_proposte.md`, punto 1), non un ripescaggio.

## Bilancio delle previsioni

10 previsioni corrette su 17 (log SOLUSDT-032, voce per voce). Le 7 sbagliate: tre idee
sono andate meglio del previsto per via del 2021 (I-04 long, I-05 long, I-09 short), due
peggio perché la famiglia è sistematicamente perdente su questa moneta (I-08 long e short),
una era BTC travestito (I-05 short), una ha avuto il segno opposto (I-06 short).

## Limiti noti (sezione 11)

* Due anni di costruzione con regimi opposti (2021 per 113, 2022 diviso 17): la potenza
  dei test è bassa e quasi tutto «segue l'anno».
* Il 2020 (109 giorni) è escluso per liquidità; il rapporto costruzione/validazione
  effettivo è 67/33.
* Vault non perfettamente cieco: chi scrive le ipotesi sa a grandi linee com'è andato il
  mercato dopo il 2023. Nessuna idea è stata scelta o scartata per quel motivo (nessuna
  voce `scarto` con quel motivo nel log); le idee short sono entrate in modo simmetrico
  alle long.
* Stesso modello, stesse fonti delle altre campagne: la convergenza fra monete misura i
  priori del modello, non il mercato.
* Buchi nei file dell'archivio (5 giorni nel last, 7 nel mark): le serie sono state
  intersecate barra per barra; i trade vicini ai buchi non sono stati controllati perché
  nessuna variante è arrivata alla Fase 4.
* Il bot esegue solo timeframe fino a 1h dal vivo: non rileva, perché non c'è nulla da
  portare in paper.

## Cosa resta da fare

Niente per questa moneta. La campagna è chiusa. Se un giorno si riaprisse, l'unica idea
che merita una regola scritta meglio PRIMA del test è lo short sui ritracciamenti in
tendenza ribassista (I-09 short), e il funding estremo (I-02) richiede più storia di quella
che SOLUSDT ha prima del 2024.
