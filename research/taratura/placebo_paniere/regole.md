# Prova a placebo dell'esame di gruppo a barre giornaliere (seconda edizione) — regole scritte PRIMA dei numeri

> **In vigore dal 13 ottobre 2026** (Passo 0 della seconda edizione, `research/PROTOCOLLO_2.md`, sezione 7, punto 2):
> «la prova a placebo si rifà a barre giornaliere prima della prima variante; se non regge, STOP». Scritta dal
> coordinamento prima di qualunque numero; non cambia. Una correzione è una voce nuova in `risultati.md`.

## 1. Che cosa si prova

L'esame di gruppo (`research/src/gruppo.py`, regole in `research/campagne/GRUPPO/regole.md`, sezione 5) giudicò
sui prezzi veri delle 80 monete, a 1 ora e a 4 ore, 192 strategie finte senza vantaggio e non le scambiò per un
vantaggio (`research/taratura/placebo_gruppo/risultati.md`: 0 «nette» su 85 in costruzione, 2 su 93 sotto p 0,10
in validazione). La seconda edizione usa candele di **1 giorno**: le barre sono 24 volte meno, il blocco del
bootstrap è grande rispetto ai trade, l'uscita a tempo dura giorni. La domanda è la stessa: **l'esame regge anche
a barre giornaliere?**

## 2. Le strategie finte (identiche alla prova a 1 ora, con tre numeri in giorni)

* Le sei regole da manuale di `placebo_gruppo.py` (incrocio di medie, RSI, rottura dei 20, Bollinger, MACD, momento
  10), long e short; uscite: ATR (stop 1,5 e target 2,5 ATR(14)) o tempo (stop 2 ATR(14), uscita dopo **10 barre**
  = 10 giorni); nessun segnale nelle prime 60 barre.
* Gli ingressi sono gli istanti di segnale di ogni regola SPOSTATI tutti dello stesso intervallo d (sfasamento
  comune, in cerchio sulla finestra: regole del gruppo, sezione 11, punto 3), per k = 0, 1, 2, 3 → 6 regole × 2
  direzioni × 1 timeframe × 4 k = 48 placebo per periodo, 96 in tutto (costruzione e validazione).
* Timeframe: **solo 1d**. I dati sono i file giornalieri delle 80 monete scaricati al Passo 0 (impronte in
  `research/campagne/PANIERE/impronte_1d.json`), con le schede e l'elenco di `research/campagne/PANIERE/`.

## 3. L'esame e le misure

* `gruppo.esame_di_gruppo` con `timeframe="1d"`, con `ingressi_placebo` (regole del gruppo, sezione 11, punto 5),
  radice di lettura fuori da git; in costruzione prima `conta_trade_di_gruppo` (scarto sotto 700 trade sommati o con
  una moneta oltre il 10%: la placebo non si giudica); in validazione si giudica con almeno 300 trade sommati.
* Le misure le calcola `riassunto.py` della prova a 1 ora, puntato su questa cartella: per periodo, quante placebo
  valutabili, quante «nette» in costruzione, quante con p sotto 0,10 in validazione, la distribuzione dei t.

## 4. Le soglie (le stesse del gruppo: `parametri.yaml`, `gruppo.placebo_soglie`)

* costruzione: «nette» al massimo il 3% delle placebo valutabili (netta_costruzione_max 0,03);
* validazione: p sotto 0,10 al massimo il 13% (p_sotto_010_validazione_max 0,13: il 10% atteso più il margine);
* almeno 80 placebo valutabili per periodo? **No**: con un solo timeframe le placebo per periodo sono 48; la soglia
  del gruppo (80) era pensata per 96 per periodo. Qui si chiede che almeno **40 su 48** siano valutabili per periodo
  (placebo_valutabili_minime_per_periodo 40), scritto prima: con meno, la prova non dice niente e si rifà con più
  sfasamenti (k da 4 a 7) prima di qualunque variante.
* L'esame regge se le tre valgono. Se cade, STOP: si corregge l'esame (non le soglie) e si rifà la prova.

## 5. Come si lancia

`python research/taratura/placebo_paniere/esegui.py --radice-dati research --lavoro <cartella fuori da git>`:
riusa il lanciatore della prova a 1 ora (`research/taratura/placebo_gruppo/esegui.py`) con i file di questa cartella,
le serie 1d, l'elenco e le schede del paniere; stesse impronte e stessi controlli di identità, ramo remoto quello
principale. Gli esiti vanno in `esiti_k<k>.jsonl` di questa cartella; il riassunto in `risultati.md`.

## 6. Le impronte degli strumenti al lancio (scritte dal coordinamento, 13 ottobre 2026)

I cinque file dell'esame, come li vede `gruppo.impronte_degli_strumenti()` al momento del lancio vero; il
lanciatore rifiuta di partire se un file sul disco non ha questa impronta.

* `7f530082d7d5119d9e12e99a0bbe44548f9671c9b28aa70f77f97d6c2b4edfa7`  `research/config/parametri.yaml`
* `4f0d47790d23801d0d5f66ec01f4f901558179051bc4d632a6825eccaa877af4`  `research/src/dati.py`
* `6875b12f5dfbeb6fc505fbb5302befe0ad652e0a96330e85e69b46ff772efd3a`  `research/src/gruppo.py`
* `2adb94e11196e9af4dcc9f2b07ac42ad6a8cfda1399b5171f019585c8f5f78f6`  `research/src/motore.py`
* `ca027d2687d9129a533077eb980c0517bd09c476331659d61eaf15dda45c9e5a`  `research/src/statistica.py`

## 7. Correzioni (solo in aggiunta)

### Correzione 1 — i parametri delle regole da manuale per il giorno (13 ott 2026, 21:55 UTC, prima di qualunque esito)

**Cosa è successo.** Con le sei regole e i parametri della prova a 1 ora (`placebo_gruppo.py`: medie 20/50, RSI 14,
rottura 20, Bollinger 20 con 2 deviazioni, MACD 12/26/9, momento 10, uscita a tempo 10 barre) le prime 11 placebo
a barre giornaliere davano 227-420 trade sommati in costruzione sulle 80 monete (`conta_trade_di_gruppo`), sotto
il minimo di 700: tutte «scarto», nessun giudizio. Il lancio è stato fermato all'undicesima; le 11 righe (solo
scarti, nessun esame) sono state cancellate con la loro identità, perché una prova fatta di soli scarti non prova
niente.

**Cosa cambia.** Le sei regole restano le stesse, con parametri da manuale più corti per il giorno, scritti in
`placebo_paniere.py` (il modulo di QUESTA prova, con la sua impronta nell'identità): medie 5/20, RSI 7 (30/70),
rottura 10, Bollinger 10 con 1,5 deviazioni, MACD 5/13/4, momento 5; uscita a tempo 5 barre; ATR(14) e multipli
come prima; riscaldamento 60 barre. Scelti **contando i trade e basta** (mai guardando un rendimento): in un
lancio di funzionamento (righe segnate, mai un esito) con k = 0 in costruzione danno 714-3.742 trade sommati per
placebo (incrocio di medie 885/897, RSI 1.211/823, rottura 802/714, Bollinger 1.474/2.421, MACD 1.831/1.344, momento
3.097/3.742, long/short), tutte sopra 700.

**Perché non si abbassa il minimo.** L'esame della campagna giudica solo varianti con almeno 700 trade sommati in
costruzione; la placebo deve avere la stessa taglia, altrimenti prova un esame che la campagna non usa.
