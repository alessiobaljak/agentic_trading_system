# DYDXUSDT — lezioni della moneta (idee provate e risultati)

Costruzione 2021-09 → 2023-04-19. `t` = contro la baseline (b) (entrata casuale con la stessa uscita).
Soglia di «netta» circa 2,0-2,1. Tutto in R dopo i costi.

| Idea (fonte) | Timeframe | Varianti | Esito in costruzione |
|---|---|---|---|
| I-01 momento a 7 giorni (Liu e Tsyvinski 2021) | 1d | long, short | long R −0,002 (`t` 0,19); short R −0,058 (`t` −1,21) |
| I-02 rottura del canale di 50 barre (Brock e altri 1992) | 4h, poi 1h | 4h: scarti (40, 54 trade); 1h long, short | R −0,007 (`t` 0,57); −0,000 (`t` 0,32) |
| I-03 RSI(2) con media a 200 (Connors e Alvarez 2008) | 1h | long, short | R −0,024 (`t` −0,05); −0,017 (`t` 0,25) |
| I-04 prima mezz'ora UTC → ultima (Gao e altri 2018; Shen e altri 2022) | 30m | long, short | R −0,041 (`t` 0,68); −0,042 (`t` 0,45): i costi dominano |
| I-05 ritorno dopo movimento forte con volume alto (Campbell, Grossman e Wang 1993) | 1h | soglie strette: scarti (57, 65); larghe long, short | R −0,013 (`t` 0,38); −0,032 (`t` −0,09) |
| I-06 funding affollato (Schmeling, Schrimpf e Todorov 2023) | 8h | ±0,03%: scarti (30, 61); >0,01% scarto (59); <0 long | R −0,014 (`t` 0,21) |
| I-07 lunedì (Caporale e Plastun 2019) | 1d | long | R +0,021 (`t` 0,92); senza i 3 migliori −0,004 |
| I-08 BTC guida, DYDX segue (Lo e MacKinlay 1990) | 1h | long, short | long R +0,060 (`t` 2,22, **candidato**); short R −0,060 (`t` −0,36) |
| I-09 numeri tondi (Osler 2003) | 1h | long, short | R −0,091 (`t` −1,57); −0,020 (`t` 0,37) |
| I-10 barra stretta e rottura (Crabel 1990) | 4h | long, short + 5 ritocchi dello short | long R −0,129 (`t` 0,25); short R +0,175 (`t` 1,35); ritocchi `t` 0,63 / 0,95 / 1,42 / scarto / 0,84 |
| I-11 squilibrio dei taker (Chordia e Subrahmanyam 2004) | 1d | long scarto (54); short + 5 ritocchi | short R +0,015 (`t` 1,14); ritocchi `t` 0,13 / 0,92 / 1,57 / 1,13 / −0,22 |
| I-12 perpetuo contro mark (He, Manela, Ross e von Wachter 2022) | 1h | short, long | R −0,015 (`t` 0,41); −0,075 (`t` −0,93) |

## Il candidato e la sua caduta

`DYDXUSDT-008` (I-08 long) era netto in costruzione per poco (`t` 2,22 contro 2,07), superava tutte le
verifiche, ma:

* il test dello scettico ha mostrato che il ritardo di DYDX non conta: conta solo l'ora forte di BTC;
* in validazione (2023-04-20 → 2023-12-31) ha perso: 83 trade, R −0,178, profit factor 0,43, `t` −1,96.

Lettura: dopo un'ora molto forte di BTC, DYDX è salita nelle ore seguenti nel 2021 e a inizio 2023, non nel
2022 (R 0,002 su 92 trade) e al contrario dopo aprile 2023. È un comportamento di regime, non un vantaggio
stabile.

## Cosa abbiamo capito su questa moneta

* Nessuna delle 13 idee da letteratura dà un vantaggio stabile su DYDX nel 2021-2023. Le più vicine al caso
  battuto (compressione e rottura al ribasso, squilibrio di vendite dei taker) restano sotto la soglia anche
  dopo 5 ritocchi ciascuna.
* Sulle durate brevi (30 minuti, 1 ora) i costi di un giro (0,14%) pesano 0,03-0,05 R a trade: la baseline
  casuale perde 0,02-0,05 R a trade, e una variante deve battere quella, non lo zero.
* La quota di acquisti dei taker sulle candele giornaliere del perpetuo è sotto 0,5 in quasi tutti i giorni
  (257 contro 54 nelle entrate possibili): sul perpetuo i taker vendono più di quanto comprano; il segno da
  solo non è un segnale bilanciato.
* Il funding di DYDX è stato estremo (oltre ±0,03% per 8 ore) troppo di rado per arrivare a 70 trade in 596
  giorni.
