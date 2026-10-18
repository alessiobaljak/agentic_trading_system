# I-006 — Il prezzo intorno al regolamento del funding, quando il funding è estremo

Scheda scritta il 18 ottobre 2026 **prima di qualunque calcolo su questa idea** (REGOLE.md, sezione 6).

## Perché

Con il funding molto positivo, chi è long paga a ogni regolamento: una parte chiude poco prima per non pagare, e vende;
dopo il regolamento la pressione sparisce. Con il funding molto negativo succede il contrario. Il funding usato come
**segnale di direzione per giorni** è un'idea bruciata (`docs/storia/README.md`, sezione 3.2); qui è un effetto di poche ore
intorno all'istante del regolamento, che nessuna ricerca ha guardato.

## La regola

* **Il funding noto**: il tasso dell'ultimo regolamento prima dell'ingresso, riportato a 8 ore (tasso × 8 ÷ ore
  dell'intervallo).
* **Ingresso** W minuti prima del regolamento successivo (orario dell'intervallo della moneta), all'apertura del minuto, a
  mercato: **short** se il funding noto è ≥ S, **long** se è ≤ −S; **uscita** 5 minuti dopo il regolamento. Costi del
  programma senza scarto doppio; il funding del regolamento attraversato si paga o si incassa (è proprio quello da evitare:
  lo short con funding positivo lo incassa).

## Le varianti (3)

| Variante | Soglia S | Anticipo W |
|---|---|---|
| I-006a | 0,05% | 60 minuti |
| I-006b | 0,03% | 60 minuti |
| I-006c | 0,05% | 120 minuti |
