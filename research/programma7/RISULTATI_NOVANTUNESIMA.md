# Prova 153: il libro degli ordini fra le monete (risultati)

### Riepilogo
Esito secondo l'esame scritto prima: **non promettente** per entrambe le varianti (netto negativo, nessun anno positivo per tutti e quattro, t sotto -2,4, lati long e short negativi senza i 10 giorni migliori). Il controllo al contrario è positivo solo per la variante A (+17,7% l'anno, Sharpe 0,68), ma il verso era fissato e non si rovescia: non è una prova, è un dato descrittivo.

### La prova come è scritta e scala di tempo
`research/programma7/NOVANTUNESIMA.md` (commit a01d561 e 1af4003, sezione «Regole corrette»). Scala: giornaliera (ordine alle 00:00 UTC, segnale del giorno D-1), Sharpe e t su settimane (52 l'anno). Periodo 2 gennaio 2023 - 4 ottobre 2026.
**Correzione dell'esame (12 novembre, revisione `audits/reports/2026-11-12-MAZZO_ASTICELLA.md`, commit 87d2b97)**: lo Sharpe corretto è `asticella.corretto_famiglie` (mazzo completo) e non `corretto_rivisto`, che conta solo le prove fino alla 48. Sostituito in `novantunesima.py` prima del calcolo; regole del resto invariate.

### Implementazione
`research/programma7/novantunesima.py` (non committato; commit di partenza ef29581). Riusa `aggrega_giorno`-stile per rilevazione (somma e numero per giorno), CHECKSUM verificato, `nucleo.passo_banda` con S al posto del funding, `nucleo.spese_limite`, `an.conto`. Seme 153 (nessuna parte casuale).
Scarico: 137.200 coppie moneta-giorno (100 monete, regola 9: 500 coppie in 85,1 s, stima 6,48 ore, sotto 10), scelta in `risultati_novantunesima/scelta.json`; riassunti in `riassunti.csv` con impronta per file; riprese: il contenitore si è riavviato due volte e lo scarico è ripreso dalle coppie già fatte. Presenti 136.736, **mancanti per l'archivio (404) 468**. Giorni con segnale 1.362 (il 2 gennaio 2023 non ha segnale: il file del 31 dicembre 2022 non esiste), monete medie al giorno 99,06.
Lettura mia: il segnale del giorno D usa il file di D-1 (coppie = moneta dell'universo di D, giorno D-1). Nel file `riassunti.csv` ci sono 4 righe in più della lista (coppie del primo giro di misura con la chiave sul giorno D, non usate dal segnale per le monete fuori universo).

### Varianti provate
2 (A: squilibrio entro il 5%; B: entro l'1%), registro `research/trials/novantunesima.csv`. Conto 312 -> 314. Il controllo al contrario non è una prova.

### Risultati (rendimento netto annuo = media settimanale x 52; Sharpe su settimane; Sharpe corretto per famiglie con `corretto_famiglie`)
| | A (5%) | B (1%) |
|---|---|---|
| rendimento netto l'anno | -40,9% | -26,4% |
| Sharpe / t | -1,59 / -3,09 | -1,26 / -2,45 |
| discesa più grande (settimane / giorni) | -83,1% / -83,8% | -72,4% / -72,7% |
| per anno 2023 / 2024 / 2025 / 2026 (parziale) | -36,3 / -21,5 / -95,5 / -0,4% | -26,2 / -26,7 / -39,6 / -8,6% |
| Sharpe corretto per famiglie | 0,00 (9e-11) | 0,00 (8e-9) |
| long l'anno (senza 10 giorni migliori) | +3,4% (-33,7%) | +11,1% (-23,2%) |
| short l'anno (senza 10 giorni migliori) | -44,6% (-79,4%) | -37,9% (-78,0%) |
| giro medio al giorno / spese l'anno / funding l'anno | 0,61 / 10,7% / 0,8% | 0,79 / 13,9% / 5,3% |
| variazioni, a ordine limite | 86.415, 84.459 | 87.216, 85.221 |
| netto con costi tripli l'anno | in `esame.json` | in `esame.json` |
| controllo al contrario: l'anno, Sharpe | +17,7%, 0,68 (2023 +2,6, 2024 -1,9, 2025 +82,3, 2026 -21,8) | -0,9%, -0,04 |
| correlazione con G1 (giorni / settimane) | -0,29 / -0,21 | -0,07 / +0,02 |
| correlazione con F5 (196 settimane) | -0,20 | -0,02 |
Esame: tutte le condizioni false per entrambe (netto positivo, ogni anno positivo, t almeno 3, Sharpe corretto almeno 0,80, lati senza i 10 giorni).

### Variante migliore e sensibilità
B è meno negativa di A, ma nessuna è vicina all'esame; A e B danno lo stesso segno, quindi non c'è una variante vicina che salvi la prova. Il t di A è -3,09: il segnale ha un verso sistematico (il contrario di A guadagna in 2025) ma con anni di segno diverso; rovesciarlo ora sarebbe una scelta dopo il risultato.

### Anomalie e possibili errori di motore o dati
Nessun errore di motore. 468 file mancanti nell'archivio (404). Il rendimento negativo grande è quasi tutto sul lato short. Le spese sono alte (giro 0,6-0,8 al giorno: il segnale cambia molto da un giorno all'altro).

### Varianti non previste che proporrei (non eseguite)
Il segnale al contrario di A come prova nuova (verso opposto fissato prima, con le sue regole e il conto delle prove); un segnale lento (media su 5 giorni) per ridurre il giro. Nessuna eseguita.

### Domande aperte
Nessuna sul calcolo. Sul contrario di A: va fatto come prova nuova solo se la sessione principale ritiene che la ragione economica lo regga.
File: `research/programma7/risultati_novantunesima/esame.json`, `riassunti.csv`, `scelta.json`.

Nota della sessione principale (12 novembre): nel repository il file dei riassunti giornalieri è compresso
(`risultati_novantunesima/riassunti.csv.gz`, 8,8 MB); per rifare il calcolo: `gunzip -k` del file, poi
`python3 -m research.programma7.novantunesima calcola`.
