# Risultati della prova 156 — G1 che esce dal lato venduto dopo una fiammata
Script `research/programma7/novantaquattresima.py`; serie e dettagli in `risultati_novantaquattresima/` (`esame.json`, `parita.json`, `giorni_*`,
`settimane_*`); registro delle varianti `research/trials/novantaquattresima.csv` (3 righe: parità, A, B). Nessun commit fatto da me
(commit al momento del calcolo: quello scritto nel registro). Seme 156.

### Riepilogo
**Esito secondo l'esame scritto prima: NON PROMETTENTE, sia A sia B.** Il netto è positivo e ogni anno è positivo (sono anche le qualità di G1), ma
nessuna delle due batte G1 in modo credibile: il t della differenza è 0,32 (A) e 0,60 (B) contro il 2 richiesto; solo 2 anni su 5 del 2021-2025
sono meglio di G1 (servivano 4); Sharpe corretto 0,73 (A) e 0,79 (B) sotto lo 0,80. B ha lo Sharpe sopra G1, A no. Quasi tutto il guadagno
(A: 143%, B: 147% della differenza totale) viene dal 2021. Varianti provate: 2 (più la parità).

### La prova come è scritta (citata, non riformulata) e scala di tempo
`NOVANTAQUATTRESIMA.md` con la sezione «Regole corrette il 14 novembre 2026 dopo la verifica» (commit 2024ab1). Fiammata = `sc.rendimenti` strettamente
sopra 0,20, nota all'apertura di F+1; la moneta non può essere venduta nei giorni F+1…F+N (nuova fiammata: fine = max(fine, F'+N)); peso venduto
a zero e non ridistribuito; lato comprato invariato. A: N = 3; B: N = 7. Scala di tempo: giornaliera (decisione alle 00:00 UTC), Sharpe sulle
settimane (52) e sui giorni (365). Periodo dal 4 gennaio 2021 al 4 ottobre 2026 compreso: 2.100 giorni, 300 settimane intere.

### Implementazione (file, commit)
`novantaquattresima.py` riusa `prima.py` come la 155 (stesse monete, banda, pesi); con `esclusione()` si trova il giorno-moneta escluso, poi
`Wv = W` con il peso negativo messo a zero, e conti `te.conto` + `cs.spese_a_limite`. Parità: con N = 0 `Wv` è uguale a `W` (verificato con `array_equal`).
Commit: nessuno fatto da me; il registro scrive l'hash del commit corrente.

### Parità con N = 0 (come nella 155)
Valida. Stessi 2.100 giorni; fino al 29 settembre 2026 le differenze massime sono: lordo 1,0e-16, funding 1,0e-16, giro 4,4e-16, monete 0; le spese
differiscono in 953 giorni (massimo 0,0053 al giorno; somma oggi 0,3665 contro 0,3774 del riferimento), per la causa già verificata il 13 novembre
(candele a 1 ora più complete oggi). Il G1 di confronto è quello ricalcolato oggi.

### Varianti provate
2: A (N = 3), B (N = 7). Registro: `research/trials/novantaquattresima.csv`.

### Risultati (stesso periodo, 2.100 giorni; rendimento netto in media giornaliera × 365; somme annue non composte)
| | G1 oggi | G1 riferimento | A (N=3) | B (N=7) |
|---|---|---|---|---|
| netto annuo | +54,6% | +54,2% | +55,6% | +57,7% |
| Sharpe 365 giorni | 1,989 | 1,978 | 2,034 | 2,068 |
| Sharpe settimanale (52) | 1,982 | 1,967 | 1,952 | 2,028 |
| t settimanale | 4,76 | 4,73 | 4,69 | 4,87 |
| discesa massima giornaliera | -30,1% | -30,1% | -28,3% | -25,8% |
| discesa massima settimanale | -28,8% | -28,8% | -27,2% | -24,9% |
| spese l'anno | 6,4% | | 6,5% | 6,4% |
| Sharpe corretto (194 famiglie, taglio 0,5) | 0,76 | | 0,73 | 0,79 |
| Sharpe corretto con taglio 0,3 / 0,7 | 0,77 / 0,64 | | 0,74 / 0,62 | 0,80 / 0,69 |

Somma dei rendimenti netti per anno (G1 / A / B): 2021 1,104 / 1,188 / 1,370; 2022 0,314 / 0,288 / 0,248; 2023 0,082 / 0,092 / 0,080;
2024 0,695 / 0,684 / 0,707; 2025 0,676 / 0,660 / 0,663; 2026 0,268 / 0,286 / 0,251. Tutti positivi.
Famiglie: G1 oggi è in famiglia propria nel conteggio fatto; A e B sono nel gruppo di «6 F2, 8 F3, 12 K1…». Correlazione settimanale con G1: A 0,97, B 0,93.

### La differenza con G1 (variante meno G1 ricalcolato)
| | media giorno | annuo | t semplice giorni (≥2) | t settimanale | t robusto (7 ritardi) | somma totale |
|---|---|---|---|---|---|---|
| A | +0,0000 | +1,0% | **0,32** | 0,35 | 0,34 | +0,059 |
| B | +0,0001 | +3,1% | **0,60** | 0,72 | 0,74 | +0,181 |

Somma per anno, 2021-2025 (poi 2026): A: 2021 +0,084, 2022 -0,026, 2023 +0,010, 2024 -0,011, 2025 -0,017 (2026 +0,018). B: 2021 +0,267,
2022 -0,066, 2023 -0,002, 2024 +0,012, 2025 -0,014 (2026 -0,017). Anni positivi su 5: **2 e 2** (serviva 4). Quota del 2021 sulla differenza totale:
A 143%, B 147%; quota del 2026: A 30%, B -9%.

### Criteri dell'esame (A / B)
1 netto positivo sì / sì; 2 ogni anno positivo sì / sì; 3 t settimanale almeno 3 sì (4,69) / sì (4,87); 4 Sharpe corretto almeno 0,80 **no (0,73) / no (0,79)**;
5 media della differenza positiva sì / sì, t almeno 2 **no (0,32) / no (0,60)**; 6 paletto 4 anni su 5 **no (2) / no (2)**; 7 Sharpe sopra G1 **no (settimanale 1,952 < 1,982) / sì**.
Criteri falliti: A quattro (4, 5b, 6, 7), B tre (4, 5b, 6). Non promossa.

### Controlli descrittivi
* **Coerenza con la misura di partenza**: giornate-moneta vendute con fiammata nel giorno, per anno, oggi (dal 4 gennaio): 2021 114, 2022 54, 2023 43,
  2024 98, 2025 69, 2026 178. La voce 12 (dal 1° gennaio, altro motore) dice 85 nel 2021, 75 nel 2024 e 176 nel 2026: il 2026 coincide quasi, il 2021 e il 2024 no
  (il conto di oggi è più alto: 114 contro 85, 98 contro 75). Non è un esame, ma la differenza fra i motori o le definizioni non è chiusa.
* **8.1 Uscite** (giornate-moneta / monete distinte / episodi), A: 2021 325/58/116, 2022 119/28/46, 2023 118/32/44, 2024 288/58/100, 2025 187/43/66, 2026 470/62/140.
  B: 2021 726/65/129, 2022 274/34/58, 2023 293/37/54, 2024 634/67/111, 2025 445/56/88, 2026 969/76/156. Quota del peso venduto tolto, A: 4,1% (2021), 0,7%, 0,7%, 1,8%, 0,9%, 3,0% (2026);
  B: 9,0%, 1,6%, 1,8%, 4,2%, 2,2%, 6,5%.
* **8.2 Dopo l'uscita** (media / mediana / quota che sale; le altre monete vendute, media). Variante A, N = 3 giorni: 2021 +0,7% / -2,7% / 42% (altre -0,5%); 2022 -3,4% / -4,0% / 39%; 2023 +2,1% / 0,0% / 50%;
  2024 +2,4% / +0,3% / 52%; 2025 -1,1% / -2,7% / 42%; 2026 +0,2% / -5,1% / 41%. A 8 giorni (D+7): 2021 +1,7%, 2022 -5,3%, 2023 -0,3%, 2024 +4,3%, 2025 -1,8%, 2026 -5,5% (mediane tutte negative).
  B, N = 7: media da -5,5% (2022) a +2,2% (2024), mediana sempre negativa (da -0,9% a -7,3%), quota che sale 32%-48%. Lettura: le monete tolte NON continuano a salire nella mediana (salgono in meno di metà dei casi);
  le medie sono mosse da pochi casi; né una continuazione chiara né un ritorno giù chiaro: la regola toglie poco e quasi senza effetto (coerente con t 0,3-0,6). Tutte le tabelle per anno e orizzonte (D+1, +3, +7) in `esame.json`, chiave `controlli`.
* **8.3 Lati**: prezzo e funding del lato comprato sono identici in G1, A e B (verificato a 1e-12); le spese del lato comprato differiscono al più di 0,0003 (A) e 0,0007 (B) l'anno, come previsto dalla deriva. Lato venduto, totale a mercato
  per anno (G1 → A → B): 2021 -1,23 → -1,14 → -0,96; 2022 +1,22 → +1,20 → +1,16; 2023 -0,75 → -0,74 → -0,75; 2024 +0,03 → +0,02 → +0,04; 2025 +1,10 → +1,08 → +1,08; 2026 -0,15 → -0,13 → -0,16.
  (Spese a mercato per lato, non a limite; la differenza è tutta nel lato venduto, soprattutto nel 2021.) Dettaglio prezzo, funding e spese per lato in `esame.json`.
* **8.4 Casi in avanti** (solo sulla fiammata, pannello): JCTUSDT 8 novembre 2026, rendimento tenuto +302,9%: fiammata sì, quindi la regola l'avrebbe tolta dal 9 novembre. TRXUSDT: 27 ottobre +0,7%, 28 ottobre -0,6%, 29 ottobre +7,2%: **nessuna fiammata**, la regola non c'entra col caso di TRX.
* **8.5** Discesa massima settimanale: G1 -28,8%, A -27,2%, B -24,9%. Correlazione settimanale con G1: A 0,97, B 0,93; A e B stanno nel gruppo di «6 F2, 8 F3, 12 K1…», G1 oggi da solo nel gruppo del conto fatto.

### Variante migliore e sua sensibilità alle varianti vicine
La migliore per Sharpe è B (N = 7): ma la differenza con G1 non è distinguibile da zero (t 0,60). Fra A e B il risultato cresce con N (Sharpe 2,03 → 2,07; discesa -28,3% → -25,8%) ma resta sotto ogni soglia. Non si provano altre durate (regole).

### Anomalie e possibili errori di motore o dati
* Parità: le spese differiscono dal riferimento per le candele a 1 ora (causa già nota). Nessun'altra anomalia.
* Il conto di oggi delle giornate-moneta con fiammata (2021: 114, 2024: 98) è più alto di quello della voce 12 (85, 75): potrebbe essere la finestra (dal 4 gennaio contro dal 1°), il motore diverso o la definizione dell'universo/pesi; non l'ho indagato (il 2026 coincide: 178 contro 176).
* Il guadagno del 2021 è anche anno parziale: 143-147% della differenza totale.

### Varianti non previste che proporrei (non eseguite)
Nessuna: l'esito è una differenza quasi nulla e senza segno stabile. La ragione economica era già dichiarata debole nelle regole.

### Domande aperte
1. Il conto delle giornate-moneta con fiammata del 2021 e del 2024 è più alto di quello della voce 12 (114 contro 85; 98 contro 75): serve chiarire se i due conti misurano la stessa cosa (finestra dal 4 gennaio, motore `nucleo.py` contro `te.conto`)? Non cambia l'esito.
2. Per il lato venduto per anno, il rapporto usa le spese «a mercato» di `te.conto`: va bene per un controllo descrittivo?

### Letture delle regole che ho dovuto scegliere
* Esclusione calcolata come «una fiammata in D−N…D−1» (equivale a fine = max(fine, F'+N)).
* «Altre monete del lato venduto»: vendute da G1 e non escluse nello stesso giorno, media semplice per cella.
* Orizzonti D+1, +3, +7 = 2, 4, 8 giorni di R da D (inclusi); N = 3 o 7 giorni di R da D.
* Quota 2021/2026 = somma dell'anno / somma totale delle differenze (positiva in entrambe le varianti).
* Il «Sharpe corretto» di G1 oggi è con nome «156 G1 stessi giorni» (come nella 155); le serie di A e B entrano come «156 A» e «156 B» e non sostituiscono nulla nel mazzo.
