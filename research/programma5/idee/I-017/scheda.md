# I-017 — Il rimbalzo dopo i crolli, provato solo sul periodo recente

Scheda scritta il 18 ottobre 2026 **prima di aprire V e R per questa idea** (REGOLE.md, sezioni 6, 6bis e 6ter).

## Da dove viene, e perché la prova è solo R

Il rimbalzo dopo i crolli è il fenomeno più forte visto finora: su C in tutti e tre gli anni e su tutte le monete
(E-001, E-002, E-004), e su V positivo dopo i costi in tutte le sei varianti di I-010 e I-016, che però sono **bruciate**
(p sopra la soglia). Siccome conosco V per questo fenomeno, V qui è **costruzione** (regola 6ter, punto 3): la prova è
**R da solo** (2024-01-01 → 2026-09-30), una volta, con la soglia severa.

## Perché dovrebbe funzionare

Nei crolli rapidi la leva viene chiusa a forza (liquidazioni, margini): chi vende non sceglie il prezzo e lo porta sotto
quello che i compratori pagano con calma; finite le vendite forzate il prezzo risale. E-004 dice che i crolli che
rimbalzano sono quelli in cui il **perpetuo scende sotto lo spot** (la vendita è sulla leva): è il segno della vendita
forzata. Chi compra in quei momenti fornisce liquidità a chi è costretto a venderla, ed è pagato per questo.

## Le 7 candidate (tutte nel motore a minuti, `strumenti/idee_ore2.py`, `per_moneta_i017`)

| Candidata | Tipo | Regola | Da |
|---|---|---|---|
| c1 | limite | ordine d'acquisto a P·exp(−6σ) ogni ora, uscita 240 minuti dopo l'esecuzione | I-016a |
| c2 | limite | come c1 a P·exp(−4σ) | I-016b |
| c3 | crollo | z_24 ≤ −3, long 4 ore, pausa 24 | I-010c |
| c4 | crollo | z_4 ≤ −5, long 12 ore, pausa 12 | I-010a |
| c5 | sconto | z_4 ≤ −3 e premio nel 10% più basso delle 720 ore, long 4 ore, pausa 4 | E-004 (P3) |
| c6 | sconto | z_1 ≤ −3 e premio nel 10% più basso, long 4 ore, pausa 4 | E-004 (P3) |
| c7 | premio basso | premio nell'1% più basso delle 720 ore, long 4 ore, pausa 4 | E-004 (P1) |

Definizioni, costi (scarto doppio su tutti i trade a mercato; ordine limite: 0,02% all'ingresso e uscita a mercato con
scarto doppio), funding e caso come nelle schede di I-010 e I-016. Premio: indice del premio di Binance a 1 ora
(`motore5.premio`), percentile fra le 720 ore prima compreso il valore (almeno 500), noto alla fine dell'ora.

## La regola meccanica che sceglie le 3 da portare su R

Si calcolano le 7 candidate su C e su V. Fra quelle con il netto medio positivo **sia su C sia su V**, si prendono le 3
con il **t più alto** del netto su C e V insieme (gruppi di giorni di calendario, `strumenti/esplorazione.t_giorni`); a
parità, il netto medio più alto. La scelta si scrive in `scelta.json` e si committa prima di R.

## La prova su R (una volta)

Per le 3 scelte, giudicate insieme (`esame.json`): netto con l'intervallo al 95% sopra zero; **p a una coda ≤ 0,005 / 3**;
positivo in almeno 2 dei 3 anni; positivo a costi doppi; positivo togliendo il giorno migliore; positivo su almeno il 60%
delle monete con almeno 20 trade (almeno 3); almeno 100 trade.
