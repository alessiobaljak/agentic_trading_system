# MATICUSDT — consegna della campagna (protocollo 4.5)

**Nessuna strategia valida trovata per questa moneta.**

Il budget di 30 varianti è stato usato per intero. Una sola variante è diventata candidato in
Fase 2 (`MATICUSDT-025`, terzo ritocco della famiglia dello squilibrio degli ordini). In Fase 4 ha
fallito due verifiche: il ritardo di una barra (crollo senza errore di codice) e i costi doppi.
Nessun candidato è arrivato alla validazione: il periodo di validazione (2023-01-09 → 2023-12-31)
non è stato toccato e l'asticella non si applica (m = 0).

## Periodi e dati

* Costruzione dal 2020-10-01 al 2023-01-08 (830 giorni); validazione dal 2023-01-09 al 2023-12-31.
* Primo dato vero il 2020-10-22; mesi sotto la liquidità minima (2020-10 … 2021-01) esclusi dagli
  ingressi: in pratica gli ingressi vanno dal 2021-02-01.
* Dettagli in `fase0_dati.md`: 1092 file verificati col CHECKSUM remoto; il mark manca in sei
  giornate (tolte con `carica_serie_allineate`); funding a 8 ore.

## Idee provate (riepilogo; dettagli in `ipotesi.md`, `lezioni_moneta.md` e nel log)

| Idea | Fonte (prima del 2024) | Varianti testate | Miglior `t` contro la (b) |
|---|---|---|---|
| I-01 momento settimanale | Moskowitz, Ooi, Pedersen 2012; Liu, Tsyvinski 2018 | 2 | 0,73 |
| I-02 rottura di canale | Faith 2007; Hudson, Urquhart 2019 | 0 (4 scarti) | — |
| I-03 rendimento giornaliero anomalo | Caporale, Plastun 2019 | 2 | 1,51 |
| I-04 prima mezz'ora → ultima | Shen, Urquhart, Wang 2021; Gao e altri 2018 | 2 | 0,71 |
| I-05 RSI(2) nella tendenza | Connors, Alvarez 2009 | 2 (2 scarti) | 0,60 |
| I-06 lunedì | Caporale, Plastun 2019 | 1 | −0,59 |
| I-07 funding estremo | He, Manela, Ross, von Wachter 2022 | 2 | −0,24 |
| I-08 volume alto | Gervais, Kaniel, Mingelgrin 2001 | 1 + 3 ritocchi (2 scarti, 1 ritocco scartato) | 1,94 |
| I-09 ritorno dopo salti orari | Wen, Bouri, Xu, Zhao 2022 | 2 | −1,62 |
| I-10 massimo di 52 settimane | George, Hwang 2004 | 0 (1 scarto) | — |
| I-11 media di 50 giorni | Brock, Lakonishok, LeBaron 1992 | 2 (2 scarti) | −0,35 |
| I-12 compressione di Bollinger | Bollinger 2001 | 0 (4 scarti) | — |
| I-13 squilibrio degli ordini aggressivi | Chordia, Subrahmanyam 2004; Silantyev 2019 | 2 + 5 ritocchi | 2,21 (candidato 025: 2,12) |
| I-14 forza relativa contro BTC | Liu, Tsyvinski, Wu 2019 | 2 | 0,67 |
| I-15 illiquidità | Amihud 2002 | 2 | 0,09 |

Idea tolta prima del test: anticipo di BTCUSDT su MATICUSDT (contaminata da un risultato di
ricerca su un articolo del 2024; nota `MATICUSDT-N008`).

## Il candidato bocciato: MATICUSDT-025

Regole complete in `candidati/MATICUSDT-025/regole.md`. Short su 1h quando lo squilibrio delle
ultime 6 ore fra volume taker buy e volume totale è sotto media − 2 deviazioni standard dei 30
giorni precedenti e BTCUSDT non è salito nelle 24 ore prima; stop a min(2 ATR14, 6%); uscita dopo
12 ore.

**Metriche di costruzione:** 124 trade; R medio dopo i costi 0,149 (senza i 3 migliori 0,070);
profit factor 1,40; drawdown massimo 5,3%; R medio 2021 0,058 (47 trade), 2022 0,195 (76);
baseline (a) −0,090, `t` 2,41 (netta); baseline (b) −0,053, `t` 2,12, soglia 2,06, p 0,020
(netta); percentile fra le simulazioni casuali 99,5; nessun trade ridotto per il tetto di leva;
nessuna violazione di liquidazione. Validazione: non eseguita (scartato prima).

**Verifiche della Fase 4:**

| Verifica | Esito |
|---|---|
| Robustezza (16 casi, ±20%) | superata di poco: `t` positivo in 16 su 16, netto in 9 su 16 |
| Timeframe adiacenti | superata: 30m `t` 3,09; 2h `t` 0,56 |
| Stabilità per anno | superata: 2021 e 2022 sopra la (b) |
| Trade estremi | superata: senza i 3 migliori 0,070 > −0,053 |
| Regola intra-barra opposta | nessuna differenza (nessun target) |
| Liquidazione | nessuna violazione |
| **Ritardo di una barra** | **non superata**: `t` 0,53 (minimo 1,06), R medio −0,003. Nessun lookahead nel codice (segnale identico su serie troncata in 80 barre su 80) |
| **Costi doppi** | **non superata**: R medio 0,094 ma `t` 2,03 sotto la soglia 2,06 |

Lettura: l'effetto, se esiste, vale qualche ora e sta a ridosso del rumore. Un'ora di ritardo lo
cancella, quindi il bot, che entra dopo la chiusura della candela con un po' di latenza, non
potrebbe prenderlo.

## Varianti e budget

* 30 varianti testate: 22 di idee nuove (22 famiglie), 8 ritocchi (5 nella famiglia
  `MATICUSDT-018`, 3 nella famiglia `MATICUSDT-016`); 16 scarti sotto i 70 trade, fra cui un
  ritocco (conta fra i ritocchi della sua famiglia).
* Candidati in Fase 2: 0 da idee nuove, 1 da ritocchi (`MATICUSDT-025`). Candidati validati: 0.
  p-value di validazione ed esito dell'asticella: non applicabili (nessun candidato in
  validazione).

## Misure di processo

Ricavate dal log con `codice/misure.py` (`esiti/misure_processo.json`); le date delle voci sono
quelle dell'orologio della macchina (UTC).

* Durata dalla prima all'ultima voce del log: 30,1 minuti (13:26:18 → 13:56:26 UTC del 2026-10-09),
  senza pause registrate (nessuna attesa di risposte durante il lavoro), quindi 30,1 anche senza
  pause. Nota: la sessione ha lavorato anche prima della prima voce (lettura del protocollo e degli
  strumenti) e la consegna è scritta dopo l'ultima.
* Minuti per idea, dalla registrazione della prima variante all'ultimo risultato: I-01 2,8; I-03 2,8;
  I-04 2,8; I-05 2,0; I-06 2,8; I-07 2,8; I-08 7,9; I-09 2,8; I-11 2,0; I-13 6,2; I-14 2,0; I-15 0,6
  (le varianti sono state registrate e testate a lotti, per questo molte idee hanno la stessa
  durata). Le idee I-02, I-10 e I-12 non hanno varianti testate (solo scarti).
* Spiegazioni concorrenti scritte in `ipotesi.md` per idea: 11 comuni a tutte (C1-C11) più quelle
  proprie: I-01 14, I-02 13, I-03 14, I-04 13, I-05 14, I-06 13, I-07 14, I-08 13, I-09 13, I-10 13,
  I-11 13, I-12 13, I-13 13, I-14 13, I-15 13.
* Varianti che hanno battuto nettamente la (a) e la (b) con R medio non positivo: 0.
* Previsioni: sbagliate soprattutto sulle strategie lente (R medi più alti del previsto per pochi
  trade estremi) e sui salti orari (continuazione invece di ritorno).

## Cosa resta da sapere (limiti)

* Potenza bassa: con circa 100-150 trade per variante un vantaggio di 0,05-0,10 R non si distingue
  dal caso (sezione 11).
* Il periodo di costruzione è quasi tutto un grande rialzo (2021) e un grande ribasso (2022): le
  strategie lente ne sono dominate.
* Lo slippage della scheda (0,02%) è ottimista per febbraio-marzo 2021 (volume sotto i 200
  milioni).

## Per il vault, il trasferimento e il paper

Nessun candidato: niente da portare al vault, al trasferimento o al paper.
