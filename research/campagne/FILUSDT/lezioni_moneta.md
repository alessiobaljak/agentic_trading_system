# Lezioni della campagna FILUSDT (idee provate e risultati)

Solo dati di costruzione (2020-10-16 → 2023-01-08), salvo dove è scritto «validazione». R = guadagno
diviso il rischio iniziale del trade, dopo i costi. «(b)» = ingressi casuali con la stessa uscita;
«t» = distanza dalla (b) in errori standard (soglia circa 2).

## Cosa non ha funzionato (nessun vantaggio contro la (b))

| Idea | Varianti | Esito in breve |
|---|---|---|
| Momento settimanale (4h) | 001 long, 002 short | t 0,41 e 0,17: lo short guadagna (+0,25) solo perché la (b) short guadagna uguale (ribasso di fondo) |
| Rottura del canale (4h) | 4 scarti | mai 70 trade in 815 giorni |
| Inversione dopo 24 ore estreme (1h) | 005 long, 006 short | nessun rimbalzo: R −0,05 e −0,09 |
| Inversione delle barre estreme con volume (1h) | 009, 010 | R −0,06 e −0,07; nel 2022 i crolli con volume continuano |
| RSI(2) nel trend (4h) | 012 short (long scarto) | +0,045, win rate 62%, t 0,94: debole, non netto |
| Funding alto/negativo (8h) | 013 short, 014 long | lo short col funding sopra 0,03% perde (−0,15): nel 2021 il prezzo è salito per giorni |
| Lunedì (1d) | 015 | il lunedì di FIL è stato peggiore di un giorno qualunque (−0,21, t −1,9) |
| Squilibrio degli ordini aggressivi (1h) | 021, 022 | dopo forti acquisti aggressivi il prezzo scende (−0,43): contrario della fonte |
| Stagionalità della fascia oraria (4h) | 023 long | nettamente negativo (t −2,36) |
| Rottura di volatilità short (1h) | 026 | +0,20 ma t 1,07: il ribasso di fondo aiuta anche la (b) |
| Momento dentro il giorno, senza filtri (4h) | 028, 029 | +0,009 e +0,007, t 1,99 e 1,29 |
| Incrocio con la media a 50 (4h) | 030, 031 | il risultato (+0,25, +0,33) viene dall'uscita all'incrocio: la (b) con la stessa uscita fa uguale |
| Volume molto alto, compressione delle bande, illiquidità | scarti | sotto i 70 trade |

## Candidati della Fase 2 e perché sono caduti

* **016 — FIL in ritardo su BTC (long, 1h):** batte la (b) (t 2,35) e regge robustezza, timeframe
  vicini, ritardo; **cade a costi doppi** (R −0,004). Il vantaggio lordo (circa 0,14 R) è solo il
  doppio del costo di un giro con stop al 3%. È l'indizio più pulito della campagna: le (a) e (b)
  perdono, il segnale no.
* **024 — fascia oraria short (4h):** cade a costi doppi e al ritardo.
* **032-036, 038-039 — momento dentro il giorno con filtri (4h):** tutti battono la (b) (t fino a
  3,40) e reggono i costi doppi, ma **crollano col ritardo di una barra**, per costruzione: la
  regola punta sulla fascia 20-24 UTC e col ritardo il trade cade nella fascia dopo. Lo studio dei
  fallimenti dice che il segnale funziona solo quando anche BTC si muove nella stessa direzione
  durante la giornata e nei giorni volatili o con volume: un effetto di mercato, coerente con la
  fonte (Gao-Han-Li-Zhou), ma trovato con 8 ritocchi sugli stessi dati.
* **025 — rottura di volatilità dall'apertura del giorno (long, 1h):** l'unico che passa la Fase 4.
  La prova dello scettico mostra che il suo vantaggio sulle baseline è in gran parte un effetto
  dei costi: le baseline con lo stesso stop all'apertura del giorno entrano spesso con lo stop
  vicinissimo e pagano costi enormi in R. Contro ingressi casuali con stop di distanza normale il
  t scende a 1,38. In **validazione (2023) perde: R −0,117 su 87 trade**, in un anno in cui FIL
  raddoppia; il p-value contro la (b) (0,085) passa l'asticella solo per lo stesso effetto dei costi.

## Cosa abbiamo capito su FILUSDT

1. A orizzonti di ore, i movimenti di FIL che non sono accompagnati da BTC non continuano
   (S2 di 025: +0,30 R nei giorni di rottura anche di BTC, −0,11 nei giorni di rottura della sola
   FIL; studi dei fallimenti di 028 e 029).
2. Le inversioni di breve (24 ore, barre estreme, squilibrio degli ordini) non pagano su FIL nel
   2020-2022: dopo i movimenti estremi il prezzo prosegue o resta casuale.
3. Su FIL il ribasso di fondo del 2021-2022 fa guadagnare qualunque short con un'uscita che lascia
   correre: un risultato short va sempre letto contro la (b), mai contro zero.
4. Con stop del 3% i costi di un giro valgono circa 0,07 R: un vantaggio lordo sotto 0,15 R non
   regge i costi doppi.
