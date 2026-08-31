# 0024-log-gate.req

_eseguito: 2026-08-31 10:55 UTC_

**richiesta:** `log-gate`
**eseguito:** `journalctl -u trading-optimizer.service -n 80 --no-pager`
**esito:** codice 0 in 0.9s

```
Aug 31 10:39:05 Trading-Agent python[632816]: [backtest] dati da cache: 78851 candele (TURBOUSDT 15m)
Aug 31 10:39:11 Trading-Agent python[632753]: [backtest] dati da cache: 29335 candele (KITEUSDT 15m)
Aug 31 10:39:14 Trading-Agent python[632753]: [backtest] dati da cache: 116383 candele (1000FLOKIUSDT 15m)
Aug 31 10:39:42 Trading-Agent python[632795]: [backtest] dati da cache: 54477 candele (TSTUSDT 15m)
Aug 31 10:39:58 Trading-Agent python[632858]: [backtest] dati da cache: 68499 candele (NEIROUSDT 15m)
Aug 31 10:40:11 Trading-Agent python[632732]: [backtest] dati da cache: 6194 candele (CAPUSDT 15m)
Aug 31 10:40:11 Trading-Agent python[632732]: [backtest] dati da cache: 28087 candele (JCTUSDT 15m)
Aug 31 10:40:14 Trading-Agent python[632732]: [backtest] dati da cache: 163489 candele (COMPUSDT 15m)
Aug 31 10:40:19 Trading-Agent python[632774]: [backtest] dati da cache: 163489 candele (AXSUSDT 15m)
Aug 31 10:41:40 Trading-Agent python[632795]: [backtest] dati da cache: 17153 candele (MANTRAUSDT 15m)
Aug 31 10:41:41 Trading-Agent python[632795]: [backtest] dati da cache: 63395 candele (GRASSUSDT 15m)
Aug 31 10:41:59 Trading-Agent python[632816]: [backtest] dati da cache: 34221 candele (OPENUSDT 15m)
Aug 31 10:42:00 Trading-Agent python[632816]: [backtest] dati da cache: 33173 candele (BARDUSDT 15m)
Aug 31 10:42:03 Trading-Agent python[632816]: [backtest] dati da cache: 163489 candele (CHZUSDT 15m)
Aug 31 10:42:03 Trading-Agent python[632837]: [backtest] dati da cache: 16077 candele (CFGUSDT 15m)
Aug 31 10:42:05 Trading-Agent python[632837]: [backtest] dati da cache: 60329 candele (MOVEUSDT 15m)
Aug 31 10:42:25 Trading-Agent python[632858]: [backtest] dati da cache: 34607 candele (PTBUSDT 15m)
Aug 31 10:42:26 Trading-Agent python[632858]: [backtest] dati da cache: 51018 candele (MUBARAKUSDT 15m)
Aug 31 10:43:04 Trading-Agent python[632753]: [backtest] dati da cache: 50653 candele (BROCCOLI714USDT 15m)
Aug 31 10:43:17 Trading-Agent python[632879]: [backtest] dati da cache: 156133 candele (APEUSDT 15m)
Aug 31 10:43:53 Trading-Agent python[632795]: [backtest] dati da cache: 19361 candele (ESPUSDT 15m)
Aug 31 10:43:54 Trading-Agent python[632795]: [backtest] dati da cache: 33847 candele (UBUSDT 15m)
Aug 31 10:43:55 Trading-Agent python[632795]: [backtest] dati da cache: 46527 candele (SXTUSDT 15m)
Aug 31 10:44:08 Trading-Agent python[632837]: [backtest] dati da cache: 42205 candele (SPKUSDT 15m)
Aug 31 10:44:15 Trading-Agent python[632858]: [backtest] dati da cache: 28073 candele (ALLOUSDT 15m)
Aug 31 10:44:15 Trading-Agent python[632858]: [backtest] dati da cache: 20427 candele (GWEIUSDT 15m)
Aug 31 10:44:16 Trading-Agent python[632858]: [backtest] dati da cache: 50556 candele (BROCCOLIF3BUSDT 15m)
Aug 31 10:45:02 Trading-Agent python[632753]: [backtest] dati da cache: 101031 candele (BIGTIMEUSDT 15m)
Aug 31 10:45:37 Trading-Agent python[632795]: [backtest] dati da cache: 163489 candele (TRBUSDT 15m)
Aug 31 10:45:44 Trading-Agent python[632837]: [backtest] dati da cache: 19632 candele (TRIAUSDT 15m)
Aug 31 10:45:46 Trading-Agent python[632837]: [backtest] dati da cache: 139341 candele (1000LUNCUSDT 15m)
Aug 31 10:45:56 Trading-Agent python[632732]: [backtest] dati da cache: 97625 candele (KASUSDT 15m)
Aug 31 10:46:06 Trading-Agent python[632858]: [backtest] dati da cache: 31055 candele (METUSDT 15m)
Aug 31 10:46:07 Trading-Agent python[632858]: [backtest] dati da cache: 60336 candele (KOMAUSDT 15m)
Aug 31 10:46:17 Trading-Agent python[632774]: [backtest] dati da cache: 56315 candele (MELANIAUSDT 15m)
Aug 31 10:47:34 Trading-Agent python[632816]: [backtest] dati da cache: 124853 candele (MINAUSDT 15m)
Aug 31 10:48:03 Trading-Agent python[632858]: [backtest] dati da cache: 163393 candele (MANAUSDT 15m)
Aug 31 10:53:18 Trading-Agent python[632707]: [discover] XRPUSDT: 1 coppie passate ✅
Aug 31 10:53:18 Trading-Agent python[632707]: [discover] TRUMPUSDT: 1 coppie passate ✅
Aug 31 10:53:18 Trading-Agent python[632707]: [discover] ENAUSDT: 2 coppie passate ✅
Aug 31 10:53:18 Trading-Agent python[632707]: [discover] PROMUSDT: 1 coppie passate ✅
Aug 31 10:53:18 Trading-Agent python[632707]: [discover] BTRUSDT: 1 coppie passate ✅
Aug 31 10:53:18 Trading-Agent python[632707]: [discover] ZORAUSDT: 2 coppie passate ✅
Aug 31 10:53:18 Trading-Agent python[632707]: [discover] XMRUSDT: 1 coppie passate ✅
Aug 31 10:53:18 Trading-Agent python[632707]: [discover] ZKUSDT: 1 coppie passate ✅
Aug 31 10:53:18 Trading-Agent python[632707]: [discover] DOTUSDT: 13 coppie passate ✅
Aug 31 10:53:18 Trading-Agent python[632707]: [discover] XPLUSDT: 1 coppie passate ✅
Aug 31 10:53:18 Trading-Agent python[632707]: [discover] DEXEUSDT: 1 coppie passate ✅
Aug 31 10:53:18 Trading-Agent python[632707]: [discover] JTOUSDT: 1 coppie passate ✅
Aug 31 10:53:18 Trading-Agent python[632707]: [discover] BICOUSDT: 1 coppie passate ✅
Aug 31 10:53:18 Trading-Agent python[632707]: [discover] STXUSDT: 3 coppie passate ✅
Aug 31 10:53:18 Trading-Agent python[632707]: [discover] MOVRUSDT: 1 coppie passate ✅
Aug 31 10:53:18 Trading-Agent python[632707]: [discover] EGLDUSDT: 1 coppie passate ✅
Aug 31 10:53:18 Trading-Agent python[632707]: [discover] USELESSUSDT: 7 coppie passate ✅
Aug 31 10:53:18 Trading-Agent python[632707]: [discover] SPXUSDT: 1 coppie passate ✅
Aug 31 10:53:18 Trading-Agent python[632707]: [discover] JUPUSDT: 1 coppie passate ✅
Aug 31 10:53:18 Trading-Agent python[632707]: [discover] VETUSDT: 1 coppie passate ✅
Aug 31 10:53:18 Trading-Agent python[632707]: [discover] ORCAUSDT: 10 coppie passate ✅
Aug 31 10:53:18 Trading-Agent python[632707]: [discover] EIGENUSDT: 1 coppie passate ✅
Aug 31 10:53:18 Trading-Agent python[632707]: [discover] SEIUSDT: 1 coppie passate ✅
Aug 31 10:53:18 Trading-Agent python[632707]: [discover] TREEUSDT: 2 coppie passate ✅
Aug 31 10:53:18 Trading-Agent python[632707]: [discover] GPSUSDT: 3 coppie passate ✅
Aug 31 10:53:18 Trading-Agent python[632707]: [discover] RENDERUSDT: 1 coppie passate ✅
Aug 31 10:53:18 Trading-Agent python[632707]: [discover] SKYAIUSDT: 5 coppie passate ✅
Aug 31 10:53:18 Trading-Agent python[632707]: [discover] HUMAUSDT: 13 coppie passate ✅
Aug 31 10:53:18 Trading-Agent python[632707]: [discover] PLUMEUSDT: 1 coppie passate ✅
Aug 31 10:53:18 Trading-Agent python[632707]: [discover] HEIUSDT: 4 coppie passate ✅
Aug 31 10:53:18 Trading-Agent python[632707]: [discover] TSTUSDT: 1 coppie passate ✅
Aug 31 10:53:18 Trading-Agent python[632707]: [discover] AXSUSDT: 1 coppie passate ✅
Aug 31 10:53:18 Trading-Agent python[632707]: [discover] MUBARAKUSDT: 3 coppie passate ✅
Aug 31 10:53:18 Trading-Agent python[632707]: [discover] BROCCOLIF3BUSDT: 1 coppie passate ✅
Aug 31 10:53:18 Trading-Agent python[632707]: [autopsy] 89/48720 passate · muoiono su: total_return 34518 · regime 6727 · recovery 3761 · trades 1411 · consistency 1223
Aug 31 10:53:18 Trading-Agent python[632707]: [autopsy] quasi-passaggi (semi per le mutazioni del prossimo run): 40
Aug 31 10:53:19 Trading-Agent python[632707]: ============================================================
Aug 31 10:53:19 Trading-Agent python[632707]: [discover] 48720 valutazioni, 89 coppie nuove passate in QUESTO run.
Aug 31 10:53:19 Trading-Agent python[632707]: [discover] coppie validate totali nel registro (base+generate): 0
Aug 31 10:53:19 Trading-Agent python[632707]: ============================================================
Aug 31 10:53:19 Trading-Agent systemd[1]: trading-optimizer.service: Deactivated successfully.
Aug 31 10:53:19 Trading-Agent systemd[1]: Finished trading-optimizer.service - Agentic Trading - GATE 1 (optimize + discover, dati reali, autonomo).
Aug 31 10:53:19 Trading-Agent systemd[1]: trading-optimizer.service: Consumed 13h 21min 40.455s CPU time.
```
