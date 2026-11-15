# Risultati della prova 160 (G1 con stop + funding coperto 161 B, quote fisse)

### Riepilogo
Due varianti calcolate (A 80/20, B 60/40). **Nessuna passa l'esame scritto**: Sharpe corretto per famiglie 0,64 (A) e 0,72 (B), sotto 0,80; tutte le altre condizioni valgono. **Sono «utili»** per i tre criteri scritti prima (ma il criterio 3 vale per un solo mese). G1 da solo: Sharpe corretto 0,58 sullo stesso mazzo.

### La prova come è scritta e scala di tempo
`research/programma7/NOVANTOTTESIMA.md` (3dc968b): pesi G1 w e coperto 1−w, riequilibrati ogni primo del mese; A 80/20, B 60/40; esame: netto > 0, ogni anno positivo, t ≥ 3, Sharpe corretto per famiglie ≥ 0,80; utile: discesa massima ≥ 5 punti sotto G1, Sharpe non sotto di più di 0,05, meno mesi negativi. Scala: giornaliera, esame sulle settimane. Periodo: 2.100 giorni, 4 gennaio 2021 - 4 ottobre 2026 (300 settimane). Verifica: `VERIFICA_NOVANTOTTESIMA.md`.

### Implementazione
`research/programma7/novantottesima.py` (nessun commit fatto, come da brief). Seme 160 (nessun elemento casuale). Serie: G1 `risultati_novantaseiesima/giorni_G1_con_stop.csv.gz` (colonna `rendimento`), coperto `risultati_novantanovesima/giorni_B.csv.gz` (`netto`). Riprodotte le settimane di G1 (158) e del coperto (161 B) con differenza 1e-15.

### Varianti provate
2 (A, B). Registro: `research/trials/novantottesima.csv`. Uscite: `research/programma7/risultati_novantottesima/` (`esame.json`, `settimane_A/B.csv.gz`, `giorni_A/B.csv.gz`).

### Risultati (stesso periodo, 70 mesi)
| | G1 con stop | A 80/20 | B 60/40 | Coperto 161 B |
|---|---|---|---|---|
| Rendimento l'anno composto | 66,2% | 53,4% | 41,0% | 6,3% |
| USDT su 1.000 (l'anno) | 662 | 534 | 410 | 63 |
| Sharpe settimanale (√52) | 1,97 | 2,02 | 2,11 | 3,51 |
| Sharpe su 365 giorni | 1,99 | 2,05 | 2,14 | 8,37 |
| t | 4,73 | 4,86 | 5,07 | 8,43 |
| t Newey-West 13 settimane | 3,31 | 3,36 | 3,42 | 3,15 |
| t Newey-West 26 settimane | 3,01 | 3,04 | 3,08 | 2,72 |
| Discesa massima giornaliera | -30,1% | -24,0% | -17,5% | -0,29% |
| Discesa massima settimanale | -28,8% | -22,9% | -16,6% | -0,27% |
| Mesi positivi su 70 | 47 | 48 | 48 | 62 |
| Sharpe corretto (famiglie 196) | 0,58 | 0,64 | 0,72 | (161 B in mazzo) |

Anni (rendimento composto): G1 2021 +177,9%, 2022 +33,0%, 2023 +6,4%, 2024 +93,1%, 2025 +92,2%, 2026 (a ottobre) +27,3%. A: +140,4, +26,6, +6,4, +74,0, +70,2, +22,3. B: +106,2, +20,2, +6,2, +55,8, +50,5, +17,1. Coperto: +22,2, +1,0, +3,7, +7,3, +2,7, +0,7. Ogni anno positivo ovunque (anche con la media settimanale).
Costo del riequilibrio: 0,49% (A) e 0,54% (B) del capitale iniziale in tutto il periodo (circa 0,09% l'anno su capitale che cresce); senza costi il rendimento sale di 0,03 punti (A 53,45%, B 41,05%). Pesi fissi ogni giorno a costo zero: A 52,9%, B 40,2%: il riequilibrio mensile non pesa.
Esame: A e B passano netto, ogni anno, t; **falliscono lo Sharpe corretto (0,64; 0,72 < 0,80)**. Utile: (1) A -6,1 punti, B -12,6 punti di discesa sotto G1: sì; (2) Sharpe non sotto G1: sì (più alto); (3) mesi negativi 22 (A, B) contro 23 di G1: sì, per un solo mese.
Correlazione G1-coperto: giornaliera 0,052, settimanale 0,152.
Peggiori 10 giornate di G1 (da -3,9% a -8,5%; 4 di 10 nel gennaio-febbraio 2021): il coperto fa da -0,02% a +0,26% (mai una perdita sopra lo 0,02%): non protegge, ma non peggiora; la discesa si riduce solo perché la quota di G1 è più piccola.

### Variante migliore e sensibilità
Per Sharpe corretto B (0,72), che è anche quella con meno rischio; la salita di 0,06 passando da A a B è monotona nel peso del coperto (G1 0,58, A 0,64, B 0,72). Nessun peso è arrivato a 0,80: se la tendenza continuasse servirebbe oltre il 40% di coperto, che non è previsto (nessuna variante nuova eseguita). Il t con la correlazione fra settimane resta sopra 3 per tutte (3,0-3,4; 26 ritardi: G1 3,01, A 3,04, B 3,08, coperto 2,72: il coperto da solo scende sotto 3).

### Anomalie e possibili errori
Nessun errore di motore o di dati. Nota: l'unico controllo di archivio (`buchi_archivio`) segnala una moneta con giorni mancanti da settembre, non usata qui. Il coperto 161 B è un'unica serie già calcolata: il rischio non misurato (borsa, USDT, tasso di base) resta quello scritto nella 161. Con un patrimonio di 1.000 USDT l'allocatore prevede una strategia sola: il risultato serve per conti più grandi.

### Varianti non previste che proporrei (non eseguite)
Un peso del coperto più alto (per esempio 50/50) solo se Alessio lo vuole come prova nuova con regole scritte prima; sarebbe una scelta fatta dopo aver visto i numeri.

### Domande aperte
1. Lo Sharpe corretto sale con il coperto ma G1 da solo è già sotto 0,80 (0,58): l'esame va tenuto uguale per le miscele? (decisione di Alessio.)
2. Per il criterio 3 «meno mesi negativi» basta un mese (22 contro 23): è la lettura voluta?
3. Il riequilibrio vero del coperto richiederebbe il pronti a 0,15%: l'effetto sarebbe piccolo (spostamenti mensili), ma le regole dicono 0,05%.

### Letture scelte
Elencate in `VERIFICA_NOVANTOTTESIMA.md` (punti 1-7): primo giorno senza costo, costo del riequilibrio sulle due gamba, rendimento di giornata, anno positivo con la media settimanale, discesa sulla curva giornaliera, mese parziale incluso, Newey-West con pesi di Bartlett.
