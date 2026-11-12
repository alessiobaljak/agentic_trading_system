# Indice della memoria dell'auditor (massimo 40 righe)
Aggiornato: 2026-11-12. Leggere all'inizio di ogni invocazione questo file e `KNOWN_PITFALLS.md`; il resto solo se serve.

## Stato degli audit per strategia
| Strategia | Ultimo audit | Verdetto | Note |
|---|---|---|---|
| BTCORA (collaudo, `research/prova_finta_audit/`) | 2026-11-07 | FAIL | prova finta per collaudare l'audit; sguardo nel futuro e funding assente |
| Prova 28: K2, F5 + M7 + K2 (riesame) | 2026-11-11 | PASS tecnico | Alti: Sharpe corretto 0,75/0,47 con N = conto, 0,89/0,69 con N = gruppi; regole: «non candidate» |
| Prova 113: N3G, monete gratis (riesame) | 2026-11-11 | PASS tecnico del «no» | corretta p 0,0268 (serve 0,01); Alto: eventi della 32 da rifare (19 persi); tocca anche N3 nel paper |
| G1 (demo, candidata ai soldi veri; configurazione 280 USDT) | 2026-11-12 | PASS tecnico | Alti: esame 0,80 solo con il limite della ricerca (A 0,81, a mercato 0,77); GTC al mark; soglia cambiata dopo; moneta fino al 44% |
| Prova 96: G22, deriva del Bitcoin dopo la Fed (riesame) | 2026-11-12 | PASS tecnico del «no» | p 0,0205 rifatta identica; 46 riunioni e ore confermate dalla Fed; nessun errore la porta a 0,01; Medi: controllo a caso esagera, limite macro di 2 ore |
| G11, G1N, F5, eventi (paper); vecchie `bot/strategies/` (ferme dal 13 ott) | mai | — | solo elenco con lo stato al prossimo avvio completo |

## Cosa contiene ogni file
- `KNOWN_PITFALLS.md`: errori del repo, con file e schema da cercare (sempre). `AUDIT_LOG.md`: una riga per audit.
- `reports/AAAA-MM-GG-<strategia>.md`: rapporto completo. Da leggere solo DOPO aver formato il verdetto, per i problemi tornati.
- `repro/`: script dei controlli; `*_esito*.json` i numeri.
  - `repro/prova28_*.py` (11 nov): prove settimanali del programma 6 (`seconda`, `terza.conto`): taglio (anche M7),
    entrata oraria, conto unico, perdita peggiore, filtri, sensibilità, Sharpe corretto nei due metodi.
  - `repro/g1_2026-11-12.py` e `g1_parte2_2026-11-12.py` (12 nov): modello per G1 e i conti giornalieri del programma 7 (`nucleo`):
    cache in `CACHE_G1N` (parte `base` prima), taglio, sensibilità ±10/20%, limite con `oltre`, dati, leva, misure, Sharpe corretto.
  - `repro/prova113_2026-11-11.py` (11 nov): modello per le prove a eventi su candele orarie (32, 113): etichette dagli annunci,
    simboli riusati, funding nella tenuta, ore mancanti scaricate in cartella temporanea (catalogo, voce 25), sensibilità.
  - `repro/prova96_2026-11-12.py` (12 nov): prova a evento su un solo simbolo (Bitcoin, ore e minuti scaricati con impronte, parte
    `scarica`): p in otto modi, entrata ritardata, funding, limite macro, misure, Sharpe corretto; ore dei comunicati della Fed.

## Decisioni aperte per Alessio
- (7 nov) Minimo di anni e di operazioni per giudicare una prova; perdita giornaliera massima del 5% da simulare o no
  (11 nov: K2 la supera 3 volte). Costi confermati dal proprietario il 7 novembre (0,05%, 0,02%, scarto 0,01%/0,02%).
- (11 nov) N nello Sharpe corretto: deciso, i gruppi (`CLAUDE.md`, 11 nov); se il riesame può rendere
  candidata una «costruzione» che le sue regole escludono; se l'esclusione della famiglia del funding vale per le miscele.
  Prove a eventi: minimo di eventi; esame della misura in avanti delle monete gratis da scrivere prima dei dati nuovi.
- (12 nov) G1 sul conto vero: quale soglia (0,95 scritta, 0,90, 0,80 del brief) e con quale costo degli ordini limite; tetto per
  moneta o perdita giornaliera massima; capitale minimo (sotto circa 220 USDT G1 rende meno).
- (12 nov, prova 96) Il limite di 2 ore attorno agli eventi macro vale per le strategie su quegli eventi? Soglia a eventi 0,01 o 0,00038.

## Note di metodo
- Mai il `main` delle prove (riscrive i risultati): importare le funzioni (voce 11). L'auditor non committa (11 nov).
- Copia troncata: ordine dei commit con `gh api` (voce 17); mai `grep -r research/`. Script: `PYTHONPATH=<radice> python3
  audits/repro/<script>.py`. `ARCHIVE.md` non esiste ancora. BTCORA: `repro/btcora_*`.
