# BCHUSDT — Consegna (protocollo 4.5, Passo 3)

## Esito

**Nessuna strategia valida trovata per questa moneta.**

Nessuna delle 30 varianti del budget ha battuto nettamente la baseline (a) o la baseline (b)
sui dati di costruzione (2020-01-01 → 2022-10-18). Non ci sono candidati: la Fase 4, la
validazione e l'asticella non sono state eseguite, e il periodo di validazione (2022-10-19 →
2023-12-31) non è stato toccato. Nulla va al vault per BCHUSDT.

## Riepilogo delle idee provate

14 idee con fonte pubblicata prima del 2024, in 10 famiglie di meccanismo; 25 varianti da idee
nuove, 5 ritocchi; 8 scarti sotto i 70 trade (nessun budget). Dettaglio in `ipotesi.md`,
risultati in `log.jsonl` e `lezioni_moneta.md`.

| Idea | Timeframe | Varianti testate | Miglior `t` contro la (b) |
|---|---|---|---|
| I-01 momento della serie a 7 giorni (Moskowitz-Ooi-Pedersen 2012; Liu-Tsyvinski 2018) | 1d | 6 (2 + 4 ritocchi) | 1,62 (short, BCHUSDT-002) |
| I-02 rottura del canale (Brock-Lakonishok-LeBaron 1992; Faith 2007) | 4h | 2 | 0,19 |
| I-03 RSI a 2 periodi (Connors-Alvarez 2008) | 4h | 2 | 0,74 |
| I-04 rottura di volatilità (Williams 1999) | 1h | 3 (2 + 1 ritocco) | 1,53 (short, BCHUSDT-008) |
| I-05 numeri tondi (Osler 2003) | 1h | 2 | −0,27 |
| I-06 sovra-reazione (Caporale-Plastun 2019) | 1d | 2 | 0,44 |
| I-07 lunedì (Caporale-Plastun 2019) | 1d | 1 | −0,16 |
| I-08 volume alto (Gervais-Kaniel-Mingelgrin 2001) | 1d | 1 | 0,24 |
| I-09 inversione con volume (Campbell-Grossman-Wang 1993) | 4h | 2 | −0,60 |
| I-10 funding estremo (He-Manela-Ross-von Wachter 2022) | 8h | 2 | 0,22 |
| I-11 flusso aggressivo (Evans-Lyons 2002) | 1h | 2 | 0,04 |
| I-12 compressione di Bollinger (Bollinger 2001) | 1h | 2 | 0,63 |
| I-13 media mobile (Detzel e altri 2018) | 1d | 2 | 0,69 |
| I-14 volatilità bassa (Moreira-Muir 2017) | 1d | 1 | 0,22 |

Il `t` più alto (1,62) resta sotto la soglia (circa 2,0). Sui 30 risultati: `t` medio 0,11,
deviazione standard 0,96, nessuno sopra 2 e uno sotto −2; R medio dopo i costi positivo in 15
varianti su 30. È la forma attesa da regole senza vantaggio (osservato). Le varianti più vicine
sono short che guadagnano quasi solo nel 2022, l'anno del ribasso (osservato); che sia un effetto
di regime e non della regola è inferito.

## Controlli fatti per smontare il risultato

* Controllo positivo degli strumenti (lookahead dichiarato): long 1h `t` 52,7 → 2,04 col ritardo
  di una barra; short 1d `t` 14,1 → −0,38; short 4h `t` 38,0 → 0,94. Gli strumenti vedono un
  vantaggio grande dove c'è e il ritardo lo smaschera (osservato).
* Verifica di causalità degli indicatori a ogni registrazione (tagli della serie): nessuna
  variante registrata ha indicatori che guardano avanti; il controllo l'ha trovato dove c'era.
* Limiti noti di questa campagna: lo slippage della scheda (0,02%) è ottimista per il 2020 e il
  2022 (volume nella fascia di 0,05%): i risultati veri sarebbero un po' peggiori, e nessuno era
  vicino alla soglia comunque. La potenza è bassa (circa 80-330 trade per variante): un vantaggio
  vero sotto circa 0,1 R a trade non si distingue dal caso (sezione 11).

## Varianti sul budget

30 varianti testate su 30 (budget usato per intero): 25 da idee nuove, 5 ritocchi (4 nella
famiglia BCHUSDT-002, che ha raggiunto il massimo di 5 ritocchi contando lo scarto
BCHUSDT-033; 1 nella famiglia BCHUSDT-008). 25 famiglie. Nessun p-value di validazione né esito
dell'asticella: nessun candidato.

## Misure di processo

Ricavate dal log con `codice/misure.py` (date prese dall'orologio della macchina).

| Misura | Valore |
|---|---|
| Durata dalla prima all'ultima voce del log | 27,0 minuti (2026-10-09 14:27:51 → 14:54:49 UTC), senza pause |
| Durata con le pause | uguale: nessuna pausa registrata |
| Voci del log | 90 |
| Varianti testate / ritocchi / famiglie / scarti | 30 / 5 / 25 / 8 (di cui 1 ritocco) |
| Varianti diventate candidati in Fase 2 | 0 da idee nuove, 0 da ritocchi |
| Varianti nette contro la (a) e la (b) con R medio dopo i costi non positivo | 0 |
| Spiegazioni concorrenti per idea (ipotesi.md) | 10 per ognuna delle 14 idee |

Minuti per idea, dalla registrazione della prima variante all'ultimo risultato delle sue
varianti: I-01 12,2 (6 varianti con i ritocchi); I-02 0,5; I-03 0,6; I-04 12,7 (con il ritocco);
I-05 1,0; I-06 0,1; I-07 1,0; I-08 0,1; I-09 1,1; I-10 1,2; I-11 1,7; I-12 0,7; I-13 0,7; I-14
0,8. Questi minuti misurano solo conta e test (il motore è veloce: un test con le 200 simulazioni
della (b) dura 1-20 secondi); la scrittura della Fase 1 è avvenuta prima delle registrazioni e
non è nel log. La sessione è cominciata alle 14:26 circa (marcatore e test del guardiano, prima
della prima voce).

Rifiuti del guardiano registrati: 5 (voci N003, N004, N005, N009, N013), tutti per la forma dei
comandi (redirezioni, `python -c`, espressioni fra apici, lettura della cartella temporanea);
nessuna lettura vietata tentata.

## Previsione

Nessun candidato va al vault o al trasferimento. Previsione per il Passo 7: le regole provate qui
sono regole da manuale; se altre monete trovano un vantaggio con le stesse famiglie, mi aspetto
che sia di regime (anni di forte ribasso o rialzo), non della regola.
