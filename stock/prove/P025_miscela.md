# Prova 25 — la miscela: più strategie insieme

Regole scritte l'11 novembre 2026 **prima di qualsiasi calcolo della miscela**, committate prima di lanciare il programma. Idea del
proprietario (I27 di `REGISTRO.md`): «non puoi avere una sola strategia, è impossibile»; «procedi anche con la miscela, in autonomia».
Conta come **1 prova**.

## Cosa si sa prima, e il pericolo

Le strategie della miscela sono già state calcolate e **bocciate da sole**: prima della banca centrale (prova 7), più investiti con il
mercato calmo (prova 15), la salita fatta da poche azioni (prova 16). Sono scelte perché avevano un vantaggio piccolo e misurato, cioè
**guardando i loro risultati**: è il pericolo dell'eccesso di adattamento, scritto qui prima. Il periodo chiuso di queste famiglie è già
stato usato (prove 9, 14, 15): **la conferma può venire solo in avanti**, sul demo. La miscela non riceve nessun numero scelto guardando la
miscela stessa.

## La regola

* **Le parti:** le serie giornaliere con i costi già calcolate e committate in `stock/prove/serie/`: `P007_SPY`, `P007_QQQ`,
  `P015_SPY`, `P015_QQQ`, `P016_SPY`, `P016_QQQ` (ogni regola su tutti e due i fondi, per non scegliere quello andato meglio).
* **I pesi:** **un sesto del capitale a ciascuna**, rimesso a pesi uguali ogni giorno (il rendimento del giorno è la media dei sei).
  Niente pesi per rischio: la regola prima della banca centrale è investita 71 giorni su 2264 e con i pesi per rischio prenderebbe quasi
  tutto il capitale.
* **Il costo del ribilanciamento:** non aggiunto. Le sei parti comprano e vendono solo SPY e QQQ, e nella realtà gli ordini delle parti
  si compenserebbero in un conto solo; si dice che è un'approssimazione a favore della miscela, di pochi punti base l'anno.
* **Periodo:** i giorni in cui ci sono tutte e sei le serie (da novembre 2016) al 31 dicembre 2024.

## L'esame

(1) Sharpe annuo più alto del tenere lo SPY **e** del tenere metà SPY e metà QQQ, sugli stessi giorni; (2) Sharpe corretto ≥ 0,95 con
tutte le serie del conto; (3) Sharpe sopra zero con i costi doppi, stimato così (le serie a costi doppi
non sono salvate): per ogni parte il costo annuo = (ln(1 + guadagno senza costi) − ln(1 + guadagno con i costi)) / anni, dai risultati
delle prove 7, 15 e 16; la miscela a costi doppi = la miscela con i costi meno la media dei sei costi annui divisa per 252, ogni giorno;
(4) almeno il 60% dei trimestri in guadagno. Accanto, da leggere: le
correlazioni fra le sei parti e lo Sharpe di ciascuna sullo stesso periodo.

**Se passa:** la miscela va sul **demo** accanto alla prima candela (un conto demo suo), perché la conferma sul passato non è più
possibile. **Se non passa** ma batte il tenere lo SPY sullo Sharpe (condizione 1): lo si dice al proprietario, che ha detto l'8 novembre
che la soglia 0,95 non è un muro, e decide lui se metterla sul demo.
