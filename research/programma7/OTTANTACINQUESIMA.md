# Programma 7 — ottantacinquesima prova: le notizie, conferma sul 2026 (GA2 al contrario sull'archivio katelabs)

Scritto il 1° novembre 2026 alle 12:34 UTC (ora dell'orologio), **prima di qualunque calcolo**: dell'archivio si sono letti solo la scheda
e la dimensione del file. Nasce dalla domanda del proprietario del 1° novembre («perché il 30 novembre? devo per forza aspettare un
mese?»): invece di aspettare i 28 giorni della nostra raccolta, la regola si prova subito su notizie del 2026 che nessuna prova ha mai
usato.

## 1. Perché

* La prova 138 ha trovato, sull'archivio CoinDesk dal 2021 al gennaio 2025, che **GA2 al contrario** (comprare le monete molto citate
  rispetto a quanto si scambiano, vendere quelle molto scambiate di cui nessuno scrive) faceva Sharpe 0,93. È nata guardando quei dati:
  va confermata su dati mai usati.
* **I dati nuovi**: l'archivio pubblico katelabs (Hugging Face, `katelabs/crypto-news-scored`, licenza CC BY-NC 4.0, uso di ricerca):
  25.407 titoli di 54 giornali dal 1° febbraio al 30 aprile 2026, con le monete di cui parla ogni titolo (`coins`) e l'ora in cui il
  titolo è stato raccolto (`ingested_at`). Salvato in `research/data/notizie_katelabs/`, fuori da git.
* **I dubbi scritti prima**: le settimane misurabili sono poche (8), quindi questa prova dice il verso e l'ordine di grandezza, non
  dimostra niente da sola; i giornali sono diversi da quelli di CoinDesk.

## 2. La regola (fissata qui, identica a `research/notizie/REGOLE.md` sezione 3)

* Una moneta è citata in un titolo se la sua sigla è nel campo `coins`; la sigla si abbina al perpetuo di Binance con
  `annunci.perpetuo`. Conta il giorno di `ingested_at` (quando il titolo era davvero noto).
* Ogni lunedì l, per ogni moneta dell'universo di G1 della settimana: log((titoli dei 28 giorni fino a l − 2 + 1) / volume in dollari
  del perpetuo negli stessi giorni); **long il quinto con il valore più alto, short il quinto con il più basso**, banda 20/40, pesi
  secondo l'inverso della volatilità, almeno 20 monete con almeno 3 titoli nei giorni dell'archivio fino a l − 2, costi e funding come F5
  (`terza.conto`).
* **Le settimane**: i lunedì con tutti i 28 giorni dentro l'archivio, dal 9 marzo al 27 aprile 2026 (8 settimane).
* **Una prova** (la conferma di un'idea nata dai dati): nel conto delle prove diventano **245**.

## 3. L'esame (scritto prima)

* **Conferma** se nelle 8 settimane il rendimento medio dopo i costi è sopra zero **e** sopra quello di G1 nelle stesse settimane
  (`risultati_ottantesima/settimane_G1.csv.gz`). Con 8 settimane non si calcola un intervallo che decida: si riportano media, settimane
  positive e il confronto con G1.
* **Se conferma**: la regola entra nel conto a tavolino appena la nostra raccolta ha i suoi 28 giorni (30 novembre) e, per la delega del
  proprietario del 22 ottobre, anche nel paper del bot, senza aspettare altro. **Se non conferma**: resta solo la misura in avanti.
* **Per capire**: quante monete hanno il segnale ogni settimana; il verso della prova 138 (GA2 com'era scritta).
