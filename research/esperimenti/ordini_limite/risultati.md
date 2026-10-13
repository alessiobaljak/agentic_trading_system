# Prova degli ordini limite — risultati

Le regole sono in `regole.md` (in vigore dal 2026-10-13 07:13 UTC) e non cambiano. Questo file si scrive in ordine di
tempo: prima le correzioni trovate dopo il lancio (sezione 1, ognuna con cosa è cambiato e perché), poi le impronte
degli strumenti, la parità M, le corse L e (b), le varianti, le misure e l'esito. Nessun numero di L compare prima
che la parità M sia passata su tutte e nove le strategie.

## 1. Correzioni alle regole, trovate dopo il lancio (prima di qualunque numero)

### Correzione 1 — l'ordine in attesa si riempie al suo prezzo, non all'apertura (13 ott 2026, 07:48 UTC)

**Cosa diceva la regola.** La 4.3 dice: «Prezzo di riempimento: P, oppure l'apertura di `k+1` se è già sotto P (il
mercato apre più in basso: si compra meglio)».

**Cosa è sbagliato.** Questo vale per un ordine A MERCATO mandato all'apertura. Un ordine LIMITE messo alla chiusura di
`k` è già nel libro quando la barra `k+1` apre: se il primo scambio avviene sotto P (per un long), l'ordine è stato
eseguito **a P** dal primo venditore che ha attraversato quel prezzo, non all'apertura. Riempirlo all'apertura
avrebbe regalato al trade la differenza fra P e l'apertura, cioè un vantaggio che un ordine limite non ha.

**Cosa cambia.** Nel motore (`riempimento_limite`) e nella variante (c) (uscita «chiudi» a limite): se la barra apre
oltre il prezzo, il riempimento è certo e avviene all'apertura della barra, **ma al prezzo del limite**. Il momento
resta l'apertura: così la regola dei gap del percorso a mercato vale anche qui (se l'apertura è già oltre lo stop,
si esce allo stop all'apertura: perdita oltre 1R, il caso peggiore e quello vero). Con il riempimento sempre a P, il
rischio iniziale vero è sempre quantità × |P − stop| = 1% del capitale, salvo il tetto di leva.

**Perché si corregge e non si lascia.** La regola 4.3 è stata scritta pensando all'ordine a mercato; l'errore è
stato visto scrivendo i test del motore (il caso «la barra apre oltre il limite»), prima di qualunque corsa sui
dati. Lasciarla avrebbe reso la prova ottimista proprio sui trade che partono con un gap a favore.

**Quando.** Trovata e corretta prima del lancio delle corse: nessun numero da rifare.

### Nota 1 — i 30 minuti sono aggregati dai 15 minuti solo per SOLUSDT-023

La sezione 2 dice «30 minuti aggregati da 15 come nelle campagne». Dai log delle campagne: SOLUSDT-023 usava i 30
minuti aggregati dai 15; BTCUSDT-V35, ETCUSDT-033 e AVAXUSDT-V-12 usavano i file nativi a 30 minuti di Binance. La
prova fa come ogni campagna ha fatto (è la condizione della parità M), quindi tre strategie su quattro a 30 minuti
usano i file nativi. Non è una correzione alle regole di esecuzione: è una precisazione sui dati.

## 2. L'esito, in breve (scritto dopo le corse: 13 ott 2026, 08:02-08:26 UTC le corse, 08:45 UTC il testo)

**Esito secondo le soglie scritte prima (sezione 7 delle regole): «conviene poco».** E1 vale (tasso di esecuzione
mediano 98,0%), E3 vale (differenza mediana del lordo L − M −0,0069 R, contro il limite di −0,0112 R), E2 cade
(risparmio mediano del costo 0,0225 R, contro i 0,04 R richiesti). Per le regole «si riporta il numero e decide il
proprietario». Fonte: sezione 7 qui sotto, calcolata da `prova.py --riassunto` sui nove file `esiti/*.json`.

### 2.1 Cosa dicono i numeri

* **La parità M è passata 13 volte su 13** (sezione 4): per tutte e nove le strategie i numeri rifatti oggi con il
  `research/src` del branch principale riproducono quelli dei log delle campagne entro mezza cifra (trade, R medio,
  profit factor, media della (b), t, p). Anche il corpo riscritto di `contro_baseline` (CHANGELOG del 10 ott) dà gli
  stessi t e p: il dubbio del lanciatore del vault è chiuso.
* **I costi scendono di circa un terzo, non della metà.** Periodo intero, mediane sulle nove strategie (dai campi
  `misure` degli esiti): costo medio M 0,0619 R → L 0,0394 R; di cui commissioni 0,0490 → 0,0345 R e scarto di prezzo
  0,0172 → 0,0087 R. Il risparmio di 0,0225 R è il 36% del costo di oggi: è solo il lato d'ingresso che cambia (0,05% →
  0,02% di commissione, scarto zero), le uscite restano a mercato. Riportato al costo del paper (0,095 R a trade, ops
  0607 del 12 ott) la stessa quota varrebbe circa 0,034 R: è una stima per proporzione, non una misura, e resta sotto
  i 0,04 R.
* **L'ordine limite alla chiusura si esegue quasi sempre: 95-99% dei segnali** (sezione 5.3, colonna «tasso»; minimo
  ADAUSDT-037 95,1%, massimo BNBUSDT-045 99,1%). Su candele da 15 minuti a un'ora il minimo della barra dopo scende
  quasi sempre sotto la chiusura precedente (per un long; simmetrico per uno short). La regola «strettamente
  attraversato» era quella prudente; «toccato» (variante a) dà 99-100%: non cambia il quadro. Quello che le candele non
  vedono resta non visto (sezione 9 delle regole): la coda al prezzo P, e il fatto che un ordine messo quando il
  prezzo è già oltre P esegue subito come taker, non come maker.
* **I pochi trade saltati sono i migliori.** In tutto 67 trade saltati su 2.747 trade di M (2,4%, periodo intero,
  dagli elenchi `trade_elenco` e `saltati_elenco`): il loro R medio in M è +0,68, contro +0,06 di tutti i trade di M;
  il 21% ha R > 1. Sono i trade in cui il prezzo parte subito senza tornare sulla chiusura: proprio quelli che
  guadagnano di più. In validazione BTCUSDT-V10 perde 3 trade da +2,63 R medi e il suo R netto passa da +0,048 a
  +0,020 (sezione 5.2). È la «selezione avversa» della domanda 3: in mediana è piccola (E3 vale), ma è concentrata
  nelle strategie di rottura (BTCUSDT-V10 −0,024 R di lordo, ADAUSDT-037 −0,043 R, FILUSDT-016 −0,024 R; sezione 7,
  elenco) e in pochi trade grandi.
* **Anche il caso risparmia uguale.** Le entrate casuali eseguite con la regola limite ((b)-L) guadagnano in mediana
  +0,0163 R rispetto alla (b)-M (stessi ingressi, stesso tasso di esecuzione 98%): il vantaggio di L sulla (b) non
  cambia (periodo intero: 8 strategie su 9 «nette» sia in M sia in L; validazione: 1 su 9 in entrambe, ADAUSDT-037). Un
  ordine limite abbassa i costi, non crea un vantaggio: nessuna strategia esce da questa prova come candidata.
* **Le uscite a limite (variante c) non convengono.** Il costo scende a 0,0217 R ma il lordo cade da 0,0859 a 0,0477 R
  (mediane, periodo intero): un'uscita a limite aspetta che il prezzo torni sulla chiusura, e quando non torna si
  esce una barra dopo, a mercato, peggio. Per le uscite «a segnale» il mercato conviene. Le varianti (a) «toccato» e
  (b) «due barre» cambiano poco (tasso 98-100%, R netto entro 0,03 R da L).
* **Per anno** (sezione 6): il risparmio compare in quasi tutti gli anni di tutte le strategie; i casi in cui L fa peggio
  di M di oltre 0,03 R sono tre (ADAUSDT-037 nel 2022, BTCUSDT-V10 e FILUSDT-016 nel 2023), tutti per trade saltati.

### 2.2 Cosa succede dopo (sezione 8 delle regole)

L'esito è «conviene poco»: decide il proprietario. Proposta, non esecuzione: il risparmio c'è ed è dell'ordine di
0,02 R a trade sulla ricerca (circa 0,03 R stimati sul paper), il lordo in mediana regge, ma la regola butta via i
trade migliori. Se si vuole provarla, va provata nel paper con una misura (tasso di esecuzione, costo per trade, R
dei segnali saltati) per qualche settimana prima di cambiare anche il gate; le uscite restano a mercato. Senza una
decisione, il bot e il gate restano come oggi.

### 2.3 Cosa NON è stato fatto

* GRUPPO-048 (in coda «se il tempo lo permette», sezione 3 delle regole): non eseguita. Servono i dati di 80 monete
  (non scaricati, circa 640 serie) e gli strumenti del gruppo: ore di lavoro per un'informazione che le nove
  strategie danno già. Resta fuori.
* Nessuna misura sul libro degli ordini vero: la prova è su candele, come scritto nella sezione 9 delle regole.

### 2.4 Gli strumenti e i tempi

* `research/src/motore.py`: ingresso «limite» con validità in barre e condizione «attraversato»/«toccato»,
  commissione maker, uscita «chiudi» a limite (variante (c)); nessun cambiamento al percorso «mercato» (test di
  parità bit per bit con il motore del commit 39bb60b2). Riga nel `CHANGELOG.md` della ricerca del 2026-10-13.
* `research/src/tests/test_motore_ordini_limite.py`: 34 casi su candele sintetiche (eseguito, saltato, apertura
  oltre il limite, stop nella stessa barra, sostituzione, variante (c), parità). Suite della ricerca: 2.408 test passati.
* `prova.py` (questa cartella): le corse della sezione 5 per ogni strategia, in processi separati, con le impronte
  SHA-256 al lancio (sezione 3); `--riassunto` scrive le sezioni da 3 in poi di questo file. Gli esiti completi, con
  l'elenco dei trade di ogni corsa, sono in `esiti/<STRATEGIA>.json`.
* Tempi: le nove strategie in 24 minuti su 4 processi (08:02-08:26 UTC); la più lenta DYDXUSDT-008 (17 minuti: il suo
  segnale ricalcola una deviazione standard a ogni barra).

<!-- da qui in poi il testo e' generato da prova.py --riassunto: non modificare a mano -->

## 3. Impronte al lancio

| Strategia | Commit | motore.py | dati.py | statistica.py | parametri.yaml | prova.py | regole.md | Inizio | Fine | Stato |
|---|---|---|---|---|---|---|---|---|---|---|
| BTCUSDT-V10 | fd7d10d40cf7 | 2adb94e11196 | 4b9ed237125e | ca027d2687d9 | 7f530082d7d5 | 314bb569fa65 | 3cccebdcc3df | 2026-10-13T08:02:13Z | 2026-10-13T08:04:11Z | completo |
| BNBUSDT-045 | fd7d10d40cf7 | 2adb94e11196 | 4b9ed237125e | ca027d2687d9 | 7f530082d7d5 | 314bb569fa65 | 3cccebdcc3df | 2026-10-13T08:02:13Z | 2026-10-13T08:03:51Z | completo |
| ADAUSDT-037 | fd7d10d40cf7 | 2adb94e11196 | 4b9ed237125e | ca027d2687d9 | 7f530082d7d5 | 314bb569fa65 | 3cccebdcc3df | 2026-10-13T08:02:13Z | 2026-10-13T08:08:24Z | completo |
| BTCUSDT-V35 | fd7d10d40cf7 | 2adb94e11196 | 4b9ed237125e | ca027d2687d9 | 7f530082d7d5 | 314bb569fa65 | 3cccebdcc3df | 2026-10-13T08:02:13Z | 2026-10-13T08:08:52Z | completo |
| ETCUSDT-033 | b0b66f4d0dd9 | 2adb94e11196 | 4b9ed237125e | ca027d2687d9 | 7f530082d7d5 | 314bb569fa65 | 3cccebdcc3df | 2026-10-13T08:03:53Z | 2026-10-13T08:07:12Z | completo |
| SOLUSDT-023 | b0b66f4d0dd9 | 2adb94e11196 | 4b9ed237125e | ca027d2687d9 | 7f530082d7d5 | 314bb569fa65 | 3cccebdcc3df | 2026-10-13T08:04:13Z | 2026-10-13T08:09:37Z | completo |
| AVAXUSDT-V-12 | b0b66f4d0dd9 | 2adb94e11196 | 4b9ed237125e | ca027d2687d9 | 7f530082d7d5 | 314bb569fa65 | 3cccebdcc3df | 2026-10-13T08:07:13Z | 2026-10-13T08:10:01Z | completo |
| FILUSDT-016 | b0b66f4d0dd9 | 2adb94e11196 | 4b9ed237125e | ca027d2687d9 | 7f530082d7d5 | 314bb569fa65 | 3cccebdcc3df | 2026-10-13T08:08:28Z | 2026-10-13T08:09:53Z | completo |
| DYDXUSDT-008 | b0b66f4d0dd9 | 2adb94e11196 | 4b9ed237125e | ca027d2687d9 | 7f530082d7d5 | 314bb569fa65 | 3cccebdcc3df | 2026-10-13T08:08:53Z | 2026-10-13T08:26:14Z | completo |

## 4. Parità M (sezione 5, punto 1)

| Strategia | Periodo | Fonte | Trade | R medio | PF | (b) media | t | p | Esito |
|---|---|---|---|---|---|---|---|---|---|
| BTCUSDT-V10 | costruzione | log riga 26 (BTCUSDT-V10) | 300 / 300 | 0.1488 / 0.148849 | 1.3615 / 1.36152 | -0.30645 / -0.306452 | 2.35384 / 2.35384 | 0.00994 / 0.00994293 | PASSATA |
| BTCUSDT-V10 | validazione | log riga 203 (BTCUSDT-V10-VAL) | 136 / 136 | 0.048 / 0.047997 | 1.128 / 1.12805 | -0.56998 / -0.569985 | 1.69024 / 1.69024 | 0.047815252205714295 / 0.0478153 | PASSATA |
| BNBUSDT-045 | costruzione | log riga 190 (BNBUSDT-045) | 74 / 74 | 0.138052 / 0.138052 | 2.758430 / 2.75843 | -0.047778 / -0.047778 | 3.963275 / 3.96328 | 0.000308 / 0.000308117 | PASSATA |
| BNBUSDT-045 | validazione | log riga 236 (BNBUSDT-045-validazione) | 32 / 32 | 0.047296 / 0.0472963 | 1.489735 / 1.48973 | -0.092328 / -0.092328 | 2.138675 / 2.13867 | 0.030576 / 0.0305765 | PASSATA |
| ADAUSDT-037 | costruzione | log riga 109 (ADAUSDT-037) | 178 / 178 | 0.25200700651574104 / 0.252007 | 1.423727484579257 / 1.42373 | -0.1370904272244546 / -0.13709 | 2.5116379195444236 / 2.51164 | 0.007926403244850366 / 0.0079264 | PASSATA |
| ADAUSDT-037 | validazione | log riga 152 (ADAUSDT-037-V06) | 82 / 82 | 0.6240172173607658 / 0.624017 | 2.146539846549591 / 2.14654 | -0.31187733743050644 / -0.311877 | 2.2848421361158127 / 2.28484 | 0.0138509429924179 / 0.0138509 | PASSATA |
| BTCUSDT-V35 | costruzione | log riga 77 (BTCUSDT-V35) | 141 / 141 | 0.0454 / 0.0453613 | 1.3326 / 1.33263 | -0.12083 / -0.120829 | 3.57732 / 3.57732 | 0.00024 / 0.000238649 | PASSATA |
| ETCUSDT-033 | costruzione | log riga 71 (ETCUSDT-033) | 124 / 124 | 0.017702628898496067 / 0.0177026 | 1.1461138850678347 / 1.14611 | -0.08953153608616223 / -0.0895315 | 3.6221673028569312 / 3.62217 | 0.00021280151378073067 / 0.000212802 | PASSATA |
| SOLUSDT-023 | costruzione | log riga 95 (SOLUSDT-023) | 193 / 193 | 0.0170 / 0.0170157 | 1.1462 / 1.14617 | -0.04629 / -0.0462872 | 2.77889 / 2.77889 | 0.00329 / 0.00328722 | PASSATA |
| AVAXUSDT-V-12 | costruzione | log riga 54 (AVAXUSDT-V12) e risultati/V-12.json | 376 / 376 | 0.0072 / 0.00716342 | 1.0528 / 1.05278 | -0.055999 / -0.055999 | 3.523072 / 3.52307 | 0.000268 / 0.000268071 | PASSATA |
| FILUSDT-016 | costruzione | log riga 37 (FILUSDT-016) | 426 / 426 | 0.067279 / 0.0672789 | 1.135196 / 1.1352 | -0.080667 / -0.0806667 | 2.350746 / 2.35075 | 0.010302 / 0.0103017 | PASSATA |
| DYDXUSDT-008 | costruzione | log riga 27 (DYDXUSDT-008) | 161 / 161 | 0.060413258867768826 / 0.0604133 | 1.3409425715852454 / 1.34094 | -0.03837480627129526 / -0.0383748 | 2.2168935870928923 / 2.21689 | 0.016264800244890458 / 0.0162648 | PASSATA |
| DYDXUSDT-008 | validazione | log riga 121 (DYDXUSDT-008-VAL) | 83 / 83 | -0.17752228756173585 / -0.177522 | 0.4310616459825442 / 0.431062 | -0.05284820531076887 / -0.0528482 | -1.959243109934988 / -1.95924 | 0.9675382187608197 / 0.967538 | PASSATA |

Ogni cella: numero del log della campagna / numero rifatto oggi. Tolleranza: metà dell'ultima cifra del log.

## 5.1. Le corse — periodo «costruzione»

| Strategia | M trade | L eseguiti / saltati | tasso | R netto M / L | R lordo M / L | costo M / L | risparmio | R in M dei saltati | t vs (b): M / L | PF M / L | senza 3 M / L |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BTCUSDT-V10 | 300 | 295 / 5 | 98% | +0.1488 / +0.1606 | +0.2210 / +0.2137 | +0.0548 / +0.0365 | +0.0183 | +0.6133 (5) | +2.35 / +1.59 | +1.362 / +1.393 | +0.0818 / +0.0913 |
| BNBUSDT-045 | 74 | 74 / 0 | 100% | +0.1381 / +0.1561 | +0.1864 / +0.1878 | +0.0473 / +0.0307 | +0.0166 | — (0) | +3.96 / +4.04 | +2.758 / +3.106 | +0.1200 / +0.1385 |
| ADAUSDT-037 | 178 | 171 / 8 | 96% | +0.2520 / +0.2339 | +0.3427 / +0.3003 | +0.0653 / +0.0410 | +0.0243 | +0.9562 (8) | +2.51 / +2.22 | +1.424 / +1.394 | +0.1094 / +0.0838 |
| BTCUSDT-V35 | 141 | 139 / 2 | 99% | +0.0454 / +0.0814 | +0.1651 / +0.1624 | +0.1187 / +0.0799 | +0.0388 | +0.3438 (2) | +3.58 / +3.78 | +1.333 / +1.689 | +0.0169 / +0.0522 |
| ETCUSDT-033 | 124 | 121 / 3 | 98% | +0.0177 / +0.0340 | +0.0793 / +0.0728 | +0.0575 / +0.0350 | +0.0225 | +0.3157 (3) | +3.62 / +3.19 | +1.146 / +1.311 | -0.0054 / +0.0101 |
| SOLUSDT-023 | 193 | 190 / 3 | 98% | +0.0170 / +0.0273 | +0.0713 / +0.0651 | +0.0499 / +0.0334 | +0.0165 | +0.3614 (3) | +2.78 / +2.78 | +1.146 / +1.250 | +0.0002 / +0.0103 |
| AVAXUSDT-V-12 | 376 | 366 / 10 | 97% | +0.0072 / +0.0186 | +0.0667 / +0.0583 | +0.0559 / +0.0360 | +0.0199 | +0.3046 (10) | +3.52 / +3.45 | +1.053 / +1.156 | -0.0078 / +0.0029 |
| FILUSDT-016 | 426 | 425 / 9 | 98% | +0.0673 / +0.0727 | +0.1362 / +0.1214 | +0.0580 / +0.0377 | +0.0203 | +0.6726 (9) | +2.35 / +2.19 | +1.135 / +1.146 | +0.0158 / +0.0213 |
| DYDXUSDT-008 | 161 | 156 / 5 | 97% | +0.0604 / +0.0699 | +0.0963 / +0.0936 | +0.0347 / +0.0225 | +0.0123 | +0.2460 (5) | +2.22 / +2.33 | +1.341 / +1.398 | +0.0163 / +0.0242 |

Varianti della sezione 4.6, periodo «costruzione», solo in L (si riportano, non decidono):

| Strategia | (a) toccato: eseguiti/saltati, tasso, R netto, lordo, costo | (b) due barre: eseguiti/saltati, tasso, R netto, lordo, costo | (c) uscite a limite: eseguiti, uscite a limite, R netto, lordo, costo |
|---|---|---|---|
| BTCUSDT-V10 | 298/2, 99%, +0.1723, +0.2265, +0.0367 | 296/4, 99%, +0.1564, +0.2096, +0.0367 | 295, 218, +0.1671, +0.2067, +0.0230 |
| BNBUSDT-045 | 74/0, 100%, +0.1561, +0.1878, +0.0307 | 74/0, 100%, +0.1561, +0.1878, +0.0307 | 74, 69, +0.1666, +0.1822, +0.0146 |
| ADAUSDT-037 | 175/3, 98%, +0.2705, +0.3372, +0.0415 | 171/8, 96%, +0.2339, +0.3003, +0.0410 | 171, 101, +0.2448, +0.2996, +0.0294 |
| BTCUSDT-V35 | 141/0, 100%, +0.0857, +0.1667, +0.0799 | 140/1, 99%, +0.0858, +0.1668, +0.0799 | 139, 128, +0.0656, +0.1098, +0.0432 |
| ETCUSDT-033 | 124/0, 100%, +0.0417, +0.0809, +0.0351 | 122/2, 98%, +0.0325, +0.0716, +0.0351 | 121, 114, +0.0105, +0.0277, +0.0134 |
| SOLUSDT-023 | 191/2, 99%, +0.0305, +0.0684, +0.0334 | 191/2, 99%, +0.0288, +0.0666, +0.0334 | 190, 185, +0.0299, +0.0514, +0.0172 |
| AVAXUSDT-V-12 | 373/3, 99%, +0.0243, +0.0643, +0.0363 | 368/8, 98%, +0.0181, +0.0579, +0.0361 | 366, 352, +0.0205, +0.0412, +0.0172 |
| FILUSDT-016 | 425/7, 98%, +0.0767, +0.1253, +0.0377 | 426/1, 100%, +0.0738, +0.1226, +0.0378 | 425, 287, +0.0778, +0.1124, +0.0239 |
| DYDXUSDT-008 | 159/2, 99%, +0.0761, +0.0998, +0.0226 | 158/3, 98%, +0.0726, +0.0962, +0.0225 | 156, 142, +0.0637, +0.0760, +0.0112 |

## 5.2. Le corse — periodo «validazione»

| Strategia | M trade | L eseguiti / saltati | tasso | R netto M / L | R lordo M / L | costo M / L | risparmio | R in M dei saltati | t vs (b): M / L | PF M / L | senza 3 M / L |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BTCUSDT-V10 | 136 | 133 / 3 | 98% | +0.0480 / +0.0196 | +0.1489 / +0.0890 | +0.0943 / +0.0627 | +0.0316 | +2.6335 (3) | +1.69 / +1.63 | +1.128 / +1.080 | -0.1002 / -0.1074 |
| BNBUSDT-045 | 32 | 31 / 1 | 97% | +0.0473 / +0.0698 | +0.1238 / +0.1191 | +0.0793 / +0.0522 | +0.0271 | +0.2528 (1) | +2.14 / +2.03 | +1.490 / +1.759 | +0.0075 / +0.0280 |
| ADAUSDT-037 | 82 | 80 / 5 | 94% | +0.6240 / +0.6162 | +0.7467 / +0.6994 | +0.1111 / +0.0719 | +0.0392 | +1.4770 (4) | +2.28 / +2.11 | +2.147 / +2.118 | +0.0137 / -0.0190 |
| BTCUSDT-V35 | 105 | 102 / 3 | 97% | -0.1396 / -0.1041 | -0.0205 / -0.0239 | +0.1188 / +0.0800 | +0.0388 | -0.0333 (3) | -0.54 / -0.47 | +0.133 / +0.218 | -0.1583 / -0.1237 |
| ETCUSDT-033 | 25 | 25 / 0 | 100% | -0.0982 / -0.0660 | -0.0103 / -0.0103 | +0.0838 / +0.0515 | +0.0323 | — (0) | +1.17 / +0.83 | +0.334 / +0.477 | -0.1458 / -0.1144 |
| SOLUSDT-023 | 83 | 82 / 1 | 99% | -0.0328 / -0.0133 | +0.0499 / +0.0435 | +0.0796 / +0.0535 | +0.0261 | +0.5136 (1) | +1.12 / +1.18 | +0.730 / +0.873 | -0.0822 / -0.0624 |
| AVAXUSDT-V-12 | 171 | 168 / 3 | 98% | -0.0861 / -0.0522 | +0.0248 / +0.0215 | +0.1077 / +0.0704 | +0.0373 | +0.0514 (3) | +0.59 / +0.76 | +0.426 / +0.581 | -0.1208 / -0.0881 |
| FILUSDT-016 | 57 | 56 / 4 | 93% | +0.2282 / +0.1669 | +0.3113 / +0.2228 | +0.0770 / +0.0499 | +0.0271 | +1.6955 (4) | +1.56 / +1.08 | +1.483 / +1.341 | -0.0356 / -0.0818 |
| DYDXUSDT-008 | 83 | 82 / 3 | 96% | -0.1775 / -0.1713 | -0.1181 / -0.1315 | +0.0570 / +0.0372 | +0.0198 | +0.0843 (3) | -1.96 / -1.98 | +0.431 / +0.447 | -0.2433 / -0.2392 |

Varianti della sezione 4.6, periodo «validazione», solo in L (si riportano, non decidono):

| Strategia | (a) toccato: eseguiti/saltati, tasso, R netto, lordo, costo | (b) due barre: eseguiti/saltati, tasso, R netto, lordo, costo | (c) uscite a limite: eseguiti, uscite a limite, R netto, lordo, costo |
|---|---|---|---|
| BTCUSDT-V10 | 136/0, 100%, +0.0798, +0.1501, +0.0637 | 135/1, 99%, +0.0127, +0.0819, +0.0627 | 133, 93, +0.0285, +0.0800, +0.0448 |
| BNBUSDT-045 | 32/0, 100%, +0.0762, +0.1251, +0.0517 | 31/1, 97%, +0.0698, +0.1191, +0.0522 | 31, 28, +0.0958, +0.1192, +0.0263 |
| ADAUSDT-037 | 82/0, 100%, +0.6757, +0.7604, +0.0730 | 80/4, 95%, +0.6161, +0.6994, +0.0720 | 80, 43, +0.6329, +0.6959, +0.0516 |
| BTCUSDT-V35 | 105/0, 100%, -0.1010, -0.0207, +0.0800 | 103/2, 98%, -0.1023, -0.0220, +0.0800 | 102, 98, -0.0789, -0.0370, +0.0416 |
| ETCUSDT-033 | 25/0, 100%, -0.0660, -0.0103, +0.0515 | 25/0, 100%, -0.0660, -0.0103, +0.0515 | 25, 25, -0.0324, -0.0110, +0.0172 |
| SOLUSDT-023 | 83/0, 100%, -0.0066, +0.0501, +0.0535 | 82/1, 99%, -0.0133, +0.0435, +0.0535 | 82, 82, -0.0112, +0.0188, +0.0268 |
| AVAXUSDT-V-12 | 170/1, 99%, -0.0501, +0.0238, +0.0706 | 168/3, 98%, -0.0522, +0.0215, +0.0704 | 168, 165, -0.0515, -0.0165, +0.0317 |
| FILUSDT-016 | 56/2, 97%, +0.1736, +0.2297, +0.0500 | 56/2, 97%, +0.1669, +0.2228, +0.0499 | 56, 38, +0.1837, +0.2204, +0.0307 |
| DYDXUSDT-008 | 83/0, 100%, -0.1577, -0.1181, +0.0371 | 82/1, 99%, -0.1713, -0.1315, +0.0372 | 82, 69, -0.1692, -0.1465, +0.0202 |

## 5.3. Le corse — periodo «intero»

| Strategia | M trade | L eseguiti / saltati | tasso | R netto M / L | R lordo M / L | costo M / L | risparmio | R in M dei saltati | t vs (b): M / L | PF M / L | senza 3 M / L |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BTCUSDT-V10 | 436 | 428 / 8 | 98% | +0.1174 / +0.1168 | +0.1985 / +0.1749 | +0.0671 / +0.0446 | +0.0225 | +1.3709 (8) | +3.05 / +2.24 | +1.281 / +1.286 | +0.0549 / +0.0598 |
| BNBUSDT-045 | 106 | 105 / 1 | 99% | +0.1107 / +0.1306 | +0.1675 / +0.1675 | +0.0570 / +0.0370 | +0.0199 | +0.2528 (1) | +4.77 / +4.80 | +2.304 / +2.626 | +0.0973 / +0.1172 |
| ADAUSDT-037 | 260 | 251 / 13 | 95% | +0.3693 / +0.3557 | +0.4701 / +0.4275 | +0.0797 / +0.0508 | +0.0289 | +1.1298 (12) | +3.47 / +3.24 | +1.705 / +1.672 | +0.1581 / +0.1328 |
| BTCUSDT-V35 | 246 | 241 / 5 | 98% | -0.0336 / +0.0029 | +0.0859 / +0.0836 | +0.1188 / +0.0800 | +0.0388 | +0.1175 (5) | +2.93 / +3.12 | +0.777 / +1.017 | -0.0507 / -0.0148 |
| ETCUSDT-033 | 149 | 146 / 3 | 98% | -0.0017 / +0.0169 | +0.0643 / +0.0586 | +0.0619 / +0.0378 | +0.0241 | +0.3157 (3) | +4.18 / +3.54 | +0.979 / +1.146 | -0.0213 / -0.0032 |
| SOLUSDT-023 | 276 | 272 / 4 | 99% | +0.0020 / +0.0150 | +0.0649 / +0.0586 | +0.0588 / +0.0394 | +0.0194 | +0.3994 (4) | +2.96 / +2.98 | +1.012 / +1.133 | -0.0145 / -0.0020 |
| AVAXUSDT-V-12 | 547 | 534 / 13 | 98% | -0.0220 / -0.0036 | +0.0536 / +0.0467 | +0.0721 / +0.0468 | +0.0253 | +0.2462 (13) | +3.06 / +3.13 | +0.837 / +0.968 | -0.0378 / -0.0202 |
| FILUSDT-016 | 483 | 481 / 13 | 97% | +0.0863 / +0.0837 | +0.1568 / +0.1332 | +0.0603 / +0.0391 | +0.0212 | +0.9873 (13) | +2.70 / +2.43 | +1.185 / +1.173 | +0.0366 / +0.0336 |
| DYDXUSDT-008 | 244 | 238 / 8 | 97% | -0.0205 / -0.0132 | +0.0234 / +0.0160 | +0.0423 / +0.0275 | +0.0148 | +0.1854 (8) | +0.56 / +0.59 | +0.904 / +0.936 | -0.0543 / -0.0481 |

Varianti della sezione 4.6, periodo «intero», solo in L (si riportano, non decidono):

| Strategia | (a) toccato: eseguiti/saltati, tasso, R netto, lordo, costo | (b) due barre: eseguiti/saltati, tasso, R netto, lordo, costo | (c) uscite a limite: eseguiti, uscite a limite, R netto, lordo, costo |
|---|---|---|---|
| BTCUSDT-V10 | 434/2, 100%, +0.1433, +0.2026, +0.0451 | 431/5, 99%, +0.1114, +0.1696, +0.0448 | 428, 311, +0.1240, +0.1673, +0.0298 |
| BNBUSDT-045 | 106/0, 100%, +0.1320, +0.1689, +0.0370 | 105/1, 99%, +0.1306, +0.1675, +0.0370 | 105, 97, +0.1457, +0.1636, +0.0180 |
| ADAUSDT-037 | 257/3, 99%, +0.3998, +0.4722, +0.0515 | 251/12, 95%, +0.3557, +0.4275, +0.0508 | 251, 144, +0.3685, +0.4259, +0.0365 |
| BTCUSDT-V35 | 246/0, 100%, +0.0061, +0.0867, +0.0800 | 243/3, 99%, +0.0061, +0.0867, +0.0800 | 241, 226, +0.0045, +0.0477, +0.0425 |
| ETCUSDT-033 | 149/0, 100%, +0.0236, +0.0656, +0.0378 | 147/2, 99%, +0.0157, +0.0577, +0.0379 | 146, 139, +0.0032, +0.0211, +0.0140 |
| SOLUSDT-023 | 274/2, 99%, +0.0193, +0.0628, +0.0395 | 273/3, 99%, +0.0161, +0.0597, +0.0394 | 272, 267, +0.0175, +0.0416, +0.0201 |
| AVAXUSDT-V-12 | 543/4, 99%, +0.0010, +0.0516, +0.0471 | 536/11, 98%, -0.0039, +0.0465, +0.0468 | 534, 518, -0.0020, +0.0230, +0.0217 |
| FILUSDT-016 | 481/9, 98%, +0.0879, +0.1375, +0.0391 | 482/3, 99%, +0.0846, +0.1342, +0.0392 | 481, 325, +0.0901, +0.1250, +0.0247 |
| DYDXUSDT-008 | 242/2, 99%, -0.0041, +0.0251, +0.0275 | 240/4, 98%, -0.0107, +0.0184, +0.0275 | 238, 211, -0.0166, -0.0007, +0.0143 |

## 6. R medio per anno (periodo intero 2020-2023), M / L

| Strategia | 2020: R netto M / L (trade M / L) | 2021: R netto M / L (trade M / L) | 2022: R netto M / L (trade M / L) | 2023: R netto M / L (trade M / L) |
|---|---|---|---|---|
| BTCUSDT-V10 | +0.3447 / +0.3781 (115 / 112) | +0.0151 / +0.0276 (113 / 112) | +0.0356 / +0.0263 (91 / 90) | +0.0563 / +0.0191 (117 / 114) |
| BNBUSDT-045 | +0.1706 / +0.1894 (21 / 21) | +0.1838 / +0.1984 (34 / 34) | +0.0101 / +0.0332 (23 / 23) | +0.0594 / +0.0827 (28 / 27) |
| ADAUSDT-037 | +0.3991 / +0.3736 (63 / 59) | +0.3045 / +0.3442 (74 / 73) | -0.1690 / -0.2651 (49 / 47) | +0.7653 / +0.7581 (74 / 72) |
| BTCUSDT-V35 | — | +0.0806 / +0.1187 (64 / 63) | -0.0271 / +0.0073 (91 / 90) | -0.1203 / -0.0845 (91 / 88) |
| ETCUSDT-033 | +0.0470 / +0.0420 (26 / 25) | +0.0198 / +0.0429 (56 / 56) | -0.0401 / -0.0205 (50 / 48) | -0.0347 / -0.0000 (17 / 17) |
| SOLUSDT-023 | -0.0269 / -0.0215 (9 / 9) | +0.0514 / +0.0598 (75 / 73) | -0.0030 / +0.0093 (109 / 108) | -0.0328 / -0.0133 (83 / 82) |
| AVAXUSDT-V-12 | -0.1379 / -0.1553 (17 / 16) | +0.0254 / +0.0339 (167 / 164) | +0.0041 / +0.0201 (192 / 186) | -0.0861 / -0.0522 (171 / 168) |
| FILUSDT-016 | -0.1344 / -0.1071 (58 / 58) | +0.1435 / +0.1530 (248 / 247) | +0.0073 / -0.0057 (120 / 120) | +0.2282 / +0.1669 (57 / 56) |
| DYDXUSDT-008 | — | +0.0734 / +0.0888 (41 / 40) | +0.0022 / +0.0070 (92 / 89) | -0.0741 / -0.0670 (111 / 109) |

## 7. Le soglie E1, E2, E3 (sezione 7), sulle mediane delle strategie — periodo intero

Strategie con L completa: 9 su 9 (BTCUSDT-V10, BNBUSDT-045, ADAUSDT-037, BTCUSDT-V35, ETCUSDT-033, SOLUSDT-023, AVAXUSDT-V-12, FILUSDT-016, DYDXUSDT-008).

* **E1, eseguibile**: tasso di esecuzione mediano 98.0% (soglia 70%; sotto il 50% «non eseguibile») → vale.
* **E2, i costi scendono**: risparmio mediano del costo medio +0.0225 R (soglia 0,04 R) → cade.
* **E3, il lordo regge**: differenza mediana del lordo L − M -0.0069 R, contro −0,5 × risparmio = -0.0112 R → vale.

**Esito secondo le soglie scritte prima: «conviene poco».**

Mediane per strategia (periodo intero): tasso, risparmio, differenza del lordo:

* BTCUSDT-V10: tasso 98.2%, risparmio +0.0225 R, lordo L − M -0.0236 R
* BNBUSDT-045: tasso 99.1%, risparmio +0.0199 R, lordo L − M +0.0001 R
* ADAUSDT-037: tasso 95.1%, risparmio +0.0289 R, lordo L − M -0.0427 R
* BTCUSDT-V35: tasso 98.0%, risparmio +0.0388 R, lordo L − M -0.0023 R
* ETCUSDT-033: tasso 98.0%, risparmio +0.0241 R, lordo L − M -0.0057 R
* SOLUSDT-023: tasso 98.6%, risparmio +0.0194 R, lordo L − M -0.0063 R
* AVAXUSDT-V-12: tasso 97.6%, risparmio +0.0253 R, lordo L − M -0.0069 R
* FILUSDT-016: tasso 97.4%, risparmio +0.0212 R, lordo L − M -0.0236 R
* DYDXUSDT-008: tasso 96.7%, risparmio +0.0148 R, lordo L − M -0.0074 R

## 8. Informazione, non promozione: in validazione, strategie con R netto > 0 che battono nettamente la (b)-L

1 strategie.

* BTCUSDT-V10: M R +0.0480 t +1.69 netta False; L R +0.0196 t +1.63 netta False → no
* BNBUSDT-045: M R +0.0473 t +2.14 netta False; L R +0.0698 t +2.03 netta False → no
* ADAUSDT-037: M R +0.6240 t +2.28 netta True; L R +0.6162 t +2.11 netta True → sì
* BTCUSDT-V35: M R -0.1396 t -0.54 netta False; L R -0.1041 t -0.47 netta False → no
* ETCUSDT-033: M R -0.0982 t +1.17 netta False; L R -0.0660 t +0.83 netta False → no
* SOLUSDT-023: M R -0.0328 t +1.12 netta False; L R -0.0133 t +1.18 netta False → no
* AVAXUSDT-V-12: M R -0.0861 t +0.59 netta False; L R -0.0522 t +0.76 netta False → no
* FILUSDT-016: M R +0.2282 t +1.56 netta False; L R +0.1669 t +1.08 netta False → no
* DYDXUSDT-008: M R -0.1775 t -1.96 netta False; L R -0.1713 t -1.98 netta False → no
