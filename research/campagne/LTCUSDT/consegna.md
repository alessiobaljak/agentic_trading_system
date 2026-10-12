# LTCUSDT — Consegna della campagna (protocollo 4.5)

**Nessuna strategia valida trovata per questa moneta.**

Il budget di 30 varianti è stato usato per intero (25 varianti di 13 idee nuove con fonte, 5
ritocchi), più 6 scarti sotto i 70 trade che non consumano budget. Nessuna variante ha battuto
nettamente sia la baseline (a) sia la (b) con R medio dopo i costi positivo: zero candidati, quindi
niente Fase 4, niente validazione, asticella con m = 0 (esito provvisorio, lo conferma il
coordinamento al Passo 4). Il periodo di validazione (2022-10-19 → 2023-12-31) non è stato toccato.

Ogni numero viene dal log (`log.jsonl`, voci `risultato`) e da `codice/misure.py`, che lo rilegge.

## Riepilogo delle idee provate (periodo di costruzione 2020-01-01 → 2022-10-18)

| Idea | Fonte | Variante | Trade | PF | R medio | t (a) | t (b) | Percentile |
|---|---|---|---|---|---|---|---|---|
| I-01 momentum settimanale | Liu e Tsyvinski 2018 | 001 1d long | 118 | 1,08 | +0,069 | 0,69 | 0,39 | 66 |
| | | 002 1d short | 121 | 0,72 | −0,165 | −0,50 | −0,76 | 22 |
| I-02 breakout di canale | Faith 2007 | 003 4h long | 85 | 1,21 | +0,171 | 0,70 | 1,07 | 94 |
| | | 004 4h short | 89 | 0,78 | −0,123 | −0,28 | 0,07 | 50 |
| I-03 RSI a 2 periodi | Connors e Alvarez 2008 | 005 4h long | 149 | 1,01 | +0,004 | 0,89 | 0,66 | 78 |
| | | 006 4h short | 150 | 1,08 | +0,016 | 1,23 | 1,34 | 87,5 |
| I-04 inversione dopo shock con volume | Campbell, Grossman, Wang 1993 | 007 1h long | 233 | 0,95 | −0,021 | 0,39 | 0,33 | 66 |
| | | 008 1h short | 210 | 0,65 | −0,165 | −1,29 | −1,46 | 4 |
| I-05 funding affollato | Schmeling, Schrimpf, Todorov 2023 | 009 8h short | 102 | 0,86 | −0,081 | 0,12 | −0,02 | 50 |
| | | 010 8h long | 79 | 0,88 | −0,052 | 0,14 | −0,21 | 41,5 |
| I-06 numeri tondi | Osler 2003 | 011 1h long | 921 | 0,80 | −0,067 | −0,77 | −0,61 | 24,5 |
| | | 012 1h short | 882 | 0,91 | −0,023 | 1,42 | 1,15 | 93 |
| I-07 range d'apertura | Crabel 1990 | 013 1h long | 568 | 0,95 | −0,018 | 2,04 | 1,73 | 92,5 |
| | | 014 1h short | 554 | 0,83 | −0,068 | 2,84 | 1,95 | 94,5 |
| I-08 lunedì | Caporale e Plastun 2019 | 015 1d long | 143 | 0,91 | −0,031 | −0,57 | −0,04 | 48 |
| I-09 squeeze | Bollinger 2001 | 016c 2h long | 138 | 0,69 | −0,201 | 2,30 | 1,36 | 90,5 |
| | | 017c 2h short | 134 | 0,85 | −0,081 | 1,02 | 1,25 | 88 |
| I-10 inerzia dopo giorno anomalo | Caporale e Plastun 2019 | 018b 1d long | 119 | 0,77 | −0,083 | −1,19 | −0,65 | 25,5 |
| | | 019b 1d short | 118 | 0,71 | −0,119 | −0,92 | −1,01 | 11 |
| I-11 continuazione con volume | Llorente e altri 2002 | 020 1h long | 179 | 1,20 | +0,102 | 1,61 | 1,58 | 97,5 |
| | | 021 1h short | 197 | 0,84 | −0,060 | 0,00 | −0,10 | 46 |
| I-12 premio sul mark | He, Manela, Ross, von Wachter 2022 | 022 1h short | 175 | 1,04 | +0,011 | 1,29 | 1,32 | 88 |
| | | 023 1h long | 153 | 0,91 | −0,027 | 0,34 | 0,39 | 68,5 |
| I-13 incrocio con la media | Brock e altri 1992; Hudson e Urquhart 2021 | 024 4h long | 136 | 0,88 | −0,046 | 0,23 | −0,23 | 40 |
| | | 025 4h short | 149 | 0,92 | −0,031 | 0,47 | 0,35 | 62,5 |
| Ritocchi della 014 | Crabel 1990 | 026 range stretto | 314 | 0,83 | −0,075 | 2,15 | 1,13 | 90,5 |
| | | 027 stop fisso 3% | 554 | 0,82 | −0,078 | 0,44 | 0,01 | 52 |
| | | 028 ingresso 04-07 UTC | 255 | 0,93 | −0,026 | 2,20 | 1,38 | 94 |
| | | 029 stop almeno 2% | 554 | 0,80 | −0,077 | 0,80 | 1,44 | 95 |
| | | 030 uscita il giorno dopo | 441 | 0,75 | −0,147 | 1,84 | 1,45 | 93 |

Nette contro la (a) (ma non contro la (b), e con R medio negativo): 013, 014, 016c, 026, 028. Nette
contro la (b): nessuna. Nessuna violazione della distanza dalla liquidazione, nessun trade ridotto per
il tetto di leva in nessuna variante.

## Cosa ho capito (con il numero e la fonte)

1. **Su LTC nel 2020-2022 il trend di fondo dell'anno spiega quasi tutto.** Quasi ogni variante long
   vince nel 2020-21 e perde nel 2022, e ogni short il contrario (R medio per anno nel log). La (b), che
   entra a caso nella stessa direzione, fa lo stesso: nessuna regola aggiunge una direzione propria.
2. **Il vantaggio apparente dei breakout con lo stop sul livello è un effetto dello stop, non della
   direzione.** La 014 batte la (b) con t 1,95; la stessa regola con lo stop fisso al 3% (027) scende a
   t 0,01, e la (b) passa da −0,24 a −0,08 R. Le 8 varianti con lo stop ancorato a un livello hanno t
   fra 1,13 e 1,95; le altre 22 hanno t medio 0,16 (nota LTCUSDT-N016).
3. **Il funding pesa sui long tenuti a lungo nel 2020-21**: 0,08 R a trade nella 001 e 0,13 R nella 003,
   più dei costi di commissione e slippage (0,023-0,030 R).
4. **I movimenti orari estremi con volume alto su LTC continuano nelle fasi di rialzo** (008: short
   dopo i balzi, R −0,165 contro −0,051 della (b)); l'idea di continuazione nata da qui (020) è positiva
   ma non netta (t 1,58) ed è stata scelta dopo aver visto il dato.

## Misure di processo

Fonte: `codice/misure.py` sul log. Il campo `data` di ogni voce viene dall'orologio della macchina
(UTC) al momento della scrittura.

* Durata dalla prima all'ultima voce del log: dal 2026-10-09 13:26:19 al 2026-10-09 13:58 UTC circa
  (32 minuti fino alla voce del risultato della 030), senza pause registrate: la durata con e senza le
  pause è la stessa. A questi minuti si aggiunge la Fase 0 e la scrittura di `ipotesi.md`, fatte in
  mezzo e registrate solo nei commit. La sessione è stata una sola.
* Minuti per idea, dalla registrazione della prima variante all'ultimo risultato: I-01 0,3; I-02 0,4;
  I-03 0,4; I-04 0,8; I-05 0,3; I-06 1,0; I-07 13,7 (con i 5 ritocchi); I-08 0,1; I-09 0,5; I-10 0,3;
  I-11 0,8; I-12 0,8; I-13 0,4. Sono i tempi di calcolo del motore: il lavoro su ogni idea (fonte,
  spiegazioni, varianti) sta prima della registrazione, in `ipotesi.md`.
* Spiegazioni concorrenti scritte in `ipotesi.md` per idea: 13 per ogni idea (10 comuni più 3
  specifiche), 12 per la I-08.
* Varianti diventate candidati in Fase 2: 0 da idee nuove, 0 da ritocchi.
* Varianti che hanno battuto nettamente la (a) e la (b) con R medio dopo i costi non positivo: 0.
* Varianti: 30 testate (25 idee nuove, 5 ritocchi), 25 famiglie, 13 idee; 6 scarti; previsioni
  dichiarate corrette 22 su 30.
* Rifiuti del guardiano: 5 (note N002, N003, N004, N005, N009), tutti per la forma dei comandi; nessun
  percorso vietato letto.

## Consegna per il coordinamento

* Candidati: nessuno. Criterio del vault, trade in paper attesi, eseguibilità nel bot: non si applicano.
* p-value di validazione ed esito dell'asticella: nessun candidato in validazione (m = 0); esito
  provvisorio, da confermare al Passo 4.
* Previsione per il vault e il trasferimento: nessuna (nessun candidato).
* Correzioni a `src/`: nessuna; nessun errore trovato nel motore o nei dati.
* Limiti: lo slippage della fascia del 2023 è probabilmente ottimista per il 2020 (volume 112 milioni
  di USDT al giorno contro 382 del 2023; `fase0_dati.md`); la prima barra vera è del 2020-01-09; la
  I-11 è stata scelta dopo aver visto i fallimenti della 007 e della 008.
