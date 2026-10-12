# ADAUSDT — lezioni della moneta (idee provate e risultati)

Costruzione 2020-01-31 → 2022-10-18. «t» è il t contro la baseline casuale (b); «netta» vuol dire
oltre la soglia. Fonte di ogni numero: le voci `risultato` del log.

| idea | variante | regola in breve | trade | R medio | t (b) | esito |
|---|---|---|---|---|---|---|
| I-01 momento a una settimana | 001 long / 002 short | 4h, segno del rendimento a 7 giorni, tenuta 7 giorni | 123 / 109 | 0,102 / 0,052 | 0,28 / 0,62 | come il caso; il long è il trend del 2021 |
| I-02 rottura del canale | 003 long / 004 short | 4h, massimo/minimo di 20 barre, uscita a 10 | 85 / 72 | 0,140 / 0,045 | −0,12 / 0,54 | come il caso |
| I-03 prezzo e media 20 giorni | 005 | 1d | 46 | — | — | scarto per trade |
| I-04 inerzia dopo eccesso | 006/007 (k=1) scarti; 030 long / 031 short (k=0,5) | 1d, tenuta un giorno | 98 / 86 | 0,060 / −0,082 | 1,46 / −1,61 | non netta |
| I-05 prima mezz'ora → ultima | 008 long / 009 short | 30m | 486 / 440 | −0,120 / −0,044 | −1,67 / 2,20 | 009 netta ma R negativo (costi) |
| I-06 BTC guida ADA | 010 long / 011 short | 1h, ora forte di BTC, tenuta 3 ore | 534 / 400 | −0,007 / −0,087 | 1,86 / −1,38 | il ritardo esiste un po', non paga i costi |
| I-07 funding affollato | 012 short / 013 long | 8h, funding estremo, tenuta 24 ore | 95 / 99 | −0,085 / −0,006 | −1,09 / 0,01 | niente |
| I-08 compressione (Bollinger) | 014/015 (120 barre), 032/033 (60) | 4h | 15-30 | — | — | scarti per trade |
| I-09 RSI(2) in tendenza | 016 (1d) / 017 (4h) | — | 8 / 54 | — | — | scarti per trade |
| I-10 volumi alti | 018 (1d) scarto; 019 (4h) | 4h, volume sopra il 90° percentile, tenuta 5 giorni | 78 | 0,268 | 1,40 | R alto, ma compatibile col caso su 78 trade |
| I-11 numeri tondi | 020 long / 021 short | 1h, attraversamento, tenuta 12 ore | 394 / 386 | 0,032 / −0,113 | 1,27 / −1,26 | niente |
| I-12 residuo rispetto a BTC | 022 long / 023 short | 1h, s-score 24 ore | 87 / 161 | 0,226 / −0,200 | 1,92 / −1,80 | asimmetrico: il long recupera, lo short perde molto |
| I-13 intervallo d'apertura | 024 long / 025 short | 15m | 795 / 821 | −0,002 / 0,016 | 2,49 / 3,28 | batte le baseline per la distanza dello stop; 025 cade ai costi doppi |
| I-14 squilibrio degli ordini | 026 long / 027 short | 1h, taker 24 ore, tenuta 24 ore | 281 / 267 | −0,043 / −0,081 | −0,41 / −0,98 | niente |
| I-15 inversione come liquidità | 028 scarto; 029 short | 4h, rialzo di 24 ore oltre 2 deviazioni | 82 | −0,092 | −1,10 | niente |

**Ritocchi (dopo l'esaurimento delle idee):**
* Famiglia 024 (5 ritocchi): 034 con filtro della media a 20 giorni (R 0,075, cade ai costi doppi);
  035 con filtro di BTC in calo (R 0,077, cade ai costi doppi); 036 con uscita il giorno dopo (R
  −0,005); 037 con entrambi i filtri (R 0,252, supera la Fase 4, va in validazione); 038 con uscita alla
  rottura fallita (R −0,067).
* Famiglia 009 (3 ritocchi): 039 con stop di almeno l'1,76% (R 0,008, cade ai costi doppi); 040 con in
  più BTC in calo (R 0,057, cade ai costi doppi e col ritardo); 041 con uscita alle 00:30 (R 0,032, non
  netta).

**Cosa ho capito di ADA in costruzione:**
* Le regole di tendenza (I-01, I-02) vanno quanto un ingresso a caso nella stessa direzione: il rialzo
  del 2020-21 e il crollo del 2022 li spiega la direzione, non il segnale.
* Sui timeframe corti (15-30 minuti) il costo fisso di un giro (0,14%) decide tutto. Una variante può
  battere nettamente il caso solo perché sceglie stop più larghi del caso.
* Due asimmetrie da annotare, non provate: il residuo negativo di ADA rispetto a BTC si richiude (022,
  t 1,92), quello positivo continua (023, t −1,80); i volumi alti senza grande movimento precedono
  rialzi (019, R 0,27 su 78 trade).
* Il candidato 037 in validazione vive di 3 giornate.
