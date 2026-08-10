"""Livello AI: ipotesi, contesto e analisi. Mai decisioni di trade.

Il perimetro e' deliberato. Il sistema quantitativo (indicatori, gate,
walk-forward, esecuzione) resta deterministico e riproducibile; il modello
interviene dove una griglia non arriva:

  * hypotheses.py     - propone strategie CON un meccanismo dichiarato, invece
                        di combinare indicatori a caso;
  * universe_filter.py- decide su quali coin vale la pena spendere validazione;
  * analyst.py        - legge il vissuto e produce ipotesi da verificare.

In tutti e tre i casi la parola finale resta al GATE 1.
"""
