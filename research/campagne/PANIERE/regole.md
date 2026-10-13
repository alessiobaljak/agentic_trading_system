# Campagna del paniere (seconda edizione del protocollo) — regole della sessione

Testo scritto dal coordinamento al Passo 0 della seconda edizione (`research/PROTOCOLLO_2.md`, approvata dal
proprietario il 13 ottobre 2026). In sola lettura per la sessione di campagna, come `monete.csv`, le `schede/` e
`via_libera_validazione.md` (guardiano, `_PROTETTI_FILE`).

## 1. Che cosa vale

* Il testo in vigore è `research/PROTOCOLLO_2.md` (versione 5.0), con tutto ciò che la sua sezione 0 tiene in
  vigore della 4.5 (`research/PROTOCOLLO.md`) e delle regole della campagna di gruppo
  (`research/campagne/GRUPPO/regole.md`). Dove i tre testi dicono cose diverse vale, nell'ordine: PROTOCOLLO_2,
  poi le regole del gruppo, poi la 4.5.
* La sessione lavora con il marcatore `{"tipo": "campagna", "simbolo": "PANIERE"}`, sul branch
  `research/campagna/PANIERE`, nella cartella `research/campagne/PANIERE/`. Il guardiano la tratta come la campagna
  di gruppo (sezione 12 delle regole del gruppo): dati in-sample delle sole 80 monete di `monete.csv` (e di BTCUSDT),
  la propria cartella, `research/src`, `research/config` in sola lettura.

## 2. Le monete, i dati, i periodi

* Le 80 monete sono quelle di `monete.csv` (identico, byte per byte, a quello del gruppo: stessa impronta approvata
  nel guardiano); le `schede/` dicono per ognuna il primo mese di dati e la fascia di scarto per lato, tutto vero al
  31 dicembre 2023.
* I dati sono le candele giornaliere (`klines/1d`, `markPriceKlines/1d`) e il funding, dal primo mese della scheda al
  2023-12-31, scaricati e verificati dal coordinamento (`impronte_1d.json`: 9.406 file, con il loro SHA-256). La
  sessione non scarica nulla: se un file manca, STOP e si chiede al coordinamento.
* Periodi (sezione 6 di PROTOCOLLO_2): costruzione fino al 2023-01-16 compreso, validazione dal 2023-01-17 al
  2023-12-31 (`dati.periodi_gruppo` sulle schede); il vault e il paper non sono di questa sessione.
* Il timeframe dei segnali è «1d» e basta.

## 3. Le idee e il budget

* Le tre idee, le 18 varianti e i ritocchi (3 per famiglia, 12 in tutto) sono quelli della sezione 5 di PROTOCOLLO_2:
  si registrano in `ipotesi.md` e nel log prima del primo test, con la previsione, e non si inventano idee nuove.
* Esecuzione: ingresso con ordine limite alla chiusura della candela di segnale, valido una candela, condizione
  «attraversato», maker 0,02%, scarto zero (`motore.Parametri`: `ingresso="limite"`,
  `limite_validita_barre=1`, `commissione_maker_per_lato=0.0002`); uscite a mercato con lo scarto della fascia della
  scheda; stop 2,5 ATR(20); uscita a tempo 60 barre; rischio 1%, leva 2, isolated. I numeri sono in
  `research/config/parametri_2.yaml` (approvato dal proprietario) e non si cambiano.

## 4. L'esame

* Lo esegue solo `research/src/gruppo.py` (`esame_di_gruppo`, `conta_trade_di_gruppo`, `controllo_positivo`) con
  `timeframe="1d"`, come per il gruppo: trade sommati, blocco, baseline (a) e (b) per moneta (semi 1000·j + s),
  strategie sfasate, «nettamente», candidato. I numeri dell'esame sono quelli del blocco `gruppo` di
  `research/config/parametri.yaml` (trade minimi 700 in costruzione, 300 in validazione; budget e ritocchi di
  PROTOCOLLO_2 prevalgono su quelli del blocco).
* Il modulo della variante segue il contratto della docstring di `gruppo.py`; la serie di paniere per le idee B e
  C (`research/src/paniere.py`) va calcolata nel modulo dalle candele che `gruppo.py` passa (BTCUSDT compreso),
  mai da file letti dal modulo.
* La prova a placebo a barre giornaliere (`research/taratura/placebo_paniere/`) e il controllo positivo devono essere
  passati PRIMA della prima variante: li fa il coordinamento e scrive l'esito qui sotto, sezione 6.

## 5. Log, consegna, cosa non si fa

* Log in `log.jsonl` (formato della sezione 6 della 4.5), solo in aggiunta. Consegna come nella sezione 8 delle
  regole del gruppo.
* Non si legge nulla delle campagne della prima edizione (nemmeno `campagne/GRUPPO/`, tranne i file che il
  guardiano ammette), né `research/confronto/`, `research/vault/`, `docs/`, il bot.
* Nessun dato oltre il 2023-12-31: il caricatore lo rifiuta (marcatore `vault/APERTURA_2.md`, che questa sessione
  non crea mai).

## 6. Esiti scritti dal coordinamento prima dell'apertura

_(da compilare al termine del Passo 0: prova a placebo a 1d, controllo positivo, impronte degli strumenti.)_
