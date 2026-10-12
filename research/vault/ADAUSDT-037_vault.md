# Vault di ADAUSDT-037 (Passo 5)

Candidato ADAUSDT-037 (long, 15 minuti: rottura dell'intervallo d'apertura con media a 20 giorni e BTC in calo nelle 24 ore). Trade contati se entrano dal 2024-01-01 00:00 UTC, fino al 2026-09-30. Scritto il 2026-10-11T21:35:18Z dal lanciatore `research/vault_strumenti/ADAUSDT.py` (SHA-256 ed89a4d0104762bae6345b7c562ee8f79c900a9a3df17ef328edf72b70064c98) con il codice del candidato (commit 47d6b2cc del branch della campagna). Python 3.11.17, numpy 1.26.4, scipy 1.13.0. Il JSON accanto, scritto prima di questo file, è il risultato completo.

## Esito: **NON PASSA**

Motivo: condizioni del criterio del vault non passate: profit_factor, rendimento_positivo, sopra_il_caso.

| condizione del criterio del vault | valore | soglia | passa |
|---|---|---|---|
| profit factor dopo i costi | 0,79 | almeno 1,10 | no |
| trade | 167 | almeno 30 | sì |
| rendimento totale (composto da 1000) | -26,3% | sopra zero | no |
| R medio a trade dopo i costi | -0,164 | sopra -0,086 (90° percentile delle 1000 entrate casuali) | no |

**Tasso del caso:** 15 strategie a entrate casuali su 1000 passano lo stesso criterio con lo stesso 90° percentile (1,5%). Stessa direzione (long), stesso numero di ingressi (167), distanza minima = durata media del candidato (32 barre da 15 minuti), stessa uscita, semi 0..999.

Quante delle 1000 passano ogni condizione: profit factor 15, trade minimi 1000, rendimento positivo 43, sopra il 90° percentile 100, tutte insieme 15. Simulazioni vuote 0; trade per simulazione in media 163,2 (minimo 154); R medio da -0,669 a 1,116, media -0,292. Il candidato sta al percentile 82,1 (indizio, non prova).

## Metriche del periodo (come nella consegna)

* Trade 167; R medio -0,164; senza i 3 migliori -0,305; profit factor 0,79; win rate 27%.
* Rendimento totale composto da 1000: -26,3% (capitale finale 736,7); drawdown massimo 34,5% (sui soli trade del periodo, dal capitale iniziale).
* Per anno d'uscita: 2024 R 0,092, 65 trade, rendimento +5,1%; 2025 R -0,329, 56 trade, rendimento -17,5%; 2026 R -0,326, 46 trade, rendimento -15,0%.
* Buy and hold per anno (contesto, long / short): 2024 +42% / -42%; 2025 -61% / +60%; 2026 -26% / +26%.
* Esiti: {'stop': 113, 'target': 0, 'segnale': 54, 'liquidazione': 0, 'fine_dati': 0}; stop medio 1,7%; stop oltre il 6% 0; durata media 8,1 ore; trade ridotti 0; violazioni di liquidazione 0.
* Baseline (a), solo per il rapporto: -0,972, t 1,77, netta no.
* Baseline (b) con 200 semi e contro_baseline come in validazione, solo per il rapporto: -0,284, t 0,72, netta no, p-value 0,2374, percentile del candidato 80,0.

## I dati del periodo, mese per mese (regola dei dati D1-D3, prima del candidato)

D1 (file mensili presenti e leggibili, prima di leggere le candele): 132 su 132 (2024-01 -> 2026-09). D2 (blocchi, prima del candidato): nessuno. Ultima barra allineata 2026-09-30 23:45 (attesa 2026-09-30 23:45), ultima di BTCUSDT 2026-09-30 23:45.

D3 (AVVISI, solo riportati: mesi sotto il 99% delle barre attese, barre di ADA senza BTC, settlement oltre l'intervallo dichiarato): ["2026-06: barre allineate al 96,7% (sotto il 99%: 96 tolte dal last perche' manca il mark, 0 tolte dal mark perche' manca il last)"].

| mese | barre attese | last | mark | allineate | quota | BTC | quota BTC | ADA senza BTC | settlement | intervalli osservati (ore: volte) | ore dichiarate | avviso |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024-01 | 2976 | 2976 | 2976 | 2976 | 1,0000 | 2976 | 1,0000 | 0 | 93 | 8: 93 | 8 |  |
| 2024-02 | 2784 | 2784 | 2784 | 2784 | 1,0000 | 2784 | 1,0000 | 0 | 87 | 8: 87 | 8 |  |
| 2024-03 | 2976 | 2976 | 2976 | 2976 | 1,0000 | 2976 | 1,0000 | 0 | 93 | 8: 93 | 8 |  |
| 2024-04 | 2880 | 2880 | 2880 | 2880 | 1,0000 | 2880 | 1,0000 | 0 | 90 | 8: 90 | 8 |  |
| 2024-05 | 2976 | 2976 | 2976 | 2976 | 1,0000 | 2976 | 1,0000 | 0 | 93 | 8: 93 | 8 |  |
| 2024-06 | 2880 | 2880 | 2880 | 2880 | 1,0000 | 2880 | 1,0000 | 0 | 90 | 8: 90 | 8 |  |
| 2024-07 | 2976 | 2976 | 2976 | 2976 | 1,0000 | 2976 | 1,0000 | 0 | 93 | 8: 93 | 8 |  |
| 2024-08 | 2976 | 2976 | 2976 | 2976 | 1,0000 | 2976 | 1,0000 | 0 | 93 | 8: 93 | 8 |  |
| 2024-09 | 2880 | 2880 | 2880 | 2880 | 1,0000 | 2880 | 1,0000 | 0 | 90 | 8: 90 | 8 |  |
| 2024-10 | 2976 | 2976 | 2976 | 2976 | 1,0000 | 2976 | 1,0000 | 0 | 93 | 8: 93 | 8 |  |
| 2024-11 | 2880 | 2880 | 2880 | 2880 | 1,0000 | 2880 | 1,0000 | 0 | 90 | 8: 90 | 8 |  |
| 2024-12 | 2976 | 2976 | 2976 | 2976 | 1,0000 | 2976 | 1,0000 | 0 | 93 | 8: 93 | 8 |  |
| 2025-01 | 2976 | 2976 | 2976 | 2976 | 1,0000 | 2976 | 1,0000 | 0 | 93 | 8: 93 | 8 |  |
| 2025-02 | 2688 | 2688 | 2688 | 2688 | 1,0000 | 2688 | 1,0000 | 0 | 84 | 8: 84 | 8 |  |
| 2025-03 | 2976 | 2976 | 2976 | 2976 | 1,0000 | 2976 | 1,0000 | 0 | 93 | 8: 93 | 8 |  |
| 2025-04 | 2880 | 2880 | 2880 | 2880 | 1,0000 | 2880 | 1,0000 | 0 | 90 | 8: 90 | 8 |  |
| 2025-05 | 2976 | 2976 | 2976 | 2976 | 1,0000 | 2976 | 1,0000 | 0 | 93 | 8: 93 | 8 |  |
| 2025-06 | 2880 | 2880 | 2880 | 2880 | 1,0000 | 2880 | 1,0000 | 0 | 90 | 8: 90 | 8 |  |
| 2025-07 | 2976 | 2976 | 2976 | 2976 | 1,0000 | 2976 | 1,0000 | 0 | 93 | 8: 93 | 8 |  |
| 2025-08 | 2976 | 2976 | 2976 | 2976 | 1,0000 | 2976 | 1,0000 | 0 | 93 | 8: 93 | 8 |  |
| 2025-09 | 2880 | 2880 | 2880 | 2880 | 1,0000 | 2880 | 1,0000 | 0 | 90 | 8: 90 | 8 |  |
| 2025-10 | 2976 | 2976 | 2976 | 2976 | 1,0000 | 2976 | 1,0000 | 0 | 93 | 8: 93 | 8 |  |
| 2025-11 | 2880 | 2880 | 2880 | 2880 | 1,0000 | 2880 | 1,0000 | 0 | 90 | 8: 90 | 8 |  |
| 2025-12 | 2976 | 2976 | 2976 | 2976 | 1,0000 | 2976 | 1,0000 | 0 | 93 | 8: 93 | 8 |  |
| 2026-01 | 2976 | 2976 | 2976 | 2976 | 1,0000 | 2976 | 1,0000 | 0 | 93 | 8: 93 | 8 |  |
| 2026-02 | 2688 | 2688 | 2688 | 2688 | 1,0000 | 2688 | 1,0000 | 0 | 84 | 8: 84 | 8 |  |
| 2026-03 | 2976 | 2976 | 2976 | 2976 | 1,0000 | 2976 | 1,0000 | 0 | 93 | 8: 93 | 8 |  |
| 2026-04 | 2880 | 2880 | 2880 | 2880 | 1,0000 | 2880 | 1,0000 | 0 | 90 | 8: 90 | 8 |  |
| 2026-05 | 2976 | 2976 | 2976 | 2976 | 1,0000 | 2976 | 1,0000 | 0 | 93 | 8: 93 | 8 |  |
| 2026-06 | 2880 | 2880 | 2784 | 2784 | 0,9667 | 2880 | 1,0000 | 0 | 90 | 8: 90 | 8 | AVVISO: barre allineate al 96,7% (sotto il 99%: 96 tolte dal last perche' manca il mark, 0 tolte dal mark perche' manca il last) |
| 2026-07 | 2976 | 2976 | 2976 | 2976 | 1,0000 | 2976 | 1,0000 | 0 | 93 | 8: 93 | 8 |  |
| 2026-08 | 2976 | 2976 | 2976 | 2976 | 1,0000 | 2976 | 1,0000 | 0 | 93 | 8: 93 | 8 |  |
| 2026-09 | 2880 | 2880 | 2880 | 2880 | 1,0000 | 2880 | 1,0000 | 0 | 90 | 8: 90 | 8 |  |

## Da dichiarare

* Ultima barra della serie allineata: 2026-09-30 23:45 (attesa 2026-09-30 23:45). Una posizione ancora aperta sull'ultima barra si chiude al close della barra delle 23:45 con esito fine_dati (la regola d'uscita direbbe all'apertura delle 00:00 del giorno dopo) e il settlement di funding delle 00:00 del giorno dopo non si conta. Trade chiusi cosi': 0; trade entrati l'ultimo giorno: 1.
* Nel periodo: 1 buchi nella serie allineata last/mark (96 barre mancanti); barre tolte dal last 96, dal mark 0; giorni con barre tolte ['2026-06-29']. Barre di ADA senza BTC: 0 (il rendimento di BTC a 24 ore del candidato si calcola 96 posizioni indietro nella serie: una barra senza BTC toglie il segnale in quella posizione e 96 posizioni dopo; con un buco, 96 posizioni indietro sono piu' di 24 ore). Sulla serie intera dal 2020 il motore conta 4 buchi e 0 settlement di funding caduti in un buco con posizione aperta: sono i numeri che il codice della campagna chiama buchi_dati e funding_in_buco.
* Mesi con meno del 99% delle barre allineate attese (AVVISO, D3; sotto il 50% il giro si sarebbe fermato prima del candidato, D2): ['2026-06'].
* Settlement di funding nel periodo: 3012; intervalli osservati fra un settlement e il precedente (ore: quante volte) {'8': 3012}; volte in cui fra due settlement passa piu' dell'intervallo dichiarato dai file: 0. Nessun mese senza settlement (altrimenti D2 avrebbe fermato il giro prima del candidato); nessun numero «atteso» costruito sull'intervallo piu' corto.
* Il blocco `come_validazione` del JSON porta «periodo»: «validazione» perché è l'uscita di `comune.valuta(periodo="validazione")` con le due costanti spostate in memoria; il periodo vero è quello scritto sopra.

## Controlli

* Le entrate casuali del tasso del caso ridanno la (b) della campagna sui semi 0..199: sì.
* Trade del candidato entrati prima del taglio nell'esecuzione: 0 (deve essere 0).
* Barre vietate alle entrate casuali (quota sulla serie dal 2020): 75,6%.
* Codice del candidato dopo il giro uguale a quello congelato: sì.
* Impronta d'avvio 312ac0a6dfe3b19dca2677248247085ec7e5f9d865546367c9790132713c503a; impronta del giro 3743db28c8c5e6cf40ac7153c0251f048cf734d6b7fd0ea4dd2f3d348899b2ec; ripresa di un giro interrotto: no.
* Semi: {'caso': [0, 999], 'baseline_b': [0, 199], 'bootstrap': {'ricampionamenti': 2000, 'seme': 0}, 'nota': 'i semi del caso e della (b) partono da 0: la (b) a 200 semi sono i primi 200 semi del caso'}.
* Tempi (secondi): {'carica': 7.7, 'indicatori': 5.9, 'candidato': 0.7, 'barre_vietate': 1.0, 'valuta': 44.6, 'simulazioni_caso': 163.9, 'pezzi_ripresi': 0, 'pezzi_calcolati': 20, 'totale_esame': 210.9}.
