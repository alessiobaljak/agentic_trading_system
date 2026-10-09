# FTMUSDT — consegna (Passo 3, protocollo 4.5)

## Esito

**Nessuna strategia valida trovata per questa moneta.** Nessuna delle 30 varianti testate
è diventata candidato in costruzione (battere nettamente la (a) e la (b) con R medio dopo i
costi positivo). Non ci sono quindi candidati, né verifiche di Fase 4, né validazione,
né p-value per l'asticella: per FTMUSDT m = 0. Il periodo di validazione (2022-12-31 →
2023-12-31) non è mai stato usato da una variante.

Il budget è usato per intero: 30 varianti, di cui 26 da 15 idee nuove con fonte e 4
ritocchi. Il dettaglio di ogni numero è nel log (`log.jsonl`); le ipotesi, con le fonti e
le spiegazioni concorrenti, sono in `ipotesi.md`; il codice è in `codice/`.

## Periodi e dati

* Costruzione: dal 2020-09-01 al 2022-12-30 (851 giorni). Validazione: dal 2022-12-31
  al 2023-12-31 (`periodi_campagna`, log FTMUSDT-N003, scritto prima dei prezzi).
* Primo dato 2020-09-24; i mesi da settembre a dicembre 2020 sono sotto la liquidità
  minima: in costruzione i trade entrano solo nel 2021 e nel 2022 (`fase0_dati.md`).
* Costi: commissione 0,05% e slippage 0,05% per lato (fascia della scheda, prudente per
  il 2021-2022, quando il volume era il doppio del 2023), funding storico a ogni
  settlement (sempre a 8 ore). Rischio 1% a trade, leva massima 2, margine isolato,
  stop sul last, liquidazione sul mark.
* Controllo positivo degli strumenti (nota FTMUSDT-N-CONTROLLO-ESITO): una strategia che
  guarda di proposito la barra dopo batte nettamente (a) e (b) (`t` contro la (b) 55,4) e
  col ritardo di una barra scende a 3,5: gli strumenti vedono un vantaggio vero e
  segnalano lo sguardo al futuro.

## Le varianti (solo costruzione)

R medio dopo i costi per trade; «(a) t» e «(b) t» sono i `t` di `contro_baseline`; «soglia»
è quella della (b); «percentile» è la quota di simulazioni casuali sotto il candidato
(indizio, non prova). Anno = anno di uscita del trade.

| id | idea | tf | dir. | ritocco di | trade | R medio | senza 3 migliori | R 2021 | R 2022 | (a) t | (b) media | (b) t | soglia | percentile |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FTMUSDT-001 | I-01 | 1d | long |  | 73 | 0.161 | 0.037 | 0.323 | -0.046 | 0.53 | 0.088 | 0.62 | 2.07 | 84.0 |
| FTMUSDT-002 | I-01 | 1d | short |  | 77 | 0.042 | -0.003 | -0.046 | 0.104 | 1.32 | -0.050 | 1.60 | 2.07 | 98.0 |
| FTMUSDT-003 | I-02 | 4h | long |  | scarto (62) | | | | | | | | | |
| FTMUSDT-004 | I-02 | 4h | short |  | scarto (62) | | | | | | | | | |
| FTMUSDT-005 | I-03 | 1h | long |  | 82 | -0.119 | -0.171 | -0.027 | -0.181 | -0.78 | -0.032 | -1.02 | 2.18 | 14.0 |
| FTMUSDT-006 | I-03 | 1h | short |  | 101 | -0.153 | -0.197 | -0.215 | -0.045 | -1.24 | -0.052 | -1.19 | 2.28 | 7.5 |
| FTMUSDT-007 | I-04 | 8h | short |  | scarto (58) | | | | | | | | | |
| FTMUSDT-008 | I-04 | 8h | long |  | 81 | -0.010 | -0.095 | 0.298 | -0.126 | -0.02 | -0.000 | -0.12 | 2.07 | 44.0 |
| FTMUSDT-009 | I-05 | 1d | long |  | 101 | -0.013 | -0.048 | 0.017 | -0.044 | -0.47 | 0.003 | -0.37 | 2.03 | 31.5 |
| FTMUSDT-010 | I-06 | 1h | long |  | 227 | 0.028 | -0.042 | 0.144 | -0.133 | 0.72 | -0.063 | 0.96 | 2.05 | 89.0 |
| FTMUSDT-011 | I-06 | 1h | short |  | 219 | -0.010 | -0.069 | -0.060 | 0.033 | 0.62 | -0.011 | 0.01 | 2.02 | 49.5 |
| FTMUSDT-012 | I-07 | 4h | long |  | 86 | 0.029 | 0.005 | 0.118 | -0.200 | 1.09 | -0.019 | 1.11 | 2.06 | 88.5 |
| FTMUSDT-013 | I-07 | 4h | short |  | 108 | 0.005 | -0.020 | -0.125 | 0.072 | 0.75 | -0.026 | 0.75 | 2.07 | 82.0 |
| FTMUSDT-014 | I-08 | 1h | long |  | 173 | -0.008 | -0.041 | -0.021 | 0.010 | 1.02 | -0.043 | 0.90 | 2.06 | 82.5 |
| FTMUSDT-015 | I-08 | 1h | short |  | 100 | -0.092 | -0.127 | -0.117 | -0.076 | -0.62 | -0.052 | -0.71 | 2.08 | 24.5 |
| FTMUSDT-016 | I-09 | 4h | long |  | scarto (43) | | | | | | | | | |
| FTMUSDT-017 | I-09 | 4h | short |  | scarto (39) | | | | | | | | | |
| FTMUSDT-018 | I-10 | 1h | short |  | 164 | 0.007 | -0.031 | -0.030 | 0.042 | 1.27 | -0.054 | 1.13 | 2.05 | 89.5 |
| FTMUSDT-019 | I-10 | 1h | long |  | 182 | -0.069 | -0.105 | -0.073 | -0.066 | -0.47 | -0.042 | -0.58 | 2.13 | 25.0 |
| FTMUSDT-020 | I-11 | 30m | long |  | 381 | -0.078 | -0.090 | -0.069 | -0.085 | -0.32 | -0.069 | -0.44 | 2.03 | 30.5 |
| FTMUSDT-021 | I-11 | 30m | short |  | 332 | -0.047 | -0.056 | -0.046 | -0.048 | 1.20 | -0.070 | 1.17 | 2.01 | 88.0 |
| FTMUSDT-022 | I-12 | 1d | long |  | 74 | -0.021 | -0.097 | 0.081 | -0.079 | -0.79 | 0.088 | -1.35 | 2.11 | 6.0 |
| FTMUSDT-023 | I-13 | 4h | long |  | scarto (53) | | | | | | | | | |
| FTMUSDT-024 | I-13 | 4h | short |  | scarto (53) | | | | | | | | | |
| FTMUSDT-025 | I-14 | 1d | long |  | scarto (23) | | | | | | | | | |
| FTMUSDT-026 | I-02 | 2h | long |  | 134 | 0.249 | -0.005 | 0.740 | -0.288 | 0.79 | 0.040 | 0.87 | 2.13 | 95.0 |
| FTMUSDT-027 | I-02 | 2h | short |  | 132 | 0.005 | -0.115 | -0.177 | 0.171 | 0.79 | -0.053 | 0.46 | 2.08 | 75.0 |
| FTMUSDT-028 | I-09 | 2h | long |  | 94 | -0.200 | -0.327 | -0.106 | -0.298 | -1.46 | -0.008 | -1.57 | 2.09 | 2.5 |
| FTMUSDT-029 | I-09 | 2h | short |  | 94 | -0.022 | -0.196 | -0.182 | 0.107 | 0.18 | -0.014 | -0.06 | 2.09 | 50.5 |
| FTMUSDT-030 | I-15 | 1h | long |  | 1846 | -0.041 | -0.046 | -0.013 | -0.085 | 0.66 | -0.046 | 0.36 | 2.02 | 67.0 |
| FTMUSDT-031 | I-15 | 1h | short |  | 1854 | -0.053 | -0.058 | -0.065 | -0.036 | 0.22 | -0.052 | -0.09 | 2.01 | 46.0 |
| FTMUSDT-032 | I-13 | 2h | long |  | 115 | 0.515 | 0.079 | 1.012 | -0.046 | 1.66 | 0.164 | 1.12 | 2.15 | 100.0 |
| FTMUSDT-033 | I-13 | 2h | short |  | 116 | 0.039 | -0.072 | -0.185 | 0.295 | 0.59 | 0.021 | 0.15 | 2.12 | 61.5 |
| FTMUSDT-034 | I-14 | 4h | long |  | 159 | -0.126 | -0.153 | -0.103 | -0.143 | -1.99 | -0.022 | -2.08 | 2.09 | 0.0 |
| FTMUSDT-035 | I-01 | 1d | short | FTMUSDT-002 | 78 | 0.023 | -0.022 | -0.106 | 0.122 | 1.13 | -0.050 | 1.14 | 2.07 | 91.5 |
| FTMUSDT-036 | I-01 | 1d | short | FTMUSDT-002 | 109 | 0.033 | 0.008 | -0.031 | 0.076 | 1.47 | -0.057 | 2.22 (netta) | 2.05 | 99.0 |
| FTMUSDT-037 | I-01 | 1d | short | FTMUSDT-036 | 83 | 0.000 | -0.041 | -0.114 | 0.080 | 0.89 | -0.056 | 1.30 | 2.06 | 93.0 |
| FTMUSDT-038 | I-01 | 1d | short | FTMUSDT-036 | 109 | -0.051 | -0.080 | -0.133 | -0.007 | 0.17 | -0.057 | 0.12 | 2.05 | 57.5 |

Idee: I-01 momento di 1-4 settimane; I-02 rottura del canale di Donchian; I-03 ritorno
dopo un movimento estremo di 3 ore; I-04 funding estremo; I-05 lunedì; I-06 rottura di
volatilità della giornata; I-07 RSI a 2 dentro il trend; I-08 BTC prima di FTM; I-09
compressione delle bande; I-10 premio del perpetuo sul mark; I-11 prima mezz'ora →
ultima mezz'ora; I-12 volatilità bassa; I-13 incrocio di medie 10/50; I-14 calo con
volume alto; I-15 attraversamento dei numeri tondi.

## Cosa si è capito (osservato, inferito, ipotizzato)

* **Osservato:** nessuna variante batte nettamente entrambe le baseline. L'unica netta
  contro la (b), FTMUSDT-036 (`t` 2,22, soglia 2,05), viene dal secondo ritocco della
  famiglia più vicina, non batte la (a) (`t` 1,47), guadagna solo nel primo semestre 2022
  (+0,15 R) e i due ritocchi che ne seguono il meccanismo peggiorano (`t` 1,30 e 0,12).
* **Inferito:** è fortuna più il ribasso del 2022. Con 30 confronti contro la (b) la
  probabilità di almeno un «netta» per caso è circa il 50% al tasso nominale e circa il
  12% al tasso misurato dalla prova a placebo; scegliere la famiglia più vicina la alza.
* **Osservato:** gli R medi alti di alcune varianti di trend (FTMUSDT-001 +0,16, 026
  +0,25, 032 +0,52) vengono dal rialzo del 2021 e da pochi trade enormi: senza i 3
  migliori scendono a +0,04, −0,01 e +0,08, e la (b) nella stessa direzione guadagna
  anch'essa (+0,09, +0,04, +0,16).
* **Osservato:** i due test di inversione dopo un movimento forte vanno peggio del caso:
  ritorno dopo l'estremo di 3 ore (FTMUSDT-005 e 006, `t` −1,02 e −1,19) e calo a 4 ore con
  volume alto (FTMUSDT-034, `t` −2,08, percentile 0). **Ipotizzato:** su FTM nel 2021-2022
  i movimenti forti con volume alto continuano nelle ore successive invece di tornare
  indietro (cascate di liquidazioni più che offerta di liquidità). Non è stato testato
  come idea a sé: il budget era finito ed è un'idea nata dai risultati, che avrebbe
  bisogno di una fonte.
* **Osservato:** le idee di calendario (lunedì, ultima mezz'ora), di posizionamento
  (funding, premio sul mark), di BTC che anticipa FTM e dei numeri tondi sono tutte vicine
  al caso (`t` contro la (b) fra −0,7 e 1,2).

## Misure di processo

Ricavate da `log.jsonl` e `ipotesi.md` con `codice/misure.py`; le date del log sono
dell'orologio della macchina.

* Durata dalla prima all'ultima voce del log: circa 26 minuti (dalle 18:24:32 alle 18:50
  UTC del 9 ottobre 2026), senza pause; non verificabile con un orologio indipendente.
* Varianti testate 30 (26 da idee nuove, 4 ritocchi), famiglie 26, scarti 8 (senza
  budget). Previsioni dichiarate corrette in 23 casi su 30.
* Per idea: minuti dalla registrazione della prima variante all'ultimo risultato
  (i test sono stati lanciati a lotti, in serie) e spiegazioni concorrenti scritte in
  `ipotesi.md` (le 8 comuni più quelle dell'idea):

| idea | varianti testate | scarti | minuti | spiegazioni concorrenti |
|---|---|---|---|---|
| I-01 | 6 (4 ritocchi) | 0 | 7 | 12 |
| I-02 | 2 | 2 | 4 | 13 |
| I-03 | 2 | 0 | 0 | 13 |
| I-04 | 1 | 1 | 0 | 13 |
| I-05 | 1 | 0 | 0 | 13 |
| I-06 | 2 | 0 | 0 | 13 |
| I-07 | 2 | 0 | 0 | 13 |
| I-08 | 2 | 0 | 0 | 13 |
| I-09 | 2 | 2 | 3 | 13 |
| I-10 | 2 | 0 | 0 | 13 |
| I-11 | 2 | 0 | 1 | 13 |
| I-12 | 1 | 0 | 0 | 13 |
| I-13 | 2 | 2 | 2 | 13 |
| I-14 | 1 | 1 | 2 | 13 |
| I-15 | 2 | 0 | 1 | 13 |

* Varianti diventate candidati in Fase 2: 0 da idee nuove, 0 da ritocchi.
* Varianti nette contro la (a) e la (b) con R medio dopo i costi non positivo: 0.
* Varianti nette solo contro la (b): 1 (FTMUSDT-036, ritocco).

## Rischi e limiti noti

* **Stop oltre il tetto del bot.** Le varianti a 1d hanno stop in ATR giornalieri con
  distanza mediana del 31-33%: il bot (stop massimo 6%) non le eseguirebbe così come sono;
  due trade di FTMUSDT-035 violano anche il margine dalla liquidazione. Non cambia
  l'esito (nessun candidato).
* **Due soli anni in costruzione** (2021 rialzo, 2022 ribasso): ogni idea di trend si
  confonde col trend dell'anno; la (b) lo assorbe, ma con poca potenza.
* **Fonti deboli:** la fonte crypto di I-08 trova una causalità in gran parte nei due
  versi; I-11 definisce la giornata col volume, qui è quella UTC.
* **Conoscenza successiva:** chi scrive sa che FTM è stata poi sostituita da un'altra
  moneta della stessa rete (dopo il 2023). Nessuna scelta ne dipende; lo si dichiara.
* **Rifiuti del guardiano:** otto, tutti per la forma dei comandi (cartella madre, file
  temporanei, testo con percorsi, sed, awk, messaggio di commit con -m, asterisco),
  registrati nel log e mai aggirati.

## Previsione per il vault e il trasferimento

Nessun candidato: niente da giudicare nel vault né da trasferire.
