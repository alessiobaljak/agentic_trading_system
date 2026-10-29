# Programma 7 — sessantottesima prova: le emissioni nuove di Tether e il Bitcoin nelle 24 ore dopo (TE)

Scritto il 29 ottobre 2026 alle 20:27 UTC (ora dell'orologio), **prima di qualunque calcolo dei rendimenti**. È l'idea 104 della coda.
Fino a qui si sono solo contate le emissioni (nessun prezzo guardato): sulla catena Tron, dall'archivio pubblico di TronGrid, 287
emissioni dal 2019, di cui 124 da almeno 500 milioni di dollari dal 2021 (2021: 42, 2022: 11, 2023: 16, 2024: 16, 2025: 26, 2026: 13).

## 1. Perché

* **Tether stampa dollari digitali nuovi** quando qualcuno li chiede per comprare crypto (o quando li prepara per chi li chiederà). Griffin
  e Shams (2020, *Journal of Finance*): nel 2017-2018 il Bitcoin saliva nelle ore dopo le emissioni di Tether.
* **L'emissione si vede subito sulla catena** (in pochi minuti la scrivono i servizi che seguono i grandi movimenti), quindi è un evento
  con l'ora esatta, pubblico e noto prima della decisione.
* **I dubbi scritti prima**:
  * gli studi dopo il 2018 non trovano l'effetto, e la prova 44 (l'offerta delle stablecoin, a settimana) non ha retto;
  * spesso Tether stampa in anticipo, per una domanda che arriva giorni dopo;
  * si usa **solo Tron**: lo storico degli eventi di Ethereum non si legge gratis (i nodi pubblici non tengono la storia vecchia, gli
    archivi chiedono una chiave), quindi le emissioni su Ethereum mancano e finiscono anche nelle ore del controllo.

## 2. La regola (fissata qui)

* **Gli eventi**: le emissioni («Issue») del contratto USDT su Tron, salvate in `research/data/tether/tron_issue.json` fuori da git. Le
  emissioni a meno di un'ora l'una dall'altra si sommano. Un evento è una somma di **almeno 500 milioni**; al massimo un evento ogni 24
  ore. Dal 1° gennaio 2021 al 30 settembre 2026.
* **L'operazione**: long il perpetuo del Bitcoin dall'apertura dell'ora dopo quella dell'emissione, per 24 ore. Costi a mercato del
  Bitcoin (`ventunesima.COSTO_BTC`, 0,12%) e funding (un terzo del funding del giorno per ogni regolamento delle 00, 08 e 16 UTC dentro
  la tenuta).
* **Una prova a eventi**: nel conto delle prove diventano **226**, le prove a eventi **39**.

## 3. L'esame

* **Come le prove a eventi** (`trentesima.esame`, ricampionamento per settimana): media per evento sopra zero con **p ≤ 0,01**, positiva
  nelle due metà e senza i 5 eventi migliori, **e sopra il controllo** (differenza con p ≤ 0,05). Contando le 39 prove a eventi la
  soglia è **0,00026**.
* **Il controllo**: la stessa operazione in 20 ore prese a caso (seme 2026) per ogni evento, fra 7 e 60 giorni prima o dopo, lontane
  almeno 48 ore da ogni emissione su Tron di almeno 100 milioni.
* **Se regge**, passa da un revisore separato prima del paper.
* **Per capire, senza decidere niente**: le tenute di 1, 4 e 72 ore; le emissioni da almeno un miliardo; per anno; le altcoin (l'Ether)
  nelle stesse 24 ore.
