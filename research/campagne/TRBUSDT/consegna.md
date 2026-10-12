# Consegna della campagna TRBUSDT (protocollo 4.5)

**Esito: nessuna strategia valida trovata per questa moneta.**

Budget usato per intero: 30 varianti su 30 (27 da idee nuove, 3 ritocchi), in 27 famiglie; 14
varianti scartate perché sotto i 70 trade stimati in costruzione (non consumano budget). Nessuna
variante ha battuto nettamente né la baseline (a) né la baseline (b) in costruzione: nessun
candidato, quindi niente Fase 4, niente validazione (il periodo 2022-12-31 → 2023-12-31 non è
stato usato da nessun test) e asticella su zero candidati. Nessun candidato va al vault.

Tutti i numeri qui sotto sono «osservati» nel log (`log.jsonl`) salvo dove è scritto «inferito».

## Dati e periodi

* Costruzione 2020-09-01 → 2022-12-30 (851 giorni), validazione 2022-12-31 → 2023-12-31
  (`periodi_campagna`). Prima barra nei file: 2020-09-03.
* Mesi esclusi dagli ingressi perché sotto 20 milioni di USDT al giorno: 7 dei 28 mesi di
  costruzione (2020-09, 2020-10, 2020-12, 2022-01 → 2022-04) e 5 dei 12 di validazione.
* Slippage della scheda (0,02% per lato) ottimista per il 2020-2022: con il volume di quegli anni
  la fascia sarebbe stata 0,10% (2020-2021) e 0,05% (2022) (`fase0_dati.md`). Con zero candidati
  non cambia l'esito: costi più alti abbassano ancora gli R.
* Dettagli: `fase0_dati.md`.

## Controllo degli strumenti

Controllo positivo (lookahead dichiarato, `codice/controllo_positivo.py`): `t` contro la (b) 54,7
senza ritardo, 1,68 con il ritardo di una barra. Il test vede un vantaggio quando c'è e crolla
quando l'informazione arriva tardi. Controllo di causalità di tutte le varianti (condizione e
segnale uguali su serie troncata e intera): 0 differenze.

## Le 30 varianti (costruzione, R dopo i costi)

`t (a)` e `t (b)`: `t` di `contro_baseline`; soglia circa 2. Nessuna è «netta».

| n | variante | tf | dir | trade | R medio | (b) | t (a) | t (b) | percentile | profit factor |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | I-01-L momentum della serie | 4h | long | 108 | −0,007 | 0,072 | −0,33 | −0,62 | 23,0 | 0,97 |
| 2 | I-01-S | 4h | short | 112 | −0,250 | −0,208 | −0,18 | −0,36 | 34,0 | 0,60 |
| 3 | I-03-L reazione eccessiva | 1h | long | 79 | 0,003 | −0,024 | 0,26 | 0,24 | 59,0 | 1,00 |
| 4 | I-03-S | 1h | short | 100 | −0,006 | −0,063 | 0,52 | 0,55 | 75,5 | 0,98 |
| 5 | I-04-A sgonfiamento dopo gonfiamento | 1h | short | 90 | −0,157 | −0,097 | −0,23 | −0,35 | 37,5 | 0,72 |
| 6 | I-04-B (soglie più basse) | 1h | short | 215 | −0,155 | −0,096 | −0,32 | −0,63 | 26,5 | 0,72 |
| 7 | I-06-L lunedì | 1d | long | 90 | 0,062 | −0,011 | 0,05 | 0,44 | 74,0 | 1,10 |
| 8 | I-08-L RSI a 2 barre | 4h | long | 84 | −0,010 | 0,000 | −0,19 | −0,23 | 34,5 | 0,93 |
| 9 | I-08-S | 4h | short | 90 | 0,002 | −0,025 | 0,54 | 0,73 | 80,0 | 1,01 |
| 10 | I-10-L prima → ultima mezz'ora | 30m | long | 310 | −0,114 | −0,090 | −0,80 | −0,59 | 30,5 | 0,62 |
| 11 | I-10-S | 30m | short | 316 | −0,110 | −0,092 | −0,68 | −0,46 | 32,5 | 0,62 |
| 12 | I-11-L numeri tondi | 1h | long | 458 | −0,040 | −0,019 | −0,26 | −0,33 | 34,5 | 0,91 |
| 13 | I-11-S | 1h | short | 449 | −0,060 | −0,087 | 0,31 | 0,43 | 73,0 | 0,87 |
| 14 | I-12-L posizione della chiusura | 1d | long | 112 | 0,036 | −0,007 | −0,12 | 0,35 | 64,0 | 1,07 |
| 15 | I-12-S | 1d | short | 110 | −0,132 | −0,091 | −0,23 | −0,38 | 34,5 | 0,74 |
| 16 | I-13-L rottura della prima ora | 15m | long | 508 | −0,070 | −0,151 | 1,65 | 0,82 | 83,0 | 0,87 |
| 17 | I-13-S | 15m | short | 474 | −0,129 | −0,273 | 1,75 | 1,37 | 92,5 | 0,77 |
| 18 | I-02-L2 rottura del canale (20 barre) | 4h | long | 72 | −0,175 | 0,060 | −1,18 | −1,46 | 6,0 | 0,72 |
| 19 | I-07-L2 compressione e rottura | 1h | long | 152 | 0,079 | −0,244 | 1,20 | 1,31 | 91,0 | 1,08 |
| 20 | I-07-S2 | 1h | short | 135 | 0,086 | −0,296 | 1,01 | 1,12 | 89,0 | 1,08 |
| 21 | I-15-S2 asimmetria (80°) | 4h | short | 106 | −0,180 | −0,103 | −0,65 | −0,87 | 20,5 | 0,63 |
| 22 | I-15-L2 (20°) | 4h | long | 106 | −0,025 | 0,025 | 0,01 | −0,58 | 27,0 | 0,92 |
| 23 | I-16-L rapporto delle varianze | 1h | long | 200 | −0,147 | −0,034 | −1,49 | −1,66 | 2,5 | 0,66 |
| 24 | I-16-S | 1h | short | 203 | −0,043 | −0,073 | 0,40 | 0,39 | 69,5 | 0,87 |
| 25 | I-17-L volatilità bassa | 4h | long | 90 | −0,003 | 0,045 | −0,32 | −0,36 | 33,0 | 0,98 |
| 26 | I-18-L martello | 4h | long | 122 | 0,066 | 0,018 | 0,07 | 0,30 | 62,5 | 1,10 |
| 27 | I-18-S stella cadente | 4h | short | 122 | −0,204 | −0,123 | −0,19 | −0,60 | 28,0 | 0,66 |
| 28 | I-13-S-R1 ritocco: rottura dalle 04 UTC | 15m | short | 179 | 0,058 | −0,184 | 1,57 | 1,25 | 91,5 | 1,09 |
| 29 | I-13-S-R2 ritocco: rottura dalle 08 UTC | 15m | short | 108 | 0,080 | −0,181 | 1,27 | 1,02 | 87,5 | 1,14 |
| 30 | I-13-S-R3 ritocco: stop + 0,5 ATR | 15m | short | 474 | −0,147 | −0,253 | 0,47 | 0,75 | 84,5 | 0,74 |

R per anno, R senza i 3 migliori, baseline complete e buy and hold per anno sono nelle voci
`risultato` del log. Le varianti più alte (I-13-S, I-07-L2, I-13-S-R1) hanno tutte R medio senza i 3
trade migliori negativo e un 2020 molto negativo.

Scarti per trade stimati (nessun budget): I-02-L 38, I-02-S 30, I-05-S 36, I-05-L 28, I-07-L 40,
I-07-S 33, I-09-L 27, I-02-S2 60, I-05-S2 53, I-05-L2 46, I-09-L2 47, I-14-L 25, I-15-S 44, I-15-L 48.

## Riepilogo delle idee provate

18 idee con fonte (`ipotesi.md`), in sette famiglie di meccanismi: trend (momentum della serie,
rottura del canale, compressione e rottura, rottura della prima ora), ritorno dopo eccessi (reazione
eccessiva, RSI a 2 barre, posizione della chiusura, ombre di rifiuto), flussi e volume (gonfiamenti
di prezzo e volume, volume alto, illiquidità), funding affollato, calendario (lunedì, mezz'ore UTC),
numeri tondi, distribuzione dei rendimenti (asimmetria, rapporto delle varianze, volatilità bassa).
Tre idee (funding affollato, volume alto, illiquidità) non sono mai arrivate a 70 trade in
costruzione, nemmeno con le soglie allentate.

## Perché «nessuna strategia valida» (osservato e inferito)

* Osservato: i `t` contro la (b) delle 30 varianti hanno media 0,05 e deviazione 0,80 (massimo
  1,37, minimo −1,66). È la forma che la prova a placebo del protocollo trova per regole senza
  vantaggio (deviazione 0,815): l'insieme dei risultati non si distingue dal rumore.
* Osservato: 25 previsioni su 30 corrette (R medio nell'intervallo scritto prima).
* Inferito: su TRBUSDT 2020-2022 la volatilità è molto alta (ATR mediano 13,4% al giorno, 2,3%
  all'ora) e ci sono ombre estreme (fino all'83% in una barra a 15m): gli stop in R sono presi spesso
  dal rumore, e un vantaggio piccolo ha bisogno di più trade di quanti la moneta ne dia (sezione 11,
  «Potenza bassa»), anche perché un quarto dei mesi di costruzione è escluso per liquidità.

## Misure di processo

Dal log (`codice/misure.py`; date prese con `date -u`):

* Durata dalla prima voce (2026-10-09 15:26:41 UTC) all'ultima: vedi l'ultima voce del log
  (nota di chiusura); fino alla Fase 5 59,5 minuti, nessuna pausa. Una sessione.
* Varianti 30, di cui 3 ritocchi; 27 famiglie; 15 idee testate su 18 scritte; 14 scarti.
* Minuti dalla registrazione della prima variante all'ultimo risultato, per idea: I-01 0,2; I-03
  2,0; I-04 2,7; I-06 0,0; I-08 0,1; I-10 1,2; I-11 0,7; I-12 0,0; I-13 29,2 (con i 3 ritocchi);
  I-02 0,1; I-07 7,3; I-15 3,4; I-16 3,5; I-17 1,0; I-18 0,1. I test girano in serie in un processo
  solo: i minuti misurano il calcolo, non il ragionamento, che sta in `ipotesi.md` ed è stato
  scritto prima dei test.
* Spiegazioni concorrenti scritte in `ipotesi.md`: 10 per ciascuna delle 18 idee (le varianti
  allentate usano quelle della loro idea).
* Varianti diventate candidati in Fase 2: 0 da idee nuove, 0 da ritocchi.
* Varianti che hanno battuto nettamente la (a) e la (b) con R medio dopo i costi non positivo: 0.

## Rischi e limiti noti

* Il modello sa a grandi linee che TRBUSDT nel 2023 (periodo di validazione) ha avuto movimenti
  molto ampi (nota del log del 15:32). Nessun candidato è arrivato alla validazione, quindi la
  conoscenza non ha toccato nessun giudizio; vale per una eventuale campagna futura su questa moneta.
* Le fonti delle idee sono note al modello: le campagne sono indipendenti nel metodo, non nel
  giudizio (sezione 11).
* Lo slippage del 2020-2022 è sottostimato dalla scheda (sopra).
* Il budget è stato usato per intero anche se 14 regole sono finite fra gli scarti: tre idee non
  sono state messe alla prova per niente.

## Previsione per vault e trasferimento

Nessun candidato: niente vault e niente trasferimento da questa moneta.
