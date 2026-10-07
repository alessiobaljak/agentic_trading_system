# Lezioni della moneta ETHUSDT

Idee provate e fallite, con i numeri. Resta in questa cartella fino al Passo 7. Tutto sul
periodo di costruzione (2020-01-01 → 2022-10-19), costi del protocollo, stop a 2 ATR.

## Cosa non funziona su ETHUSDT (23 varianti, nessuna batte le entrate casuali oltre 2 errori standard)

| Famiglia | Idea | Esito in breve |
|---|---|---|
| Tendenza | momento a 7 giorni (4h) | long 1,38 di profit factor ma uguale a un long casuale nel 2020-21 e in perdita nel 2022; short 0,86 |
| Ritorno alla media | RSI a 2 periodi (1h) | perde in entrambe le direzioni (0,75 e 0,66) e sta sotto il 98 % delle entrate casuali: le molte piccole vincite non pagano gli stop |
| Valore relativo | ritardo di ETH su BTC (1h) | long 0,95, short 0,69: nessun recupero sfruttabile a 1 ora |
| Calendario | prima ora predice l'ultima (1h) | long 0,72; short 0,88 con percentile 98,5 ma 1,5 errori standard e in perdita |
| Funding | funding estremo contrario (8h) | short 0,77, uguale allo short casuale: il funding incassato in 8 ore non compensa il prezzo |
| Base del perpetuo | premio del last sul mark (1h) | 0,78 e 0,88: il premio non predice nulla a 1 ora |
| Range d'apertura | rottura di mezzo ATR giornaliero (1h) | long 1,32 e 99° percentile ma 1,2 errori standard, tutto 2020-21; short 1,02 |
| Sessione | ore americane long, asiatiche short (1h) | +0,02 e −0,02 R netti, percentili 97,5 e 98,5, 1,1-1,2 errori standard: struttura debole, non paga i costi |
| Dipendenza seriale | segno del giorno prima (1d) | 0,87 e 0,68, sotto l'86 % delle casuali: a un giorno semmai inversione debole |
| Livelli tondi | attraversamento di multipli di 10/100 USDT (1h) | 0,78 e 0,68, come il caso |
| Volume condizionato | inversione dopo movimento a volume alto (4h) | 0,96 e 0,77, come il caso |
| Figure di candele | avvolgente dopo 3 contrarie (4h) | short 0,84, come il caso (la fonte aveva ragione) |
| Inversione lunga | 33 % sopra il minimo a 30 giorni, short (4h) | 0,55, la peggiore: i rialzi ampi del 2020-21 continuano |

Scartate prima del test per pochi trade (meno di 100 per direzione in 1.023 giorni): rottura
del canale a 30 barre, candela anomala a 2,5 sigma, rapporto ETH/BTC a 2 sigma, momento
relativo settimanale, inversione del fine settimana, compressione della volatilità,
premio del volume alto, funding estremo long, squilibrio degli ordini aggressivi,
vicinanza al massimo a 30 giorni, continuazione a volume basso, avvolgente long,
inversione lunga long.

## Tre cose capite su questa moneta

1. **Il 2020-21 regala e il 2022 toglie.** Ogni long con un filtro qualunque guadagna nel
   2020 (ripresa dopo marzo) e nel 2021 e perde nel 2022; è il motivo per cui le entrate
   casuali con la stessa direzione sono la baseline giusta e perché tre profit factor
   sopra 1 non valgono nulla.
2. **A 1 ora i costi sono il mercato.** Con 0,12 % per giro e durate di 1-4 ore il profit
   factor dopo costi sta fra 0,66 e 0,95 anche per idee con percentile alto: su ETHUSDT un
   vantaggio a 1 ora deve valere più di 0,1 R per trade per sopravvivere, e nessuno lo fa.
3. **Il funding non è un segnale a 8 ore.** Il funding estremo è stato quasi sempre
   positivo nel 2020-21 (97 % dei settlement sopra zero) e ha accompagnato il trend, non lo
   ha invertito.

## Cosa resterebbe da guardare (non fatto: la campagna è chiusa)

* Sessione del giorno e range d'apertura con durate più lunghe o costi da maker: solo come
  nuove ipotesi scritte prima, in un'altra campagna o al Passo 7, mai riaprendo questa.
* Le idee settimanali con le due direzioni insieme, se il coordinamento scrive la regola.
