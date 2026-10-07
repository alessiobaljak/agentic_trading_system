# Collegamenti fra contratti (ridenominazioni e migrazioni)

Branch `research/coordinamento`. Al Passo 1 NON si applica nessuna cucitura: la selezione usa i simboli validi
nel 2023 e i loro dati fino al 2023-12-31. I collegamenti servono al Passo 5 (vault) e al Passo 6
(trasferimento), dove una moneta di campagna può continuare sotto un altro simbolo; lì si verificano SUI DATI
(ultimo mese del vecchio simbolo, primo mese del nuovo, rapporto di conversione) prima di usarli.

## Prima del 2024 (riguardano l'in-sample)

Nessun collegamento applicato: i contratti «1000x» (1000SHIBUSDT, 1000LUNCUSDT, 1000XECUSDT, 1000PEPEUSDT,
1000FLOKIUSDT, 1000BONKUSDT, 1000SATSUSDT) sono stati quotati con quel nome fin dall'inizio, non sono
ridenominazioni. Se al Passo 3 una campagna trova un buco o un salto di prezzo nella sua serie, lo registra in
`fase0_dati.md` e si ferma: si decide col coordinamento.

## Dopo il 2023 (ipotesi da verificare sui dati al Passo 5, non prima)

| Simbolo 2023 | Ipotesi di continuazione | Quando (ipotizzato) | Nota |
|---|---|---|---|
| MATICUSDT | POLUSDT | 2024 | migrazione del token 1:1 |
| RNDRUSDT | RENDERUSDT | 2024 | ridenominazione |
| FTMUSDT | SUSDT | 2025 | migrazione 1:1; nell'archivio FTMUSDT ha file fino al 2026-09 e oggi non è TRADING: da capire sui dati |
| KLAYUSDT | KAIAUSDT | 2024 | migrazione |
| AGIXUSDT, OCEANUSDT | FETUSDT | 2024 | fusione di token: rapporto diverso da 1, da verificare |

Sono ipotesi scritte a memoria il 7 ott 2026 ("ipotizzato", non "osservato"): nessuna è stata controllata.
Al Passo 5 ognuna si conferma o si scarta guardando i file: se il vecchio simbolo finisce e il nuovo comincia
nello stesso mese, con un rapporto di prezzo coerente, si ricuce (`motore.ricuci_serie`) e si dichiara il punto;
altrimenti il contratto si tratta come delistato (regola «Delisting» della sezione 7).

## Trovati al Passo 1 (7 ott 2026)

Fra le 20 monete di campagna, due non sono più negoziate con il simbolo del 2023: **MATICUSDT** (ultimo file
nell'archivio 2024-09, ipotesi POLUSDT) e **FTMUSDT** (file nell'archivio fino al 2026-09, ma su exchangeInfo al 7 ott 2026 lo stato non è TRADING: contratto in chiusura; ipotesi di continuazione SUSDT, da verificare). Le loro campagne
valgono per il vault e il trasferimento (regola del Passo 1); la cucitura si decide al Passo 5 sui dati.
Contratti spariti durante l'in-sample (nessuno di campagna): 1000BTTCUSDT, AKROUSDT, ANCUSDT, BTTUSDT,
DODOUSDT, KEEPUSDT, LUNAUSDT, NUUSDT, YFIIUSDT.
