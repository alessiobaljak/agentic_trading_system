# Consegna della campagna ETHUSDT

**Esito: nessuna strategia valida trovata per questa moneta.**

Campagna del protocollo di ricerca (versione 4.3), Passo 3, seconda delle tre monete della
prova di processo. Sessione unica del 7 ottobre 2026, dalle 08:50 alle 13:30 UTC circa
(la prima sessione, aperta alle 08:43, ha perso il lavoro per un problema di permessi del
push e non ha lasciato nulla). Tutto quello che segue viene dal log
`campagne/ETHUSDT/log.jsonl` (solo in aggiunta, 23 varianti registrate prima di eseguirle)
e dai file in `risultati/`.

## In una frase per riga

* Dati: 2020-01-01 → 2023-12-31, 240 file mensili con checksum verificato, nessun buco
  nelle candele last, nessun giorno sotto 20 milioni di USDT (`fase0_dati.md`).
* Costruzione 2020-01-01 → 2022-10-19 (1.023 giorni); validazione 2022-10-20 → 2023-12-31
  (438 giorni), fissate nel log prima di caricare i prezzi. **La validazione non è mai stata
  usata**: nessun candidato è arrivato fin lì.
* 22 idee di 17 famiglie, tutte con fonte pubblicata prima del 2024 e scritte prima dei
  test (`ipotesi.md`): 45 varianti possibili, 22 scartate prima del test per stima dei trade
  sotto 100 (nessun budget), 23 testate sui dati di costruzione, 7 varianti di budget non
  spese.
* Nessuna delle 23 batte nettamente (oltre 2 errori standard, bootstrap a blocchi) le
  entrate casuali con la stessa uscita. Nessun candidato passa alla Fase 3; Fase 4,
  validazione e asticella non hanno nulla su cui girare.
* Il controllo positivo degli strumenti (strategia con lookahead dichiarato) passa: gli
  strumenti vedono un vantaggio quando esiste e il ritardo di una barra lo smaschera.

## Le regole uguali per tutte le varianti

Segnali e stop sul last price, liquidazione sul mark price, funding storico a ogni
settlement (sempre 8 ore nel periodo). Commissione 0,05 % e slippage 0,01 % per lato.
Rischio 1 % del capitale sulla distanza dallo stop, leva massima 2, margine isolato, tasso
di mantenimento 2,5 %, capitale 1.000 (regole del bot, `config/regole_dimensione.md`). Stop
a 2 volte l'ATR a 14 barre del timeframe del segnale, durata massima H dichiarata per idea,
eventuale uscita su segnale. Ingresso all'apertura della barra dopo il segnale.

Baseline: (a) ingresso a ogni barra libera con la stessa uscita; (b) 200 strategie a
entrate casuali con stesso numero di trade, stessa distanza media, stessa uscita e
direzione, con il percentile dell'R medio del candidato e la differenza dalla strategia
casuale mediana in errori standard a blocchi; (c) buy and hold e il suo opposto. Criterio
di passaggio alla Fase 3, scritto prima: almeno 100 trade, differenza dalla casuale oltre 2
errori standard e percentile almeno 90, R medio sopra la baseline (a), profit factor sopra 1.

## Le 23 varianti testate (periodo di costruzione)

Tabella generata dal log con `codice/riepilogo_varianti.py`; R medio per anno con il numero
di trade fra parentesi.

| Id | Idea | Timeframe | Dir. | Trade | Profit factor | R medio | Win rate | Percentile fra 200 casuali | Differenza vs casuale (err. std.) | Netta | R medio per anno |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 001 | I-01 momento di serie temporale a 7 giorni | 4h | long | 275 | 1.381 | +0.178 | 0.34 | 95.5 | 0.0941 (0.1341) | no | 2020: +0.407 (92), 2021: +0.192 (112), 2022: -0.140 (71) |
| 002 | I-01 momento di serie temporale a 7 giorni | 4h | short | 251 | 0.86 | -0.040 | 0.31 | 70.5 | 0.0261 (0.0971) | no | 2020: -0.210 (76), 2021: -0.099 (92), 2022: +0.180 (83) |
| 003 | I-03 inversione RSI a 2 periodi | 1h | long | 1579 | 0.745 | -0.077 | 0.63 | 1.5 | -0.0235 (0.0192) | no | 2020: -0.028 (524), 2021: -0.102 (569), 2022: -0.102 (486) |
| 004 | I-03 inversione RSI a 2 periodi | 1h | short | 1622 | 0.656 | -0.074 | 0.61 | 2.0 | -0.0204 (0.0187) | no | 2020: -0.101 (627), 2021: -0.096 (567), 2022: -0.004 (428) |
| 005 | I-05 ritardo di ETH su BTC | 1h | long | 644 | 0.946 | -0.013 | 0.46 | 88.5 | 0.0267 (0.0367) | no | 2020: +0.066 (198), 2021: -0.045 (342), 2022: -0.059 (104) |
| 006 | I-05 ritardo di ETH su BTC | 1h | short | 491 | 0.691 | -0.087 | 0.40 | 12.0 | -0.03 (0.0402) | no | 2020: -0.140 (139), 2021: -0.083 (252), 2022: -0.024 (100) |
| 007 | I-09 momento intragiornaliero | 1h | long | 380 | 0.718 | -0.041 | 0.45 | 69.0 | 0.0079 (0.0236) | no | 2020: -0.054 (131), 2021: -0.019 (152), 2022: -0.058 (97) |
| 008 | I-09 momento intragiornaliero | 1h | short | 351 | 0.877 | -0.015 | 0.50 | 98.5 | 0.0389 (0.0256) | no | 2020: +0.023 (116), 2021: -0.056 (144), 2022: +0.002 (91) |
| 009 | I-10 funding estremo come segnale contrario | 8h | short | 190 | 0.77 | -0.031 | 0.51 | 48.0 | -0.001 (0.0335) | no | 2020: -0.055 (71), 2021: -0.051 (69), 2022: +0.030 (50) |
| 010 | I-14 premio del perpetuo sul prezzo mark | 1h | short | 1549 | 0.777 | -0.053 | 0.45 | 50.5 | 0.0003 (0.0255) | no | 2020: -0.096 (482), 2021: -0.050 (589), 2022: -0.015 (478) |
| 011 | I-14 premio del perpetuo sul prezzo mark | 1h | long | 1598 | 0.884 | -0.033 | 0.49 | 75.5 | 0.0118 (0.0245) | no | 2020: +0.003 (506), 2021: -0.020 (592), 2022: -0.084 (500) |
| 012 | I-15 rottura del range d'apertura del giorno UTC | 1h | long | 287 | 1.315 | +0.150 | 0.48 | 99.0 | 0.1273 (0.1024) | no | 2020: +0.385 (103), 2021: +0.125 (112), 2022: -0.148 (72) |
| 013 | I-15 rottura del range d'apertura del giorno UTC | 1h | short | 256 | 1.017 | +0.014 | 0.39 | 94.0 | 0.0869 (0.0997) | no | 2020: +0.017 (84), 2021: -0.001 (95), 2022: +0.030 (77) |
| 014 | I-16 ore americane (long) e ore asiatiche (short) | 1h | long | 1022 | 1.036 | +0.022 | 0.49 | 97.5 | 0.0489 (0.0444) | no | 2020: +0.099 (365), 2021: +0.021 (365), 2022: -0.073 (292) |
| 015 | I-16 ore americane (long) e ore asiatiche (short) | 1h | short | 1022 | 0.921 | -0.021 | 0.47 | 98.5 | 0.042 (0.036) | no | 2020: -0.032 (365), 2021: -0.026 (365), 2022: -0.001 (292) |
| 016 | I-17 autocorrelazione dei rendimenti giornalieri | 1d | long | 359 | 0.874 | -0.018 | 0.47 | 14.0 | -0.0222 (0.029) | no | 2020: +0.028 (128), 2021: -0.030 (136), 2022: -0.061 (95) |
| 017 | I-17 autocorrelazione dei rendimenti giornalieri | 1d | short | 324 | 0.677 | -0.046 | 0.44 | 14.5 | -0.02 (0.0294) | no | 2020: -0.085 (111), 2021: -0.043 (112), 2022: -0.008 (101) |
| 018 | I-18 attraversamento di un livello tondo | 1h | long | 1912 | 0.778 | -0.041 | 0.43 | 70.0 | 0.0055 (0.0163) | no | 2020: -0.041 (659), 2021: -0.041 (834), 2022: -0.039 (419) |
| 019 | I-18 attraversamento di un livello tondo | 1h | short | 1815 | 0.68 | -0.060 | 0.40 | 36.0 | -0.0048 (0.0163) | no | 2020: -0.078 (599), 2021: -0.060 (787), 2022: -0.037 (429) |
| 020 | I-20i inversione dopo movimento oltre 1 sigma a volume alto | 4h | long | 513 | 0.96 | -0.007 | 0.54 | 58.0 | 0.0038 (0.0333) | no | 2020: +0.027 (161), 2021: +0.035 (185), 2022: -0.087 (167) |
| 021 | I-20i inversione dopo movimento oltre 1 sigma a volume alto | 4h | short | 531 | 0.77 | -0.042 | 0.49 | 43.5 | -0.0025 (0.0289) | no | 2020: -0.064 (197), 2021: -0.056 (200), 2022: +0.011 (134) |
| 022 | I-21 candela avvolgente dopo 3 candele contrarie | 4h | short | 123 | 0.835 | -0.057 | 0.49 | 42.0 | -0.0104 (0.1016) | no | 2020: -0.050 (40), 2021: -0.178 (39), 2022: +0.045 (44) |
| 023 | I-22 inversione a lungo orizzonte dopo ribasso profondo (o rialzo ampio) a 30 giorni | 4h | short | 185 | 0.545 | -0.283 | 0.29 | 0.5 | -0.2052 (0.143) | no | 2020: -0.317 (70), 2021: -0.278 (90), 2022: -0.209 (25) |

### Varianti scartate prima del test (stima dei trade sotto 100, nessun budget)

| Idea | Dir. | Timeframe | Trade stimati | Motivo |
|---|---|---|---|---|
| I-02 rottura del canale a 30 barre | long | 4h | 74 | stima dei trade in costruzione sotto il minimo di 100 |
| I-02 rottura del canale a 30 barre | short | 4h | 57 | stima dei trade in costruzione sotto il minimo di 100 |
| I-04 reazione eccessiva dopo candela anomala | long | 4h | 83 | stima dei trade in costruzione sotto il minimo di 100 |
| I-04 reazione eccessiva dopo candela anomala | short | 4h | 87 | stima dei trade in costruzione sotto il minimo di 100 |
| I-06 ritorno alla media del rapporto ETH/BTC | long | 4h | 28 | stima dei trade in costruzione sotto il minimo di 100 |
| I-06 ritorno alla media del rapporto ETH/BTC | short | 4h | 31 | stima dei trade in costruzione sotto il minimo di 100 |
| I-07 momento relativo ETH contro BTC | long | 1d | 42 | stima dei trade in costruzione sotto il minimo di 100 |
| I-07 momento relativo ETH contro BTC | short | 1d | 40 | stima dei trade in costruzione sotto il minimo di 100 |
| I-08 inversione del fine settimana | long | 1d | 56 | stima dei trade in costruzione sotto il minimo di 100 |
| I-08 inversione del fine settimana | short | 1d | 63 | stima dei trade in costruzione sotto il minimo di 100 |
| I-10 funding estremo come segnale contrario | long | 8h | 94 | stima dei trade in costruzione sotto il minimo di 100 |
| I-11 compressione della volatilita' e rottura | long | 4h | 3 | stima dei trade in costruzione sotto il minimo di 100 |
| I-11 compressione della volatilita' e rottura | short | 4h | 4 | stima dei trade in costruzione sotto il minimo di 100 |
| I-12 premio del volume alto | long | 12h | 98 | stima dei trade in costruzione sotto il minimo di 100 |
| I-13 squilibrio degli ordini a mercato (compratori aggressivi) | long | 1h | 63 | stima dei trade in costruzione sotto il minimo di 100 |
| I-13 squilibrio degli ordini a mercato (compratori aggressivi) | short | 1h | 69 | stima dei trade in costruzione sotto il minimo di 100 |
| I-19 vicinanza al massimo e al minimo a 30 giorni | long | 4h | 63 | stima dei trade in costruzione sotto il minimo di 100 |
| I-19 vicinanza al massimo e al minimo a 30 giorni | short | 4h | 20 | stima dei trade in costruzione sotto il minimo di 100 |
| I-20c continuazione dopo movimento oltre 1 sigma a volume basso | long | 4h | 89 | stima dei trade in costruzione sotto il minimo di 100 |
| I-20c continuazione dopo movimento oltre 1 sigma a volume basso | short | 4h | 73 | stima dei trade in costruzione sotto il minimo di 100 |
| I-21 candela avvolgente dopo 3 candele contrarie | long | 4h | 87 | stima dei trade in costruzione sotto il minimo di 100 |
| I-22 inversione a lungo orizzonte dopo ribasso profondo (o rialzo ampio) a 30 giorni | long | 4h | 69 | stima dei trade in costruzione sotto il minimo di 100 |

## Lettura dei risultati

**Nessun vantaggio netto.** Le differenze dall'entrata casuale vanno da −0,21 a +0,13 R
per trade, con errori standard da 0,016 a 0,14: la più grande in errori standard è 1,5
(momento intragiornaliero short, che però perde dopo costi), le altre sopra il 90°
percentile stanno a 1,1-1,2 errori.

**I quattro profit factor sopra 1 sono il trend 2020-21.** Momento a 7 giorni long (1,38),
rottura del range d'apertura long (1,32), ore americane long (1,04) e rottura del range
short (1,02) guadagnano nel 2020 e nel 2021 e perdono nel 2022 (colonna «R medio per anno»
della tabella); un long qualunque con la stessa uscita fa lo stesso, e infatti nessuno dei
tre long supera le entrate casuali long oltre 2 errori standard. Il momento a 7 giorni long
ha inoltre 99 trade su 275 con stop oltre il 6 % del prezzo, che il bot non aprirebbe.

**A 1 ora i costi decidono.** Dodici varianti a 1 ora, con durate di 1-4 barre: profit factor
dopo costi fra 0,66 e 0,95 in undici casi, con commissioni e slippage (0,12 % per giro)
dello stesso ordine del movimento tipico. È il limite già scritto nella sezione 11 del
protocollo («costi a orizzonte corto»), confermato con numeri.

**Indizi deboli, non candidati.** Sessione americana contro asiatica (I-16: long +0,02 R
netto, short −0,02 ma sopra lo short casuale) e rottura del range d'apertura (I-15) sono le
uniche idee con un po' di struttura coerente con le loro fonti. Con questi costi e questa
uscita non pagano; non si portano in validazione perché non hanno superato il criterio
scritto prima.

**Le direzioni separate costano trade.** Otto idee su ventidue (canale, candela anomala,
rapporto ETH/BTC, momento relativo, fine settimana, compressione, vicinanza al massimo,
inversione lunga) non arrivano a 100 trade per direzione in 1.023 giorni; due di esse
(momento relativo, fine settimana) ci arriverebbero con le due direzioni insieme. È
una scelta del protocollo, dichiarata in `lezioni_metodo_proposte.md`.

## Verifiche della Fase 4, validazione, asticella, vault, paper

Non eseguite: nessun candidato è sopravvissuto alle Fasi 1-2. Il periodo di validazione è
intatto per questa moneta. Il controllo positivo (`risultati/controllo_positivo.json`,
nota N009) sostituisce la domanda «gli strumenti avrebbero visto un vantaggio?»: sì, con
30 errori standard, e il ritardo di una barra lo riporta sotto 1.

## Budget

23 varianti su 30. Le 7 restanti non sono state spese: le idee con una fonte anteriore
al 2024 e un meccanismo diverso da quelli già provati si sono esaurite, e le varianti
rimaste possibili sarebbero soglie o timeframe diversi di idee fallite (selezione sul
risultato). Il protocollo lo prevede.

## Cosa può eseguire il bot

Domanda senza oggetto: nessun candidato. Per memoria, nessuna delle idee provate usa dati
che il bot non ha, tranne il premio sul mark (I-14) e il flusso degli ordini (I-13), che
richiederebbero il mark price storico e il campo del volume taker.

## Previsione per vault e trasferimento

Nessun candidato: nulla da prevedere. Se il coordinamento volesse comunque un'indicazione
per il confronto fra monete (Passo 7): le famiglie che su ETHUSDT hanno mostrato un filo di
struttura sono «sessione del giorno» e «range d'apertura»; quelle nettamente peggio del
caso sono l'inversione a brevissimo (RSI a 2 periodi), il ritardo di ETH su BTC short e
l'inversione lunga short.

## Limiti dichiarati (sezione 11)

* Vault non perfettamente cieco: le scelte sono dichiarate a priori nel log, ma chi le ha
  scritte conosce a grandi linee i mercati dopo il 2024.
* Storia corta: 2,8 anni di costruzione con un solo ribasso pieno (2022); i tre long con
  profit factor sopra 1 vivono di 2020-21.
* Fascia di slippage del 2023 (0,01 %) ottimista per il 2020 (volume medio 723 milioni,
  minimi di 45 milioni).
* Due giorni interi senza candele mark (2 ottobre 2022, 24 febbraio 2023): usata la
  candela last per la liquidazione; nessuna liquidazione in nessuna variante.
* Stop a 2 ATR su candele da 4h e 1d spesso oltre il 6 % del bot: contati per variante
  nel log (`n_stop_oltre_6pct`), non imposti.

## File della consegna

`ipotesi.md` (22 idee, 5 lotti), `fase0_dati.md` (dati e 192 impronte), `log.jsonl` (81
voci), `risultati/riepilogo_varianti.md` e `.json`, `risultati/ETHUSDT-0NN_costruzione.json`
(tutti i trade di ogni variante), `risultati/controllo_positivo.json`, `lezioni_moneta.md`,
`lezioni_metodo_proposte.md`, `codice/` (tutto il codice usato, riproducibile con i semi
scritti).
