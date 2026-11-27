# Stato della sessione (compito in corso, decisioni, prossimi passi)

Aggiornato a ogni tappa dalla sessione principale (regole dei token in `CLAUDE.md`). Corto: il resto sta nel diario
(`docs/andremo_live.md`) e nei piani.

## Compito in corso (27 novembre 2026, 13:30 UTC)
- **Audit del 26 novembre: correzioni finite e salvate.** Commit: stato e agente (`e824f22`, attivo, controllato sulla risposta 0779),
  esame in una funzione sola (`research/programma6/ESAME_NUMERI_2026-11-27.md`), bot/demo/monitor (`16c5712`, APPROVE al secondo giro,
  **entra con il riavvio: aspetta l'ok del proprietario**), motore della ricerca (funding vero, non monete, rilanci divisi; due verifiche).
  Rapporto rigenerato: `audits/reports/2026-11-26-AUDIT_SISTEMA.md`. Prima del riavvio: leggere `/commands/bot_state`, `kill_switch`,
  `/positions`, `/ordini_limite` (lo stato non li legge: backlog P36) e uno «stato» fresco; mai fra le 23:30 e le 01:00 UTC.
- Mattino del 27: programma 5 e paper del programma 6 salvati (il paper rifatto alle 11:18 dopo il limite di tempo dei comandi: per il
  calcolo del paper dare un limite lungo, 100 minuti). Giri delle 08:17 (fatto alle 11:20) e 12:17 fatti.
- Dal prossimo giro del mattino il paper delle candidate usa il motore nuovo: i numeri cambiano (C1 nel periodo P da −25,89% a −8,55%);
  controllare che il giro non cada e che PREDICTUSDT abbia il funding vero (645 monete da scaricare).

## Compito in corso (27 novembre 2026, 04:35 UTC)
- **Aggiornamento delle 04:35**: secondo giro dell'audit finito (i test di GitHub: 9 problemi, in tutto 61; rapporto rigenerato).
  Corretti e committati: `requirements-ricerca.txt`, `tests.yml` (due lavori, la corsa in corso finisce sempre), documento storico e
  quattro test saltati, CLAUDE.md; qui `research/src/tests` passa (3.142, 9 saltati). Revisione di F5 committata: **FAIL a 280-300 USDT,
  PASS tecnico a 1.000** (backlog P36). Giro delle 04:17 fatto (raccolta da una copia pulita in `<S>/wt_raccolta`, fogli, voce 8, diario).
  In corso: il flusso delle correzioni (wf_2957b2e1-ccc; finiti scarico, motore, notizie; poi balene, esame, registro, misure, segreti,
  stato, bot, verifiche e revisioni) e il flusso delle idee nuove «idee-nuove-27nov» (wf_3836c0f0-689: tre scout A, B, C con le bozze
  in `<S>/scout_27nov/`, controllo di novità, verifica, ritocco; le idee scartate stanno nel journal del flusso). Dopo: numeri 170 e
  seguenti alle bozze (nomi CENTOTTAVA, CENTONOVESIMA...), commit delle regole, righe del registro e LOG delle idee; i calcoli solo
  dopo il commit delle correzioni del motore. Alle 06:13: il paper del programma 6 usa `aggiorna.sh`, che è in correzione: decidere
  se lanciarlo dalla copia pulita o con le correzioni già controllate.

## Compito in corso, prima parte (27 novembre 2026, 02:40 UTC)
- **Audit del sistema** (richiesta del proprietario del 26 novembre): 52 problemi confermati, rapporto
  `audits/reports/2026-11-26-AUDIT_SISTEMA.md`, backlog P37. Corretti e committati: i fogli del mattino si fermano senza la raccolta
  fresca, VVV nei fatti gravi del 26 (terza correzione), scout e routine con la decisione del 22 novembre, P18 e P28.
  In corso il flusso «correzioni-audit-26nov» (wf_2957b2e1-ccc): scarico, motore (funding vero, azioni, rilanci, giorni a metà),
  notizie (prova in avanti del 30 novembre, ore in UTC, PAROLE), balene (mercato di Hyperliquid, conti con posizioni, giudice),
  esame (funzione unica e numeri accanto), registro, misure (idea 45); segreti e stato con live-path-reviewer (entrano senza riavvio);
  bot (finestra degli ordini limite del paper, monete non disponibili sul demo, allarmi, lettura oraria, ordine dei giri, vecchio
  sistema, Telegram) con live-path-reviewer: entra solo con il riavvio approvato dal proprietario; revisione di F5 (backtest-auditor).
  In corso anche il secondo giro dell'audit (completezza, wf_cece32c1-27d ripreso). Dopo: test completi, commit, rapporto con gli
  stati finali, righe dell'esame nel registro (162-169), risposta breve al proprietario con le due decisioni (esame e riavvio).
- **Da fare dopo le correzioni del motore**: `python3 -m research.programma6.buchi_archivio --dal 2020-01-01` (buchi del 2022, P37).
- **Giro delle 12:17**: rilanciare `bash research/programma6/paper/aggiorna.sh <S>/impronte_p6g` (l'archivio pubblica il giorno
  prima fra le 08:44 e le 11:03: alle 06:13 manca sempre).

## Compito precedente (17 novembre 2026, 12:30 UTC)
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
- **27 novembre, dall'audit**: ok al riavvio del bot (correzioni del demo, vecchio sistema fermo); le regole dell'esame (V
  simmetrica, t robusto, numeri accanto in `ESAME_NUMERI_2026-11-27.md`); la taglia del conto vero per F5 (FAIL a 280-300 USDT, PASS a
  1.000); avvisi in pochi minuti (servizio esterno); 219 e 220 del bot (429 lunghi e fermo al telefono).
- Funding coperto (prova 157): rifarlo come prova nuova con una regola di margine scritta prima, o seguirlo solo a tavolino.
- Conto vero: `docs/conto_vero.md`, punti 1-5 (Firebase per primo).
- Confronto settimanale: le soglie di `gate2/THRESHOLDS.md` non vanno approvate così (due sono già superate solo per le monete che il
  demo di Binance non ha): prima decidere come trattare le monete mancanti.
- Allocatore: la miscela sopra i 500 USDT e la regola della sostituzione (`allocazione/REGOLE.md`).

## Prossimi passi
- **Lunedì 30 novembre, Hyperliquid**: al giro delle 00:17 la prima scelta nuova della mappa (circa 4 minuti) e delle balene:
  controllare `candidati_letti` in `liquidazioni_conti_2026-11-30.json` (nella prova 1.228) ed `esclusi_conto_a_leva_zero` in
  `scelti_balene_2026-11-30.json`; nel commit della raccolta aggiungere il file nuovo `hyperliquid/mercato_AAAA-MM.jsonl.gz`. Al giro
  delle 04:17 `python3 -m research.trader_copiati.giudice_balene`, poi il giudizio in `giudice_balene/giudizi/2026-11-30.json` nel
  formato della nota del 27 novembre di `GIUDICE_BALENE.md`, commit e push subito.
- **Lunedì 30 novembre, prova in avanti delle notizie** (P31): dopo il conto a tavolino `python3 -m research.notizie.prova_avanti`, poi
  commit di `research/notizie/avanti/`; il 30 dice solo che non ci sono settimane finite, il primo numero (30 novembre - 6 dicembre)
  arriva il 7 dicembre e va nei numeri del lunedì al proprietario.
- **Conto vero su F5** (25 novembre): codice committato dopo l'APPROVE di live-path-reviewer per il commit (spento); prima
  dell'accensione la voce P36 del backlog (testi «G1» rimasti, peso massimo di F5, settimana saltata dopo un blocco, decisioni del proprietario).
- **Giudice delle balene** (idea 152, regole `research/trader_copiati/GIUDICE_BALENE.md` del 24 novembre): scrivere
  `research/trader_copiati/giudice_balene.py` (i numeri per conto della sezione del giudizio) **prima di lunedì 30 novembre**, primo
  giudizio quel lunedì, salvato prima della settimana dopo; misura dopo 8 settimane.
- **Ogni lunedì, F5 accanto a G1** (domanda del proprietario del 23 novembre: «perché F5 non è meglio di G1?»): nel riepilogo e
  nel confronto settimanale la settimana di F5 e di G1 sulle stesse letture dello stato (16-23 novembre: F5 −1,2%, G1 −6,0%); sul
  passato sono pari (300 settimane: F5 +55,4% l'anno, Sharpe 1,88; G1 +54,1%, 1,97). Se il proprietario sceglie F5 per il conto
  piccolo, il codice del conto vero va adattato (stesso motore, decisione il lunedì) e rivisto da live-path-reviewer.
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
