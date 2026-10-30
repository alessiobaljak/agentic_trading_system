# Programma 7 — settantatreesima prova: il funding di Hyperliquid contro quello di Binance (HL)

Scritto il 30 ottobre 2026 alle 06:18 UTC (ora dell'orologio), **prima di qualunque calcolo**. È l'idea 110 della coda (dalla ricerca
nelle pubblicazioni del 29 ottobre). Fino a qui si è solo controllato che l'API pubblica di Hyperliquid risponda: lo storico del funding
parte dal maggio 2023, l'elenco di oggi ha 235 monete, e per le monete tolte (per esempio LUNA) l'API non dà niente.

## 1. Perché

* **Hyperliquid è una piattaforma di perpetui sulla catena**, con una clientela diversa da Binance: molti speculatori, pochi
  arbitraggisti istituzionali. Secondo BitMEX (rapporto del secondo trimestre 2026, letto da un articolo) Hyperliquid ha pagato in media
  il 7,17% l'anno più di Binance sul Bitcoin e il 5,31% sull'Ether fra il 2023 e il 2026.
* **L'ipotesi**: dove su una moneta Hyperliquid paga molto più di Binance, l'eccesso di leva sta lì e l'arbitraggio non basta a toglierlo;
  il prezzo della moneta dovrebbe soffrirne anche su Binance. È la famiglia che regge, «chi paga la leva perde», con una misura
  dell'affollamento presa fuori da Binance.
* **I dubbi scritti prima**:
  * la prova 132 (il funding in moneta contro quello in USDT) ha appena detto che lo scarto fra due funding non aggiunge niente al
    livello; uno studio pubblico su 791 perpetui dice lo stesso del funding di altre piattaforme;
  * lo storico è corto (dal maggio 2023) e all'inizio le monete su Hyperliquid sono poche;
  * **sopravvivenza**: l'API dà lo storico solo delle monete ancora quotate oggi su Hyperliquid. Il confronto con G1 sulle stesse monete
    ha lo stesso difetto, quindi resta giusto; i numeri assoluti no.

## 2. La regola (fissata qui)

* **Dati**: il funding di ogni moneta dell'elenco di oggi di Hyperliquid (`fundingHistory`), sommato per giorno di tenuta con la
  convenzione del pannello (`seconda.pannello`: il regolamento delle 00:00 lo paga chi ha tenuto il giorno prima), salvato in
  `research/data/hyperliquid/` fuori da git. La moneta si abbina al perpetuo di Binance con il nome (`XYZ` → `XYZUSDT`, `kXYZ` →
  `1000XYZUSDT`).
* **Il segnale**, ogni giorno alle 00:00 come G1: la somma del funding di Hyperliquid dei 7 giorni prima meno quella del funding di
  Binance degli stessi 7 giorni, arrotondata a 12 decimali; solo le monete con il funding di Hyperliquid in tutti e 7 i giorni.
* **Il portafoglio, come G1**: fra le monete dell'universo di G1 del giorno con il segnale, **short il quinto con lo scarto più alto,
  long il quinto con il più basso**, banda 20/40, pesi secondo l'inverso della volatilità, almeno 20 monete; ordini limite e costi come
  G1 (`cinquantaduesima.conto`); si opera solo su Binance.
* **Periodo**: dal 5 giugno 2023 (il primo lunedì dopo un mese di storico di Hyperliquid) al 5 ottobre 2026 (`prima.FINE`).
* **Una variante**: nel conto delle prove diventano **232**.

## 3. L'esame

* **Come le prove a portafoglio** (`terza.esame`, `terza.esito`, con il Bitcoin come riferimento; anni pieni 2024 e 2025): lo Sharpe
  corretto con l'aggiunta sopra 0,95, il t contro 3 e la regola del proprietario del 24 ottobre.
* **E in più**: lo Sharpe di HL deve essere sopra quello di **G1 sulle stesse monete e negli stessi giorni**.
* **Se regge**, passa da un revisore separato prima del paper.
* **Per capire, senza decidere niente**: quante monete hanno il segnale ogni giorno; lo scarto medio fra Hyperliquid e Binance; la
  correlazione fra lo scarto e il funding di Binance; i due lati; per anno; la media dei ranghi con G1.
