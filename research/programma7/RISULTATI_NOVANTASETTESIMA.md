# Risultati della prova 159 (BQ: la base dei future trimestrali come rendimento fisso) — 15 novembre 2026

## Riepilogo
**Non promettente secondo l'esame scritto prima.** A (moneta, Bitcoin + Ether): netto positivo, Sharpe 1,70 (1,80 sulle settimane del mazzo), t 4,2,
ma **Sharpe corretto 0,41 (sotto 0,80)** e **il 2020 è negativo (−0,7%)**, quindi non «ogni anno positivo». B (Bitcoin in USDT, dal 2022): ogni anno
positivo, ma t 2,45 (sotto 3), **Sharpe corretto 0,04**, e **6 liquidazioni su 19 trimestri** con la riserva del 25%. Rendimento annuo sul capitale con
riserva: A 5,5% su tutto il periodo e 6,7% nel 2024-2026 (sopra il 4%); B 3,0% dal 2022 e 4,5% nel 2024-2026. Regolare ma piccolo.
Giudizio sulla credibilità: spetta a backtest-auditor; qui non si dice «valida».

## La prova come è scritta e scala di tempo
`research/programma7/NOVANTASETTESIMA.md`, regole committate in 0a0b941 e corrette in 676f5c3 (letture A1, A4, A5, A6, A7, A8, A11 della verifica).
Scala: ingresso all'apertura delle 09:00 UTC dopo la scadenza T nel trimestrale T+3 mesi, uscita alla scadenza (regolamento = chiusura dell'ora delle 08:00,
pronti venduto all'apertura delle 08:00), valore del giorno alle chiusure giornaliere, esame su settimane intere (lunedì-domenica) sommando i giorni.

## Implementazione
`research/programma7/novantasettesima.py` (nessun commit richiesto qui). Dati: `research/data/trimestrali_binance/` (fuori da git); le impronte sono in
`risultati_novantasettesima/impronte_file_scaricati.json` (1.310 file, uguali al CHECKSUM pubblico). Seme: nessun elemento casuale.
Scelte di calcolo (le mie letture, vedi in fondo): capitale 1 = pronti 0,8 + riserva 0,2, **senza capitalizzare** (come la prova 157); A: 0,4 per moneta;
B: 0,8 sul Bitcoin; costo del ciclo 0,33% del nozionale (pronti 0,15% per lato, future 0,02% limite + 0,01% scarto all'ingresso, uscita del future gratuita).

## Varianti provate
2 (A, B), registro `research/trials/novantasettesima.csv` (2 righe, esito «calcolata»). Nessuna variante fuori dalle regole; nessuna interrotta.

## Risultati (periodo: A dal 25/9/2020, B dal 25/3/2022, fino al 4/10/2026)
| | A (moneta) | B (USDT, 100% Bitcoin) |
|---|---|---|
| Trimestri (dentro/saltati) | 42 dentro, 7 saltati su 49 (BTC + ETH) | 19 dentro, 0 saltati; **6 liquidati** |
| Rendimento annuo sul capitale con riserva, tutto | 5,5% (55 USDT su 1.000) | 3,0% dal 2022 (30 USDT); 2,3% con le settimane ferme prima del 2022 |
| Rendimento annuo 2024-2026 | 6,7% (67 USDT su 1.000) | 4,5% (45 USDT su 1.000) |
| Sul solo pronti (descrittivo) | 6,9% | 2,9% |
| Sharpe (52 settimane) | 1,70 su 315 settimane; 1,80 su 300 (mazzo, da gen 2021) | 0,99 su 315 (con zeri prima del 2022); 1,15 su 237 (mazzo) |
| t | 4,18 (4,3 sul mazzo) | 2,44 (2,45 sul mazzo) |
| Discesa massima | −4,0% (giornaliera, somma); −2,8% (settimanale) | −2,7% |
| Mesi positivi | 52 su 74 | 31 su 56 |
| Per anno (annualizzato) | 2020 **−2,4%**, 2021 +10,9%, 2022 +2,7%, 2023 +1,9%, 2024 +11,3%, 2025 +5,7%, 2026 +1,9% | 2022 +1,1%, 2023 +0,3%, 2024 +7,3%, 2025 +3,8%, 2026 +1,6% |
| Costo medio | 0,33% a ciclo | 0,33% a ciclo (+0,66% circa per una liquidazione) |
| **Sharpe corretto** (`corretto_famiglie`, 196 famiglie, 277 serie nel mazzo) | **0,41** | **0,04** |
| Famiglia | 159 A e 159 B insieme, da sole | idem |
| Correlazione con G1 | 0,16 | 0,05 |
| Correlazione con la prova 157 (A / B) | 0,13 / 0,14 | −0,03 / −0,03 |

Conto delle prove: da 324 a 326 (lo scrive la sessione principale).
Esame: A: netto positivo sì; ogni anno positivo **no** (2020 parziale −0,7%); t da 3 sì; Sharpe corretto da 0,80 **no**; media 2024-2026 6,7% sopra il 4%.
B: netto sì; ogni anno (dal 2022) sì; t da 3 **no**; Sharpe corretto **no**.

## Variante migliore e sensibilità
A è la migliore. Non ci sono varianti vicine (regola: nessuna altra variante). Il rendimento è dominato dal 2021 e dal 2024 (base alta); nel 2023 e 2026 è 1,9%.
La base media dei trimestri di A è 7,3% annuo, **il funding medio dei perpetui negli stessi trimestri 11,1%**: la base ha pagato più del funding solo in 19 trimestri su 49.

## Anomalie e possibili errori di motore o dati
* Nessun motore ufficiale per i future con scadenza: contabilità scritta nella prova (valore S·Fe/F per A, Q·(S−F+Fe) per B).
* Buco nei dati 27 agosto - 1 settembre 2023 (contratti 230929/231229): 8 giorni riempiti in tutto con l'ultima chiusura nota in A, come da regole; 0 in B.
* Il valore giornaliero ha oscillazioni di ±0,5% al giorno nel dicembre 2020 (base di mercato che si muove): spiega il 2020 negativo di A.
* A, contratto in moneta con copertura esatta e leva 1: la liquidazione non può scattare in teoria (margine e posizione in moneta si muovono insieme), anche se il future arriva a +239% sull'ingresso (ETHUSD_210326). Non è simulato nessun margine di mantenimento.
* B: 6 liquidazioni (giorni 14/1/2023, 24/10/2023, 26/2/2024, 11/11/2024, 21/5/2025, 21/8/2026), tutte con rialzo del future oltre il 25%; il conteggio sui massimi orari dà lo stesso numero (6). Il rialzo massimo del Bitcoin è +19,5% in un giorno e +38,4% in 7 giorni (nei giorni di tenuta il massimo del future su ingresso è +75,8%): **la riserva di 0,25 non basta**.
* Stress: base annua dei trimestrali del Bitcoin al 10/5/2021 +25%, al 9-12/11/2022 da −2,3% a −6,1% (sul trimestrale più vicino; il successivo ≈ −0,2/−1,0%), al 10/10/2025 +7,8%: nel crollo della borsa del novembre 2022 la base è andata sotto zero e la soglia avrebbe fatto stare fuori.
* L'ultimo contratto è ancora aperto al 4 ottobre: valutato a mercato, il costo di chiusura (≈0,4% del nozionale a pronti e future) non è nel conto.

## Varianti non previste che proporrei (non eseguite)
Tenere il pronti da una scadenza all'altra senza venderlo (risparmia 0,30% a trimestre di costo a pronti, circa 1,2% l'anno, rispetto alla regola di venderlo e ricomprarlo). Una soglia di ingresso più alta della base (la regola vieta altre soglie). Il pronti come margine in B (conto in moneta) invece della riserva in USDT.

## Domande aperte
1. Per la variante B ho tenuto la serie intera dal 2020 (zeri prima del 2022) per il file e l'esame «intero» e la serie del mazzo (dal 2021 senza zeri iniziali) per lo Sharpe corretto; la regola non dice quale sia l'esame ufficiale del t (A: 4,18 contro 4,3; B: 2,44 contro 2,45: non cambia l'esito).
2. Il caso «la perdita aperta supera la riserva» l'ho controllato alla chiusura giornaliera, come nelle regole corrette; con i massimi orari il conto è uguale.
3. I rendimenti annui sono medie delle settimane per 52 sul capitale fisso, senza capitalizzare; la capitalizzazione non è stata provata.

## Elenco delle letture delle regole che ho dovuto scegliere
Capitale fisso 1,25 per 1 di pronti senza capitalizzare; settimane intere lunedì-domenica, ultima settimana del 28/9/2026; segnale con le chiusure delle 08:00, esecuzione all'apertura delle 09:00; base annualizzata con la durata in giorni frazionari; soglia = 0,33% di ciclo; ingresso del future con costo 0,03% (limite sempre eseguito); liquidazione B a chiusura giornaliera con costi di mercato (pronti 0,15%, future 0,06%); dopo la liquidazione si resta fuori fino alla scadenza successiva; buco 2023 riempito con l'ultima chiusura nota; il valore di mercato del 4 ottobre resta aperto.
