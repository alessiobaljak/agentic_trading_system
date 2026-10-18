# I-002 — Ritorno dopo le salite estreme fatte di short liquidati

Scheda scritta il 18 ottobre 2026 **prima di qualunque calcolo su questa idea** (REGOLE.md, sezione 6).

## Perché

È lo specchio di I-001: in una salita violenta chi è short a leva viene liquidato, gli acquisti forzati spingono il prezzo
sopra il livello che i venditori accettano, e finite le liquidazioni il prezzo torna indietro. Se è così, le salite che
tornano indietro di più sono quelle in cui l'interesse aperto **cala** (short chiusi a forza). La prima analisi dello
scalping (`research/scalping/risultati.md`) dopo le salite estreme, senza condizioni, **non** ha visto un ritorno (−0,22%
al netto a 60 minuti per chi va contro): l'idea parte con un'indicazione contraria, ed è dichiarato.

## La regola

Come I-001 (`../I-001/scheda.md`), con il segno rovesciato:
* **Salita** alla chiusura del minuto t: ln(chiusura_t / chiusura_{t−5}) **maggiore di +L volte** la mediana di |r5| delle
  24 ore prima.
* **Short liquidati**: variazione dell'interesse aperto fra le ultime due rilevazioni note nel 5% più negativo dei 30
  giorni prima.
* **Ingresso**: short all'apertura del minuto t+1, a mercato; **uscita** alla chiusura del 60° minuto; pausa di 60 minuti
  per moneta; costi del programma con lo scarto doppio; funding.

## Le varianti (3)

| Variante | L | Interesse aperto |
|---|---|---|
| I-002a | 16 | 5% più negativo |
| I-002b | 8 | 5% più negativo |
| I-002c | 16 | nessuna condizione |
