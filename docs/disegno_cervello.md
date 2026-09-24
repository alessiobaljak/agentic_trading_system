# Il cervello — disegno (24 set 2026)

Richiesta del proprietario: «il sistema deve imparare da tutti i trade: leva,
rischio, take profit, stop, segnali; tutto deve convergere in un cervello che
impara e migliora l'esecuzione». Questo documento è il disegno, prima del codice,
dei due pezzi che mancano rispetto a come lavorano i sistemi quantitativi seri:

* **Punto 2 — il selettore**: un secondo modello che, davanti a un segnale, dice
  «prendilo / non prenderlo, e con quanta size», addestrato sulle migliaia di
  trade che i backtest del gate producono già.
* **Punto 1 — la ritaratura periodica**: le soglie d'ingresso di una strategia
  validata vengono riprovate a intervalli fissi sulla storia recente, invece di
  restare congelate alla nascita.

Regola che vale per entrambi: **il paper propone e verifica, la storia decide.**
Nessuno dei due impara dai 40 trade del paper.

---

## Punto 2 — Il selettore (in gergo: meta-labeling)

### Cosa impara

Per ogni segnale che una strategia validata produce — coin, strategia, direzione,
momento — la **probabilità che il trade chiuda in utile netto** (`p`). Con `p` il
bot decide due cose che oggi non decide: se aprire, e con quanta size.

Oggi il bot apre *tutti* i segnali validi, uno per coin (`decide_all` in
`bot/orchestrator/orchestrator.py`), e la confidenza dei segnali generati è fissa
a 60: la calibrazione la giudica «flat» (log del bot, 23 set). Il selettore è ciò
che dà a quel numero un significato.

### Da quali dati

Dai trade simulati del gate. Ogni valutazione produce `SimTrade`
(`backtesting/engine.py`): strategia, coin, direzione, regime, esito, pnl, mfe_r,
barre tenute, ora, istante d'ingresso. **Manca ciò che c'era sul grafico al
momento dell'ingresso**: oggi non viene salvato (riga 816, dove nasce il trade).
Il passo 0 è aggiungerlo, e le colonne esistono già nel frame degli indicatori
(`bot/core/indicators.py`): rsi, adx, atr, bande, medie, macd, stocastico, volume,
vwap.

Le variabili del selettore, poche e fisse (per non imparare il rumore):

| variabile | da dove |
|---|---|
| rsi, adx, stocastico | frame all'ingresso |
| volatilità: atr / close | frame |
| distanza dalla media lenta: close / ema_slow − 1 | frame |
| posizione nelle bande: (close − bb_lower) / (bb_upper − bb_lower) | frame |
| volume / volume_sma | frame |
| larghezza dello stop in % e primo gradino in R | geometria del trade (`setup_check`) |
| direzione, regime, ora del giorno | già in `SimTrade` |
| mercato: BTC sopra/sotto la sua media a 1h | contesto di mercato già caricato dal gate |
| famiglia della strategia (le feature della spec) | spec |

Nessuna variabile «identità della coin»: il selettore deve imparare *condizioni*,
non *nomi*.

Quanti trade: ogni coppia validata porta decine o centinaia di trade OOS dal 2022;
con 59 coppie sono migliaia. **Stima, da misurare al passo 0.**

### Come si addestra

Un modello semplice e leggibile: **regressione logistica con regolarizzazione**
(coefficienti che si possono stampare e spiegare). Se non basta, un gradient
boosting piccolo — ma solo se batte la logistica fuori campione. Pesi di recenza
sui trade (`entry_ts` c'è già). Libreria: numpy/scipy, nessuna dipendenza nuova (implementato così il 24 set).

Un modello per famiglia di strategie (mean-reversion, momentum, breakout), non uno
per strategia: per strategia i trade sono troppo pochi.

### Come si valida senza barare

Come il gate: **walk-forward nel tempo**. Si addestra sui trade fino a una data
T, si applica ai trade dopo T; mai lo stesso periodo da tutte e due le parti.
(Implementazione del 24 set: 40% iniziale di train, poi tre fette di test
consecutive sul conteggio dei trade; verdetto per permutazione dal 24 sera.)

Il metro è uno solo: **rendimento e drawdown di «apri solo se p ≥ soglia, size
secondo p» contro «apri tutto»**, sulle stesse finestre. La soglia si sceglie sul
train e si giudica sul test. Il selettore entra solo se batte «apri tutto» con
margine su almeno 2 finestre su 3 e sull'holdout. Altrimenti resta spento e il
bot fa come oggi (fail-open).

Questo confronto non richiede nuovi backtest: si rigiocano i trade già simulati.
Costo: secondi.

### Come agisce nel bot

In `decide_all`, prima della soglia di decisione:

* `p` sotto la soglia validata → il segnale non si apre;
* sopra → `size_mult` fra 0,5 e 1,25 in funzione di `p`, dentro i cap del risk
  manager (che può solo ridurre).

Il gate e il bot usano **la stessa funzione**: parità, come per tutto il resto. Il
modello viaggia su Firestore (`selector/current`: coefficienti, soglia, data,
finestre su cui è stato validato); il bot lo ricarica al refresh dei pesi.

### Riaddestramento e ruolo del paper

Si riaddestra nel giro completo notturno, ogni giorno, sui trade del gate. Il paper
non entra nel training: serve a **verificare che `p` predica davvero** — la stessa
calibrazione che oggi misura la confidenza (`bot/learning/calibration.py`). Se sul
paper la relazione fra `p` e l'esito è «flat», l'influenza del selettore si
restringe verso il neutro, come già succede per la confidenza.

### Rischi, e come si contengono

| rischio | contenimento |
|---|---|
| pochi trade per famiglia → sovradattamento | poche variabili fisse, regolarizzazione, minimo 500 trade per famiglia, altrimenti «apri tutto» |
| perdita di informazione nel tempo (leakage) | walk-forward obbligatorio, mai train e test sullo stesso periodo |
| impara la coin invece delle condizioni | nessuna variabile di identità |
| il modello invecchia | riaddestramento giornaliero, calibrazione sul paper come freno |
| toglie troppi trade | il metro include il rendimento assoluto, non solo il win rate: un selettore che apre un trade al mese perde il confronto |

### Passi e go/no-go

| passo | cosa | metro | tempo |
|---|---|---|---|
| 0 | salvare le variabili all'ingresso in `SimTrade` e scrivere il dataset di ogni giro (file sulla VPS, un riepilogo su Firestore) | quanti trade, quante famiglie con ≥ 500 | 1 giorno |
| 1 | training e confronto offline: report `selettore` (allowlist) con «apri tutto» vs «selettore» per finestra e holdout | batte «apri tutto» su ≥ 2/3 finestre e holdout | 2-3 giorni |
| 2 | ombra nel bot: il selettore scrive cosa avrebbe fatto e la sua `p`, non agisce | calibrazione sul paper non «flat» dopo 40 segnali | 1 settimana di misura |
| 3 | attivazione: soglia e size dal selettore, con interruttore (`SELECTOR_ENABLED`) | il controllo del mattino confronta PnL con e senza | — |

Il passo 0 e 1 non toccano il bot. Il passo 3 non parte senza il sì.

---

## Punto 1 — La ritaratura periodica (B8, seconda metà)

### Cosa

Le strategie generate hanno le soglie congelate alla nascita (`params` vuoto nel
registro; backlog B8). Qui, per ogni strategia validata (o in `watch`/`drift`), si
prova l'**intorno**: ogni parametro numerico spostato di un gradino in su e uno in
giù, sulle liste del generatore (`bot/strategies/generator.py`: RSI low/high e
mid, stocastico, adx_lo/adx_hi, vol_pct, stretch_max, htf_gap, rs_gap,
atr_mult_stop, volume_mult, min_adx). Le feature non cambiano: quello lo fa già la
mutazione. Sono 2 figlie per parametro, in media 6-12 per strategia.

### Quando

Solo nel giro completo (02:00), non in tutti i giri. Ogni strategia va nell'intorno
al massimo una volta ogni 7 giorni, prima le coppie in `watch`/`drift`, poi le
validate a rotazione. **Tetto per notte: 40 coppie**, così il costo è noto prima.

### Come si giudica

Stessa pipeline del gate: walk-forward, holdout, e le **conferme retroattive** a 8
e 16 giorni già usate per le varianti dai referti (`conferme_retroattive`). La
figlia **sostituisce** il genitore nel registro solo se:

1. passa il gate come qualunque candidata;
2. batte il genitore su (rendimento OOS − drawdown) con margine ≥ 10%;
3. passa l'holdout.

Il genitore non si butta via: resta nel registro e esce con le regole di sempre
(deriva, purga). La figlia porta `genitore` e `ipotesi = "intorno:<parametro>"`,
così la vita del registro dice quanto la ritaratura ha reso.

Una strategia cambia soglie al massimo una volta ogni 14 giorni: senza questo
freno l'intorno insegue il rumore settimana per settimana.

### Costo

Ogni figlia costa una valutazione di coppia (spec × coin), più due retroattive se
passa. Con 40 coppie a notte e ~8 figlie l'una sono ~320 valutazioni più le
retroattive: **da misurare** contro il giro completo di 2h29 (cronometro in
`gate`). Si attiva solo con il giro completo sotto 1h30, come già scritto in
backlog per B8; fino ad allora il tetto scende a 10 coppie a notte.

### Rischi

| rischio | contenimento |
|---|---|
| scegliere la migliore fra 8 è di nuovo una piccola lotteria | holdout, conferme retroattive, margine del 10% sul genitore |
| soglie che cambiano ogni settimana | una sostituzione al massimo ogni 14 giorni per strategia |
| il giro sfora le 3 ore | tetto per notte, misurato prima di alzarlo |

### Cosa NON è

Non tocca il paper e non usa i suoi trade. Non cambia il vocabolario delle
strategie. Non abbassa nessuna soglia del gate.

---

## Ordine consigliato

1. Punto 2, passi 0 e 1: dataset e confronto offline. Nessun effetto sul bot.
2. Punto 1 con tetto a 10 coppie a notte, per misurare il costo.
3. Punto 2, passi 2 e 3, dopo il verdetto del passo 1.
