# Prova a placebo a barre giornaliere — risultati

Scritto da `riassunto.py` di questa cartella il 2026-10-14T11:40:52Z, commit 49a1e99b; regole in `regole.md` (soglie: al massimo il 3% di «nette» in costruzione, al massimo il 13% con p sotto 0,10 in validazione, almeno 40 placebo valutabili per periodo). Le righe sono in `esiti_k<k>.jsonl`, il riassunto completo in `riassunto.json`.

```
file di k [0, 1, 2, 3]; righe 96, illeggibili 0; commit principale ['08e2c95a'], prova ['08e2c95a']
sfasamenti usati [0, 1, 2, 3]; copertura: 96 su 96 (24 combinazioni x 4 sfasamenti x 2 periodi); righe con errore 0, errori senza una riga buona 0
campione: valutabili in costruzione 46, in validazione 47 (minimo 40 per periodo); scarti in costruzione {'sotto il minimo di trade': 2, 'una moneta oltre il 10%': 0}; validazione sotto il minimo di trade 0
non valutabili: {'validazione: meno di 3 blocchi interi o candidato senza rumore stimabile': 1}
costruzione: n 46; M1 0 con z > 2 (limite 1, quota 0.00%); μ 0.090, σ 0.707; M3 P(z > 2) 0.35% (soglia 3.00%)
validazione: n 47; M2 0 con z > 1,282 (limite 6, quota 0.00%); μ -0.084, σ 0.550; M3 P(z > 1,282) 0.65% (soglia 13.00%)
condizioni: M1 regge, M2 regge, M3_costruzione regge, M3_validazione regge
ESITO: l'esame di gruppo regge sui prezzi veri
--- solo informative ---
letture diverse fra z e «netta»/«p < 0,10» del confronto, costruzione: 0
letture diverse fra z e «netta»/«p < 0,10» del confronto, validazione: 0
senza il pavimento delle sfasate, costruzione: n 46; M1 0 con z > 2 (limite 1, quota 0.00%); μ 0.089, σ 0.738; M3 P(z > 2) 0.48% (soglia 3.00%)
senza il pavimento delle sfasate, validazione: n 47; M2 1 con z > 1,282 (limite 6, quota 2.13%); μ -0.104, σ 0.636; M3 P(z > 1,282) 1.46% (soglia 13.00%)
dove decide il pavimento delle sfasate, costruzione: 12 placebo, sd((R - B)/pavimento) 0.785
dove decide il pavimento delle sfasate, validazione: 15 placebo, sd((R - B)/pavimento) 0.835
validazione, R medio sopra il 90° percentile delle proprie sfasate: 3 su 47 (6.38%, atteso circa 10%)
costruzione: effetto grappolo mediana 15.08 (25-75%: 11.60-17.73); quota della moneta piu' presente mediana 2.84%, massimo 4.04%
validazione: effetto grappolo mediana 13.60 (25-75%: 8.82-17.08); quota della moneta piu' presente mediana 2.25%, massimo 2.77%
intervalli al 95% ricampionando le combinazioni, costruzione: quota 0.00%-0.00%; μ -0.058-0.244; σ 0.558-0.811; coda M3 0.04%-0.98%
intervalli al 95% ricampionando le combinazioni, validazione: quota 0.00%-0.00%; μ -0.294-0.127; σ 0.421-0.640; coda M3 0.03%-2.47%
per timeframe:
  1d costruzione: n 46; M1 0 con z > 2 (limite 1, quota 0.00%); μ 0.090, σ 0.707; M3 P(z > 2) 0.35% (soglia 3.00%)
  1d validazione: n 47; M2 0 con z > 1,282 (limite 6, quota 0.00%); μ -0.084, σ 0.550; M3 P(z > 1,282) 0.65% (soglia 13.00%)
per direzione:
  long costruzione: n 23; M1 0 con z > 2 (limite 0, quota 0.00%); μ 0.234, σ 0.564; M3 P(z > 2) 0.09% (soglia 3.00%)
  long validazione: n 23; M2 0 con z > 1,282 (limite 2, quota 0.00%); μ -0.019, σ 0.505; M3 P(z > 1,282) 0.50% (soglia 13.00%)
  short costruzione: n 23; M1 0 con z > 2 (limite 0, quota 0.00%); μ -0.054, σ 0.813; M3 P(z > 2) 0.58% (soglia 3.00%)
  short validazione: n 24; M2 0 con z > 1,282 (limite 3, quota 0.00%); μ -0.147, σ 0.595; M3 P(z > 1,282) 0.82% (soglia 13.00%)
per regola:
  bollinger costruzione: n 8; M1 0 con z > 2 (limite 0, quota 0.00%); μ 0.005, σ 0.622; M3 P(z > 2) 0.07% (soglia 3.00%)
  bollinger validazione: n 8; M2 0 con z > 1,282 (limite 1, quota 0.00%); μ 0.011, σ 0.797; M3 P(z > 1,282) 5.54% (soglia 13.00%)
  incrocio_medie costruzione: n 6; M1 0 con z > 2 (limite 0, quota 0.00%); μ 0.210, σ 0.425; M3 P(z > 2) 0.00% (soglia 3.00%)
  incrocio_medie validazione: n 8; M2 0 con z > 1,282 (limite 1, quota 0.00%); μ -0.205, σ 0.282; M3 P(z > 1,282) 0.00% (soglia 13.00%)
  macd costruzione: n 8; M1 0 con z > 2 (limite 0, quota 0.00%); μ 0.031, σ 0.762; M3 P(z > 2) 0.49% (soglia 3.00%)
  macd validazione: n 8; M2 0 con z > 1,282 (limite 1, quota 0.00%); μ -0.036, σ 0.222; M3 P(z > 1,282) 0.00% (soglia 13.00%)
  momento costruzione: n 8; M1 0 con z > 2 (limite 0, quota 0.00%); μ 0.190, σ 0.989; M3 P(z > 2) 3.36% (soglia 3.00%)
  momento validazione: n 8; M2 0 con z > 1,282 (limite 1, quota 0.00%); μ -0.349, σ 0.565; M3 P(z > 1,282) 0.19% (soglia 13.00%)
  rottura costruzione: n 8; M1 0 con z > 2 (limite 0, quota 0.00%); μ 0.111, σ 0.736; M3 P(z > 2) 0.52% (soglia 3.00%)
  rottura validazione: n 7; M2 0 con z > 1,282 (limite 0, quota 0.00%); μ -0.092, σ 0.707; M3 P(z > 1,282) 2.60% (soglia 13.00%)
  rsi costruzione: n 8; M1 0 con z > 2 (limite 0, quota 0.00%); μ 0.023, σ 0.747; M3 P(z > 2) 0.41% (soglia 3.00%)
  rsi validazione: n 8; M2 0 con z > 1,282 (limite 1, quota 0.00%); μ 0.166, σ 0.545; M3 P(z > 1,282) 2.04% (soglia 13.00%)
limiti: finestra unione diversa da quella del pavimento in 0 placebo []; durata massima dei trade a meno di 60 barre dal margine in 93 ['GRUPPO|1d|incrocio_medie|long|costruzione|0', 'GRUPPO|1d|incrocio_medie|short|costruzione|0', 'GRUPPO|1d|rsi|long|costruzione|0', 'GRUPPO|1d|rsi|short|costruzione|0', 'GRUPPO|1d|rottura|long|costruzione|0', 'GRUPPO|1d|rottura|short|costruzione|0', 'GRUPPO|1d|bollinger|long|costruzione|0', 'GRUPPO|1d|bollinger|short|costruzione|0', 'GRUPPO|1d|macd|long|costruzione|0', 'GRUPPO|1d|macd|short|costruzione|0', 'GRUPPO|1d|momento|long|costruzione|0', 'GRUPPO|1d|momento|short|costruzione|0', 'GRUPPO|1d|rsi|long|costruzione|1', 'GRUPPO|1d|rsi|short|costruzione|1', 'GRUPPO|1d|rottura|long|costruzione|1', 'GRUPPO|1d|rottura|short|costruzione|1', 'GRUPPO|1d|bollinger|long|costruzione|1', 'GRUPPO|1d|bollinger|short|costruzione|1', 'GRUPPO|1d|macd|long|costruzione|1', 'GRUPPO|1d|macd|short|costruzione|1', 'GRUPPO|1d|momento|long|costruzione|1', 'GRUPPO|1d|momento|short|costruzione|1', 'GRUPPO|1d|incrocio_medie|long|costruzione|2', 'GRUPPO|1d|incrocio_medie|short|costruzione|2', 'GRUPPO|1d|rsi|long|costruzione|2', 'GRUPPO|1d|rsi|short|costruzione|2', 'GRUPPO|1d|rottura|long|costruzione|2', 'GRUPPO|1d|rottura|short|costruzione|2', 'GRUPPO|1d|bollinger|long|costruzione|2', 'GRUPPO|1d|bollinger|short|costruzione|2', 'GRUPPO|1d|macd|long|costruzione|2', 'GRUPPO|1d|macd|short|costruzione|2', 'GRUPPO|1d|momento|long|costruzione|2', 'GRUPPO|1d|momento|short|costruzione|2', 'GRUPPO|1d|incrocio_medie|long|costruzione|3', 'GRUPPO|1d|incrocio_medie|short|costruzione|3', 'GRUPPO|1d|rsi|long|costruzione|3', 'GRUPPO|1d|rsi|short|costruzione|3', 'GRUPPO|1d|rottura|long|costruzione|3', 'GRUPPO|1d|rottura|short|costruzione|3', 'GRUPPO|1d|bollinger|long|costruzione|3', 'GRUPPO|1d|bollinger|short|costruzione|3', 'GRUPPO|1d|macd|long|costruzione|3', 'GRUPPO|1d|macd|short|costruzione|3', 'GRUPPO|1d|momento|long|costruzione|3', 'GRUPPO|1d|momento|short|costruzione|3', 'GRUPPO|1d|incrocio_medie|long|validazione|0', 'GRUPPO|1d|incrocio_medie|short|validazione|0', 'GRUPPO|1d|rsi|long|validazione|0', 'GRUPPO|1d|rsi|short|validazione|0', 'GRUPPO|1d|rottura|short|validazione|0', 'GRUPPO|1d|bollinger|long|validazione|0', 'GRUPPO|1d|bollinger|short|validazione|0', 'GRUPPO|1d|macd|long|validazione|0', 'GRUPPO|1d|macd|short|validazione|0', 'GRUPPO|1d|momento|long|validazione|0', 'GRUPPO|1d|momento|short|validazione|0', 'GRUPPO|1d|incrocio_medie|long|validazione|1', 'GRUPPO|1d|incrocio_medie|short|validazione|1', 'GRUPPO|1d|rsi|long|validazione|1', 'GRUPPO|1d|rsi|short|validazione|1', 'GRUPPO|1d|rottura|long|validazione|1', 'GRUPPO|1d|rottura|short|validazione|1', 'GRUPPO|1d|bollinger|long|validazione|1', 'GRUPPO|1d|bollinger|short|validazione|1', 'GRUPPO|1d|macd|long|validazione|1', 'GRUPPO|1d|macd|short|validazione|1', 'GRUPPO|1d|momento|long|validazione|1', 'GRUPPO|1d|momento|short|validazione|1', 'GRUPPO|1d|incrocio_medie|long|validazione|2', 'GRUPPO|1d|incrocio_medie|short|validazione|2', 'GRUPPO|1d|rsi|long|validazione|2', 'GRUPPO|1d|rsi|short|validazione|2', 'GRUPPO|1d|rottura|long|validazione|2', 'GRUPPO|1d|rottura|short|validazione|2', 'GRUPPO|1d|bollinger|long|validazione|2', 'GRUPPO|1d|bollinger|short|validazione|2', 'GRUPPO|1d|macd|long|validazione|2', 'GRUPPO|1d|macd|short|validazione|2', 'GRUPPO|1d|momento|long|validazione|2', 'GRUPPO|1d|momento|short|validazione|2', 'GRUPPO|1d|incrocio_medie|long|validazione|3', 'GRUPPO|1d|incrocio_medie|short|validazione|3', 'GRUPPO|1d|rsi|long|validazione|3', 'GRUPPO|1d|rsi|short|validazione|3', 'GRUPPO|1d|rottura|long|validazione|3', 'GRUPPO|1d|rottura|short|validazione|3', 'GRUPPO|1d|bollinger|long|validazione|3', 'GRUPPO|1d|bollinger|short|validazione|3', 'GRUPPO|1d|macd|long|validazione|3', 'GRUPPO|1d|macd|short|validazione|3', 'GRUPPO|1d|momento|long|validazione|3', 'GRUPPO|1d|momento|short|validazione|3']
  senza la sfasata piu' vicina agli ingressi della regola, costruzione: 0 su 46 cambiano lettura; distanza 0 in 14; distanza mediana 1.0 barre; scarto mediano 0.43 sd
  senza la sfasata piu' vicina agli ingressi della regola, validazione: 0 su 47 cambiano lettura; distanza 0 in 38; distanza mediana 0.0 barre; scarto mediano 0.07 sd
```
