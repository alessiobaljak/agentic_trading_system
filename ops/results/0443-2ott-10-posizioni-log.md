# 0443-2ott-10-posizioni-log.req

_eseguito: 2026-10-02 18:53 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Oct 02 16:03:29 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 02 16:03:29 Trading-Agent python[2005927]: [learning] filtrati 8/233 trade (esplorativi: 8)
Oct 02 16:03:29 Trading-Agent python[2005927]: [main] pesi ricalcolati: 146 coppie strat×regime da 233 trade (30g)
Oct 02 16:03:30 Trading-Agent python[2005927]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 02 16:17:37 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 02 16:17:37 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 02 16:18:41 Trading-Agent python[2005927]: [rifiutati] 1 segnali rifiutati valutati
Oct 02 16:32:42 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 02 16:32:42 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 02 16:33:46 Trading-Agent python[2005927]: [rifiutati] 1 segnali rifiutati valutati
Oct 02 16:43:57 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 2962 (rifiutati 1301 · controllo 620 · registro 595 · trade 291 · pesi 54 · memoria 41 · deriva 19 · referti 19) — quota gratuita 50000/giorno
Oct 02 16:43:57 Trading-Agent python[2005927]: [learning] filtrati 8/233 trade (esplorativi: 8)
Oct 02 16:43:58 Trading-Agent python[2005927]: [main] pesi ricalcolati: 146 coppie strat×regime da 233 trade (30g)
Oct 02 16:43:59 Trading-Agent python[2005927]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 02 16:44:01 Trading-Agent python[2005927]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 2025 ms
Oct 02 16:47:25 Trading-Agent python[2005927]: [scarti] 1 secondo segnale stessa coin
Oct 02 16:47:26 Trading-Agent python[2005927]: [selettore] BANKUSDT gen_fb3d971f long p=0.59 soglia=0.50 -> avrebbe aperto (ombra: apre comunque)
Oct 02 16:47:26 Trading-Agent python[2005927]: [DRY_RUN] OPEN long BANKUSDT qty=2310.8677 @ 0.03002 lev=2.0x SL=0.0296 TP=0.0307
Oct 02 16:47:26 Trading-Agent python[2005927]: [declassata] BANKUSDT gen_fb3d971f long size x0.25
Oct 02 16:47:32 Trading-Agent python[2005927]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=bankusdt@bookTicker/jupusdt@bookTicker
Oct 02 16:48:59 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 02 16:48:59 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 02 16:49:01 Trading-Agent python[2005927]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Oct 02 16:49:01 Trading-Agent python[2005927]: [rifiutati] 1 segnali rifiutati valutati
Oct 02 17:02:44 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 02 17:02:44 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 02 17:09:28 Trading-Agent python[2005927]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 02 17:14:38 Trading-Agent python[2005927]: [DRY_RUN] SCALE-OUT 83.0717 JUPUSDT @ 0.3251856589393036 (netto +0.7307, residuo 193.8340)
Oct 02 17:17:27 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 02 17:17:27 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 02 17:17:27 Trading-Agent python[2005927]: [rifiuto] BANKUSDT gen_fb3d971f long: posizione gia' aperta su questa coin
Oct 02 17:19:32 Trading-Agent python[2005927]: [main] verdetti (trailing/post-stop) assegnati a 2 trade paper
Oct 02 17:32:38 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 02 17:32:38 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 02 17:43:58 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 3241 (rifiutati 1444 · controllo 682 · registro 653 · trade 296 · pesi 57 · memoria 45 · deriva 20 · referti 20) — quota gratuita 50000/giorno
Oct 02 17:43:58 Trading-Agent python[2005927]: [learning] filtrati 8/233 trade (esplorativi: 8)
Oct 02 17:43:59 Trading-Agent python[2005927]: [main] pesi ricalcolati: 146 coppie strat×regime da 233 trade (30g)
Oct 02 17:44:00 Trading-Agent python[2005927]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 02 17:44:02 Trading-Agent python[2005927]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1905 ms
Oct 02 17:47:31 Trading-Agent python[2005927]: [scarti] 2 secondo segnale stessa coin
Oct 02 17:47:32 Trading-Agent python[2005927]: [selettore] SPXUSDT gen_ba3a671f long p=0.77 soglia=0.50 -> avrebbe aperto (ombra: apre comunque)
Oct 02 17:47:32 Trading-Agent python[2005927]: [DRY_RUN] OPEN long SPXUSDT qty=182.3651 @ 0.4334 lev=2.0x SL=0.4253 TP=0.4456
Oct 02 17:47:32 Trading-Agent python[2005927]: [declassata] SPXUSDT gen_ba3a671f long size x0.25
Oct 02 17:47:39 Trading-Agent python[2005927]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=bankusdt@bookTicker/jupusdt@bookTicker/spxusdt@bookTicker
Oct 02 17:50:08 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 02 17:50:08 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 02 17:50:09 Trading-Agent python[2005927]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Oct 02 18:02:54 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 02 18:02:54 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 02 18:07:36 Trading-Agent python[2005927]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 02 18:17:45 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 02 18:17:45 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 02 18:18:16 Trading-Agent python[2005927]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 02 18:27:41 Trading-Agent python[2005927]: [DRY_RUN] SCALE-OUT 83.0717 JUPUSDT @ 0.3159713178786072 (netto +1.4962, residuo 110.7623)
Oct 02 18:28:44 Trading-Agent python[2005927]: [DRY_RUN] CLOSE SPXUSDT @ 0.42527354875575707 (stop_loss)
Oct 02 18:28:44 Trading-Agent python[2005927]: [referto] SPXUSDT gen_ba3a671f: a favore fino a 0.37R ma sotto il primo gradino (0.75R) · il lock non si e' mai armato (serviva 0.38R)
Oct 02 18:28:47 Trading-Agent python[2005927]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 02 18:28:47 Trading-Agent python[2005927]: [learning] filtrati 8/234 trade (esplorativi: 8)
Oct 02 18:28:47 Trading-Agent python[2005927]: [main] pesi ricalcolati: 146 coppie strat×regime da 234 trade (30g)
Oct 02 18:28:48 Trading-Agent python[2005927]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 02 18:28:50 Trading-Agent python[2005927]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=bankusdt@bookTicker/jupusdt@bookTicker
Oct 02 18:32:38 Trading-Agent python[2005927]: [scarti] 2 secondo segnale stessa coin
Oct 02 18:32:40 Trading-Agent python[2005927]: [selettore] VETUSDT gen_b9c251a1 long p=0.74 soglia=0.50 -> avrebbe aperto (ombra: apre comunque)
Oct 02 18:32:40 Trading-Agent python[2005927]: [DRY_RUN] OPEN long VETUSDT qty=6891.1181 @ 0.00853 lev=1.0x SL=0.0084 TP=0.0089
Oct 02 18:32:40 Trading-Agent python[2005927]: [declassata] VETUSDT gen_b9c251a1 long size x0.25
Oct 02 18:32:47 Trading-Agent python[2005927]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=bankusdt@bookTicker/jupusdt@bookTicker/vetusdt@bookTicker
Oct 02 18:39:27 Trading-Agent python[2005927]: [DRY_RUN] CLOSE BANKUSDT @ 0.029571437169665368 (stop_loss)
Oct 02 18:39:27 Trading-Agent python[2005927]: [referto] BANKUSDT gen_fb3d971f: mai andato a favore (mfe 0.14R): direzione sbagliata · controtrend rispetto al regime all'ingresso
Oct 02 18:39:27 Trading-Agent python[2005927]: [DRY_RUN] CLOSE VETUSDT @ 0.008357975533691282 (stop_loss)
Oct 02 18:39:27 Trading-Agent python[2005927]: [referto] VETUSDT gen_b9c251a1: mai andato a favore (mfe 0.00R): direzione sbagliata
Oct 02 18:39:29 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 02 18:39:29 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 02 18:39:30 Trading-Agent python[2005927]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Oct 02 18:39:30 Trading-Agent python[2005927]: [learning] filtrati 8/236 trade (esplorativi: 8)
Oct 02 18:39:31 Trading-Agent python[2005927]: [main] pesi ricalcolati: 147 coppie strat×regime da 236 trade (30g)
Oct 02 18:39:32 Trading-Agent python[2005927]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 02 18:39:36 Trading-Agent python[2005927]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=jupusdt@bookTicker
Oct 02 18:40:02 Trading-Agent python[2005927]: [main] market scan...
Oct 02 18:42:19 Trading-Agent python[2005927]: [main] valutate 71 coin validate (71 nel registro): ['PENGUUSDT', 'VETUSDT', 'JUPUSDT', 'DOTUSDT', 'NEIROUSDT', 'SPXUSDT', 'SEIUSDT', 'ATOMUSDT', 'TRUMPUSDT', 'RAYSOLUSDT', 'PNUTUSDT', 'FORMUSDT', 'TSTUSDT', 'XPLUSDT', 'DEXEUSDT', 'USELESSUSDT', 'SUIUSDT', 'AXSUSDT', 'HEMIUSDT', 'JASMYUSDT', 'SAHARAUSDT', 'ONGUSDT', 'OPENUSDT', 'RSRUSDT', 'PUNDIXUSDT', 'STXUSDT', 'AIOUSDT', 'PARTIUSDT', 'ARCUSDT', 'XPINUSDT', 'SCRUSDT', 'AVAAIUSDT', 'RENDERUSDT', 'ZKUSDT', 'ZORAUSDT', 'HOMEUSDT', 'STEEMUSDT', 'GALAUSDT', 'GPSUSDT', 'IDUSDT', 'PLUMEUSDT', 'HEIUSDT', 'SUPERUSDT', 'TAUSDT', 'MTLUSDT', 'ENAUSDT', 'MUBARAKUSDT', 'ORCAUSDT', 'CROSSUSDT', 'QUSDT', 'BANKUSDT', 'HUMAUSDT', 'WALUSDT', 'EPICUSDT', 'THEUSDT', 'UBUSDT', 'BMTUSDT', 'BULLAUSDT', 'CVCUSDT', 'SYRUPUSDT', 'PHAUSDT', 'MITOUSDT', 'SOPHUSDT', 'SKYAIUSDT', 'BTRUSDT', 'TUTUSDT', 'B2USDT', 'FLOCKUSDT', 'PROMUSDT', 'GRIFFAINUSDT', 'CATIUSDT']
Oct 02 18:44:21 Trading-Agent python[2005927]: [firebase] letture ultime 24 h: 3503 (rifiutati 1552 · controllo 744 · registro 717 · trade 302 · pesi 65 · memoria 49 · deriva 23 · referti 23) — quota gratuita 50000/giorno
Oct 02 18:44:21 Trading-Agent python[2005927]: [learning] filtrati 8/236 trade (esplorativi: 8)
Oct 02 18:44:21 Trading-Agent python[2005927]: [main] pesi ricalcolati: 147 coppie strat×regime da 236 trade (30g)
Oct 02 18:44:23 Trading-Agent python[2005927]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 02 18:44:25 Trading-Agent python[2005927]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1748 ms
Oct 02 18:47:50 Trading-Agent python[2005927]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 02 18:47:50 Trading-Agent python[2005927]:   return query.where(field_path, op_string, value)
Oct 02 18:47:50 Trading-Agent python[2005927]: [scarti] 20 secondo segnale stessa coin
Oct 02 18:47:51 Trading-Agent python[2005927]: [selettore] PENGUUSDT gen_a32bee42 long p=0.64 soglia=0.50 -> avrebbe aperto (ombra: apre comunque)
Oct 02 18:47:51 Trading-Agent python[2005927]: [DRY_RUN] OPEN long PENGUUSDT qty=4200.8130 @ 0.008716 lev=1.0x SL=0.0084 TP=0.0091
Oct 02 18:47:51 Trading-Agent python[2005927]: [declassata] PENGUUSDT gen_a32bee42 long size x0.25
Oct 02 18:47:51 Trading-Agent python[2005927]: [rifiuto] VETUSDT gen_fb3d971f long: cooldown dopo stop (53m)
Oct 02 18:47:53 Trading-Agent python[2005927]: [selettore] DOTUSDT gen_9588ad8e long p=0.61 soglia=0.50 -> avrebbe aperto (ombra: apre comunque)
Oct 02 18:47:53 Trading-Agent python[2005927]: [DRY_RUN] OPEN long DOTUSDT qty=44.3174 @ 1.1518 lev=1.0x SL=1.1251 TP=1.1918
Oct 02 18:47:53 Trading-Agent python[2005927]: [declassata] DOTUSDT gen_9588ad8e long size x0.25
Oct 02 18:47:54 Trading-Agent python[2005927]: [selettore] USELESSUSDT gen_194e2514 long p=0.64 soglia=0.50 -> avrebbe aperto (ombra: apre comunque)
Oct 02 18:47:54 Trading-Agent python[2005927]: [DRY_RUN] OPEN long USELESSUSDT qty=126.8471 @ 0.2249 lev=1.0x SL=0.2156 TP=0.2482
Oct 02 18:47:54 Trading-Agent python[2005927]: [declassata] USELESSUSDT gen_194e2514 long size x0.25
Oct 02 18:47:55 Trading-Agent python[2005927]: [selettore] SAHARAUSDT gen_95aff747 long p=0.66 soglia=0.50 -> avrebbe aperto (ombra: apre comunque)
Oct 02 18:47:55 Trading-Agent python[2005927]: [DRY_RUN] OPEN long SAHARAUSDT qty=10254.6940 @ 0.009019 lev=1.0x SL=0.0089 TP=0.0092
Oct 02 18:47:55 Trading-Agent python[2005927]: [rifiuto] RSRUSDT gen_b2f350ff long: correlazione: Troppe posizioni correlate >0.85 (PENGUUSDT=0.92, DOTUSDT=0.93, SAHARAUSDT=0.96)
Oct 02 18:47:56 Trading-Agent python[2005927]: [selettore] ARCUSDT gen_96c1ed1b long p=0.60 soglia=0.50 -> avrebbe aperto (ombra: apre comunque)
Oct 02 18:47:56 Trading-Agent python[2005927]: [DRY_RUN] OPEN long ARCUSDT qty=834.0551 @ 0.07009 lev=1.0x SL=0.0691 TP=0.0716
Oct 02 18:47:56 Trading-Agent python[2005927]: [declassata] ARCUSDT gen_96c1ed1b long size x0.25
Oct 02 18:47:57 Trading-Agent python[2005927]: [selettore] XPINUSDT gen_c60cc1b9 long p=0.59 soglia=0.50 -> avrebbe aperto (ombra: apre comunque)
Oct 02 18:47:57 Trading-Agent python[2005927]: [DRY_RUN] OPEN long XPINUSDT qty=112105.5579 @ 0.000825 lev=1.0x SL=0.0008 TP=0.0009
Oct 02 18:47:58 Trading-Agent python[2005927]: [price_stream] connesso · 6 simboli · wss://fstream.binance.com/stream?streams=arcusdt@bookTicker/dotusdt@bookTicker/jupusdt@bookTicker/penguusdt@bookTicker/saharausdt@bookTicker/uselessusdt@bookTicker
Oct 02 18:48:04 Trading-Agent python[2005927]: [price_stream] connesso · 7 simboli · wss://fstream.binance.com/stream?streams=arcusdt@bookTicker/dotusdt@bookTicker/jupusdt@bookTicker/penguusdt@bookTicker/saharausdt@bookTicker/uselessusdt@bookTicker/xpinusdt@bookTicker
Oct 02 18:48:06 Trading-Agent python[2005927]: [selettore] HOMEUSDT gen_116faa2d long p=0.74 soglia=0.50 -> avrebbe aperto (ombra: apre comunque)
Oct 02 18:48:06 Trading-Agent python[2005927]: [DRY_RUN] OPEN long HOMEUSDT qty=8511.1153 @ 0.005624 lev=1.0x SL=0.0055 TP=0.0060
Oct 02 18:48:06 Trading-Agent python[2005927]: [declassata] HOMEUSDT gen_116faa2d long size x0.25
Oct 02 18:48:07 Trading-Agent python[2005927]: [selettore] GPSUSDT gen_871647b8 long p=0.59 soglia=0.50 -> avrebbe aperto (ombra: apre comunque)
Oct 02 18:48:07 Trading-Agent python[2005927]: [DRY_RUN] OPEN long GPSUSDT qty=9090.5332 @ 0.010174 lev=1.0x SL=0.0100 TP=0.0107
Oct 02 18:48:07 Trading-Agent python[2005927]: [rifiuto] BANKUSDT gen_fb3d971f long: cooldown dopo stop (53m)
Oct 02 18:48:08 Trading-Agent python[2005927]: [selettore] UBUSDT gen_5b847426 long p=0.66 soglia=0.50 -> avrebbe aperto (ombra: apre comunque)
Oct 02 18:48:08 Trading-Agent python[2005927]: [DRY_RUN] OPEN long UBUSDT qty=428.2412 @ 0.13348 lev=1.0x SL=0.1315 TP=0.1393
Oct 02 18:48:08 Trading-Agent python[2005927]: [declassata] UBUSDT gen_5b847426 long size x0.25
Oct 02 18:48:09 Trading-Agent python[2005927]: [selettore] BMTUSDT gen_571cdda2 long p=0.68 soglia=0.50 -> avrebbe aperto (ombra: apre comunque)
Oct 02 18:48:09 Trading-Agent python[2005927]: [DRY_RUN] OPEN long BMTUSDT qty=3959.1687 @ 0.01843 lev=1.0x SL=0.0181 TP=0.0192
Oct 02 18:48:09 Trading-Agent python[2005927]: [declassata] BMTUSDT gen_571cdda2 long size x0.25
Oct 02 18:48:13 Trading-Agent python[2005927]: [price_stream] connesso · 11 simboli · wss://fstream.binance.com/stream?streams=arcusdt@bookTicker/bmtusdt@bookTicker/dotusdt@bookTicker/gpsusdt@bookTicker/homeusdt@bookTicker/jupusdt@bookTicker/penguusdt@bookTicker/saharausdt@bookTicker/ubusdt@bookTicker/uselessusdt@bookTicker/xpinusdt@bookTicker
```
