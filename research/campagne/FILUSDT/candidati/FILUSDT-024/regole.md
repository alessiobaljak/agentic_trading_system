# Candidato FILUSDT-024 — stagionalità della fascia di 4 ore, short (SCARTATO in Fase 4)

| | Regola |
|---|---|
| Moneta | FILUSDT |
| Timeframe | 4 ore (6 fasce al giorno, UTC) |
| Direzione | short |
| Ingresso | alla chiusura della barra i: per la fascia oraria della barra i+1, media e t dei rendimenti open→close delle ultime 30 barre di quella fascia; se t < −1,5 → short all'apertura della barra i+1 |
| Stop | close + 1,5 × ATR(14) |
| Target | nessuno |
| Uscita | dopo 1 barra |
| Dimensione e leva | rischio 1%, leva fra 1 e 2, margine isolato (regole del bot) |

**Motivo economico.** Heston, Korajczyk, Sadka (2010): i flussi che si ripetono alla stessa ora
del giorno rendono periodici i rendimenti di quella fascia.

**Esito della Fase 4 (2026-10-09): SCARTATO.** Costi doppi: R medio −0,009 (non positivo).
Ritardo di una barra: `t` −0,31 contro la (b) (crollo atteso dal disegno: col ritardo il trade
cade nella fascia sbagliata; nessun lookahead trovato). Superate robustezza, timeframe adiacenti,
stabilità, trade estremi, liquidazione. La variante long della stessa idea (FILUSDT-023) va
nettamente nel verso opposto.

Codice: `codice/varianti.py`, funzione `i12("short", ...)`.
