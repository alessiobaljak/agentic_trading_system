# Stato della sessione (compito in corso, decisioni, prossimi passi)

Aggiornato a ogni tappa dalla sessione principale (regole dei token in `CLAUDE.md`). Corto: il resto sta nel diario
(`docs/andremo_live.md`) e nei piani.

## Compito in corso (17 novembre 2026, 12:30 UTC)
- **Bot**: dal 16 novembre 07:36 UTC gira la fase 2 (versione 884b9b1a: conto vero spento, pulsante di approvazione, funding dei paper per
  regolamento); `DRY_RUN` vero. Demo di G1
  a 1.000 USDT dall'8 novembre (misura dei minimi a ogni ribilancio nel piano `research/programma7/MIGLIORARE_G1.md`, voce 8). Fase 2
  (codice del conto vero, spento) committata (ff89531), caricata dal riavvio del 16 novembre.
- **Conto vero**: lista del proprietario e decisioni in `docs/conto_vero.md` (riletta il 12 novembre). Punti aperti prima
  dell'accensione: canale di approvazione della versione (firma o dashboard: la regola di GitHub non basta), Firebase, Binance, le
  decisioni a-k, i problemi 66, 70, 72, 73, pulsante e stato in dashboard, revisione finale.
- **Ricerca**: due binari a ogni giro (migliorare G1, ricerca nuova). Agenti: strategy-scout, strategy-researcher (prima in modalità
  verifica), backtest-auditor, strategy-improver (voci 9-13 del piano di G1), gate2-reconciler e portfolio-allocator il lunedì.
  Prove 149-151 chiuse senza candidate; prova 152 (concentrazione di G1) chiusa: il tetto del 20% non passa l'esame scritto solo per
  8 ordini saltati in più su circa 123.000, decisione al proprietario (conto 312). Revisione di G1: PASS tecnico con 4 Alti
  (`audits/reports/2026-11-12-G1_CONTO_VERO.md`). Riesame: fatte la 28 e la 113; in corso la 96 (backtest-auditor); resta la 55.
  Prove 153 (libro degli ordini) e 154 (dimensione media dello scambio) chiuse senza candidate (conto 316); riesami finiti (28 PASS
  tecnico, 113, 96 e 55 restano bocciate). Pulsante di approvazione, estratto dal demo e funding dei paper committati, in attesa del
  riavvio (ok del proprietario). 13 novembre: lo scout non trova idee forti (idee 138-140 nella coda con il perché no); voce 9 di G1
  misurata (scarto del demo = minimi + monete mancanti; costo nel funding); trappola del funding di novembre nel pannello annotata in
  `research/INDEX.md` (per i confronti con paper e demo si usa `applica_stima`).
  Pomeriggio: voce 11 di G1 misurata (il demo è sopra il paper solo per il primo giorno; a regime il paper sopravvaluta di 0,045
  punti al giorno); prova 155 (G1 frenata dall'indice di paura delle opzioni) non passa, conto 318; le spese di G1 della prova 120
  erano un po' sovrastimate (ordini senza candele a 1 ora).
  14-15 novembre: prova 156 (uscita dal lato venduto dopo una fiammata) no; lo stato della macchina scrive i pesi di oggi di paper e
  demo moneta per moneta (96c6094, APPROVE di live-path-reviewer, senza riavvio); il ritardo del demo sul paper nei giorni forti viene
  dalla moneta che il demo non ha (龙虾USDT) e dai resti sotto il minimo, non dall'arrotondamento. Su richiesta del proprietario: prova
  157 funding coperto su BTC ed ETH (FAIL di backtest-auditor per il margine; circa +4% l'anno dal 2022), 158 G1 con più leva (no), 159
  base dei trimestrali (no); idea 145 e prova 160 (G1 con funding coperto) in attesa della 157 rifatta. Conto delle prove 326.
  16-17 novembre: prova 161 (funding coperto con il margine vero) PASS tecnico con 2 Alti, prova 160 no per l'esame; conto 330. Riavvio
  con la fase 2 (ok del proprietario). Lunedì: confronto settimanale e allocatore (tieni G1). Prova in avanti del programma 5: M-001c non
  passa. Il funding più basso del demo è del conto demo (meno monete a 4 ore), confermato dagli incassi del demo stesso; nello stato
  c'è il confronto regolamento per regolamento (d5c6708). Commissione del demo 12-17 novembre 0,0273%, 34% del valore a commissione
  piena. Idea 146 (eventi di CoinMarketCap) in attesa del proprietario; scout del 17 senza idee forti.
- **Dashboard**: «Plancia» (aree Crypto e Azioni, menu a sinistra richiudibile); la scheda Azioni la riempie la sessione «trading
  stock». Aree del repository separate (`AREE.md`, blocco `.claude/hooks/aree.py`).

## Decisioni del proprietario di questi giorni
- 8 nov: nessuna strategia del paper o del demo si perde; lo 0,90 non è un muro. 9 nov: Sharpe corretto minimo 0,80; sotto i 500 USDT
  una strategia sola. 11 nov: la ricerca nuova non si ferma; aree separate; Sharpe corretto per famiglie di prove simili; la miscela
  F5 + M7 + K2 si misura a tavolino.

## Decisioni aperte per il proprietario
- Funding coperto (prova 157): rifarlo come prova nuova con una regola di margine scritta prima, o seguirlo solo a tavolino.
- Conto vero: `docs/conto_vero.md`, punti 1-5 (Firebase per primo).
- Confronto settimanale: le soglie di `gate2/THRESHOLDS.md` non vanno approvate così (due sono già superate solo per le monete che il
  demo di Binance non ha): prima decidere come trattare le monete mancanti.
- Allocatore: la miscela sopra i 500 USDT e la regola della sostituzione (`allocazione/REGOLE.md`).

## Prossimi passi
- **Trading AI sul demo suo** (decisione del 23 novembre): la sessione «trading AI» (session_01RPSK4kasjZfRQYXznD4TfF, riaperta)
  scrive il codice in `trader_ai/`; **a ogni giro leggere `trader_ai/RICHIESTE_CRYPTO.md`**: il collegamento sulla macchina (modulo nel
  bot o servizio, chiavi del secondo conto demo) lo scrive questa sessione, poi live-path-reviewer e l'ok del proprietario al primo avvio.
  La chiave del modello sulla macchina funziona (`ops/results/0770`, 23 novembre); il conto demo nuovo e le sue chiavi li crea il proprietario.
- **Ogni mattina dal 23 novembre, giro delle 04:17, anche i fatti gravi** (idea 158, il proprietario: «Scrivi la regola e procedi
  da domani»): `python3 -m research.notizie.fatti_gravi`, si leggono i titoli, si segnano i casi con direzione, forza, ore e perché
  PRIMA dei prezzi, si committa subito (regole `research/notizie/FATTI_GRAVI.md`). Misura dopo 40 casi.
- **Ogni mattina dal 22 novembre, giro delle 04:17** (voce 14 di G1, approvata dal proprietario il 21 novembre): appena arriva la
  risposta «stato», `python3 -m research.programma7.misure_g1.voce14_lettura`, poi si leggono le notizie delle monete vendute (archivio
  + al più una ricerca sul web per moneta con peso di almeno il 2%), si scrive il giudizio nel foglio `misure_g1/voce14_letture/` PRIMA
  di guardare i prezzi, e si committa subito (regole `misure_g1/VOCE14_REGOLE.md`). Misura dopo 20 mattine e 20 «sì».
- 21 novembre: la prova 163 (arbitraggio del funding fra Binance e Hyperliquid) non passa; le altre strade nuove (Polymarket contro
  le opzioni, le occasioni del conto piccolo) aspettano il via libera del proprietario.
- **21 novembre, decisione del proprietario**: niente più ricerca da manuale (`docs/decisioni_del_proprietario.md`); lo scout ha le
  istruzioni nuove (`.claude/agents/strategy-scout.md`). Area nuova `trader_ai/` con la sua sessione «trading AI» (creata il 21
  novembre, session_01RPSK4kasjZfRQYXznD4TfF): il modello linguistico che decide, prima a soldi finti simulati, mai sul demo di G1.
  Qui: le idee che un'intelligenza artificiale può fare (leggere notizie e posizioni dei conti grandi, regole cercate in automatico
  con dati nascosti), provate solo sui giorni dopo la data di addestramento del modello e in avanti.
- Da costruire nella ricerca: una funzione unica per l'esame (famiglie), un controllo dei dati a inizio giro (giorni a metà, candele
  mancanti, file vecchi), le voci rimaste del backlog P32.
- Idee passate a strategy-scout il 12 novembre: differenze di funding fra borse, base dei future trimestrali, dominanza del Bitcoin.
- Decisione aperta: la variante di G1 con il tetto del 20% per moneta (prova 152) al revisore e poi nel paper accanto a G1?
- Ogni mattina alle 04:17: log-bot e stato dalla macchina (prossime richieste 0762 e 0763), voce 8 del piano di G1.
- Ogni mattina alle 06:13: `SALTA_AVANTI2=1 bash research/programma5/avanti/aggiorna.sh <scratchpad>/impronte_avanti` e, finito quello,
  `PYTHONPATH=. python3 -W ignore research/programma5/avanti/avanti2.py` come comando a parte (insieme superano i 50 minuti);
  i commit mentre gira qualcosa in background si fanno senza `git stash` (add dei soli file, poi fetch e merge).
- Nel riepilogo di lunedì 23 dire al proprietario che la ricerca di idee nuove è quasi ferma: dal 17 al 20 novembre lo scout ha
  trovato una sola idea (prova 162, no); i freni di G1 sono già tutti provati; le idee nuove verranno dai dati raccolti in avanti
  (Hyperliquid, notizie, eventi di CoinMarketCap se il proprietario dice sì).
- Lunedì 23 novembre: riepilogo settimanale, gate2-reconciler (il funding si giudica contro il mercato vero, non contro il demo; la
  quota a commissione piena con 13 giorni a regime), portfolio-allocator.
- Il contesto di questa conversazione è molto lungo: conviene compattarla.
