# Programma 7 — quarantanovesima prova: il resto dello scalping del documento, divergenze, candele e intervallo (SK2)

Scritto il 26 ottobre 2026, alle 08:24 UTC, **prima di qualunque calcolo**. Completa la prova 108 (`QUARANTASEIESIMA.md`) con le strategie del
documento del proprietario del 26 ottobre che lì non c'erano: la 8 (divergenze), la 11 (candele: engulfing e pin bar) e la 9 (il trading
nell'intervallo). **Non si fanno**, con il perché: la 7 (Keltner + ALMA + stocastico) e la 13 (il ribaltamento supporto-resistenza) sono
varianti della 4 (Bollinger) e della 9 (rottura) già provate nella 108, che prima dei costi facevano zero.

## 1. Perché, e il dubbio

Il documento le presenta come lo scalping «senza indicatori ritardatari»: la forma delle candele e i livelli. **Il dubbio scritto prima**:
la prova 108 ha mostrato che a 1-5 minuti nove regole classiche fanno zero prima dei costi; non c'è un motivo per cui queste debbano fare
diverso. Probabilità molto bassa: si fanno per chiudere il documento.

## 2. Le regole (stesse monete, periodo, costi, uscita ed esame della prova 108)

BTC, ETH, SOL, XRP, DOGE, BNB; dal 1° gennaio 2024 al 30 settembre 2026; a 1 e 5 minuti; entrata all'apertura della candela dopo il segnale,
stop a 1 ATR(14) e obiettivo a 2 ATR(14), al massimo 60 candele, salvo dove scritto.

1. **Divergenza dell'RSI(14)**: long quando il minimo della candela è il più basso delle ultime 5 e sotto il minimo delle candele da 20 a 5 prima,
   mentre l'RSI è sopra l'RSI della candela di quel minimo vecchio; short allo specchio con i massimi.
2. **Engulfing**: long quando dopo tre chiusure in discesa una candela verde ha il corpo che contiene tutto il corpo rosso della candela prima;
   short allo specchio.
3. **Pin bar**: long quando la candela ha l'ombra bassa almeno doppia del corpo, chiude nel terzo alto e il minimo è il più basso delle 20;
   short allo specchio (ombra alta, terzo basso, massimo delle 20).
4. **Intervallo** (uscita del documento): quando le ultime 60 candele stanno in un intervallo largo meno dell'1,5%, long al tocco del minimo
   dell'intervallo con obiettivo al massimo e stop sotto il minimo di un quarto della larghezza; short allo specchio.

4 regole × 2 tempi = **8 varianti**: nel conto **206**. Esame per ognuna: p ≤ 0,01/8, positiva in ogni anno e su almeno 4 monete.
