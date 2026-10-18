# 0627-18ott-esporta-storia-chiusura.req

_eseguito: 2026-10-18 11:16 UTC_

**richiesta:** `esporta-storia`
**eseguito:** `.venv/bin/python -m scripts.esporta_storia`
**esito:** codice 0 in 121.8s

```
[firebase] connesso (Firestore + RTDB)
[esporta] piano: data/voto_t: 4 file, 0 MB non compressi (fatta)
[esporta] piano: data/replay_gate: 1149 file, 0 MB non compressi (fatta)
[esporta] piano: data/gate_storia: 1 file, 25 MB non compressi (fatta)
[esporta] piano: data/gruppo_controllo: 239 file, 43 MB non compressi (fatta)
[esporta] piano: data/selettore: 1261 file, 2785 MB non compressi (da fare)
[esporta] macchina/backup_radice.tar.gz: 2 voci, 0.2 MB
[esporta] macchina/selettore_parte10.tar.gz: 18 voci, 14.1 MB
Archivio in ops/results/archivio_20261018 (2026-10-18 11:16 UTC): COMPLETO
file: 58 (2 scritti in questo giro) · 191.6 MB compressi · letture Firestore in questo giro: 0 (tetto 20000)

  macchina/gate_storia.tar.gz                            ? voci    4075.3 kB  sha256 352ec19c730c
  macchina/gruppo_controllo.tar.gz                       ? voci   13079.2 kB  sha256 88fc16a9ea1d
  macchina/replay_gate.tar.gz                            ? voci      65.2 kB  sha256 bda4b9827adf
  firestore/_healthcheck.json.gz                         ? voci       0.1 kB  sha256 d0ef7d84b054
  firestore/ai_hypotheses.json.gz                        ? voci       1.0 kB  sha256 56ab73fba67b
  firestore/ai_shadow.json.gz                            ? voci      69.8 kB  sha256 58d31f07c291
  firestore/ai_spesa.json.gz                             ? voci       0.7 kB  sha256 c18a2055ad61
  firestore/asset_scores.json.gz                         ? voci       1.9 kB  sha256 fdaa74415639
  firestore/calibration.json.gz                          ? voci       0.5 kB  sha256 10a8f502906f
  firestore/dashboard.json.gz                            ? voci      35.9 kB  sha256 0ce36cd0e628
  firestore/discover_shards.json.gz                      ? voci       1.7 kB  sha256 1f0ba8f18fe5
  firestore/discovered_strategies.json.gz                ? voci      39.9 kB  sha256 1b5769622c0b
  firestore/drift.json.gz                                ? voci      19.9 kB  sha256 7fe42830b1c4
  firestore/gate_autopsy.json.gz                         ? voci       2.4 kB  sha256 93c66f9a9c62
  firestore/gate_history.json.gz                         ? voci       8.9 kB  sha256 cc2631c31515
  firestore/giorni.json.gz                               ? voci       1.9 kB  sha256 3260bab0a93e
  firestore/insights.json.gz                             ? voci       2.3 kB  sha256 c19a03cbf072
  firestore/learning.json.gz                             ? voci      19.6 kB  sha256 7f197be6fb48
  firestore/memory.json.gz                               ? voci      34.2 kB  sha256 4faff00f6872
  firestore/optimize_shards.json.gz                      ? voci       1.1 kB  sha256 a3cf70359643
  firestore/portfolio.json.gz                            ? voci       3.6 kB  sha256 ce061a220e94
  firestore/report_giornaliero.json.gz                   ? voci      35.0 kB  sha256 d36c2ecbbb7d
  firestore/segnali_rifiutati.json.gz                    ? voci      48.1 kB  sha256 033eec7a3dbb
  firestore/selector.json.gz                             ? voci       1.4 kB  sha256 d629868df9ac
  firestore/strategy_params.json.gz                      ? voci      83.1 kB  sha256 b505e18a9671
  firestore/strategy_registry.json.gz                    ? voci      92.5 kB  sha256 45c73838e160
  firestore/strategy_weights.json.gz                     ? voci     389.3 kB  sha256 7c0b0a032051
  firestore/supervisor.json.gz                           ? voci       0.5 kB  sha256 b9252975b474
  firestore/trades.json.gz                               ? voci     938.0 kB  sha256 96dc297c2942
  rtdb/_healthcheck.json.gz                              ? voci       0.0 kB  sha256 f753aa988ce1
  rtdb/account.json.gz                                   ? voci       0.1 kB  sha256 27c73dbbcad0
  rtdb/adapt_state.json.gz                               ? voci       1.4 kB  sha256 8953596ca413
  rtdb/avvii.json.gz                                     ? voci       0.2 kB  sha256 b775de7f754b
  rtdb/avvii_config.json.gz                              ? voci       1.0 kB  sha256 67ffa15b6fb7
  rtdb/backlog.json.gz                                   ? voci       9.6 kB  sha256 1ae05f3b184d
  rtdb/bot_status.json.gz                                ? voci       0.3 kB  sha256 82048cfd7375
  rtdb/btc_history.json.gz                               ? voci       2.5 kB  sha256 b1a7ad92919c
  rtdb/commands.json.gz                                  ? voci       0.5 kB  sha256 293e4e048892
  rtdb/controllo.json.gz                                 ? voci       5.7 kB  sha256 4b8469cfb212
  rtdb/decision_status.json.gz                           ? voci       0.3 kB  sha256 fb1bff6376d8
  rtdb/gate.json.gz                                      ? voci      14.6 kB  sha256 c9a82085c2fe
  rtdb/giorni_fatti.json.gz                              ? voci       0.2 kB  sha256 2dfc3d37e4a8
  rtdb/learning_giorni.json.gz                           ? voci      40.1 kB  sha256 7df3f7c11dc0
  rtdb/learning_indice.json.gz                           ? voci       0.3 kB  sha256 a1ca4d87dbad
  rtdb/ops.json.gz                                       ? voci       0.1 kB  sha256 9a391b59d6f9
  rtdb/paper.json.gz                                     ? voci       3.4 kB  sha256 3b277cc27ba3
  rtdb/positions.json.gz                                 ? voci       7.2 kB  sha256 dfb1486a8196
  rtdb/regime_history.json.gz                            ? voci       0.6 kB  sha256 67cb4d38cf0a
  rtdb/report_giornaliero.json.gz                        ? voci       6.0 kB  sha256 42eb8c4eecb1
  rtdb/risk_state.json.gz                                ? voci       0.2 kB  sha256 65e9816a27d5
  macchina/selettore_parte1.tar.gz                     282 voci   39176.3 kB  sha256 937f8c8d15f0
  macchina/selettore_parte2.tar.gz                     175 voci   39777.2 kB  sha256 8a1dc76dbb62
  macchina/file_sciolti.tar.gz                           2 voci       7.4 kB  sha256 0d82ccc8a975
  macchina/voto_t.tar.gz                                 4 voci      11.2 kB  sha256 b5d244288454
  macchina/selettore_parte3.tar.gz                     160 voci   39573.6 kB  sha256 8a40253fd989
  macchina/selettore_parte4.tar.gz                     122 voci   39616.4 kB  sha256 09bd492a3057
  macchina/backup_radice.tar.gz                          2 voci     219.1 kB  sha256 9f3f9f200dc6
  macchina/selettore_parte10.tar.gz                     18 voci   14081.5 kB  sha256 14d8dcb1a0cd

RIMASTI FUORI (con il motivo):
  macchina/selettore_parte5.tar.gz: 121 file, 299 MB non compressi (circa 42 compressi, stima): oltre il tetto dell'archivio (200 MB); restano sulla macchina, in data/selettore
  macchina/selettore_parte6.tar.gz: 118 file, 294 MB non compressi (circa 41 compressi, stima): oltre il tetto dell'archivio (200 MB); restano sulla macchina, in data/selettore
  macchina/selettore_parte7.tar.gz: 97 file, 293 MB non compressi (circa 41 compressi, stima): oltre il tetto dell'archivio (200 MB); restano sulla macchina, in data/selettore
  macchina/selettore_parte8.tar.gz: 95 file, 300 MB non compressi (circa 42 compressi, stima): oltre il tetto dell'archivio (200 MB); restano sulla macchina, in data/selettore
  macchina/selettore_parte9.tar.gz: 73 file, 299 MB non compressi (circa 42 compressi, stima): oltre il tetto dell'archivio (200 MB); restano sulla macchina, in data/selettore
```
