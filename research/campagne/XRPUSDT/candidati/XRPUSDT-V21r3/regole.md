# Candidato XRPUSDT-V21r3 — premio negativo del perpetuo, long a 1 ora

Famiglia XRPUSDT-V21 (idea I-11), terzo ritocco (ritocco di XRPUSDT-V21r1, a sua volta ritocco di
XRPUSDT-V21). Codice: `codice/varianti.py` (`_i11("long", 0.0020, 0.10)`, tenuta 4) eseguito con
`codice/quadro.py`. Regole congelate dalla registrazione nel log (voce XRPUSDT-V21r3).

## Regole

* **Moneta e timeframe**: XRPUSDT, candele da 1 ora del last price; mark price allineato con
  `carica_serie_allineate`.
* **Direzione**: long.
* **Ingresso**: alla chiusura della barra i, se
  1. premio = close del last[i] / close del mark[i] − 1 < −0,0020 (il perpetuo chiude oltre lo 0,20%
     sotto il mark price), e
  2. close[i] / close[i−1] − 1 ≥ −0,10 (la barra non è un crollo oltre il 10%),

  si compra all'apertura della barra i + 1.
* **Stop**: close[i] − min(1,5 × ATR(14) di Wilder a 1 ora, 6% di close[i]); scatta sul last.
* **Target**: nessuno.
* **Uscita**: a tempo, all'apertura della quinta barra dopo l'ingresso (tenuta 4 barre = 4 ore), se
  lo stop non è scattato prima.
* **Dimensione e leva**: regole del bot (rischio 1% del capitale per trade, quantità = capitale ×
  0,01 / |apertura − stop|, leva massima 2, riduzione al tetto di leva se serve, margine isolated).
* **Filtri**: nessun mese escluso (nessun mese sotto la liquidità minima).

## Motivo economico

He, Manela, Ross e von Wachter («Fundamentals of Perpetual Futures», 2022): il prezzo del perpetuo
si scosta dal prezzo a pronti e lo scostamento rientra. Il mark price di Binance segue l'indice a
pronti; un last molto sotto il mark vuol dire vendite aggressive concentrate sul perpetuo (chiusure
di posizioni lunghe con leva, liquidazioni) che spingono il perpetuo sotto il mercato a pronti. Il
rientro del premio e la fine della pressione di vendita fanno salire il last nelle ore dopo. Il
filtro sui crolli oltre il 10% esclude i casi in cui il premio negativo è parte di un crollo che
continua (notizia vera), che nella costruzione sono finiti tutti allo stop.

## Rischi noti (scritti prima delle verifiche)

* È il terzo ritocco della stessa famiglia: due soglie (crollo massimo 10%, premio 0,20%) scelte
  guardando i fallimenti sugli stessi dati di costruzione. Il rischio di adattamento al caso è alto;
  lo giudica la validazione.
* Il premio grande è frequente quando il volume era basso (primo semestre 2020): lì lo slippage
  vero era probabilmente più alto dello 0,02% simulato (`fase0_dati.md`).
* Il bot vede il mark price (`premiumIndex`) ma decide sulle candele: per eseguire la regola serve
  la chiusura oraria del mark price accanto a quella del last.
