# E-201 — Il libro degli ordini, periodo C2 (fase 4)

Piano scritto e committato il 18 ottobre 2026 **prima del calcolo** (REGOLE.md, sezioni 6bis e 10). Periodo C2
(2024-01-01 → 2025-06-30); le 24 monete della fase 2; misure a ore del libro (`strumenti/libro.py`) e barre di un'ora.

## Perché

Chi lascia ordini grandi fermi vicino al prezzo dice dove è disposto a comprare o vendere: un libro molto più pieno dal lato
degli acquisti è un pavimento (e chi vuole vendere grosso aspetta), uno sottile vuol dire che un ordine a mercato muove
molto il prezzo. Si guarda se questo dice la direzione delle ore dopo, oltre i costi.

## Le famiglie (decisione alla chiusura dell'ora t con le misure dell'ora t; ingresso, uscita, pausa, caso come E-001)

pct(x) = percentile fra le 720 ore prima (compreso il valore, almeno 500). imb = squilibrio medio dell'ora.

| Famiglia | Segnale | «Segue» | Valori | h |
|---|---|---|---|---|
| D1 squilibrio | pct(imb_k) ≥ 95% o ≤ 5% | long se pieno di acquisti | k 1, 2, 5 | 1, 4, 12, 24 |
| D2 variazione | pct(imb_k − imb_k di w ore prima) ≥ 95% o ≤ 5% | long se gli acquisti crescono | k 1, 5; w 1, 4 | 1, 4, 24 |
| D3 libro sottile o spesso | liquidità entro l'1% / mediana delle 720 ore ≤ 0,4 («sottile») o ≥ 2,5 («spesso»), con z_1 ≥ 2 o ≤ −2 | verso del prezzo | — | 4, 12, 24 |
| D4 prezzo e libro | z_4 ≥ 2 o ≤ −2, con pct(imb_2) ≤ 10% o ≥ 90% (4 combinazioni) | verso del prezzo | — | 4, 24 |
| D5 squilibrio che dura | pct(media di imb_2 delle 24 ore) ≥ 95% o ≤ 5% | long se pieno di acquisti | — | 24, 72 |

Celle: D1 24, D2 24, D3 12, D4 8, D5 4 = **72** (144 con i due versi).

## Criteri di promozione

Gli stessi di E-101: |lordo| ≥ 0,30% e contro il caso ≥ 0,25% nello stesso verso; stesso segno in ogni semestre di C2
con almeno 20 trade; stesso segno su almeno il 70% delle monete con almeno 10 trade, almeno 10 monete; |t| ≥ 3; almeno 100
trade. Al massimo 5 idee K (stessa famiglia, stesso lato e stesso verso in un'idea, al massimo 3 varianti).
