# J-009 — Scalping a limite nelle code dei crolli: acquisto a 6σ, rivendita a limite (monete fuori dalla fase 1)

Scheda scritta il 18 ottobre 2026 **prima del calcolo di questa idea nel motore a minuti e prima di aprire V2**
(REGOLE.md, sezioni 6bis, 7 e 7bis).

## Da dove viene

Dall'esplorazione **E-102** (`research/programma5/esplorazione/E-102/risultati.md`), celle promosse sul periodo C2 e 24
monete. Trovata cercando: a dire se è vera è V2.

## Perché

Un ordine d'acquisto fermo 6 volte la volatilità oraria sotto il prezzo si esegue solo nei crolli rapidi, quando
le vendite forzate attraversano il libro; si rivende con un ordine fermo 1-2σ sopra. Nel 2024-2025 ha reso dopo i costi
in ogni semestre e su 23-24 monete su 24. È parente del rimbalzo dopo i crolli e di I-020 (già provati su R sulle 12 monete
della fase 1): su V2 si prova **solo sulle altre monete**. La differenza con I-020 (k = 3, morto su R): qui solo i crolli
veri.

## La regola

Ogni variante è esattamente la cella di E-102 (`strumenti/esplora_limiti.py`), simulata nel motore a minuti
(`strumenti/idee_fase2.py`, `per_moneta_rete`): all'inizio di ogni ora un ordine limite d'acquisto a `P·exp(−k·σ)` (P
chiusura dell'ora prima, σ dei rendimenti orari delle 720 ore fino all'ora prima), valido 60 minuti, eseguito solo ad
attraversamento al livello (0,02%, niente scarto). Tipo **S**: uscita a limite a `L·exp(m·σ)` dal minuto dopo, ad
attraversamento (0,02%), altrimenti a mercato dopo H minuti (0,05% e scarto doppio). Tipo **R**: uscita a mercato dopo H
minuti (0,05% e scarto doppio). Funding. Mentre il trade è aperto, nessun ordine nuovo sulla moneta. Il caso:
`motore5.caso_limite` (R) o `scalping.caso_doppio` (S).

## Le varianti (giudicate insieme)

| Variante | Cella | In E-102 (lordo R / netto S) | Trade | t |
|---|---|---|---|---|
| J-009a | `S acquisto k6 m1 H240` | +0.486% | 965 | 4.88 |
| J-009b | `S acquisto k6 m2 H240` | +0.743% | 901 | 4.18 |

## Le monete e l'esame

* **C2**: le 24 monete della fase 2; netto con l'intervallo sopra zero e meglio del caso.
* **V2** (una volta): le 100 di `universo_top100.json` **tranne le 12 della fase 1** (88 monete); l'esame della sezione 7
  (p ≤ 0,005 / 2, costi doppi, senza il giorno migliore, tutte e due le metà, 60% delle monete con almeno 20 trade,
  almeno 200 trade).
