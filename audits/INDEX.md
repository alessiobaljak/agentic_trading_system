# Indice della memoria dell'auditor (massimo 40 righe)

Aggiornato: 2026-11-07. Leggere all'inizio di ogni invocazione questo file e `KNOWN_PITFALLS.md`; il resto solo se serve.

## Stato degli audit per strategia
| Strategia | Ultimo audit | Verdetto | Note |
|---|---|---|---|
| BTCORA (collaudo, `research/prova_finta_audit/`) | 2026-11-07 | FAIL | prova finta per collaudare l'audit; sguardo nel futuro e funding assente |
| G1 (demo, candidata ai soldi veri) | mai | — | **da fare**: il primo avvio prevede l'audit completo di G1 (`research/programma7/PRIMA.md`, `revisione_g1n/`, `bot/portafoglio/f5.py`, demo); escluso dal brief del 7 nov 2026 |
| G11, G1N, F5, eventi (paper) | mai | — | da elencare con lo stato al prossimo avvio completo |
| Vecchie strategie `bot/strategies/` (ferme dal 13 ott 2026) | mai | — | solo elenco con lo stato |

## Cosa contiene ogni file
- `KNOWN_PITFALLS.md`: errori trovati in questo repo, con file e schema da cercare. Sempre.
- `AUDIT_LOG.md`: una riga per audit (data, strategia, commit, verdetto, rapporto). Per sapere se una strategia è già stata vista.
- `ARCHIVE.md`: non esiste ancora; ci vanno le voci chiuse oltre le ultime 10 del registro.
- `reports/AAAA-MM-GG-<strategia>.md`: rapporto completo. Da leggere solo DOPO aver formato il verdetto, per i problemi tornati.
- `repro/`: script che riproducono i controlli e i problemi; `repro/*_esito.json` i numeri ottenuti.
  - `repro/btcora_2026-11-07.py`: riproduzione BTCORA, controlli dei dati e del funding, varianti senza gli errori, sensibilità.
    Utile come modello per prove con segnale giornaliero e conto orario.

## Decisioni aperte per Alessio (dal rapporto del 2026-11-07)
- Commissioni (0,05% / 0,02% per lato) e scarto di prezzo (0,01% / 0,02%) da confermare con il conto Binance.
- Minimo di anni e di operazioni per giudicare una prova; perdita giornaliera massima del 5% da simulare o no.

## Note di metodo
- Non eseguire il `main` delle prove che riscrive i risultati: importare le funzioni (vedi `KNOWN_PITFALLS.md`, voce 11).
- La cartella `audits/` al 7 nov 2026 non è committata: lo decide la sessione principale.
