# Candidato BTCUSDT-V10 — rottura di volatilità dall'apertura del giorno, long

Regole congelate l'8 ottobre 2026, prima della validazione. Da qui non cambiano più.
Codice: `codice/varianti.py`, funzione `v10()` (e `_i06`), con `codice/quadro.py`.

## Regole

| | |
|---|---|
| Moneta | BTCUSDT, perpetuo USDS-M |
| Timeframe | 1h (candele last price; giorno = giorno UTC) |
| Direzione | solo long |
| Ingresso | alla chiusura di una barra oraria, se il close supera l'apertura del giorno (open della barra delle 00:00 UTC) più 0,5 × il range (high − low) del giorno UTC precedente, calcolato sulle sue 24 barre orarie (servono tutte e 24, altrimenti nessun segnale). Solo la PRIMA chiusura oltre la soglia del giorno; nessun segnale sulla barra delle 23:00. Ingresso all'apertura della barra successiva |
| Stop | l'apertura del giorno (sotto l'ingresso per costruzione), sul last price |
| Target | nessuno |
| Uscita | «chiudi» alla chiusura della barra delle 23:00 UTC: si esce all'apertura del giorno dopo (00:00) |
| Dimensione e leva | regole del sistema (`config/parametri.yaml`): rischio 1% del capitale a trade, quantità = capitale × 0,01 / (apertura − stop), leva massima 2 (oltre, la quantità si riduce al tetto), margine isolato, mantenimento 2,5% |
| Costi nel test | commissione 0,05% per lato (taker), slippage 0,01% per lato (scheda), funding storico vero ai settlement |
| Filtri | nessuno (nessun mese escluso per liquidità) |

## Motivo economico

Larry Williams, «Long-Term Secrets to Short-Term Trading» (1999): quando il prezzo si
allontana dall'apertura di oltre mezzo range del giorno prima, nella giornata è arrivata
un'informazione o un flusso che tende a continuare fino a fine giornata (ordini spezzati,
chi insegue il movimento, stop degli short sopra i massimi). L'uscita a fine giornata
limita la tenuta al periodo in cui il flusso persiste.

## Numeri di costruzione (2020-01-01 → 2022-10-18), dal log

* 300 trade; R medio +0,149; profit factor 1,36; win rate 47,7%; durata media 10,5 ore;
  drawdown massimo 12,7%; rendimento totale +53,2% (2020 +47,0%, 2021 +1,2%, 2022 +2,9%).
* R medio per anno: 2020 +0,345; 2021 +0,015; 2022 +0,046. Senza i 3 trade migliori +0,082.
* Baseline (a) −0,832 (t 3,29, netta); baseline (b) −0,306 (t 2,35, netta); percentile fra le
  simulazioni casuali 96,5.
* Trade ridotti per il tetto di leva: 0. Violazioni della liquidazione: 0. Stop oltre il 6%
  (tetto `stop_massimo_bot`): 16 trade su 300.
* Fase 4: tutte le verifiche superate (log, BTCUSDT-V10-F01..F07 e nota BTCUSDT-V10-F).
* Fase 5, scettico (stop fisso al 2% per candidato e baseline): R +0,173 contro (b) −0,039,
  t 3,10, netta; R positivo in tutti e tre gli anni.

## Rischi noti

* Più di metà del rendimento di costruzione viene dal 2020; nel 2021 l'R medio è quasi zero.
* Le baseline con lo stop originale sono molto negative per la normalizzazione in R
  (stop vicino all'apertura per gli ingressi a caso): il confronto pulito è quello con lo
  stop fisso (Fase 5), dove il vantaggio resta ma è più piccolo in t.
* Il sistema chiude d'ufficio dopo 96 barre: qui la tenuta è al massimo 23 ore, nessun
  problema. Il sistema ha indicatori dal vivo su 1h: il timeframe è eseguibile. Serve però
  l'aggiunta «coppia del protocollo» (config/regole_dimensione.md, punto 4) e uno stop che
  può superare il 6% in circa il 5% dei trade.
