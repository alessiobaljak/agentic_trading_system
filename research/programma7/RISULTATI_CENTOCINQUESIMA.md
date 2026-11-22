# Risultati della prova 167 (regole in `CENTOCINQUESIMA.md`, commit 699508f)

## Riepilogo
**Esito: «campione troppo piccolo».** Dopo tutti i filtri gli eventi sono **26**, meno di 40. Come scritto nelle regole: nessun prezzo
caricato, nessun rendimento calcolato, nessuna variante eseguita, la prova non entra nel conto. Non è né PASS né FAIL sul valore.
Eventi per anno (fine del voto): 2021: 1, 2022: 3, 2023: 3, 2024: 6, 2025: 9, 2026: 4.

## La prova come è scritta (citata) e scala di tempo
«Un voto che passa e destina soldi ai possessori [...] comprare il perpetuo della moneta e vendere il perpetuo del Bitcoin per lo stesso
valore»; entrata all'apertura del primo giorno dopo la fine del voto; tenuta A = 5 giorni, B = 10 giorni. Scala di tempo: giornaliera
(entrata e uscita all'apertura del giorno), serie settimanali. «Se gli eventi veri sono meno di 40 il rapporto lo scrive e l'esito è
"campione troppo piccolo"» (regole, sezione sul numero di eventi; e punto 7 della Chiusura della verifica).

## Implementazione (file, commit)
* `research/programma7/centocinquesima_dati.py`: proposte e spazi da Snapshot (`hub.snapshot.org/graphql`, una query per parola, `skip` a passi
  di 1.000), elenco dei nomi delle cartelle di `data.binance.vision` (solo nomi, nessun prezzo), filtri, elenco eventi.
* `research/programma7/centocinquesima.py`: ferma la prova sotto i 40 eventi. Il passo 2 (prezzi, A e B, esame) non è scritto.
* Dati grezzi in `research/data/centocinquesima/` (non in git). Nessun commit fatto (come richiesto). Regole committate: 164b6c2 e 699508f.

## Varianti provate
**0.** Nessuna variante eseguita e nessuna riga scritta in `research/trials/centocinquesima.csv` (il file non esiste): niente è stato calcolato.

## Risultati
Nessun rendimento, nessuna discesa, nessun Sharpe: non calcolati per regola.

### Conto dei filtri (solo Snapshot e nomi dei file)
| Passo | Proposte |
|---|---|
| Proposte chiuse trovate con le 9 parole (pezzo di parola, senza doppioni) | 1.599 (in 841 spazi) |
| Parola intera nel titolo (`burn` non dentro altra parola; «buybacks», «burns», «burning» non valgono) | 1.211 |
| Fine del voto dal 1° gen 2021 al 31 ott 2026 | 1.170 |
| Spazio ufficiale (criterio meccanico, vedi sotto) | 55 |
| Senza parole di stop (pause, stop, end, ...) | 52 |
| Approvata (scelta più votata comincia con Yes/For/Approve/Accept/In favor; voti > 0) | 31 |
| Perpetuo presente nel mese dell'entrata (archivio mensile) | 27 |
| Un solo evento per moneta ogni 30 giorni dalla fine dell'ultimo evento tenuto | **26** |
Il numero massimo di eventi aperti insieme (con tenuta 10 giorni) sarebbe 2: il limite di 10 non si raggiunge.
Il controllo sul giorno esatto (perpetuo e Bitcoin con candela il giorno di entrata e di uscita) richiede i prezzi e non è stato fatto: può
solo togliere eventi.

### Spazi: 28 entrano, 813 escono (elenco completo con motivo: `risultati_centocinquesima/spazi.json`)
Motivi di uscita: sigla senza perpetuo USDT nell'archivio 754; non verificato in Snapshot 50; il nome dello spazio non contiene né la sigla né
il nome della moneta 8; sigla sempre fuori e nome della moneta assente 1 (nessuno spazio risulta segnalato fra quelli con perpetuo).
Entrano (spazio → perpetuo): aavedao.eth → AAVEUSDT, balancer.eth → BALUSDT, chaingov.eth → XCNUSDT, chaingptai.eth → CGPTUSDT, cvx.eth → CVXUSDT, dao.spaceid.eth → IDUSDT, dforcenet.eth → DFUSDT, diadao.eth → DIAUSDT, dodobird.eth → DODOUSDT, ethenagovernance.eth → ENAUSDT, etherfi-dao.eth → ETHFIUSDT, floki-inu.eth → 1000FLOKIUSDT, gmx.eth → GMXUSDT, governance.qredo.eth → OPENUSDT, listavote.eth → LISTAUSDT, pathvote.eth → PATHUSDT, quickvote.eth → QUICKUSDT, rbn.eth → AEVOUSDT, skale.eth → SKLUSDT, snxgov.eth → SNXUSDT, synapseprotocol.eth → SYNUSDT, trustwallet → TWTUSDT, uma.eth → UMAUSDT, uniswapgovernance.eth → UNIUSDT, uxlinkcommunity.eth → UXLINKUSDT, venus-xvs.eth → XVSUSDT, vote-perp.eth → PERPUSDT, worldlibertyfinancial.com → WLFIUSDT.
Usciti pur con perpetuo e verificati (da vedere): aavegotchi-dao.eth (GHST, «Aavegotchi»), abracadabrabymerlinthemagician.eth (SPELL, «Magic Internet Money»), airdaofoundation.eth (AMB, «AirDAO»), babydogevote.eth (BABYDOGE, «Baby Doge»), curve.eth (CRV, «Curve Finance»), harmony-mainnet.eth (ONE, «Harmony Mainnet»), lido-snapshot.eth (LDO, «Lido»), otterclam.eth (MATIC, «OtterClam»), radiantcapital.eth (RDNT, «Radiant Capital»).
Regola applicata alla lettera: il nome dello spazio deve contenere la sigla o il nome della moneta (da `nomi_2026-11.json`); nessuna correzione a mano.

### Gli eventi (26), per anno

* 2021: 1
* 2022: 3
* 2023: 3
* 2024: 6
* 2025: 9
* 2026: 4

| id proposta | spazio | perpetuo | titolo | fine del voto (UTC) | entrata | scelta vincente |
|---|---|---|---|---|---|---|
| QmVnsMXvSG84x3… | uniswapgovernance.eth | UNIUSDT | Turning on the fee switch for V2 | 2021-07-25 10:00 | 2021-07-26 | Yes, lets do it! |
| 0x043e3e4b29d7… | balancer.eth | BALUSDT | Protocol revenue sharing for pool creators | 2022-02-18 14:00 | 2022-02-19 | Yes, let's do it. |
| 0x4dd49ee723a7… | uniswapgovernance.eth | UNIUSDT | Temp Check: "Fee switch" activation for ETH/USDC & USDC/USDT | 2022-07-21 16:00 | 2022-07-22 | Yes |
| 0x29a37ab71ce0… | balancer.eth | BALUSDT | [BIP-32] Funding Proposal for Daoism Systems: PROTOCOL REVENUE SHARING | 2022-07-24 17:15 | 2022-07-25 | Yes, let's do it |
| 0xf5540d84b628… | cvx.eth | CVXUSDT | [Frax] [FIP - 207] Authorize matching FRAX from the FXS buyback fund w | 2023-04-04 18:42 | 2023-04-05 | For |
| 0xda972700a6d6… | dao.spaceid.eth | IDUSDT |  [IDP3] Proposed Purchase and Burn of ID Tokens | 2023-06-26 13:20 | 2023-06-27 | For |
| 0xa10a3acad164… | trustwallet | TWTUSDT | Proposal to Burn Locked TWTs for Enhanced Capitalization | 2023-11-17 14:33 | 2023-11-18 | Yes |
| 0xec8b0fd54d2b… | floki-inu.eth | 1000FLOKIUSDT | PROPOSAL: BURN 190,918,585,431.84 FLOKI TOKENS  | 2024-03-02 10:29 | 2024-03-03 | YES, BURN THE TOKENS. |
| 0xeb0cad899fbf… | floki-inu.eth | 1000FLOKIUSDT | PROPOSAL: BURN 15,246,000,000 $FLOKI TOKENS | 2024-05-15 19:12 | 2024-05-16 | YES, I VOTE IN FAVOR |
| 0x287dffb9a390… | etherfi-dao.eth | ETHFIUSDT | ETHFI DAO Proposal: ETHFI Buyback and Liquidity Pool Seeding | 2024-06-24 18:38 | 2024-06-25 | For |
| 0x34828455477f… | etherfi-dao.eth | ETHFIUSDT | ETHFI DAO Proposal: Increase to Buyback and LP Seeding Allocation | 2024-08-12 22:22 | 2024-08-13 | For |
| 0xf376c8ef077a… | quickvote.eth | QUICKUSDT | The Trial of Fire: 100% QUICK Burn | 2024-09-09 11:30 | 2024-09-10 | Yes: 3 Months |
| 0x3e8a9ad0cd5c… | synapseprotocol.eth | SYNUSDT | [SIP - 41] – Buyback 3.5 million USD worth of $SYN over 3 months | 2024-12-13 18:02 | 2024-12-14 | For |
| 0x9f7d33d74c65… | cvx.eth | CVXUSDT | [FXN] FIP 09 - bFXN Buyback and Lock Program | 2025-02-08 13:00 | 2025-02-09 | For |
| 0xee9981697978… | quickvote.eth | QUICKUSDT | Additional Extension of the 100% QUICK Burn 'Trial of Fire' | 2025-04-08 15:00 | 2025-04-09 | For |
| 0x6a9bdf1bb43b… | etherfi-dao.eth | ETHFIUSDT | #11 Ether.fi DAO Proposal - Withdrawal Revenue Buyback Program | 2025-04-29 23:17 | 2025-04-30 | For |
| 0x2a7ef78fe452… | rbn.eth | AEVOUSDT | AGP-2: Surplus Revenue Buyback Policy | 2025-05-03 16:00 | 2025-05-04 | For |
| 0xb8f03ad2dd29… | venus-xvs.eth | XVSUSDT | Proposal: BNB Afterburn – Allocating 25% of Venus BNB Chain Revenue to | 2025-06-14 18:03 | 2025-06-15 | For: Proceed to VIP. |
| 0xdb92580e04ca… | listavote.eth | LISTAUSDT | LIP 021 - LISTA Deflationary Initiative: 20% Token Burn & Tokenomics O | 2025-08-14 09:03 | 2025-08-15 | YES |
| 0x21cb61f1d925… | worldlibertyfinancial.com | WLFIUSDT | Proposal: Use 100% of WLFI Treasury Liquidity Fees for Buyback & Burn | 2025-09-18 19:27 | 2025-09-19 | FOR |
| 0xe5b64c773d23… | etherfi-dao.eth | ETHFIUSDT | Ether.Fi DAO Proposal: Treasury Deployment for ETHFI Buy-Back Program | 2025-11-03 21:57 | 2025-11-04 | For |
| 0x357d730275a8… | uxlinkcommunity.eth | UXLINKUSDT | Governance Proposal: Unlocking UXLINK’s True Value & Monthly Buyback | 2025-12-27 06:32 | 2025-12-28 | For |
| 0xe1f47bd04001… | aavedao.eth | AAVEUSDT | [ARFC] Buyback Program - Budget Adjustment | 2026-03-15 14:36 | 2026-03-16 | For |
| 0x8c6dcd025ead… | quickvote.eth | QUICKUSDT | Burn 20M QUICK from QuickSwap’s Community Treasury | 2026-07-03 16:00 | 2026-07-04 | Yes |
| 0xcb6b9ed95bf0… | ethenagovernance.eth | ENAUSDT | ENA Fee Switch | 2026-09-02 13:59 | 2026-09-03 | For |
| 0xa5d326424f02… | balancer.eth | BALUSDT | [BIP-934] Burn the 10M BEETS held by the Balancer DAO on Sonic | 2026-10-27 18:00 | 2026-10-28 | Yes, let's do it |

### Scartati dopo il filtro degli spazi (motivo → numero)
scelta vincente non e' un si → 20; parola esclusa → 3; perpetuo OPENUSDT non presen → 2; perpetuo CVXUSDT non present → 1; perpetuo CGPTUSDT non presen → 1; senza voti → 1; entro 30 giorni dall'ultimo  → 1. Elenco per proposta: `risultati_centocinquesima/scarti.json`.

## Variante migliore e sua sensibilità
Non applicabile (nessuna variante eseguita).

## Anomalie e possibili errori di motore o dati
* Snapshot rifiuta (errore 1010) le chiamate senza intestazione `user-agent`: aggiunta una generica. L'archivio S3 ha chiuso qualche connessione: ripetute le chiamate. Nomi di simboli non ASCII nell'archivio (monete con nome cinese): esclusi dal conto (non possono essere simboli di spazi in maiuscole latine).
* Totale proposte 1.599 in 841 spazi: uguale al conto della verifica.
* Effetto della regola meccanica del nome: spazi veri esclusi perché il nome non contiene la sigla o il nome nell'elenco (Curve «Curve Finance» contro CRV, Lido «Lido» contro LDO, Radiant, Aavegotchi, ecc.: vedi elenco). Il campione si restringe per il criterio, che le regole fissano.
* Il motivo più grande della perdita fra «ufficiale» e «approvata» (52 → 31) è la scelta «sYES» (10 proposte): nome delle scelte degli spazi di Synthetix, che la regola 3 della Chiusura scarta («deve cominciare con Yes/For/...»: «sYES» no). Lo scrivo come fatto, senza correggerlo.

## Varianti non previste che proporrei (non eseguite)
* Nessuna sulla prova. Annoto soltanto che con la sola lettura delle scelte («sYES» come sì) il numero salirebbe di qualche unità, ma servirebbero più di 14 eventi in più per arrivare a 40: non basta.

## Domande aperte
1. Il campione (26 eventi in sei anni, 1 nel 2021 e 4 nel 2026) è fisso con queste regole: si chiude la prova come «campione troppo piccolo», oppure la sessione principale vuole nuove regole (più parole, altre fonti di voto) scritte prima di qualsiasi prezzo?
2. Il controllo sul nome dello spazio, scritto alla lettera, tiene fuori spazi ufficiali (Curve, Lido, Radiant): lo si lascia così?
3. «Parole intere» è stato letto alla lettera: «buybacks», «burns», «burned» non contano. Corretto?
4. Il controllo del giorno esatto del perpetuo (fine del voto nel mese di quotazione) non è stato fatto perché richiede i prezzi: non cambia l'esito (può solo ridurre).
