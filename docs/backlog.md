# Backlog — cose emerse e rimandate

Elenco delle cose **trovate e NON fatte**, con il motivo per cui sono state
rimandate e cosa servirebbe per deciderle. Non è un piano: è una memoria, perché
finora questi punti vivevano solo dentro le conversazioni e sparivano.

**Regola d'ingresso:** ci si mette una voce quando si scopre qualcosa che vale la
pena valutare ma NON si fa subito. Con: cosa, perché rimandata, e il numero
misurato che l'ha fatta emergere. Senza il numero, una voce è un'opinione.

**Regola d'uscita:** si toglie quando è fatta (e finisce in `andremo_live.md` con
la misura) oppure quando si decide di non farla — scrivendo perché. Una voce che
sparisce senza verdetto è peggio di una voce mai scritta.

**Due vincoli che valgono per quasi tutto qui sotto:**

1. **Niente cambia le uscite prima dei 40 trade chiusi.** Siamo a 15. Cambiare
   stop, obiettivi o size a metà misurazione rende i primi trade non confrontabili
   coi successivi, e il verdetto che aspettiamo da tre settimane sparisce.
2. **Tutto passa dal GATE, mai solo dal paper.** Una modifica applicata al paper e
   non al gate fa sì che il PF promesso descriva un sistema diverso da quello che
   opera. È la classe di problema che ha prodotto BIRBUSDT (1,51 promesso, 0,16
   vissuto).

---

## A. Uscite — dopo il verdetto dei 40 trade

### A1. La protezione del profitto si accende troppo tardi
**Stato:** aperto · emerso 19 set, confermato dal proprietario il 20 set

Il profit-lock si arma a metà della distanza dall'**ultimo** gradino. Con la scala
2/4/6 significa **3R**, mentre il primo incasso è a 2R: fra 2R e 3R il 70% della
posizione è protetto solo al pareggio.

```
mfe mediana (15 trade) ..... 0,85R
trade oltre 3R ............. 7%
```

I "runner" che un floor più basso taglierebbe sono **rari**; le inversioni nella
zona scoperta sono il caso comune. Proposta del proprietario: stop al primo
gradino una volta superato. Resa validabile: **ancorare il lock al PRIMO gradino
invece che all'ultimo** (su 2/4/6 si armerebbe a 1R).

**Serve:** farlo nel gate, rivalidare, poi il paper. **Non** prima dei 40 trade.

### A2. Il break-even non è validato per le strategie generate
**Stato:** aperto · emerso 20 set

`breakeven_after_tp1` dice che «lo decide il gate per ogni coppia». Per le generate
— cioè **tutte e 52 le validate** — non lo decide mai: non hanno griglia di ricerca,
e il passaggio che sceglie la scala dei TP non sceglie anche questo flag. Girano
tutte sul default globale `true`.

È lo stesso buco già chiuso per la scala (*«le generate non hanno grid → senza
questo passo restavano per sempre sulla scala globale»*), lasciato indietro su un
parametro.

**Serve:** estendere il ciclo che sceglie la scala perché provi anche
`sl_to_breakeven`. Non è ovvio che convenga: protegge, ma con mfe mediana 0,85R il
prezzo ritocca l'entrata di continuo e ogni volta chiude il 70% a zero.

### A3. La manopola del rischio non fa quello che dice
**Stato:** aperto · emerso 18 set

L'utente imposta 1% e il sistema rischia ~0,35-0,39%, variabile col trade: il cap
del 10% per posizione morde quasi sempre, e più lo stop è largo meno si rischia.

**Serve:** decidere se il cap per posizione deve restare al 10%. Non è un difetto
da riparare di nascosto — è una scelta. Toccarlo cambia la size a metà esperimento.

---

## B. Ricerca — dove il sistema smette di cercare

### B1. Il vocabolario è chiuso: 18 mattoncini
**Stato:** aperto · **la più importante di questa sezione** · emerso 19 set

L'AI può solo **combinare** 18 feature (RSI, Bollinger, MACD, VWAP, volume,
sessione, volatilità). Non può inventarne una nuova. Tutto lo spazio di ricerca è
chiuso lì dentro, per sempre.

È probabilmente la causa di un'osservazione archiviata il 6 settembre: **quasi ogni
strategia funziona su UNA sola moneta**. Se il vocabolario è troppo povero per
descrivere una regolarità vera, l'unica cosa che resta da adattare è la storia
della singola moneta.

**Serve:** un percorso perché l'AI proponga una feature NUOVA come formula
dichiarativa, validata dal gate come tutto il resto.

### B2. Le strategie scritte a mano non hanno mai validato niente
**Stato:** aperto · misurato ogni giorno

```
strategie base: 1312 valutazioni, 0 passate (0,00%)
registro: 2024 coppie base · 574 generate
```

Le 8 strategie a mano non producono una singola coppia validata da quando il
registro esiste, e occupano il 78% del registro.

**Serve:** decidere se continuare a valutarle. Toglierle libererebbe tempo di
calcolo e spazio; tenerle costa poco ma il conto è zero da settimane.

### B2bis. `rr` non serve a niente, ma scarta il 74% delle proposte AI
**Stato:** aperto · emerso 20 set

Sotto scale-out il take-profit non è più `rr × R`: è la **scala di gradini**. Il
ramo scale-out ignora `target`, quindi **`rr` non ha nessun effetto sulle uscite** —
lo dice la docstring di `effective_param_grid`, che per le strategie classiche lo
sostituisce apposta nella griglia.

Per le generate invece `rr` resta un campo obbligatorio e validato. Risultato
misurato il 20 settembre: **14 proposte AI su 19 scartate** perché `rr` era sotto
1,5, cioè per un parametro che non cambia un solo trade.

**Serve:** decidere se per le generate `rr` vada ignorato del tutto (accettando
qualsiasi valore, o togliendolo dalla spec) quando lo scale-out è attivo. Non
toccato ora: cambiare cosa si valida a metà misurazione invalida il confronto fra
le coppie validate prima e dopo.

### B3. Nessuno chiede PERCHÉ le candidate muoiono
**Stato:** aperto · emerso 19 set

Il 68% muore su `total_return`, giro dopo giro. Contiamo i morti, non facciamo
l'autopsia. Ci sono ~40 quasi-passaggi a ogni giro che nessuno legge.

**Serve:** dare all'AI i quasi-passaggi e chiederle uno schema. È ipotesi sulla
RICERCA, non su una strategia.

### B4. Un referto su ogni trade chiuso
**Stato:** aperto · emerso 19 set

Ogni trade registra indicatori all'entrata, regime, confidenza, dove è arrivato il
prezzo, perché è uscito. **Nessuno li legge.** Con 15 trade è aneddoto; con 200
diventa il dato più ricco che abbiamo — e l'AI è l'unica cosa capace di leggere 200
referti e trovare il filo comune.

### B5. Notizie e dati macro
**Stato:** aperto, **bassa priorità nonostante sia la richiesta originale**

Non esistono nel sistema: le strategie vedono solo prezzo e volume. Fear&Greed e
funding ci sono ma li usa solo il riconoscimento del regime.

**Il problema non è leggerle, è validarle:** serve l'archivio STORICO delle notizie
allineato al minuto, altrimenti il gate non può testarle e si finirebbe a operare
qualcosa di mai verificato. Costosa e incerta: le altre tre voci di questa sezione
usano dati che abbiamo già.

---

## C. Timeframe e universo

### C1. A 1 ora le strategie vanno molto meglio
**Stato:** aperto · misurato 15 set (sonda `timeframe_probe`)

```
candidate che battono il pareggio:
   5 minuti ..... 2-3%
  15 minuti ..... 8%      ← dove giriamo
   1 ora ........ 29-37%
```

L'ordine è monotono. La spiegazione più semplice sono i **costi**: più corto
l'orizzonte, più trade per lo stesso movimento, più fee e funding. Coerente col
paper, dove i costi sono 4,61 su un lordo di −13,39.

**Serve:** il verdetto dei 40 trade. Cambiare timeframe azzera il confronto.

### C2. L'universo è fermo a `--top 200`
**Stato:** aperto · rimandato per scelta

Allargarlo aumenterebbe le monete coperte (15% contro l'obiettivo del 35%), ma un
giro dura già ~2h contro un timer di 3h.

**Serve:** prima misurare quanto dura davvero un giro, poi decidere.

### C3. La copertura non raggiungerà mai il 35%
**Stato:** da decidere

Il gate è "pronto" per numero di coppie, non per copertura: 25 monete su 164 = 15%,
contro un obiettivo del 35% che con questo tasso di passaggio non arriverà.

**Serve:** decidere se l'obiettivo del 35% ha ancora senso o va sostituito.

---

## D. Infrastruttura

### D1. Il registro su più documenti
**Stato:** aperto · rimandato 19 set, non più urgente

È l'unica correzione che **scala** davvero. Rimandata perché tocca ogni lettore —
bot, learning, quattro script, due componenti della dashboard — e farla di fretta
su un documento che contiene settimane di attesa, mentre il paper gira, trasforma
un problema di spazio in una perdita di dati.

Il formato compatto ha spostato il vincolo da 3 giorni a mesi (272 KiB su 879, 108
byte a coppia): c'è tempo per farla bene.

### D2. I dati sintetici sono attivi per default
**Stato:** parzialmente chiuso · 19 set

`BACKTEST_ALLOW_SYNTHETIC` vale `true` di default. È spento esplicitamente ovunque
si validi (unit systemd, script, workflow) e nelle analisi in lista bianca, ma
qualunque percorso nuovo che carichi candele **ricade su dati inventati in
silenzio** se Binance non risponde.

**Serve:** invertire il default e accenderlo solo nei test. Richiede di verificare
ogni chiamante.

### D3. Il modello dell'AI è la versione precedente
**Stato:** aperto · banale

`ANTHROPIC_MODEL=claude-opus-4-8`. Rimandato il 19 set per non cambiare due cose
insieme mentre si verificava la chiave.

### D4. LunarCrush: abbonamento scaduto
**Stato:** da decidere · emerso 19 set

HTTP 402. È una fonte di sentiment **opzionale** e il sistema ricade su CoinGecko
(funzionante), quindi non è rotto niente. Da rinnovare o da togliere: una chiave
scaduta in configurazione è rumore che a ogni controllo sembra un guasto.

---

## E. Da tenere d'occhio (non ancora azioni)

### E1. Le short perdono sistematicamente
**Stato:** in osservazione · aggiornato 20 set

```
long    7 trade · 3 vinti · +0,53 · mfe 1,23R
short   8 trade · 1 vinto  · −18,52 · mfe 0,72R
```

Il 19 settembre erano 7 short e 0 vinte (probabilità 1,3% se il sistema fosse sano);
poi una ha vinto e si è risaliti al 5,7%. **Il divario non si è chiuso, ha smesso di
allargarsi.**

Se regge ai 40 trade, il trend smette di essere un suggerimento sulla size
(`size_mult ≥ 0,5`) e diventa un **veto**. Oggi sarebbe una reazione al rumore.

### E2. L'AI si vede scartare quasi tutte le proposte
**Stato:** corretto 20 set · in attesa di conferma al prossimo giro

Diagnosi misurata (`ai_hypotheses/last`, giro delle 08:41 ora italiana):

```
1 proposta accettata su 20
rr=1.3 ×4 · rr=1.2 ×4 · rr=1 ×3 · rr=0.9 ×3   →  14 su 19
rsi_momentum: manca il parametro mid ×1
nessuna feature direzionale ×1
```

**Non** era il parametro mancante, come mi aspettavo: era `rr` sotto il minimo di
1.5. E il prompt non nominava **nessuna** fascia numerica, quindi il modello non
poteva saperlo. Corretto generando le fasce dalle stesse costanti che validano.

Resta da vedere al prossimo giro se il tasso di accettazione sale.

### E3. Binance risponde 451 dai runner GitHub
**Stato:** noto e gestito · nessuna azione

Blocco geografico. La ricerca e la validazione girano sulla VPS dove Binance
risponde, e i due workflow che avrebbero bisogno di dati veri hanno lo schedule
disabilitato apposta. Registrato perché a ogni controllo sembra un guasto nuovo.
