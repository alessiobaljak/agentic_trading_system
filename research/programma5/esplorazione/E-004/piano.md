# E-004 — Premio sullo spot e liquidazioni a ore, periodo C

Piano scritto e committato il 18 ottobre 2026 **prima del calcolo** (REGOLE.md, sezione 6bis). Solo periodo C; le 12
monete; barre di un'ora (`strumenti/ore.py`) e l'indice del premio del perpetuo sullo spot di Binance a 1 ora
(`motore5.premio`, chiusura dell'ora, nota alla fine dell'ora).

## Perché

E-001 dice che i crolli di qualche ora rimbalzano. Due dati che le candele non hanno possono dire **quali** crolli sono
fatti di vendite forzate sul perpetuo: (1) il **premio** del perpetuo sullo spot: se il perpetuo scende sotto lo spot
(premio molto negativo) a vendere è la leva, non chi tiene la moneta, e l'arbitraggio lo riporta su; (2) l'**interesse
aperto** che crolla nell'ora (posizioni chiuse a forza). Si prova anche il premio da solo (la folla a leva in un verso).

## Le famiglie

Misure come in E-001 (σ, z_w, decisione alla chiusura dell'ora t, ingresso all'apertura di t+1, uscita alla chiusura di
t+h, funding compreso, pausa max(w, h); «segue» e «contro»). pct(x) = percentile del valore fra quelli delle 720 ore prima
(compreso il valore, almeno 500).

| Famiglia | Segnale | «Segue» | Valori | h |
|---|---|---|---|---|
| P1 premio | pct(premio) ≥ 1−q (alto) o ≤ q (basso) | long se alto | q 5%, 1% | 1, 4, 24, 72 |
| P2 variazione del premio | pct(premio_t − premio_{t−w}) ≥ 95% o ≤ 5% | long se sale | w 1, 4 | 1, 4, 24 |
| P3 scossa e premio | z_w ≤ −3 con pct(premio) ≤ 10% («sconto») o > 10% («senza sconto»); z_w ≥ 3 con pct(premio) ≥ 90% («premio») o < 90% | verso della scossa | w 1, 4 | 4, 12, 24 |
| L1 liquidazioni | pct(variazione dell'interesse aperto in 1 ora) ≤ 2% e z_1 ≤ −2 (giù) o z_1 ≥ 2 (su) | verso del prezzo | — | 4, 12, 24 |
| L2 posizioni nuove | pct(variazione dell'interesse aperto in 1 ora) ≥ 98% e z_1 ≤ −2 o ≥ 2 | verso del prezzo | — | 4, 12, 24 |

Per il confronto si calcolano anche 6 celle di **riferimento** L0 (z_1 ≤ −2 o ≥ 2, senza condizione, h 4, 12, 24),
che non si promuovono. Celle: P1 16, P2 12, P3 24, L1 6, L2 6 = **64** (128 con i due versi), più le 6 di riferimento. L'interesse aperto c'è da settembre 2020 per BTC e
da dicembre 2021 per le altre (L1 e L2 di fatto: BTC 2020-2022, le altre il 2022). Il premio c'è da gennaio 2020 (le
monete quotate dopo, dalla quotazione).

## Criteri di promozione

Gli stessi di E-001: |lordo| ≥ 0,30% e contro il caso ≥ 0,25% nello stesso verso; stesso segno in ogni anno con almeno 20
trade; stesso segno su almeno il 70% delle monete con almeno 10 trade e almeno 6; |t| ≥ 3; almeno 100 trade. Al massimo 5
idee, le più forti per t. **In più**, siccome questa esplorazione nasce per spiegare I-010: una cella di P3 o L1 che non
batte la stessa scossa senza la condizione (la cella gemella «senza sconto» o la scossa di E-001) di almeno 0,30% non
porta niente di nuovo e non si promuove. Per P3 la gemella è la cella con la stessa w, lo stesso lato e lo stesso h
senza la condizione sul premio; per L1 e L2 è la cella L0 con lo stesso lato e lo stesso h.
