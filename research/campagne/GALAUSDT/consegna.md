# Consegna della campagna GALAUSDT

Protocollo 4.5 (testo approvato il 2026-10-09 alle 12:06 UTC). Sessione di campagna unica, branch
`research/campagna/GALAUSDT`. Costruzione dal 2021-09-01 al 2023-04-19 (prima barra del last il
2021-09-18), validazione dal 2023-04-20 al 2023-12-31 (non usata).

## Esito

**Nessuna strategia valida trovata per questa moneta.**

Il budget di 30 varianti è stato usato per intero. Una sola variante è diventata candidato in Fase 2
(GALAUSDT-032, short quando il last è sopra il mark più del solito, 1 ora): batte nettamente la (a)
e la (b) con R medio dopo i costi di +0,013, ma a costi doppi perde (R medio -0,043) e cade in Fase 4.
Nessun candidato è arrivato alla validazione: il periodo di validazione non è mai stato toccato,
l'asticella non si applica (m = 0) e non ci sono p-value di validazione.

Osservato: nessuna delle 17 idee provate dà su GALAUSDT, in costruzione, un vantaggio che resti
dopo costi realistici raddoppiati. Inferito: i vantaggi lordi che compaiono (032; le varianti di
breve a 1 ora sul lato long, 011, 015, 017, con `t` contro il caso fra 1,3 e 1,9) sono dello stesso
ordine dei costi di un giro (0,03-0,10 R).

## Riepilogo delle idee provate (costruzione)

| Idea (fonte) | Varianti | Trade | R medio | `t` contro (a) | `t` contro (b) | Esito |
|---|---|---|---|---|---|---|
| I-01 momentum di serie temporale, 4h (Moskowitz-Ooi-Pedersen 2012; Liu-Tsyvinski 2018) | 001 long, 002 short | 109, 107 | +0,98, +0,29 | 1,11, 1,81 | 0,54, 0,64 | non nette; R di 001 tutto in 3 trade del 2021 (senza i 3 migliori -0,28) |
| I-02 Donchian delle tartarughe (Faith 2007) | 003, 004 su 4h scarti (41, 46); 025 long, 026 short su 2h | 89, 98 | +0,78, +0,01 | 1,01, 0,15 | 0,49, -0,53 | non nette; 025 senza i 3 migliori -0,48 |
| I-03 RSI(2) con filtro di tendenza, 4h (Connors-Alvarez 2008) | 005 scarto (53); 006 short; 027 ritirata | 120 | -0,14 | -1,08 | -1,43 | perde |
| I-04 falsa rottura e spazzata degli stop, 1h (Osler 2005) | 007 long, 008 short | 251, 254 | -0,14, -0,11 | 0,38, -0,73 | 0,84, -0,53 | non nette, perdono |
| I-05 funding estremo, 8h (Schmeling-Schrimpf-Todorov 2023) | 009 e 028 scarti (41, 65); 010 long | 125 | -0,00 | -0,07 | 0,37 | non netta |
| I-06 ritardo rispetto a BTC, 1h (Lo-MacKinlay 1990) | 011 long, 012 short; ritocchi 037, 038 | 162, 97, 111, 162 | +0,07, +0,00, +0,10, +0,05 | 1,91, 0,51, 1,79, 1,64 | 1,95, 0,55, 1,81, 1,62 | vicine ma non nette |
| I-07 barra stretta NR7, 4h (Crabel 1990) | 013 long, 014 short | 131, 137 | -0,33, +0,07 | -0,43, 1,83 | 0,01, 1,80 | non nette |
| I-08 movimento grande con volume alto, 1h (Llorente e altri 2002) | 015 long, 016 short | 163, 166 | +0,12, +0,03 | 1,84, 1,05 | 1,84, 0,92 | non nette |
| I-09 rottura di volatilità di Williams, 1h (Williams 1999) | 017 long, 018 short | 181, 216 | +0,14, +0,01 | 1,27, 0,21 | 1,29, -0,40 | non nette |
| I-10 lunedì, 1d (Caporale-Plastun 2019) | 019 long | 79 | -0,18 | -0,85 | -1,28 | perde |
| I-11 valore relativo rispetto a BTC, 4h (Gatev-Goetzmann-Rouwenhorst 2006) | 020 long, 021 short | 99, 82 | -0,30, -0,16 | -1,67, -0,59 | -1,76, -0,79 | perdono |
| I-12 reazione eccessiva giornaliera (Caporale-Plastun 2019) | 022, 023 scarti (20, 15) | — | — | — | — | non provabile: pochi trade |
| I-13 pompa e scarico, 1h (Kamps-Kleinberg 2018) | 024 short | 88 | -0,31 | -1,80 | -2,75 | perde, peggio del caso |
| I-14 periodicità oraria, 1h (Heston-Korajczyk-Sadka 2010) | 029 long, 030 short | 724, 993 | -0,07, -0,05 | -0,59, 0,72 | -0,52, 0,36 | perdono, come il caso |
| I-15 scarto fra last e mark, 1h (He-Manela-Ross-von Wachter 2022) | 031 long, **032 short** | 404, 325 | -0,03, **+0,01** | 1,10, **2,18** | 1,25, **2,22** | 032 candidato, cade ai costi doppi |
| I-16 numeri tondi, 1h (Osler 2003) | 033 short, 034 long | 383, 449 | -0,06, -0,19 | 0,50, -1,09 | -0,83, -1,06 | perdono |
| I-17 momentum dentro la giornata, 30m (Gao-Han-Li-Zhou 2018) | 035 long, 036 short | 315, 255 | -0,08, -0,08 | 0,07, 0,06 | 0,18, -0,05 | perdono, come il caso |

Numeri dal log (voci `risultato`), costi normali. Soglie di «nettamente» fra 2,0 e 2,6 secondo i
blocchi. Il buy and hold per anno è nel log accanto a ogni variante.

## Il candidato di Fase 2 e le sue verifiche

GALAUSDT-032 (regole in `candidati/GALAUSDT-032/regole.md`): 325 trade, R medio +0,013, profit
factor 1,06, drawdown 6,6%, R per anno 2021 +0,036, 2022 +0,004, 2023 +0,013; senza i 3 migliori
-0,005. Contro la (a): t 2,18 (soglia 2,05); contro la (b): media -0,050, t 2,22 (soglia 2,05),
percentile 99. Fase 4 (log, voci `GALAUSDT-032-V-*` e `GALAUSDT-032-FASE4`):

| Verifica | Esito |
|---|---|
| Robustezza ±20% (10 casi, tutti sopra i 70 trade) | superata: `t` positivo in 10 su 10, netto in 6 |
| Timeframe adiacenti (30m, 2h, parametri in barre convertiti) | superata: `t` 1,02 e 0,56, positivi |
| Stabilità per anno | superata: sopra la media della (b) nei 3 anni |
| Trade estremi | superata: -0,005 contro -0,050 della (b) |
| Regola intra-barra opposta | nessuna differenza (nessun target) |
| Ritardo di una barra | superata: `t` 1,72 contro 2,22 |
| Liquidazione | nessuna violazione |
| **Costi doppi** | **non superata**: R medio -0,043 (batte ancora la (b), t 2,25, ma perde) |

Rischi noti, se qualcuno volesse riprenderlo: lo stop è al tetto del 6% in 78 trade su 325 (lo stop
medio è del 4,1%); il vantaggio è di circa 0,06 R sopra il caso e i costi di un giro sono circa 0,05 R.

## Cose che non si fanno senza candidati

Validazione, asticella, criterio del vault, trade al mese attesi in paper e previsione per vault e
trasferimento: non applicabili. Per l'esecuzione nel bot: nessuna regola da tradurre.

## Varianti usate sul budget

30 varianti testate su 30: 28 da idee nuove (17 idee, 18 fonti), 2 ritocchi (037 e 038, entrambi
della famiglia di 011, nell'ordine del `t` contro la (b) dopo la nota di esaurimento delle idee).
28 famiglie. Scarti per pochi trade, senza budget: 7 (003, 004, 005, 009, 022, 023, 028). Una
variante ritirata prima del test per un errore di tempi (027, log GALAUSDT-N007). Nessuna famiglia
oltre i 5 ritocchi.

## Misure di processo

Dal log (date dall'orologio della macchina, `codice/misure.py`) e da `ipotesi.md`:

* Durata dalla prima all'ultima voce del log: dal 2026-10-09 18:24:49 alle 18:50:23 UTC
  (l'ultima voce è la nota di chiusura), 25,6 minuti; nessuna pausa, quindi 25,6 minuti anche senza
  pause. Il lavoro di lettura del
  protocollo e degli strumenti è prima della prima voce.
* Minuti per idea, dalla registrazione della prima variante all'ultimo risultato: I-01 1,6; I-02
  4,8; I-03 1,5; I-04 1,8; I-05 4,2; I-06 6,7 (con i due ritocchi); I-07 1,8; I-08 2,1; I-09 1,7;
  I-10 1,7; I-11 1,8; I-12 0 (solo scarti); I-13 1,9; I-14 0,6; I-15 0,8; I-16 0,6; I-17 1,2. I
  test sono veloci (pochi secondi a variante) e le varianti di un'idea sono state registrate tutte
  insieme e testate in parallelo: i minuti misurano il calcolo, non il ragionamento, che è in
  `ipotesi.md` ed è stato scritto prima delle registrazioni.
* Spiegazioni concorrenti scritte in `ipotesi.md` (Fase 1, punto 4): 10 per ognuna delle 17 idee
  (6 comuni a tutte, C1-C6, più 4 proprie dell'idea).
* Varianti diventate candidati in Fase 2: 1 da idee nuove (032), 0 da ritocchi.
* Varianti che hanno battuto nettamente la (a) e la (b) con R medio dopo i costi non positivo: 0.

## Errori e deviazioni da dichiarare

* GALAUSDT-027 ritirata: scritta in `ipotesi.md` 8 secondi dopo il risultato della prima variante
  testata della stessa idea (log, GALAUSDT-N007).
* Le idee I-14 - I-17 sono state scritte in `ipotesi.md` dopo aver letto i risultati delle varianti
  1-18 (dichiarato in `ipotesi.md`). Nessuna di esse è arrivata alla validazione.
* Quattro rifiuti del guardiano, tutti per la forma dei comandi (redirezioni, variabili della shell,
  cartella madre dei dati, file di uscita fuori da `research/`), registrati nel log (N002, N003, N004)
  o, per gli ultimi due (un `$` in una ricerca e un ciclo di attesa con `$(...)`), qui: rifatti nella
  forma ammessa, nessuno aggirato.
* `pytest` mancava nella macchina della sessione ed è stato installato per i test del guardiano.
