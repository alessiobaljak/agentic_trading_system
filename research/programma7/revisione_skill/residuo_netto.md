# Residual Edge Analysis

**Status:** RESIDUAL_EDGE
**Decision eligibility:** REVIEW_REQUIRED
**Period:** 2021-01-04 to 2026-10-04 (2100 observations)
**Primary model:** mercato_e_altcoin

## Primary Model

| Metric | Value |
|---|---:|
| R² | 0.0355 |
| Adjusted R² | 0.0346 |
| Annualized alpha | 55.8567% |
| Alpha HAC t-stat | 4.602 |
| Annualized residual volatility | 26.9234% |
| Residual edge ratio | 2.075 |

## Baseline Loadings

| Baseline | Loading | HAC t-stat | VIF |
|---|---:|---:|---:|
| mercato | 0.0064 | 0.197 | 2.743 |
| pesi_uguali | -0.0635 | -2.366 | 2.743 |

## Model Sensitivity

| Model | Role | R² | Annualized alpha | Residual edge ratio | Status |
|---|---|---:|---:|---:|---|
| mercato_e_altcoin | primary | 0.0355 | 55.8567% | 2.075 | RESIDUAL_EDGE |
| mercato | sensitivity | 0.0211 | 56.5354% | 2.084 | RESIDUAL_EDGE |
| piu_momento | sensitivity | 0.0356 | 55.9265% | 2.077 | RESIDUAL_EDGE |
| piu_settori | sensitivity | 0.0366 | 55.7022% | 2.070 | RESIDUAL_EDGE |
| tutti | sensitivity | 0.0366 | 55.7241% | 2.071 | RESIDUAL_EDGE |

## Evidence Warnings

- **HIGH — RETURN_BASIS_MISMATCH:** Strategy and baseline returns use different gross/net cost bases.
- **HIGH — NOT_OUT_OF_SAMPLE:** Treat in-sample residual edge as exploratory until confirmed out of sample.

## Regime Breakdown

### bitcoin_30_giorni

| Regime | N | Evidence | Annualized active return | Active Sharpe |
|---|---:|---|---:|---:|
| sopra | 1130 | ADEQUATE | 49.1713% | 1.739 |
| sotto | 970 | ADEQUATE | 63.6449% | 2.519 |

## Interpretation

- Alpha, residual edge ratio, and rolling stability clear the configured thresholds.
- This report does not authorize a trade or an automatic exposure change.
- Confirm exploratory findings on untouched out-of-sample or live data.
