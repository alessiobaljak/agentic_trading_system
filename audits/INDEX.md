# Indice della memoria dell'auditor (massimo 40 righe)

Aggiornato: 2026-11-11. Leggere all'inizio di ogni invocazione questo file e `KNOWN_PITFALLS.md`; il resto solo se serve.

## Stato degli audit per strategia
| Strategia | Ultimo audit | Verdetto | Note |
|---|---|---|---|
| BTCORA (collaudo, `research/prova_finta_audit/`) | 2026-11-07 | FAIL | prova finta per collaudare l'audit; sguardo nel futuro e funding assente |
| Prova 28: K2, F5 + M7 + K2 (riesame) | 2026-11-11 | PASS tecnico | Alti: Sharpe corretto 0,75/0,47 con N = conto, 0,89/0,69 con N = gruppi; regole: «non candidate» |
| Prova 113: N3G, monete gratis (riesame) | 2026-11-11 | PASS tecnico del «no» | corretta p 0,0268 (serve 0,01); Alto: eventi della 32 da rifare (19 persi); tocca anche N3 nel paper |
| G1 (demo, candidata ai soldi veri) | mai | — | **da fare**: il primo avvio prevede l'audit completo di G1 (`research/programma7/PRIMA.md`, `revisione_g1n/`, `bot/portafoglio/f5.py`, demo); escluso dal brief del 7 nov 2026 |
| G11, G1N, F5, eventi (paper) | mai | — | da elencare con lo stato al prossimo avvio completo |
| Vecchie strategie `bot/strategies/` (ferme dal 13 ott 2026) | mai | — | solo elenco con lo stato |

## Cosa contiene ogni file
- `KNOWN_PITFALLS.md`: errori trovati in questo repo, con file e schema da cercare. Sempre.
- `AUDIT_LOG.md`: una riga per audit (data, strategia, commit, verdetto, rapporto). Per sapere se una strategia è già stata vista.
- `ARCHIVE.md`: non esiste ancora; ci vanno le voci chiuse oltre le ultime 10 del registro.
- `reports/AAAA-MM-GG-<strategia>.md`: rapporto completo. Da leggere solo DOPO aver formato il verdetto, per i problemi tornati.
- `repro/`: script che riproducono i controlli e i problemi; `repro/*_esito.json` i numeri ottenuti.
  - `repro/btcora_2026-11-07.py`: BTCORA; modello per prove con segnale giornaliero e conto orario.
  - `repro/prova28_*.py` (11 nov): modello per le prove settimanali del programma 6 (pannello `seconda`, `terza.conto`):
    riproduzione, prova del taglio (anche per il modello M7), entrata oraria, conto unico compensato, perdita peggiore,
    filtri e capitale dichiarato, sensibilità, Sharpe corretto nei due metodi. M7 si rifà in 3 minuti
    (`prova28_m7_2026-11-11.py <cartella>`).
  - `repro/prova113_2026-11-11.py` (11 nov): modello per le prove a eventi su candele orarie (32, 113): etichette dagli annunci,
    simboli riusati, funding nella tenuta, ore mancanti scaricate in cartella temporanea (catalogo, voce 25), sensibilità.

## Decisioni aperte per Alessio
- (7 nov) Minimo di anni e di operazioni per giudicare una prova; perdita giornaliera massima del 5% da simulare o no
  (11 nov: K2 la supera 3 volte). Costi confermati dal proprietario il 7 novembre (0,05%, 0,02%, scarto 0,01%/0,02%).
- (11 nov) Quale N nello Sharpe corretto dell'esame del 9 novembre (conto delle prove o gruppi); se il riesame può rendere
  candidata una «costruzione» che le sue regole escludono; se l'esclusione della famiglia del funding vale per le miscele.
  Prove a eventi: minimo di eventi; esame della misura in avanti delle monete gratis da scrivere prima dei dati nuovi.

## Note di metodo
- Non eseguire il `main` delle prove che riscrive i risultati: importare le funzioni (vedi `KNOWN_PITFALLS.md`, voce 11).
- `audits/` è nel repository (11 nov 2026): l'auditor non committa, lo fa la sessione principale.
- Copia locale troncata: l'ordine dei commit si verifica con `gh api` sul remoto (catalogo, voce 17). Mai `grep -r research/`.
- Script di audit: `PYTHONPATH=<radice> python3 audits/repro/<script>.py`.
