# Consegna della campagna BTC51 (Passo 4)

Scritto dalla sessione di ricerca il 17 ottobre 2026, dopo il sì del proprietario («procedi con la consegna»,
riportato dal coordinamento), **prima dell'apertura del vault**. Il vault resta chiuso: si apre solo con la frase
«APRI IL VAULT 3» (Passo 5, coordinamento).

- **Varianti usate:** 40 su 40 (V-001 … V-040, log `log.jsonl`; idee in `ipotesi.md`).
- **Candidati che hanno superato la validazione:** uno, **V-020**. Nessun altro candidato è stato costruito
  (V-030 ha superato la Fase 2 ma non la Fase 4; regola 9: dopo la validazione non si costruisce niente).

## 1. V-020 — specifica completa

```json
{"timeframe": "1h", "direzione": "long",
 "filtro": {"codice": "F6", "giorni": "feriali"},
 "ingresso": {"codice": "E11", "soglia": 0.0},
 "conferma": null,
 "tipo_ingresso": {"codice": "M"},
 "stop": {"codice": "S1", "k": 2.0},
 "uscite": [{"codice": "U2", "n": 24}]}
```

- **Timeframe:** candele da 1 ora (last price di BTCUSDT perpetuo, Binance USDS-M).
- **Direzione:** solo long.
- **Filtro (F6):** la candela del segnale è di un giorno feriale (lunedì-venerdì, UTC).
- **Ingresso (E11):** alla chiusura della prima candela che inizia dopo un regolamento del funding (00:00, 08:00,
  16:00 UTC), l'ultimo funding regolato è **sotto 0,00%** per 8 ore.
- **Conferma:** nessuna.
- **Tipo d'ingresso (M):** a mercato, all'apertura della candela successiva al segnale.
- **Stop (S1):** prezzo d'ingresso − 2 × ATR(14) della candela del segnale; non si sposta.
- **Uscita (U2):** all'apertura della candela successiva alla 24ª candela chiusa dopo l'ingresso (circa 24 ore).
- Regole fisse della sezione 7.8 (una posizione alla volta, niente aggiunte), costi della sezione 6, dimensione,
  leva 2 e liquidazione della sezione 9.4. Scheda: `candidati/V-020/regole.md` (impronta in `validazione.md`).

## 2. Ipotesi e meccanismo economico

- **Ipotesi I-04 → I-09** (`ipotesi.md`). Fonte del meccanismo: Schmeling, Schrimpf, Todorov, «Crypto carry», BIS
  Working Paper 1087, 2023 (il carry/funding misura la domanda di leva e la scarsità di capitale di arbitraggio);
  fonte del filtro: Baur, Cahill, Godfrey, Liu, Finance Research Letters 31, 2019 (volume più basso nel fine
  settimana).
- **Meccanismo (ipotizzato, non dimostrato):** un funding negativo vuol dire che gli short a leva pagano i long, cioè
  che c'è una folla di short. Nelle 24 ore seguenti le loro ricoperture e il ritorno del funding verso il valore
  normale spingono il prezzo in su più del caso. Nel fine settimana, con meno operatori, il funding negativo misura
  meno una folla vera.
- **L'inferenza contraria è della sessione, non della fonte**: la fonte descrive il funding, non dice che preveda i
  prezzi.

## 3. Metriche affiancate (sezione 9.7)

| Metrica | Costruzione (2020-01-01 → 2022-09-30) | Validazione (2022-10-01 → 2023-12-31) |
|---|---|---|
| Trade | 180 | 80 |
| Trade al mese | 5,46 | 5,33 |
| R medio dopo i costi | **+0,223** | **+0,167** |
| Profit factor | 1,46 | 1,29 |
| Vincenti | 48,3% | 40,0% |
| R medio dei vincenti / dei perdenti | (vedi `risultati/V-020.json`) | +1,852 / −0,957 |
| Drawdown massimo | −9,0 R | −14,7 R |
| R medio a costi doppi | +0,147 | +0,064 |
| p-value contro le entrate casuali | 0,017 (casuali: −0,004 R) | non previsto in validazione (10.3) |
| Somma degli R per anno | 2020 +16,50; 2021 +12,98; 2022 (gen-set) +10,60 | 2022 (ott-dic) +7,52; 2023 +5,81 |
| Funding nel risultato | −0,0003 R a trade | — |
| Trade ridotti per la leva / violazioni di liquidazione | 0 violazioni | 3 / 0 |

Ingresso a mercato: la percentuale di esecuzione degli ordini limit non si applica.

## 4. Verifiche della Fase 4 (costruzione; `risultati/V-020_fase4.json`)

| # | Verifica | Esito | Numeri |
|---|---|---|---|
| 1 | Robustezza dei parametri (±20%) | supera | 6 prove, R medio da +0,196 a +0,278 (ATR 11/17, stop 1,6/2,4 ATR, uscita 19/29 candele) |
| 2 | Timeframe adiacenti | supera | 30m +0,273 (202 trade); 2h +0,267 (164 trade) |
| 3 | Stabilità nel tempo | supera | blocchi: +0,402 (42 trade); −0,022 (17); +0,433 (30); +0,117 (91); quota massima 42% |
| 4 | Senza il 5% dei trade migliori | supera **per poco** | 9 trade tolti: R medio **+0,012** |
| 5 | Costi doppi | supera | +0,147 |
| 6 | Troncamento | supera | nessuna differenza |
| 7 | Liquidazione | supera | 0 violazioni |
| 8 | Riempimento severo | non si applica | ingresso a mercato |
| 9 | Regola intra-barra opposta (informativa) | — | differenza 0,000 |
| 10 | Ritardo di una candela (informativa) | — | +0,237 (175 trade), +0,014 rispetto alla regola |
| 11 | Versione a mercato (informativa) | non si applica | è già a mercato |

## 5. Limiti già visti (da tenere presenti nel leggere il vault)

1. **Pochi trade estremi.** Senza i 9 trade migliori l'R medio di costruzione scende da +0,223 a +0,012: il vantaggio
   vive di guadagni grandi e rari.
2. **La scelta dei giorni feriali è nata dai dati.** È venuta guardando i trade del fine settimana di V-012 (59 trade,
   −0,134 R); in V-011 (lo specchio short) il fine settimana era invece migliore. È il punto più esposto
   all'adattamento al passato.
3. **La robustezza non ha spostato il segnale.** La soglia del funding è 0,00%: ±20% di zero è zero, quindi la
   verifica 1 ha mosso stop e uscita ma non l'ingresso. Il catalogo ha solo un'altra soglia bassa (−0,01%), con
   troppo pochi trade (84 senza il filtro).
4. **Il vantaggio cala.** Da +0,223 (costruzione) a +0,167 (validazione), e nel solo 2023 +0,112 a trade (52 trade).
   A costi doppi in validazione resta +0,064.
5. **Il caso.** Con 40 varianti il protocollo si attende circa 0,9 candidati falsi (sezione 8.3); con un solo
   candidato i numeri di costruzione non bastano a distinguerlo da un falso. In validazione +0,167 R su 80 trade sta
   a circa 1,2 errori standard da zero (dispersione 1,2 R, sezione 5.2).
6. **Regola 7.** BTC è la moneta di cui il modello sa di più sul 2024-2026; non ho scelto l'idea per quello, ma non
   posso escluderne un'influenza inconsapevole.

## 6. Previsione per il vault (scritta prima dell'apertura)

Metodo: solo costruzione e validazione, nessuna conoscenza del periodo 2024-2026.

- **Trade attesi in 33 mesi:** circa **175** (5,3-5,5 al mese, come in costruzione e in validazione); intervallo
  plausibile **110-230**, perché il numero dipende da quanto spesso il funding è negativo, che cambia con il regime del
  mercato. Sotto 100 trade il vault non si può superare (10.3).
- **R medio atteso:** **+0,08 R a trade**, intervallo plausibile da −0,10 a +0,20. Ragionamento: la media pesata di
  costruzione e validazione è +0,206; la si riduce perché il candidato è il migliore di 40 varianti (selezione) e
  perché il vantaggio cala già fra costruzione e validazione (+0,223 → +0,167 → +0,112 nel 2023).
- **Probabilità di superare il vault** (almeno 100 trade, R medio positivo anche a costi doppi, profit factor ≥ 1,10,
  asticella di Benjamini-Hochberg al 10% con un solo candidato, cioè p ≤ 0,10): **circa 1 su 4**, inferito.

## 7. Eseguibile dal bot?

**No, così com'è** (`research/config/bot_3.md`; scelta (b) della sezione 7.10: le aggiunte si fanno prima del
paper, Passo 8). Per V-020 servono:

| Elemento | Stato nel bot | Cosa serve |
|---|---|---|
| Timeframe 1h | eseguibile solo in modalità di parità | un orologio da 1 ora per la strategia |
| E11 funding regolato sotto 0,00% alla prima candela dopo il regolamento | da aggiungere | lettura del funding regolato e del suo istante |
| F6 giorni feriali (UTC) | da aggiungere | filtro sul giorno della candela del segnale |
| S1 2 × ATR(14) con ingresso a mercato | eseguibile | — |
| U2 uscita dopo 24 candele | da aggiungere | uscita a tempo per strategia |
| Ingresso a mercato | diverso | in paper gli ingressi diventano limit se l'interruttore `PAPER_INGRESSO_LIMITE` è acceso: per V-020 va spento |
| Uscite globali del bot | diverso | spegnere per questa strategia profit-lock, uscita a 96 candele e pausa dopo lo stop |
| Funding nei costi | diverso | il paper del bot conta il funding in modo continuo, il motore per regolamento |
| Esecuzione fuori dal registro del gate | da aggiungere | un modo di far girare una strategia del protocollo senza il registro |
| Rigioco storico del codice del paper | non esiste | da costruire per la prova C (13bis.4) prima del paper |

## 8. Paper (Passo 8, se il vault è superato)

- **Trade al mese attesi in paper:** circa **5,4** (costruzione 5,46, validazione 5,33).
- 40 trade richiesti dal Passo 8: circa **7-8 mesi**, sotto il limite di 12 mesi (stima; il ritmo vero dipende da
  quanto spesso il funding sarà negativo).
- Prima: la prova C di parità con il bot (C1, C2 e V-020) e le aggiunte della sezione 7.
