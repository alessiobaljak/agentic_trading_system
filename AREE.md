# Le aree del repository: chi scrive dove

Il proprietario, 11 novembre 2026: «una cartella con crypto dove ci scrivi solo tu, una cartella con stock dove ci scrive l'altra
sessione e altre cartelle che magari creo dopo tipo Forex». Ogni area ha la sua sessione; una sessione scrive solo nella sua area e
nei file in comune, e legge tutto. Il blocco è nel codice (`.claude/hooks/aree.py`, test `tests/test_hook_aree.py`), la mappa che
legge è `AREE.json`.

| Area | Chi scrive | Dove |
|---|---|---|
| **crypto** | la sessione delle crypto | tutto quello che non è di un'altra area né in comune: `bot/`, `research/`, `ops/`, `scripts/`, `docs/`, `tests/`, `backtesting/`, `firebase/`, `allocazione/`, `gate2/`, `reviews/`, `audits/` e il resto |
| **stock** (azioni) | la sessione «trading stock» | `stock/` e la sua scheda in dashboard, `dashboard/app/components/stock/` |
| **in comune** | tutte, con attenzione | `dashboard/` (ogni area tocca la sua scheda e una riga in `dashboard/app/components/aree.ts`), `.claude/`, `.github/`, `AREE.md`, `AREE.json`, `CLAUDE.md`, `README.md`, `.gitignore` |

## Come funziona il blocco
* Ogni sessione è registrata in `AREE.json` (sezione `sessioni`) con il suo identificativo remoto e la sua area. Una sessione non
  registrata scrive solo nei file in comune finché non si registra: `python3 .claude/hooks/aree.py registra <area>`, poi commit di
  `AREE.json`.
* Blocca le scritture con Edit e Write e i comandi che scrivono in un'altra area (redirezioni, `rm`, `mv`, `cp`, `sed -i`,
  `git add`...). È una protezione contro gli errori, non contro chi la vuole aggirare: uno script che scrive da solo non lo vede.
* Leggere è sempre permesso: una sessione può guardare il lavoro delle altre per imparare (`stock/LEZIONI_DALLE_CRYPTO.md`).

## Un'area nuova (per esempio Forex)
1. Una cartella in cima al repository, `forex/`, con il suo `README.md`.
2. In `AREE.json` una riga nelle `aree`: `"forex": {"descrizione": "...", "cartelle": ["forex/", "dashboard/app/components/forex/"]}`.
3. Una sessione nuova per l'area, che si registra con `python3 .claude/hooks/aree.py registra forex`.
4. In dashboard una riga in `dashboard/app/components/aree.ts` e la sua scheda in `dashboard/app/components/forex/`
   (`dashboard/GUIDA_SCHEDA_AZIONI.md` vale come esempio).

## Il trasloco delle crypto in `crypto/` (rimandato)
Spostare oggi il lavoro delle crypto in una cartella `crypto/` fermerebbe il bot sulla macchina (servizi, timer e percorsi da
aggiornare sulla VPS a mano) e tocca centinaia di file, le routine e il controllo della versione del conto vero. Il proprietario ha
scelto di farlo, se servirà, in un momento deciso insieme (11 novembre 2026).
