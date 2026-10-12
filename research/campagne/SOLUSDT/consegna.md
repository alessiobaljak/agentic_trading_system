# SOLUSDT — Consegna della campagna (protocollo 4.4)

**Nessuna strategia valida trovata per questa moneta.**

Tutti i numeri vengono dal log (`log.jsonl`): per le varianti vale l'ultima voce `risultato` o
`correzione` di ogni id (le 22 correzioni del 2026-10-08 rifanno i risultati dopo la correzione del
caricatore del funding, voci N015–N019). Periodo giudicato: solo costruzione (2020-09-01 → 2022-12-30,
in pratica novembre 2020 e gennaio 2021 → dicembre 2022). La validazione (2022-12-31 → 2023-12-31) non è
stata usata: nessun candidato è arrivato fin lì.

## In breve

| | |
|---|---|
| Varianti testate (budget) | 30 su 30, nessun avanzo |
| di cui idee nuove / ritocchi | 22 / 8 |
| Idee con fonte | 13, in 8 famiglie di meccanismi |
| Famiglie di varianti con ritocchi | 2 (015 e 012), entrambe al massimo di 5 |
| Scarti per trade sotto 70 (senza budget) | 9: 004, 005, 006, 007, 010, 017, 020, 029, 031 |
| Candidati in costruzione | 4 (023, 024, 026, 027, tutti della famiglia di 015) |
| Candidati dopo la Fase 4 | 0 |
| Candidati in validazione / asticella | 0 / m = 0 |
| Esito | nessuna strategia valida |

## Le idee provate (costruzione, dopo i costi)

R medio = guadagno medio per trade in unità di rischio; t = distanza dalla baseline in errori standard;
«netta» = sopra la soglia di Student (circa 2). (a) = la stessa uscita entrando a ogni barra libera;
(b) = 200 strategie a ingressi casuali con la stessa uscita.

| Id | Idea (fonte) | tf, direzione | Trade | R medio | t (a) | t (b) | Esito |
|---|---|---|---|---|---|---|---|
| 001 | momentum di 7 giorni (Moskowitz et al. 2012; Liu e Tsyvinski 2018) | 1d long | 71 | +0,187 | 0,33 | 0,56 | no: la (b) long fa +0,108 |
| 002 | idem | 1d short | 71 | −0,046 | 0,57 | 0,48 | no |
| 003 | rottura di 20 barre (Covel 2007) | 4h long | 70 | +0,329 | 0,75 | 0,84 | no: la (b) long fa +0,069; senza i 3 migliori +0,03 |
| 004b | idem | 2h short | 130 | +0,050 | 0,84 | 0,28 | no |
| 005b | incrocio sopra la SMA50 (Brock et al. 1992) | 2h long | 81 | +0,343 | 0,37 | 0,30 | no: la (b) long fa +0,262 |
| 006b | RSI(2) < 10 sopra la SMA200 (Connors e Alvarez 2008) | 4h long | 89 | +0,006 | 0,44 | 0,37 | no |
| 007b | RSI(2) > 90 sotto la SMA200 | 4h short | 101 | +0,017 | 0,76 | 0,60 | no |
| 008 | inversione dopo −3 σ a 1h (Lehmann 1990; Nagel 2012) | 1h long | 127 | −0,078 | −0,43 | −0,48 | no |
| 009 | inversione dopo +3 σ | 1h short | 183 | −0,127 | −1,11 | −1,30 | no: i rialzi estremi continuano |
| 010b | cali con volume alto (Campbell et al. 1993) | 4h long | 86 | −0,079 | −0,54 | −0,83 | no |
| 011 | NR7 e rottura (Crabel 1990) | 4h long | 172 | −0,106 | 0,43 | 0,17 | no |
| 012 | idem | 4h short | 179 | +0,013 | 1,28 | 1,18 | no (madre dei ritocchi 028–032) |
| 013 | lunedì (Caporale e Plastun 2019) | 1d long | 106 | −0,001 | −0,13 | −0,08 | no |
| 014 | prima mezz'ora → ultima (Gao et al. 2018; Shen et al. 2022) | 30m long | 379 | −0,056 | −0,27 | −0,33 | no |
| 015 | idem | 30m short | 366 | −0,013 | 2,18 | 1,98 | no: batte il caso al lordo, non dopo i costi |
| 016 | funding sopra lo 0,05% (Schmeling et al. 2023) | 8h short | 79 | −0,198 | −2,11 | −2,70 | no: col funding alto SOL ha continuato a salire |
| 017b | funding sotto −0,01% | 8h long | 99 | −0,039 | −0,73 | −0,54 | no |
| 018 | BTC guida, SOL segue (Hou 2007) | 1h long | 208 | −0,006 | 0,83 | 0,74 | no |
| 019 | idem | 1h short | 144 | −0,074 | −0,63 | −0,62 | no |
| 020b | giorno di volume alto (Gervais et al. 2001) | 1d long | 78 | +0,089 | 0,58 | 0,57 | no |
| 021 | attraversamento di un numero tondo (Osler 2003) | 1h long | 493 | −0,002 | 0,75 | 1,04 | no |
| 022 | idem | 1h short | 480 | +0,000 | 1,34 | 1,14 | no |

### Ritocchi (regola 6, in ordine)

| Id | Ritocco di | Cosa cambia | Trade | R medio | t (a) | t (b) | Esito in costruzione |
|---|---|---|---|---|---|---|---|
| 023 | 015 | solo sotto la SMA200 (30m) | 193 | +0,017 | 2,80 | 2,78 | candidato |
| 024 | 015 | solo nei giorni UTC in calo | 208 | +0,003 | 2,32 | 2,28 | candidato |
| 025 | 015 | stop 3 ATR | 366 | −0,009 | 2,30 | 2,06 | no (R negativo) |
| 026 | 025 | 025 + SMA200 | 193 | +0,009 | 2,78 | 2,61 | candidato |
| 027 | 025 | 025 + giorno in calo | 208 | +0,0002 | 2,30 | 2,20 | candidato |
| 028 | 012 | solo sotto la SMA200 (4h) | 101 | +0,179 | 1,75 | 1,63 | no |
| 029 | 028 | + volatilità sotto il 4,5% | 69 | — | — | — | scarto (69 trade) |
| 030 | 028 | tenuta 12 barre | 85 | +0,243 | 1,43 | 1,81 | no |
| 031 | 030 | + barra di rottura sotto il 3% | 62 | — | — | — | scarto (62 trade) |
| 032 | 030 | NR4 al posto di NR7 | 125 | +0,268 | 1,79 | 2,32 | no (non batte la (a)) |

## I candidati e perché sono caduti (Fase 4)

Regole complete in `candidati/<ID>/regole.md`: SOLUSDT, 30m, short; ingresso alle 23:30 UTC se la prima
mezz'ora del giorno UTC ha chiuso in calo (più il filtro di ciascuno); uscita alle 00:00; stop 2 o 3 ATR(14);
rischio 1% per trade, leva 1–2, margine isolato. Motivo economico: momentum dentro la giornata (fine giornata
che segue l'inizio), con filtri scelti dallo studio dei fallimenti sui dati di costruzione.

| Candidato | Costi doppi (R medio) | Ritardo di una barra (t (b): senza → con) | Robustezza | Timeframe 15m / 1h (t (b)) | Anni sopra la (b) | Senza i 3 migliori | Liquidazione |
|---|---|---|---|---|---|---|---|
| 023 | **−0,037 fallita** | **2,78 → −0,32 fallita** | superata (6/6 positivi, 5 netti) | 2,87 / 1,89 | 2 su 2 | +0,000 > −0,046 | 0 violazioni |
| 024 | **−0,049 fallita** | **2,28 → −0,53 fallita** | superata (4/4 netti) | 2,31 / 2,98 | 2 su 2 | −0,013 > −0,046 | 0 |
| 026 | **−0,027 fallita** | **2,61 → −0,63 fallita** | superata (6/6 positivi, 5 netti) | 2,67 / 1,92 | 2 su 2 | −0,002 > −0,032 | 0 |
| 027 | **−0,035 fallita** | **2,20 → −0,71 fallita** | superata (4/4 netti) | 2,21 / 2,96 | 2 su 2 | −0,010 > −0,032 | 0 |

* Regola intra-barra opposta: nessuna differenza (nessun target). Trade ridotti dal tetto di leva: vedi
  le metriche del log (`ridotti_tetto_leva`).
* Crollo col ritardo: cercato l'errore come chiede il protocollo. Prova di causalità per troncamento: 0
  differenze su 866 barre per candidato; motore già provato dal controllo positivo. Il crollo è del
  meccanismo: la regola vale a un'ora precisa e 30 minuti dopo l'ingresso cade nella prima mezz'ora del
  giorno seguente.
* Prova dello scettico (Fase 5): la stessa regola di 023 alle 11:30 UTC ha R −0,082 e t contro la (b) −1,52.
  L'effetto lordo è legato alla fine della giornata UTC, ma è più piccolo dei costi.

Esito: nessun candidato va in validazione; p-value di validazione e asticella non esistono (m = 0).
Criterio del vault (`criterio_vault`), trade al mese in paper e previsione per vault e trasferimento: non si
applicano.

## Cosa resta utile

* Il bot oggi non potrebbe comunque eseguire una strategia a 30m (indicatori dal vivo solo a 1m, 5m, 15m, 1h).
* Il vantaggio lordo della fine giornata UTC (circa +0,04 R a trade al lordo, contro costi di circa 0,05 R)
  esiste in costruzione ed è specifico dell'ora: con costi più bassi (ordini limit, commissioni ridotte) potrebbe
  diventare un'idea. Non è stato validato e non va usato così.
* La famiglia NR7/NR4 short sotto la SMA200 (028–032) ha R medio alto (+0,18 / +0,27) ma non batte nettamente
  entrambe le baseline: con 85–125 trade l'errore è largo.

## Limiti (sezione 11)

Vault non perfettamente cieco (chi scrive sa a grandi linee com'è andata SOL dopo il 2023); campagne dello stesso
modello; mercato comune; potenza bassa con 70–500 trade; storia corta (costruzione utile di circa 2,1 anni, con il
2021 di rialzo di circa 100 volte e il 2022 di calo del 94%); slippage dello 0,01% ottimista per il 2020 e l'inizio
del 2021 (`fase0_dati.md`); il guardiano ferma le letture per sbaglio, non le scorciatoie volute.
