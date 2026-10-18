# E-101 — Esplorazione a ore sul periodo recente C2 (fase 2)

Piano scritto e committato il 18 ottobre 2026 **prima del calcolo** (REGOLE.md, sezioni 6bis e 7). Periodo **C2**
(2024-01-01 → 2025-06-30); le **24 monete** della fase 2 (le 12 del programma e le 12 di `universo_fase2.json`).

## Cosa si calcola

Le famiglie a ore delle esplorazioni della fase 1, con le stesse definizioni e gli stessi valori, in un solo programma
(`strumenti/esplora_fase2.py`): F1 (scossa), G1 (scossa propria coperta con BTC), F5 (rottura), F6 (funding), F7
(rapporti long/short), F8 (acquisti aggressivi), F9 (volume), F10 (calma poi rottura), F11 (calendario), F12 (tendenza),
F13 (prezzo e interesse aperto), P1-P3 (premio sullo spot), L0-L2 (liquidazioni e posizioni nuove; L0 solo riferimento),
G2-G5 (classifiche fra monete: qui long le **5** prime e short le **5** ultime, con almeno 12 monete in fila), G6 (paniere
contro BTC). In tutto 468 celle (936 con i due versi).

## Criteri di promozione (tutti)

1. |lordo| ≥ 0,30% a trade e contro il caso ≥ 0,25% nello stesso verso (G1: 0,50% e 0,40%; G2-G6: il caso è zero);
2. stesso segno in **ognuno dei semestri** di C2 (2024-1, 2024-2, 2025-1) con almeno 20 trade;
3. stesso segno su almeno il **70%** delle monete con almeno 10 trade, e almeno **10** monete (G2-G5: contributo della
   moneta nel portafoglio; G6: niente criterio delle monete, ma |t| ≥ 3,5);
4. |t| ≥ 3 (gruppi di giorni di calendario);
5. almeno 100 trade.

Le celle promosse della stessa famiglia, dello stesso lato e dello stesso verso diventano **una** idea J con al massimo 3
varianti (le più forti per t); al massimo 5 idee, le più forti per t. Ogni cella promossa del rimbalzo dopo i crolli
(`esplora_fase2.PARENTI_R`: già provato su R sulle 12 monete della fase 1) è segnata «parente_R»: se diventa un'idea, su
V2 si prova solo sulle 12 monete nuove (REGOLE.md, 7).
