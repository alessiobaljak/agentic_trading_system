# 0588-11ott-settimanale-log-gate.req

_eseguito: 2026-10-11 03:47 UTC_

**richiesta:** `log-gate`
**eseguito:** `journalctl -u trading-optimizer.service -n 80 --no-pager`
**esito:** codice 0 in 0.1s

```
Oct 11 03:00:27 Trading-Agent python[2434739]: [discover] QUSDT|gen_3595f15b (variante di gen_18c839a0, intorno:atr_mult_stop=2.5): conferme retroattive 2/2 -> VALIDATA oggi
Oct 11 03:00:53 Trading-Agent python[2434739]: [backtest] cache riusata (tagliata da 2026-10-10): 96425 candele (XAIUSDT 15m)
Oct 11 03:01:18 Trading-Agent python[2434760]: [discover] ASTERUSDT|gen_e4423db0 (variante di gen_1390f7aa, intorno:rsi_extreme.high=75): conferme retroattive 2/2 -> VALIDATA oggi
Oct 11 03:02:21 Trading-Agent python[2434760]: [discover] ASTERUSDT|gen_34bf3d21 (variante di gen_1390f7aa, intorno:trend_strength.adx_lo=22): conferme retroattive 2/2 -> VALIDATA oggi
Oct 11 03:02:54 Trading-Agent python[2434739]: [backtest] cache riusata (tagliata da 2026-10-10): 61963 candele (GRIFFAINUSDT 15m)
Oct 11 03:03:25 Trading-Agent python[2434760]: [discover] ASTERUSDT|gen_6f9976e1 (variante di gen_1390f7aa, intorno:htf_fade.htf_gap=0): conferme retroattive 2/2 -> VALIDATA oggi
Oct 11 03:03:30 Trading-Agent python[2434718]: [backtest] cache riusata (tagliata da 2026-10-10): 93775 candele (RONINUSDT 15m)
Oct 11 03:04:31 Trading-Agent python[2434760]: [discover] ASTERUSDT|gen_042c5262 (variante di gen_1390f7aa, intorno:htf_fade.htf_gap=0.02): conferme retroattive 2/2 -> VALIDATA oggi
Oct 11 03:04:39 Trading-Agent python[2434697]: [backtest] cache riusata (tagliata da 2026-10-10): 167329 candele (GALAUSDT 15m)
Oct 11 03:04:52 Trading-Agent python[2434739]: [backtest] cache riusata (tagliata da 2026-10-10): 31630 candele (SENTUSDT 15m)
Oct 11 03:04:55 Trading-Agent python[2434739]: [backtest] cache riusata (tagliata da 2026-10-10): 167329 candele (1000SHIBUSDT 15m)
Oct 11 03:05:35 Trading-Agent python[2434718]: [backtest] cache riusata (tagliata da 2026-10-10): 39615 candele (WLFIUSDT 15m)
Oct 11 03:05:36 Trading-Agent python[2434655]: [backtest] cache riusata (tagliata da 2026-10-10): 167329 candele (ALGOUSDT 15m)
Oct 11 03:05:36 Trading-Agent python[2434760]: [discover] ASTERUSDT|gen_a616c496 (variante di gen_1390f7aa, intorno:min_adx=20): conferme retroattive 2/2 -> VALIDATA oggi
Oct 11 03:05:36 Trading-Agent python[2434760]: [backtest] cache riusata (tagliata da 2026-10-10): 9569 candele (GRAMUSDT 15m)
Oct 11 03:05:40 Trading-Agent python[2434760]: [backtest] cache ESTESA di 193 candele (invece di riscaricarne 167425) (AXSUSDT 15m)
Oct 11 03:06:43 Trading-Agent python[2434676]: [backtest] cache ESTESA di 193 candele (invece di riscaricarne 32495) (FOLKSUSDT 15m)
Oct 11 03:06:46 Trading-Agent python[2434676]: [backtest] cache riusata (tagliata da 2026-10-10): 89795 candele (ETHFIUSDT 15m)
Oct 11 03:08:31 Trading-Agent python[2434739]: [backtest] cache riusata (tagliata da 2026-10-10): 3706 candele (MARSCOINUSDT 15m)
Oct 11 03:08:32 Trading-Agent python[2434739]: [backtest] cache riusata (tagliata da 2026-10-10): 66960 candele (ACTUSDT 15m)
Oct 11 03:08:58 Trading-Agent python[2434697]: [backtest] cache riusata (tagliata da 2026-10-10): 167329 candele (TRXUSDT 15m)
Oct 11 03:09:05 Trading-Agent python[2434676]: [backtest] cache riusata (tagliata da 2026-10-10): 34037 candele (币安人生USDT 15m)
Oct 11 03:09:06 Trading-Agent python[2434676]: [backtest] cache ESTESA di 193 candele (invece di riscaricarne 54285) (NILUSDT 15m)
Oct 11 03:10:12 Trading-Agent python[2434655]: [backtest] cache riusata (tagliata da 2026-10-10): 101031 candele (PYTHUSDT 15m)
Oct 11 03:10:29 Trading-Agent python[2434676]: [backtest] cache riusata (tagliata da 2026-10-10): 167329 candele (CRVUSDT 15m)
Oct 11 03:12:39 Trading-Agent python[2434697]: [backtest] cache riusata (tagliata da 2026-10-10): 64175 candele (VIRTUALUSDT 15m)
Oct 11 03:12:41 Trading-Agent python[2434655]: [backtest] cache riusata (tagliata da 2026-10-10): 167329 candele (ETCUSDT 15m)
Oct 11 03:13:02 Trading-Agent python[2434718]: [backtest] cache riusata (tagliata da 2026-10-10): 99513 candele (JTOUSDT 15m)
Oct 11 03:14:13 Trading-Agent python[2434697]: [backtest] cache riusata (tagliata da 2026-10-10): 54858 candele (MUBARAKUSDT 15m)
Oct 11 03:14:52 Trading-Agent python[2434676]: [backtest] cache riusata (tagliata da 2026-10-10): 70921 candele (EIGENUSDT 15m)
Oct 11 03:15:24 Trading-Agent python[2434718]: [backtest] cache riusata (tagliata da 2026-10-10): 60633 candele (SUSDT 15m)
Oct 11 03:16:18 Trading-Agent python[2434697]: [discover] MUBARAKUSDT|gen_1eec02f5 (variante di gen_9758394b, intorno:atr_mult_stop=2.5): conferme retroattive 0/2
Oct 11 03:16:49 Trading-Agent python[2434655]: [backtest] cache riusata (tagliata da 2026-10-10): 167329 candele (DASHUSDT 15m)
Oct 11 03:16:52 Trading-Agent python[2434718]: [backtest] cache ESTESA di 193 candele (invece di riscaricarne 97871) (MOVRUSDT 15m)
Oct 11 03:17:01 Trading-Agent python[2434676]: [backtest] cache ESTESA di 193 candele (invece di riscaricarne 167425) (NEOUSDT 15m)
Oct 11 03:18:05 Trading-Agent python[2434697]: [backtest] cache riusata (tagliata da 2026-10-10): 110391 candele (SEIUSDT 15m)
Oct 11 03:19:30 Trading-Agent python[2434718]: [backtest] cache ESTESA di 193 candele (invece di riscaricarne 160401) (GMTUSDT 15m)
Oct 11 03:20:33 Trading-Agent python[2434697]: [backtest] cache riusata (tagliata da 2026-10-10): 167329 candele (BELUSDT 15m)
Oct 11 03:21:10 Trading-Agent python[2434655]: [backtest] cache riusata (tagliata da 2026-10-10): 50639 candele (AIOTUSDT 15m)
Oct 11 03:21:11 Trading-Agent python[2434676]: [backtest] cache riusata (tagliata da 2026-10-10): 141937 candele (LDOUSDT 15m)
Oct 11 03:22:14 Trading-Agent python[2434655]: [backtest] cache riusata (tagliata da 2026-10-10): 115729 candele (NMRUSDT 15m)
Oct 11 03:22:58 Trading-Agent python[2434718]: [backtest] cache ESTESA di 193 candele (invece di riscaricarne 67331) (GRASSUSDT 15m)
Oct 11 03:23:17 Trading-Agent python[2434739]: [backtest] cache riusata (tagliata da 2026-10-10): 72624 candele (POLUSDT 15m)
Oct 11 03:24:17 Trading-Agent python[2434676]: [backtest] cache riusata (tagliata da 2026-10-10): 43830 candele (AINUSDT 15m)
Oct 11 03:24:35 Trading-Agent python[2434697]: [backtest] cache riusata (tagliata da 2026-10-10): 77337 candele (RENDERUSDT 15m)
Oct 11 03:24:52 Trading-Agent python[2434739]: [backtest] cache riusata (tagliata da 2026-10-10): 34311 candele (LABUSDT 15m)
Oct 11 03:24:55 Trading-Agent python[2434739]: [backtest] cache ESTESA di 193 candele (invece di riscaricarne 47293) (LAUSDT 15m)
Oct 11 03:27:11 Trading-Agent python[2434697]: [backtest] cache riusata (tagliata da 2026-10-10): 89999 candele (BOMEUSDT 15m)
Oct 11 03:28:04 Trading-Agent python[2434676]: [discover] AINUSDT|gen_e70074cc (variante di gen_b0e86c70, intorno:min_adx=25): conferme retroattive 2/2 -> VALIDATA oggi
Oct 11 03:29:11 Trading-Agent python[2434697]: [backtest] cache riusata (tagliata da 2026-10-10): 63190 candele (FARTCOINUSDT 15m)
Oct 11 03:29:16 Trading-Agent python[2434676]: [discover] AINUSDT|gen_fc726ece (variante di gen_d926b0fd, intorno:volume_mult=2): conferme retroattive 1/2
Oct 11 03:30:44 Trading-Agent python[2434676]: [discover] AINUSDT|gen_b64c1611 (variante di gen_e3f3663c, intorno:rsi_extreme.high=70): conferme retroattive 2/2 -> VALIDATA oggi
Oct 11 03:31:53 Trading-Agent python[2434676]: [discover] AINUSDT|gen_e7f2455d (variante di gen_e3f3663c, intorno:trend_strength.adx_lo=18): conferme retroattive 1/2
Oct 11 03:32:48 Trading-Agent python[2434676]: [discover] AINUSDT|gen_2cfdf866 (variante di gen_e3f3663c, intorno:trend_strength.adx_lo=28): conferme retroattive 0/2
Oct 11 03:33:21 Trading-Agent python[2434739]: [backtest] cache riusata (tagliata da 2026-10-10): 36335 candele (AKEUSDT 15m)
Oct 11 03:34:15 Trading-Agent python[2434676]: [discover] AINUSDT|gen_9507825f (variante di gen_e3f3663c, intorno:min_adx=25): conferme retroattive 2/2 -> VALIDATA oggi
Oct 11 03:34:18 Trading-Agent python[2434676]: [backtest] cache ESTESA di 193 candele (invece di riscaricarne 94984) (LSKUSDT 15m)
Oct 11 03:34:34 Trading-Agent python[2434739]: [backtest] cache riusata (tagliata da 2026-10-10): 167329 candele (SKLUSDT 15m)
Oct 11 03:35:09 Trading-Agent python[2434760]: [backtest] cache riusata (tagliata da 2026-10-10): 112311 candele (PENDLEUSDT 15m)
Oct 11 03:35:25 Trading-Agent python[2434718]: [backtest] cache riusata (tagliata da 2026-10-10): 60059 candele (VTHOUSDT 15m)
Oct 11 03:36:48 Trading-Agent python[2434718]: [backtest] cache ESTESA di 193 candele (invece di riscaricarne 48237) (HUMAUSDT 15m)
Oct 11 03:38:02 Trading-Agent python[2434760]: [backtest] cache riusata (tagliata da 2026-10-10): 48727 candele (AGTUSDT 15m)
Oct 11 03:38:22 Trading-Agent python[2434739]: [backtest] cache riusata (tagliata da 2026-10-10): 834 candele (CTUSDT 15m)
Oct 11 03:38:23 Trading-Agent python[2434739]: [backtest] cache riusata (tagliata da 2026-10-10): 115057 candele (MAVUSDT 15m)
Oct 11 03:39:13 Trading-Agent python[2434718]: [backtest] cache riusata (tagliata da 2026-10-10): 37186 candele (0GUSDT 15m)
Oct 11 03:40:26 Trading-Agent python[2434718]: [backtest] cache riusata (tagliata da 2026-10-10): 53911 candele (PAXGUSDT 15m)
Oct 11 03:41:11 Trading-Agent python[2434697]: [backtest] cache riusata (tagliata da 2026-10-10): 23120 candele (AZTECUSDT 15m)
Oct 11 03:41:15 Trading-Agent python[2434697]: [backtest] cache riusata (tagliata da 2026-10-10): 94889 candele (ALTUSDT 15m)
Oct 11 03:41:17 Trading-Agent python[2434739]: [backtest] cache riusata (tagliata da 2026-10-10): 126673 candele (CKBUSDT 15m)
Oct 11 03:41:34 Trading-Agent python[2434760]: [backtest] cache riusata (tagliata da 2026-10-10): 95560 candele (WIFUSDT 15m)
Oct 11 03:41:38 Trading-Agent python[2434718]: [backtest] cache riusata (tagliata da 2026-10-10): 25697 candele (FRAXUSDT 15m)
Oct 11 03:41:41 Trading-Agent python[2434718]: [backtest] cache riusata (tagliata da 2026-10-10): 166739 candele (DUSKUSDT 15m)
Oct 11 03:43:29 Trading-Agent python[2434697]: [backtest] cache riusata (tagliata da 2026-10-10): 102479 candele (ORDIUSDT 15m)
Oct 11 03:43:50 Trading-Agent python[2434760]: [backtest] cache riusata (tagliata da 2026-10-10): 160069 candele (APEUSDT 15m)
Oct 11 03:44:34 Trading-Agent python[2434739]: [backtest] cache riusata (tagliata da 2026-10-10): 44413 candele (BULLAUSDT 15m)
Oct 11 03:45:01 Trading-Agent python[2434655]: [backtest] cache riusata (tagliata da 2026-10-10): 50843 candele (JSTUSDT 15m)
Oct 11 03:46:00 Trading-Agent python[2434718]: [backtest] cache ESTESA di 193 candele (invece di riscaricarne 95657) (MANTAUSDT 15m)
Oct 11 03:46:08 Trading-Agent python[2434655]: [backtest] cache ESTESA di 193 candele (invece di riscaricarne 5797) (DOSUSDT 15m)
Oct 11 03:46:12 Trading-Agent python[2434655]: [backtest] cache ESTESA di 193 candele (invece di riscaricarne 163475) (IMXUSDT 15m)
Oct 11 03:46:27 Trading-Agent python[2434697]: [backtest] cache riusata (tagliata da 2026-10-10): 63872 candele (VELODROMEUSDT 15m)
```
