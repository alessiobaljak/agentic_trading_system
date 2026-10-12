# ETHUSDT — Lezioni della moneta

Idee provate, risultati e cosa se ne capisce. Tutto sul periodo di costruzione
(2020-01-01 → 2022-10-18), salvo dove detto. Fonte di ogni numero: il log
(`log.jsonl`, voce indicata) e gli esiti in `data/insample/ETHUSDT/lavoro/` (si rifanno con
`codice/testa.py`). Restano in questa cartella fino al Passo 7.

## In una riga

Su 30 varianti testate (18 idee con fonte, 15 famiglie di meccanismo) nessuna ha un
vantaggio che regga: una sola e' diventata candidato (ETHUSDT-026, short sul rifiuto del
massimo del giorno prima) ed e' caduta alle verifiche della Fase 4 (costi doppi e ritardo).

## Tutte le varianti

R medio dopo i costi; "(b)" = R medio delle 200 simulazioni a entrate casuali con la stessa
uscita; t = la lettura di «nettamente» (soglia circa 2,0-2,2 secondo i blocchi).

| id | variante | tf | direzione | trade | R medio | R senza 3 migliori | t contro (a) | R medio (b) | t contro (b) | candidato | previsione giusta |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ETHUSDT-001 | I-01a | 1d | long | 123 | +0,245 | +0,122 | +0,33 | +0,174 | +0,48 | no | no |
| ETHUSDT-002 | I-01b | 1d | short | 110 | -0,121 | -0,281 | +0,43 | -0,164 | +0,31 | no | si' |
| ETHUSDT-003 | I-02a | 4h | long | 106 | +0,343 | -0,089 | +0,70 | +0,297 | +0,17 | no | no |
| ETHUSDT-004 | I-02b | 4h | short | 81 | -0,046 | -0,262 | +0,61 | -0,162 | +0,69 | no | si' |
| ETHUSDT-005 | I-03a | 1d | long | 34 | scarto |  |  |  |  |  |  |
| ETHUSDT-006 | I-03b | 1d | short | 47 | scarto |  |  |  |  |  |  |
| ETHUSDT-007 | I-04a | 4h | long | 170 | -0,027 | -0,053 | +0,05 | -0,021 | -0,13 | no | si' |
| ETHUSDT-008 | I-04b | 4h | short | 130 | -0,001 | -0,037 | +1,06 | -0,057 | +1,24 | no | si' |
| ETHUSDT-009 | I-05a | 4h | long | 246 | +0,153 | +0,047 | +1,02 | -0,025 | +0,82 | no | no |
| ETHUSDT-010 | I-05b | 4h | short | 224 | -0,014 | -0,115 | -0,04 | -0,114 | +0,21 | no | si' |
| ETHUSDT-011 | I-06a | 30m | long | 532 | -0,087 | -0,093 | -1,08 | -0,071 | -1,13 | no | si' |
| ETHUSDT-012 | I-06b | 30m | short | 489 | -0,038 | -0,047 | +2,56 | -0,073 | +2,32 | no | no |
| ETHUSDT-013 | I-07a | 1h | long | 213 | -0,038 | -0,061 | +0,28 | -0,046 | +0,21 | no | si' |
| ETHUSDT-014 | I-07b | 1h | short | 103 | -0,181 | -0,242 | -1,95 | -0,058 | -1,93 | no | no |
| ETHUSDT-015 | I-08a | 8h | short | 111 | -0,137 | -0,245 | -0,05 | -0,085 | -0,39 | no | si' |
| ETHUSDT-016 | I-08b | 8h | long | 121 | -0,006 | -0,101 | -0,20 | +0,049 | -0,47 | no | si' |
| ETHUSDT-017 | I-09a | 1d | long | 145 | +0,058 | -0,016 | +0,05 | +0,017 | +0,50 | no | si' |
| ETHUSDT-018 | I-10a | 1d | long | 126 | -0,097 | -0,165 | -1,77 | +0,013 | -1,52 | no | si' |
| ETHUSDT-019 | I-10b | 1d | short | 124 | -0,180 | -0,240 | -1,16 | -0,049 | -1,86 | no | no |
| ETHUSDT-020 | I-11a | 1h | long | 1641 | -0,051 | -0,060 | +0,37 | -0,053 | +0,09 | no | si' |
| ETHUSDT-021 | I-11b | 1h | short | 1530 | -0,078 | -0,088 | -0,07 | -0,073 | -0,24 | no | si' |
| ETHUSDT-022 | I-12a | 1d | long | 65 | scarto |  |  |  |  |  |  |
| ETHUSDT-023 | I-12b | 1d | short | 42 | scarto |  |  |  |  |  |  |
| ETHUSDT-024 | I-13a | 1h | long | 136 | -0,366 | -0,547 | -2,00 | -0,087 | -2,09 | no | no |
| ETHUSDT-025 | I-13b | 1h | short | 111 | -0,513 | -0,618 | -2,75 | -0,138 | -2,89 | no | no |
| ETHUSDT-026 | I-14a | 1h | short | 615 | +0,023 | -0,023 | +2,76 | -0,175 | +2,67 | si' | no |
| ETHUSDT-027 | I-14b | 1h | long | 530 | -0,044 | -0,075 | +1,34 | -0,133 | +1,08 | no | si' |
| ETHUSDT-028 | I-15a | 1d | long | 328 | +0,005 | -0,029 | -0,66 | +0,010 | -0,10 | no | si' |
| ETHUSDT-029 | I-15b | 1d | short | 326 | -0,091 | -0,114 | +0,01 | -0,046 | -1,02 | no | si' |
| ETHUSDT-030 | I-16a | 1h | long | 1000 | -0,031 | -0,036 | +1,36 | -0,047 | +1,55 | no | si' |
| ETHUSDT-031 | I-16b | 1h | short | 997 | -0,041 | -0,046 | +0,95 | -0,054 | +1,14 | no | si' |
| ETHUSDT-032 | I-17a | 1h | long | 316 | +0,229 | +0,182 | +1,38 | -0,099 | +1,52 | no | no |
| ETHUSDT-033 | I-17b | 1h | short | 306 | +0,021 | -0,027 | +1,99 | -0,283 | +1,66 | no | si' |
| ETHUSDT-034 | I-18a | 1h | short | 127 | +0,015 | -0,031 | +1,39 | -0,130 | +1,17 | no | no |

## Cosa abbiamo capito (osservato, con la sua fonte nel log)

* **Il rialzo del 2020-2021 fa sembrare buone le strategie long, e lo prende anche il caso.**
  Long su una settimana positiva (ETHUSDT-001): +0,245 R, ma un long casuale con la stessa
  uscita fa +0,174 (t 0,48). Rottura di Donchian long (ETHUSDT-003): +0,343 R, il caso +0,297
  (t 0,17), e senza i 3 trade migliori -0,089. Con lo stop al 6% (sotto 1 ATR giornaliero,
  che era il 7%) anche pochi punti di trend valgono molto in R.
* **Le idee "di trend" (momentum di una settimana, Donchian, media di 50 giorni) non danno
  nulla oltre il caso** in entrambe le direzioni (t fra 0,17 e 0,69); la media di 50 giorni
  ha troppo pochi trade in tre anni (34 e 47).
* **Sotto l'ora i costi mangiano tutto.** A 30 minuti un giro costa 0,067 R: lo short
  dell'ultima mezz'ora dopo una prima mezz'ora in discesa (ETHUSDT-012) e' davvero migliore di
  uno short casuale (t 2,32), ma l'effetto, circa 0,035 R, e' la meta' del costo. Lo stesso per
  la "stessa ora dei giorni passati" a 1 ora (ETHUSDT-030 e -031: t 1,55 e 1,14, R negativo).
* **Le barre orarie enormi con volume altissimo non rimbalzano** (ETHUSDT-024 e -025: R -0,37
  e -0,51, peggio del caso, t -2,09 e -2,89, in tutti gli anni). Ma nemmeno continuano
  abbastanza: lo short dopo la caduta con uno stop largo (ETHUSDT-034) fa +0,015 R, t 1,17. Il
  fallimento del rimbalzo era soprattutto lo stop stretto, toccato da una volatilita' che resta
  alta per ore.
* **Nei ribassi forti ETH tende a resistere.** Short quando ETH scende meno di BTC
  (ETHUSDT-014: t -1,93) e short dopo un giorno anomalo negativo (ETHUSDT-019: t -1,86) vanno
  peggio di uno short casuale. Anche il long dopo un giorno anomalo positivo (ETHUSDT-018: t
  -1,52) va peggio del caso: a un giorno, dopo i giorni estremi il prezzo non prosegue. Sono
  indizi, non prove (nessuno supera la soglia).
* **Il funding, il lunedi', lo squilibrio degli ordini e i numeri tondi non dicono nulla** a
  queste scale: t fra -1,02 e +0,50. I numeri tondi sono il risultato piu' "pulito": circa
  1.600 trade per direzione, R identico al caso (t 0,09 e -0,24).
* **La famiglia piu' vicina a qualcosa e' la rottura di volatilita' dall'apertura del giorno**
  (ETHUSDT-032 long: +0,229 R, +0,182 senza i 3 migliori, t 1,52; ETHUSDT-033 short: t 1,66).
  Non batte nettamente il caso: non e' un risultato.
* **L'unico candidato era fragile** (ETHUSDT-026, vedi sotto): batte il caso perche' perde
  meno di uno short casuale nel rialzo, con R medio +0,023, che non sopravvive ai costi doppi.

## Il candidato ETHUSDT-026 alle verifiche della Fase 4

| Verifica | Esito | Numeri |
|---|---|---|
| Stabilita' per anno | superata | R per anno -0,050 / +0,138 / -0,056, tutti sopra la (b) (-0,175) |
| Pochi trade estremi | superata | senza i 3 migliori -0,023, sopra la (b) |
| Liquidazione | superata | 0 violazioni |
| Robustezza (+-20%) | superata | 6 casi su 6, t contro la (b) fra 2,22 e 3,08, tutti netti |
| Timeframe adiacenti | superata | 30m t 3,05 (netta); 2h t 1,57 |
| Regola intra-barra opposta | nessuna differenza | il candidato non ha target |
| **Costi doppi** | **non superata** | R medio -0,076 (contro la (b) a costi doppi t 3,58, ma l'R deve restare positivo) |
| **Ritardo di una barra** | **non superata** | t 1,27 contro 2,67 (serve almeno 1,33); nessun lookahead trovato (voce N014) |

Cosa si capisce: il rifiuto al massimo del giorno prima porta un'informazione **stabile**
(in ogni parametro e timeframe vicino lo short perde molto meno di uno short casuale), ma
in assoluto vale circa zero dopo i costi e si concentra nella prima ora dopo il segnale.
Non e' un vantaggio da negoziare short da solo (voce ETHUSDT-N015).

## Quanto credere a questi numeri

Con 30 varianti, la regola «nettamente» uscirebbe per caso in circa 0,7 varianti; ne sono
uscite 2 (ETHUSDT-012 e -026), e 2 dalla parte opposta (t sotto -2). La probabilita' di
vederne almeno 2 per caso e' il 14,8% (`codice/fase5.py`). Il quadro e' compatibile con
"nessun vantaggio" su ETHUSDT con queste idee.
