# Programma 6 — risultati della quattordicesima prova (il modello che unisce gli indicatori)

Regole in `QUATTORDICESIMA.md` (scritte prima). Le 100 monete più scambiate, dal 3 gennaio 2022; il modello si allena ogni 4 settimane solo sul passato.

| Modello | Rendimento/anno | Sharpe | Intervallo (settimana) | Sharpe corretto | Anni positivi | Ultimo anno | Dal prezzo | Dal funding | Correlazione F3, K1 | 101-200 (informazione) | Esito |
|---|---|---|---|---|---|---|---|---|---|---|---|
| M1 | +50.9% | 1.35 | +0.29%; +1.67% | 0.59 | 4/5 | +57.9% | +71.7% | -12.1% | 0.17, 0.03 | +309.9%, Sharpe 6.67 | Sharpe corretto 0.59 sotto 0,95 |
| M2 | +25.4% | 0.62 | -0.24%; +1.20% | 0.09 | 3/5 | +55.7% | +42.5% | -9.1% | 0.27, 0.01 | +82.7%, Sharpe 1.98 | netto con l'intervallo non sopra zero |

**M1, per anno**: 2022 +84.9%, 2023 +38.9%, 2024 -5.1%, 2025 +62.6%, 2026 +80.5%
**M1, gli ingredienti che contano di più nell'ultimo modello**: eta (0.0107), vol_30 (0.0091), min_30 (0.0082), oi_1 (0.0077), btc_rend_30 (0.0071), ampiezza_7 (0.0062), oi_sul_volume (0.0059), vol_propria_90 (0.0058), btc_rend_7 (0.0058), grandezza (0.0056)

**M2, per anno**: 2022 +70.3%, 2023 -15.8%, 2024 -20.5%, 2025 +30.9%, 2026 +73.1%
**M2, gli ingredienti che contano di più nell'ultimo modello**: sma_10d (0.0810), boll_high (0.0728), rend_7 (0.0612), ls_differenza_7 (0.0592), boll_low (0.0565), ls_tutti_7 (0.0553), ampiezza_7 (0.0548), sma_200d (0.0516), rend_180 (0.0478), sma_50d (0.0399)

## Correzione dopo la verifica (20 ottobre 2026)

Il numero «101-200 (informazione)» della tabella (+309,9% l'anno, Sharpe 6,67 per M1) è **sbagliato**: è una fuga di
informazione dal futuro. I dati sulle posizioni (`scarico_metrics.py`) li ho scaricati solo per le monete delle prime 100 e
per i 30 giorni prima che ci entrassero: fra le monete 101-200 ha il dato proprio chi **sta per entrare** fra le prime 100
(cioè chi sta per avere un'impennata di volume e spesso di prezzo). Lo mostra il legame medio di rango fra un ingrediente e il
rendimento della settimana dopo: per il rapporto fra acquisti e vendite a mercato 0,370 sulle 101-200 contro 0,044 sulle
prime 100; per il rapporto long/short dei conti 0,319 contro 0,018.

* **Sulle prime 100 la fuga non c'è**: il dato esiste per tutte le monete dell'universo di quella settimana (i 30 giorni
  prima di ogni settimana in cui la moneta è dentro), quindi la sua presenza non dice niente sul futuro. Il risultato
  dell'esame (M1: Sharpe 1,35) resta.
* **Rifatto sulle 101-200 senza i dati sulle posizioni** (`risultati_quattordicesima/monete_101_200_senza_posizioni.json`):
  M1 −2,3% l'anno (Sharpe −0,05), M2 +0,4% (Sharpe 0,01) su 182 settimane. Come per F3: fra le monete piccole, con lo scarto
  allo 0,10%, il vantaggio non c'è.
