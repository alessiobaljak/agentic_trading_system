# Programma 5: stato e registro delle idee

Regole: `REGOLE.md`. Aggiornato a ogni passo. **Strategie valide finora: 0** (servono 3 per scrivere al proprietario).

## Dove siamo

* 18 ott 2026, sera: regole scritte; dati delle 12 monete scaricati e verificati (candele da 1 minuto, `metrics`, funding,
  premio sullo spot a 1 ora).
* Le idee a 1 minuto (I-001 ... I-007) cadono tutte in C: a pochi minuti il lordo è vicino a zero contro costi di
  0,12-0,17%.
* Quattro esplorazioni a ore su C (REGOLE.md, 6bis): E-001 (13 celle promosse su 353), E-002 (11 su 96), E-003 (26 su
  185), E-004 (4 su 70). Le idee promosse I-010 ... I-016 passano C, ma **nessuna** supera V.
* **Cosa abbiamo capito**: (1) il fenomeno più forte e costante è il **rimbalzo dopo i crolli**: su C in tutti e tre gli
  anni e su 12 monete su 12, e anche su V (2023) **positivo dopo i costi in tutte e sei le varianti** di I-010 e I-016, ma
  senza la forza statistica richiesta (nel 2023 i crolli sono pochi); (2) E-004 dice **quali** crolli rimbalzano: quelli
  in cui il perpetuo scende sotto lo spot (premio nel 10% più basso): +1,36-1,43% in 4 ore, contro +0,12-0,55% dei crolli
  senza sconto, che nel 2022 continuano a scendere; (3) le idee di tendenza e di continuazione (I-011, I-013c, I-014) su V
  fanno quanto il caso: era il rialzo del mercato, non il segnale; (4) la scossa propria coperta con BTC (I-015) regge su C
  e cade su V.
* La soglia di V era troppo severa per idee a eventi rari dopo cui c'è anche R: corretta **per le idee nuove**
  (REGOLE.md, 6ter), con le idee parenti di un V positivo provate solo su R con la soglia severa.
* **I-017** (il rimbalzo dopo i crolli, prova solo su R): la candidata c4 (long dopo un crollo di 4 ore con z ≤ −5, 12
  ore) su R fa **+2,20% netto a trade** (211 trade), positivo nel 2024 (+3,13%), 2025 (+1,61%) e 2026 (+1,01%), a costi
  doppi (+2,03%), togliendo il giorno migliore (+1,77%) e su 12 monete su 12; ma p è **0,0037** contro la soglia 0,0017:
  **bruciata**. Il fenomeno è positivo in C, V e R, ma è raro (circa 75 trade l'anno su 12 monete, e i crolli arrivano
  insieme su tutte): con la storia che c'è non si può dimostrare alla soglia scelta. Lo dice il calcolo, non un'opinione.
* I-018: numero non usato (era la salita senza premio, rinviata).
* **E-005 e I-020** (scalping con ordini limite in entrata e in uscita: acquisto a 3σ sotto il prezzo, rivendita a 0,5-1σ
  sopra): su C netto +0,19-0,32% a trade su oltre 6.000 trade, 12 monete, t fino a 7; su V (costruzione) già sceso a
  +0,02-0,15%; su R (una volta) **zero**: −0,01% / +0,01% / +0,05%, intervalli intorno allo zero. **Bruciata.** Lezione:
  il vantaggio di chi fornisce liquidità nelle code delle candele era grande nel 2020-2021 e si è chiuso anno dopo anno
  (2022 piccolo, 2023 più piccolo, 2024-2026 niente): il mercato è diventato più efficiente nelle microstrutture. Le
  inefficienze di questo tipo vanno cercate sui dati recenti, non sul 2020-2021.

## Fase 2 (REGOLE.md, sezioni 7 e 7bis)

* 18 ott 2026, 16:45 UTC: periodi spostati sul recente (costruzione C2 = 2024-01 → 2025-06, prova V2 = 2025-07 →
  2026-09, una volta per idea); 12 monete nuove scelte con la regola (`universo_fase2.json`).
* 17:15 UTC, istruzione del proprietario: l'intero universo o almeno le 100 monete più scambiate. Universo esteso in
  `universo_top100.json` (regola scritta prima; le 24 della fase 2 tutte dentro); scarico dal settembre 2023 in corso.
* Esplorazioni scritte prima del calcolo: E-101, E-102, E-103 (24 monete) ed E-111, E-112, E-113 (100 monete). Le idee
  della fase 2 si chiamano J-NNN e si provano su V2 sulle 100 monete.
* Risultati sulle 24 monete (C2): E-101 31 celle promosse su 468, E-102 5 su 104, E-103 6 su 46. **Cosa abbiamo capito**:
  nel 2024-2025 i due fenomeni più forti sono (1) la **continuazione dopo le salite forti** (1-4 ore oltre 3σ: il prezzo
  continua a salire per 4-72 ore, su 22-24 monete su 24, in tutti e tre i semestri), che nel 2020-2022 non c'era; (2) il
  **rimbalzo dopo i crolli**, ancora più forte (+4,4-4,8% a trade su 24 ore, concentrato in pochi giorni: 5 mar, 13 apr,
  5 ago, 20 dic 2024; 3 feb, 7 apr 2025). Le reti d'acquisto a 6σ rendono ancora (+0,49-0,74% netto), quelle a 3σ meno.
* Idee J-001 ... J-010: tutte passano C2 (`idee/J-NNN/C2.md`); regole congelate con le impronte (commit `bba987e4`).
* **V2 (18 ott, 18:00-18:45 UTC, una volta per idea, sulle 100 monete o sulle 88 fuori dalla fase 1): nessuna delle dieci
  passa.** Il primo giro si è interrotto per un difetto tecnico (due calcoli in parallelo scrivevano lo stesso file di
  appoggio delle barre orarie) prima di scrivere qualunque risultato; i file sono stati ricostruiti in ordine e il calcolo
  rifatto identico (unica eccezione: una prova di un minuto su una moneta di J-002 prima del giro). **Cosa abbiamo
  capito**: (1) nei 15 mesi recenti la seconda metà del 2025 è andata male per i rimbalzi (J-004 −7,9% a trade nella
  variante b, J-006 −3,8%) e il 2026 bene per tutto ciò che è long; (2) le idee di continuazione restano positive (J-002
  +0,4-1,4%, J-005 +0,4-0,9%, J-001 +0,1-1,6%) ma **quanto un ingresso a caso nello stesso mese** (caso +0,2-1,9%): era il
  mercato, non il segnale; (3) la più vicina è J-005b (volume dieci volte il solito in un'ora in salita, long un giorno):
  +0,93% netto, intervallo +0,24; +1,63, tutte e due le metà positive, ma p 0,0030 contro 0,0025 e solo +0,26% sopra il
  caso; (4) le reti d'acquisto nelle code (J-009, J-010) e le idee di sessione (J-007, J-008) non reggono.

| Idea | Stato | C2: netto a trade (trade) — V2: netto, p, caso |
|---|---|---|
| J-001 | **bruciata in V2** | a +1.74% (360); b +0.80% (360); c +2.67% (286) — V2: a +0.51% (p 0.1096, caso +0.45%); b +0.11% (p 0.3599, caso +0.04%); c +1.57% (p 0.0109, caso +1.89%) |
| J-002 | **bruciata in V2** | a +3.87% (372); b +2.87% (772); c +1.27% (1628) — V2: a +1.40% (p 0.0957, caso +1.79%); b +0.78% (p 0.1553, caso +0.94%); c +0.43% (p 0.0747, caso +0.15%) |
| J-003 | **bruciata in V2** | a +1.06% (1454); b +1.50% (496); c +1.12% (876) — V2: a +0.21% (p 0.1722, caso +0.05%); b +0.11% (p 0.4015, caso +0.20%); c +0.38% (p 0.0354, caso +0.11%) |
| J-004 | **bruciata in V2** | a +4.67% (268); b +4.56% (252); c +4.36% (250) — V2: a +0.55% (p 0.3658, caso -0.35%); b -3.19% (p 0.9383, caso +0.34%); c +1.55% (p 0.0706, caso -0.33%) |
| J-005 | **bruciata in V2** | a +1.01% (1749); b +1.87% (430) — V2: a +0.44% (p 0.0413, caso +0.32%); b +0.93% (p 0.0030, caso +0.67%) |
| J-006 | **bruciata in V2** | a +4.79% (345); b +1.52% (527) — V2: a -0.66% (p 0.6105, caso +0.00%); b -0.45% (p 0.6694, caso -0.14%) |
| J-007 | **bruciata in V2** | a +0.34% (1556); b +0.69% (364) — V2: a -0.17% (p 0.9125, caso -0.09%); b +0.00% (p 0.5020, caso -0.03%) |
| J-008 | **bruciata in V2** | a +0.26% (1636); b +0.61% (393) — V2: a -0.24% (p 0.9792, caso -0.11%); b -0.32% (p 0.9553, caso -0.10%) |
| J-009 | **bruciata in V2** | a +0.49% (965); b +0.74% (901) — V2: a -0.09% (p 0.5376, caso -0.11%); b +0.26% (p 0.2946, caso -0.10%) |
| J-010 | **bruciata in V2** | a +2.58% (715); b +0.20% (5891); c +1.03% (3192) — V2: a +1.04% (p 0.1754, caso +0.06%); b +0.13% (p 0.1468, caso -0.09%); c +0.36% (p 0.1343, caso +0.07%) |

## Coda delle idee della fase 1 (in ordine)

| N. | Idea | Perché dovrebbe funzionare | Stato |
|---|---|---|---|
| I-001 | Rimbalzo dopo i crolli fatti di liquidazioni: crollo estremo a 5 minuti con l'interesse aperto che cala | le vendite forzate spingono il prezzo sotto il valore che i compratori pagano; la prima analisi ha visto il rimbalzo (`research/scalping/risultati.md`) | bruciata in C |
| I-002 | Il contrario dopo le salite estreme fatte di short liquidati (interesse aperto che cala) | come I-001, dalla parte opposta | bruciata in C |
| I-003 | Continuazione quando l'esplosione arriva con interesse aperto che cresce (posizioni nuove, non chiusure) | denaro nuovo che entra con una direzione | bruciata in C |
| I-004 | Rapporto long/short dei conti grandi agli estremi, orizzonte 1 giorno | la folla in un verso estremo paga chi sta dall'altra parte | bruciata in C |
| I-005 | Squilibrio degli acquisti aggressivi a 5 minuti durante un'esplosione | chi aggredisce ha informazione o fretta | bruciata in C |
| I-006 | Il prezzo intorno al regolamento del funding quando il funding è estremo | chi chiude prima di pagare il funding sposta il prezzo | bruciata in C |
| I-007 | Le monete dopo BTC al minuto: BTC esplode, le altre seguono in 1-5 minuti | il prezzo di BTC arriva prima nelle altre | bruciata in C |
| I-008 | Premio del perpetuo sullo spot estremo, ritorno nelle ore dopo | l'arbitraggio riporta il perpetuo verso lo spot | da fare |
| I-009 | Rottura dopo la calma con interesse aperto che cresce | la pressione accumulata si sfoga nella direzione delle posizioni nuove | da fare |

## Registro delle idee concluse

Numeri da `idee/I-NNN/C.md` e `V.md`: netto medio a trade dopo i costi (trade, p a una coda).

| N. | Esito | C | V | Motivo e lezione |
|---|---|---|---|---|
| I-001 | bruciata in C | a +0,11% (567, p 0,30); b −0,10% (2.887); c −0,02% (1.123) | — | il rimbalzo al minuto dopo i crolli con l'interesse aperto che cala non c'è nel periodo con il dato (quasi solo 2022) |
| I-002 | bruciata in C | a −0,29%; b −0,18%; c −0,25% | — | dopo le salite estreme al minuto il prezzo non torna indietro |
| I-003 | bruciata in C | a −0,18%; b −0,27%; c −0,64% | — | l'esplosione con interesse aperto che cresce non continua |
| I-004 | bruciata in C | a +0,35% (1.385, p 0,05); b −0,44%; c −0,10% | — | i rapporti long/short agli estremi a un giorno: intervallo che passa lo zero |
| I-005 | bruciata in C | a −0,16%; b −0,24%; c −0,16% | — | lo squilibrio degli acquisti aggressivi nell'esplosione non dice la direzione |
| I-006 | bruciata in C | a −0,18%; b −0,17%; c −0,17% | — | il regolamento del funding estremo non muove il prezzo più del caso |
| I-007 | bruciata in C | a −0,17%; b −0,16%; c −0,16% | — | le altre monete non restano indietro a BTC al minuto |
| I-010 | **bruciata in V di poco** | a +2,51% (283); b +1,56% (522); c +2,32% (327) | a +0,70% (97, p 0,12); b +0,53% (188, p 0,14); c +0,82% (74, p **0,0018**, soglia 0,0017) | il rimbalzo dopo i crolli di qualche ora c'è anche nel 2023, a costi doppi e su 9-11 monete su 12, ma con pochi eventi |
| I-011 | bruciata in V | +5,56% (327) | +1,47% (145, p 0,04), caso +2,55% | la rottura del massimo di 60 giorni fa meno del caso nel 2023: era il rialzo |
| I-012 | bruciata in V | a +0,31%; b +0,98% | a +0,04% (p 0,34); b +0,18% (p 0,19) | il volume enorme in discesa non basta a dire quali crolli rimbalzano |
| I-013 | bruciata in V | a +0,34%; b +0,80%; c +1,58% | a +0,00%; b −0,08%; c −0,00% | la scossa propria senza copertura nel 2023 non dà niente |
| I-014 | bruciata in V | +3,28% (658) | +1,32% (231, p 0,09), caso +1,36% | le altre monete dopo lo strappo di BTC fanno quanto il caso |
| I-015 | bruciata in V | a +0,31%; b +0,65%; c +0,62% | a −0,31%; b −0,58%; c −0,38% | la discesa propria coperta con BTC nel 2023 continua invece di tornare |
| I-017 | **bruciata in R di poco** | 7 candidate tutte positive (`C.md`) | costruzione: 7 su 7 positive (`V.md`) | R: c4 +2,20% (211, p **0,0037**, soglia 0,0017), positivo nei 3 anni, a costi doppi, senza il giorno migliore e su 12 monete su 12; c1 +0,44% (778, intervallo −0,12; +1,02); c2 +0,06% |
| I-020 | bruciata in R | a +0,19% (6.821); b +0,21% (6.649); c +0,32% (6.121), t fino a 7 | costruzione: +0,02% / +0,06% / +0,15% | R: −0,01% / +0,01% / +0,05% (intervalli intorno allo zero): lo scalping a limite nelle code non rende più dal 2024 |
| I-019 | bruciata in V | a +2,48%; b +0,84%; c +1,53% | a +0,12% (p 0,43); b −0,27%; c +0,16% | la salita propria coperta con BTC nel 2023 non continua |
| I-016 | **bruciata in V** | a +1,69% (916); b +0,81% (2.509); c +0,17% (6.713) | a +0,60% (435, p 0,047); b +0,28% (1.086, p 0,044); c +0,10% (2.619, p 0,040) | le reti d'acquisto sotto il prezzo guadagnano anche nel 2023 su 11 monete su 12, ma senza la forza richiesta |
