# 0563-9ott-mattina-rifiuti.req

_eseguito: 2026-10-09 04:05 UTC_

**richiesta:** `rifiuti`
**eseguito:** `journalctl -u trading-bot.service --since -24h --no-pager -g \[rifiuto\]`
**esito:** codice 0 in 0.2s

```
Oct 08 04:17:53 Trading-Agent python[2005927]: [rifiuto] ZORAUSDT gen_ceab7f6a long: posizione gia' aperta su questa coin
Oct 08 09:17:45 Trading-Agent python[2005927]: [rifiuto] AVAAIUSDT gen_e50a9211: veto di regime (bull_trending)
Oct 08 11:17:52 Trading-Agent python[2005927]: [rifiuto] ZECUSDT gen_e6ddc613 long: posizione gia' aperta su questa coin
Oct 08 11:32:40 Trading-Agent python[2005927]: [rifiuto] ZECUSDT gen_e6ddc613 long: posizione gia' aperta su questa coin
Oct 08 11:47:45 Trading-Agent python[2005927]: [rifiuto] ZECUSDT gen_e6ddc613 long: posizione gia' aperta su questa coin
Oct 08 12:02:52 Trading-Agent python[2005927]: [rifiuto] ZECUSDT gen_e6ddc613 long: posizione gia' aperta su questa coin
Oct 08 13:17:42 Trading-Agent python[2005927]: [rifiuto] STXUSDT gen_14e1775b long: posizione gia' aperta su questa coin
Oct 08 13:32:55 Trading-Agent python[2005927]: [rifiuto] STXUSDT gen_14e1775b long: posizione gia' aperta su questa coin
Oct 08 14:18:13 Trading-Agent python[2005927]: [rifiuto] USELESSUSDT gen_acea368d short: posizione gia' aperta su questa coin
Oct 08 15:02:48 Trading-Agent python[2005927]: [rifiuto] HEIUSDT gen_9a383fff long: posizione gia' aperta su questa coin
Oct 08 15:02:48 Trading-Agent python[2005927]: [rifiuto] BULLAUSDT gen_5a52c06b long: posizione gia' aperta su questa coin
Oct 08 15:17:39 Trading-Agent python[2005927]: [rifiuto] PNUTUSDT gen_4810faab long: posizione gia' aperta su questa coin
Oct 08 15:17:39 Trading-Agent python[2005927]: [rifiuto] BULLAUSDT gen_5a52c06b long: posizione gia' aperta su questa coin
Oct 08 15:48:02 Trading-Agent python[2005927]: [rifiuto] CVCUSDT gen_7b4a474b long: posizione gia' aperta su questa coin
Oct 08 15:48:03 Trading-Agent python[2005927]: [rifiuto] CROSSUSDT gen_4e6e1ae0 long: correlazione: Troppe posizioni correlate >0.85 (PNUTUSDT=0.85, CVCUSDT=0.90, VETUSDT=0.92)
Oct 08 15:48:03 Trading-Agent python[2005927]: [rifiuto] VETUSDT gen_b9c251a1 long: posizione gia' aperta su questa coin
Oct 08 15:48:03 Trading-Agent python[2005927]: [rifiuto] SPXUSDT gen_725cb5f4 long: correlazione: Troppe posizioni correlate >0.85 (PNUTUSDT=0.90, CVCUSDT=0.88, VETUSDT=0.85)
Oct 08 15:48:03 Trading-Agent python[2005927]: [rifiuto] HEIUSDT gen_9a383fff long: cooldown dopo stop (37m)
Oct 08 16:03:11 Trading-Agent python[2005927]: [rifiuto] DOTUSDT gen_22b2cade long: correlazione: Troppe posizioni correlate >0.85 (PNUTUSDT=0.97, CVCUSDT=0.95, VETUSDT=0.97, ASTERUSDT=0.91, TUTUSDT=0.87, DEXEUSDT=0.90)
Oct 08 16:03:12 Trading-Agent python[2005927]: [rifiuto] VETUSDT gen_fb3d971f long: posizione gia' aperta su questa coin
Oct 08 16:03:12 Trading-Agent python[2005927]: [rifiuto] HUSDT gen_22b2cade long: correlazione: Troppe posizioni correlate >0.85 (PNUTUSDT=0.88, CVCUSDT=0.92, VETUSDT=0.92, ASTERUSDT=0.88)
Oct 08 16:03:12 Trading-Agent python[2005927]: [rifiuto] ASTERUSDT gen_d74845a5 long: posizione gia' aperta su questa coin
Oct 08 16:03:15 Trading-Agent python[2005927]: [rifiuto] KERNELUSDT gen_c647ead7 long: correlazione: Troppe posizioni correlate >0.85 (PNUTUSDT=0.97, CVCUSDT=0.95, VETUSDT=0.98, ASTERUSDT=0.92, TUTUSDT=0.88, DEXEUSDT=0.90)
Oct 08 16:17:43 Trading-Agent python[2005927]: [rifiuto] CVCUSDT gen_7b4a474b long: posizione gia' aperta su questa coin
Oct 08 16:17:46 Trading-Agent python[2005927]: [rifiuto] HUSDT gen_22b2cade long: correlazione: Troppe posizioni correlate >0.85 (PNUTUSDT=0.88, CVCUSDT=0.92, VETUSDT=0.92)
Oct 08 16:17:47 Trading-Agent python[2005927]: [rifiuto] ASTERUSDT gen_d74845a5 long: cooldown dopo stop (48m)
Oct 08 16:17:47 Trading-Agent python[2005927]: [rifiuto] UBUSDT gen_5b847426 long: posizione gia' aperta su questa coin
Oct 08 16:17:48 Trading-Agent python[2005927]: [rifiuto] KERNELUSDT gen_c647ead7 long: correlazione: Troppe posizioni correlate >0.85 (PNUTUSDT=0.97, CVCUSDT=0.95, VETUSDT=0.98, TUTUSDT=0.88, DEXEUSDT=0.90)
Oct 08 17:18:14 Trading-Agent python[2005927]: [rifiuto] CROSSUSDT gen_4e6e1ae0 long: posizione gia' aperta su questa coin
Oct 08 17:18:14 Trading-Agent python[2005927]: [rifiuto] HUSDT gen_22b2cade long: posizione gia' aperta su questa coin
Oct 08 17:33:13 Trading-Agent python[2005927]: [rifiuto] HUSDT gen_22b2cade long: posizione gia' aperta su questa coin
Oct 08 17:47:57 Trading-Agent python[2005927]: [rifiuto] ORCAUSDT gen_fb3d971f long: posizione gia' aperta su questa coin
Oct 08 17:47:58 Trading-Agent python[2005927]: [rifiuto] HUSDT gen_22b2cade long: posizione gia' aperta su questa coin
Oct 08 19:17:56 Trading-Agent python[2005927]: [rifiuto] ZORAUSDT gen_ceab7f6a short: posizione gia' aperta su questa coin
Oct 08 19:33:00 Trading-Agent python[2005927]: [rifiuto] ZORAUSDT gen_ceab7f6a short: posizione gia' aperta su questa coin
Oct 08 19:47:52 Trading-Agent python[2005927]: [rifiuto] ZORAUSDT gen_ceab7f6a short: posizione gia' aperta su questa coin
Oct 08 20:02:43 Trading-Agent python[2005927]: [rifiuto] ZORAUSDT gen_ceab7f6a short: posizione gia' aperta su questa coin
Oct 08 20:02:43 Trading-Agent python[2005927]: [rifiuto] BULLAUSDT gen_5a52c06b long: posizione gia' aperta su questa coin
Oct 08 20:18:07 Trading-Agent python[2005927]: [rifiuto] ZORAUSDT gen_ceab7f6a short: posizione gia' aperta su questa coin
Oct 08 20:18:07 Trading-Agent python[2005927]: [rifiuto] BULLAUSDT gen_5a52c06b long: posizione gia' aperta su questa coin
Oct 08 20:33:08 Trading-Agent python[2005927]: [rifiuto] ZORAUSDT gen_ceab7f6a short: posizione gia' aperta su questa coin
Oct 08 20:33:08 Trading-Agent python[2005927]: [rifiuto] BULLAUSDT gen_5a52c06b long: posizione gia' aperta su questa coin
Oct 08 21:17:43 Trading-Agent python[2005927]: [rifiuto] BULLAUSDT gen_5a52c06b long: posizione gia' aperta su questa coin
Oct 08 21:33:03 Trading-Agent python[2005927]: [rifiuto] OPENUSDT gen_b9bf5d01 short: posizione gia' aperta su questa coin
Oct 08 21:33:03 Trading-Agent python[2005927]: [rifiuto] BULLAUSDT gen_5a52c06b long: posizione gia' aperta su questa coin
Oct 08 21:47:44 Trading-Agent python[2005927]: [rifiuto] OPENUSDT gen_46f0717f short: posizione gia' aperta su questa coin
Oct 08 21:47:44 Trading-Agent python[2005927]: [rifiuto] BULLAUSDT gen_5a52c06b long: posizione gia' aperta su questa coin
Oct 08 22:02:54 Trading-Agent python[2005927]: [rifiuto] BULLAUSDT gen_5a52c06b long: posizione gia' aperta su questa coin
Oct 08 22:18:04 Trading-Agent python[2005927]: [rifiuto] BULLAUSDT gen_5a52c06b long: posizione gia' aperta su questa coin
Oct 08 22:47:59 Trading-Agent python[2005927]: [rifiuto] OPENUSDT gen_b9bf5d01 short: posizione gia' aperta su questa coin
Oct 08 23:02:55 Trading-Agent python[2005927]: [rifiuto] OPENUSDT gen_b9bf5d01 short: posizione gia' aperta su questa coin
Oct 08 23:17:43 Trading-Agent python[2005927]: [rifiuto] OPENUSDT gen_46f0717f short: posizione gia' aperta su questa coin
Oct 08 23:33:06 Trading-Agent python[2005927]: [rifiuto] OPENUSDT gen_46f0717f short: posizione gia' aperta su questa coin
Oct 08 23:47:53 Trading-Agent python[2005927]: [rifiuto] XPINUSDT gen_2e0818c8 short: cooldown dopo stop (34m)
Oct 09 00:47:48 Trading-Agent python[2005927]: [rifiuto] STEEMUSDT gen_addf82da long: correlazione: Troppe posizioni correlate >0.85 (VETUSDT=0.86, ZORAUSDT=0.87, FLOCKUSDT=0.87, 1000PEPEUSDT=0.87)
Oct 09 01:03:04 Trading-Agent python[2005927]: [rifiuto] STEEMUSDT gen_addf82da long: correlazione: Troppe posizioni correlate >0.85 (VETUSDT=0.86, ZORAUSDT=0.87, FLOCKUSDT=0.87, 1000PEPEUSDT=0.87)
Oct 09 01:47:59 Trading-Agent python[2005927]: [rifiuto] QUSDT gen_1f224994 short: risk gate: stop troppo largo: 6.4% del prezzo > 6% (ATR gonfiato: primo incasso a +10%, lock a +5%)
Oct 09 02:32:50 Trading-Agent python[2005927]: [rifiuto] ZORAUSDT gen_ceab7f6a long: posizione gia' aperta su questa coin
Oct 09 03:48:08 Trading-Agent python[2005927]: [rifiuto] QUSDT gen_1f224994 short: risk gate: stop troppo largo: 6.8% del prezzo > 6% (ATR gonfiato: primo incasso a +10%, lock a +5%)
```
