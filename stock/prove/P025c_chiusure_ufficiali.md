# Controllo dopo la revisione della prova 37 — la miscela del demo con le chiusure ufficiali di SPY e QQQ

Metodo scritto il 17 novembre 2026 **prima di calcolare**. **Non è una prova** (le regole delle prove 15, 16 e 25 non cambiano e non
entra nel conto): rifà gli stessi calcoli cambiando un solo dato.

## Perché

Il revisore della prova 37 (`REVISIONE_P037.md`) ha trovato che le chiusure giornaliere di SPY di Alpaca, nell'archivio delle prove,
differiscono da quelle ufficiali; la sessione l'ha controllato contro Yahoo: in marzo 2020 14 giorni su 22 oltre 5 punti base (fino a
287), nel 2019 15 su 252 (`STATO.md`, «Cosa non è fatto»). Le prove 15 e 16 decidono e si eseguono con le barre al giorno di SPY e QQQ
dell'archivio, e sono quattro delle sei parti della **miscela della prova 25, che gira sul conto demo dal 13 novembre**. La domanda: il
risultato della miscela (Sharpe con i costi 1,08 contro 0,89 del tenere lo SPY, `P025_risultati.md`) regge con le chiusure ufficiali?

## Come

* Per SPY e QQQ, sugli stessi giorni dell'archivio (dal 4 gennaio 2016 al 31 dicembre 2024, mai oltre), apertura, massimo, minimo e
  chiusura **di Yahoo** al posto di quelli di Alpaca (volume e dividendi restano quelli dell'archivio); si contano prima i giorni in cui
  le due fonti differiscono di più di 5 punti base, all'apertura e alla chiusura.
* Le prove 15 e 16 si rifanno con gli stessi programmi (`p005.esegui`, stesse regole, stessi costi); l'ampiezza della prova 16 resta
  calcolata come prima sulle azioni dell'S&P 500. La prova 7 (minuti) non cambia.
* La miscela si ricalcola come nella prova 25 (media delle sei parti) e il tenere lo SPY e metà SPY metà QQQ con le stesse chiusure di
  Yahoo. I risultati vanno in `P025c_risultati.md`; le serie nuove **non** sostituiscono quelle committate.

## Che cosa se ne fa (scritto prima)

* Se lo Sharpe con i costi della miscela resta sopra quello del tenere lo SPY e di metà SPY metà QQQ: la miscela resta sul demo come
  è, e si annota.
* Se scende sotto: lo si scrive subito al proprietario; la miscela sul demo l'ha decisa lui, e spegnerla o cambiarla è una sua
  decisione (8 novembre).
