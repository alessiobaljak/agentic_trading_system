# Consegna della campagna MASKUSDT (protocollo 4.5)

**Nessuna strategia valida trovata per questa moneta.** L'unico candidato della costruzione
(MASKUSDT-029) non supera l'asticella in validazione: p-value 0,29 contro il limite di 0,10
(esito provvisorio: lo conferma il coordinamento al Passo 4). Nessun candidato va al vault.

Il budget è stato usato per intero: 30 varianti testate su 30 (25 da 15 idee nuove con fonte,
5 ritocchi, tutti nella famiglia MASKUSDT-006), più 6 scarti sotto i trade minimi che non
consumano budget. Tutto il log è in `log.jsonl`; le ipotesi in `ipotesi.md`; i dati in
`fase0_dati.md`; il codice in `codice/`.

## Il candidato arrivato alla validazione: MASKUSDT-029

Regole complete in `candidati/MASKUSDT-029/regole.md`. In breve: MASKUSDT, 1 ora, solo short;
ingresso dopo una barra oraria con rendimento oltre +3 deviazioni (168 barre precedenti) e
ultimo funding regolato non negativo; stop 2 ATR(14), target 4 ATR, uscita dopo 12 barre;
rischio 1% del capitale, leva massima 2, margine isolato. Motivo economico: le impennate di
un'ora su una moneta media sono spesso liquidità che si esaurisce e rientrano; con funding
negativo sono più probabilmente chiusure forzate di short affollati, che possono continuare.

| | Costruzione (2021-08-27 → 2023-04-10) | Validazione (2023-04-11 → 2023-12-31) |
|---|---|---|
| Trade | 86 | 41 |
| R medio dopo i costi | +0,264 | +0,011 |
| R medio senza i 3 migliori | +0,201 | −0,138 |
| Profit factor | 1,69 | 1,01 |
| Drawdown massimo | −4,1% | −7,3% |
| Rendimento | +25,0% (2021 +7,3%, 2022 +15,3%, 2023 +1,1%) | +0,3% |
| R medio per anno (anno d'uscita) | 2021 +0,255 (28), 2022 +0,376 (38), 2023 +0,062 (20) | 2023 +0,011 (41) |
| Baseline (a), entrata a ogni barra | −0,041; `t` 2,72 su soglia 2,21: netta | −0,048; `t` 0,37: non netta |
| Baseline (b), entrata casuale | −0,047; `t` 2,85 su soglia 2,21: netta (p 0,007) | −0,073; `t` 0,56 su soglia 2,23: non netta (p 0,293) |
| Percentile fra le entrate casuali (indizio) | 100 | 73 |
| Buy and hold, short (contesto) | 2021 +8%, 2022 +83%, 2023 −174% | 2023 (aprile-dicembre) +36% |
| Trade ridotti dal tetto di leva | 0 | 0 |
| Violazioni della distanza dalla liquidazione | 0 | 0 |

**Verifiche della Fase 4 (costruzione), tutte superate con i criteri del protocollo** (nota
MASKUSDT-N008): robustezza ±20% su 6 parametri (11 casi su 12 contano, `t` positivo in tutti,
netto in 9); timeframe adiacenti (30 minuti `t` 0,33 positivo ma R medio −0,03; 2 ore sotto i
trade minimi); stabilità per anno; senza i 3 trade migliori; regola intra-barra opposta (nessuna
differenza); ritardo di una barra (`t` 1,85, sopra la metà); nessuna violazione di liquidazione;
costi doppi (R medio +0,22, `t` 2,95).

**Asticella** (Benjamini-Hochberg al 10%, m = 1): p-value 0,293 > 0,10, **non passa**.
Provvisorio: lo conferma il coordinamento.

**Rischi noti.** Il candidato è il migliore di 7 varianti della stessa famiglia e di 30 in tutto;
il filtro del funding e l'uscita a 12 barre sono venuti da ritocchi sulla costruzione; il 2023 di
costruzione era già debole; 32 trade su 86 hanno lo stop oltre il 6% che il bot accetta (la
versione con stop a 1,5 ATR, MASKUSDT-032, non era netta). La validazione dice che la parte
«vantaggio» della costruzione era con buona probabilità selezione e fortuna.

* Criterio del vault (non si applica: il candidato non ci va): profit factor ≥ 1,10, almeno 30
  trade, rendimento positivo, R medio sopra il 90° percentile delle entrate casuali.
* Trade al mese attesi in paper (dalla costruzione): 86 in circa 19,5 mesi ≈ 4,4 al mese; 50
  trade in circa 11 mesi. Non si applica.
* Il bot potrebbe eseguirlo: timeframe 1 ora presente nel bot, funding letto dal bot
  (`lastFundingRate`), ma lo stop supera spesso il 6% e servirebbe il percorso «coppia del
  protocollo» (`config/regole_dimensione.md`). Non si applica.
* Previsione per vault e trasferimento: non si applica.

## Riepilogo delle idee provate (costruzione)

| Idea | Varianti (t contro la (b)) | Esito |
|---|---|---|
| I-01 momento a 7 giorni, 4h | 001 L (−0,26), 002 S (−0,00) | nessun effetto |
| I-02 rottura del canale di 48 ore, 1h | 003 L (0,02), 004 S (1,26) | non netto |
| I-03 ritorno dopo barra estrema, 1h | 005 L (0,29), 006 S (1,54); ritocchi 028 (2,08), **029 (2,85, candidato)**, 030 (0,97), 031 (1,55), 032 (2,18) | candidato 029, bocciato in validazione |
| I-04 ritracciamento RSI 2, 1h | 007 L (1,02), 008 S (0,39) | non netto |
| I-05 funding estremo, 8h | 009 S scarto (12 trade), 010 L (1,38) | non netto |
| I-06 volume alto, 4h | 011 e 011b scarti (21 e 60 trade) | non testabile |
| I-07 scarico dopo il pump, 1h | 012 scarto (44), 012b (−0,38) | nessun effetto |
| I-08 ritardo su BTC, 1h | 013 e 014 scarti (58, 36), 013b L (0,96), 014b S (0,27) | non netto |
| I-09 compressione e rottura, 1h | 015 L (0,59), 016 S (0,77) | non netto |
| I-10 martello e stella cadente, 1h | 017 L (−0,39), 018 S (0,11) | nessun effetto |
| I-11 intervallo d'apertura UTC, 1h | 019 L (−0,62), 020 S (0,96) | non netto |
| I-12 ordini aggressivi, 1h | 021 L (0,20), 022 S (0,04) | nessun effetto |
| I-13 trend di BTC, 4h | 023 L (0,90; R medio +0,31 ma errore grande) | non netto |
| I-14 scarto last-mark, 1h | 024 S (−0,92), 025 L (−0,13) | nessun effetto |
| I-15 momento intraday, 30m | 026 L (0,68), 027 S (−1,17) | nessun effetto |

## Misure di processo

Ricavate dal log con `codice/misure.py` (date dall'orologio della macchina, UTC).

* Prima voce del log 2026-10-09T17:22:58Z, ultima (validazione) 17:48:49Z: **26 minuti**, nessuna
  pausa registrata. Il lavoro di lettura del protocollo e di scrittura di `ipotesi.md` è avvenuto
  dentro questo intervallo e prima della prima voce di variante (17:3x); i test sono veloci (2-11
  secondi per variante con 200 simulazioni della (b)).
* Varianti testate 30: 25 di idee nuove (25 famiglie), 5 ritocchi (tutti nella famiglia
  MASKUSDT-006). Idee nuove registrate 15; 14 con almeno una variante testata (I-06 solo scarti).
  Scarti senza budget: 6 (009, 011, 011b, 012, 013, 014).
* Minuti fra la prima registrazione e l'ultimo risultato, per idea: I-01 0,1; I-02 0,2; I-03 7,5
  (con i 5 ritocchi); I-04 0,2; I-05 0,0 (una variante); I-07 0,1; I-08 0,2; I-09 0,2; I-10 0,2;
  I-11 0,2; I-12 0,3; I-13 0,0; I-14 0,2; I-15 0,4. Le idee si sono testate in lotti: il tempo
  speso su ogni idea sta soprattutto nella Fase 1, prima dei test, e non è misurato dal log.
* Spiegazioni concorrenti scritte in `ipotesi.md`: 11 per ognuna delle 15 idee.
* Varianti diventate candidati in Fase 2: da idee nuove 0; da ritocchi 1 (MASKUSDT-029).
* Varianti che hanno battuto nettamente la (a) e la (b) con R medio dopo i costi non positivo: 0.
* Rifiuti del guardiano: 7, tutti di forma (note N002, N003, N004 e un `sed`), nessuno su contenuti.

## Note per il coordinamento

* Nessuna correzione a `src/`: nessun hash da portare sul principale.
* Nella voce `risultato` di ogni variante il campo `baseline_b.errore_standard` è l'errore della
  media della (b) (non l'errore della differenza): l'errore del confronto si ricava da
  `errore_candidato` e `baseline_errore_standard` (nota MASKUSDT-C002).
* Il controllo positivo degli strumenti è superato (note MASKUSDT-CP-1 e CP-2).
