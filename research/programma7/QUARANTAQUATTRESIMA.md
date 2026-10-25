# Programma 7 — quarantaquattresima prova: l'effetto della quotazione su OKX, conferma della prova 105 (CBO)

Scritto il 25 ottobre 2026, alle 12:52 UTC, **prima di qualunque calcolo sui prezzi**, mentre il revisore separato controlla la prova
105. È una **prova di conferma**: la regola della prova 105 (l'effetto Coinbase) identica, sugli eventi di un'altra borsa grande. Le date
vengono dall'elenco pubblico dei prodotti a pronti di OKX (`www.okx.com/api/v5/public/instruments?instType=SPOT`, campo `listTime`,
letto il 25 ottobre 2026; `research/data/okx_primi_giorni.json`, fuori da git). Il controllo di fattibilità ha contato solo le date: 96
monete quotate su OKX contro dollaro o stablecoin dal 2021 con il perpetuo di Binance da almeno 30 giorni, ma **43 tutte il 29 gennaio
2021**: è una data tecnica (la migrazione dei prodotti), non una quotazione. Solo 3 eventi cadono entro 7 giorni da una quotazione su
Coinbase: il campione è quasi indipendente dalla prova 105.

## 1. Perché

Se il guadagno della prova 105 viene davvero da «si compra sulla voce, si vende sulla notizia» quando una borsa grande apre una moneta al
suo pubblico, deve vedersi anche con le quotazioni di OKX. Se non si vede, la prova 105 è più probabilmente un caso o un effetto proprio
di Coinbase. **Il dubbio scritto prima**: il pubblico di OKX è diverso (asiatico, più esperto, meno al dettaglio di Coinbase); gli eventi
validi sono circa 50; il `listTime` può non coincidere con l'apertura vera degli scambi.

## 2. La regola (identica alla prova 105)

* **Evento**: il primo giorno L di un prodotto OKX contro dollaro o stablecoin (USDT, USDC, USD) per la moneta, con il perpetuo di Binance
  nato almeno 30 giorni prima di L e volume sopra zero il giorno L; L dal 1° gennaio 2021 al 1° ottobre 2026. **Fuori i giorni con 10 o
  più quotazioni** (date tecniche).
* **Operazione, controllo, costi, funding**: come la prova 105 (`quarantatreesima.operazione`): short il perpetuo di Binance e long il
  Bitcoin dall'apertura di L+1, uscita a +30% o dopo 7 giorni; controllo sulle stesse monete in 20 giorni presi a caso fra i 60 e i 365
  giorni dopo.
* Prova di conferma: **non entra nel conto** (come le conferme delle prove 4, 5 e 7).

## 3. L'esame

La conferma riesce se la media è sopra zero con **p ≤ 0,05** (bootstrap per settimana) e sopra il controllo sulle stesse monete. Si
riportano per anno e il confronto con la prova 105.
