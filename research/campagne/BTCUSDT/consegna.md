# Consegna della campagna BTCUSDT (prova di processo, Passo 2)

**Esito: nessuna strategia valida trovata per questa moneta.**

Sessione di campagna aperta il 2026-10-07; una sola sessione di lavoro (circa 2 ore e mezza di
orologio, dalla Fase 0 alla consegna). Protocollo versione 4.3, parametri congelati di
`research/config/parametri.yaml`. Branch `research/campagna/BTCUSDT`. Il log completo e' in
`log.jsonl` (ogni test registrato prima di eseguirlo, con previsione); le ipotesi in `ipotesi.md`;
i dati in `fase0_dati.md`; il codice in `codice/`; gli esiti completi in `codice/risultati/`.

Nessun candidato e' arrivato alla validazione: il periodo di validazione (2022-10-20 → 2023-12-31)
**non e' stato toccato** da nessun test. Nessun candidato va al vault. Non c'e' un `candidati/`.

## Cosa e' stato fatto

| Voce | Valore |
|---|---|
| Dati | BTCUSDT, 2020-01-01 → 2023-12-31, 192 file mensili con checksum verificato (impronte in `fase0_dati.md`) |
| Costruzione | 2020-01-01 → 2022-10-19 (1.023 giorni) |
| Validazione | 2022-10-20 → 2023-12-31 (438 giorni), mai usata |
| Idee scritte | 13 (I-01 … I-13), piu' 3 scartate senza fonte o fuori regola (S-01 … S-03) |
| Varianti usate | 16 su 30 |
| Scarti per stima dei trade | 11 (nessun budget) |
| Verifiche | 12, tutte su V08 (Fase 5, per smontare il risultato piu' vicino) |
| Candidati sopravvissuti alla Fase 2 | 0 |
| Candidati validati | 0 |

Costi usati in ogni test: commissione 0,05% per lato, slippage 0,01% per lato, funding storico
vero (8 ore), rischio 1% per trade, leva massima 2, margine isolato, stop prima del target.
Nessun trade ridotto per il tetto di leva, nessuna violazione del margine dalla liquidazione in
nessuna variante (con leva 2 la liquidazione dista circa il 47%).

## Criterio applicato per andare avanti (Fase 2)

Un'idea andava avanti solo se, in costruzione: almeno 100 trade; R medio positivo dopo i costi;
R medio sopra il 90° percentile delle entrate casuali con la stessa uscita e direzione (100
simulazioni, 50 a 30 minuti); differenza «netta» (oltre 2 errori standard, bootstrap a blocchi)
sia dalla simulazione casuale mediana sia dalla baseline incondizionata (stessa uscita su ogni
barra). Nessuna variante ha soddisfatto tutte le condizioni.

## Risultati per idea (osservato in costruzione)

* **I-01 Rottura del canale (4h, Gerritsen et al. 2020).** Long: 72 trade (sotto il minimo: non si
  sa), PF 1,51 ma trade mediano uno stop pieno, tutto nel 2020. Short: scartato dalla stima.
* **I-02 / I-02b Momentum di serie temporale (1d, Moskowitz et al. 2012; Liu & Tsyvinski 2021).**
  A 7 giorni scartato dalla stima; a 5 giorni: long R medio −0,005 (14° percentile del caso:
  peggio dell'entrata casuale long), short +0,005. Il segno del rendimento a 5 giorni non predice il
  successivo su BTCUSDT 2020-2022.
* **I-03 Momentum intragiornaliero (30m, Shen et al. 2022).** Long PF 0,37, short PF 0,62; anche
  senza condizione, nell'ultima mezz'ora UTC perdono sia i long (−0,12 R) sia gli short (−0,07 R):
  il movimento e' piu' piccolo dei costi.
* **I-04 / I-04b Funding estremo (8h, Schmeling et al. 2023; He et al. 2022).** Il risultato piu'
  vicino della campagna: funding nel decile piu' basso → long 24 ore: 122 trade, PF 1,54, R medio
  0,08, positivo in tutti e tre gli anni, 96° percentile del caso, **ma non netto** (differenza 0,09 R
  con margine 0,13). La Fase 3 ha mostrato che il funding incassato non conta (0,4% del risultato)
  e che la media dipende dai 5 trade migliori (senza: 0,02). La generalizzazione a «funding < 0»
  (V12) e' piu' debole (R 0,03, 82° percentile). Lo short sul funding alto (V13) perde. Le verifiche
  della Fase 5 su V08: con un ritardo di 8 ore l'R medio scende a 0,02; a 12 ore sparisce (0,004);
  l'effetto cresce con l'estremita' della soglia (85°/90°/95°: 0,03/0,08/0,18 R, ma al 95° solo 85
  trade); in nessuna configurazione la media regge senza i 5 trade migliori; mai netta.
* **I-05 Lunedi' (1d, Aharon & Qadan 2019).** 144 trade, R medio 0,02, 85° percentile, non netto.
* **I-06 Giorno anomalo (1d, Caporale & Plastun 2019).** Scartato dalla stima (71 e 58 trade).
* **I-07 Intervallo di apertura (1h, Crabel 1990).** Long: 490 trade, PF 1,09, R medio 0,12, ma
  54% di stop, R mediano −1,04, drawdown 47%, tutto nel 2020 (+0,57; poi −0,09 e −0,20); al 100°
  percentile del caso ma non netto sulla simulazione mediana. Short: R −0,10.
* **I-08 Ritracciamento RSI(2) nel trend (4h, Connors & Alvarez 2009).** Long PF 0,79, short 0,98:
  win rate alto, ma gli stop a −1 R cancellano tutto.
* **I-09 Premio del volume (1d, Gervais et al. 2001).** Scartato dalla stima (68).
* **I-10 Compressione delle bande (4h, Bollinger 2001).** Scartato dalla stima (21 e 17).
* **I-11 Regime di bassa volatilita' (1d, Moreira & Muir 2017).** 129 trade, R medio −0,003, 31°
  percentile.
* **I-12 Contrazione NR7 (1h, Crabel 1990).** Scartato dalla stima (68 e 62).
* **I-13 Ritorno alla media dalle bande (4h, Bollinger 2001; Lento et al. 2007).** Long R −0,22
  (nettamente peggio del caso), short R −0,12: comprare sotto la banda bassa a 4 ore e' comprare
  dentro i crolli.

Confronto con il buy and hold (baseline c) in costruzione: +166% long, −166% short (costi
inclusi, leva 1). Nessuna variante long si avvicina al buy and hold in rendimento totale; non e' il
criterio (il criterio e' l'R per unita' di rischio contro il caso), ma va detto.

## Previsioni dichiarate prima dei test

Su 16 varianti il profit factor e' caduto nell'intervallo previsto 3 volte (V09, V17, V23). Le
previsioni hanno sbagliato in peggio 10 volte e in meglio 3 (V01, V08, V14). Le previsioni erano
gia' pessimiste e la realta' lo e' stata di piu': l'errore sistematico e' stato sottostimare quanto i costi e gli stop pesano sui timeframe
corti e quanto un singolo anno (2020) domina i risultati positivi.

## Rischi noti e limiti

* Un solo periodo di costruzione di 2,8 anni con un rialzo enorme (2020-21) e un ribasso (2022):
  qualunque long «funziona» nel 2020 e qualunque short nel 2022; il confronto per anno e con le
  entrate casuali della stessa direzione e' stato decisivo per non farsi ingannare.
* Le baseline casuali usano 100 simulazioni (50 a 30 minuti): i percentili hanno un passo dell'1-2%.
* Gli stop a 2 ATR su candele giornaliere valgono il 10-12% del prezzo: nel bot il tetto e' il 6%,
  quindi nessuna variante giornaliera cosi' com'e' sarebbe eseguibile dal bot; a 8 ore lo stop e'
  in media il 7% (meta' dei trade oltre il 6%); a 4 ore e sotto rientra.
* Le barre mark mancanti (770 a 15 minuti) sono state riempite con il last: ininfluente qui, nessuna
  liquidazione e' mai scattata.
* Il bot oggi non puo' eseguire una strategia del protocollo senza un'aggiunta (decisione 4 del
  Passo 0): irrilevante per questa consegna, che non ha candidati.
* Vault non cieco: le idee vengono da fonti precedenti al 2024, ma la scelta del funding come
  famiglia e' influenzata anche dal senso comune del settore.

## Tabelle complete

### Varianti testate (periodo di costruzione, 2020-01-01 → 2022-10-19)

| n | Variante | Idea | TF | Dir. | Trade | PF | R medio | R mediano | R medio per anno (2020/2021/2022) | Percentile sul caso | Netta vs caso | Netta vs incondizionata | Previsione PF | PF nell'intervallo | Esito |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | BTCUSDT-V05-long | I-03 | 30m | long | 527 | 0,37 | -0,114 | -0,126 | -0,12/-0,11/-0,11 | 8 | no | no | 0,85–1,00 | no | non va avanti |
| 2 | BTCUSDT-V01-long | I-01 | 4h | long | 72 | 1,51 | 0,386 | -1,024 | 0,99/0,10/-0,20 | 77 | no | no | 0,95–1,20 | no | sotto 100 trade: non si sa |
| 3 | BTCUSDT-V09-long | I-05 | 1d | long | 144 | 1,14 | 0,021 | 0,023 | 0,11/-0,07/0,02 | 85 | no | no | 0,90–1,20 | sì | non va avanti |
| 4 | BTCUSDT-V08-long | I-04 | 8h | long | 122 | 1,54 | 0,081 | 0,060 | 0,11/0,12/0,05 | 96 | no | no | 0,90–1,10 | no | non va avanti |
| 5 | BTCUSDT-V06-short | I-03 | 30m | short | 496 | 0,62 | -0,054 | -0,073 | -0,08/-0,07/-0,02 | 100 | sì | no | 0,85–1,00 | no | non va avanti |
| 6 | BTCUSDT-V12-long | I-04b | 8h | long | 185 | 1,18 | 0,031 | 0,041 | 0,04/0,05/0,02 | 82 | no | no | 1,20–1,60 | no | non va avanti |
| 7 | BTCUSDT-V13-short | I-04 | 8h | short | 111 | 0,88 | -0,026 | -0,006 | -0,02/-0,03/— | 53 | no | no | 0,90–1,10 | no | non va avanti |
| 8 | BTCUSDT-V16-long | I-08 | 4h | long | 129 | 0,79 | -0,052 | 0,107 | -0,04/-0,02/-0,13 | 33 | no | no | 1,00–1,30 | no | non va avanti |
| 9 | BTCUSDT-V17-short | I-08 | 4h | short | 126 | 0,98 | -0,002 | 0,139 | -0,09/0,05/0,01 | 79 | no | no | 0,80–1,00 | sì | non va avanti |
| 10 | BTCUSDT-V14-long | I-07 | 1h | long | 490 | 1,09 | 0,118 | -1,042 | 0,57/-0,09/-0,20 | 100 | no | sì | 0,85–1,05 | no | non va avanti |
| 11 | BTCUSDT-V15-short | I-07 | 1h | short | 524 | 0,84 | -0,096 | -1,035 | -0,11/-0,06/-0,12 | 67 | no | no | 0,85–1,05 | no | non va avanti |
| 12 | BTCUSDT-V21-long | I-11 | 1d | long | 129 | 0,98 | -0,003 | -0,009 | 0,08/0,02/-0,09 | 31 | no | no | 1,00–1,30 | no | non va avanti |
| 13 | BTCUSDT-V22-long | I-02b | 1d | long | 131 | 0,98 | -0,005 | -0,049 | 0,15/-0,02/-0,19 | 14 | no | no | 1,00–1,25 | no | non va avanti |
| 14 | BTCUSDT-V23-short | I-02b | 1d | short | 115 | 1,01 | 0,005 | -0,076 | -0,05/-0,07/0,13 | 77 | no | no | 0,85–1,05 | sì | non va avanti |
| 15 | BTCUSDT-V26-long | I-13 | 4h | long | 163 | 0,53 | -0,218 | -0,188 | -0,31/-0,06/-0,32 | 0 | sì | no | 0,85–1,05 | no | non va avanti |
| 16 | BTCUSDT-V27-short | I-13 | 4h | short | 194 | 0,71 | -0,123 | -0,270 | -0,24/-0,06/0,08 | 1 | no | no | 0,85–1,05 | no | non va avanti |

### Scarti per stima dei trade (nessun budget consumato)

| Variante | Idea | TF | Dir. | Segnali grezzi | Trade stimati | Occupazione (barre) |
|---|---|---|---|---|---|---|
| BTCUSDT-V02-short | I-01 | 4h | short | 153 | 76 | 15 |
| BTCUSDT-V03-long | I-02 | 1d | long | 541 | 97 | 7 |
| BTCUSDT-V04-short | I-02 | 1d | short | 475 | 84 | 7 |
| BTCUSDT-V07-short | I-04 | 8h | short | 230 | 90 | 3 |
| BTCUSDT-V10-long | I-06 | 1d | long | 77 | 71 | 1 |
| BTCUSDT-V11-short | I-06 | 1d | short | 62 | 58 | 1 |
| BTCUSDT-V18-long | I-09 | 1d | long | 144 | 68 | 5 |
| BTCUSDT-V19-long | I-10 | 4h | long | 21 | 21 | 20 |
| BTCUSDT-V20-short | I-10 | 4h | short | 17 | 17 | 20 |
| BTCUSDT-V24-long | I-12 | 1h | long | 68 | 68 | 12 |
| BTCUSDT-V25-short | I-12 | 1h | short | 62 | 62 | 12 |

### Verifiche eseguite (costruzione)

| Verifica di | Verifica | TF | Trade | PF | R medio | R mediano | R medio per anno | Senza i 5 migliori | Percentile sul caso | Netta |
|---|---|---|---|---|---|---|---|---|---|---|
| BTCUSDT-V08-long | ritardo di 1 barra | 8h | 112 | 1,08 | 0,017 | -0,008 | 0,22/0,10/-0,10 | -0,065 | 68 | no |
| BTCUSDT-V08-long | costi doppi | 8h | 122 | 1,37 | 0,059 | 0,026 | 0,08/0,10/0,03 | -0,002 | 98 | no |
| BTCUSDT-V08-long | regola intra-barra opposta (target prima) | 8h | 122 | 1,54 | 0,081 | 0,060 | 0,11/0,12/0,05 | 0,020 | — | no |
| BTCUSDT-V08-long | robustezza: stop 1,5 ATR | 8h | 124 | 1,55 | 0,111 | 0,080 | 0,15/0,18/0,06 | 0,031 | 98 | no |
| BTCUSDT-V08-long | robustezza: stop 3 ATR | 8h | 120 | 1,56 | 0,056 | 0,065 | 0,07/0,08/0,04 | 0,015 | 98 | no |
| BTCUSDT-V08-long | robustezza: uscita a 2 barre (16 ore) | 8h | 146 | 1,38 | 0,056 | 0,055 | 0,08/0,10/0,02 | 0,007 | 96 | no |
| BTCUSDT-V08-long | robustezza: uscita a 4 barre (32 ore) | 8h | 111 | 1,70 | 0,129 | 0,055 | 0,29/0,16/0,05 | 0,044 | 98 | no |
| BTCUSDT-V08-long | robustezza: uscita a 6 barre (48 ore) | 8h | 91 | 1,60 | 0,136 | 0,055 | 0,29/0,16/0,07 | 0,038 | 90 | no |
| BTCUSDT-V08-long | robustezza: percentile 85 (soglia piu' larga) | 8h | 155 | 1,14 | 0,032 | 0,012 | 0,10/0,05/-0,01 | -0,025 | 76 | no |
| BTCUSDT-V08-long | robustezza: percentile 95 (soglia piu' stretta) | 8h | 85 | 2,50 | 0,182 | 0,109 | 0,25/0,22/0,14 | 0,087 | 100 | no |
| BTCUSDT-V08-long | adiacente: timeframe 4h, stessa regola (270 settlement = 540 barre), uscita a 6 barre (24 ore) | 4h | 144 | 1,19 | 0,053 | 0,099 | 0,11/0,02/0,04 | -0,025 | 80 | no |
| BTCUSDT-V08-long | adiacente: timeframe 12h, stessa regola (270 settlement = 180 barre), uscita a 2 barre (24 ore) | 12h | 102 | 1,02 | 0,004 | -0,020 | -0,01/0,08/-0,03 | -0,057 | 54 | no |

Budget: 16 varianti registrate su 30; 11 scarti per stima; 12 verifiche.
