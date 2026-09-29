# 0344-29set-log-bot.req

_eseguito: 2026-09-29 06:12 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Sep 29 02:22:37 Trading-Agent python[1830204]: [DRY_RUN] CLOSE SPXUSDT @ 0.39686813674170257 (stop_loss)
Sep 29 02:22:37 Trading-Agent python[1830204]: [referto] SPXUSDT gen_725cb5f4: mai andato a favore (mfe 0.17R): direzione sbagliata
Sep 29 02:22:44 Trading-Agent python[1830204]: [price_stream] connesso · 5 simboli · wss://fstream.binance.com/stream?streams=gpsusdt@bookTicker/jupusdt@bookTicker/promusdt@bookTicker/theusdt@bookTicker/xplusdt@bookTicker
Sep 29 02:22:48 Trading-Agent python[1830204]: [learning] filtrati 5/168 trade (esplorativi: 5)
Sep 29 02:22:48 Trading-Agent python[1830204]: [main] pesi ricalcolati: 108 coppie strat×regime da 168 trade (30g)
Sep 29 02:22:49 Trading-Agent python[1830204]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 29 02:32:20 Trading-Agent python[1830204]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 02:32:20 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 29 02:33:55 Trading-Agent python[1830204]: [DRY_RUN] CLOSE PROMUSDT @ 6.22769514594732 (stop_loss)
Sep 29 02:33:55 Trading-Agent python[1830204]: [referto] PROMUSDT gen_cd5c842f: mai andato a favore (mfe 0.20R): direzione sbagliata
Sep 29 02:33:59 Trading-Agent python[1830204]: [learning] filtrati 5/169 trade (esplorativi: 5)
Sep 29 02:34:00 Trading-Agent python[1830204]: [main] pesi ricalcolati: 109 coppie strat×regime da 169 trade (30g)
Sep 29 02:34:01 Trading-Agent python[1830204]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 29 02:34:02 Trading-Agent python[1830204]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=gpsusdt@bookTicker/jupusdt@bookTicker/theusdt@bookTicker/xplusdt@bookTicker
Sep 29 02:47:43 Trading-Agent python[1830204]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 02:47:43 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 29 02:47:45 Trading-Agent python[1830204]: [selettore] ORCAUSDT gen_9a383fff long p=0.68 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Sep 29 02:47:45 Trading-Agent python[1830204]: [DRY_RUN] OPEN long ORCAUSDT qty=19.3917 @ 1.607 lev=1.0x SL=1.5641 TP=1.7357
Sep 29 02:47:45 Trading-Agent python[1830204]: [declassata] ORCAUSDT gen_9a383fff long size x0.25
Sep 29 02:47:51 Trading-Agent python[1830204]: [price_stream] connesso · 5 simboli · wss://fstream.binance.com/stream?streams=gpsusdt@bookTicker/jupusdt@bookTicker/orcausdt@bookTicker/theusdt@bookTicker/xplusdt@bookTicker
Sep 29 02:47:56 Trading-Agent python[1830204]: [ai-shadow] ok in 11.1s · 1189+715 token
Sep 29 02:53:17 Trading-Agent python[1830204]: [DRY_RUN] CLOSE GPSUSDT @ 0.01040770241255896 (stop_loss)
Sep 29 02:53:17 Trading-Agent python[1830204]: [referto] GPSUSDT gen_8a66a70b: mai andato a favore (mfe 0.07R): direzione sbagliata · controtrend rispetto al regime all'ingresso
Sep 29 02:53:20 Trading-Agent python[1830204]: [learning] filtrati 5/170 trade (esplorativi: 5)
Sep 29 02:53:20 Trading-Agent python[1830204]: [main] pesi ricalcolati: 110 coppie strat×regime da 170 trade (30g)
Sep 29 02:53:21 Trading-Agent python[1830204]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 29 02:53:25 Trading-Agent python[1830204]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=jupusdt@bookTicker/orcausdt@bookTicker/theusdt@bookTicker/xplusdt@bookTicker
Sep 29 02:55:57 Trading-Agent python[1830204]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Sep 29 03:02:14 Trading-Agent python[1830204]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 03:02:14 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 29 03:02:14 Trading-Agent python[1830204]: [rifiuto] ORCAUSDT gen_9a383fff long: posizione gia' aperta su questa coin
Sep 29 03:02:25 Trading-Agent python[1830204]: [ai-shadow] ok in 10.3s · 1053+680 token
Sep 29 03:02:55 Trading-Agent python[1830204]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Sep 29 03:03:58 Trading-Agent python[1830204]: [firebase] letture ultime 24 h: 2694 (rifiutati 1470 · registro 455 · controllo 434 · trade 195 · pesi 49 · memoria 29 · deriva 17 · referti 17) — quota gratuita 50000/giorno
Sep 29 03:03:58 Trading-Agent python[1830204]: [learning] filtrati 5/170 trade (esplorativi: 5)
Sep 29 03:03:58 Trading-Agent python[1830204]: [main] pesi ricalcolati: 110 coppie strat×regime da 170 trade (30g)
Sep 29 03:03:59 Trading-Agent python[1830204]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 29 03:04:01 Trading-Agent python[1830204]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1646 ms
Sep 29 03:05:06 Trading-Agent python[1830204]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Sep 29 03:08:47 Trading-Agent python[1830204]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 03:08:47 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 29 03:08:51 Trading-Agent python[1830204]: [rifiutati] 1 segnali rifiutati valutati
Sep 29 03:17:11 Trading-Agent python[1830204]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 03:17:11 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 29 03:25:37 Trading-Agent python[1830204]: [DRY_RUN] CLOSE JUPUSDT @ 0.3274075 (scale_out)
Sep 29 03:25:41 Trading-Agent python[1830204]: [learning] filtrati 5/171 trade (esplorativi: 5)
Sep 29 03:25:41 Trading-Agent python[1830204]: [main] pesi ricalcolati: 110 coppie strat×regime da 171 trade (30g)
Sep 29 03:25:42 Trading-Agent python[1830204]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 29 03:25:43 Trading-Agent python[1830204]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=orcausdt@bookTicker/theusdt@bookTicker/xplusdt@bookTicker
Sep 29 03:32:23 Trading-Agent python[1830204]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 03:32:23 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 29 03:47:40 Trading-Agent python[1830204]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 03:47:40 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 29 04:02:15 Trading-Agent python[1830204]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 04:02:15 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 29 04:03:16 Trading-Agent python[1830204]: [main] market scan...
Sep 29 04:05:22 Trading-Agent python[1830204]: [scanner] 1 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Sep 29 04:05:22 Trading-Agent python[1830204]: [main] valutate 69 coin validate (69 nel registro): ['QUSDT', 'CROSSUSDT', 'MUBARAKUSDT', 'GPSUSDT', 'B2USDT', 'ORCAUSDT', 'AVAAIUSDT', 'SUIUSDT', 'PHAUSDT', 'DOTUSDT', 'SEIUSDT', 'ENAUSDT', 'SUPERUSDT', 'PENGUUSDT', 'USELESSUSDT', 'MTLUSDT', 'SPXUSDT', 'JUPUSDT', 'PLUMEUSDT', 'XPLUSDT', 'ATOMUSDT', 'WALUSDT', 'UBUSDT', 'GRIFFAINUSDT', 'AXSUSDT', 'PARTIUSDT', 'BANKUSDT', 'PNUTUSDT', 'ARCUSDT', 'ZKUSDT', 'TRUMPUSDT', 'RENDERUSDT', 'BTRUSDT', 'DEXEUSDT', 'JASMYUSDT', 'ZORAUSDT', 'ONGUSDT', 'SAHARAUSDT', 'RAYSOLUSDT', 'HOMEUSDT', 'STXUSDT', 'HEMIUSDT', 'HUMAUSDT', 'HEIUSDT', 'SOPHUSDT', 'PROMUSDT', 'SYRUPUSDT', 'XPINUSDT', 'AIOUSDT', 'EPICUSDT', 'MITOUSDT', 'CATIUSDT', 'TAUSDT', 'GALAUSDT', 'PUNDIXUSDT', 'BMTUSDT', 'STEEMUSDT', 'TUTUSDT', 'BULLAUSDT', 'THEUSDT', 'OPENUSDT', 'FORMUSDT', 'NEIROUSDT', 'SKYAIUSDT', 'CVCUSDT', 'RSRUSDT', 'VETUSDT', 'TSTUSDT', 'FLOCKUSDT']
Sep 29 04:05:53 Trading-Agent python[1830204]: [firebase] letture ultime 24 h: 3107 (rifiutati 1738 · registro 516 · controllo 496 · trade 203 · pesi 54 · memoria 33 · deriva 19 · referti 19) — quota gratuita 50000/giorno
Sep 29 04:05:53 Trading-Agent python[1830204]: [learning] filtrati 5/171 trade (esplorativi: 5)
Sep 29 04:05:53 Trading-Agent python[1830204]: [main] pesi ricalcolati: 110 coppie strat×regime da 171 trade (30g)
Sep 29 04:05:54 Trading-Agent python[1830204]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 29 04:05:56 Trading-Agent python[1830204]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1545 ms
Sep 29 04:11:10 Trading-Agent python[1830204]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 04:11:10 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 29 04:17:36 Trading-Agent python[1830204]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 04:17:36 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 29 04:26:29 Trading-Agent python[1830204]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Sep 29 04:26:30 Trading-Agent python[1830204]: [rifiutati] 1 segnali rifiutati valutati
Sep 29 04:32:25 Trading-Agent python[1830204]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 04:32:25 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 29 04:47:38 Trading-Agent python[1830204]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 04:47:38 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 29 04:57:08 Trading-Agent python[1830204]: [main] verdetti (trailing/post-stop) assegnati a 3 trade paper
Sep 29 05:02:32 Trading-Agent python[1830204]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 05:02:32 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 29 05:06:09 Trading-Agent python[1830204]: [firebase] letture ultime 24 h: 3511 (rifiutati 2006 · registro 572 · controllo 558 · trade 211 · pesi 57 · memoria 37 · deriva 20 · referti 20) — quota gratuita 50000/giorno
Sep 29 05:06:09 Trading-Agent python[1830204]: [learning] filtrati 5/171 trade (esplorativi: 5)
Sep 29 05:06:10 Trading-Agent python[1830204]: [main] pesi ricalcolati: 110 coppie strat×regime da 171 trade (30g)
Sep 29 05:06:11 Trading-Agent python[1830204]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 29 05:06:13 Trading-Agent python[1830204]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1653 ms
Sep 29 05:08:20 Trading-Agent python[1830204]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Sep 29 05:12:30 Trading-Agent python[1830204]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 05:12:30 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 29 05:12:32 Trading-Agent python[1830204]: [main] verdetti (trailing/post-stop) assegnati a 2 trade paper
Sep 29 05:17:24 Trading-Agent python[1830204]: [selettore] MUBARAKUSDT gen_cf6a181e short p=0.66 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Sep 29 05:17:24 Trading-Agent python[1830204]: [DRY_RUN] OPEN short MUBARAKUSDT qty=549.3858 @ 0.06356 lev=1.0x SL=0.0651 TP=0.0598
Sep 29 05:17:24 Trading-Agent python[1830204]: [esplorativa] MUBARAKUSDT gen_cf6a181e short size x0.25
Sep 29 05:17:33 Trading-Agent python[1830204]: [ai-shadow] ok in 9.1s · 782+419 token
Sep 29 05:17:34 Trading-Agent python[1830204]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=mubarakusdt@bookTicker/orcausdt@bookTicker/theusdt@bookTicker/xplusdt@bookTicker
Sep 29 05:27:31 Trading-Agent python[1830204]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 05:27:31 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 29 05:34:01 Trading-Agent python[1830204]: [DRY_RUN] CLOSE ORCAUSDT @ 1.62425 (trailing_stop)
Sep 29 05:34:02 Trading-Agent python[1830204]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 05:34:02 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 29 05:34:04 Trading-Agent python[1830204]: [learning] filtrati 5/172 trade (esplorativi: 5)
Sep 29 05:34:04 Trading-Agent python[1830204]: [main] pesi ricalcolati: 111 coppie strat×regime da 172 trade (30g)
Sep 29 05:34:05 Trading-Agent python[1830204]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 29 05:34:07 Trading-Agent python[1830204]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=mubarakusdt@bookTicker/theusdt@bookTicker/xplusdt@bookTicker
Sep 29 05:34:35 Trading-Agent python[1830204]: [DRY_RUN] CLOSE THEUSDT @ 0.078445 (trailing_stop)
Sep 29 05:34:38 Trading-Agent python[1830204]: [learning] filtrati 5/173 trade (esplorativi: 5)
Sep 29 05:34:38 Trading-Agent python[1830204]: [main] pesi ricalcolati: 112 coppie strat×regime da 173 trade (30g)
Sep 29 05:34:39 Trading-Agent python[1830204]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 29 05:34:44 Trading-Agent python[1830204]: [price_stream] connesso · 2 simboli · wss://fstream.binance.com/stream?streams=mubarakusdt@bookTicker/xplusdt@bookTicker
Sep 29 05:35:41 Trading-Agent python[1830204]: [DRY_RUN] CLOSE MUBARAKUSDT @ 0.062427500000000004 (trailing_stop)
Sep 29 05:35:44 Trading-Agent python[1830204]: [learning] filtrati 6/174 trade (esplorativi: 6)
Sep 29 05:35:44 Trading-Agent python[1830204]: [main] pesi ricalcolati: 112 coppie strat×regime da 174 trade (30g)
Sep 29 05:35:45 Trading-Agent python[1830204]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 29 05:35:48 Trading-Agent python[1830204]: [price_stream] connesso · 1 simboli · wss://fstream.binance.com/stream?streams=xplusdt@bookTicker
Sep 29 05:47:37 Trading-Agent python[1830204]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 05:47:37 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 29 06:02:40 Trading-Agent python[1830204]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Sep 29 06:02:40 Trading-Agent python[1830204]:   return query.where(field_path, op_string, value)
Sep 29 06:03:10 Trading-Agent python[1830204]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Sep 29 06:06:16 Trading-Agent python[1830204]: [firebase] letture ultime 24 h: 3946 (rifiutati 2274 · registro 645 · controllo 620 · trade 216 · pesi 68 · memoria 41 · deriva 24 · referti 24) — quota gratuita 50000/giorno
Sep 29 06:06:16 Trading-Agent python[1830204]: [learning] filtrati 6/174 trade (esplorativi: 6)
Sep 29 06:06:16 Trading-Agent python[1830204]: [main] pesi ricalcolati: 112 coppie strat×regime da 174 trade (30g)
Sep 29 06:06:17 Trading-Agent python[1830204]: [referti] 2 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Sep 29 06:06:19 Trading-Agent python[1830204]: [controllo] pubblicato: sistema verde, paper giallo, 2 anomalie, 1747 ms
Sep 29 06:07:25 Trading-Agent python[1830204]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
```
