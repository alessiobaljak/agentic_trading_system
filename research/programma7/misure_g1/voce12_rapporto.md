# Voce 12: il lato venduto di G1 nel 2026 (12 novembre 2026)
Fonte: `voce12_venduto_2026.py` -> `voce12_risultati.json`. Motore `revisione_g1n/nucleo.py`, pesi di G1 (lati fissi 1 e 1), costi confermati,
1 gen - 4 ott di ogni anno. Somme dei rendimenti giornalieri (non composte), in punti percentuali del conto; lato venduto = prezzo + funding - spese.

| anno | prezzo | funding | spese | totale | piccole / medie / grandi | età <1a / 1-2a / >2a | 10 giornate-moneta peggiori |
|---|---|---|---|---|---|---|---|
| 2021 | -191,6 | +44,8 | -3,3 | -150,1 | -65,4 / -36,3 / -48,3 | -75,2 / -74,9 / 0 | -46,2 |
| 2022 | +81,5 | +3,9 | -2,6 | +82,8 | +22,6 / +29,4 / +30,8 | +19,2 / +52,1 / +11,5 | -11,3 |
| 2023 | -21,6 | +7,3 | -2,7 | -17,0 | -3,6 / -5,7 / -7,7 | +0,7 / -16,3 / -1,4 | -11,9 |
| 2024 | +7,4 | +13,6 | -3,2 | +17,7 | +18,5 / +2,0 / -2,9 | -7,3 / +0,7 / +24,3 | -17,3 |
| 2025 | +38,7 | +5,9 | -3,1 | +41,6 | +16,9 / +14,9 / +9,8 | +10,2 / +12,5 / +18,9 | -10,2 |
| 2026 | -20,4 | +9,4 | -2,5 | -13,4 | -14,5 / +1,8 / -0,7 | -10,0 / -4,6 / +1,2 | -19,7 |

2026: movimenti oltre +20% in un giorno su una moneta venduta: 176 giornate-moneta (2021: 85, 2024: 75, altri 22-48), prezzo -119,3 contro +99 di tutto il resto.
Mesi 2026: gen +14,3, feb +10,2, mar +5,4, apr -14,1, mag -0,2, giu +1,1, lug -2,6, ago -21,4, set -4,7, ott -1,3 (4 giorni).
Monete vendute in perdita nel 2026: 46% (2022 35%, 2023 54%, 2024 41%, 2025 37%).

Lettura: il funding del lato venduto nel 2026 (+9,4) è normale (2024 +13,6, 2023 +7,3): il guaio è tutto nel prezzo (-20,4).
Non è il mercato intero: le monete grandi (-0,7) e medie (+1,8) sono ferme, la perdita sta nel terzile piccolo (-14,5) e nelle monete con meno di 1 anno
sul perpetuo (-10,0). Le 10 peggiori giornate-moneta valgono -19,7, cioè più dell'intera perdita: senza di loro il lato venduto farebbe +6,3.
Ma non è un difetto solo del 2026: il 2021 fu molto peggio (-150) e il 2023 negativo; il 2026 ha il maggior numero di fiammate (176). E la perdita
è in pochi mesi (aprile, agosto). Verdetto: **difetto concentrato** (poche giornate di fiammate su monete piccole/giovani) dentro un anno con più fiammate del solito.
Limiti: monete in perdita 46% è nella norma; il terzile è calcolato fra le monete vendute del giorno (volume medio a 30 giorni); somme non composte.
Proposta (non provata): un tetto di peso per moneta venduta o un'uscita dopo +20% in un giorno sono idee collegate alla voce 13 e alla prova 152; vanno scritte come prova con regole prima.
