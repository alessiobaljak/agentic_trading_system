# Consegna della campagna DOGEUSDT (protocollo 4.5)

**Esito: nessuna strategia valida trovata per questa moneta.**

Il budget di 30 varianti è stato usato per intero: 25 varianti da 16 idee nuove con fonte e 5
ritocchi. Una sola variante è diventata candidato in Fase 2 (DOGEUSDT-042, al terzo ritocco di
una stessa famiglia) e non ha superato le verifiche della Fase 4 (robustezza e costi doppi).
Nessun candidato è andato in validazione: il periodo di validazione (2022-12-13 → 2023-12-31) è
rimasto intatto e l'asticella non si applica (zero candidati).

Tutti i numeri vengono dal log (`log.jsonl`), salvo dove è scritto altrimenti.

## Periodi e dati

* Costruzione 2020-07-01 → 2022-12-12, validazione 2022-12-13 → 2023-12-31 (`periodi_campagna`).
* Tutti i mesi del 2020 sono sotto la liquidità minima (2,9-14,0 milioni di USDT al giorno
  contro 20): nessun ingresso su segnali di quelle barre. La costruzione utile per gli ingressi
  va quindi dal 2021-01-01 al 2022-12-12 (711 giorni) ed è fatta di due anni molto diversi: la
  grande salita e il picco del 2021 (buy and hold +3.536% nel 2021) e il ribasso del 2022
  (−47%). Dettagli in `fase0_dati.md`.
* Controllo positivo degli strumenti superato prima della prima variante: `t` contro la (b) 57,1
  senza ritardo, 2,7 con il ritardo di una barra.

## Le idee provate (Fase 2, dati di costruzione)

`t` = `t` di `contro_baseline` contro la (b); soglia circa 2,0-2,1. Nessuna variante delle idee
nuove ha battuto nettamente né la (a) né la (b).

| Idea (fonte) | Varianti testate | R medio | `t` contro la (b) |
|---|---|---|---|
| I-01 momento a una settimana (Moskowitz-Ooi-Pedersen 2012; Liu-Tsyvinski 2018) | 001 long 1d, 002 short 1d | 0,078; 0,000 | −0,07; 1,01 |
| I-02 prima mezz'ora prevede l'ultima (Shen-Urquhart-Wang 2021) | 003 long 30m, 004 short 30m | −0,092; −0,048 | −1,23; 0,81 |
| I-03 rottura del canale (Brock-Lakonishok-LeBaron 1992; Hudson-Urquhart 2019) | 033 short 4h (allentata) | 0,033 | 0,20 |
| I-04 rottura di volatilità (Williams 1999) | 007 long 1h, 008 short 1h | 0,030; 0,021 | 0,67; 0,21 |
| I-05 RSI a 2 barre (Connors-Alvarez 2008) | 009 long 4h, 010 short 4h | −0,073; 0,007 | −0,82; 0,91 |
| I-06 volume alto o basso (Gervais-Kaniel-Mingelgrin 2001) | 012 short 1d | 0,002 | 0,68 |
| I-07 lotteria (Bali-Cakici-Whitelaw 2011; Grobys-Junttila 2021) | 013 short 1d | −0,112 | −1,02 |
| I-08 funding estremo (He-Manela-Ross-von Wachter 2022) | 015 short 8h, 016 long 8h | −0,163; −0,037 | −2,67; −0,98 |
| I-09 lunedì (Caporale-Plastun 2019) | 017 long 1d | −0,057 | −1,29 |
| I-10 strettoia di Bollinger (Bollinger 2001) | 034 long 1h, 035 short 1h (allentate) | −0,089; 0,124 | −0,39; 1,33 |
| I-11 inversione dopo una barra estrema (Lehmann 1990) | 020 long 1h, 021 short 1h | −0,064; −0,076 | −0,10; −0,51 |
| I-12 inerzia dopo un giorno anomalo (Caporale-Plastun 2019) | nessuna: 4 varianti sotto i 70 trade | — | — |
| I-13 squilibrio degli ordini aggressivi (Chordia-Subrahmanyam 2004) | 025 short 1d | 0,002 | 1,01 |
| I-14 numeri tondi (Osler 2003) | 026 long 1h, 027 short 1h | −0,106; −0,023 | −1,71; 0,61 |
| I-15 giorno stretto NR4 (Crabel 1990) | 028 long 1h, 029 short 1h | −0,227; 0,172 | −0,98; 1,17 |
| I-16 movimenti direzionali (Wilder 1978) | 038 long 1h, 039 short 1h (allentate) | −0,078; −0,068 | −0,73; −0,46 |

Scarti sotto i 70 trade (nessun budget): 005, 006, 011, 014, 018, 019, 022, 023, 024, 030, 031,
032, 036, 037.

## Ritocchi (regola 6) e il candidato caduto

Tutti e 5 i ritocchi sono andati alla famiglia DOGEUSDT-035 (strettoia di Bollinger short a 1h),
rimasta prima nell'ordine a ogni passo:

| Ritocco | Cosa cambia | R medio | `t` (a) | `t` (b) |
|---|---|---|---|---|
| 040 (da 035) | uscita dopo 24 barre | 0,123 | 1,05 | 0,59 |
| 041 (da 035) | stop 3 ATR | 0,112 | 1,87 | 1,81 |
| **042 (da 041)** | **strettoia sulle ultime 480 barre** | **0,158** | **2,19** | **2,14** |
| 043 (da 041) | strettoia al 10° percentile | 0,072 | 1,15 | 0,99 |
| 044 (da 041) | stop 4 ATR | 0,085 | 1,90 | 1,86 |

**DOGEUSDT-042** (regole in `candidati/DOGEUSDT-042/regole.md`): 130 trade in costruzione, R
medio 0,158, profit factor 1,62, drawdown massimo −7,2%, rendimento +14,0% nel 2021 e +7,3% nel
2022 (rischio 1% a trade), R medio 0,201 nel 2021 e 0,114 nel 2022, senza i 3 migliori 0,080,
percentile fra le simulazioni casuali 100. Batte nettamente la (a) (`t` 2,19, soglia 2,04) e la
(b) (`t` 2,14, soglia 2,04, media della (b) −0,017). Nessun trade ridotto per il tetto di leva,
nessuna violazione della liquidazione, 13 stop oltre il 6% del prezzo (tetto del bot).

Verifiche della Fase 4 (registrate prima, nel log come DOGEUSDT-042-V01 … V20):

| Verifica | Esito | Superata |
|---|---|---|
| Robustezza (14 casi ±20%) | `t` contro la (b) positivo in 14 su 14 (da 1,66 a 2,82), netto in 6 su 14; ne servivano 7 | **no** |
| Timeframe adiacenti | 30m: 173 trade, `t` 2,34; 2h: 55 trade, sotto il minimo (dichiarato) | sì |
| Stabilità temporale | R sopra la (b) nel 2021 e nel 2022 | sì |
| Pochi trade estremi | senza i 3 migliori R 0,080 contro la (b) −0,017 | sì |
| Ritardo di una barra | `t` 1,95 (metà dell'originale: 1,07) | sì |
| Costi doppi | R 0,115 positivo, `t` 2,013 contro soglia 2,040: non netto | **no** |
| Liquidazione | 0 violazioni | sì |
| Regola intra-barra opposta | nessuna differenza (non c'è target) | dichiarata |
| Stop sul mark invece che sul last | `t` 2,10 invece di 2,14 | dichiarata |

Il candidato si scarta in Fase 4. È un picco, non un'area stabile: metà dei vicini cade sotto la
soglia, e a costi doppi non è più netto.

## Misure di processo

Dal log (orologio della macchina, `date -u`):

* Durata dalla prima all'ultima voce del log: 2026-10-09 12:23:09 → 13:05:01 UTC, 42 minuti;
  nessuna pausa, quindi 42 minuti anche senza pause. Prima della prima
  voce del log ci sono circa 3 minuti di apertura (branch, marcatore, test del guardiano).
* Minuti per idea (dalla registrazione della prima variante all'ultimo risultato): I-01 0,2;
  I-02 1,0; I-03 4,7; I-04 1,4; I-05 1,4; I-06 1,5; I-07 1,5; I-08 1,6; I-09 1,6; I-10 15,5
  (compresi i 5 ritocchi); I-11 1,9; I-12 4,5; I-13 0,1; I-14 0,6; I-15 0,9; I-16 1,5. Le idee
  I-01 … I-12 sono state scritte tutte insieme in `ipotesi.md` mentre i dati si scaricavano, e
  registrate e testate in un lotto: i minuti per idea misurano il tempo di calcolo, non quello
  di pensiero.
* Spiegazioni concorrenti scritte in `ipotesi.md`: 8 comuni a tutte le idee più quelle
  specifiche: I-01 11, I-02 11, I-03 11, da I-04 a I-16 10 ciascuna.
* Varianti: 30 testate (25 da idee nuove, 5 ritocchi), 25 famiglie, 14 scarti sotto i trade
  minimi; candidati in Fase 2: 0 da idee nuove, 1 da ritocchi (DOGEUSDT-042).
* Varianti che hanno battuto nettamente la (a) e la (b) con R medio dopo i costi non positivo: 0.

## Cosa resta per il vault e il trasferimento

Nessun candidato: nulla va al vault né al trasferimento. Nessuna aggiunta al bot serve per
questa moneta.

## Previsione

Se la regola di DOGEUSDT-042 si guardasse nel vault (non succederà: è scartata), mi aspetterei un
R medio vicino a zero: il suo `t` è nato da una salita di tre ritocchi su una variante allentata,
e le verifiche mostrano un picco.
