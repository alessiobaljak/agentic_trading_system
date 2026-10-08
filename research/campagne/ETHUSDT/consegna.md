# ETHUSDT — Consegna della campagna (Passo 3, protocollo 4.4)

Scritta l'8 ottobre 2026 dalla sessione di campagna ETHUSDT, sul branch
`research/campagna/ETHUSDT`. Ogni numero ha la sua voce nel log (`log.jsonl`).

## Esito

**Nessuna strategia valida trovata per questa moneta.**

Nessun candidato va al vault. Il periodo di validazione (2022-10-19 → 2023-12-31) non e'
stato usato: nessun candidato e' sopravvissuto alla Fase 4. Asticella (Benjamini-Hochberg
al 10%): m = 0, nessun p-value; esito provvisorio, lo conferma il coordinamento al Passo 4.

## Budget e conti (regola 6)

| | |
|---|---|
| Varianti testate | 30 su 30 (budget usato per intero) |
| Ritocchi | 0 (le idee nuove con fonte hanno riempito il budget) |
| Famiglie (nel senso della regola 6) | 30, ognuna senza ritocchi |
| Idee con fonte | 18 (I-01 ... I-18), in circa 15 famiglie di meccanismo |
| Varianti contate ma scartate sotto i 70 trade | 4 (ETHUSDT-005, -006, -022, -023), senza budget |
| Candidati in costruzione | 1 (ETHUSDT-026) |
| Candidati dopo la Fase 4 | 0 |
| Varianti nette contro la (b) per caso, attese / osservate | 0,68 / 2 (probabilita' di almeno 2 per caso: 14,8%) |

Periodi (voce ETHUSDT-N002): costruzione 2020-01-01 → 2022-10-18 (1022 giorni),
validazione 2022-10-19 → 2023-12-31. Dati: fase0_dati.md (impronte in impronte.json).
Strumenti verificati con il controllo positivo (voce N006: t 42,5 senza ritardo, 0,40 col
ritardo).

## Riepilogo delle idee provate

| Idea | Fonte (prima del 2024) | Varianti | Esito in costruzione |
|---|---|---|---|
| I-01 momentum di una settimana, 1d | Liu e Tsyvinski, RFS 2021 | long, short | come il caso (t 0,48 e 0,31) |
| I-02 rottura di Donchian, 4h | Faith, «Way of the Turtle», 2007 | long, short | come il caso (t 0,17 e 0,69) |
| I-03 media di 50 giorni, 1d | Brock, Lakonishok, LeBaron, JF 1992 | long, short | scarti: 34 e 47 trade |
| I-04 RSI(2) con media di 200, 4h | Connors e Alvarez, 2009 | long, short | come il caso (t -0,13 e 1,24) |
| I-05 barra piu' stretta di 7 (NR7), 4h | Crabel, 1990 | long, short | come il caso (t 0,82 e 0,21) |
| I-06 prima mezz'ora prevede l'ultima, 30m | Shen, Urquhart, Wang, Financial Review 2022 | long, short | long come il caso; short netto (t 2,32) ma R dopo i costi negativo |
| I-07 BTC anticipa ETH, 1h | Lo e MacKinlay, RFS 1990 | long, short | long come il caso; short peggio del caso (t -1,93) |
| I-08 funding alto o negativo, 8h | Schmeling, Schrimpf, Todorov, BIS 2023 | short, long | come il caso (t -0,39 e -0,47) |
| I-09 il lunedi', 1d | Caporale e Plastun, FRL 2019 | long | come il caso (t 0,50) |
| I-10 continuazione dopo un giorno anomalo, 1d | Caporale e Plastun, JES 2019 | long, short | peggio del caso (t -1,52 e -1,86) |
| I-11 passaggio dei numeri tondi, 1h | Osler, JF 2003 | long, short | identico al caso (t 0,09 e -0,24) |
| I-12 volume insolito, 1d | Gervais, Kaniel, Mingelgrin, JF 2001 | long, short | scarti: 65 e 42 trade |
| I-13 rimbalzo dopo vendite forzate, 1h | Brunnermeier e Pedersen, RFS 2009 | long, short | peggio del caso (t -2,09 e -2,89) |
| I-14 rifiuto al massimo/minimo di ieri, 1h | Osler, FRBNY EPR 2000 | short, long | short CANDIDATO (t 2,67), scartato in Fase 4; long t 1,08 |
| I-15 squilibrio degli ordini, 1d | Chordia e Subrahmanyam, JFE 2004 | long, short | come il caso (t -0,10 e -1,02) |
| I-16 stessa ora dei giorni passati, 1h | Heston, Korajczyk, Sadka, JF 2010 | long, short | t 1,55 e 1,14, R dopo i costi negativo |
| I-17 rottura di volatilita' dall'apertura, 1h | Williams, 1999 | long, short | t 1,52 e 1,66, non netti |
| I-18 continuazione dopo vendite forzate, 1h | Llorente, Michaely, Saar, Wang, RFS 2002 | short | t 1,17 (idea nata dai fallimenti di I-13, dichiarata) |

La tabella completa, variante per variante, e' in `lezioni_moneta.md`.

## L'unico candidato: ETHUSDT-026 (scartato in Fase 4)

Regole in `candidati/ETHUSDT-026/regole.md`: ETHUSDT, 1 ora, short; si entra quando una
barra supera il massimo del giorno UTC precedente e chiude sotto; stop al massimo della barra
piu' 0,25 ATR(14), al massimo 6%; esce dopo 6 barre; rischio 1%, leva al massimo 2, margine
isolated.

| Metrica (costruzione) | Valore |
|---|---|
| Trade | 615 (17 ridotti per il tetto di leva) |
| R medio dopo i costi | +0,023 (senza i 3 migliori -0,023) |
| R medio per anno | 2020 -0,050; 2021 +0,138; 2022 -0,056 |
| Profit factor | 1,03 |
| Drawdown massimo | -21,6% |
| Rendimento totale | +9,6% in 2 anni e 10 mesi |
| Contro la (a) | t 2,76, netta (la (a) fa -0,190 R) |
| Contro la (b) | t 2,67, netta (la (b) fa -0,175 R); percentile fra le simulazioni 99,5 |
| Buy and hold, long / short | 2020 +470% / -471%; 2021 +398% / -399%; 2022 (fino al 18 ottobre) -64% / +64% |

Verifiche della Fase 4: superate stabilita', trade estremi, liquidazione, robustezza (6 su 6
netti), timeframe adiacenti (30m t 3,05; 2h t 1,57); **non superate i costi doppi (R medio
-0,076) e il ritardo di una barra (t 1,27, serve 1,33)**. Non e' andato in validazione:
nessun p-value, nessun criterio del vault da applicare, nessuna previsione per il vault o il
trasferimento, nessuna stima di trade in paper.

## Rischi e limiti da sapere (sezione 11)

* La conclusione «nessuna strategia» vale per queste 18 idee su ETHUSDT 2020-2022, con le
  regole del protocollo: la potenza e' bassa, un vantaggio vero e piccolo puo' non passare.
* Lo slippage del 2020 e' ottimista (volume un decimo di quello del 2023): un costo piu' alto
  peggiora tutte le varianti, non ne salva nessuna.
* Quattro idee sono state scritte dopo aver visto i primi risultati (I-15 ... I-18), una
  (I-18) proprio dai fallimenti di costruzione: dichiarato in `ipotesi.md`.
* Tre azioni rifiutate dal guardiano, tutte per la forma del comando (voci N003, N007, N009):
  nessun dato vietato e' stato letto.

## Cosa puo' eseguire il bot

Nessuna regola da portare al bot. (Per la cronaca: il candidato scartato sarebbe stato
eseguibile a 1 ora con stop sotto il 6%, ma l'orizzonte di 6 ore e l'abilitazione senza il
gate richiedono l'aggiunta decisa al Passo 0, `config/regole_dimensione.md`.)
