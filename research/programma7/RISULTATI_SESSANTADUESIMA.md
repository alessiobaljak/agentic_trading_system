# Programma 7 — risultati della sessantaduesima prova (G1M: G1 con un minimo di monete per lato)

Regole in `SESSANTADUESIMA.md` (scritte prima). Dal 4 gennaio 2021 al 5 ottobre 2026, stesso codice e stessi dati per tutte e due.

| | Sharpe | l'anno | discesa (settimane) | discesa (giorni) | giorno peggiore | settimana peggiore |
|---|---|---|---|---|---|---|
| G1 | 1.97 | +54.3% | -28.8% | -30.1% | -8.50% (2021-01-30) | -9.36% |
| G1M | 1.95 | +52.8% | -30.4% | -31.7% | -6.80% (2021-01-30) | -9.36% |

* Giorni con l'esposizione ridotta: 88, fattore medio 0.75.
* Per anno G1M: 2021 +103.7%, 2022 +31.7%, 2023 +8.2%, 2024 +65.6%, 2025 +72.5%, 2026 +28.5%; G1: 2021 +109.9%, 2022 +31.7%, 2023 +8.2%, 2024 +68.0%, 2025 +72.5%, 2026 +28.5%.
* Ricampionamento a blocchi di 8 settimane: G1M scende meno di G1 nel 21% dei casi.
* Sharpe corretto di G1M 0.85 (80 gruppi), t 4.69.

**Esito: non passa** (discesa e giorno peggiore più bassi di G1, Sharpe non più di 0,10 sotto).

## Cosa abbiamo capito

* **Ridurre l'esposizione nei giorni con poche monete toglie il giorno peggiore, ma non la discesa.**
  * L'esposizione scende in 88 giorni, al 75% in media.
  * Il giorno peggiore passa da −8,50% a −6,80% (30 gennaio 2021, il rialzo di XRP che la revisione di G1N aveva indicato).
  * La discesa massima però peggiora un poco (−30,4% contro −28,8%), perché nei giorni ridotti si perdono anche i guadagni (2021 +103,7%
    contro +109,9%, 2024 +65,6% contro +68,0%).
  * Nel ricampionamento G1M scende meno di G1 solo nel 21% dei casi.
* **Esito: no**, per la regola scritta prima.
* **Il rischio della moneta sola molto pesante resta**, per i soldi veri (backlog P26). Il tetto per moneta (prova 61) e questo minimo di
  monete non lo tolgono senza costare. L'unica protezione semplice resta il capitale piccolo all'inizio, come previsto nel piano.
