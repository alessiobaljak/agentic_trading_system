# Passo 0 della seconda edizione — rapporto del coordinamento (13 ottobre 2026, sera)

> Stato: **in corso**. Il Passo 0 finisce con uno STOP: il proprietario approva `research/config/parametri_2.yaml`
> e solo dopo si apre la sessione di campagna `PANIERE` (`research/PROTOCOLLO_2.md`, sezione 10). Questo file dice
> cosa è fatto, con i numeri e le fonti, e cosa manca.

## La tabella del Passo 0 (sezione 10 di PROTOCOLLO_2)

| Punto | Cosa | Stato | Numeri e fonte |
|---|---|---|---|
| 1 | Dati 1d delle 80 monete e di BTCUSDT (klines, mark, funding) 2020-2023, più BTCUSDT 8h | **fatto** | 245 serie, 0 errori, 0 checksum mancanti, 48 minuti (`scratchpad`, log dello scarico); 9.406 file con SHA-256 in `research/campagne/PANIERE/impronte_1d.json`; mesi presenti 3.061 klines/1d, 3.061 mark 1d, 3.044 funding su 3.061 attesi dalle schede (il funding ha 17 mesi in meno: le monete che partono nel mese del listing, come nel gruppo a 1 ora) |
| 2 | Motore a barre giornaliere: funding 1d contro 8h, distanza dello stop, costo per trade | **fatto** | `research/passo0_2/misure_motore_1d.md`: stessa strategia (A1-20) su BTCUSDT, 24 trade long e 16 short identici a 1d e a 8h; differenza di funding per trade −0,0003 R (long) e +0,0007 R (short), massima 0,016 R → **si usano le barre di 1 giorno** (sotto i 0,005 R della sezione 3.4). Stop 2,5 ATR(20): mediana 22,2% del prezzo sulle 80 monete (da 13,3% a 27,8%; BTC 11,8%). Costo atteso per trade: mediana 0,0068 R (0,0043-0,0113) |
| 3 | Serie di paniere con controllo di causalità | **fatto** | `research/src/paniere.py` (allineamento sul calendario UTC, rendimento a n giorni, classifica con parità alfabetica, giorni forti di Bitcoin con la deviazione dei 60 giorni precedenti); `test_paniere.py`, 6 test, fra cui quello che cambia il futuro e controlla che il passato non cambi |
| 4 | Strumenti di gruppo a 1d, prova a placebo a 1d, controllo positivo | **in corso** | il modulo delle regole da manuale ammette «1d» (uscita a tempo 10 barre); lanciatore `research/taratura/placebo_paniere/esegui.py` (riusa quello a 1 ora: sfasamento comune, ingressi placebo, esame, identità); copertura dei dati: 80 monete, tutte con barre 1d, funding e giorni 1d nei due periodi; **la prova (96 esami) sta girando**; esito e controllo positivo: sezione sotto |
| 5 | Caricatore e vault; guardiano della sessione PANIERE | **fatto** | il vault si riapre solo con `research/vault/APERTURA_2.md` (`APERTURA.md` dell'11 ottobre non apre più); la campagna PANIERE è una campagna di gruppo per guardiano, caricatore e strumenti (`SIMBOLI_GRUPPO`), con elenco e schede propri in sola lettura; test: 1.348 passati (`test_guardiano_paniere.py`, `test_guardiano_gruppo.py`, `test_guardiano.py`, `test_dati.py`, `test_gruppo_dati.py`) |
| 6 | `research/config/parametri_2.yaml` | **bozza scritta** | tutti i numeri del testo più quelli misurati al punto 2; stato `bozza_passo_0`; lo approva il proprietario allo STOP |
| 7 | Il bot: cosa gli manca per il Passo 9 | **deciso, non costruito** | sezione sotto |

## Il bot (punto 7): cosa serve, cosa no

Il bot esegue oggi strategie generate dal gate (combinazioni di indicatori a 15 minuti e 1 ora, registro
`strategy_registry/validated`), con l'ingresso a ordine limite dal 13 ottobre. Per il paper della seconda edizione
(sezione 9) servirebbero, SOLO se una candidata passa il vault: (1) un tipo di strategia «di paniere a barre
giornaliere» che legga le 80 monete insieme (classifica, giorno forte di Bitcoin) e decida alla chiusura del giorno
UTC; (2) lo stop a 2,5 ATR(20) giornalieri e l'uscita a tempo in giorni al posto delle 96 barre del gate; (3) il tetto
di esposizione per verso che già esiste (`MAX_DIRECTIONAL_RISK_PCT`). Non si costruisce ora: si costruisce dopo il
vault, e si prova sui dati del vault che il paper riproduca il motore (parità), come per le campagne.

## Cosa si è capito al Passo 0 (per il diario)

* **A giorni il costo d'esecuzione sparisce, il funding no.** Con lo stop a 2,5 ATR(20) il rischio di un trade vale
  un quinto del nozionale: 0,09% di commissioni e scarto fanno 0,007 R. Ma un long su Bitcoin tenuto 25 giorni nel
  2020-2023 ha pagato in media 0,23 R di funding (24 trade della misura): a questo orizzonte il funding è il costo
  che conta, e il motore lo addebita (gli short lo incassano: −0,018 R sui 16 short).
* **Lo stop giornaliero è largo**: 22% mediano sulle monete del paniere, 12% su Bitcoin. È quello che dice l'ATR a
  giorni; le posizioni escono soprattutto a segnale e a tempo, non allo stop (BTC: 8 stop su 24).
* **Il motore a barre giornaliere non ha bisogno di barre più fini**: la stessa strategia dà gli stessi trade a 1d e
  a 8h, con il funding a meno di un millesimo di R.

## La prova a placebo a 1d e il controllo positivo

_(da scrivere a prova finita: placebo valutabili per periodo, «nette» in costruzione, p sotto 0,10 in validazione,
distribuzione dei t; poi il controllo positivo long e short con il modulo delle regole da manuale.)_

## Lo STOP

Quando la sezione sopra è scritta, il coordinamento manda al proprietario: la tabella, i numeri misurati, l'esito
della prova a placebo e la richiesta di approvare `parametri_2.yaml`. Nessuna sessione di campagna si apre prima.
