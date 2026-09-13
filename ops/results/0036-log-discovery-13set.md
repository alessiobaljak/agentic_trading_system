# 0036-log-discovery-13set.req

_eseguito: 2026-09-13 05:27 UTC_

**richiesta:** `log-gate`
**eseguito:** `journalctl -u trading-optimizer.service -n 80 --no-pager`
**esito:** codice 0 in 1.1s

```
Sep 13 04:57:46 Trading-Agent python[1182280]: [backtest] dati da cache: 89693 candele (STRKUSDT 15m)
Sep 13 04:57:59 Trading-Agent python[1182406]: [backtest] dati da cache: 164641 candele (GALAUSDT 15m)
Sep 13 04:59:55 Trading-Agent python[1182427]: [backtest] dati da cache: 33947 candele (BLESSUSDT 15m)
Sep 13 04:59:56 Trading-Agent python[1182427]: [backtest] dati da cache: 33555 candele (LIGHTUSDT 15m)
Sep 13 04:59:57 Trading-Agent python[1182427]: [backtest] dati da cache: 55629 candele (TSTUSDT 15m)
Sep 13 05:00:13 Trading-Agent python[1182301]: [backtest] dati da cache: 47083 candele (DOODUSDT 15m)
Sep 13 05:01:33 Trading-Agent python[1182280]: [backtest] dati da cache: 51886 candele (BRUSDT 15m)
Sep 13 05:01:52 Trading-Agent python[1182364]: [backtest] dati da cache: 34498 candele (0GUSDT 15m)
Sep 13 05:01:53 Trading-Agent python[1182385]: [backtest] dati da cache: 29043 candele (PIEVERSEUSDT 15m)
Sep 13 05:01:55 Trading-Agent python[1182385]: [backtest] dati da cache: 88933 candele (PORTALUSDT 15m)
Sep 13 05:01:55 Trading-Agent python[1182364]: [backtest] dati da cache: 164641 candele (RUNEUSDT 15m)
Sep 13 05:02:19 Trading-Agent python[1182301]: [backtest] dati da cache: 164737 candele (XTZUSDT 15m)
Sep 13 05:02:20 Trading-Agent python[1182427]: [backtest] dati da cache: 26941 candele (POWERUSDT 15m)
Sep 13 05:02:21 Trading-Agent python[1182427]: [backtest] dati da cache: 51501 candele (PARTIUSDT 15m)
Sep 13 05:03:00 Trading-Agent python[1182343]: [backtest] dati da cache: 89625 candele (GLMUSDT 15m)
Sep 13 05:03:06 Trading-Agent python[1182322]: [backtest] dati da cache: 61861 candele (ORCAUSDT 15m)
Sep 13 05:04:28 Trading-Agent python[1182280]: [backtest] dati da binance: 164737 candele
Sep 13 05:04:45 Trading-Agent python[1182427]: [backtest] dati da cache: 33365 candele (EDENUSDT 15m)
Sep 13 05:04:47 Trading-Agent python[1182427]: [backtest] dati da cache: 126573 candele (TUSDT 15m)
Sep 13 05:05:20 Trading-Agent python[1182406]: [backtest] dati da cache: 39700 candele (TAGUSDT 15m)
Sep 13 05:05:35 Trading-Agent python[1182385]: [backtest] dati da cache: 164641 candele (PEOPLEUSDT 15m)
Sep 13 05:06:10 Trading-Agent python[1182322]: [backtest] dati da cache: 102279 candele (BIGTIMEUSDT 15m)
Sep 13 05:06:50 Trading-Agent python[1182343]: [backtest] dati da cache: 45453 candele (HUMAUSDT 15m)
Sep 13 05:06:54 Trading-Agent python[1182406]: [backtest] dati da cache: 39321 candele (ESPORTSUSDT 15m)
Sep 13 05:08:22 Trading-Agent python[1182406]: [backtest] dati da cache: 61486 candele (SPXUSDT 15m)
Sep 13 05:08:26 Trading-Agent python[1182364]: [backtest] dati da cache: 51203 candele (WALUSDT 15m)
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] LSKUSDT: 1 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] SOLUSDT: 1 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] FLOCKUSDT: 2 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] RAYSOLUSDT: 1 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] GRIFFAINUSDT: 1 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] USELESSUSDT: 3 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] TRUMPUSDT: 4 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] XMRUSDT: 2 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] DOTUSDT: 3 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] SOPHUSDT: 1 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] STEEMUSDT: 1 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] PUNDIXUSDT: 2 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] XPLUSDT: 1 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] PENGUUSDT: 1 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] GPSUSDT: 2 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] MUBARAKUSDT: 8 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] TAUSDT: 3 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] BULLAUSDT: 5 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] HEMIUSDT: 7 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] JUPUSDT: 1 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] VETUSDT: 7 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] VIRTUALUSDT: 1 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] STXUSDT: 2 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] JTOUSDT: 2 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] TUTUSDT: 1 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] AEROUSDT: 1 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] CVCUSDT: 3 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] VELVETUSDT: 1 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] BANKUSDT: 1 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] SEIUSDT: 2 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] EGLDUSDT: 1 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] NEIROUSDT: 3 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] PHAUSDT: 1 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] BTRUSDT: 2 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] QUSDT: 4 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] RENDERUSDT: 2 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] OPENUSDT: 5 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] DEXEUSDT: 2 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] BICOUSDT: 2 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] ZORAUSDT: 1 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] PARTIUSDT: 1 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] ORCAUSDT: 14 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] HUMAUSDT: 15 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] SPXUSDT: 4 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [discover] WALUSDT: 3 coppie passate ✅
Sep 13 05:11:44 Trading-Agent python[1182254]: [autopsy] 131/69204 passate · muoiono su: total_return 47790 · regime 10124 · recovery 5876 · consistency 1980 · trades 1876
Sep 13 05:11:44 Trading-Agent python[1182254]: [autopsy] quasi-passaggi (semi per le mutazioni del prossimo run): 40
Sep 13 05:11:45 Trading-Agent python[1182254]: ============================================================
Sep 13 05:11:45 Trading-Agent python[1182254]: [discover] 69204 valutazioni, 131 coppie nuove passate in QUESTO run.
Sep 13 05:11:45 Trading-Agent python[1182254]: [discover] coppie validate totali nel registro (base+generate): 0
Sep 13 05:11:45 Trading-Agent python[1182254]: ============================================================
Sep 13 05:11:46 Trading-Agent systemd[1]: trading-optimizer.service: Deactivated successfully.
Sep 13 05:11:46 Trading-Agent systemd[1]: Finished trading-optimizer.service - Agentic Trading - GATE 1 (optimize + discover, dati reali, autonomo).
Sep 13 05:11:46 Trading-Agent systemd[1]: trading-optimizer.service: Consumed 15h 58min 12.586s CPU time.
```
