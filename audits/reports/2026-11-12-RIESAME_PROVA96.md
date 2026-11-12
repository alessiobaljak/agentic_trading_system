# Riesame della prova 96 (G22, la deriva del Bitcoin dopo il comunicato della Fed) — 12 novembre 2026

Auditor: backtest-auditor. Riesame delle prove bocciate di poco (idea 137, `research/riesame/ELENCO.md`, riga 3). Script e numeri:
`audits/repro/prova96_2026-11-12.py` e `audits/repro/prova96_2026-11-12_esito_<parte>.json`; ora dei comunicati letta dalla Fed in
`audits/repro/prova96_comunicati_fed.txt`.

## Riepilogo e verdetto

**PASS tecnico sul calcolo: nessun errore che cambi il verdetto. Il «no» della prova 96 resta.**

* Il calcolo si riproduce identico, su due fonti di candele diverse: 46 riunioni, +0,608% a operazione, intervallo +0,03%; +1,20%,
  **p 0,0205**, vinte 65%, metà 2021-2023 +0,85% e 2024-2026 +0,34% (differenza massima con il file committato 1e-16).
* Elenco delle riunioni completo e con l'ora giusta: le 46 date coincidono con il calendario ufficiale della Fed e tutti i 46 comunicati
  sono usciti alle 14:00 di New York (12 d'inverno, 19:00 UTC; 34 d'estate, 18:00 UTC), letti uno per uno dalle pagine della Fed.
* L'esame calcolato è quello scritto: bootstrap delle 46 operazioni, p = quota delle medie ricampionate ≤ 0, lo stesso metodo delle
  altre prove del programma 7. Ogni altro modo ragionevole di calcolare la p dà fra 0,016 e 0,036: nessuno arriva a 0,01.
* Costi giusti (0,05% a mercato più 0,01% di scarto per lato sul Bitcoin, decisione del 7 novembre). Il funding, lasciato fuori come
  dichiarato dalle regole, sposta la media di −0,002 punti (p 0,0208).
* Per arrivare a p 0,01 la media dovrebbe salire di +0,09 punti (da 0,61% a 0,70%) a parità di dispersione: nessun errore trovato ha
  quell'ordine di grandezza; quelli trovati vanno tutti nella direzione opposta (abbassano il risultato).
* Nessun problema Bloccante né Alto. Tre problemi Medi (il controllo sui giorni a caso esagera la forza del risultato; entrata allo
  stesso istante del segnale; la strategia opera proprio nelle 2 ore dopo un evento macro che i limiti fissi del bot vietano) e cinque
  Bassi. PASS significa «calcolo tecnicamente credibile», non «da promuovere».

Raccomandazione: non rifare la prova sugli stessi 46 eventi con varianti (per esempio la tenuta di 8 ore, che darebbe p 0,0097: è una
scelta fatta dopo aver visto i numeri). Se l'idea si riguarda «quando le riunioni saranno di più», le regole vanno scritte prima, con il
numero di riunioni nuove, la stessa tenuta di 6 ore e la risposta sul limite delle 2 ore attorno agli eventi macro.

**Indipendenza.** Il brief era neutro, ma rimandava alla riga 3 di `research/riesame/ELENCO.md`, che contiene la colonna «perché vale un
riesame» con un giudizio («Probabilità bassa che un errore la salvi»); lo stesso elenco dice che quella colonna non va passata
all'auditor. L'ho letta: la segnalo e non l'ho usata. Nessun audit precedente della prova 96 (`audits/AUDIT_LOG.md`).

## Oggetto

| Voce | Valore |
|---|---|
| Strategia | G22: segno della candela oraria del perpetuo BTCUSDT che contiene il comunicato della Fed (14:00-15:00 di New York); entrata a mercato all'apertura delle 15:00, uscita all'apertura delle 21:00 di New York, nella direzione del segno |
| Regole | `research/programma7/TRENTAQUATTRESIMA.md`, commit `2a931b6` (25 ott 2026 07:52:38 UTC), mai modificate dopo |
| Codice e risultati | `research/programma7/trentaquattresima.py`, `RISULTATI_TRENTAQUATTRESIMA.md`, `risultati_trentaquattresima/` (esame.json, eventi_G22.csv), commit `a43efd0` (25 ott 2026 07:58:09 UTC), mai modificati dopo |
| Lettura delle candele | `research/programma6/esecuzione.py:34-49` (`ore_di`), alla data del calcolo nella versione prima della correzione `4561064` (25 ott 13:14) |
| Configurazione | 46 riunioni (2021-01-27 … 2026-09-16), tenuta 6 ore, costo 0,06% per lato, bootstrap 10.000 ricampionamenti seme 2026; controllo: giorni feriali senza riunione dal 2021 al 5 ott 2026, 2.000 estrazioni di 46 giorni, seme 2026 |
| Periodo e scala | 27 gennaio 2021 – 16 settembre 2026 (eventi), candele da 1 ora |
| Esame scritto | `TRENTAQUATTRESIMA.md:34-37`: media sopra zero con p ≤ 0,01 (bootstrap sulle 46 operazioni) e positiva nelle due metà; «contando le 26 prove a eventi la soglia è 0,00038» |
| Repository locale | `93e7717` (copia troncata: ordine dei commit verificato sul remoto con `gh api`) |

## Checklist A–F

### A. Dati

| Punto | Esito | Evidenza e comando |
|---|---|---|
| Buchi, duplicati, ordine, orari UTC, valori anomali | **OK** | File mensili da 1 ora dell'archivio pubblico di Binance, dicembre 2020 – ottobre 2026 (71 file, impronte verificate): 51.864 ore, 0 duplicati, 0 fuori ordine, 0 aperture non all'ora intera, 0 chiusure diverse da apertura + 59:59,999, **0 ore mancanti** (anche nei giorni mancanti dell'archivio giornaliero, 26-28 febbraio e 1-2 aprile 2022: catalogo, voce 1). Nelle finestre delle 46 riunioni (da 3 ore prima a 8 ore dopo): 0 valori mancanti, 0 candele incoerenti, salto massimo fra chiusura e apertura successiva 0,035%; l'ora più ampia è il 22 marzo 2023 (4,87%). Le ore ricostruite dai minuti dei 46 giorni coincidono con le candele orarie (differenza 0,0). Ore oltre l'8% nel periodo: 4, tutte nel 2021 e fuori dagli eventi. `PYTHONPATH=. python3 audits/repro/prova96_2026-11-12.py <cartella> dati` → `_esito_dati.json` |
| Fonte usata dalla prova (catalogo, voce 20) | **OK** | Il calcolo del 25 ottobre usava `ore_di` prima della correzione (per BTCUSDT solo le barre fatte dai minuti). Nessun evento perso (46 su 46) e i rendimenti coincidono con quelli rifatti sui file mensili a meno di 1e-16: la correzione non tocca questa prova. `... base` |
| Funding storico presente e allineato | **OK** | Funding dall'archivio (file mensili, impronte verificate): intervallo di 8 ore in tutti i 6.483 regolamenti del periodo; ogni operazione attraversa **esattamente un** regolamento, alle **00:00 UTC** (46 su 46), letto dai dati. Nessun giorno stimato. `... funding` |
| Periodi uguali a quelli scritti prima | **OK** (nota Bassa) | Le 46 date di `TRENTAQUATTRESIMA.md:18-22` sono uguali a `trentaquattresima.py:21-26` (confronto automatico) e al calendario della Fed (`federalreserve.gov/monetarypolicy/fomccalendars.htm`, 2021-2026: 8 riunioni l'anno, più il voto per notazione del 22 agosto 2025, escluso dalle regole). Nessuna riunione non programmata. La riunione del 28 ottobre 2026 è dopo la fine dei dati dichiarata e resta fuori. Controllo: parte dal 4 gennaio 2021 (`trentaquattresima.py:77`), quindi salta venerdì 1° gennaio 2021, e scarta il 23 febbraio 2024 (candela piatta): 1.454 giorni su 1.455 feriali. Nessun giorno oltre quelli dichiarati. |
| Ora del comunicato | **OK** | Pagine dei 46 comunicati (`federalreserve.gov/newsevents/pressreleases/monetaryAAAAMMGGa.htm`): tutti «For release at 2:00 p.m.», 12 EST e 34 EDT; `ora_utc` (`trentaquattresima.py:34-38`, `ZoneInfo("America/New_York")`) dà 19:00 UTC ai 12 invernali e 18:00 ai 34 estivi, 0 differenze. `audits/repro/prova96_comunicati_fed.txt`; `... base` (`ora_utc_contro_fed`) |

### B. Sguardo nel futuro e tempi

| Punto | Esito | Evidenza e comando |
|---|---|---|
| Segnale sulla chiusura di t, esecuzione dall'apertura di t+1 | **OK** (Medio, problema 2) | `trentaquattresima.py:41-50`: segno di `close - open` della candela h (14:00-15:00 di New York, etichetta = apertura: `esecuzione.py:46`, `quarta.py:40`), entrata `open` di h+1, uscita `open` di h+7. Prova del taglio: segno ricalcolato con le candele fino all'ora h compresa, 0 differenze su 46. L'entrata è però nello stesso istante della chiusura del segnale (catalogo, voce 14): con 1, 2, 5 minuti di ritardo media +0,58%, +0,58%, +0,57%, p 0,023, 0,023, 0,022; con 15 minuti +0,47%, p 0,042. `... entrata` |
| Indicatori senza dati futuri | **OK** | Nessun indicatore: solo il segno di una candela chiusa. |
| Più scale di tempo | **OK** (non si applica) | Solo candele da 1 ora; i minuti li uso io solo per i controlli. |
| Stop e obiettivo nella stessa candela | **OK** (non si applica) | Nessuno stop, nessun obiettivo. |
| Decisione su candele chiuse | **OK** | La candela del segnale è chiusa all'entrata. La strategia non è nel bot: niente da segnalare sulle candele aperte. |

### C. Esecuzione e costi

| Punto | Esito | Evidenza e comando |
|---|---|---|
| Commissioni coerenti con l'ordine | **OK** | Ordini a mercato in entrata e in uscita (`TRENTAQUATTRESIMA.md:24-27`); costo per lato `seconda.costi_moneta` = `TAKER` 0,05% + scarto 0,01% (`seconda.py:288-290`, `motore5.py:47-49`), 0,12% a operazione, come la decisione del 7 novembre. Lo 0,05% è la commissione a mercato standard di Binance per il primo livello: da verificare sul conto, come sempre. |
| Scarto di prezzo | **OK** | 0,01% per lato sul Bitcoin. Nessun ordine limite simulato (il controllo `oltre` non si applica). Con i costi dimezzati p 0,0128; senza costi p 0,0064 (solo per capire: i costi giusti sono quelli usati). `... sensibilita` |
| Funding con il segno giusto | **OK, dichiarato** (Basso, problema 4) | Le regole dicono «niente funding» (`TRENTAQUATTRESIMA.md:26-27`). Misurato: un regolamento a operazione alle 00:00 UTC, effetto medio −0,0024 punti (massimo 0,046 punti), con il funding p 0,0208. `... funding` |
| Leva, margine, liquidazione | **OK** | Leva 1 implicita (rendimento sul valore della posizione); operazione peggiore −2,87% in 6 ore: lontanissima da una liquidazione. |
| Passi, minimi, filtri veri | **NON VERIFICABILE** (Basso, problema 8) | Capitale non dichiarato. Filtri veri per BTCUSDT: passo 0,001, minimo 0,001, valore minimo 50 USDT (`bot/portafoglio/filtri_conto_vero.json:543-547`). Con 250-280 USDT l'arrotondamento a 0,001 BTC sposta la posizione di decine di punti percentuali. Non cambia un «no». |
| Dimensionamento e limiti fissi | **PROBLEMA** (Medio, problema 3) | Dimensionamento implicito: tutto il capitale a operazione, non composto (media semplice). `bot/risk/hard_limits.py:29`: `MACRO_FLAT_HOURS: float = 2.0  # flat obbligatorio 2h prima/dopo evento macro high-impact` (usato in `bot/risk/circuit_breakers.py:92-101`): la prova sta in posizione da 1 a 7 ore dopo il comunicato, cioè dentro la finestra vietata. Entrando alla prima ora permessa (16:00 di New York, tenuta 6 ore) media +0,20%, **p 0,18**. Anche `MAX_RISK_PER_TRADE` 3% (`hard_limits.py:18`) senza stop non è definito. `... entrata` (`tutto_spostato_di_1_ore`) |

### D. Misure

| Punto | Esito | Evidenza e comando |
|---|---|---|
| Annualizzazione su 365 | **OK** (non si applica alla prova) | La prova non annualizza. Le mie misure sotto usano 365 giorni (52 settimane per lo Sharpe corretto). |
| Misure riportate | **PROBLEMA** (Basso, problema 6) | La prova riporta numero, media, intervallo, p, vinte, metà, anni. Mancano e le ho calcolate (serie giornaliera dal 1° gennaio 2021 al 5 ottobre 2026, capitale intero, leva 1): rendimento composto +30,9% (+4,8% l'anno), Sharpe 0,81, Sortino 1,74, **discesa massima −7,7% dal 7 maggio 2025 al 16 settembre 2026, non recuperata al 5 ottobre 2026**, profit factor 2,22, esposizione 0,55% delle ore, media lorda +0,73% contro un costo di 0,12% a operazione, migliore +6,25%, peggiore −2,87%. `... misure` |
| Concentrazione | **PROBLEMA** (Basso, problema 6) | **Le 5 operazioni migliori fanno il 79% della somma**; i 3 mesi migliori (settembre, giugno e gennaio 2022) il 56%. Senza la migliore media +0,48%, p 0,042; senza le 3 migliori +0,28%. `... misure`, `... p` |
| Anni e climi | **OK** (riportati in parte) | Anni: 2021 −0,07%, 2022 +1,65%, 2023 +0,97%, 2024 +1,69%, 2025 −0,59%, 2026 −0,21% (3 anni negativi su 6: la regola di Alessio sugli anni non è l'esame di questa prova, ma non sarebbe rispettata). Climi (definizione mia, non della prova: rendimento del Bitcoin nei 30 giorni prima, oltre +10% rialzo, sotto −10% ribasso): laterale 21 operazioni +0,10%, rialzo 14 +0,87%, ribasso 11 +1,25%. Vendite 23 +0,76%, acquisti 23 +0,45%. |

### E. Eccesso di adattamento e conto delle prove

| Punto | Esito | Evidenza e comando |
|---|---|---|
| Varianti contate dal registro | **OK** | Una sola variante (`TRENTAQUATTRESIMA.md:27`, «Nessun'altra variante»); al momento conto 166, prove a eventi 26 (`TRENTAQUATTRESIMA.md:32`). Oggi: `python3 -m research.src.registro --riepilogo` → 152 prove, conto 312. |
| Correzione per il numero di prove | **OK** per l'esame scritto; Sharpe corretto per completezza | L'esame delle prove a eventi è la p (≤ 0,01; con le 26 prove a eventi 0,00038, `trentaquattresima.py:107-110`). Per completezza, Sharpe corretto della serie settimanale (`asticella.corretto_rivisto`, G22 aggiunta al mazzo): Sharpe 0,82, t 1,95, corretto 0,00 con N = 81 gruppi, 0,02 con l'aggiunta del 23 ottobre, 0,00 con N = conto (312). G22 non è nel mazzo di `asticella.serie_programma7` (`asticella.py:211-265`): Basso, problema 7. `... asticella` |
| Sensibilità ±10% e ±20% | **OK** (con avviso) | Tenuta 6 ± 10-20% → 5 e 7 ore: p 0,0109 e 0,0204, medie +0,60% e +0,60%, metà sempre positive: il risultato non crolla, ma nessuna passa. Per capire: 3 ore p 0,069, 4 ore 0,050, **8 ore 0,0097**, 9 ore 0,019, 12 ore 0,029. La p oscilla intorno alla soglia con la tenuta: è rumore, e la tenuta di 8 ore scelta adesso sarebbe una scelta fatta dopo. `... sensibilita` |
| Parametri liberi e numero di operazioni | **OK** (nota) | Uno o due parametri (tenuta; finestra di un'ora del segnale) su 46 operazioni. Le regole non fissano un minimo di operazioni; il dubbio scritto prima (`TRENTAQUATTRESIMA.md:13-15`) lo dice. |
| Validazione dentro il periodo | **OK** | Le regole chiedono le due metà, non le finestre che avanzano: tutte e due positive (+0,85%, +0,34%). |
| L'esame calcolato è quello scritto (la p) | **OK** | `trentaquattresima.py:53-57`: 10.000 ricampionamenti con reinserimento delle 46 operazioni, p = quota delle medie ≤ 0; uguale a `trentasettesima.py:95-99`, `quarantesima.py:52-60`, `programma7/seconda.py:78-84`. Le regole non fissano il numero di ricampionamenti. Variabilità e alternative (`... p`): 50 semi 0,016-0,022; 2.000 ricampionamenti 0,017; bootstrap centrato su zero 0,022; t a una coda 0,025 (t 2,01); segni mescolati 0,025; Wilcoxon 0,036; segno (30 vinte su 46) 0,027. Aumento della media che servirebbe per p 0,01: +0,09 punti. |

### F. Riproducibilità e parità

| Punto | Esito | Evidenza e comando |
|---|---|---|
| Rieseguendo si ottiene lo stesso risultato | **OK** | Funzioni della prova importate senza il `main` (che riscrive i risultati). Con `ore_di` locale e con i file mensili scaricati: 46 eventi, 0 segni diversi, 0 ore diverse, differenza massima 1e-16, p 0,0205, metà e anni identici; controllo 1.454 giorni, media −0,113%, quota 0,0 come nel file. `... base`, `... controllo` |
| Parità ricerca, paper, demo, bot | **OK** (non si applica) | G22 non è nel paper né nel demo. |

## Problemi

1. **Medio — Il controllo sui giorni a caso fa sembrare il risultato più forte di quanto è.** I 1.454 giorni senza riunione sono più
   calmi delle riunioni (dispersione per operazione 1,48% contro 2,05%), quindi le medie di 46 giorni a caso stanno strette intorno a
   −0,11% (99° percentile +0,41%, massimo +0,59%) e «nessuna delle 2.000 estrazioni arriva alla media delle riunioni». Con i giorni a
   caso riportati alla dispersione delle riunioni la quota è **0,95%**; il confronto diretto riunioni contro giorni (Welch, una coda) dà
   p 0,011. Il controllo è descrittivo per le regole (`TRENTAQUATTRESIMA.md:28-29,37`), ma il registro e i risultati lo citano come
   sostegno. Riprodurre: `... controllo`. Correzione suggerita alla sessione principale: nella riga 96 del registro, accanto a «nessuna
   delle 2.000 estrazioni», scrivere che i giorni senza riunione sono più calmi e che a pari dispersione la quota è circa 1%.
2. **Medio — Entrata nello stesso istante della chiusura del segnale** (catalogo, voce 14). Con 1-5 minuti di ritardo la media scende
   da +0,61% a +0,57-0,58% (p 0,022-0,023), con 15 minuti a +0,47% (p 0,042). Abbassa il risultato, non lo salva. Riprodurre:
   `... entrata`. Correzione suggerita: nelle prove a eventi orari, scrivere nelle regole un ritardo di almeno un minuto.
3. **Medio — La strategia opera dentro la finestra che i limiti fissi del bot vietano.** `bot/risk/hard_limits.py:29` impone di stare
   fuori dal mercato 2 ore prima e dopo un evento macro; la prova entra un'ora dopo il comunicato e il guadagno sta tutto nella prima
   ora (+0,41% firmata, `RISULTATI_TRENTAQUATTRESIMA.md`). Alla prima ora permessa: +0,20%, p 0,18. Non cambia il «no»; diventa
   decisivo se l'idea si riprende. Correzione suggerita: chi riscrive le regole di una prova su eventi macro dica prima se il limite
   vale per quella strategia (decisione di Alessio, sotto).
4. **Basso — Funding fuori dal conto per scelta dichiarata.** Effetto −0,0024 punti a operazione, p 0,0208. Riprodurre: `... funding`.
5. **Basso — Il controllo salta un giorno feriale** (venerdì 1° gennaio 2021, `trentaquattresima.py:77` parte dal 4 gennaio) e scarta
   il 23 febbraio 2024 (candela del segnale piatta, come prevede la regola). Nessun effetto sul verdetto.
6. **Basso — Misure non riportate**: discesa massima (−7,7%, aperta dal maggio 2025), concentrazione (5 operazioni = 79% della somma),
   Sharpe, Sortino, profit factor, esposizione, climi. Calcolate qui (`... misure`). Dicono che il guadagno viene da poche operazioni
   del 2022-2024 e che dal 2025 la regola perde.
7. **Basso — G22 non è nel mazzo dello Sharpe corretto** (`asticella.py:211-265`: le prove a eventi del programma 7 si fermano alla
   74; la 96 manca). Cambia di poco gli N delle altre prove. Correzione suggerita: aggiungere le prove a eventi dalla 75 in poi, con il
   portafoglio della prova 41 come le altre.
8. **Basso — Capitale e filtri non dichiarati** (passo 0,001 BTC, minimo 50 USDT): con un capitale piccolo la posizione arrotondata
   si allontana molto dal capitale intero. Non cambia un «no».

Nessun errore trovato porta la p sotto 0,01: tutti quelli misurati la alzano o la lasciano uguale.

## Problemi tornati da audit precedenti

Nessun audit precedente della prova 96. Errori del catalogo controllati: voce 20 (lettura oraria di prima del 25 ottobre) non tocca
la prova (46 eventi su 46, rendimenti identici); voce 14 (entrata all'istante della decisione) presente, misurata (problema 2); voce 24
(p che dipende dagli strati) non si applica (nessuno strato); voce 29 (soglia cambiata dopo) non presente: p ≤ 0,01 nelle regole e nel
brief; voce 16 (due modi di contare le prove) calcolati tutti e due.

## Segnalazioni per live-path-reviewer

* Il limite fisso `MACRO_FLAT_HOURS` (2 ore prima e dopo un evento macro, `bot/risk/hard_limits.py:29`) è definito nei limiti fissi e
  usato in `bot/risk/circuit_breakers.py:92-101`. Da verificare se il percorso degli ordini di oggi (paper e demo,
  `bot/portafoglio/`) lo applica: se no, il limite c'è sulla carta ma non nei fatti; se sì, ogni strategia futura sugli eventi macro
  andrebbe bloccata. Non ho guardato il codice del bot oltre questa riga.

## Decisioni per Alessio

1. **Il limite di 2 ore attorno agli eventi macro** vale anche per una strategia che opera proprio su quegli eventi? Oggi la prova
   viola il limite; alla prima ora permessa la deriva non c'è più (p 0,18).
2. **Quale soglia per le prove a eventi**: le regole della 96 scrivono p ≤ 0,01 e, contando le 26 prove a eventi, 0,00038; il codice
   chiama «valida» solo la seconda. Per il riesame vale 0,01 (brief): conviene fissare per iscritto quale delle due decide.
3. (Già aperta dall'11 novembre) **Minimo di eventi** per una prova a eventi: con 46 eventi e questa dispersione serve una media di
   circa 0,70% a operazione per arrivare a p 0,01.

## Domande aperte

1. Alla sessione principale: la riga 96 del registro va corretta sul controllo dei giorni a caso (problema 1)? Il testo «nessuna delle
   2.000 estrazioni arriva alla media delle riunioni» presenta come quasi certo un confronto che a pari dispersione dà circa 1%.
2. Alla sessione principale: chi aggiunge al mazzo dello Sharpe corretto (`asticella.serie_programma7`) la 96 e le altre prove a eventi
   dopo la 74 che mancano? Non ho controllato una per una quali manchino oltre alla 96.
3. Per il futuro dell'idea («da riguardare quando le riunioni saranno di più»): le regole della ripresa vanno scritte prima, sulle sole
   riunioni nuove (dalla riunione del 28 ottobre 2026 in poi), con la stessa tenuta di 6 ore e senza varianti scelte su questi 46
   eventi. Quante riunioni nuove servono, e con quale esame? Solo per informazione, senza peso: la riunione del 28 ottobre 2026, fuori
   dalla prova, avrebbe fatto −0,01%.
