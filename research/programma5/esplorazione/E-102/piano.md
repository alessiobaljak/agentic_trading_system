# E-102 — Reti di ordini limite sul periodo recente C2 (fase 2)

Piano scritto e committato il 18 ottobre 2026 **prima del calcolo** (REGOLE.md, sezioni 6bis e 7). Periodo C2
(2024-01-01 → 2025-06-30); 24 monete della fase 2. Programma: `strumenti/esplora_limiti.py`.

## Cosa si calcola

* **R** (come E-002): ordine limite ogni ora a `P·exp(∓k·σ)`, esecuzione solo ad attraversamento, uscita a mercato H
  minuti dopo; lordo senza costi. Lato acquisto e vendita; k 2, 3, 4, 6; H 15, 60, 240, 1.440. **32 celle.**
* **S** (come E-005): lo stesso ingresso, uscita a limite a `L·exp(±m·σ)` dal minuto dopo, ad attraversamento, altrimenti
  a mercato dopo H minuti; **netto** (0,02% per lato a limite, a mercato 0,05% e scarto doppio). k 2, 3, 4, 6; m 0,5,
  1, 2; H 15, 60, 240. **72 celle.**

## Criteri di promozione

R: lordo ≥ 0,25% e contro il caso ≥ 0,20%; S: netto ≥ 0,05% e netto a costi doppi > 0. Per tutte: t ≥ 3; positivo in
ogni semestre di C2 con almeno 20 trade; positivo su almeno il 70% delle monete con almeno 10 trade, e almeno 10 monete;
almeno 100 trade. Al massimo 3 idee J (stesso tipo e stesso lato in una idea, al massimo 3 varianti, le più forti per t).
**Il lato acquisto** è parente del rimbalzo dopo i crolli e dello scalping di I-020, già provati su R sulle 12 monete della
fase 1: se diventa un'idea, su V2 si prova solo sulle 12 monete nuove. Il lato vendita no.
