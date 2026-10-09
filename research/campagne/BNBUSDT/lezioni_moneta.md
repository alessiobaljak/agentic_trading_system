# BNBUSDT — lezioni della moneta

Idee provate e risultati, sui dati di costruzione (2020-02-01 → 2022-10-28) salvo dove detto.
t = t contro la baseline (b) (entrate casuali con la stessa uscita). Costi: 0,14% a giro.

| Idea (fonte) | Variante | Trade | R medio | t (b) | Lettura |
|---|---|---|---|---|---|
| I-01 momentum settimanale (Moskowitz et al. 2012) | long 1d | 98 | +0,142 | −0,21 | il long guadagna quanto un ingresso a caso: è il trend del 2020-2021 |
| | short 1d | 80 | −0,081 | +0,55 | perde meno del caso, non abbastanza |
| I-02 Donchian (Faith 2007) | long 4h | 86 | +0,814 | +0,29 | 3 trade del 2021 fanno tutto: senza di loro −0,10 |
| | short 4h | 71 | −0,035 | +0,45 | niente |
| I-03 RSI(2) (Connors, Alvarez 2008) | long 1h | 270 | +0,003 | +1,67 | la più vicina al caso fra le idee nuove; 4h: scarto (65 trade) |
| I-04 lunedì (Caporale, Plastun 2019) | long 1d | 128 | −0,004 | −0,38 | nessun effetto del lunedì su BNB |
| I-05 funding estremo (Schmeling et al. 2023) | short 8h | 97 | −0,103 | −0,88 | il funding alto non annuncia un calo |
| | long 8h | 147 | +0,064 | +1,16 | funding molto negativo: un po' meglio del caso, non abbastanza |
| I-06 compressione di Bollinger (2001) | 4h | 23 e 23 | — | — | scarto; a 1h: long +0,155 (t 0,65, trainato dal 2021), short −0,093 |
| I-07 volume alto (Gervais et al. 2001) | long 1d | 46 → 72 | +0,155 | +0,18 | come il caso (quintile più alto) |
| I-08 sovrareazione (Caporale, Plastun 2019) | 4h, 2 dev. std | 69 e 53 | — | — | scarti; a 1,5 dev. std: long +0,049 (t 0,38), short −0,213 (t −1,95): dopo un crollo di 24 ore il ribasso NON continua |
| I-09 squilibrio degli ordini (Chordia, Subrahmanyam 2004) | long 4h | 181 | +0,103 | +1,50 | vicino, non abbastanza; 2022 negativo |
| | short 4h | 163 | −0,096 | −0,57 | niente |
| I-10 media a 50 (Brock et al. 1992) | long 4h | 180 | +0,477 | +0,01 | identico al caso: il trend del 2021 |
| | short 4h | 178 | −0,019 | +0,26 | niente |
| I-11 prima e ultima mezz'ora (Shen et al. 2022) | long 30m | 491 | −0,070 | +0,91 | i costi (circa 0,14 R) mangiano tutto |
| | short 30m | 431 | −0,101 | −0,76 | niente |
| I-12 rimbalzo dopo caduta forzata (Brunnermeier, Pedersen 2009) | long 1h, 2 ATR | 176 | −0,178 | −2,13 | dopo una caduta oraria di 2 ATR il prezzo NON rimbalza: tende a continuare |
| I-13 cambio del mese (Lakonishok, Smidt 1988) | long 1d | 30 | — | — | scarto |
| I-14 volatilità bassa (Moreira, Muir 2017) | long 4h | 353 | −0,036 | −1,10 | peggio del caso |
| I-15 ADX (Wilder 1978) | 4h | 46-53 | — | — | scarto anche con soglia 20 |
| I-16 shock di illiquidità (Amihud 2002) | long 4h | 176 | +0,096 | +1,20 | vicino, non abbastanza |
| I-17 asimmetria negativa (Amaya et al. 2015) | long 4h, 7 giorni | 44 → 89 | +0,179 | −0,24 | come il caso, 2022 molto negativo |
| I-18 numeri tondi (Osler 2003) | long 1h | 1482 | −0,032 | +0,44 | niente |
| | short 1h | 1396 | −0,056 | +0,82 | niente |

## Ritocchi (famiglia di I-03 a 1h)

| Variante | Cambio | Trade | R medio | t (b) | Esito |
|---|---|---|---|---|---|
| BNBUSDT-041 | uscita dopo 12 barre | 270 | +0,003 | +1,67 | quasi identica: l'uscita non scatta mai |
| BNBUSDT-042 | uscita dopo 4 barre | 272 | −0,007 | +1,43 | peggio |
| BNBUSDT-043 | ATR ≥ 1,5% del prezzo | 93 | +0,074 | +2,48 | candidato, scartato in Fase 4: col ritardo di un'ora t −0,04 |
| BNBUSDT-044 | close ≥ SMA200 + 1,7 ATR | 181 | +0,047 | +2,74 | candidato, scartato in Fase 4: ritardo (t 1,08) e costi doppi (R −0,001) |
| BNBUSDT-045 | solo sabato e domenica | 74 | +0,138 | +3,96 | candidato, supera la Fase 4 e la validazione al limite (32 trade, p 0,031) |

## Cosa ho capito su BNBUSDT

* Le regole di tendenza (momentum settimanale, Donchian, media a 50, ADX) nel 2020-2022 guadagnano
  quanto un ingresso casuale nella stessa direzione: il guadagno è il trend del 2021, non la regola.
* Dopo i crolli, su BNB, il prezzo tende a continuare più che a rimbalzare (caduta oraria di 2 ATR:
  t −2,13; crollo di 24 ore oltre 1,5 deviazioni standard, short: R −0,21). Fa eccezione il calo di
  poche ore dentro una tendenza rialzista (RSI a 2 periodi), che rimbalza nella prima ora.
* Il rimbalzo dei cali brevi vive nella prima ora: entrando un'ora dopo sparisce per le versioni
  senza il filtro del fine settimana. È un vantaggio di esecuzione più che di previsione.
* Su 30 minuti i costi (circa 0,14 R a giro) bastano a cancellare qualunque idea provata.
