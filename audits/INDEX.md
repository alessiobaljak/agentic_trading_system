# Indice della memoria dell'auditor (massimo 40 righe)
Aggiornato: 2026-11-12. Leggere all'inizio di ogni invocazione questo file e `KNOWN_PITFALLS.md`; il resto solo se serve.

## Stato degli audit per strategia
| Strategia | Ultimo audit | Verdetto | Note |
|---|---|---|---|
| BTCORA (collaudo, `research/prova_finta_audit/`) | 2026-11-07 | FAIL | prova finta per collaudare l'audit; sguardo nel futuro e funding assente |
| Prova 28: K2, F5 + M7 + K2 (riesame) | 2026-11-11 | PASS tecnico | Alti: Sharpe corretto 0,75/0,47 con N = conto, 0,89/0,69 con N = gruppi; regole: «non candidate» |
| Prova 113: N3G, monete gratis (riesame) | 2026-11-11 | PASS tecnico del «no» | corretta p 0,0268 (serve 0,01); Alto: eventi della 32 da rifare (19 persi); tocca anche N3 nel paper |
| G1 (demo, candidata ai soldi veri; configurazione 280 USDT) | 2026-11-12 | PASS tecnico | Alti: esame 0,80 solo con il limite della ricerca (A 0,81, a mercato 0,77); GTC al mark; soglia cambiata dopo; moneta fino al 44% |
| Prova 96: G22, deriva del Bitcoin dopo la Fed (riesame) | 2026-11-12 | PASS tecnico del «no» | p 0,0205 rifatta identica; nessun errore la porta a 0,01; Medi: controllo a caso esagera, limite macro di 2 ore |
| Prova 55: C3, punteggio unico F5 + K2 + M7 (riesame) | 2026-11-12 | FAIL del calcolo, «no» confermato | settimana oltre il periodo; «peggio di F5» falso sulle stesse settimane (1,87 contro 1,61); corretto oggi 0,75 |
| Mazzo dello Sharpe corretto (`asticella.py`, `78235da`) | 2026-11-12 | FAIL del mazzo | numeri rifatti identici; 27 varianti senza serie tolte, 81-82 senza filtro, conferme dentro; corretti G1 0,733, miscela 0,797/0,802 |
| G11, G1N, F5, eventi (paper); vecchie `bot/strategies/` (ferme dal 13 ott) | mai | — | solo elenco con lo stato al prossimo avvio completo |

## Cosa contiene ogni file
- `KNOWN_PITFALLS.md`: errori del repo, con file e schema da cercare (sempre). `AUDIT_LOG.md`: una riga per audit.
- `reports/AAAA-MM-GG-<strategia>.md`: rapporto completo. Da leggere solo DOPO aver formato il verdetto, per i problemi tornati.
- `repro/`: script dei controlli; `*_esito*.json` i numeri.
  - `repro/prova28_*.py` (11 nov): prove settimanali del programma 6: taglio, entrata oraria, conto unico, filtri, sensibilità.
  - `repro/g1_2026-11-12.py` e `g1_parte2_2026-11-12.py` (12 nov): G1 e i conti giornalieri del programma 7 (`nucleo`): cache in
    `CACHE_G1N` (parte `base` prima), taglio, sensibilità ±10/20%, limite con `oltre`, dati, leva, misure, Sharpe corretto.
  - `repro/prova113_2026-11-11.py` (11 nov): prove a eventi su candele orarie (32, 113), ore mancanti scaricate in cartella temporanea.
  - `repro/prova96_2026-11-12.py` (evento su Bitcoin, p in otto modi); `repro/prova55_2026-11-12.py` (punteggio settimanale a parti).
  - `repro/mazzo_2026-11-12.py` (12 nov): il mazzo dello Sharpe corretto. Prima `cache <cartella>` (7 s), poi `numeri` (formula
    riscritta), `copertura` (registro prova per prova), `allinea`, `eventi`, `sensi`, `regola_scritta`, `fino57`, `varianti_g1`.

## Decisioni aperte per Alessio
- (7 nov) Minimo di anni e di operazioni; perdita giornaliera del 5% da simulare o no (K2 3 volte, C3 7). Costi confermati il 7 nov.
- (11 nov) Se il riesame può rendere candidata una «costruzione» che le sue regole escludono; esclusione della famiglia del funding
  nelle miscele. Prove a eventi: minimo di eventi; esame della misura in avanti delle monete gratis da scrivere prima dei dati nuovi.
- (12 nov) G1 sul conto vero: soglia (0,95 scritta, 0,80 di oggi), costo degli ordini limite, tetto per moneta, capitale minimo.
- (12 nov) Prova 96: limite di 2 ore attorno agli eventi macro; soglia a eventi. Prova 55: «qualche punto sotto» per C3; riserva del 23 ott.
- (12 nov) Mazzo: le prove dopo la scoperta contano? (G1 fino alla 57: 0,946; tutte: 0,733-0,769); prove senza serie come 26, 13 o 2
  famiglie; conferme; serie corte (147, 151); la miscela F5 + M7 + K2 corretta è sulla soglia (0,797/0,802; 0,755 al taglio 0,7).

## Note di metodo
- Mai il `main` delle prove (riscrive i risultati): importare le funzioni (voce 11). L'auditor non committa (11 nov).
- Copia troncata: commit con `gh api` (voce 17); mai `grep -r research/`. Script: `PYTHONPATH=<radice> python3 audits/repro/<script>.py`.
