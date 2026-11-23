# Voce 12: cosa fa G1 dopo un crollo del Bitcoin (misura, 23 novembre 2026)

## Regole, scritte prima di guardare i numeri
* Passato: dal 1 gennaio 2021 al 4 ottobre 2026, motore e serie della prova 57 (`nucleo.pesi` con pesi fissi 1:1, come `voce12_venduto_2026.py`), un solo passaggio sull'intero periodo.
* Crollo: giorno e in cui la chiusura del Bitcoin e' almeno il 10% sotto la chiusura di 3 giorni prima. Si prende il primo; dopo un evento se ne ignorano altri per 14 giorni.
* Dopo: somma (non composta) del contributo giornaliero dei giorni e+1 .. e+h, con h = 1, 3, 7. Contributo = prezzo + funding - spese, sul peso di ogni moneta, diviso per lato (comprato peso>0, venduto peso<0; le spese di chiusura vanno al lato del giorno prima).
* Fasce per volume: posto della moneta per volume medio dei 30 giorni precedenti fra le monete in universo quel giorno: 1-10, 11-50, 51-100.
* Giorni normali: tutte le finestre di h giorni che partono da un giorno senza crollo nei 7 giorni prima; si confronta la media per finestra.
* Oscillazione: scarto fra gli eventi e errore della media (scarto / radice di n); quanti eventi sono positivi.
* Monete piccole che perdono di piu': contributo per unita' di peso tenuto (somma contributi / somma pesi) per fascia e lato, dopo il crollo contro normale.
* Nessuna regola provata: se esce un'idea, solo scritta nel piano.

## Risultati (script `voce12_rimbalzi.py`, dati in `voce12_rimbalzi_risultati.json`)
Eventi: **26** in 5,8 anni (primo 11 gen 2021). Somme in % del conto, non composte, media sugli eventi (errore della media; eventi positivi su 26), contro la media normale della stessa finestra.

| Dopo | G1 | comprato | venduto | venduto 1-10 | venduto 11-50 | venduto 51-100 |
|---|---|---|---|---|---|---|
| 1 giorno | +0,37 (±0,36; 17) normale +0,15 | -0,64 (±1,24; 14) | +1,01 (±1,37; 12) | +0,20 | +0,03 | +0,79 (±0,87) |
| 3 giorni | -0,06 (±0,53; 12) normale +0,44 | -2,01 (±1,77; 10) | +1,95 (±1,80; 15) | -0,17 | +1,09 | +1,02 (±0,93) |
| 7 giorni | -0,16 (±0,79; 13) normale +1,01 | -2,77 (±2,76; 10) | +2,60 (±2,69; 15) | +0,17 | +1,83 (±1,55) | +0,61 (±1,25) |

Normale a 7 giorni: comprato +0,95, venduto +0,05.
Per unita' di peso al giorno (punti base), venduto, 7 giorni dopo contro normale: 1-10 +18,9 / -47,8; 11-50 +66,5 / -18,5; 51-100 +18,1 / +11,1.

## Lettura
* **No: nei 26 crolli del passato le monete piccole vendute non perdono di piu'.** Il lato venduto guadagna dopo il crollo (+1,0, +2,0, +2,6 a 1, 3, 7 giorni), la fascia 51-100 resta positiva. Nessuna differenza e' netta: l'errore e' grande quanto la media (ad esempio venduto a 7 giorni +2,60 con errore 2,69).
* Quello che si vede e' sul lato comprato: -2,8 a 7 giorni contro +0,95 normale (10 eventi positivi su 26), anch'esso non netto. G1 intero e' a +0,37, -0,06, -0,16 contro +0,15, +0,44, +1,01: sotto il normale, non meno di zero.
* Il rimbalzo di domenica 22 novembre e' fuori dal passato (finisce al 4 ottobre): resta un caso in avanti, non un'abitudine misurata. Le perdite delle piccole vendute del 2026 (voce 12 del 12 novembre) non si spiegano con i crolli del Bitcoin.
* Limiti: 26 eventi, soglia scelta a priori (-10% in 3 giorni, 14 giorni fra eventi), niente altre soglie provate; il caso del 21 novembre (Bitcoin a circa 55.000) puo' non rientrare nella regola.

## Idea (non provata)
Nessuna regola sul lato venduto dopo i crolli: il passato non la sostiene. Semmai, da guardare con una nuova misura: il lato comprato dopo un crollo (-2,8 a 7 giorni, non netto); serve prima un perche' forte e regole scritte.
