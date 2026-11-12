# gate2: memoria del confronto fra paper, demo e ricerca (aggiornato 2026-11-12)

## Stato per strategia
- G1 (paper del bot dal 23 ott 2026; demo di Binance a fasi: 5.000 USDT fino al 6 nov, 280, poi 1.000 dall'8 nov 00:18 UTC)
  - ultimo confronto: 2026-11-09, rapporto `reports/2026-11-09-G1.md`
  - verdetto: nessuno (soglie solo PROPOSTE, non approvate da Alessio); sul minimo giorni sarebbe INCONCLUSIVE
  - regole e codice: parità del bot con la ricerca confermata il 30 ott (60 giorni, scarto max 6e-17); da allora le funzioni dei pesi non sono cambiate (git)
  - 12 nov: misure funding e commissioni del demo 8-11 nov, rapporto `reports/2026-11-12-G1-funding-commissioni.md`: funding demo 0,828% contro paper 1,181% (differenza 0,019/0,033/0,146/0,155 punti); causa non dimostrata (9 nov: tutta alla 00:00; 10-11 nov no); commissioni 0,89 USDT, quota a mercato non stimabile (8 nov: 0,038% medio)
  - aperto: giorno 30 ott (paper +3,41% contro ricerca +1,46%), demo da zero dell'8 nov, 龙虾USDT rifiutata, ICPUSDT mancante sul demo

## File
- `THRESHOLDS.md`: soglie proposte (sezione approvate vuota)
- `RECON_LOG.md`: una riga per confronto (aperti + ultime 10); `ARCHIVE.md`: il resto
- `reports/AAAA-MM-GG-<strategia>.md`: rapporti completi
- `exports/`: script e risultati del ricalcolo (`ricalcolo_g1_ricerca.py` ricalcola G1 dalla partenza del paper con banda vuota; `confronto_giorni_g1.py` confronta con le serie scritte a mano; `ricalcolo_g1_ricerca_2026-11-09.json` risultato)

## Come rifare il confronto di G1
1. Pannello: `research/data/p6g_pannello.pkl` (arriva al 7 nov; il funding dopo il 31 ott e' riempito, non vero).
2. `python3 -m` ... vedi l'intestazione degli script in `exports/` (eseguire con la radice del repo nel percorso).
3. Serie del paper e del demo: tabella «G1: il demo contro il paper» delle risposte `ops/results/*stato*.md` (usare l'ultima per ogni giorno).
