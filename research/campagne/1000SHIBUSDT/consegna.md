# Consegna — campagna 1000SHIBUSDT

Protocollo versione 4.5. Sessione di campagna del 9 ottobre 2026, branch
`research/campagna/1000SHIBUSDT`. Log: `log.jsonl`; idee: `ipotesi.md`; dati: `fase0_dati.md`.

## Esito

**Nessuna strategia valida trovata per questa moneta.**

Il budget di 30 varianti è stato usato per intero (27 varianti da idee nuove, 3 ritocchi),
più 10 varianti scartate perché sotto i 70 trade in costruzione (8 di idee nuove, 2 ritocchi;
non consumano budget). Due varianti sono diventate candidati in Fase 2, entrambe ritocchi
della stessa famiglia (I-08 b, momento interno al giorno lato short), ed entrambe sono state
**scartate in Fase 4 perché a costi doppi il loro R medio diventa negativo**. Nessun
candidato è arrivato alla validazione: il periodo di validazione (2023-03-14 → 2023-12-31) non
è stato usato, e l'asticella non ha candidati (m = 0, nessun p-value).

Cosa si è osservato (fatti, dai dati di costruzione 2021-05-10 → 2023-03-13):

* nessuna delle 16 idee con fonte, in 12 meccanismi diversi, batte nettamente le due baseline
  con un R medio positivo nella sua forma registrata;
* le varianti con R medio alto (I-01 a 0,22; I-03 c 0,55; I-05 b 0,47; I-12 a 0,08) lo devono
  alla mania del 2021 e a pochi trade: senza i 3 migliori l'R medio diventa negativo in tutte;
  la (b), che entra a caso con la stessa uscita, spiega gran parte del resto;
* il segnale più vicino a un vantaggio è il momento dell'ultima mezz'ora del giorno UTC dopo una
  prima mezz'ora in calo (Gao e altri 2018): batte il caso dopo 5 ritocchi, regge su 15 minuti e
  1 ora e non compare a mezzogiorno, ma il suo lordo (circa 0,08 R, cioè 0,1-0,15% di prezzo a
  trade) non copre due giri di costi.

## Candidati (entrambi scartati in Fase 4)

Regole complete in `candidati/1000SHIBUSDT-028/regole.md` e `candidati/1000SHIBUSDT-030/regole.md`.

| | 028 (ritocco 1 di I-08 b) | 030 (ritocco 5 della famiglia I-08 b) |
|---|---|---|
| Regola | short alle 23:30 UTC per mezz'ora se la prima mezz'ora del giorno è ≤ −0,9% | short alle 23:30 UTC per mezz'ora se la prima mezz'ora è ≤ −0,5% e il giorno fino alle 23:30 è negativo |
| Timeframe, stop | 30 minuti, stop 2 ATR (al massimo 6%), nessun target | uguale |
| Trade in costruzione | 111 | 96 |
| R medio dopo i costi | +0,005 | +0,027 |
| Profit factor | 1,04 | 1,23 |
| Drawdown massimo | −2,0% | −2,2% |
| R medio per anno | 2021 −0,002 (67); 2022 +0,037 (39); 2023 −0,158 (5) | 2021 +0,038 (52); 2022 −0,021 (35); 2023 +0,153 (9) |
| Senza i 3 trade migliori | −0,015 | −0,037 |
| Contro la (a) | −0,068: t 2,20, netta (soglia 2,02) | −0,068: t 2,13, netta (soglia 2,05) |
| Contro la (b) | −0,069: t 2,08, netta | −0,068: t 2,15, netta |
| Percentile fra le simulazioni | 99,0 | 100,0 |
| Costi doppi | **R −0,045: fallita** (t contro la (b) a costi doppi 2,56) | **R −0,028: fallita** (t 2,48) |
| Ritardo di una barra | t 1,09 (≥ 1,04): superata | t 1,081 (≥ 1,075): superata al limite |
| Robustezza | 4 casi netti su 7: superata | 5 su 7: superata |
| Timeframe adiacenti | 15m t 2,17; 1h t 1,53: superata | 15m t 2,12; 1h t 2,22: superata |
| Stabilità, trade estremi | superate | superate |
| Liquidazione | 0 violazioni, 0 trade ridotti per il tetto di leva | uguale |
| Regola intra-barra opposta | nessuna differenza | nessuna differenza |

Rendimento in percentuale sul capitale iniziale, costruzione: 028 +0,5% in totale; 030 +2,6%.
Buy and hold per anno della costruzione (contesto, sezione 8): 2021 (da maggio) long +22%, short
−23%; 2022 long −76%, short +76%; 2023 (fino al 13 marzo) long +36%, short −37%.

**Perché i costi doppi bastano a scartarli, e cosa dice il fatto che il distacco dalla (b)
cresca con i costi.** La (b) entra a qualunque ora con lo stesso stop in ATR; i candidati
entrano solo nei giorni volatili, dove l'ATR è più largo e quindi il costo di un giro pesa meno
in R. Una parte del vantaggio sulla (b) è questo effetto costi, non la direzione: a costi doppi
il `t` contro la (b) sale (2,08 → 2,56; 2,15 → 2,48) mentre l'R medio diventa negativo.

**Rischi noti, se qualcuno volesse riprenderli.** Cinque ritocchi della stessa famiglia su dati
già visti; margine dopo i costi di qualche centesimo di R; posizioni di mezz'ora, che il bot
dal vivo non sa gestire (indicatori solo a 1m, 5m, 15m, 1h: `config/regole_dimensione.md`);
trade al mese in paper: circa 5 (111 trade in 22 mesi), quindi circa 10 mesi per 50 trade.

## Varianti, budget, asticella

* Varianti testate: 30 su 30. Ritocchi testati: 3 (028, 029, 030), tutti nella famiglia 008.
  Famiglie testate: 27. Scarti sotto i 70 trade: 10 (S01-S10), di cui 2 ritocchi della 008.
* Candidati in Fase 2: 2, entrambi da ritocchi (0 da idee nuove). Varianti che battono
  nettamente la (a) e la (b) con R medio dopo i costi non positivo: 1 (029, R −0,003).
* Asticella (Benjamini-Hochberg al 10%): nessun candidato in validazione, m = 0; nessun
  p-value. Esito provvisorio (lo conferma il coordinamento al Passo 4): nessun candidato passa.
* `criterio_vault`: non si applica (nessun candidato).

## Tutte le varianti testate (costruzione)

| N | id | variante | tf | dir. | trade | R medio | senza 3 migliori | t (a) | t (b) | percentile | esito |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 001 | I-01 a | 4h | long | 171 | 0,221 | -0,126 | 0,69 | 0,67 | 88,0 | non netta |
| 2 | 002 | I-01 b | 4h | short | 201 | 0,018 | -0,070 | 0,28 | -0,05 | 48,0 | non netta |
| 3 | 003 | I-02 a | 1h | long | 123 | -0,143 | -0,211 | -1,29 | -1,41 | 6,5 | non netta |
| 4 | 004 | I-02 b | 1h | short | 192 | -0,194 | -0,227 | -2,20 | -2,33 | 0,0 | non netta |
| 5 | 005 | I-04 b | 4h | long | 177 | -0,128 | -0,275 | -0,65 | -1,16 | 13,5 | non netta |
| 6 | 006 | I-07 a | 1d | long | 93 | 0,002 | -0,170 | 0,02 | 0,01 | 52,5 | non netta |
| 7 | 007 | I-08 a | 30m | long | 352 | -0,061 | -0,068 | 0,56 | 0,58 | 70,0 | non netta |
| 8 | 008 | I-08 b | 30m | short | 316 | -0,026 | -0,049 | 1,99 | 1,92 | 98,0 | non netta |
| 9 | 009 | I-09 a | 1h | long | 229 | -0,004 | -0,040 | 1,12 | 1,04 | 86,0 | non netta |
| 10 | 010 | I-09 b | 1h | short | 152 | 0,023 | -0,015 | 1,22 | 1,25 | 95,0 | non netta |
| 11 | 011 | I-11 a | 4h | long | 76 | 0,012 | -0,066 | 0,59 | 0,64 | 78,0 | non netta |
| 12 | 012 | I-11 b | 4h | short | 105 | -0,053 | -0,090 | -0,01 | -0,31 | 34,5 | non netta |
| 13 | 013 | I-12 a | 1h | long | 170 | 0,083 | -0,094 | 0,53 | 0,53 | 89,5 | non netta |
| 14 | 014 | I-12 b | 1h | short | 179 | 0,020 | -0,030 | 0,77 | 0,22 | 61,0 | non netta |
| 15 | 015 | I-03 c | 2h | long | 102 | 0,547 | -0,277 | 0,76 | 0,36 | 70,5 | non netta |
| 16 | 016 | I-03 d | 2h | short | 111 | -0,083 | -0,226 | -0,31 | -0,52 | 26,0 | non netta |
| 17 | 017 | I-04 c | 4h | short | 74 | -0,003 | -0,238 | 0,07 | -0,13 | 45,5 | non netta |
| 18 | 018 | I-05 b | 4h | long | 85 | 0,470 | -0,114 | 0,97 | 0,97 | 91,5 | non netta |
| 19 | 019 | I-06 b | 15m | short | 109 | -0,174 | -0,249 | -0,98 | -0,91 | 18,5 | non netta |
| 20 | 020 | I-10 d | 1h | short | 78 | 0,214 | -0,017 | 1,52 | 1,27 | 99,5 | non netta |
| 21 | 021 | I-13 a | 4h | long | 80 | 0,232 | -0,066 | 0,97 | 1,07 | 98,5 | non netta |
| 22 | 022 | I-13 b | 4h | short | 83 | -0,219 | -0,324 | -1,57 | -2,25 | 1,0 | non netta |
| 23 | 023 | I-14 a | 4h | long | 96 | 0,003 | -0,202 | 0,16 | 0,11 | 54,5 | non netta |
| 24 | 024 | I-14 b | 4h | short | 99 | -0,060 | -0,156 | -0,34 | -0,37 | 37,0 | non netta |
| 25 | 025 | I-15 a | 1h | long | 1129 | -0,020 | -0,040 | 1,04 | 1,04 | 93,5 | non netta |
| 26 | 026 | I-15 b | 1h | short | 1177 | -0,024 | -0,035 | 0,20 | 0,10 | 53,0 | non netta |
| 27 | 027 | I-16 a | 4h | short | 173 | -0,026 | -0,091 | 0,15 | -0,11 | 43,5 | non netta |
| 28 | 028 | ritocco 1 di I-08 b | 30m | short | 111 | 0,005 | -0,015 | 2,20 | 2,08 | 99,0 | candidato, scartato in Fase 4 (costi doppi) |
| 29 | 029 | ritocco 4 di I-08 b | 30m | short | 171 | -0,003 | -0,045 | 2,06 | 2,06 | 99,0 | netta ma R non positivo |
| 30 | 030 | ritocco 5 di I-08 b (ritocco della 029) | 30m | short | 96 | 0,027 | -0,037 | 2,13 | 2,15 | 100,0 | candidato, scartato in Fase 4 (costi doppi) |

Idee: I-01 momento della serie (Moskowitz, Ooi, Pedersen 2012; Liu, Tsyvinski 2018); I-02
inversione a breve (Jegadeesh 1990; Lehmann 1990); I-03 rottura del canale (Faith 2007); I-04
affollamento dal funding (Schmeling, Schrimpf, Todorov 2023); I-05 volume alto (Gervais, Kaniel,
Mingelgrin 2001); I-06 gonfia e sgonfia (Kamps, Kleinberg 2018; Li, Shin, Wang 2018); I-07
lunedì (Caporale, Plastun 2019); I-08 momento interno al giorno (Gao, Han, Li, Zhou 2018; Shen,
Urquhart, Wang 2022); I-09 BTC guida (Lo, MacKinlay 1990; Ciaian e altri 2018); I-10
compressione delle bande (Bollinger 2001); I-11 RSI a 2 in tendenza (Connors, Alvarez 2008);
I-12 squilibrio degli aggressori (Chordia, Subrahmanyam 2004); I-13 momento dopo rendimenti
anomali (Caporale, Plastun 2020); I-14 incrocio con la media (Brock, Lakonishok, LeBaron 1992);
I-15 numeri tondi (Osler 2003); I-16 effetto lotteria (Bali, Cakici, Whitelaw 2011).
Scartate per pochi trade senza una variante testata: nessuna idea; I-03 a/b, I-04 a, I-05 a,
I-06 a, I-10 a/b/c sono scarti, sostituiti da varianti allentate scritte prima di vedere
risultati.

## Previsione per il vault e il trasferimento

Non ci sono candidati: nulla va al vault né al trasferimento da questa moneta. Se il
coordinamento volesse comunque sapere che cosa ci si aspetta dal segnale più vicino (famiglia
I-08 b): R medio dopo i costi vicino a zero o negativo, come in costruzione a costi doppi.

## Misure di processo

Ricavate dal log con `codice/misure.py` e da `ipotesi.md`. Orari dall'orologio della macchina.

* Durata dalla prima all'ultima voce del log: dal 2026-10-09 16:25:50 UTC al 2026-10-09
  17:08:36 UTC, 42,8 minuti, con e senza pause (nessuna voce `pausa_da`). Prima della prima voce: circa 15 minuti di lettura del protocollo e
  degli strumenti; durante la campagna lo scarico dei dati (circa 20 minuti) è andato in
  parallelo con la scrittura delle idee e del codice.
* Minuti per idea, dalla registrazione della prima variante all'ultimo risultato: I-01 0,9;
  I-02 0,9; I-03 1,7; I-04 6,3; I-05 1,7; I-06 1,7; I-07 0,9; I-08 18,0 (con i 3 ritocchi e le
  verifiche); I-09 1,1; I-10 1,7; I-11 1,1; I-12 1,1; I-13 1,7; I-14 1,7; I-15 0,8; I-16 0,8.
  Sono brevi perché le varianti di ogni lotto sono state registrate insieme e testate in serie
  subito dopo; il lavoro di Fase 1 (fonti, spiegazioni, varianti) sta prima, in `ipotesi.md`.
* Spiegazioni concorrenti scritte in `ipotesi.md` (Fase 1, punto 4): I-01 11, I-02 11, I-03 11,
  I-04 11, tutte le altre 10 (sei comuni a tutte le idee, scritte una volta con la previsione
  specifica in ogni idea, più quattro o cinque proprie).
* Varianti diventate candidati in Fase 2: 0 da idee nuove, 2 da ritocchi (028, 030).
* Varianti che battono nettamente la (a) e la (b) con R medio dopo i costi non positivo: 1 (029).
* Rifiuti del guardiano: 4 (N002, N004, N005, N006), tutti per la forma dei comandi; nessuno ha
  richiesto un percorso vietato dal protocollo.
