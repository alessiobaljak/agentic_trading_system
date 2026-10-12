# XRPUSDT — Consegna della campagna (protocollo 4.5)

Sessione di campagna del 2026-10-09, branch `research/campagna/XRPUSDT`. Log: `log.jsonl`;
ipotesi: `ipotesi.md`; dati: `fase0_dati.md`; codice: `codice/`.

## Esito in una riga

**Nessuna strategia valida trovata per questa moneta.** Un solo candidato in costruzione
(XRPUSDT-V21r3), che in validazione ha fatto 5 trade: sotto i 30 minimi, esito «non si sa»,
non passa l'asticella (provvisorio, lo conferma il coordinamento al Passo 4). Nessun candidato va
al vault.

## Il candidato XRPUSDT-V21r3

### Regole complete

In `candidati/XRPUSDT-V21r3/regole.md`. In breve: XRPUSDT, candele da 1 ora, long. Alla chiusura
della barra i, se il last chiude oltre lo 0,20% sotto il mark price (close last / close mark − 1 <
−0,0020) e la barra non è scesa oltre il 10%, si compra all'apertura della barra dopo. Stop a
min(1,5 ATR14, 6%) sotto la chiusura del segnale, nessun target, uscita a tempo dopo 4 barre.
Rischio 1% per trade, leva massima 2, isolated (regole del bot).

**Motivo economico**: il premio del perpetuo sull'indice rientra (He, Manela, Ross e von Wachter,
«Fundamentals of Perpetual Futures», 2022); un last molto sotto il mark è pressione di vendita
concentrata sul perpetuo, che finisce. Il filtro sui crolli toglie i casi in cui il premio negativo
fa parte di un crollo vero.

### Metriche, separate per periodo

| | Costruzione (2020-01-01 → 2022-10-18) | Validazione (2022-10-19 → 2023-12-31) |
|---|---|---|
| Trade | 97 (2020: 84, 2021: 8, 2022: 5) | **5** (2022: 1, 2023: 4) |
| R medio a trade | +0,167 | −0,574 |
| R medio per anno | 2020 +0,178; 2021 +0,188; 2022 −0,053 | 2022 +0,509; 2023 −0,845 |
| R medio senza i 3 migliori | +0,059 | — |
| Profit factor | 1,48 | 0,15 |
| Drawdown massimo | 8,6% | 3,4% |
| Rendimento per anno | 2020 +15,7%; 2021 +1,5%; 2022 −0,3% | 2022 +0,5%; 2023 −3,4% |
| Baseline (a): media, `t`, netta | −0,090; 2,43; sì | −0,131; −1,21; no |
| Baseline (b): media, `t`, netta | −0,078; 2,33 (soglia 2,18, 16 blocchi); sì | −0,026; −0,44; no |
| Percentile fra le simulazioni casuali | 100 | — |
| Buy and hold (long / short) | 2020 +11% / −12%; 2021 +277% / −278%; 2022 −44% / +44% | — |

Trade ridotti per il tetto di leva: 0 in costruzione, 0 in validazione. Rendimento medio di BTC
nella finestra dei trade: +0,01% (XRP +0,55%): non è il mercato.

### Verifiche della Fase 4 (costruzione)

| Verifica | Esito |
|---|---|
| Robustezza (±20% su soglia del premio, crollo massimo, multiplo dell'ATR, periodo dell'ATR, tenuta) | superata: 9 casi su 10 contano (soglia 0,0024: 55 trade, sotto il minimo); `t` contro la (b) sempre positivo (1,95-3,09), netta in 7 |
| Timeframe adiacenti | superata: 30m `t` 1,60; 2h 58 trade, sotto il minimo (dichiarato) |
| Stabilità temporale | superata per la lettera della regola, ma solo il 2020 ha almeno 10 trade |
| Pochi trade estremi | superata: senza i 3 migliori +0,059 contro −0,078 della (b) |
| Regola intra-barra opposta | nessuna differenza (nessun target) |
| Ritardo di una barra | superata: `t` 1,48 (metà di 2,33 = 1,165) |
| Liquidazione | 0 violazioni |
| Costi doppi | superata: `t` 2,59 contro la (b) a costi doppi, R +0,110 |
| Fase 5, slippage 0,10% per lato | regge: R +0,103, `t` 2,56 |

### Rischi noti

* **Adattamento**: è il terzo ritocco della famiglia V21; le due soglie (crollo 10%, premio 0,20%)
  sono state scelte sui fallimenti degli stessi dati di costruzione. La variante d'origine aveva
  `t` 1,77.
* **Un solo regime**: 84 trade su 97 nel 2020, quando il volume era 22-162 milioni al giorno e i
  premi grandi frequenti. Dal 2021 la condizione scatta di rado (13 volte in 22 mesi di costruzione,
  5 in 14 mesi e mezzo di validazione).
* **Tetto dello stop**: 21 trade hanno lo stop al tetto del 6% della chiusura del segnale; misurato
  dal riempimento vero la distanza supera di poco il 6%, e il controllo del bot potrebbe rifiutarli.

### Budget, asticella, vault

* Varianti usate: **30 su 30**; 27 da idee nuove, **3 ritocchi** (tutti della famiglia V21);
  **27 famiglie**. Scarti sotto i 70 trade (non contano nel budget): 7 (V05, V06, V08, V16, V17,
  V16b, V17b).
* Validazione: 5 trade, sotto i 30 minimi: p-value 1 per regola; Benjamini-Hochberg al 10% con
  m = 1: **non passa** (esito provvisorio, Passo 4).
* Criterio del vault (non si applica: il candidato non va al vault): profit factor dopo i costi
  almeno 1,10, almeno 30 trade, rendimento totale positivo, R medio sopra il 90° percentile delle
  entrate casuali con la stessa uscita.

### Paper e bot

* Trade al mese attesi dalla frequenza del backtest: in costruzione 97 in 33,5 mesi ≈ 2,9 al mese,
  ma dal 2021 ≈ 0,4 al mese (13 in 22 mesi), in validazione 0,35 al mese. Per arrivare a 50 trade
  di paper servirebbero più di 10 anni al ritmo recente: oltre i 12 mesi di `paper_durata_massima_mesi`.
* Il bot oggi non può eseguirlo così com'è: serve il percorso «coppia del protocollo» fuori dal
  gate (`config/regole_dimensione.md`, punto 4) e la chiusura oraria del mark price accanto a quella
  del last (il bot legge il mark solo dal `premiumIndex` istantaneo). Timeframe 1h e tenuta di 4
  barre sono già nelle possibilità del bot.

### Previsione per il vault e il trasferimento

Non va al vault. Se ci andasse, la previsione sarebbe: meno di 30 trade in 33 mesi (esito «non si
sa») e, nel trasferimento, segnali concentrati sulle monete e sui periodi a volume basso.

## Le idee provate (tutte su costruzione)

| Variante | Idea, direzione, timeframe | Trade | R medio | `t` contro la (b) | Esito |
|---|---|---|---|---|---|
| V01 | momentum 7 giorni, long, 1d | 125 | +0,091 | 0,34 | no |
| V02 | momentum 7 giorni, short, 1d | 126 | −0,018 | 0,05 | no |
| V03 | rientro dopo ora estrema con volume, long, 1h | 298 | −0,145 | −0,84 | no |
| V04 | idem, short | 289 | −0,111 | −0,64 | no |
| V05 / V06 | sovrareazione giornaliera 1,5 σ | 66 / 53 | — | — | scarti |
| V05b | sovrareazione 1,0 σ, long, 1d | 103 | −0,064 | −0,28 | no |
| V06b | sovrareazione 1,0 σ, short, 1d | 110 | −0,173 | −1,43 | no |
| V07 | funding ≥ 0,05%, short, 8h | 144 | −0,128 | −0,52 | no |
| V08 | funding ≤ −0,02% | 42 | — | — | scarto |
| V08b | funding ≤ −0,01%, long, 8h | 78 | +0,146 | 0,92 | no |
| V09 | lunedì, long, 1d | 140 | +0,098 | 1,11 | no |
| V10 | BTC guida, long, 1h | 363 | −0,045 | 0,91 | no |
| V11 | BTC guida, short, 1h | 202 | −0,136 | −1,20 | no |
| V12 | rottura del canale di 20 barre, long, 4h | 96 | +0,417 | 0,97 | no |
| V13 | idem, short | 90 | −0,057 | −0,09 | no |
| V14 | RSI(2) nel trend, long, 4h | 136 | −0,096 | −1,11 | no |
| V15 | idem, short | 161 | +0,042 | 1,61 | no |
| V16 / V17, V16b / V17b | compressione delle bande | 28 / 26, 65 / 63 | — | — | scarti |
| V18 | squilibrio degli ordini aggressivi, long, 1h | 249 | −0,028 | 0,95 | no |
| V19 | idem, short | 1041 | −0,090 | −0,77 | no |
| V20 | premio last/mark > 0,15%, short, 1h | 367 | −0,075 | −0,13 | no |
| V21 | premio last/mark < −0,15%, long, 1h | 238 | +0,022 | 1,77 | no |
| V22 | numeri tondi, long, 1h | 1717 | −0,061 | 0,86 | no |
| V23 | numeri tondi, short, 1h | 1677 | −0,065 | 0,05 | no |
| V24 | prima mezz'ora → ultima, long, 30m | 513 | −0,130 | −1,23 | no |
| V25 | idem, short | 476 | −0,058 | 1,75 | no |
| V26 | forza relativa contro BTC, long, 1d | 120 | +0,026 | 0,00 | no |
| V27 | idem, short | 144 | −0,081 | −0,48 | no |
| V28 | rottura dell'intervallo d'apertura UTC, long, 1h | 621 | −0,048 | 0,10 | no |
| V29 | idem, short | 658 | −0,036 | 0,37 | no |
| V21r1 | V21 + niente ingressi dopo crolli oltre il 10% | 227 | +0,044 | 2,04 | no (soglia non superata) |
| V21r2 | V21r1 con tenuta 8 | 203 | +0,059 | 1,81 | no |
| V21r3 | V21r1 con premio sotto −0,20% | 97 | +0,167 | 2,33 | **candidato**; validazione: 5 trade |

## Misure di processo

Ricavate dal log con `codice/misure.py`; le date sono dell'orologio della macchina.

* Durata dalla prima voce (12:22:28 UTC) all'ultima voce prima di questa consegna (13:02 UTC):
  circa 40 minuti, nessuna pausa registrata. Nota: l'orologio della macchina ha segnato tempi che
  sembrano brevi rispetto al lavoro fatto; li riporto come misurati.
* Minuti dalla registrazione della prima variante all'ultimo risultato, per idea: I-01 0,2; I-02 0,6;
  I-03 0,0; I-04 4,9; I-05 0,0; I-06 0,6; I-07 0,1; I-08 0,2; I-09 (solo scarti); I-10 0,6;
  I-11 6,6 (con i 3 ritocchi); I-12 0,8; I-13 1,3; I-14 0,1; I-15 0,6.
* Spiegazioni concorrenti scritte in `ipotesi.md`: 10 per ognuna delle 15 idee (le 7 comuni con la
  previsione propria dell'idea, più 3 proprie). Alcune righe delle 7 comuni non hanno una previsione
  propria scritta (trattino): valgono la previsione e la smentita della sezione comune.
* Varianti diventate candidati in Fase 2: 0 da idee nuove, 1 da ritocchi (V21r3).
* Varianti che hanno battuto nettamente la (a) e la (b) con R medio dopo i costi non positivo: 0.
