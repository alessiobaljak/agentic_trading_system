# 0242-lista-bianca.req

_eseguito: 2026-09-25 06:36 UTC_

**richiesta:** `lista`
**eseguito:** `cat ops/allowlist`
**esito:** codice 0 in 0.0s

```
# LISTA BIANCA DELL'AGENTE OPS — copiala in `ops/allowlist` (senza .example).
#
# Questo file NON e' versionato, ed e' il punto in cui sta tutto il controllo:
# l'agente esegue SOLO cio' che compare qui. Una richiesta puo' nominare una voce,
# mai comporre un comando. Se fosse nel repo, chiunque possa committare potrebbe
# ampliarla — e la lista bianca non sarebbe piu' una garanzia.
#
# Formato:   chiave: comando            (una riga, niente shell, niente pipe)
#            chiave: comando +args      se la richiesta puo' aggiungere argomenti
#
# Regola pratica: aggiungi una voce solo se sei disposto a vederla eseguita
# automaticamente, di notte, senza che tu la stia guardando.
#
# DUE COSE DA NON METTERE, imparate a caro prezzo:
#  * niente `+args` se puoi evitarlo. Gli argomenti vengono appesi in coda al
#    comando, e `/root/.env` o `--file=/root/.git-credentials` superano tutti i
#    filtri: e' il chiamante a scegliere COSA il comando andra' a leggere.
#  * niente `git remote -v` ne' `git config --list`: se il token e' nell'URL del
#    remoto, uscirebbe in chiaro dentro una risposta committata.

# ---- diagnosi (sola lettura) ----------------------------------------------
autopsy:      .venv/bin/python -m scripts.gate_autopsy
gate:         .venv/bin/python -m scripts.gate_progress
supervisor:   .venv/bin/python -m scripts.supervisor --dry-run
stato:        .venv/bin/python -m scripts.state_snapshot --no-write
shadow:       .venv/bin/python -m scripts.shadow_report
trades:       .venv/bin/python -m scripts.trade_stats
connettivita: .venv/bin/python -m scripts.connectivity_check
test:         .venv/bin/python -m pytest -q
confronto:    .venv/bin/python -m scripts.confronto_gate_paper
storico-oi:   .venv/bin/python -m scripts.binance_metrics_probe

# ---- diagnosi del canale stesso (indispensabili se smette di rispondere) ---
log-ops:      journalctl -u trading-ops.service -n 200 --no-pager
ops-unit:     systemctl show trading-ops.service -p ActiveState -p SubState -p Result -p ExecMainStatus -p ExecMainStartTimestamp
git-stato:    git status --short --branch
git-storia:   git log --oneline -20 --decorate
attivi:       systemctl is-active trading-bot.service trading-ops.timer trading-optimizer.timer trading-supervisor.timer
ai-stato:     .venv/bin/python -m scripts.ai_status
mfe:          .venv/bin/python -m scripts.mfe_report

# ---- stato del sistema -----------------------------------------------------
servizi:      systemctl list-timers --no-pager trading-*
log-bot:      journalctl -u trading-bot.service -n 120 --no-pager
log-gate:     journalctl -u trading-optimizer.service -n 80 --no-pager
log-super:    journalctl -u trading-supervisor.service -n 40 --no-pager
memoria:      free -g
disco:        df -h /
rifiuti: journalctl -u trading-bot.service --since -24h --no-pager -g "\[rifiuto\]"

# ---- azioni operative (cambiano qualcosa, ma nulla di distruttivo) ---------
aggiorna:     git pull
riavvia-bot:  systemctl restart trading-bot.service
lancia-gate:  systemctl start --no-block trading-optimizer.service
lancia-super: .venv/bin/python -m scripts.supervisor
portafoglio: .venv/bin/python -m scripts.portafoglio_backtest
selettore: .venv/bin/python -m scripts.selettore_report

# ---- DISTRUTTIVE: lasciate commentate di proposito -------------------------
# fast_gate AZZERA il registro validato: i passaggi accumulati (settimane di
# attesa) spariscono. Abilitala solo quando vuoi davvero una rivalidazione da capo.
# fast-gate:  bash scripts/fast_gate.sh --yes
# reset-paper: .venv/bin/python -m scripts.reset_paper --yes
spike: .venv/bin/python -m scripts.spike_response

# --- analisi in sola lettura ---
gate-top:      .venv/bin/python -m scripts.gate_progress --top 40
gate-vs-paper: .venv/bin/python -m scripts.gate_vs_paper
edge:          .venv/bin/python -m scripts.edge_stability
frequenza:     .venv/bin/python -m scripts.signal_frequency
sopravvivenza: .venv/bin/python -m scripts.survivorship_report
confidenza:    .venv/bin/python -m scripts.confidence_analysis
costi:         .venv/bin/python -m scripts.revalidate_costs

# --- stato macchina ---
carico:        uptime
processi:      ps -eo pid,pcpu,pmem,etime,args --sort=-pcpu
tmux:          tmux ls
cache:         du -sh .cache

# --- rimettere in moto un timer inceppato ---
riavvia-gate:        systemctl restart trading-optimizer.timer
riavvia-super-timer: systemctl restart trading-supervisor.timer
timeframe:    .venv/bin/python -m scripts.timeframe_probe
lista: cat ops/allowlist
```
