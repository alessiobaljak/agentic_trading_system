# 0194-log-super.req

_eseguito: 2026-09-24 12:30 UTC_

**richiesta:** `log-super`
**eseguito:** `journalctl -u trading-supervisor.service -n 40 --no-pager`
**esito:** codice 0 in 0.4s

```
Sep 24 07:03:35 Trading-Agent python[1626264]: [supervisor] validate=59 ready=True stagnazione=2.0g · valutazioni=1770 passate=1 (tasso 0.056%)
Sep 24 07:03:35 Trading-Agent python[1626264]: [supervisor] NONE: GATE 1 superato: il paper opera, la taratura si ferma
Sep 24 07:03:36 Trading-Agent systemd[1]: trading-supervisor.service: Deactivated successfully.
Sep 24 07:03:36 Trading-Agent systemd[1]: Finished trading-supervisor.service - Agentic Trading - supervisore (taratura automatica dentro il budget).
Sep 24 07:03:36 Trading-Agent systemd[1]: trading-supervisor.service: Consumed 1.928s CPU time.
Sep 24 08:02:15 Trading-Agent systemd[1]: Starting trading-supervisor.service - Agentic Trading - supervisore (taratura automatica dentro il budget)...
Sep 24 08:02:16 Trading-Agent python[1628679]: [firebase] connesso (Firestore + RTDB)
Sep 24 08:02:17 Trading-Agent python[1628679]: [supervisor] validate=59 ready=True stagnazione=2.0g · valutazioni=1770 passate=1 (tasso 0.056%)
Sep 24 08:02:17 Trading-Agent python[1628679]: [supervisor] NONE: GATE 1 superato: il paper opera, la taratura si ferma
Sep 24 08:02:18 Trading-Agent systemd[1]: trading-supervisor.service: Deactivated successfully.
Sep 24 08:02:18 Trading-Agent systemd[1]: Finished trading-supervisor.service - Agentic Trading - supervisore (taratura automatica dentro il budget).
Sep 24 08:02:18 Trading-Agent systemd[1]: trading-supervisor.service: Consumed 2.180s CPU time.
Sep 24 09:04:41 Trading-Agent systemd[1]: Starting trading-supervisor.service - Agentic Trading - supervisore (taratura automatica dentro il budget)...
Sep 24 09:04:43 Trading-Agent python[1630777]: [firebase] connesso (Firestore + RTDB)
Sep 24 09:04:43 Trading-Agent python[1630777]: [supervisor] validate=59 ready=True stagnazione=2.0g · valutazioni=1770 passate=1 (tasso 0.056%)
Sep 24 09:04:43 Trading-Agent python[1630777]: [supervisor] NONE: GATE 1 superato: il paper opera, la taratura si ferma
Sep 24 09:04:44 Trading-Agent systemd[1]: trading-supervisor.service: Deactivated successfully.
Sep 24 09:04:44 Trading-Agent systemd[1]: Finished trading-supervisor.service - Agentic Trading - supervisore (taratura automatica dentro il budget).
Sep 24 09:04:44 Trading-Agent systemd[1]: trading-supervisor.service: Consumed 2.807s CPU time.
Sep 24 10:02:01 Trading-Agent systemd[1]: Starting trading-supervisor.service - Agentic Trading - supervisore (taratura automatica dentro il budget)...
Sep 24 10:02:04 Trading-Agent python[1631749]: [firebase] connesso (Firestore + RTDB)
Sep 24 10:02:04 Trading-Agent python[1631749]: [supervisor] validate=59 ready=True stagnazione=2.1g · valutazioni=1770 passate=1 (tasso 0.056%)
Sep 24 10:02:04 Trading-Agent python[1631749]: [supervisor] NONE: GATE 1 superato: il paper opera, la taratura si ferma
Sep 24 10:02:06 Trading-Agent systemd[1]: trading-supervisor.service: Deactivated successfully.
Sep 24 10:02:06 Trading-Agent systemd[1]: Finished trading-supervisor.service - Agentic Trading - supervisore (taratura automatica dentro il budget).
Sep 24 10:02:06 Trading-Agent systemd[1]: trading-supervisor.service: Consumed 3.881s CPU time.
Sep 24 11:02:51 Trading-Agent systemd[1]: Starting trading-supervisor.service - Agentic Trading - supervisore (taratura automatica dentro il budget)...
Sep 24 11:02:53 Trading-Agent python[1632677]: [firebase] connesso (Firestore + RTDB)
Sep 24 11:02:53 Trading-Agent python[1632677]: [supervisor] validate=59 ready=True stagnazione=2.1g · valutazioni=1770 passate=1 (tasso 0.056%)
Sep 24 11:02:53 Trading-Agent python[1632677]: [supervisor] NONE: GATE 1 superato: il paper opera, la taratura si ferma
Sep 24 11:02:54 Trading-Agent systemd[1]: trading-supervisor.service: Deactivated successfully.
Sep 24 11:02:54 Trading-Agent systemd[1]: Finished trading-supervisor.service - Agentic Trading - supervisore (taratura automatica dentro il budget).
Sep 24 11:02:54 Trading-Agent systemd[1]: trading-supervisor.service: Consumed 2.966s CPU time.
Sep 24 12:02:43 Trading-Agent systemd[1]: Starting trading-supervisor.service - Agentic Trading - supervisore (taratura automatica dentro il budget)...
Sep 24 12:02:44 Trading-Agent python[1633725]: [firebase] connesso (Firestore + RTDB)
Sep 24 12:02:45 Trading-Agent python[1633725]: [supervisor] validate=59 ready=True stagnazione=2.2g · valutazioni=1770 passate=1 (tasso 0.056%)
Sep 24 12:02:45 Trading-Agent python[1633725]: [supervisor] NONE: GATE 1 superato: il paper opera, la taratura si ferma
Sep 24 12:02:46 Trading-Agent systemd[1]: trading-supervisor.service: Deactivated successfully.
Sep 24 12:02:46 Trading-Agent systemd[1]: Finished trading-supervisor.service - Agentic Trading - supervisore (taratura automatica dentro il budget).
Sep 24 12:02:46 Trading-Agent systemd[1]: trading-supervisor.service: Consumed 2.939s CPU time.
```
