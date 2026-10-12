# Passo 7 — Giudizio d'insieme e confronto fra monete (12 ottobre 2026)

Protocollo di ricerca 4.5, Passo 7, punti 1, 2 e 4, scritto dalla sessione di coordinamento il 12 ottobre 2026 dopo il
vault dell'11 ottobre (`research/vault/risultati.md`) e la decisione del proprietario di saltare il trasferimento
(Passo 6). Le regole sono quelle del protocollo, scritte prima del vault. Questo file non propone modifiche al bot né
al gate: dice cosa la ricerca ha trovato e cosa no.

**Da dove vengono i numeri.** Dalle consegne e dai log delle 21 campagne (`research/campagne/<SIMBOLO>/consegna.md`,
`ipotesi.md`, `lezioni_moneta.md`, `log.jsonl`; per i tre candidati del vault `candidati/<ID>/regole.md`), ora tutti
sul branch principale (Passo 7, punto 3); dal riepilogo del Passo 4 (`research/passo4/riepilogo.md`); dai risultati
del vault (`research/vault/`); dai parametri congelati (`research/config/parametri.yaml`). I conteggi per timeframe,
direzione e famiglia sono stati rifatti dal coordinamento sulle 630 voci `registrazione` e `risultato` dei 21
`log.jsonl`: i massimi di `t` per campagna così ottenuti coincidono con quelli scritti nelle 21 consegne. Le etichette
delle famiglie di meccanismo (sezione 1) sono del coordinamento, assegnate idea per idea dal campo `meccanismo` e
dalla fonte di ogni registrazione; le campagne usavano nomi diversi per la stessa cosa. Le idee che hanno prodotto
solo scarti (sotto i trade minimi, mai testate) non contano fra le famiglie «provate».

## Punto 1 — Giudizio d'insieme

**Candidati passati nel vault: 0 su 3.** Il tasso del caso di ciascun candidato (quota delle 1000 strategie a entrate
casuali con la stessa uscita che passano lo stesso `criterio_vault`) è 0,001 per BTCUSDT-V10, 0,004 per BNBUSDT-045 e
0,015 per ADAUSDT-037 (`research/vault/risultati.md`): la somma, cioè il numero di passaggi atteso per puro caso, è
0,020, e la probabilità di vedere 0 passaggi se i tre candidati non avessero alcun vantaggio è circa il 98%. Il
risultato è quello che il caso puro avrebbe dato. La quota reale (0%) non è «vicina» a quella del caso nel senso di
«i passaggi valgono poco»: è che non ce ne sono.

L'imbuto completo, dalle campagne al vault: 630 varianti testate → 45 candidati di Fase 2 (nette contro le due
baseline con R medio positivo in costruzione) → 7 arrivati in validazione → 3 al vault → 0 passati. Dei 7 in
validazione, nessuno ha tenuto l'R medio della costruzione (BTCUSDT-V10 +0,149 → +0,048 → +0,031 nel vault; BNBUSDT-045
+0,138 → +0,047 → −0,087; ADAUSDT-037 → +0,624 fatto da 3 trade → −0,164; FILUSDT-025 +0,084 → −0,117; DYDXUSDT-008
+0,060 → −0,178; MASKUSDT-029 → +0,011 su 41 trade; XRPUSDT-V21r3 → 5 trade). Il solo candidato con un residuo di
vantaggio nel vault è BTCUSDT-V10, che batte ancora nettamente le entrate casuali con la stessa uscita (t 3,01, p
0,0015) ma non arriva al profit factor minimo (1,067 contro 1,10) e guadagna solo nel 2024.

Un indizio in più, non una prova: in costruzione 71 varianti su 600 con un `t` leggibile (11,8%) erano nette contro la
(b), contro lo 0,41% di strategie finte senza vantaggio della prova a placebo del 9 ottobre. La differenza non è un
vantaggio: viene dai ritocchi concentrati sulle famiglie vicine alla soglia (34 candidati su 45 sono ritocchi) e dalla
trappola dello stop agganciato a un livello di prezzo, che gonfia il confronto con le baseline (sezioni 2.1 e 2.3);
la Fase 4 (costi doppi, ritardo di una barra) e la validazione hanno poi fermato quasi tutto, e il vault il resto.

**Conclusione del Passo 7, punto 1:** con questo protocollo, su 20 monete e sul gruppo di 80, con 630 varianti da
fonti pubblicate prima del 2024, non è stato trovato nessun vantaggio sfruttabile dopo i costi. Dove un effetto c'è
(ultima mezz'ora del giorno UTC, ritardo delle monete rispetto a BTC, rottura dall'apertura del giorno su BTC) è più
piccolo del costo di un giro o si consuma anno dopo anno.

## 0. Il quadro in poche righe

* 21 campagne (20 monete più la campagna di gruppo su 80 monete), **630 varianti** testate (30 per campagna:
  519 da idee nuove, 111 ritocchi), 197 scarti sotto i trade minimi che non consumano budget (dai log;
  stessi numeri delle consegne).
* **45 varianti** sono diventate candidati in Fase 2 (battono nettamente la (a) e la (b) in costruzione con R
  medio dopo i costi positivo): 34 da ritocchi, 11 da idee nuove (log, campi `netta` e `r_medio`).
* **7** sono arrivate in validazione (riepilogo del Passo 4): 3 sono andate al vault (BTCUSDT-V10, BNBUSDT-045,
  ADAUSDT-037), 4 no (XRPUSDT-V21r3 con 5 trade, FILUSDT-025 con R negativo, DYDXUSDT-008 con p 0,968,
  MASKUSDT-029 con p 0,293).
* **Vault: 0 su 3** (`vault/risultati.md`). Passaggi attesi per puro caso, sommando i tre tassi del caso:
  circa 0,02. BTCUSDT-V10 fallisce per il solo profit factor (1,067 contro 1,10) con R medio +0,031 su 325
  trade; BNBUSDT-045 fa −0,087 R su 94 trade (come le entrate casuali, percentile 40); ADAUSDT-037 fa −0,164 R su
  167 trade (percentile 82).
* Sulle 600 varianti con un `t` contro la (b) leggibile, la media del `t` è 0,46 e la deviazione 1,30
  (log); 71 sono sopra 2 e 18 sotto −2. BCHUSDT e TRBUSDT, che hanno fatto lo stesso conto sulle loro 30,
  scrivono «la forma del caso» (t medio 0,11 e 0,05, deviazione 0,96 e 0,80; consegne).

## 1. Una tabella per campagna

Le famiglie uniformi usate nella tabella (20 etichette; fra parentesi le fonti tipiche):

| Etichetta | Cosa è |
|---|---|
| momento | tendenza di più giorni: il rendimento di 1-4 settimane continua (Moskowitz-Ooi-Pedersen 2012; Liu-Tsyvinski 2018) |
| canale | rottura del massimo/minimo di N barre (Faith 2007; Brock-Lakonishok-LeBaron 1992) |
| media mobile | incrocio del prezzo con una media, ADX (Brock e altri 1992; Detzel e altri 2018; Wilder 1978) |
| RSI(2) | ritorno alla media su RSI a 2 periodi dentro la tendenza (Connors-Alvarez 2008) |
| Williams | rottura di volatilità dall'apertura del giorno: apertura + frazione del range di ieri (Williams 1999) |
| intervallo d'apertura | rottura dell'intervallo delle prime ore UTC, «opening range» (Crabel 1990) |
| NR7 | barra più stretta di 7 (o 4) e rottura (Crabel 1990) |
| Bollinger | compressione delle bande e rottura (Bollinger 2001) |
| ultima mezz'ora | momento dentro la giornata: la prima mezz'ora, o la giornata, predice l'ultima mezz'ora o fascia (Gao-Han-Li-Zhou 2018; Shen-Urquhart-Wang 2022; Wen-Bouri-Xu-Zhao 2022) |
| stagionalità | lunedì, cambio di mese, fascia oraria che si ripete (Caporale-Plastun 2019; Lakonishok-Smidt 1988; Heston-Korajczyk-Sadka 2010) |
| funding | funding estremo come affollamento (Schmeling-Schrimpf-Todorov 2023; He-Manela-Ross-von Wachter 2022) |
| last/mark | premio o sconto del perpetuo sul mark price che rientra (He-Manela-Ross-von Wachter 2022) |
| volume | volume alto o basso, illiquidità (Gervais-Kaniel-Mingelgrin 2001; Amihud 2002) |
| squilibrio ordini | squilibrio degli ordini aggressivi (Chordia-Subrahmanyam 2004; Evans-Lyons 2002) |
| inversione | inversione di breve dopo un movimento estremo, con o senza volume, pump and dump, falsa rottura (Lehmann 1990; Jegadeesh 1990; Nagel 2012; Campbell-Grossman-Wang 1993; Kamps-Kleinberg 2018; Kozlowski e altri 2021) |
| continuazione | continuazione dopo un giorno o una barra anomala, con o senza volume (Caporale-Plastun 2019/2020; Llorente e altri 2002; Zaremba e altri 2021) |
| numeri tondi | numeri tondi e livelli di supporto/resistenza (Osler 2003; Osler 2000) |
| relazione con BTC | ritardo rispetto a BTC, forza relativa, residuo o coppia con BTC, trend di BTC (Lo-MacKinlay 1990; Hou-Moskowitz 2005; Koutmos 2018; Liu-Tsyvinski-Wu 2019; Avellaneda-Lee 2010; Gatev e altri 2006; Da-Liu-Schaumburg 2014; Blitz e altri 2011) |
| candele | martello, stella cadente (Nison 1991; Caginalp-Laurent 1998) |
| distribuzione | volatilità bassa, asimmetria, lotteria (Moreira-Muir 2017; Amaya e altri 2015; Boyer e altri 2010; Bali-Cakici-Whitelaw 2011) |

Colonne: «Varianti» = idee nuove / ritocchi / scarti (consegne e log); «Famiglie» = quante famiglie uniformi
con almeno una variante testata, e quali (fra parentesi le famiglie con più di 2 varianti); «Timeframe e
direzioni» = varianti per timeframe e long/short (log); «t più alto contro la (b)» in costruzione (log; «rit.»
= ritocco); «Candidati F2» = candidati di Fase 2; «In validazione» = trade, R medio dopo i costi, p-value
(consegne); «Esito».

| Moneta | Vers. | Varianti | Famiglie provate | Timeframe e direzioni | t più alto contro la (b) | Cand. F2 | In validazione | Esito finale |
|---|---|---|---|---|---|---|---|---|
| BTCUSDT | 4.4 | 25 / 5 / 7 | 15: momento, canale, media mobile, RSI(2), Williams, NR7, ultima mezz'ora (6), stagionalità, funding, volume, squilibrio ordini, inversione (3), continuazione, numeri tondi, candele | 4h 14, 30m 6, 1h 5, 1d 3, 8h 2; L 16 / S 14 | 3,58: V35, ultima mezz'ora, 30m short, rit., R +0,045 (caduto in Fase 4). Il candidato V10 (Williams, 1h long): 2,35 | 5 | V10: 136 trade, R +0,048, p 0,048 | al vault: **non passa** (PF 1,067) |
| ETHUSDT | 4.4 | 30 / 0 / 4 | 13: momento, canale, RSI(2), Williams, NR7, ultima mezz'ora, stagionalità (3), funding, squilibrio ordini, inversione, continuazione (3), numeri tondi/livelli (4), relazione con BTC | 1h 13, 1d 7, 4h 6, 30m 2, 8h 2; L 15 / S 15 | 2,67: 026, livello (massimo di ieri), 1h short, R +0,023 | 1 | nessuno (026 caduto in Fase 4: costi doppi, ritardo) | nessuna strategia valida |
| SOLUSDT | 4.4 | 22 / 8 / 9 | 12: momento, canale, media mobile, RSI(2), NR7 (5), ultima mezz'ora (7), stagionalità, funding, volume, inversione (3), numeri tondi, relazione con BTC | 4h 9, 30m 7, 1h 6, 1d 4, 2h 2, 8h 2; L 13 / S 17 | 2,78: 023, ultima mezz'ora, 30m short, rit., R +0,017 | 4 | nessuno (tutti caduti: costi doppi e ritardo) | nessuna strategia valida |
| XRPUSDT | 4.5 | 27 / 3 / 7 | 13: momento, canale, RSI(2), intervallo d'apertura, ultima mezz'ora, stagionalità, funding, last/mark (5), squilibrio ordini, inversione, continuazione, numeri tondi, relazione con BTC (4) | 1h 15, 1d 7, 4h 4, 30m 2, 8h 2; L 17 / S 13 | 2,33: V21r3, last/mark, 1h long, rit., R +0,167 | 1 | V21r3: 5 trade, «non si sa» | nessuna strategia valida |
| DOGEUSDT | 4.5 | 25 / 5 / 15 | 15: momento, canale, media mobile, RSI(2), Williams, NR7, Bollinger (7), ultima mezz'ora, stagionalità, funding, volume, squilibrio ordini, inversione, numeri tondi, distribuzione | 1h 17, 1d 6, 4h 3, 30m 2, 8h 2; L 11 / S 19 | 2,14: 042, Bollinger, 1h short, rit., R +0,158 | 1 | nessuno (042 caduto: robustezza, costi doppi) | nessuna strategia valida |
| BNBUSDT | 4.5 | 25 / 5 / 15 | 14: momento, canale, media mobile, RSI(2) (6), Bollinger, ultima mezz'ora, stagionalità, funding, volume, squilibrio ordini, inversione, continuazione, numeri tondi, distribuzione | 4h 11, 1h 11, 1d 4, 30m 2, 8h 2; L 21 / S 9 | 3,96: 045, RSI(2), 1h long, rit., R +0,138 | 3 | 045: 32 trade, R +0,047, p 0,031 | al vault: **non passa** (R −0,087) |
| LTCUSDT | 4.5 | 25 / 5 / 6 | 12: momento, canale, media mobile, RSI(2), intervallo d'apertura (7), Bollinger, stagionalità, funding, last/mark, inversione, continuazione (4), numeri tondi | 1h 15, 4h 6, 1d 5, 2h 2, 8h 2; L 13 / S 17 | 1,95: 014, intervallo d'apertura, 1h short, R −0,068 (netta solo contro la (a)) | 0 | nessuno | nessuna strategia valida |
| MATICUSDT | 4.5 | 22 / 8 / 16 | 11: momento, media mobile, RSI(2), ultima mezz'ora, stagionalità, funding, volume (6), squilibrio ordini (7), inversione, continuazione, relazione con BTC | 1h 13, 4h 8, 1d 5, 30m 2, 8h 2; L 15 / S 15 | 2,21: 026, squilibrio ordini, 1h short, rit., R +0,068 (non netta contro la (a)); il candidato 025: 2,12 | 1 | nessuno (025 caduto: ritardo, costi doppi) | nessuna strategia valida |
| BCHUSDT | 4.5 | 25 / 5 / 8 | 14: momento (6), canale, media mobile, RSI(2), Williams (3), Bollinger, stagionalità, funding, volume, squilibrio ordini, inversione, continuazione, numeri tondi, distribuzione | 1d 13, 1h 9, 4h 6, 8h 2; L 14 / S 16 | 1,62: 002, momento, 1d short, R +0,109 | 0 | nessuno | nessuna strategia valida |
| LINKUSDT | 4.5 | 27 / 3 / 4 | 12: momento, canale, RSI(2), Williams, Bollinger, ultima mezz'ora, stagionalità (3), funding, squilibrio ordini, inversione (7), continuazione (4), numeri tondi | 1h 14, 1d 10, 4h 2, 30m 2, 8h 2; L 18 / S 12 | 2,23: V24, inversione giornaliera, 1d long, R +0,042 (non netta contro la (a): 1,71) | 0 | nessuno | nessuna strategia valida |
| AVAXUSDT | 4.5 | 25 / 5 / 7 | 13: momento, canale, RSI(2), Williams, Bollinger, ultima mezz'ora (7), stagionalità, funding, volume, squilibrio ordini, inversione, continuazione, relazione con BTC (3) | 4h 9, 1h 8, 30m 7, 1d 4, 8h 2; L 19 / S 11 | 3,52: V-12, ultima mezz'ora, 30m short, R +0,007 | 5 | nessuno (4 caduti ai costi doppi, V-14 al ritardo: t 1,327 contro 1,342) | nessuna strategia valida |
| ADAUSDT | 4.5 | 22 / 8 / 11 | 11: momento, canale, intervallo d'apertura (7), ultima mezz'ora (5), funding, volume, squilibrio ordini, inversione, continuazione, numeri tondi, relazione con BTC (4) | 1h 8, 15m 7, 4h 6, 30m 5, 1d 2, 8h 2; L 16 / S 14 | 6,57: 038, intervallo d'apertura, 15m long, rit., R −0,067 (netta ma R negativo: effetto dello stop, nota N011); il candidato 037: 2,51 | 6 | 037: 82 trade, R +0,624, p 0,014 | al vault: **non passa** (R −0,164) |
| TRBUSDT | 4.5 | 27 / 3 / 14 | 12: momento, canale, RSI(2), intervallo d'apertura (5), Bollinger, ultima mezz'ora, stagionalità, inversione (6), continuazione, numeri tondi, candele, distribuzione (3) | 4h 10, 1h 10, 15m 5, 1d 3, 30m 2; L 14 / S 16 | 1,37: I-13-S, intervallo d'apertura, 15m short, R −0,129 | 0 | nessuno | nessuna strategia valida |
| FILUSDT | 4.5 | 22 / 8 / 9 | 10: momento, media mobile, RSI(2), Williams, ultima mezz'ora (10), stagionalità (3), funding, squilibrio ordini, inversione (4), relazione con BTC | 4h 17, 1h 10, 8h 2, 1d 1; L 16 / S 14 | 3,40: 035, ultima mezz'ora (fascia 20-24 UTC), 4h long, rit., R +0,112 (caduto al ritardo); il candidato 025 (Williams, 1h long): 2,34 | 10 | 025: 87 trade, R −0,117, p 0,085: fallito (decisione del proprietario, 9 ott) | nessuna strategia valida |
| 1000SHIBUSDT | 4.5 | 27 / 3 / 10 | 15: momento, canale, media mobile, RSI(2), Bollinger, ultima mezz'ora (5), stagionalità, funding, volume, squilibrio ordini, inversione (3), continuazione, numeri tondi, relazione con BTC, distribuzione | 4h 12, 1h 9, 30m 5, 2h 2, 1d 1, 15m 1; L 13 / S 17 | 2,15: 030, ultima mezz'ora, 30m short, rit., R +0,027 | 2 | nessuno (028 e 030 caduti ai costi doppi) | nessuna strategia valida |
| DYDXUSDT | 4.5 | 21 / 9 / 9 | 12: momento, canale, RSI(2), NR7 (6), ultima mezz'ora, stagionalità, funding, last/mark, squilibrio ordini (6), inversione, numeri tondi, relazione con BTC | 1h 12, 1d 9, 4h 6, 30m 2, 8h 1; L 11 / S 19 | 2,22: 008, relazione con BTC (ritardo), 1h long, R +0,060 | 1 | 008: 83 trade, R −0,178, p 0,968 | nessuna strategia valida |
| MASKUSDT | 4.5 | 25 / 5 / 6 | 12: momento, canale, RSI(2), intervallo d'apertura, Bollinger, ultima mezz'ora, funding, last/mark, squilibrio ordini, inversione (8), relazione con BTC (3), candele | 1h 24, 4h 3, 30m 2, 8h 1; L 13 / S 17 | 2,85: 029, inversione dopo barra estrema, 1h short, rit., R +0,264 | 1 | 029: 41 trade, R +0,011, p 0,293 | nessuna strategia valida |
| FTMUSDT | 4.5 | 26 / 4 / 8 | 14: momento (6), canale, media mobile, RSI(2), Williams, Bollinger, ultima mezz'ora, stagionalità, funding, last/mark, inversione (3), numeri tondi, relazione con BTC, distribuzione | 1h 10, 1d 8, 2h 6, 4h 3, 30m 2, 8h 1; L 15 / S 15 | 2,22: 036, momento, 1d short, rit., R +0,033 (non netta contro la (a): 1,47) | 0 | nessuno | nessuna strategia valida |
| GALAUSDT | 4.5 | 28 / 2 / 7 | 13: momento, canale, RSI(2), Williams, NR7, ultima mezz'ora, stagionalità (3), funding, last/mark, inversione (3), continuazione, numeri tondi, relazione con BTC (6) | 1h 17, 4h 7, 2h 2, 30m 2, 1d 1, 8h 1; L 16 / S 14 | 2,22: 032, last/mark, 1h short, R +0,013 | 1 | nessuno (032 caduto ai costi doppi) | nessuna strategia valida |
| ETCUSDT | 4.5 | 23 / 7 / 9 | 12: momento (4), media mobile, RSI(2), intervallo d'apertura, ultima mezz'ora (7), stagionalità, volume (3), squilibrio ordini, inversione, continuazione, numeri tondi, relazione con BTC | 4h 11, 1h 9, 30m 7, 1d 3; L 13 / S 17 | 3,85: 035, ultima mezz'ora, 30m short, rit., R −0,009 (netta ma R negativo); i candidati 033/036/037: 3,62 / 3,14 / 3,51 | 3 | nessuno (tutti caduti: costi doppi e ritardo) | nessuna strategia valida |
| GRUPPO (80 monete) | regole.md (4.5) | 20 / 10 / 6 | 10: momento, canale, RSI(2), stagionalità, funding, inversione, continuazione, relazione con BTC (16), candele, distribuzione | 1d 16, 4h 7, 1h 7; L 19 / S 11 | 2,06: 048, relazione con BTC (ritardo dopo un'ora forte di BTC), 1h long, rit., R +0,008 (soglia 2,16) | 0 | nessuno | nessuna strategia valida per il gruppo |

Totali (log): 630 varianti, 519 idee nuove, 111 ritocchi, 197 scarti; 45 candidati di Fase 2; 7 in
validazione; 3 al vault; 0 passati.

## 2. Confronto fra monete (Passo 7, punto 2)

Definizioni del protocollo (`PROTOCOLLO.md`, Passo 7): «simili» = stessa famiglia di meccanismo, stessa
direzione, timeframe uguale o adiacente (i timeframe ammessi sono 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d:
adiacente a 1h sono 30m e 2h; adiacente a 15m è solo 30m). Il confronto «serve a leggere i risultati, non a
validarli». Tutti i `t` qui sotto sono di costruzione, contro la (b), dal log, salvo dove scritto.

### 2.1 BTCUSDT-V10 — rottura di volatilità dall'apertura del giorno (Williams), long, 1 ora

Regole (`candidati/V10/regole.md`): prima chiusura oraria sopra apertura del giorno + 0,5 × range di ieri;
stop all'apertura del giorno; uscita a fine giorno UTC; nessun filtro.

La famiglia «Williams» è stata provata su **9 campagne, 19 varianti** (tutte a 1h: 9 long, 10 short, 1 ritocco).
Le varianti simili (long, 1h) sulle altre 8 monete:

| Moneta | Variante | Trade | R medio | t contro la (b) | Esito |
|---|---|---|---|---|---|
| ETHUSDT | 032 | 316 | +0,225 | 1,53 | non netta |
| FILUSDT | 025 | 177 | +0,084 | 2,34 | **candidato**; supera la Fase 4; in validazione R −0,117 su 87 trade (t 1,39, p 0,085): fallito |
| GALAUSDT | 017 | 181 | +0,144 | 1,29 | non netta |
| FTMUSDT | 010 | 227 | +0,028 | 0,96 | non netta |
| BCHUSDT | 007 | 307 | +0,017 | 0,94 | non netta |
| AVAXUSDT | V-16 | 265 | −0,119 | 0,91 | non netta |
| LINKUSDT | V15 | 327 | +0,044 | 0,86 | non netta |
| DOGEUSDT | 007 | 201 | +0,030 | 0,67 | non netta |

Lato short (non «simile» per direzione, ma stessa famiglia): BTCUSDT-V11 era netta (t 3,01) e cade alla prova
dello scettico con lo stop fisso (t 1,01); sulle altre monete nessuna netta (AVAX V-17 1,72; ETH 033 1,66; LINK
V16 1,62; BCH 008 1,53 e il ritocco 038 1,44; FIL 026 1,07; DOGE 008 0,21; FTM 011 0,01; GALA 018 −0,40).
Su 30m e 2h la famiglia è stata provata solo come verifica di Fase 4 su BTC stessa (30m t 2,45; 2h t 2,39,
consegna BTCUSDT), mai come variante su altre monete.

**Cosa dice.** Su 9 monete la stessa regola è stata netta solo su 2 (BTC e FIL). FIL è caduta in validazione; BTC
è passata in validazione con p 0,048 ed è caduta nel vault per il profit factor (1,067), con R medio +0,031 e
positivo solo nel 2024, anno in cui BTC fa +121% (`vault/risultati.md`). Il segno dell'R medio long è positivo su 7
monete su 8 (tutte tranne AVAX), ma mai nettamente sopra entrate casuali nella stessa direzione: la (b) long
assorbe i rialzi del 2020-2021. Tre campagne indipendenti (BTC lezione 4, FIL Fase 5 prova S1, LTC lezione 2) hanno
scritto la stessa cosa sul meccanismo di questa famiglia: **lo stop ancorato all'apertura del giorno rende le
baseline molto negative** (gli ingressi a caso hanno lo stop vicinissimo e costi enormi in R), e contro ingressi
casuali con uno stop di distanza normale il `t` scende (FIL: da 2,34 a 1,38; BTC V11: da 3,01 a 1,01; BTC V10 con
lo stop fisso al 2% resta netta, t 3,10, ma la stessa prova non è stata rifatta in validazione). Nel vault BTC-V10
batte ancora nettamente la (b) con lo stesso stop (t 3,01, p 0,0015) e sta al 99° percentile, ma dopo i costi il
profit factor non arriva a 1,10. In breve: la famiglia dà un effetto lordo piccolo e un confronto con le baseline
gonfiato dallo stop; il vault lo ha confermato sulla moneta migliore.

Famiglia vicina ma non uguale, «intervallo d'apertura» (Crabel, stop sul minimo dell'intervallo): long a 1h su
LTC 013 (t 1,73, R −0,018), ETC 029 (0,85, +0,007), XRP V28 (0,10, −0,048), MASK 019 (−0,62, −0,150): nessuna netta.

### 2.2 BNBUSDT-045 — cali bruschi in tendenza (RSI a 2 periodi), solo fine settimana, long, 1 ora

Regole (`candidati/BNBUSDT-045/regole.md`): close > SMA(200), RSI(2) < 5, barra che apre di sabato o domenica
UTC; uscita sopra la SMA(5) o dopo 12 barre; stop 2,5 ATR. È il quinto ritocco della famiglia BNBUSDT-005.

La famiglia «RSI(2) in tendenza» è stata provata su **20 campagne, 40 varianti** (4h 29, 1h 10, 1d 1; 22 long, 18
short; 5 ritocchi, tutti su BNB). Varianti simili (long, 30m / 1h / 2h) sulle altre monete: solo due.

| Moneta | Variante | tf | Trade | R medio | t contro la (b) | Esito |
|---|---|---|---|---|---|---|
| MASKUSDT | 007 | 1h | 261 | −0,009 | 1,02 | non netta |
| DYDXUSDT | 003 | 1h | 262 | −0,024 | −0,05 | come il caso |

Sulla stessa BNB la variante di partenza senza filtri (005) aveva t 1,67 e R +0,003 (270 trade); i due gemelli
con filtri diversi (043 ATR ≥ 1,5%; 044 close ≥ SMA200 + 1,7 ATR) erano netti (2,48; 2,74) e sono caduti al
ritardo di una barra (t −0,04 e 1,08). A 4h, timeframe non adiacente ma quello della maggior parte delle
campagne, il long è stato provato su 14 monete e non è mai stato netto: FTM 1,11, LTC 0,66, 1000SHIB 0,64,
MATIC 0,60, SOL 0,37, LINK −0,04, ETC −0,11, ETH −0,12, BCH −0,21, TRB −0,23, AVAX −0,27, BTC −0,81, DOGE −0,82,
XRP −1,11 (ADA e GALA: scarti sotto i 70 trade; FIL: solo lo short). Sul gruppo di 80 monete solo lo short a 1d
(GRUPPO-029, t −0,82); il long è uno scarto (453 trade stimati su 700).

Il filtro del fine settimana non ha un gemello in questa famiglia su altre monete. L'unica altra variante con lo
stesso filtro è BTCUSDT-V33 (ultima mezz'ora short + solo fine settimana, 30m): netta in costruzione (t 3,11),
caduta in Fase 4; la campagna BTC la segnala come «filtro visto nei dati».

**Cosa dice.** Nessuna moneta oltre BNB ha mostrato un vantaggio netto con questo meccanismo, a nessun
timeframe; su BNB il vantaggio è comparso solo dopo i ritocchi e, scrive la campagna stessa, il filtro del fine
settimana è «il migliore di 7 gruppi per giorno guardati sugli stessi trade di costruzione». Due campagne
(BNB lezioni; BTC lezione 2) osservano che nel 2020-2022 dopo i cali il prezzo tende a continuare più che a
rimbalzare. Il vault (R −0,087, come le entrate casuali) è coerente con un filtro adattato ai dati di costruzione.

### 2.3 ADAUSDT-037 — rottura dell'intervallo d'apertura (Crabel) con due filtri, long, 15 minuti

Regole (`candidati/ADAUSDT-037/regole.md`): massimo/minimo delle 4 barre 00:00-00:45 UTC; ingresso alla prima
chiusura sopra il massimo fra le 01:15 e le 19:45; filtri: close > media semplice di 20 giorni e BTC in calo nelle
24 ore prima; stop al minimo dell'intervallo; uscita alle 00:00. Quarto ritocco della famiglia ADAUSDT-024.

La famiglia «intervallo d'apertura» è stata provata su **6 campagne, 25 varianti** (15m 12, 1h 13; 11 long, 14
short; 13 ritocchi). Varianti simili in senso stretto (long, 15m o 30m) fuori da ADA: una sola.

| Moneta | Variante | tf | Trade | R medio | t contro la (b) | Esito |
|---|---|---|---|---|---|---|
| TRBUSDT | I-13-L | 15m | 508 | −0,070 | 0,82 | non netta |

Stessa famiglia e direzione a 1h (due passi più in là, non «adiacente»): LTC 013 (t 1,73, R −0,018), ETC 029
(0,85, +0,007), XRP V28 (0,10, −0,048), MASK 019 (−0,62, −0,150): nessuna netta. Lato short: ADA 025 era netta
(3,28, R +0,016) ed è caduta ai costi doppi; LTC 014 (1,95, R −0,068) e i suoi 5 ritocchi (t da 0,01 a 1,45, R
sempre negativo); TRB I-13-S (1,37) e 3 ritocchi (≤ 1,25); MASK 020 0,96; ETC 030 0,70; XRP V29 0,37.

Dentro ADA, la famiglia ha prodotto 6 varianti nette contro la (b) su 7, ma con R medio negativo o nullo senza
filtri (024: t 2,49, R −0,002; 038: t 6,57, R −0,067): la campagna scrive (nota N011) che «le baseline sono molto
negative per la distanza dello stop», lo stesso effetto visto per Williams. I due filtri del candidato
(tendenza a 20 giorni e BTC in calo) sono nati dallo studio dei fallimenti della 024; la prova dello scettico
(nota N034) dice che entrando a caso solo nelle barre dove valgono i filtri l'R medio è già +0,110 e il candidato
(+0,252) non lo batte nettamente (t 0,63). Filtri dello stesso tipo altrove: MATICUSDT-025 (squilibrio ordini short
con «BTC non in rialzo nelle 24 ore», caduto al ritardo), ADAUSDT-035 e 040 (BTC in calo; caduti ai costi doppi),
FILUSDT-025 prova S2 (il guadagno sta nei giorni in cui sale tutto il mercato), LINKUSDT V24 nota N013 (il rimbalzo
vive nei giorni in cui scende tutto il mercato).

**Cosa dice.** Fuori da ADA questa famiglia non ha mai battuto il caso, su 5 monete e a nessun timeframe; dentro ADA
batteva il caso per lo stop, non per la direzione, e il candidato aggiungeva uno stato del mercato scelto sui dati.
In validazione l'R medio +0,624 veniva da 3 trade (senza: +0,014); nel vault la coda non è arrivata (R −0,164, 113
stop su 167 trade). Due campagne diverse (LTC lezione 2; BTC lezione 4) avevano già scritto la lezione sullo stop
agganciato a un livello: su LTC la stessa regola con lo stop fisso al 3% passa da t 1,95 a 0,01.

### 2.4 «Idea di gruppo»: nessuna

Per il protocollo un'idea di gruppo è un'idea simile **passata nel vault** su almeno `idea_di_gruppo_monete_minime`
= 3 monete (`config/parametri.yaml`) **e** confermata dal trasferimento di almeno un candidato. I passaggi nel vault
sono 0 su 3 e il trasferimento (Passo 6) non è stato fatto: **non esiste nessuna idea di gruppo**, e nessuna delle
due condizioni può essere soddisfatta con i dati che abbiamo. La convergenza che si vede in costruzione (per
esempio l'ultima mezz'ora short netta su 7 monete, sezione 3) resta, per il protocollo, «un indizio, non una prova»,
e in ogni caso nessuna di quelle varianti è sopravvissuta alla Fase 4.

## 3. I fallimenti

### 3.1 Famiglie provate su più monete che non hanno mai dato un candidato

Conteggi dal log (varianti testate, cioè con un risultato; i ritocchi sono compresi). «t max» è il `t` più alto
contro la (b) in costruzione fra tutte le varianti della famiglia.

| Famiglia | Campagne | Varianti | Nette contro la (b) | t max (dove) | Note |
|---|---|---|---|---|---|
| momento (tendenza di più giorni) | 21 | 52 | 2 | 2,22 (FTMUSDT-036, 1d short, ritocco, non netta contro la (a)) | R medi alti sui long (ETC 001 +0,42; MATIC I-01 +0,43; GALA 001 +0,98, tutto in 3 trade) ma uguali alla (b) long: è il trend 2020-21 (scritto da BTC, BNB, ADA, LTC, MATIC, AVAX, ETC, FIL, BCH) |
| canale | 18 | 33 | 0 | 1,26 (MASKUSDT-004, 1h short) | R medi alti sui long (BTC V03 +0,44 contro +0,27 della (b); BNB I-02 +0,81, «3 trade del 2021 fanno tutto»; XRP V12 +0,42) ma non netti; in almeno 8 campagne (MATIC, FIL, ETC, AVAX, GALA, FTM, DYDX, 1000SHIB) la versione a 4h non arriva a 70 trade |
| funding | 19 | 33 | 0 | 1,47 (BTCUSDT-V14, 8h short) | in 5 campagne lo short dopo funding alto va peggio del caso (BCH −2,05; DOGE −2,67; MATIC −2,27; SOL −2,70; LINK −1,64): «dopo il funding alto il prezzo ha continuato a salire» |
| volume (alto/basso, illiquidità) | 10 | 18 | 0 | 1,94 (MATICUSDT-016, 1d long, R +1,02 ma la (a) fa già 0,45) | pochi trade estremi del 2021 |
| media mobile | 11 | 20 | 0 | 1,57 (ETCUSDT-025, 4h short) | come il caso nella stessa direzione |
| NR7 | 6 | 18 | 1 | 2,32 (SOLUSDT-032, 4h short, ritocco, non netta contro la (a)) | 7 ritocchi senza candidato |
| candele | 4 | 7 | 0 | 1,66 (BTCUSDT-V22, 4h long: senza i 3 migliori −0,03) | |
| distribuzione (volatilità bassa, asimmetria, lotteria) | 7 | 10 | 0 | 0,22 (BCHUSDT-032) | la più lontana dal caso in assoluto |

Famiglie con un solo candidato di Fase 2, poi caduto in Fase 4 (quindi mai un candidato in validazione):

| Famiglia | Campagne | Varianti | Nette (b) | Candidato e dove è caduto |
|---|---|---|---|---|
| stagionalità (lunedì, cambio di mese, fascia oraria) | 19 | 28 | 1 | FILUSDT-024 (fascia oraria, 4h short): costi doppi e ritardo. Il lunedì long (19 campagne) non è mai netto: t fra −1,90 (FIL: «il contrario della fonte») e 1,13 (BTC) |
| Bollinger | 10 | 24 | 1 | DOGEUSDT-042 (1h short, terzo ritocco): robustezza (6 casi netti su 14) e costi doppi; «un picco, non un'area stabile» |
| squilibrio ordini | 15 | 38 | 5 | MATICUSDT-025 (1h short): ritardo (t 0,53) e costi doppi. Su BCH e FIL dopo acquisti aggressivi il prezzo scende (t −1,99; R −0,43) |
| continuazione dopo barra anomala | 15 | 35 | 1 | AVAXUSDT-V14 (4h long): ritardo per 0,015 di t (1,327 contro 1,342); la campagna lo porta come lezione di metodo, non chiede di recuperarlo |
| numeri tondi e livelli | 16 | 34 | 1 | ETHUSDT-026 (livello del massimo di ieri, 1h short): costi doppi (R −0,076) e ritardo (t 1,27 contro 1,33). I numeri tondi (Osler 2003) su 15 campagne: mai netti |
| inversione di breve | 21 | 61 | 3 | MASKUSDT-029 (1h short, secondo ritocco): arrivato in validazione, p 0,293. In 9 campagne l'inversione dopo un'ora o una barra estrema va peggio del caso (ETH I-13 −2,09/−2,89; LINK V05/V06 −2,59/−3,13; BNB I-12 −2,13; MATIC I-09 −1,62/−2,70; SOL 009 −1,30; FTM 034 −2,08; AVAX V-28 −1,65; 1000SHIB 004 −2,33; FIL con R negativi): «dopo gli eccessi il prezzo continua» |

### 3.2 Famiglie che hanno dato i candidati

| Famiglia | Campagne | Varianti | Nette (b) | Cand. F2 | In validazione | Al vault | Come è finita |
|---|---|---|---|---|---|---|---|
| ultima mezz'ora (momento dentro la giornata) | 18 | 69 (33 ritocchi) | 34 | **25** (BTC 3, SOL 4, AVAX 4, ADA 2, FIL 7, 1000SHIB 2, ETC 3) | 0 | 0 | tutti e 25 caduti in Fase 4: costi doppi (BTC, SOL, AVAX, ADA, SHIB, ETC) e/o ritardo di una barra (BTC, SOL, FIL, ETC). Sei campagne scrivono la stessa cosa: l'effetto lordo esiste (BTC +0,045 R; SOL +0,04; AVAX +0,065; SHIB +0,08; ETC +0,045 R a trade) ed è più piccolo o uguale ai costi di un giro (0,05-0,14 R); ETC lo misura anche su BTC («è del mercato, non di ETC») |
| Williams | 9 | 19 | 3 | 3 (BTC V10, V11; FIL 025) | 2 (BTC V10; FIL 025 fallito) | 1 (BTC V10: non passa) | sezione 2.1 |
| intervallo d'apertura | 6 | 25 (13 ritocchi) | 6 (tutte su ADA) | 4 (tutte ADA) | 1 (ADA 037) | 1 (non passa) | sezione 2.3 |
| RSI(2) in tendenza | 20 | 40 | 3 (tutte BNB) | 3 (tutte BNB, ritocchi) | 1 (BNB 045) | 1 (non passa) | sezione 2.2 |
| relazione con BTC | 14 | 51 (12 ritocchi) | 2 | 2 (FIL 016 1h long; DYDX 008 1h long) | 1 (DYDX 008: R −0,178) | 0 | FIL 016 cade ai costi doppi (R −0,004); DYDX 008 passa la Fase 4, lo scettico smentisce il motivo («conta solo l'ora forte di BTC») e la validazione lo boccia. Sul gruppo di 80 monete la stessa idea (ritardo dopo un'ora forte di BTC) è la più vicina alla soglia (t 2,06 e 2,01 dopo 3 e 5 ritocchi, soglia 2,16), con effetto lordo +0,04-0,09 R contro costi 0,05-0,07 R |
| last/mark | 6 | 15 | 2 | 2 (XRP V21r3 1h long; GALA 032 1h short) | 1 (XRP: 5 trade) | 0 | XRP: 84 trade su 97 nel 2020, poi la condizione quasi non scatta; GALA: costi doppi (R −0,043) |
| inversione di breve | 21 | 61 | 3 | 1 (MASK 029) | 1 (p 0,293) | 0 | sopra |

### 3.3 Cosa succede sui timeframe (log, tutte le 21 campagne)

| Timeframe | Varianti | Long / short | t medio contro la (b) | Nette contro la (b) | Cand. F2 | In validazione | Al vault |
|---|---|---|---|---|---|---|---|
| 15m | 13 | 7 / 6 | 1,94 | 6 | 4 (ADA 3 long, 1 short) | 1 (ADA 037) | 1 (non passa) |
| 30m | 59 | 22 / 37 | 1,39 | 27 | 18 (3 long, 15 short) | 0 | 0 |
| 1h | 242 | 117 / 125 | 0,40 | 18 | 14 (8 long, 6 short) | 6 (BTC, BNB, XRP, FIL, DYDX, MASK) | 2 (non passano) |
| 2h | 14 | 7 / 7 | 0,28 | 0 | 0 | 0 | 0 |
| 4h | 160 | 86 / 74 | 0,39 | 10 | 9 (6 long, 3 short) | 0 | 0 |
| 8h | 30 | 17 / 13 | −0,46 | 0 | 0 | 0 | 0 |
| 1d | 112 | 62 / 50 | 0,19 | 4 | 0 | 0 | 0 |

Letture, con la fonte:
* **Sotto l'ora (15m e 30m) i `t` sono alti e i candidati molti (22 su 45), ma nessuno regge i costi.** 27 nette su 59
  a 30m, quasi tutte della famiglia «ultima mezz'ora» (sezione 3.2). A questi timeframe il costo di un giro vale
  0,05-0,14 R a trade (BNB: «su 30 minuti i costi, circa 0,14 R a giro, bastano a cancellare qualunque idea
  provata»; ADA: «sui timeframe corti il costo fisso di un giro decide tutto»; GALA, DYDX, LINK, ETC lo scrivono
  allo stesso modo). Inoltre a 15m e 30m la (b) ha spesso un R medio negativo in partenza (ADA −0,137 a 15m; TRB −0,151 e −0,273 a 15m;
  SOL −0,046 e −0,032, 1000SHIB −0,069 a 30m; dalle consegne), per cui «battere nettamente la (b)» e «guadagnare» sono due cose diverse: 10 varianti sono nette contro (a) e (b)
  con R medio non positivo (log; elenco: BTC V19 e V31, ETH 012, SOL 025, AVAX V11, ADA 024 e 038, 1000SHIB 029, ETC
  023 e 035).
* **A 1 ora stanno 6 dei 7 candidati in validazione e 2 dei 3 del vault**, ma il `t` medio è 0,40 e solo 18 varianti su
  242 sono nette: i candidati a 1h sono eccezioni in una distribuzione che somiglia al caso.
* **A 2h, 8h e 1d nessun candidato**; a 8h (funding) il `t` medio è negativo. A 4h e 1d gli R medi dei long sono i più
  alti (R medio medio +0,061 a 4h) ma la (b) long fa lo stesso: è il trend.
* Le regole legate a un'ora precisa (ultima mezz'ora, fascia 20-24 UTC, intervallo d'apertura) crollano per
  costruzione al ritardo di una barra (SOL, FIL, ETC, MATIC, AVAX lo spiegano: il trade slitta fuori dalla finestra).
  FIL e AVAX lo propongono come lezione di metodo (`lezioni_metodo_proposte.md`).

### 3.4 Long contro short (log)

* Varianti: 318 long, 312 short. R medio medio: long +0,041, short −0,017. R medio positivo: 151 long su 304, 130
  short su 296 (con `t` leggibile). Nette contro la (b): 25 long, 40 short. `t` medio: long 0,44, short 0,49.
* Candidati di Fase 2: 20 long, 25 short; ma 15 dei 25 short sono «ultima mezz'ora» a 30m, caduti ai costi.
* In validazione: 6 long (BTC, BNB, ADA, XRP, FIL, DYDX) e 1 short (MASK). Al vault: 3 long, 0 short.
* Le campagne leggono i long così: nel 2020-2021 «bastava essere long» (BTC lezione 1; BNB; ADA; LTC lezione 1; MATIC;
  AVAX; ETC lezione 1); gli short che guadagnano lo fanno nel 2022 (BCH: «un vantaggio di regime, non di regola»; FTM
  036; FIL lezione 3: «un risultato short va sempre letto contro la (b), mai contro zero»). I tre candidati del
  vault sono long e hanno tutti fatto bene nel 2024 (anno di rialzo) e male nel 2025-2026 (`vault/risultati.md`).

### 3.5 Ritocchi contro idee nuove (log e consegne)

111 ritocchi su 630 varianti (18%) hanno prodotto 34 candidati su 45 (76%); 519 idee nuove ne hanno prodotti 11.
Dei 7 in validazione, 4 erano ritocchi (BNB 045 quinto; ADA 037 quarto; XRP V21r3 terzo; MASK 029 secondo) e 3 idee
nuove (BTC V10; FIL 025; DYDX 008). Dei 3 al vault, 2 ritocchi e 1 idea nuova. Le campagne lo dicono da sole:
«salita a tentativi su una sola famiglia» (BTC lezione 5), «il migliore di 7 varianti della stessa famiglia e di 30
in tutto» (MASK), «le tre soglie sono state scelte sui quartili: la parte più probabilmente fortunata» (ETC), «il
caso più esposto alla fortuna di tutta la campagna» (BNB).

## 4. Riserve scritte dalle campagne e limiti dichiarati (Passo 7, punto 4, con la sezione 11 del protocollo)

### 4.1 Riserve delle campagne sui tre candidati del vault (scritte prima del vault)

**BTCUSDT-V10** (consegna BTCUSDT, «Rischi noti» e «In breve»): vantaggio «piccolo e fragile»; in validazione senza i
3 trade migliori l'R è negativo (−0,100); in validazione non batte nettamente la (b) (t 1,69 contro 2,04); passa
l'asticella solo perché unico candidato; il p-value è «probabilmente ottimista» perché la (b) è depressa dallo stop
all'apertura e la prova con lo stop fisso non si rifà in validazione; più di metà del rendimento di costruzione
viene dal 2020 e il 2021 è quasi zero; «30 varianti, un solo candidato rimasto è del tutto compatibile con il
caso»; slippage 0,01% ottimista per il 2020; stop oltre il 6% in circa il 5% dei trade. Previsione scritta: circa
40% di passare il vault, «il punto debole è il profit factor: prevedo 1,00-1,20» (è andato a 1,067).

**BNBUSDT-045** (consegna BNBUSDT, «Rischi noti»): il filtro del fine settimana è il migliore di 7 gruppi per giorno
visti sugli stessi dati, e il motivo economico del fine settimana è stato scritto dopo aver visto i numeri (nota
N018); 32 trade di validazione (due sopra il minimo), t sotto la soglia, senza i 3 migliori +0,008, i 4 trade del
2022 negativi; costi in validazione 0,079 R a trade, più dell'R medio (+0,047); quinto ritocco di una sola
famiglia; i due gemelli senza il filtro sono caduti al ritardo e per 045 l'R col ritardo scende da +0,138 a
+0,048; 3 stop su 74 contro il 14% della regola senza filtro; correlazione con BTC da 0,31 a 0,54; slippage 2020
ottimista; paper di circa 22 mesi (oltre i 12). Previsione: 25-35%.

**ADAUSDT-037** (consegna ADAUSDT, «Rischi noti», consegnato «con forti riserve», «non lo dichiaro validato»): il
risultato di validazione è fatto di 3 trade (0,624 → 0,014); la prova dello scettico attribuisce il vantaggio di
costruzione allo stato del mercato scelto dai filtri (t 0,63 contro la baseline filtrata); i filtri sono nati dai
dati di costruzione della stessa famiglia (quarto di 5 ritocchi); le baseline sono molto negative per la distanza
dello stop; il 2022 è negativo; slippage 0,02% ottimista per il 2020. Previsione: «più probabilmente fallisce, con
R medio vicino a zero o negativo»; «non mi aspetto che si trasferisca».

### 4.2 Riserve sugli altri candidati e sui risultati vicini alla soglia

* **XRPUSDT-V21r3**: terzo ritocco con due soglie scelte sui fallimenti; 84 trade su 97 nel 2020 («un solo regime»); dal
  2021 la condizione scatta 0,4 volte al mese; 21 trade con lo stop al tetto del 6%.
* **FILUSDT-025**: baseline gonfiate dai costi (stop vicinissimo), contro stop di distanza normale t 1,38; il guadagno
  sta nei giorni in cui sale tutto il mercato; 29% degli stop oltre il 6%; p 0,085 «alla lettera passa», dichiarato
  fallito dal proprietario per il principio «battere il caso perdendo meno di lui non è un vantaggio».
* **DYDXUSDT-008**: un solo candidato su 30 con t appena sopra la soglia (circa 12% di probabilità di almeno una
  netta per caso, con la quota della prova a placebo); motivo economico smentito dallo scettico; guadagno concentrato
  nel 2021 e a inizio 2023; «comportamento di regime, non vantaggio stabile».
* **MASKUSDT-029**: migliore di 7 varianti della stessa famiglia; filtro del funding e uscita a 12 barre da ritocchi; 32
  stop su 86 oltre il 6%; «la validazione dice che la parte "vantaggio" era con buona probabilità selezione e fortuna».
* **DOGEUSDT-042**: «un picco, non un'area stabile». **ETCUSDT-033/036/037**: soglie sui quartili; la regola «è legata
  all'orologio». **AVAXUSDT-V-14**: scartato dal ritardo «per una regola tarata per scoprire gli errori di lookahead»,
  effetto concentrato nelle prime barre, mediana dei trade vicina a zero. **1000SHIBUSDT-028/030**: «una parte del
  vantaggio sulla (b) è un effetto costi, non la direzione» (il t sale a costi doppi mentre l'R diventa negativo).
  **SOLUSDT**: «l'effetto lordo è legato alla fine della giornata UTC, ma è più piccolo dei costi». **MATICUSDT-025**:
  «l'effetto, se esiste, vale qualche ora e sta a ridosso del rumore».
* **Riepilogo del Passo 4** (indizio da rileggere al Passo 7): 6 candidati valutabili in validazione, 3 sotto la
  soglia; senza vantaggio ce ne aspetteremmo 0,2-0,6. Con il vault: 3 candidati, 0 passaggi, attesi per caso 0,02.

### 4.3 Limiti dichiarati nelle consegne (sezioni «Limiti» e «Rischi»), raccolti e deduplicati

1. **Potenza bassa.** Con 70-500 trade per variante un vantaggio di 0,03-0,10 R a trade non si distingue dal caso
   (ETH, SOL, MATIC, BCH, LINK, TRB, ETC, GRUPPO; sezione 11 del protocollo). «Nessuna strategia valida» non vuol dire
   «nessun vantaggio» (ETC, GRUPPO). Per il gruppo si aggiunge l'effetto grappolo (fino a 33) e la poca potenza della
   (a) di gruppo con tenute lunghe (controllo positivo passato solo con l'uscita a 1 giorno).
2. **Slippage della scheda ottimista** per il 2020-2021 (fascia calcolata sul volume del 2023): BTC, ETH, SOL, BNB, LTC,
   MATIC, BCH, AVAX, ADA, TRB (fascia giusta 0,10% nel 2020-21), DYDX, ETC, LINK. Solo FTM dichiara la sua prudente.
   Con zero passaggi non cambia l'esito: costi più alti abbassano tutto.
3. **Periodo corto e dominato da un rialzo e un ribasso** (2020-21 e 2022): le strategie lente sono spiegate dal
   trend, che la (b) assorbe (12 campagne); storia utile di circa 2 anni per SOL, FTM, DYDX (596 giorni), GALA, MASK,
   1000SHIB, DOGE (ingressi solo dal 2021); 2 anni in costruzione per FTM, MATIC.
4. **Stop agganciato a un livello di prezzo** (apertura del giorno, estremi dell'intervallo, ATR nei giorni volatili):
   gonfia il confronto con le baseline (BTC, ADA, FIL, LTC, 1000SHIB). FIL lo propone come lezione di metodo.
5. **Costi a 15-30 minuti e 1 ora** decidono il risultato (BNB, ADA, DYDX, GALA, LINK, ETC, 1000SHIB, AVAX, GRUPPO);
   il protocollo conta tutto come taker, mentre il bot entrerebbe con ordini limit (ETC lo nota).
6. **Regole legate all'orologio crollano al ritardo di una barra per costruzione** (SOL, FIL, ETC, MATIC, AVAX): il test
   del ritardo scarta regole legate all'ora, lookahead o no (FIL e AVAX, lezioni di metodo proposte).
7. **Idee scritte dopo i primi risultati, dichiarate**: ETH I-15…I-18 (I-18 dai fallimenti); LTC I-11; LINK I-14, I-15;
   GALA I-14…I-17; AVAX seconda tornata (senza aver visto risultati); MATIC ha tolto un'idea contaminata da un
   articolo del 2024; GALA 027 ritirata. Nessuna di queste è arrivata in validazione.
8. **Vault non perfettamente cieco e stesso modello**: chi scrive sa a grandi linee com'è andata la moneta dopo il
   2023 (SOL, TRB, FTM); le fonti sono note al modello; le campagne sono «indipendenti nel metodo, non nel giudizio»
   (TRB); mercato comune (ETC: l'effetto di fine giornata c'è anche su BTC; BNB: correlazione con BTC).
9. **Il bot non può eseguire così come sono** quasi tutte le regole vicine alla soglia: serve il percorso «coppia del
   protocollo» (tutte); i timeframe 30m e 2h-1d non sono dal vivo (SOL, 1000SHIB, ETC, GRUPPO); stop oltre il 6% (BTC
   5% dei trade; BNB 8 su 74; FIL 29%; AVAX V-14 98 su 113; MASK 32 su 86; GALA 78 su 325; XRP 21; DYDX 17%; LINK, FTM e
   GRUPPO a 1d con stop del 31-33%; ETC I-01 tre trade su quattro).
10. **Dati**: mark price mancante in giornate intere (MATIC 6; AVAX luglio 2021 e tre altri giorni; DYDX 2; ETC 2; nel vault un giorno di giugno 2026);
    mesi esclusi per liquidità (DOGE tutto il 2020; TRB 7 mesi su 28 di costruzione e 5 su 12 di validazione; MATIC,
    FTM, BNB, ADA, LINK, ETC alcuni mesi); funding di ICPUSDT assente per 16 mesi nel gruppo; il 2019 escluso per
    tutte.
11. **Il guardiano** giudica le azioni, non gli script (SOL, GRUPPO); 4-9 rifiuti di forma per campagna, nessuno
    aggirato (tutte).
12. **Processo**: durate dal log di 25-80 minuti per campagna (i minuti per idea misurano il calcolo, non il
    ragionamento; XRP e FTM notano che l'orologio non è verificabile); BTCUSDT ha lavorato con la regola dei ritocchi
    della 4.4 (2 varianti nette con R non positivo), e il proprietario ha deciso di non rifarla (riepilogo Passo 4);
    FIL ha avuto una pausa di 92 minuti per una domanda; SOL una di 4 ore e 20.
13. **Ritocchi concentrati** su 1-2 famiglie per campagna, come vuole la regola 6: i `t` più alti sono «il massimo di 5
    tentativi e vanno letti con questo sconto» (GRUPPO; stesso avviso in BTC, BNB, ADA, ETC, MASK, DOGE).

## 5. Fonti citate dalle campagne per le idee con i `t` migliori

Senza giudizi. Per ogni fonte: titolo, autori, anno, come scritti in `ipotesi.md`; e dove ha dato il `t` più alto.

* Larry Williams, «Long-Term Secrets to Short-Term Trading», Wiley, 1999 — BTCUSDT-V10 e V11 (candidati), FILUSDT-025
  (candidato), ETH, DOGE, BCH, LINK, AVAX, FTM, GALA.
* Toby Crabel, «Day Trading with Short Term Price Patterns and Opening Range Breakout», Traders Press, 1990 —
  ADAUSDT-037 (candidato) e l'intervallo d'apertura su LTC, TRB, XRP, MASK, ETC; NR7 su BTC, ETH, SOL, DOGE, DYDX, GALA.
* Larry Connors, Cesar Alvarez, «Short Term Trading Strategies That Work», TradingMarkets Publishing, 2008 —
  BNBUSDT-043, 044, 045 (candidati); provata su 20 campagne.
* Lei Gao, Yufeng Han, Sophia Zhengzi Li, Guofu Zhou, «Market intraday momentum», Journal of Financial Economics
  129(2), 2018 — BTCUSDT-V35 (t 3,58), SOLUSDT-023 (2,78), AVAXUSDT-V-12 (3,52), FILUSDT-035 (3,40), 1000SHIBUSDT-030
  (2,15), ETCUSDT-035 (3,85), TRB, DYDX, MASK, XRP, GALA.
* Dehua Shen, Andrew Urquhart, Pengfei Wang, «Bitcoin intraday time series momentum», The Financial Review 57(2), 2022 —
  la stessa idea su ETH, DOGE, BNB, MATIC, LINK, FTM.
* Zhuzhu Wen, Elie Bouri, Yahua Xu, Yang Zhao, «Intraday return predictability in the cryptocurrency markets:
  Momentum, reversal, or both», North American Journal of Economics and Finance 62, 2022 — ADAUSDT-039/040 (candidati
  caduti), AVAX (seconda fonte), MATIC I-09.
* Songrun He, Asaf Manela, Omri Ross, Victor von Wachter, «Fundamentals of Perpetual Futures», arXiv 2212.06888, 2022 —
  XRPUSDT-V21r3 (candidato, t 2,33), GALAUSDT-032 (candidato, 2,22); funding su BTC, DOGE, MATIC, BCH, AVAX, ADA.
* Andrew W. Lo, A. Craig MacKinlay, «When Are Contrarian Profits Due to Stock Market Overreaction?», Review of
  Financial Studies 3(2), 1990 — DYDXUSDT-008 (candidato, 2,22); ETH, ADA, 1000SHIB, FTM, GALA.
* Dimitrios Koutmos, «Return and volatility spillovers among cryptocurrencies», Economics Letters 173, 2018 —
  GRUPPO-048 e 046 (t 2,06 e 2,01, le più vicine del gruppo).
* Kewei Hou, Tobias J. Moskowitz, «Market Frictions, Price Delay, and the Cross-Section of Expected Stock Returns», The
  Review of Financial Studies 18(3), 2005; Imtiaz Mohammad Sifat, Azhar Mohamad, Mohamed Shariff, «Lead-Lag
  relationship between Bitcoin and Ethereum: Evidence from hourly and daily data», Research in International Business
  and Finance 50, 2019 — FILUSDT-016 (candidato, 2,35); AVAX, MASK.
* Narasimhan Jegadeesh, «Evidence of Predictable Behavior of Security Returns», Journal of Finance 45(3), 1990; Bruce N.
  Lehmann, «Fads, Martingales, and Market Efficiency», Quarterly Journal of Economics 105(1), 1990 — MASKUSDT-029
  (candidato, 2,85); SOL, FIL, 1000SHIB, FTM.
* Carol L. Osler, «Support for Resistance: Technical Analysis and Intraday Exchange Rates», Federal Reserve Bank of New
  York Economic Policy Review 6(2), 2000 — ETHUSDT-026 (candidato, 2,67).
* John Bollinger, «Bollinger on Bollinger Bands», McGraw-Hill, 2001 — DOGEUSDT-042 (candidato, 2,14).
* Tarun Chordia, Avanidhar Subrahmanyam, «Order imbalance and individual stock returns: Theory and evidence», Journal
  of Financial Economics 72(3), 2004; E. Silantyev, «Order flow analysis of cryptocurrency markets», Digital Finance 1,
  2019 — MATICUSDT-025 e 026 (2,12 e 2,21).
* Guglielmo Maria Caporale, Alex Plastun, «Price overreactions in the cryptocurrency market», Journal of Economic
  Studies 46(5), 2019 — AVAXUSDT-V-14 (candidato, 2,68).
* Adam Kozlowski, Michael Puleo, Jian Zhou, «Cryptocurrency return reversals», Applied Economics Letters 28(11), 2021 —
  LINKUSDT-V24 (2,23).
* Tobias J. Moskowitz, Yao Hua Ooi, Lasse Heje Pedersen, «Time series momentum», Journal of Financial Economics 104(2),
  2012; Yukun Liu, Aleh Tsyvinski, «Risks and Returns of Cryptocurrency», NBER Working Paper 24877, 2018 (Review of
  Financial Studies 34(6), 2021) — FTMUSDT-036 (2,22), BCHUSDT-002 (1,62); provata su tutte le 21 campagne.
* Steven L. Heston, Robert A. Korajczyk, Ronnie Sadka, «Intraday Patterns in the Cross-Section of Stock Returns», The
  Journal of Finance 65(4), 2010 — FILUSDT-024 (candidato, 2,20).
* Zhi Da, Qianqiu Liu, Ernst Schaumburg, «A Closer Look at the Short-Term Return Reversal», Management Science 60(3),
  2014 — GRUPPO-050/051 (1,80 e 1,89, seconda famiglia del gruppo).

## 6. Cosa resta e cosa non è stato fatto

* **Passo 5, punto 2 e Passo 6** (dati del vault delle altre 17 monete, trasferimento dei candidati sulle altre monete):
  non fatti, per decisione del proprietario del 12 ottobre («sì, salta e passa alla conclusione»), con i tre candidati
  bocciati nel loro vault. Nessun numero fuori campione per le altre monete, nessuna «idea di gruppo» possibile.
* **Passo 7, punto 3**: fatto il 12 ottobre. I 21 branch `research/campagna/<SIMBOLO>` e `research/coordinamento` sono
  uniti nel branch principale (22 commit di unione); per i file condivisi (`PROTOCOLLO.md`, `src/`, `config/`, test,
  `CHANGELOG.md`, `lezioni/metodo.md`) resta la versione del principale, sempre più avanti; i file di lavoro
  voluminosi della campagna di gruppo (`trade/`, `avanzamento/`, 114 MB) sono tolti dal principale e restano nel
  branch. `lezioni/metodo.md` ha la sezione del Passo 7 in fondo; `confronto/lezioni_comuni.md` è nuovo. I tre branch
  `research/archivio/campagna/*` della prova di processo restano archiviati, non uniti.
* **Passo 8** (combinazione) e **Passo 9** (paper): solo se il proprietario li chiede; senza candidati passati nel vault
  non hanno oggetto.
* **Limiti di questo file.** Per BTCUSDT, BNBUSDT, ADAUSDT, MATICUSDT, BCHUSDT, AVAXUSDT, DYDXUSDT e FILUSDT la
  consegna non ha la tabella completa variante per variante: i numeri per variante vengono da `lezioni_moneta.md` e dal
  log. Le voci di validazione nei log non hanno un formato uniforme: i numeri dei 7 candidati sono presi dalle consegne
  e dal riepilogo del Passo 4. L'assegnazione delle famiglie è una scelta del coordinamento: nei casi di confine
  un'altra assegnazione cambierebbe i conteggi di qualche unità, non il quadro.
