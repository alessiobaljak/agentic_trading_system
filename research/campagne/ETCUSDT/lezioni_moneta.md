# ETCUSDT — lezioni sulla moneta (idee provate e risultati)

Resta nella cartella della moneta fino al Passo 7. Solo dati di costruzione (2020-01-01 → 2022-10-18).

## Idee provate

| Idea | Fonte | Esito |
|---|---|---|
| I-01 momento a 7 giorni (4h) | Moskowitz, Ooi, Pedersen 2012; Liu, Tsyvinski 2018 | R alto (long +0,42, short +0,27) ma come le entrate casuali nella stessa direzione: `t` (b) 0,38 e 1,75; due ritocchi dello short (stop 3 ATR, filtro sulla barra in calo) non cambiano nulla (1,06 e 1,49). Stop oltre il 6% del bot in 3 trade su 4. |
| I-02 rottura del canale di 50 barre (4h) | Brock, Lakonishok, LeBaron 1992 | Sotto i 70 trade (43 e 40). |
| I-03 inversione dopo uno shock di 3 deviazioni (1h) | Nagel 2012; Jegadeesh 1990 | Long nulla (−0,002 R), short perde (−0,18 R, `t` (b) −1,9): dopo un rialzo forte di un'ora il prezzo non torna indietro. |
| I-04 continuazione dopo giornata anomala (1d) | Caporale, Plastun 2019 | Nulla (long +0,09, short −0,11). |
| I-05 funding estremo (8h) | He, Manela, Ross, von Wachter 2022 | Sotto i 70 trade (67 e 59). |
| I-06 volume alto / basso (4h) | Gervais, Kaniel, Mingelgrin 2001 | Long +0,46 R ma `t` (b) 0,50 (trend del periodo); short nullo. |
| I-07 squilibrio dei taker (1h) | Chordia, Subrahmanyam 2004 | Perde (−0,09 e −0,07 R su quasi 900 trade): costi. |
| I-08 lunedì (1d) | Caporale, Plastun 2019 | Nulla. |
| I-09 BTC guida, ETC segue (1h) | Hou 2007; Koutmos 2018 | Long nullo; short sotto i minimi. |
| I-10 compressione di Bollinger (4h) | Bollinger 2001 | Sotto i minimi (15 e 17). |
| I-11 RSI a 2 nel trend (4h) | Connors, Alvarez 2009 | Nulla. |
| I-12 fine giornata UTC (30m) | Gao, Han, Li, Zhou 2018; Shen, Urquhart, Wang 2022 | **L'unica che batte nettamente il caso** (short dopo giornata in calo, `t` (b) 3,15), ma il guadagno lordo (~+0,045 R) è più piccolo dei costi. Tre ritocchi candidati, tutti caduti a costi doppi e col ritardo. Il long simmetrico perde. |
| I-13 incrocio medie 10/30 (4h) | Hudson, Urquhart 2021 | Come I-01: R alto, `t` (b) 0,85 e 1,57. |
| I-14 numeri tondi (1h) | Osler 2003 | Nulla (−0,05 e −0,06 R). |
| I-15 illiquidità alta (4h) | Amihud 2002 | Nulla (`t` (b) −1,07). |
| I-16 rottura delle prime 4 ore UTC (1h) | Crabel 1990 | Nulla. |
| I-17 coppia con BTC (4h) | Gatev, Goetzmann, Rouwenhorst 2006 | Sotto i minimi (48 e 47). |

## Cosa resta da sapere

* L'effetto di fine giornata UTC nei giorni in calo è di tutto il mercato (su BTC è la mezz'ora più
  negativa delle 48, −14,8 punti base nei giorni in calo). Su ETC vale circa 10 punti base lordi (29 nei
  giorni sotto −5%), contro circa 20 punti base di costi per giro con commissioni e slippage da taker. Con
  costi più bassi (ordini limit, monete più liquide) potrebbe essere un'altra storia: qui non si può dire.
* Le idee lente (canale, funding, compressione, coppia) non arrivano a 70 trade su una moneta sola in 2,8
  anni: la campagna di gruppo (Passo 4bis) sarebbe il posto per provarle.
* Nel 2020-2022 il trend di ETC ha dato R alti a qualunque ingresso nella sua direzione: i confronti con la
  (b) sono stati indispensabili per non scambiarlo per un segnale.
