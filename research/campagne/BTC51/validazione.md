# Validazione della campagna BTC51 (Passo 3)

Scritto dalla sessione di ricerca il 2026-10-17T13:49:00Z. Via libera del coordinamento: `via_libera_validazione.md` (sì del proprietario, «sì procedi con la validazione»).

## 1. Candidato congelato

Candidati: **V-020** (l'unico). Impronte SHA-256 calcolate prima di caricare i dati della validazione, confrontate con quelle del via libera:

| File | SHA-256 | Uguale al via libera |
|---|---|---|
| `candidati/V-020/regole.md` | `7eb2cc234a8dc6a64d09bb310c46968309e3b6b0532559cb95a0f28b39d129f7` | sì |
| `codice/lotto_2.json` | `dfb3695b8b2d0aebe3236beab610f07f7bc394df00a2c86fed49f5e4fdfa8232` | sì |
| `codice/lotto.py` | `455b5ca3a16e9c308b0de5625ea1943cf31abb342de3f063f1c5bf13d714a91f` | sì |
| `codice/registro.py` | `fe3d7a140092fc887e0abd8042c40896c4402cc1ead5c15606f5bd72dc08b1ab` | sì |

Esito del confronto: **tutte uguali**. Congelamento committato (`678c86d`) prima di caricare i dati della validazione.

## 2. Esecuzione

Una sola esecuzione, il 17 ottobre 2026 (log: `V-020-VAL`, registrazione e risultato; codice
`codice/passo3_validazione.py`; trade in `risultati/V-020_validazione.json`), senza ritocchi, a costi normali e a costi
doppi. Decisioni alle chiusure delle candele orarie dal 2022-10-01 00:00 al 2023-12-31 23:00 UTC.

Scelta dichiarata: la serie è caricata dal 2020-01-01, così gli indicatori (qui solo l'ATR 14 dello stop) arrivano
già calcolati all'inizio della validazione, come per il bot dal vivo. Nessun dato oltre il 2023-12-31, nessun trade
legge oltre la fine del periodo. Con la serie caricata solo dal 2022-10-01 cambierebbero al massimo le prime 42 ore.

Previsione scritta prima (log): R medio fra −0,1 e +0,15, probabilmente sotto la metà dell'R di costruzione.
**La previsione era sbagliata.**

## 3. Risultati (osservato)

| Metrica | Costruzione (2020-01 → 2022-09) | Validazione (2022-10 → 2023-12) |
|---|---|---|
| Trade | 180 | 80 |
| Trade al mese | 5,46 | 5,33 |
| R medio | +0,223 | **+0,167** |
| Profit factor | 1,46 | 1,29 |
| Vincenti | 48,3% | 40,0% |
| R medio dei vincenti / perdenti | — | +1,852 / −0,957 |
| Drawdown massimo | −9,0 R | −14,7 R |
| R medio a costi doppi | +0,147 | **+0,064** |
| Uscite | — | 40 per stop, 40 a tempo |
| Trade ridotti per la leva / violazioni di liquidazione | — | 3 / 0 |

Somma degli R per anno: 2022 (ottobre-dicembre, 28 trade) +7,52 R, cioè +0,268 a trade; 2023 (52 trade) +5,81 R,
cioè +0,112 a trade.

## 4. Condizioni della sezione 10.3 (validazione)

| Condizione | Soglia | Valore | Esito |
|---|---|---|---|
| Trade | almeno 60 | 80 | sì |
| R medio positivo dopo i costi | > 0 | +0,167 | sì |
| Almeno la metà dell'R di costruzione | ≥ 0,111 | +0,167 | sì |
| Profit factor | almeno 1,05 | 1,29 | sì |
| R medio positivo a costi doppi | > 0 | +0,064 | sì |

**Esito: V-020 supera la validazione.**

## 5. Da sapere prima del vault (inferito)

- Il vantaggio si è ridotto: da +0,223 a +0,167 R a trade, e nel 2023 da solo +0,112. A costi doppi resta poco
  (+0,064). Il drawdown è più profondo che in costruzione (−14,7 contro −9,0 R).
- Per il protocollo la validazione toglie solo i candidati che crollano; la significatività si giudica una volta
  sola, nel vault (sezione 10.3). Con 80 trade un R medio di +0,167 sta a circa 1,2 errori standard da zero (dispersione
  1,2 R, sezione 5.2): compatibile con un vantaggio vero, ma anche con il caso.
- Da qui non si costruiscono nuovi candidati (regola 9). Il vault resta chiuso: si apre solo con «APRI IL VAULT 3».

