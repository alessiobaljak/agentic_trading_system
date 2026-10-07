# Lezioni su BTCUSDT (idee provate e fallite, 2020-01-01 → 2022-10-19)

Tutto osservato in costruzione; nulla e' stato validato. Dettagli in `consegna.md` e `log.jsonl`.

* **Il periodo domina.** 2020 fa guadagnare qualunque long che tenga qualche giorno (rottura del
  canale +0,99 R medio, intervallo di apertura +0,57, momentum a 5 giorni +0,15); nel 2022 gli stessi
  long perdono. Un'idea long va giudicata contro l'entrata casuale long dello stesso periodo, non
  contro zero: V22 (momentum long) sembra neutro (R −0,005) ma e' al 14° percentile del caso, cioe'
  peggio di entrare a caso.
* **Timeframe corti: i costi vincono.** A 30 minuti l'ultima mezz'ora del giorno UTC perde in media
  per long e short (−0,12 e −0,07 R senza condizione): il movimento medio e' sotto i 12 punti base di
  andata e ritorno. A 1 ora la rottura della prima ora produce il 54-57% di stop.
* **Ritorno alla media a 4 ore: no, in nessuna forma.** RSI(2) nel trend (win rate 64-67% ma stop a
  −1 R che cancellano tutto) e bande di Bollinger (comprare sotto la banda bassa = comprare dentro i
  crolli, R −0,22, 0° percentile del caso).
* **Funding negativo estremo → 24 ore positive, ma non abbastanza.** Decile piu' basso: 122 trade,
  R 0,08, positivo ogni anno, 96° percentile, mai netto; dipende dai 5 trade migliori; sparisce a
  12 ore; perde quattro quinti con 8 ore di ritardo; cresce con l'estremita' della soglia (al 95°:
  R 0,18 ma 85 trade). Funding alto → short: perde (il funding alto accompagna i rialzi). Il funding
  incassato non conta (0,4% del risultato).
* **Calendario e volatilita': niente.** Lunedi' long R 0,02; bassa volatilita' R −0,003.
* **Troppo pochi segnali su 2,8 anni** per: rotture di canale short, momentum a 7 giorni, giorno
  anomalo, premio del volume, compressione delle bande, NR7. Con 100 trade minimi in costruzione le
  idee a 1 giorno con eventi rari non si possono giudicare su una moneta sola.
* **Stop in ATR giornaliero = 10-12% del prezzo:** fuori dal tetto del 6% del bot; le idee
  giornaliere qui testate non sarebbero comunque eseguibili dal bot cosi' come sono.
