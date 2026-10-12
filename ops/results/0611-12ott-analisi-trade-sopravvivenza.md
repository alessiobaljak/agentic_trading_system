# 0611-12ott-analisi-trade-sopravvivenza.req

_eseguito: 2026-10-12 19:07 UTC_

**richiesta:** `sopravvivenza`
**eseguito:** `.venv/bin/python -m scripts.survivorship_report`
**esito:** codice 0 in 53.5s

```
[surv] elenco dei simboli con dati STORICI su data.binance.vision…
[surv] perpetual *USDT mai esistiti: 900
[surv] dato ogni simboli la finestra dei dati (una richiesta ciascuno, 16 in parallelo)…

    …100/900
    …200/900
    …300/900
    …400/900
    …500/900
    …600/900
    …700/900
    …800/900
    …900/900

[surv] datati: 900/900
[surv] ancora VIVI (dati fino a 2026-09 o 2026-10): 869
[surv] DELISTATI (dati interrotti prima): 31
[surv] di cui delistati DOPO 2022-01 (dentro la finestra del gate): 28

[surv] QUOTA INVISIBILE AL GATE: 28 su 897 simboli attivi nella finestra = 3.1%

[surv] esempi di coin nate e morte dentro la finestra:
    AERGOUSDT            2024-09 → 2026-06
    BTCSTUSDT            2021-03 → 2026-06
    SXPUSDT              2020-07 → 2026-05
    BDXNUSDT             2025-06 → 2026-03
    EOSUSDT              2020-01 → 2025-05
    FRONTUSDT            2023-09 → 2024-09
    MATICUSDT            2020-10 → 2024-09
    GALUSDT              2022-05 → 2024-07
    RNDRUSDT             2023-02 → 2024-07
    ANTUSDT              2021-12 → 2024-05
    AUDIOUSDT            2021-08 → 2024-05
    BLUEBIRDUSDT         2022-11 → 2024-05
    BTSUSDT              2021-02 → 2024-05
    COCOSUSDT            2023-02 → 2024-05
    FOOTBALLUSDT         2022-09 → 2024-05

[surv] VERDETTO: bias MARGINALE. Documentarlo e proseguire: costruire
       la pipeline dei delistati non ripagherebbe il lavoro.

[surv] NB: non vogliamo TRADARE le coin morte — vogliamo che il gate le
       abbia viste morire, cosi' le sue statistiche includono i peggiori esiti.
```
