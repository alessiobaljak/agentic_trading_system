# Residual Edge Analysis

**Status:** RESIDUAL_EDGE
**Decision eligibility:** REVIEW_REQUIRED
**Period:** 2021-01-04 to 2026-10-04 (2100 observations)
**Primary model:** mercato_e_altcoin

## Primary Model

| Metric | Value |
|---|---:|
| R² | 0.0356 |
| Adjusted R² | 0.0347 |
| Annualized alpha | 62.4095% |
| Alpha HAC t-stat | 5.140 |
| Annualized residual volatility | 26.9409% |
| Residual edge ratio | 2.317 |

## Baseline Loadings

| Baseline | Loading | HAC t-stat | VIF |
|---|---:|---:|---:|
| mercato | 0.0069 | 0.211 | 2.743 |
| pesi_uguali | -0.0638 | -2.376 | 2.743 |

## Model Sensitivity

| Model | Role | R² | Annualized alpha | Residual edge ratio | Status |
|---|---|---:|---:|---:|---|
| mercato_e_altcoin | primary | 0.0356 | 62.4095% | 2.317 | RESIDUAL_EDGE |
| mercato | sensitivity | 0.0210 | 63.0917% | 2.324 | RESIDUAL_EDGE |
| piu_momento | sensitivity | 0.0356 | 62.4816% | 2.319 | RESIDUAL_EDGE |
| piu_settori | sensitivity | 0.0367 | 62.2529% | 2.312 | RESIDUAL_EDGE |
| tutti | sensitivity | 0.0367 | 62.2765% | 2.313 | RESIDUAL_EDGE |

## Evidence Warnings

- **HIGH — NOT_OUT_OF_SAMPLE:** Treat in-sample residual edge as exploratory until confirmed out of sample.

## Regime Breakdown

### bitcoin_30_giorni

| Regime | N | Evidence | Annualized active return | Active Sharpe |
|---|---:|---|---:|---:|
| sopra | 1130 | ADEQUATE | 56.4021% | 1.993 |
| sotto | 970 | ADEQUATE | 69.4078% | 2.745 |

## Interpretation

- Alpha, residual edge ratio, and rolling stability clear the configured thresholds.
- This report does not authorize a trade or an automatic exposure change.
- Confirm exploratory findings on untouched out-of-sample or live data.
