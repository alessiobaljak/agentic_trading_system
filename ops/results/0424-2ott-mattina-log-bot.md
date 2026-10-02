# 0424-2ott-mattina-log-bot.req

_eseguito: 2026-10-02 06:04 UTC_

**richiesta:** `log-bot`
**eseguito:** `journalctl -u trading-bot.service -n 120 --no-pager`
**esito:** codice 0 in 0.1s

```
Oct 02 02:13:31 Trading-Agent python[1975598]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 02 02:13:31 Trading-Agent python[1975598]:   return query.where(field_path, op_string, value)
Oct 02 02:17:19 Trading-Agent python[1975598]: [main] trade bloccato dal gate: stop troppo largo: 7.1% del prezzo > 6% (ATR gonfiato: primo incasso a +11%, lock a +5%)
Oct 02 02:17:19 Trading-Agent python[1975598]: [rifiuto] SCRUSDT gen_bd8f158b short: risk gate: stop troppo largo: 7.1% del prezzo > 6% (ATR gonfiato: primo incasso a +11%, lock a +5%)
Oct 02 02:28:37 Trading-Agent python[1975598]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 02 02:28:37 Trading-Agent python[1975598]:   return query.where(field_path, op_string, value)
Oct 02 02:29:42 Trading-Agent python[1975598]: [firebase] letture ultime 24 h: 3253 (rifiutati 1480 · controllo 682 · registro 659 · trade 276 · pesi 51 · memoria 45 · deriva 17 · referti 17) — quota gratuita 50000/giorno
Oct 02 02:29:42 Trading-Agent python[1975598]: [learning] filtrati 8/220 trade (esplorativi: 8)
Oct 02 02:29:43 Trading-Agent python[1975598]: [main] pesi ricalcolati: 140 coppie strat×regime da 220 trade (30g)
Oct 02 02:29:44 Trading-Agent python[1975598]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 02 02:29:46 Trading-Agent python[1975598]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1613 ms
Oct 02 02:43:51 Trading-Agent python[1975598]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 02 02:43:51 Trading-Agent python[1975598]:   return query.where(field_path, op_string, value)
Oct 02 02:58:58 Trading-Agent python[1975598]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 02 02:58:58 Trading-Agent python[1975598]:   return query.where(field_path, op_string, value)
Oct 02 03:14:05 Trading-Agent python[1975598]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 02 03:14:05 Trading-Agent python[1975598]:   return query.where(field_path, op_string, value)
Oct 02 03:25:07 Trading-Agent python[1975598]: [main] market scan...
Oct 02 03:27:16 Trading-Agent python[1975598]: [scanner] 2 coin validate sotto la soglia di volume ammesse comunque: hanno passato il gate coi loro costi
Oct 02 03:27:16 Trading-Agent python[1975598]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 02 03:27:16 Trading-Agent python[1975598]:   return query.where(field_path, op_string, value)
Oct 02 03:27:16 Trading-Agent python[1975598]: [main] valutate 71 coin validate (71 nel registro): ['DEXEUSDT', 'ZKUSDT', 'USELESSUSDT', 'DOTUSDT', 'XPLUSDT', 'RENDERUSDT', 'MUBARAKUSDT', 'GPSUSDT', 'ARCUSDT', 'SCRUSDT', 'HEIUSDT', 'FORMUSDT', 'PENGUUSDT', 'ENAUSDT', 'ORCAUSDT', 'SUIUSDT', 'FLOCKUSDT', 'PARTIUSDT', 'BMTUSDT', 'NEIROUSDT', 'ATOMUSDT', 'PLUMEUSDT', 'PROMUSDT', 'RSRUSDT', 'CATIUSDT', 'SUPERUSDT', 'VETUSDT', 'TRUMPUSDT', 'BTRUSDT', 'GALAUSDT', 'ZORAUSDT', 'PUNDIXUSDT', 'JUPUSDT', 'TAUSDT', 'SPXUSDT', 'MTLUSDT', 'PNUTUSDT', 'IDUSDT', 'HEMIUSDT', 'WALUSDT', 'QUSDT', 'TUTUSDT', 'PHAUSDT', 'SAHARAUSDT', 'RAYSOLUSDT', 'STXUSDT', 'UBUSDT', 'MITOUSDT', 'HUMAUSDT', 'SYRUPUSDT', 'SEIUSDT', 'AVAAIUSDT', 'JASMYUSDT', 'AXSUSDT', 'BANKUSDT', 'CVCUSDT', 'STEEMUSDT', 'XPINUSDT', 'AIOUSDT', 'THEUSDT', 'BULLAUSDT', 'SKYAIUSDT', 'HOMEUSDT', 'EPICUSDT', 'OPENUSDT', 'GRIFFAINUSDT', 'TSTUSDT', 'SOPHUSDT', 'B2USDT', 'ONGUSDT', 'CROSSUSDT']
Oct 02 03:29:22 Trading-Agent python[1975598]: [rifiutati] 1 segnali rifiutati valutati
Oct 02 03:29:53 Trading-Agent python[1975598]: [firebase] letture ultime 24 h: 3500 (rifiutati 1596 · controllo 744 · registro 714 · trade 280 · pesi 54 · memoria 49 · deriva 18 · referti 18) — quota gratuita 50000/giorno
Oct 02 03:29:53 Trading-Agent python[1975598]: [learning] filtrati 8/220 trade (esplorativi: 8)
Oct 02 03:29:53 Trading-Agent python[1975598]: [main] pesi ricalcolati: 140 coppie strat×regime da 220 trade (30g)
Oct 02 03:29:54 Trading-Agent python[1975598]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 02 03:29:56 Trading-Agent python[1975598]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1666 ms
Oct 02 03:32:42 Trading-Agent python[1975598]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 02 03:32:42 Trading-Agent python[1975598]:   return query.where(field_path, op_string, value)
Oct 02 03:39:24 Trading-Agent python[1975598]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 02 03:44:37 Trading-Agent python[1975598]: [rifiutati] 1 segnali rifiutati valutati
Oct 02 03:47:23 Trading-Agent python[1975598]: [main] trade bloccato dal gate: stop troppo largo: 9.8% del prezzo > 6% (ATR gonfiato: primo incasso a +15%, lock a +7%)
Oct 02 03:47:23 Trading-Agent python[1975598]: [rifiuto] SCRUSDT gen_bd8f158b short: risk gate: stop troppo largo: 9.8% del prezzo > 6% (ATR gonfiato: primo incasso a +15%, lock a +7%)
Oct 02 03:47:53 Trading-Agent python[1975598]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 02 03:59:44 Trading-Agent python[1975598]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 02 03:59:44 Trading-Agent python[1975598]:   return query.where(field_path, op_string, value)
Oct 02 04:14:54 Trading-Agent python[1975598]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 02 04:14:54 Trading-Agent python[1975598]:   return query.where(field_path, op_string, value)
Oct 02 04:30:01 Trading-Agent python[1975598]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 02 04:30:01 Trading-Agent python[1975598]:   return query.where(field_path, op_string, value)
Oct 02 04:30:03 Trading-Agent python[1975598]: [main] verdetti (trailing/post-stop) assegnati a 2 trade paper
Oct 02 04:30:04 Trading-Agent python[1975598]: [firebase] letture ultime 24 h: 3773 (rifiutati 1716 · controllo 806 · registro 785 · trade 285 · pesi 59 · memoria 53 · selettore 21 · deriva 19) — quota gratuita 50000/giorno
Oct 02 04:30:04 Trading-Agent python[1975598]: [learning] filtrati 8/220 trade (esplorativi: 8)
Oct 02 04:30:04 Trading-Agent python[1975598]: [main] pesi ricalcolati: 140 coppie strat×regime da 220 trade (30g)
Oct 02 04:30:06 Trading-Agent python[1975598]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 02 04:30:08 Trading-Agent python[1975598]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1849 ms
Oct 02 04:32:56 Trading-Agent python[1975598]: [scarti] 1 esplorativa dietro una validata
Oct 02 04:32:58 Trading-Agent python[1975598]: [selettore] HEMIUSDT gen_f001d778 short p=0.59 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Oct 02 04:32:58 Trading-Agent python[1975598]: [DRY_RUN] OPEN short HEMIUSDT qty=9939.9007 @ 0.006463 lev=2.0x SL=0.0066 TP=0.0063
Oct 02 04:32:58 Trading-Agent python[1975598]: [declassata] HEMIUSDT gen_f001d778 short size x0.25
Oct 02 04:32:59 Trading-Agent python[1975598]: [selettore] ENAUSDT gen_bb762669 short p=0.69 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Oct 02 04:32:59 Trading-Agent python[1975598]: [DRY_RUN] OPEN short ENAUSDT qty=219.4595 @ 0.24783 lev=2.0x SL=0.2540 TP=0.2386
Oct 02 04:32:59 Trading-Agent python[1975598]: [declassata] ENAUSDT gen_bb762669 short size x0.25
Oct 02 04:33:05 Trading-Agent python[1975598]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=crossusdt@bookTicker/enausdt@bookTicker/hemiusdt@bookTicker/syrupusdt@bookTicker
Oct 02 04:33:38 Trading-Agent python[1975598]: [DRY_RUN] CLOSE SYRUPUSDT @ 0.2382975 (trailing_stop)
Oct 02 04:33:40 Trading-Agent python[1975598]: [learning] filtrati 8/221 trade (esplorativi: 8)
Oct 02 04:33:41 Trading-Agent python[1975598]: [main] pesi ricalcolati: 141 cop

[... 18 caratteri omessi (testa e coda conservate) ...]

a 221 trade (30g)
Oct 02 04:33:42 Trading-Agent python[1975598]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 02 04:33:44 Trading-Agent python[1975598]: [price_stream] connesso · 3 simboli · wss://fstream.binance.com/stream?streams=crossusdt@bookTicker/enausdt@bookTicker/hemiusdt@bookTicker
Oct 02 04:47:22 Trading-Agent python[1975598]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 02 04:47:22 Trading-Agent python[1975598]:   return query.where(field_path, op_string, value)
Oct 02 04:47:22 Trading-Agent python[1975598]: [scarti] 3 secondo segnale stessa coin
Oct 02 04:47:23 Trading-Agent python[1975598]: [selettore] AIOUSDT gen_581d4a68 long p=0.58 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Oct 02 04:47:23 Trading-Agent python[1975598]: [DRY_RUN] OPEN long AIOUSDT qty=2379.7765 @ 0.0389 lev=1.0x SL=0.0385 TP=0.0401
Oct 02 04:47:23 Trading-Agent python[1975598]: [declassata] AIOUSDT gen_581d4a68 long size x0.25
Oct 02 04:47:29 Trading-Agent python[1975598]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=aiousdt@bookTicker/crossusdt@bookTicker/enausdt@bookTicker/hemiusdt@bookTicker
Oct 02 04:47:32 Trading-Agent python[1975598]: [selettore] BULLAUSDT gen_7ac562e3 short p=0.67 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Oct 02 04:47:32 Trading-Agent python[1975598]: [DRY_RUN] OPEN short BULLAUSDT qty=664.7009 @ 0.08291 lev=2.0x SL=0.0840 TP=0.0807
Oct 02 04:47:32 Trading-Agent python[1975598]: [declassata] BULLAUSDT gen_7ac562e3 short size x0.25
Oct 02 04:47:32 Trading-Agent python[1975598]: [rifiuto] ENAUSDT gen_bb762669 short: posizione gia' aperta su questa coin
Oct 02 04:47:38 Trading-Agent python[1975598]: [price_stream] connesso · 5 simboli · wss://fstream.binance.com/stream?streams=aiousdt@bookTicker/bullausdt@bookTicker/crossusdt@bookTicker/enausdt@bookTicker/hemiusdt@bookTicker
Oct 02 04:49:08 Trading-Agent python[1975598]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 02 05:02:33 Trading-Agent python[1975598]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 02 05:02:33 Trading-Agent python[1975598]:   return query.where(field_path, op_string, value)
Oct 02 05:02:34 Trading-Agent python[1975598]: [selettore] HUMAUSDT gen_771790b1 short p=0.61 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Oct 02 05:02:34 Trading-Agent python[1975598]: [DRY_RUN] OPEN short HUMAUSDT qty=1287.2273 @ 0.034379 lev=1.0x SL=0.0351 TP=0.0329
Oct 02 05:02:35 Trading-Agent python[1975598]: [declassata] HUMAUSDT gen_771790b1 short size x0.25
Oct 02 05:02:35 Trading-Agent python[1975598]: [selettore] SYRUPUSDT gen_4c6df481 long p=0.58 soglia=0.45 -> avrebbe aperto (ombra: apre comunque)
Oct 02 05:02:35 Trading-Agent python[1975598]: [DRY_RUN] OPEN long SYRUPUSDT qty=784.1209 @ 0.23612 lev=2.0x SL=0.2311 TP=0.2486
Oct 02 05:02:44 Trading-Agent python[1975598]: [price_stream] connesso · 7 simboli · wss://fstream.binance.com/stream?streams=aiousdt@bookTicker/bullausdt@bookTicker/crossusdt@bookTicker/enausdt@bookTicker/hemiusdt@bookTicker/humausdt@bookTicker/syrupusdt@bookTicker
Oct 02 05:04:14 Trading-Agent python[1975598]: [rifiutati] 1 segnali rifiutati valutati
Oct 02 05:17:21 Trading-Agent python[1975598]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 02 05:17:21 Trading-Agent python[1975598]:   return query.where(field_path, op_string, value)
Oct 02 05:17:21 Trading-Agent python[1975598]: [rifiuto] HUMAUSDT gen_771790b1 short: posizione gia' aperta su questa coin
Oct 02 05:19:30 Trading-Agent python[1975598]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 02 05:23:20 Trading-Agent python[1975598]: [DRY_RUN] CLOSE BULLAUSDT @ 0.08402278012906354 (stop_loss)
Oct 02 05:23:20 Trading-Agent python[1975598]: [referto] BULLAUSDT gen_7ac562e3: mai andato a favore (mfe 0.11R): direzione sbagliata · controtrend rispetto al regime all'ingresso
Oct 02 05:23:26 Trading-Agent python[1975598]: [price_stream] connesso · 6 simboli · wss://fstream.binance.com/stream?streams=aiousdt@bookTicker/crossusdt@bookTicker/enausdt@bookTicker/hemiusdt@bookTicker/humausdt@bookTicker/syrupusdt@bookTicker
Oct 02 05:23:31 Trading-Agent python[1975598]: [learning] filtrati 8/222 trade (esplorativi: 8)
Oct 02 05:23:32 Trading-Agent python[1975598]: [main] pesi ricalcolati: 141 coppie strat×regime da 222 trade (30g)
Oct 02 05:23:33 Trading-Agent python[1975598]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 02 05:30:33 Trading-Agent python[1975598]: [firebase] letture ultime 24 h: 4016 (rifiutati 1812 · controllo 868 · registro 842 · trade 289 · pesi 66 · memoria 57 · deriva 22 · referti 22) — quota gratuita 50000/giorno
Oct 02 05:30:34 Trading-Agent python[1975598]: [learning] filtrati 8/222 trade (esplorativi: 8)
Oct 02 05:30:34 Trading-Agent python[1975598]: [main] pesi ricalcolati: 141 coppie strat×regime da 222 trade (30g)
Oct 02 05:30:35 Trading-Agent python[1975598]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 02 05:30:37 Trading-Agent python[1975598]: [controllo] pubblicato: sistema giallo, paper giallo, 3 anomalie, 1696 ms
Oct 02 05:38:58 Trading-Agent python[1975598]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 02 05:38:58 Trading-Agent python[1975598]:   return query.where(field_path, op_string, value)
Oct 02 05:39:00 Trading-Agent python[1975598]: [cattura] misure dopo l'uscita (post-uscita/motore/verdetto gate) aggiunte a 1 trade paper
Oct 02 05:47:47 Trading-Agent python[1975598]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 02 05:47:47 Trading-Agent python[1975598]:   return query.where(field_path, op_string, value)
Oct 02 05:47:47 Trading-Agent python[1975598]: [scarti] 1 secondo segnale stessa coin
Oct 02 05:47:47 Trading-Agent python[1975598]: [rifiuto] HUMAUSDT gen_771790b1 short: posizione gia' aperta su questa coin
Oct 02 05:48:20 Trading-Agent python[1975598]: [DRY_RUN] CLOSE AIOUSDT @ 0.03848894480978522 (stop_loss)
Oct 02 05:48:20 Trading-Agent python[1975598]: [referto] AIOUSDT gen_581d4a68: mai andato a favore (mfe 0.13R): direzione sbagliata
Oct 02 05:48:24 Trading-Agent python[1975598]: [main] verdetti (trailing/post-stop) assegnati a 1 trade paper
Oct 02 05:48:24 Trading-Agent python[1975598]: [learning] filtrati 8/223 trade (esplorativi: 8)
Oct 02 05:48:24 Trading-Agent python[1975598]: [main] pesi ricalcolati: 142 coppie strat×regime da 223 trade (30g)
Oct 02 05:48:25 Trading-Agent python[1975598]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 02 05:48:26 Trading-Agent python[1975598]: [price_stream] connesso · 5 simboli · wss://fstream.binance.com/stream?streams=crossusdt@bookTicker/enausdt@bookTicker/hemiusdt@bookTicker/humausdt@bookTicker/syrupusdt@bookTicker
Oct 02 05:51:35 Trading-Agent python[1975598]: [main] registro riscritto dal gate: ricarico pesi, registro, spec e selettore
Oct 02 05:55:53 Trading-Agent python[1975598]: [DRY_RUN] CLOSE HUMAUSDT @ 0.03511451306572168 (stop_loss)
Oct 02 05:55:53 Trading-Agent python[1975598]: [referto] HUMAUSDT gen_771790b1: a favore fino a 0.73R ma sotto il primo gradino (2R) · il lock non si e' mai armato (serviva 1R)
Oct 02 05:55:57 Trading-Agent python[1975598]: [learning] filtrati 8/224 trade (esplorativi: 8)
Oct 02 05:55:58 Trading-Agent python[1975598]: [main] pesi ricalcolati: 143 coppie strat×regime da 224 trade (30g)
Oct 02 05:55:58 Trading-Agent python[1975598]: [referti] 3 ipotesi dai referti del paper -> varianti al prossimo giro del gate: gen_fa304106: solo_long — short 4/4 persi (campione 4) | gen_fa304106: solo_short — long 3/3 persi (campione 3) | gen_fca11c08: conferma_trend — 6 perdite controtrend (campione 6)
Oct 02 05:56:02 Trading-Agent python[1975598]: [price_stream] connesso · 4 simboli · wss://fstream.binance.com/stream?streams=crossusdt@bookTicker/enausdt@bookTicker/hemiusdt@bookTicker/syrupusdt@bookTicker
Oct 02 06:02:29 Trading-Agent python[1975598]: /root/agentic_trading_system/.venv/lib/python3.12/site-packages/google/cloud/firestore_v1/base_collection.py:317: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
Oct 02 06:02:29 Trading-Agent python[1975598]:   return query.where(field_path, op_string, value)
```
