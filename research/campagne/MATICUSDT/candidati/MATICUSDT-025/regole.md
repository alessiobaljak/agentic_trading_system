# Candidato MATICUSDT-025 — regole

Variante V40 (registrazione `MATICUSDT-025` nel log), famiglia `MATICUSDT-018` (idea I-13,
squilibrio fra acquisti e vendite aggressivi), terzo ritocco della famiglia. Codice:
`codice/varianti.py` (`V40`, che usa `V38` e `_squilibrio`) e la stessa regola con parametri in
`codice/candidato_025.py` (identica con i predefiniti: verifica `MATICUSDT-V025-0`).

* **Moneta e serie.** MATICUSDT, perpetuo USDT di Binance. Segnali sul last price (candele 1h a
  barre chiuse); BTCUSDT last 1h solo come filtro di mercato.
* **Timeframe.** 1h. **Direzione.** Short.
* **Squilibrio.** Per ogni barra: q = (somma del volume taker buy delle ultime 6 barre, barra
  corrente compresa) / (somma del volume delle stesse 6 barre) − 0,5. Volumi in moneta base,
  colonne `taker_buy_volume` e `volume` dei file klines.
* **Ingresso.** Alla chiusura della barra i, se
  1. q[i] < media − 2 × deviazione standard (campionaria) di q sulle 720 barre precedenti
     (i−720 … i−1), e
  2. il rendimento di BTCUSDT nelle 24 barre prima (chiusura i / chiusura i−24 − 1) è ≤ 0,
  e non c'è una posizione aperta: short all'apertura della barra i+1.
* **Stop.** Sopra la chiusura della barra di segnale di min(2 × ATR(14) di Wilder su 1h, 6% della
  chiusura). Nessun target.
* **Uscita.** Dopo 12 barre in posizione (alla chiusura della dodicesima barra si chiude
  all'apertura della successiva), oppure allo stop.
* **Filtri.** Nessun ingresso su barre dei mesi sotto la liquidità minima (per MATICUSDT, fino a
  gennaio 2021: Fase 0).
* **Dimensione e leva (regole del bot).** Rischio 1% del capitale per trade; quantità = capitale ×
  0,01 / |apertura − stop|; nozionale al massimo 2 volte il capitale (tetto di leva 2); margine
  isolato; con stop fra 1% e 6% la leva effettiva resta sotto 1 (minimo 1x), la liquidazione è a
  circa il 97% di distanza: nessuna violazione del margine minimo.
* **Costi nel backtest.** Commissione taker 0,05% per lato, slippage 0,02% per lato (fascia del
  2023), funding storico ogni 8 ore.
* **Motivo economico.** Chi spezza un ordine grande di vendita in più ore lascia una traccia nel
  flusso aggressivo: uno squilibrio di vendite insolito nelle ultime 6 ore annuncia altre vendite
  nelle ore dopo (Chordia e Subrahmanyam 2004, sulle azioni: lo squilibrio di oggi predice il
  rendimento di domani). Il filtro su BTCUSDT tiene i casi in cui la vendita non va contro il
  mercato (nato dallo studio dei fallimenti, nota `MATICUSDT-N012`).
* **Rischi noti.** È il terzo di cinque ritocchi della famiglia; batte la (b) con un margine
  sottile (t 2,12 contro soglia 2,06); il guadagno è più alto nel ribasso del 2022.
