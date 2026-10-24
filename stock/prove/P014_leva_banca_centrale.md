# Prova 14 — sempre investiti, con la leva nelle 24 ore prima della banca centrale (SPY, QQQ)

Regole scritte il 24 ottobre 2026 **prima di qualsiasi calcolo** (idea I11 di `REGISTRO.md`; richiesta del proprietario del 24 ottobre:
«prova la leva nei giorni prima della banca centrale»), committate prima di lanciare il programma.

## Perché, e perché decide solo il periodo chiuso

La prova 7 ha trovato che nelle 24 ore prima del comunicato della banca centrale l'indice sale in media dello 0,23% (SPY, t 2,9), ma
quei giorni sono troppo pochi per battere il tenere sempre. Qui si tiene sempre l'indice e in quei giorni se ne tiene di più, con la leva.
**La regola nasce dopo aver visto la prova 7**: sul 2016-2024 il risultato è già in gran parte noto. Per questo **l'esito lo decide solo
il periodo chiuso** (2 gennaio 2025 → 30 settembre 2026, 14 comunicati), aperto una volta per questa prova. Il 2016-2024 si calcola solo
da leggere. **Sospetto scritto prima:** 14 eventi sono pochissimi: anche un esito positivo sarà una prova debole.

## La regola

* **Titoli:** SPY e QQQ, ognuno da solo; barre al minuto di seduta, dividendi sulla prima barra del giorno di stacco.
* **Sempre investiti:** alla prima barra del periodo si compra il 98% del conto.
* **Prima della banca centrale** (finestra della prova 7): alla chiusura della barra delle 13:59 del giorno di borsa prima del comunicato
  si porta la posizione al **148% del conto** (50% in più, a prestito), eseguito all'apertura delle 14:00; alla chiusura della barra delle
  13:58 del giorno del comunicato si torna al 98%, eseguito all'apertura delle 13:59. Leva massima 1,5.
* **Interesse sul prestito:** **6% l'anno** sui contanti sotto zero, per ogni notte (fissato qui per prudenza: Interactive Brokers chiede
  il tasso di riferimento più circa l'1,5%, e il tasso di riferimento nel 2016-2026 è andato da circa 0 a circa 5,3%; da verificare).
* Costi come le prove 1 e 7 (scarto misurato, 0,5 punti base di slittamento, commissioni Interactive Brokers «fisso», costi doppi).

## L'esame, solo sul periodo chiuso

Per ogni titolo: (1) Sharpe annuo con i costi più alto del comprare e tenere lo SPY e del comprare e tenere lo stesso titolo; (2) con i
costi doppi la strategia guadagna più del comprare e tenere lo stesso titolo (il guadagno in più deve reggere anche ai costi doppi); (3)
almeno 4 trimestri su 7 in guadagno. Da leggere accanto: il guadagno in più rispetto al tenere, evento per evento. Nel conto: **2 prove
più 1 apertura = 3**.
