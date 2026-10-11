# Vault — risultati (Passo 5, 11 ottobre 2026)

Vault aperto alle 19:26 UTC dell'11 ottobre (`APERTURA.md`, commit de09b557) dopo la frase del proprietario delle 17:29
UTC. Ogni candidato ha girato **una volta sola**, con il suo codice e il lanciatore committato prima dell'apertura
(`research/vault_strumenti/`, commit 92946ab2): BTCUSDT-V10 alle 19:27-19:31 UTC, BNBUSDT-045 alle 19:32-19:37, ADAUSDT-037
alle 21:32-21:35. Risultati completi accanto: `<ID>_vault.json` (scritto per primo), `<ID>_vault.md`, e il marcatore
`<ID>_giro_iniziato.json` con la storia del giro. Dati del vault: tutti i file mensili presenti e leggibili per le tre
monete; un solo avviso, giugno 2026, con un giorno di prezzo mark mancante (96,7% delle barre allineate), uguale per le
tre. Nessuna fermata sui dati, nessuna ripresa.

## Esito

**Nessuno dei tre candidati passa il criterio del vault.**

| Candidato | Trade | R medio a trade dopo i costi | Profit factor (min 1,10) | Rendimento | Sopra il 90° percentile del caso | Esito | Tasso del caso |
|---|---|---|---|---|---|---|---|
| BTCUSDT-V10 (rottura dall'apertura del giorno, long, 1 ora) | 325 | +0,031 | **1,067** | +9,8% | sì (90° percentile −0,274) | **non passa** (solo il profit factor) | 0,1% (1 su 1000) |
| BNBUSDT-045 (cali bruschi in tendenza, fine settimana, long, 1 ora) | 94 | −0,087 | 0,55 | −9,1% | no (−0,028) | **non passa** | 0,4% (4 su 1000) |
| ADAUSDT-037 (rottura dell'intervallo d'apertura con due filtri, long, 15 minuti) | 167 | −0,164 | 0,79 | −26,3% | no (−0,086) | **non passa** | 1,5% (15 su 1000) |

Il tasso del caso è la quota delle 1000 strategie a entrate casuali (stessa moneta, direzione, numero di trade, durata
media e uscita, semi 0-999) che passano lo stesso criterio. Sommato sui tre candidati, il numero di passaggi atteso per
puro caso è circa 0,02; i passaggi veri sono 0. Il giudizio d'insieme è del Passo 7.

## Cosa è cambiato rispetto all'in-sample (Passo 5, punto 5)

**BTCUSDT-V10.** Il vantaggio si è assottigliato a ogni periodo: R medio a trade +0,149 in costruzione (300 trade,
profit factor 1,36), +0,048 in validazione (136 trade, 1,128), +0,031 nel vault (325 trade, 1,067). Nel vault è positivo
solo il 2024 (+0,159 su 119 trade, anno in cui BTC fa +121%), poi −0,041 nel 2025 e −0,046 nel 2026. Contro le entrate
casuali con la stessa uscita resta nettamente sopra (baseline (b): t 3,01, p 0,0015; baseline (a): t 4,67; percentile 99):
qualcosa di non casuale c'è, ma dopo i costi non basta per il profit factor minimo. Senza i 3 trade migliori l'R medio
scende a −0,011. Fallisce per la sola condizione del profit factor.

**BNBUSDT-045.** Il vantaggio è sparito del tutto: R medio +0,138 in costruzione (74 trade, profit factor 2,76), +0,047 in
validazione (32 trade, 1,49), −0,087 nel vault (94 trade, 0,55), negativo in tutti e tre gli anni (−0,041, −0,113,
−0,112). Nel vault fa come la media delle entrate casuali (−0,079; percentile 40; baseline (b): p 0,60). La campagna
aveva scritto le sue riserve: 32 trade di validazione appena sopra il minimo, costi maggiori dell'R medio, cinque ritocchi.

**ADAUSDT-037.** In validazione l'R medio di +0,624 (82 trade, profit factor 2,15) veniva quasi tutto da 3 trade: senza di
loro era +0,014, come la campagna stessa aveva scritto. Nel vault la coda dei grandi guadagni non è arrivata: R medio
−0,164 su 167 trade, 113 uscite allo stop, profit factor 0,79, rendimento −26,3%; positivo solo il 2024 (+0,092 su 65
trade), poi −0,329 e −0,326, negli anni in cui ADA scende (buy and hold −61% nel 2025 e −26% nel 2026). Non batte le
entrate casuali (baseline (b): p 0,24; percentile 82).

## Cosa resta da fare (STOP del Passo 5)

* **Passo 5, punto 2** (dati del vault delle altre 17 monete di campagna) e **Passo 6** (trasferimento dei candidati sulle
  altre monete): non fatti. Il protocollo li prevede per «ogni candidato consegnato»; con tre candidati bocciati nel loro
  vault il trasferimento direbbe solo se le stesse regole funzionano altrove. Decide il proprietario.
* **Passo 7** (giudizio d'insieme, confronto fra monete, unione dei branch e delle lezioni): dopo la sua decisione.
