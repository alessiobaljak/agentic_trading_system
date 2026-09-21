# 0129-storico-oi-validate.req

_eseguito: 2026-09-21 07:03 UTC_

**richiesta:** `storico-oi`
**eseguito:** `.venv/bin/python -m scripts.binance_metrics_probe`
**esito:** codice 0 in 26.3s

```
[firebase] connesso (Firestore + RTDB)
========================================================================
STORICO «metrics» DI BINANCE VISION · 26 coppie · finestra 2022-01-01 → 2026-09-20
========================================================================
[metrics] leggo il listing S3 (nessun download: le dimensioni sono gia' li')…

coppia          primo dato   ultimo       gg dal 2022-01-01  copertura     MiB
------------------------------------------------------------------------
DOTUSDT         2021-12-01   2026-09-20             1724       100%    18.5
EGLDUSDT        2021-12-01   2026-09-20             1724       100%    17.7
VETUSDT         2021-12-01   2026-09-20             1724       100%    18.5
JASMYUSDT       2022-04-20   2026-09-20             1615        94%    17.8
STXUSDT         2023-02-21   2026-09-20             1307        76%    14.0
SEIUSDT         2023-08-17   2026-09-20             1131        66%    12.0
BICOUSDT        2023-09-28   2026-09-20             1089        63%    11.2
JTOUSDT         2023-12-08   2026-09-20             1018        59%    10.6
ZKUSDT          2024-06-17   2026-09-20              826        48%     8.7
NEIROUSDT       2024-09-16   2026-09-20              735        43%     8.3
SCRUSDT         2024-10-22   2026-09-20              699        41%     7.2
ORCAUSDT        2024-12-06   2026-09-20              654        38%     6.7
SPXUSDT         2024-12-10   2026-09-20              650        38%     6.7
DEXEUSDT        2024-12-24   2026-09-20              636        37%     6.7
PROMUSDT        2025-01-15   2026-09-20              614        36%     6.2
TRUMPUSDT       2025-01-18   2026-09-19              610        35%     6.7
HEIUSDT         2025-02-13   2026-09-20              585        34%     6.1
GPSUSDT         2025-02-17   2026-09-20              581        34%     6.1
MUBARAKUSDT     2025-03-17   2026-09-20              553        32%     5.9
TUTUSDT         2025-03-20   2026-09-20              550        32%     5.8
SYRUPUSDT       2025-05-07   2026-09-20              502        29%     5.2
SKYAIUSDT       2025-05-13   2026-09-20              496        29%     5.1
SAHARAUSDT      2025-06-26   2026-09-20              452        26%     4.7
USELESSUSDT     2025-08-15   2026-09-20              402        23%     4.2
HEMIUSDT        2025-08-29   2026-09-20              388        23%     4.1
QUSDT           2025-09-02   2026-09-20              384        22%     4.0
------------------------------------------------------------------------

[metrics] coppie con dati dall'inizio della finestra (2022-01-01): 3 su 26
[metrics] coppie con dati (anche piu' recenti): 26
[metrics] PESO SUL DISCO, compresso, tutta la finestra: 228.7 MiB
[metrics] 21649 file giornalieri in tutto (~11 KiB l'uno)
[metrics] coppie con giorni MANCANTI dentro il loro storico: 2
     STXUSDT        1 buchi (es. 2023-12-08)
     TRUMPUSDT      1 buchi (es. 2026-09-20)

[metrics] provo il lettore su 2 giorni per coppia (download vero, con checksum)…
[metrics] righe lette: 11800 · compresso 0.46 MiB → csv 1.42 MiB (×3.1)
[metrics] proiezione dello SCOMPATTATO su tutta la finestra: ~705 MiB
[metrics] nessun file illeggibile nel campione.

========================================================================
Questo comando MISURA e basta: non scrive niente e non cambia il gate.
Serve a decidere se vale la pena costruirci una feature — decisione
che resta aperta finche' il paper non chiude i 40 trade.
```
