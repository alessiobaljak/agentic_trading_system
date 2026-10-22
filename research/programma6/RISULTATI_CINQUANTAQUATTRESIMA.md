# Programma 6 — risultati della cinquantaquattresima prova (lo scalping sul serio)

Regole in `CINQUANTAQUATTRESIMA.md` (scritte prima; Z1b aggiunto prima dei risultati, sezione 3bis); le scelte di calcolo non scritte nelle regole sono in testa a `cinquantaquattresima.py`. Le 30 monete più scambiate di ogni mese fra le 100 con le candele a 1 minuto, dal 2024-01-01 al 2026-10-15; 72 monete in tutto.

| Schema | Operazioni | Vinte | Almeno il TP1 | R medio netto (lordo) | Vinte, perse (R medio) | Costi (R) | p | Portafoglio: l'anno, Sharpe, discesa | Esito |
|---|---|---|---|---|---|---|---|---|---|
| Z1 | 5095 | 71% | 71% | -0.053 (-0.007) | +0.36, -1.05 | 0.046 | 1.0000 | -95.4%, -2.41, -96.5% | non valida |
| Z1b | 42824 | 70% | 71% | -0.052 (-0.007) | +0.37, -1.05 | 0.046 | 1.0000 | -798.3%, -6.38, -100.0% | non valida |
| Z2 | 71708 | 48% | 21% | -0.098 (-0.027) | +0.59, -0.72 | 0.070 | 1.0000 | -2493.6%, -13.35, -100.0% | non valida |
| Z3 | 8565 | 39% | 39% | -0.146 (+0.013) | +1.46, -1.18 | 0.159 | 1.0000 | -444.0%, -3.66, -100.0% | non valida |
| Z4 | 25761 | 31% | 22% | -0.338 (-0.082) | +1.45, -1.15 | 0.256 | 1.0000 | -3105.8%, -13.63, -100.0% | non valida |

* **Z1**: per anno 2024 -0.032 R (1830), 2025 -0.063 R (1825), 2026 -0.064 R (1440); uscite pareggio dopo il TP1 49%, stop 29%, obiettivi 22%, tempo 1%; metà -0.041 e -0.064; senza i 5 giorni migliori -0.057; Sharpe corretto rivisto 0.00 (65 gruppi), t -4.04; portafoglio: netto con l'intervallo non sopra zero.
* **Z1b**: per anno 2024 -0.047 R (18060), 2025 -0.061 R (14984), 2026 -0.048 R (9780); uscite pareggio dopo il TP1 48%, stop 29%, obiettivi 22%, tempo 1%; metà -0.056 e -0.048; senza i 5 giorni migliori -0.055; Sharpe corretto rivisto 0.00 (65 gruppi), t -10.69; portafoglio: netto con l'intervallo non sopra zero.
* **Z2**: per anno 2024 -0.095 R (25515), 2025 -0.091 R (25308), 2026 -0.108 R (20885); uscite tempo 52%, stop 27%, obiettivi 21%; metà -0.093 e -0.102; senza i 5 giorni migliori -0.100; Sharpe corretto rivisto 0.00 (65 gruppi), t -22.37; portafoglio: netto con l'intervallo non sopra zero.
* **Z3**: per anno 2024 -0.129 R (3113), 2025 -0.144 R (2970), 2026 -0.168 R (2482); uscite stop 61%, obiettivi 20%, pareggio dopo il TP1 20%, tempo 0%; metà -0.145 e -0.146; senza i 5 giorni migliori -0.155; Sharpe corretto rivisto 0.00 (65 gruppi), t -6.14; portafoglio: netto con l'intervallo non sopra zero.
* **Z4**: per anno 2024 -0.346 R (9592), 2025 -0.348 R (7654), 2026 -0.322 R (8515); uscite stop 58%, obiettivi 22%, tempo 20%; metà -0.351 e -0.326; senza i 5 giorni migliori -0.345; Sharpe corretto rivisto 0.00 (65 gruppi), t -22.83; portafoglio: netto con l'intervallo non sopra zero.

Soglia per operazione p ≤ 0.0020 (0,01 diviso i 5 schemi). R = guadagno in multipli del rischio fra entrata e stop (1% del capitale a operazione).

Nota: «l'anno» del portafoglio è la somma semplice dei guadagni a operazione (R per 1% del capitale) divisa per gli anni, non composta: con decine di migliaia di operazioni negative la somma scende sotto −100%, che nel conto vero vuol dire il capitale finito molto prima. La discesa (-100%) è invece calcolata sul capitale composto.
