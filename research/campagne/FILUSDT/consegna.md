# Consegna della campagna FILUSDT (protocollo 4.5)

**Esito: nessuna strategia valida trovata per questa moneta.**

L'unico candidato sopravvissuto alla Fase 4, FILUSDT-025, ha **fallito in validazione**. Nel 2023
fa un R medio dopo i costi di −0,117 su 87 trade. Il p-value contro la (b) sarebbe 0,0854, sotto
l'asticella con un solo candidato. La decisione di riportarlo come fallito è dell'utente, data il
2026-10-09 alle 17:52 UTC («fallito», nota FILUSDT-N027 del log). Il motivo è il principio della
sezione 8: «battere il caso perdendo meno di lui non è un vantaggio». Nessun candidato va al vault.

Periodi: costruzione dal 2020-10-01 al 2023-01-08, con i primi dati dal 2020-10-16. Validazione
dal 2023-01-09 al 2023-12-31. Dati e impronte sono in `fase0_dati.md`.

## Riepilogo delle idee provate

16 idee, tutte con fonte pubblicata prima del 2024, in 12 famiglie di meccanismi. 22 varianti di
idee nuove e 8 ritocchi, per 30 varianti su 30. Altri 9 scarti erano sotto i 70 trade e non hanno
consumato budget. Il dettaglio è in `ipotesi.md` e `lezioni_moneta.md`.

| Idea (fonte) | Varianti | Esito |
|---|---|---|
| I-01 momento settimanale (Moskowitz-Ooi-Pedersen 2012; Liu-Tsyvinski 2018) | 001, 002 | non netto |
| I-02 rottura del canale (Brock-Lakonishok-LeBaron 1992; Faith 2007) | 4 scarti | sotto i 70 trade |
| I-03 inversione dopo 24 ore estreme (Lehmann 1990; Jegadeesh 1990) | 005, 006 | non netto, R negativo |
| I-04 barre estreme con volume (Campbell-Grossman-Wang 1993) | 009, 010 | non netto, R negativo |
| I-05 RSI(2) nel trend (Connors-Alvarez 2008) | 012 (011 scarto) | non netto |
| I-06 funding (Schmeling-Schrimpf-Todorov 2023) | 013, 014 | non netto, R negativo |
| I-07 lunedì (Caporale-Plastun 2019; Aharon-Qadan 2019) | 015 | il contrario della fonte (t −1,90) |
| I-08 ritardo di FIL rispetto a BTC (Hou-Moskowitz 2005; Sifat e altri 2019) | 016, 017 | 016 candidato, scartato a costi doppi |
| I-09 compressione delle bande (Bollinger 2001) | 2 scarti | sotto i 70 trade |
| I-10 volume molto alto (Gervais-Kaniel-Mingelgrin 2001) | 1 scarto | sotto i 70 trade |
| I-11 squilibrio degli ordini (Chordia-Subrahmanyam 2004) | 021, 022 | non netto, R negativo |
| I-12 stagionalità della fascia oraria (Heston-Korajczyk-Sadka 2010) | 023, 024 | 024 candidato, scartato (costi doppi, ritardo) |
| I-13 rottura di volatilità (Williams 1999; Crabel 1990) | 025, 026 | 025 candidato, fallito in validazione |
| I-14 shock di illiquidità (Amihud 2002) | 1 scarto | sotto i 70 trade |
| I-15 momento dentro il giorno (Gao-Han-Li-Zhou 2018; Shen-Urquhart-Wang 2022) | 028, 029 + 8 ritocchi | 7 ritocchi candidati, tutti scartati per il ritardo |
| I-16 incrocio con la media (Gerritsen e altri 2020) | 030, 031 | non netto (vale l'uscita, non l'ingresso) |

## Il candidato che è arrivato in validazione: FILUSDT-025 (fallito)

**Regole complete** (in `candidati/FILUSDT-025/regole.md`, congelate al commit `a414d1e`):

- moneta FILUSDT, segnali su candele da 1 ora, direzione long;
- ingresso: nelle ore 00-22 UTC, alla prima barra del giorno in cui il close supera l'apertura del
  giorno UTC di più di 0,6 volte l'escursione del giorno precedente; si entra all'apertura della
  barra dopo;
- stop all'apertura del giorno, nessun target, uscita a fine giorno UTC;
- rischio 1% a trade, leva fra 1 e 2, margine isolato; nessun trade ridotto per il tetto di leva.

**Motivo economico.** Un movimento ampio dall'apertura, rispetto alla volatilità recente, segnala
un flusso direzionale che continua nella giornata.

| | Costruzione | Validazione |
|---|---|---|
| Trade | 177 | 87 |
| R medio dopo i costi | +0,084 | −0,117 |
| R medio senza i 3 migliori | +0,009 | −0,218 |
| Profit factor | 1,22 | 0,69 |
| Rendimento | +14,9% | −11,6% |
| Drawdown massimo | 13,3% | 19,9% |
| Rendimento per anno | 2020 −0,27 R (16 trade), 2021 +0,17 R (93), 2022 +0,03 R (65) | 2023 −0,117 R (87) |
| (a): media, t | −0,668, t 2,11 (netto) | −0,873, t 2,49 (p 0,0083) |
| (b): media, t | −0,309, t 2,34 (netto) | −0,392, t 1,39 (p 0,0854) |
| Buy and hold long | 2021 +40%, 2022 −91% | circa +100% |

**Verifiche della Fase 4.** Tutte superate: robustezza, timeframe adiacenti, stabilità per anno,
trade estremi, ritardo (t 1,40), costi doppi (R +0,035), liquidazione (0 violazioni). La regola
intra-barra opposta dà un risultato identico.

**Rischi noti, emersi in Fase 5 e confermati in validazione.**

- Le baseline con lo stop all'apertura del giorno sono gonfiate dai costi: entrano spesso con lo
  stop vicinissimo all'ingresso.
- Contro ingressi casuali con uno stop di distanza normale, in costruzione il t è solo 1,38 (prova
  S1).
- Il guadagno di costruzione sta nei giorni in cui sale tutto il mercato (prova S2).
- Il 29% dei trade ha uno stop oltre il 6%, il tetto del bot.

**Asticella.** Benjamini-Hochberg al 10% con m = 1 e p = 0,0854: alla lettera l'esito sarebbe
«passa». Per decisione dell'utente il candidato è fallito. L'esito resta provvisorio fino al
Passo 4.

Per il criterio del vault, i trade attesi in paper e l'eseguibilità nel bot non c'è nulla da
scrivere: nessun candidato va avanti. Per la stessa ragione la previsione per il vault e il
trasferimento non si applica.

## Altri candidati della Fase 2, scartati in Fase 4

| Candidato | Motivo dello scarto |
|---|---|
| FILUSDT-016 | costi doppi (R −0,004); il resto superato |
| FILUSDT-024 | costi doppi (R −0,009) e ritardo (t −0,31) |
| FILUSDT-032, 033, 034, 035, 036, 038, 039 | ritardo di una barra (t fra 0,16 e 1,10). Le regole sono legate alla fascia 20-24 UTC e col ritardo cadono nella fascia dopo; nessun lookahead trovato |

## Misure di processo

Le misure vengono da `codice/misure.py`, sul log e su `ipotesi.md`.

| Misura | Valore |
|---|---|
| Prima e ultima voce del log | 2026-10-09 15:26:24 → 17:52:18 UTC |
| Durata con le pause | 145,9 minuti |
| Durata senza le pause | 53,4 minuti (una pausa di 92,5 minuti per la domanda sulla validazione) |
| Varianti testate | 30, di cui 8 ritocchi |
| Famiglie | 22 |
| Scarti (sotto i 70 trade) | 9 |
| Spiegazioni concorrenti scritte | 11 per ognuna delle 16 idee |
| Candidati della Fase 2 da idee nuove | 3 (016, 024, 025) |
| Candidati della Fase 2 da ritocchi | 7 (032, 033, 034, 035, 036, 038, 039) |
| Varianti nette contro (a) e (b) con R medio non positivo | 0 |

Minuti per idea, dalla registrazione della prima variante all'ultimo risultato: I-01 1,4; I-03
1,4; I-04, I-05, I-06, I-07, I-08, I-11, I-12, I-13 1,8 ciascuna; I-15 13,4 (con 8 ritocchi);
I-16 0,4. I test sono veloci, da 2 a 30 secondi l'uno. Queste durate non contano il tempo della
Fase 1 (la scrittura in `ipotesi.md`) né quello della Fase 4. Le idee arrivate al solo scarto non
hanno durata.

## Note

- Il guardiano ha rifiutato 7 comandi, tutti per la loro forma. Nessuno è stato aggirato e sono
  registrati nel log (FILUSDT-N002, N003, N005, N025).
- Due commit hanno il titolo del commit precedente (FILUSDT-N023). Nessun contenuto è andato perso.
- Non è stata fatta nessuna correzione a `src/`.
- Le lezioni di metodo proposte sono in `lezioni_metodo_proposte.md`. Riguardano le baseline con lo
  stop a un livello di prezzo, il test del ritardo sulle regole legate all'ora del giorno e la
  validazione senza la richiesta di un R medio positivo.
