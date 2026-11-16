# gate2: memoria del confronto fra paper, demo e ricerca (aggiornato 2026-11-16)

## Stato per strategia
- G1 (paper del bot dal 23 ott 2026; demo di Binance a fasi: 5.000 USDT fino al 6 nov, 280, poi 1.000 dall'8 nov 00:18 UTC)
  - ultimo confronto: 2026-11-16, rapporto `reports/2026-11-16-G1.md` (settimana 9-15 nov); prima: 2026-11-09
  - verdetto: nessuno (soglie solo PROPOSTE, non approvate da Alessio); sul minimo giorni sarebbe INCONCLUSIVE
  - regole e codice: parità del bot con la ricerca confermata il 30 ott (60 giorni, scarto max 6e-17); da allora le funzioni dei pesi non sono cambiate (git)
  - 12 nov: misure funding e commissioni del demo 8-11 nov, rapporto `reports/2026-11-12-G1-funding-commissioni.md`: funding demo 0,828% contro paper 1,181% (differenza 0,019/0,033/0,146/0,155 punti); causa non dimostrata (9 nov: tutta alla 00:00; 10-11 nov no); commissioni 0,89 USDT
  - 12 nov sera (0736, letture vere): commissione demo maker 0,02% taker 0,04%; 6 giorni 0,0303% del valore, regime 0,0254% con 27% a mercato, partenza da vuoto 0,032% (60%); funding 10-11 nov: gap nei regolamenti 08/16/altre ore, non alle 00:00 (anomalia della 00:00 del paper da confermare); monete mancanti al più un terzo
  - 16 nov: parita' codice OK (commit 2c5e7b6). Demo-paper 9-15 nov -2,06 punti (media -0,30/giorno, mediana +0,09; 13-14 nov quasi tutto; ~1,2 non spiegati). Ricerca (con applica_stima) NON riproduce il paper dal 9 nov: paper-ricerca +3,79 in 5 giorni (prima 0,22 mediana); causa probabile funding di novembre stimato che cambia la scelta delle monete (14 nov: 8 monete paper fuori, 13 ricerca fuori), da confermare. Commissione demo 0,0275% (1,38x il limite assunto), 33% a mercato. Pannello ricerca fermo al 13 nov. Binance non raggiungibile da qui
  - aperto: giorno 30 ott (paper +3,41% contro ricerca +1,46%), demo da zero dell'8 nov, 龙虾USDT rifiutata, ICPUSDT mancante sul demo

## File
- `THRESHOLDS.md`: soglie proposte (sezione approvate vuota)
- `RECON_LOG.md`: una riga per confronto (aperti + ultime 10); `ARCHIVE.md`: il resto
- `reports/AAAA-MM-GG-<strategia>.md`: rapporti completi
- `exports/`: script e risultati del ricalcolo (`ricalcolo_g1_ricerca.py` ricalcola G1 dalla partenza del paper con banda vuota; `confronto_giorni_g1.py` confronta con le serie scritte a mano; dal 16 nov `ricalcolo_g1_ricerca_16nov.py` (con applica_stima), `confronto_settimana_16nov.py` (tabella giorno per giorno 9-16), `pesi_14nov_ricerca.py` (pesi del 14 nov contro il paper); `ricalcolo_g1_ricerca_2026-11-09.json` risultato)

## Come rifare il confronto di G1
1. Pannello: `research/data/p6g_pannello.pkl` (arriva al 13 nov; il funding dopo il 31 ott e' stima con applica_stima, non vero).
2. `python3 -m` ... vedi l'intestazione degli script in `exports/` (eseguire con la radice del repo nel percorso).
3. Serie del paper e del demo: tabella «G1: il demo contro il paper» delle risposte `ops/results/*stato*.md` (usare l'ultima per ogni giorno).
