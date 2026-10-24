# Prova 9 — i giorni speciali insieme: il cambio del mese e le 24 ore prima della banca centrale (SPY, QQQ)

Regole scritte il 24 ottobre 2026 **prima di qualsiasi calcolo** di questa unione, committate prima di lanciare il programma (idea I10 di
`REGISTRO.md`, richiesta dal proprietario il 24 ottobre: «procedi con i giorni speciali insieme»).

## Perché, e perché si giudica solo sul periodo chiuso

Le prove 6 e 7 hanno trovato due effetti che ci sono ancora, ognuno troppo raro per battere da solo il tenere sempre (prova 7: +0,23% a
evento sullo SPY, t 2,9; prova 6: +47% in nove anni stando investiti circa 6 giorni al mese). Unirli aumenta i giorni investiti. **Ma
l'unione è nata dopo aver visto quei risultati**: sul 2016-2024 il suo risultato è in gran parte già noto, e giudicarla lì vorrebbe dire
scegliere il meglio fra cose viste. Per questo **l'esito lo decide solo il periodo chiuso** (2 gennaio 2025 → 30 settembre 2026), che per
le idee di calendario non è mai stato aperto (decisione del proprietario del 24 ottobre: si riusa per famiglie diverse). Il calcolo sul
2016-2024 si fa e si scrive, ma **solo da leggere**.

## La regola (nessun numero nuovo: le finestre delle prove 6 e 7)

* **Titoli:** SPY e QQQ, ognuno da solo. Barre al minuto di seduta, come le prove 1, 2, 4 e 7.
* **Dentro** in una barra se la barra sta in almeno una delle due finestre:
  * **cambio del mese** (prova 6): dalla prima barra del penultimo giorno di borsa del mese all'ultima barra del terzo giorno di borsa del
    mese dopo (si vende all'apertura del quarto);
  * **banca centrale** (prova 7): dalla barra delle 14:00 del giorno di borsa prima del comunicato alla barra delle 13:58 del giorno del
    comunicato (si vende all'apertura delle 13:59). Date: `stock/dati/fomc.py` (2016-2024 e il periodo chiuso, fonte il sito della
    Federal Reserve).
* Alla chiusura di ogni barra: se la barra dopo è «dentro» e non si hanno azioni, si compra a mercato con il 98% del conto; se la barra
  dopo è «fuori» e si hanno azioni, si vende a mercato. Esecuzione all'apertura della barra dopo. Dividendi sulla prima barra del giorno
  di stacco, come la prova 4. Niente vendite allo scoperto, niente leva, contanti a zero fuori.
* **Costi** come le prove precedenti (metà della mediana dello scarto misurato sul 2016-2024, 0,5 punti base di slittamento,
  commissioni Interactive Brokers «fisso», costi raddoppiati, capitale 100'000 dollari).

## L'esame, solo sul periodo chiuso

Per ognuno dei due titoli passa se sono vere **tutte**: (1) Sharpe annuo con i costi più alto del comprare e tenere lo SPY e del comprare
e tenere lo stesso titolo, sugli stessi giorni; (2) Sharpe annuo con i costi doppi sopra zero; (3) almeno 4 trimestri su 7 in guadagno
dopo i costi. Le decisioni partono dal 2 gennaio 2025 (i prezzi di novembre e dicembre 2024 servono solo per avere le barre prima). Il
periodo chiuso si apre una volta sola per questa prova: il risultato vale com'è. Nel conto: **2 prove più 1 apertura del periodo
chiuso = 3**. Se passa: revisore separato, poi il demo.
