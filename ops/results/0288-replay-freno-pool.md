# 0288-replay-freno-pool.req

_eseguito: 2026-09-27 05:59 UTC_

**richiesta:** `replay`
**eseguito:** `.venv/bin/python -m scripts.replay_freno`
**esito:** codice 0 in 9.5s

```
[firebase] connesso (Firestore + RTDB)
REPLAY DEL FRENO PER GRUPPO (26 set 2026, passo 4) — sola lettura
  soglie COSTANTI (bot/learning/drift.py, bot/config.py): CUSUM h=4R k=0, ripresa 2.5R, SPRT p0=0.45 p1=0.25 alpha=beta=0.05
  LA REGOLA: il replay puo' solo BOCCIARE le soglie, mai sceglierle. Un pool che suona DOPO il freno globale e' inutile;
  piu' di 5 allarmi ogni 100 trade sani del gate = h troppo basso. Nessuna soglia si sposta «finche' torna».
  trade del paper: 110 (validate, esiti esterni fuori) dal 2026-09-16 al 2026-09-27; con R calcolabile 71 (R = pnl / (|entry - stop originale| x size); senza stop originale il trade si salta)
  freno globale: acceso il 2026-09-25 (fonte: drift/current.global.dal)

PER POOL (famiglia x regime all'ingresso; direzione x contesto BTC, «ignoto» escluso):
  pool                              n   rif R  R medio  CUSUM suona     vs globale allarmi     SPRT     quando    PnL 7g dopo  verdetto
  dir:long|btc_giu                  7   +0.37    -0.24   2026-09-27     1.8 g DOPO       1 continue        mai   +0.00 (0 tr)  BOCCIATO qui: suona dopo il globale (inutile)
  dir:long|btc_su                   7   +0.37    -0.22   2026-09-27     1.8 g DOPO       1 continue        mai   +0.43 (1 tr)  BOCCIATO qui: suona dopo il globale (inutile)
  dir:short|btc_giu                 9   +0.37    -0.15   2026-09-26     1.3 g DOPO       1 continue        mai   +2.78 (3 tr)  BOCCIATO qui: suona dopo il globale (inutile)
  dir:short|btc_su                  3   +0.37    -0.12          mai              —       0 continue        mai              —  non suona
  fam:momentum|bear_trending        1   +0.41    -1.09          mai              —       0 continue        mai              —  non suona
  fam:momentum|high_uncertainty     3   +0.41    -0.06          mai              —       0 continue        mai              —  non suona
  fam:reversion|bear_trending       8   +0.36    -0.29   2026-09-26     1.0 g DOPO       1 continue        mai   +1.21 (1 tr)  BOCCIATO qui: suona dopo il globale (inutile)
  fam:reversion|bull_trending      32   +0.36    -0.24   2026-09-25     0.1 g DOPO       1   reject 2026-09-25 -10.50 (24 tr)  BOCCIATO qui: suona dopo il globale (inutile)
  fam:reversion|high_uncertainty   13   +0.36    +0.05   2026-09-25     0.1 g DOPO       1 continue        mai   +3.50 (6 tr)  BOCCIATO qui: suona dopo il globale (inutile)
  fam:reversion|sideways           14   +0.36    -0.10   2026-09-25    0.0 g PRIMA       1 continue        mai  -0.08 (10 tr)  suona prima; allarme utile (il pool ha poi perso)
  riferimento: media di (1-wr)*(PF-1) delle validate del pool
  lo SPRT e' solo registrato: il freno ascolta il CUSUM; qui si vede chi dei due avrebbe suonato prima.

ARL0 — falsi allarmi su storia SANA (trade OOS delle validate dal dataset del selettore, data/selettore/*.jsonl):
  pool                               n allarmi  per 100  verdetto (> 5 = h troppo basso)
  fam:momentum|bear_trending       101       4      4.0  regge
  fam:momentum|bull_trending        88       3      3.4  regge
  fam:momentum|high_uncertainty     93       3      3.2  regge
  fam:momentum|sideways            158       7      4.4  regge
  fam:reversion|bear_trending      902      32      3.5  regge
  fam:reversion|bull_trending      471      15      3.2  regge
  fam:reversion|high_uncertainty   275      11      4.0  regge
  fam:reversion|sideways           566      18      3.2  regge
  tutti i pool: 93 allarmi su 2654 trade-pool = 3.5 per 100 (un trade conta in ogni pool a cui appartiene)
```
