# Candidato ADAUSDT-037 — regole congelate (prima della validazione)

Congelate il 2026-10-09, dopo la Fase 5 e prima di eseguire la validazione. Codice:
`codice/varianti.py`, classe `AperturaDueFiltri` (eredita da `AperturaFiltro` e `Apertura`), con
`barre_intervallo=4, ultima_ora=20, giorni_media=20`, direzione long; strumenti in `codice/comune.py`.

## Regole

* **Moneta e timeframe:** ADAUSDT, candele last da 15 minuti; mark price per la liquidazione
  (`carica_serie_allineate`).
* **Direzione:** long.
* **Intervallo d'apertura:** massimo e minimo delle 4 barre 00:00, 00:15, 00:30, 00:45 UTC del giorno
  (solo se la prima barra del giorno è delle 00:00 e le 4 barre sono consecutive).
* **Ingresso:** alla chiusura di una barra che apre fra le 01:15 e le 19:45 UTC (il codice chiede che
  anche la barra precedente abbia l'intervallo già noto, quindi la barra delle 01:00 non può dare
  segnale), se
  * la chiusura è sopra il massimo dell'intervallo e la chiusura precedente era sotto o uguale;
  * la chiusura è sopra la media semplice delle ultime 1.920 chiusure (20 giorni);
  * il rendimento di BTCUSDT (last) dalle 96 barre prima alla barra di segnale è negativo;
  * la barra di segnale non apre in gennaio, marzo o aprile 2020 (filtro di liquidità della Fase 0).
  Si entra all'apertura della barra successiva.
* **Stop:** il minimo dell'intervallo d'apertura (stop medio in costruzione 3,1% dall'ingresso).
* **Target:** nessuno.
* **Uscita:** alla chiusura della barra delle 23:45 UTC (cioè all'apertura delle 00:00), se lo stop non è
  scattato prima.
* **Dimensione e leva:** regole del bot (`config/regole_dimensione.md`): rischio 1% del capitale per
  trade, quantità = capitale × 0,01 / |apertura − stop|, nozionale al massimo 2 volte il capitale (trade
  ridotti contati: 0 in costruzione), margine isolato, liquidazione sul mark con margine di mantenimento
  2,5%. Costi: commissione 0,05% e slippage 0,02% per lato, funding storico.

## Motivo economico (e il suo limite)

La fonte (Crabel, 1990) dice che la rottura dell'intervallo d'apertura prosegue nella giornata. I due
filtri sono nati dallo studio dei fallimenti della variante senza filtri (024) sui dati di costruzione:
rotture nella direzione della tendenza a 20 giorni, e rotture di ADA quando BTC scende (forza propria
della moneta). **Limite dichiarato (Fase 5, nota N034):** entrando a caso solo nelle barre in cui valgono
i due filtri, con lo stesso stop e la stessa uscita, l'R medio è già +0,11 e 037 (+0,25) non lo batte
nettamente (t 0,63). Il vantaggio misurato in costruzione viene in gran parte dallo stato del mercato
scelto dai filtri, non dalla rottura.

## Il bot

Il bot non esegue questa regola così com'è: servono una strategia in codice e l'abilitazione della
coppia senza il gate (Passo 0, `esecuzione_strategie_bot`); 15 minuti è un timeframe che il bot ha dal
vivo; lo stop (3,1% in media) è sotto il tetto del 6%; l'orizzonte (fino a ~23 ore, al massimo 92 barre
da 15 minuti) sta sotto le 96 barre del bot.
