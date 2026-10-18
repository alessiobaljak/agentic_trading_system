# I-007 — Le altre monete dopo BTC, al minuto

Scheda scritta il 18 ottobre 2026 **prima di qualunque calcolo su questa idea** (REGOLE.md, sezione 6).

## Perché

Le grandi notizie arrivano prima su BTC, il mercato più liquido; le altre monete si adeguano con un ritardo di secondi o
minuti. Se una moneta non si è ancora mossa quando BTC è già esploso, c'è un movimento da prendere. Il «ritardo dopo BTC» a 1
ora e a 1 giorno è arrivato vicino alla soglia due volte senza passare (`docs/storia/06_ricerca_protocolli_2_4.md`, sezione
3.11, punto 8): qui è al minuto.

## La regola

* **BTC esplode** alla chiusura del minuto t: |r5 di BTCUSDT| > 8 volte la sua mediana delle 24 ore prima.
* **La moneta è indietro**: il suo r5 nello stesso minuto, nella direzione di BTC, è meno di un terzo di quello di BTC
  diviso il rapporto fra le due mediane di |r5| (cioè: si è mossa meno di un terzo di quanto «dovrebbe» per la sua
  volatilità normale).
* **Ingresso** sulla moneta nella direzione di BTC all'apertura del minuto t+1, a mercato; **uscita** a tempo; pausa di 60
  minuti per moneta; costi con scarto doppio; funding. Monete: le 11 del programma senza BTC.

## Le varianti (3)

| Variante | Uscita | Indietro di |
|---|---|---|
| I-007a | 5 minuti | meno di un terzo |
| I-007b | 15 minuti | meno di un terzo |
| I-007c | 15 minuti | meno di metà |
