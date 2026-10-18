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

## Coda delle idee (in ordine)

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
| I-019 | bruciata in V | a +2,48%; b +0,84%; c +1,53% | a +0,12% (p 0,43); b −0,27%; c +0,16% | la salita propria coperta con BTC nel 2023 non continua |
| I-016 | **bruciata in V** | a +1,69% (916); b +0,81% (2.509); c +0,17% (6.713) | a +0,60% (435, p 0,047); b +0,28% (1.086, p 0,044); c +0,10% (2.619, p 0,040) | le reti d'acquisto sotto il prezzo guadagnano anche nel 2023 su 11 monete su 12, ma senza la forza richiesta |
