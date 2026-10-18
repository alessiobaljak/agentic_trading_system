# 04 — Le idee di miglioramento registrate nel backlog, e cosa ne è stato

> Capitolo della storia del progetto: il riepilogo è in [`README.md`](README.md). Scritto il 18 ottobre 2026 da un lettore in sola lettura sul repository, poi ricontrollato da un secondo lettore che ha aperto le fonti e corretto nel testo gli errori trovati (circa 150 affermazioni, 136 giuste, 14 corrette). Dove il testo dice «bozza» o «questo pezzo», intende questo capitolo.

> I rimandi «bl. N» sono alle righe di `docs/backlog.md` al commit `672663b8` (18 ott, 09:02 UTC). Dopo, lo stesso
> giorno, è nata la voce P12 con le cose trovate scrivendo questa storia (`README.md`, sezione 8), e le righe del file
> sono spostate.

Bozza del 18 ottobre 2026. Pezzo della storia del progetto (cartella prevista: `docs/storia/`). Solo lettura del repo:
nessun file del repo è stato cambiato.

## Come leggere questo pezzo

**Da dove viene.** Il backlog nasce il 20 settembre 2026 (commit `f0ac205f`, «backlog: le cose trovate e non fatte
smettono di vivere solo nelle conversazioni»). Prima di quella data le idee non venivano registrate in modo
sistematico: lo dice l'intestazione dell'archivio («finora questi punti vivevano solo dentro le conversazioni e
sparivano», `docs/backlog_archivio.md` righe 9-11). Il 1 ottobre il file è stato diviso in due (commit `8d241733`):
`docs/backlog.md` tiene solo le voci da fare o in attesa, `docs/backlog_archivio.md` le voci fatte e in misura. Molte
voci però sono state **tolte** dal file fra il 30 settembre e il 1 ottobre e vivono solo nella storia di git e nel
diario (`docs/andremo_live.md`, sezioni «voci tolte dal backlog» del 30 set, riga 2217, e «pulizia del backlog» del
1 ott, riga 2321). Per ricostruirle ho letto ogni versione di `docs/backlog.md` (143 commit, `git log --follow`) e
preso, per ogni sigla, la prima e l'ultima versione in cui compare come titolo (elenco in fondo, appendice A).

**Quante sono.** 102 sigle diverse: 38 hanno un titolo in `docs/backlog.md`, 47 in `docs/backlog_archivio.md` (20
sono in tutti e due), 65 in almeno uno dei due file; le altre 37 esistono solo nella storia di git (A1, A2, A3, A5,
B1, B2, B2bis, B3, B4, C2, C3, D2, D3, D4, E2, E3, F1, F2, G1, G2, G4, G5, H1, H2, I2, I7, I8, I9, J1, J3, J4, J5,
J12, P3, P4, P5, R1b). In più ci sono sotto-voci con un nome
proprio nate nella revisione del 30 settembre (`docs/revisione_sospese_30set.md`): FR-leva, D6-IPOTESI, D6-L1..L4,
D6-FILTRO, D6-OMBRA, I2-bis (diventata K6), H1-misura (diventata K2), H1-soglia-holdout, E4-adx, C4-misura.

**Abbreviazioni delle fonti.**
* `bl. N` = `docs/backlog.md`, riga N (versione del 18 ott, commit `672663b8`).
* `arch. N` = `docs/backlog_archivio.md`, riga N.
* `diario N` = `docs/andremo_live.md`, riga N.
* `git <hash>` = l'ultima versione della voce in `docs/backlog.md` a quel commit (`git show <hash>:docs/backlog.md`).
* `ops NNNN` = `ops/results/NNNN-...md`, risultato di un comando eseguito sulla macchina.
* «stima» = numero calcolato da noi o da una simulazione, non misurato dal sistema.

**Parole.** R = risultato di un trade in multipli del rischio (−1 R è uno stop pieno). Gate = il filtro che decide
quali coppie (moneta + strategia) il bot può operare. Motore = il simulatore storico con cui il gate giudica. Paper =
il bot che opera senza soldi veri. Fuori campione = giorni che il gate non aveva visto quando ha scelto.
Margine = la fascia (di solito 2 errori standard) dentro cui una differenza può essere solo caso.

---

## 1. Tutte le voci

Stati usati: **fatta** (costruita e lasciata accesa; «solo misura» se raccoglie dati senza cambiare decisioni),
**provata e tolta** (costruita, misurata, spenta), **scartata** (decisa di non farla, con un numero), **aperta** (mai
fatta, ancora in attesa), **parcheggiata** (ferma per scelta del proprietario). «Nata» = primo commit in cui il titolo
compare nel backlog.

### 1.1 Serie A — uscite (nate il 20-24 set)

| Sigla | Nata | Cosa propone | Tema | Stato | Esito misurato (fonte) | Motivo del rinvio o dello scarto |
|---|---|---|---|---|---|---|
| A1 | 20 set | Armare la protezione del profitto al primo gradino di incasso invece che all'ultimo (con la scala 2/4/6 si armava a 3 R) | uscite, stop e trailing | fatta (21 set, git `432e7f48`) | Numero che l'ha decisa: 13 stop su 21 erano andati a favore (massimo a favore mediano 0,69 R) senza toccare il primo gradino e uscivano a −1 R (git `3d8f20a2`, voce A1). Effetto da sola mai misurato | tolta dal file il 1 ott perché fatta (diario 2321) |
| A2 | 20 set | Far scegliere al gate, per ogni coppia generata, se spostare lo stop al pareggio dopo il primo incasso | uscite, stop e trailing | fatta (21 set, git `340fda18`) | Tutte e 52 le validate di allora giravano sul valore di default (git `3d8f20a2`, voce A2). Effetto mai misurato da solo | tolta il 1 ott perché fatta (diario 2321) |
| A3 | 20 set | Correggere la «manopola del rischio»: il rischio vero per trade cresce con l'ampiezza dello stop (formula `min(2 × 0,10 × stop, 1%)`), il contrario di quanto scritto | dimensione e rischio | scartata (1 ott) | USELESSUSDT 21 set: −8,25 e −8,65 su ~970 di equity = 0,85% e 0,89% di rischio con stop ~4,3% (git `3d8f20a2`). Revisione: non cambia nessun risultato in R; alzando il tetto per posizione ci starebbero 1-3 posizioni contro un massimo misurato di 9 (ops 0360; `docs/revisione_sospese_30set.md` riga 75) | «scelta neutra», non serve (diario 2321) |
| A4 | 21 set | Registrare la vita di ogni strategia validata (diario `gate_history/lifecycle`, la prova non si cancella più alla rimozione); poi «declassare» a un quarto di size le validate bocciate due notti di fila | gate | fatta (21 set vite, git `9d3b69ae`; 26 set declassate) | Al primo giro completo del 26 set 167 validate su 182 non ripassavano il gate (ops 0282-0284, arch. 247). La domanda «quanto vive una validata?» non ha mai avuto un numero: unico esempio trovato HEIUSDT, 14,1 giorni (ops 0593). Declassate contro attive: «non si decide» il 3 ott (−0,131 R su 70 contro +0,127 su 33, margine ±0,458; ops 0445) e il 16 ott (−0,098 su 283 contro −0,119 su 194, ±0,174; ops 0620) | la lettura della vita mediana non è mai stata fatta; la domanda «la strategia sarebbe passata nel 2022? nel 2023?» (arch. 292-298) mai posta |
| A5 | 24 set | Prendere i take profit dai livelli del grafico (massimi e minimi recenti) invece che come multipli dello stop | uscite, stop e trailing | scartata (smentita il 24 e il 30 set) | Livello del grafico a 3,96 R in mediana, raggiunto nel 2% dei trade contro l'11% del primo gradino (ops 0210, git `ee6bf270`); il 30 set 3,35 R e 7% contro 11% (ops 0366, diario 2220); il 12 ott 3,29 R e 8% (ops 0597). Le due prime fonti non coincidono: campioni diversi | il prezzo non va lontano (massimo a favore mediano 0,84 R) |

### 1.2 Serie B — ricerca delle strategie e dati esterni (nate il 20-21 set)

| Sigla | Nata | Cosa propone | Tema | Stato | Esito misurato (fonte) | Motivo del rinvio o dello scarto |
|---|---|---|---|---|---|---|
| B1 | 20 set | Vocabolario chiuso di 18 «mattoncini»: far proporre all'AI una variabile nuova come formula | strategie e segnali | fatta a metà (21-22 set: 6 parole nuove `market_trend`, `market_fade`, `relative_strength`, `not_stretched`, `adx_below`, `htf_confirm`), il resto scartato (1 ott) | Lo stesso vocabolario a 1 ora passa lo 0,94% delle prove, a 15 minuti lo 0,20% (ops 0363) | «il limite sono i costi, non le parole» (diario 2321) |
| B2 | 20 set | Smettere di valutare le 8 strategie scritte a mano | gate | fatta (21 set, git `1670bc71`) | 1.312 valutazioni, 0 passate; 2.024 coppie base su 2.598, il 78% del registro (git `3d8f20a2`) | — |
| B2bis | 20 set | Togliere il controllo sul parametro `rr`, che non cambia nessun trade ma scartava le proposte AI | learning e AI | fatta (21 set, git `340fda18`) | 14 proposte AI su 19 scartate per `rr` sotto 1,5 il 20 set (git `3d8f20a2`) | — |
| B3 | 20 set | «Autopsia»: dare all'AI i ~40 quasi-passaggi di ogni giro e chiederle perché le candidate muoiono | learning e AI | fatta il 21 set, spenta il 2 ott insieme alle idee AI | Il 68% delle candidate moriva su «rendimento totale» (git `3d8f20a2`). Al 2 ott 0 validate su 103 strategie di origine AI (ops 0423) | spesa senza risultato (diario 2723) |
| B4 | 20 set | Un referto su ogni trade chiuso, poi la lettura dei referti da parte dell'AI | learning e AI | parte meccanica fatta (23 set: `bot/risk/setup_check.py`, `bot/learning/referti.py`); lettura AI scartata (1 ott) | La stessa domanda su 92.257 trade storici non trova condizioni utili, 0 finestre su 3 (ops 0368); su 143 referti anche il puro rumore produce un «filo comune» da +0,21 R apparenti (stima, `docs/revisione_sospese_30set.md` riga 77-79) | diario 2321 |
| B5 | 20 set | Notizie e dati macro come variabili delle strategie | dati | parcheggiata (23 set, «sessione dedicata ai dati esterni») | Nessuna fonte gratuita e verificata con storico: CryptoPanic, CryptoCompare, Dune, CoinGecko, Santiment chiusi o limitati nel 2026 (arch. 318-326). GDELT unica fonte gratuita, non provata; un dataset di notizie su Hugging Face (ott 2019-feb 2025) indicato come primo passo a costo zero, mai usato (arch. 333-344) | il problema è validarle: serve lo storico allineato al minuto (arch. 307-309) |
| B6 | 20 set | Usare lo storico gratuito di open interest e long/short di Binance | dati | parcheggiata (23 set) | Scaricato e misurato il 20 set: solo 3 coppie validate su 25 hanno dati dal 2022; 221 MiB compressi (arch. 380-386). Dal 1 ott l'open interest all'ingresso viene registrato su ogni trade (`open_interest_at_entry`, D8; diario 2561) | la copertura non basta per validare sulla finestra del gate (arch. 392-398) |
| B7 | 20 set | Registrare da soli lo storico dei dati esterni da oggi in poi | dati | parcheggiata (23 set) | 23 coppie validate su 25 senza un id CoinGecko; il backtest consuma solo candele (arch. 412-417) | serve prima un canale nel backtest |
| B8 | 21 set | Poter «ritarare» una strategia generata invece di farla solo morire: (1) varianti nate dai referti del paper, giudicate dal gate; (2) «intorno»: le soglie di una validata spostate di un gradino; (3) pre-registrazione: le varianti giudicate solo sui dati precedenti al paper | gate; learning e AI | (1) fatta 23 set, spenta 2 ott; (2) fatta 24 set, ancora accesa al 13 ott; (3) spenta dal 24 set, **aperta** | (1) 0 varianti promosse (ops 0391, 0423); storia per tipo all'11 ott: 13 ipotesi nate, 4 varianti, 0 passate (ops 0586). (2) Nel registro 36 coppie dell'intorno, 28 validate (ops 0586); nel paper −0,281 R su 13 trade contro −0,103 delle casuali (ops 0596). (3) Il taglio raddoppiava la memoria dei worker e ha ucciso quattro giri (picco 2,3 GB a worker con 6 worker, ops 0225; arch. 424) | (3) si riaccende quando la memoria lo permette (bl. 315-320). L'analisi del 12 ott propone di spegnere l'intorno (`docs/analisi_trade_16set_12ott.md`, sezione 4) |

### 1.3 Serie C — orizzonte, universo, costi (nate il 20 set-2 ott)

| Sigla | Nata | Cosa propone | Tema | Stato | Esito misurato (fonte) | Motivo del rinvio o dello scarto |
|---|---|---|---|---|---|---|
| C1 | 20 set | Strategie native a 1 ora (a 1 ora le candidate battono il pareggio nel 29-37% dei casi contro l'8% a 15 minuti) | strategie e segnali | fatta (22 set su BTC, git `e9989e7f`; 26 set su ~30 monete) | La passata a 1 ora passa di più (1,77% contro 0,86%, ops 0391), ma per composizione: 259 prove su 328 erano strategie già note (ops 0468, diario 2774). Nessuna validata né trade a 1 ora il 9 ott (ops 0559, diario 3187); nessun trade a 1 ora il 10 ott (ops 0574, diario 3280). Lettura prevista il 18 ott (`docs/letture.md`) non fatta | la prima validata a 1 ora era attesa «non prima dell'8 ott» (arch. 492) |
| C2 | 20 set | Allargare l'universo oltre le prime 200 monete per volume | gate | scartata (30 set) | La voce diceva di allargare se la copertura restava sotto 40 monete: erano 70 (ops 0363, diario 2224) | condizione non avverata |
| C3 | 20 set | Rivedere l'obiettivo di copertura del 35%, ritenuto irraggiungibile | gate | scartata (30 set) | Copertura al 35,0% il 30 set (ops 0363); 38,5% l'11 ott (ops 0586) | smentita dai numeri |
| C4 | 20 set | Chiudere le posizioni prima degli annunci macro USA (FOMC, CPI, lavoro) | regime e mercato | aperta (gruppo «prima dei soldi veri») | Nessuna fonte gratuita affidabile: FRED vieta l'archiviazione, ForexFactory ~2 mesi indietro (arch. 516-531). Nel paper tocca 1 trade su 189 (FOMC del 16 set, −4,19 USDT; ops 0371); nel caso migliore ~0,001 R sul trade medio (stima, `docs/revisione_sospese_30set.md` riga 97) | adesso renderebbe il paper diverso dal motore (bl. 387-390) |
| C5 | 2 ott | Allineare i costi a quelli veri di Binance: commissioni 0,10% andata e ritorno invece di 0,08%, funding con la sua scadenza vera (4 o 1 ora per molte monete) | esecuzione e paper | aperta (sì del proprietario il 2 ott «sì C5»; sbloccata dalle letture del 16 ott) | +4,77 USDT su 222 trade, ~+0,012 R a trade (bl. 278-279); funding sottostimato ×2 o ×8 dove pesa (bl. 280-282) | cambia i verdetti del gate; dopo il 13 ott il gate è fermo e il paper misura gli ordini limite (bl. 274) |

### 1.4 Serie D — infrastruttura, AI, dati raccolti (nate il 20 set-1 ott)

| Sigla | Nata | Cosa propone | Tema | Stato | Esito misurato (fonte) | Motivo del rinvio o dello scarto |
|---|---|---|---|---|---|---|
| D1 | 20 set | Dividere il registro delle strategie su più documenti Firestore (oggi uno solo, con limite di dimensione) | dashboard, ops e macchina | aperta («solo se serve») | Spazio rimasto ~325 coppie l'11 ott (771 KiB su 879; ops 0586), sotto la soglia di ~500 della voce e sotto l'allarme dei 400 | tocca bot, learning, quattro script e dashboard; rischio di perdere settimane di conferme (bl. 412-417). Dal 13 ott il gate è fermo |
| D2 | 20 set | Spegnere di default i dati sintetici (candele inventate se Binance non risponde) | dati | fatta (21 set) | — | — |
| D3 | 20 set | Rendere configurabile il modello AI | learning e AI | fatta (21 set) | Dal 24 set il proprietario ha scelto sulla VPS `claude-opus-4-8` (git `3d8f20a2`) | — |
| D4 | 20 set | Usare LunarCrush per il sentiment | dati | scartata (23 set, decisione del proprietario) | La chiave risponde 402 in tre misure (arch. 328-331) | i dati esterni si fanno tutti insieme in una sessione dedicata |
| D5 | 28 set | Far azzerare a `reset_paper.py` anche l'inizio del paper e il prezzo BTC di partenza | dashboard, ops e macchina | fatta (1 ott, git `edc3aaab`) | Trovata leggendo il codice, nessun reset andato male (arch. 764-775) | — |
| D6 | 29 set | Misurare e ridurre la spesa dell'AI | learning e AI | misura fatta (contatore dal 29 set); leve mai fatte; idee AI e autopsia spente il 2 ott | Stima dai log ~2,75 $/giorno (arch. 777-806); misurato il 30 set 2,80 $ in 57 chiamate, idee 55% (diario 2378). Dopo lo spegnimento 0 $ (ops 0510, 0525). Origini all'11 ott: AI 117 coppie nel registro, 4 validate; casuali 2.165 e 207 (ops 0586). Nel paper 6 trade da idee AI a −0,232 R (ops 0596) | le idee AI non producevano validate (0 su 103 al 2 ott, ops 0423) |
| D7 | 29 set | Smettere di pagare chiamate AI buttate (risposta tagliata del filtro monete; narrativa della domenica che falliva) | learning e AI | fatta (29 set-1 ott) | Filtro monete fallito 11 volte (ops 0104 … 0345); confermato «troncata» il 29 set (ops 0356): spazio portato a 5000 token. Il 30 set il filtro ha tolto 10 monete su 30 giudicandole dal nome (ops 0365) | chiusa il 1 ott quando il proprietario ha riempito il segreto del modello (arch. 808) |
| D8 | 1 ott | Raccogliere 12 dati che mancavano (versione del codice per trade, promessa del gate all'ingresso, cosa fa il prezzo dopo ogni uscita, qualità dell'ingresso, regime globale, open interest...) | dati | fatta, solo misura (attiva dal riavvio del 1 ott) | Prova di parità: motore ed executor identici prima e dopo (`tests/test_dati_parita.py`; diario 2561). Ingresso rispetto al segnale +0,027/+0,031 R, ritardo 156-161 s (ops 0503, 0521, 0536) | restano: scarti silenziosi contati ma non simulati; nessuna pulizia automatica di `data/gate_storia` (bl. 166-168) |

### 1.5 Serie E — direzione e strategie gemelle (nate il 20-21 set)

| Sigla | Nata | Cosa propone | Tema | Stato | Esito misurato (fonte) | Motivo del rinvio o dello scarto |
|---|---|---|---|---|---|---|
| E1 | 20 set | Le vendite (short) perdono sempre: se regge, trasformare il freno sul trend in un veto | regime e mercato | osservazione poi smentita (mai fatta) | 23 set: short 23 trade, −35,84; long 14, +4,75 (arch. 838). Poi il segno si gira: dal 27 set short +0,137 R su 50, long −0,073 su 69 (ops 0465); al 12 ott long −0,161 R su 242, short −0,048 su 200 (ops 0596) | «oggi sarebbe una reazione al rumore» (arch. 849-850) |
| E2 | 20 set | Dire all'AI le fasce numeriche ammesse, perché scartava quasi tutte le proposte | learning e AI | fatta (chiusa il 21 set) | Da 1 accettata su 20 a 20 su 20; 2 strategie AI passate il gate il 21 set (git `3d8f20a2`) | — |
| E3 | 20 set | Togliere i workflow GitHub che non possono avere dati (Binance risponde 451 dai runner) | dashboard, ops e macchina | fatta (21 set) | — | — |
| E4 | 21 set | Non vendere le salite verticali; togliere le strategie «quasi gemelle» sulla stessa moneta | strategie e segnali | in parte fatta (21 set, git `1d96dc3d`: freno sul trend corretto, attesa dopo uno stop nel motore e nel bot, impronta anti-gemelle, parole `not_stretched` e `adx_below`); aperte le gemelle già validate; `min_adx` sulle esistenti scartata (1 ott) | MUBARAKUSDT 21 set +37% in ~30 ore, presa short con RSI 88; USELESSUSDT tre PF 1,541/1,541/1,54 = la stessa scommessa contata tre volte (arch. 855-889). Almeno 8 gruppi di gemelle (ops 0365); l'11 ott non visibili nel log (ops 0588). ADX ultima su 18 variabili, +0,002 (ops 0368) | le gemelle già validate «vanno decise, non nascoste» (arch. 916) |

### 1.6 Serie F — scegliere fra i segnali (nate il 23-25 set)

| Sigla | Nata | Cosa propone | Tema | Stato | Esito misurato (fonte) | Motivo del rinvio o dello scarto |
|---|---|---|---|---|---|---|
| F1 | 23 set | Un «selettore»: un modello che sceglie quali segnali aprire, validato come una strategia | learning e AI | costruito (24-25 set), accensione scartata (1 ott) | Non batte «apri tutto» in 0 finestre su 3 su 92.257 trade (ops 0368); il 12 ott 0 su 3 per ogni famiglia su 150.015 trade (ops 0604) | diario 2321 |
| F1bis | 25 set | «Paper esplorativo»: operare a un quarto di size le coppie che passano il gate per un pelo | esecuzione e paper | fatta (25 set), ancora accesa | Regola scritta prima: a 100 trade esplorativi, se nessuna coppia esplorativa è poi passata, si spegne (arch. 542). Al 16 ott 35 trade a −0,081 R contro −0,116 delle validate, ±0,327 «non si vede» (ops 0620); 4 coppie poi validate, 694 scartate (ops 0620). Il 4 ott, su 10 trade, era «contribuisce» (+0,450 ±0,419, ops 0465), poi sparito | i 100 trade non sono mai arrivati |
| F1ter | 25 set | Il selettore «in ombra»: annota la sua probabilità su ogni trade senza decidere | learning e AI | fatta, solo misura | Probabilità media dei vinti 0,651 contro 0,639 dei persi, correlazione +0,098 su 409 trade (ops 0596) | si accende solo se batte «apri tutto» (non succede) |
| F2 | 23 set | Gate a due livelli: «candidata» in paper a un quarto di size dopo una conferma, «validata» dopo tre | gate | scartata (30 set, «F2 e J12 chiudile») | Il 70-77% delle coppie a 1-2 conferme non ripassa; il quarto di size non limita il danno (K5) (diario 2313-2316) | la domanda «servono 3 conferme?» la doveva dire il gruppo di controllo (K3), mai riletto |

### 1.7 Serie G — portafoglio e gate (nate il 24 set-8 ott)

| Sigla | Nata | Cosa propone | Tema | Stato | Esito misurato (fonte) | Motivo del rinvio o dello scarto |
|---|---|---|---|---|---|---|
| G1 | 24 set | Tetto di rischio per direzione (3%) | dimensione e rischio | fatta (esisteva già dall'8 set; tolta una seconda copia scritta per sbaglio il 24 set) | Sul motore: PnL da +48.444 a +56.445, drawdown da 11,74% a 10,75% (ops 0387, diario 2516); al 3% «quasi neutra» (ops 0188). Nel paper non è mai scattato (diario 2516) | — |
| G2 | 24 set | Simulare tutte le validate insieme come un portafoglio | gate | fatta (24 set, comando `portafoglio`) | Strumento usato per H3, H4, H5 | — |
| G3 | 24 set | Usare la statistica t (guadagno medio diviso quanto oscilla) come criterio del gate | gate | aperta sulla carta («a metà novembre», bl. 380-383), **ma per la regola già chiusa** | Regola H1 decisa il 30 set prima dei numeri. Il 12 ott: t ≥ 1,5 −0,23 R su 99 segnali, sotto 1,5 −0,02 su 238, differenza −0,21 ±0,24 → «H1: chiusa» (ops 0600). Il 16 ott: −0,09 ±0,21 → «chiusa» (ops 0619, diario 3858) | il backlog non è stato aggiornato (vedi sezione 6) |
| G4 | 24 set | Meno candidate casuali a giro (40 invece di 100) | gate | fatta (24 set) | 0,21-0,26% di passaggio contro 0,3% prima: nessun miglioramento visibile (diario 2333) | — |
| G5 | 24 set | Correggere il bias di sopravvivenza dell'universo (si valida solo sulle monete oggi nel top 200) | dati | scartata (1 ott) | Monete delistate nella finestra: 28 su 897, 3,1% (ops 0611) | nessuna correzione semplice; resta un avvertimento (diario 2321) |
| G6 | 24 set | Pesare di più i dati recenti (emivita 180 giorni) anche nei criteri di validazione | gate | metà fatta (25 set: solo nella scelta di scala, pareggio e keep), metà **aperta** | Prima sette giorni nuovi su 4,6 anni valevano lo 0,42% dell'evidenza (arch. 553) | cambierebbe chi entra: da decidere col tasso di passaggio prima e dopo |
| G7 | 4 ott | Far giudicare al gate candidate su prezzi rimescolati (senza vantaggio possibile) e confrontare con le vere | gate | fatta (5 ott) | Vere 8 passate su 7.200 (0,11%), rimescolate 16 su 7.200 (0,22%), rapporto 2,0 → per la regola «non si sa» perché sul vero passano meno di 10 (ops 0506, diario 2899) | — |
| G8 | 8 ott | Una «porta» nel gate per direzione e contesto: una coppia opera i long solo dove regge con BTC in discesa, ecc. | gate; regime e mercato | aperta | «Long mentre BTC scende» 79 trade dal 27 set, −0,229 R, la casella peggiore; «short mentre BTC sale» +0,134 su 48 (ops 0538); 31 long e 9 short in un giorno (ops 0551), con BTC −4,4% dal 5 all'8 ott (bl. 260) | aspettava la seconda lettura (confermata il 16 ott, ops 0619), ma la ricerca del gate è ferma dal 13 ott (bl. 272) |

### 1.8 Serie H — audit del 24 set (nate il 24 set)

| Sigla | Nata | Cosa propone | Tema | Stato | Esito misurato (fonte) | Motivo del rinvio o dello scarto |
|---|---|---|---|---|---|---|
| H1 | 24 set | Chiedere t ≥ 3 nelle finestre del gate | gate | scartata (1 ott), sostituita da K2 | La t mediana delle validate era 2,23 (ops 0363): ne avrebbe tolte la maggior parte, su dati già usati per sceglierle | diario 2321 |
| H2 | 24 set | Holdout (ultimo esame di 45 giorni) diverso per ogni candidata; almeno 10 trade invece di 5 | gate | scartata (29 set i 10 trade, 1 ott l'holdout diverso) | Simulazione (stima): senza vantaggio passa il 31% con 5 trade e il 37% con 10; con PF 2 il 63% e il 78%; rapporto buone/fortunate da 2,0 a 2,1 (git `3d8f20a2`, voce H2). Toglierebbe soprattutto le coppie con pochi trade (mediana 8 negli ultimi 45 giorni, ops 0290). Trovato un artefatto: lo «scarto 0,000» scritto d'ufficio, 21 quasi-passaggi su 32 letti dall'AI (ops 0341) → K7 | non riduce la fortuna della singola candidata e toglie l'esame sul mercato recente |
| H3 | 24 set | Stop giornaliero di portafoglio (fermarsi dopo una perdita del 2-3% nel giorno) | dimensione e rischio | parcheggiata (25 set: «non voglio limitare la quantità, voglio trade migliori») | Portafoglio del gate su 160 coppie: stop 3% PnL −21%, drawdown 16,8% invece di 14,8% (ops 0232, arch. 570). 1 ott: sul paper +2,00 su −81,11; sul gate −11.615 e drawdown da 11,7% a 20,3% (ops 0404, 0405). 12 ott: +2,00 su −130,22 (ops 0596) | aiuta il paper solo perché toglie esposizione a un sistema che perde (bl. 423-427) |
| H4 | 24 set | Freno di serie: meno size dopo una serie di perdite | dimensione e rischio | provata e tolta (acceso 23 set, spento 24 set), poi parcheggiata | Win rate dopo 4 perdite 56% su 16 contro 63%, t −0,58 (ops 0232); 62,5% su 8 contro 68,2%, t −0,34 (ops 0387). Rigioco sul gate: «3 perdite del bot → metà» −3.957 (ops 0405); sul paper +20,63 su −130,22 (ops 0596). Le due fonti sul win rate hanno campioni diversi | «nessuna prova che serva» (bl. 429-432) |
| H5 | 24 set | Separare «è il mercato» da «è il bot che esegue male» | esecuzione e paper; gate | fatta (30 set la misura fuori campione) | 25 set la prima risposta «è il mercato» (ops 0232), poi riconosciuta sbagliata: sugli stessi giorni il simulato fa −1.357 con le coppie del 25 set e +8.465 con quelle del 30 (ops 0232, 0359): misurava la selezione (arch. 51-57). Letture ufficiali: 7 ott selezione → «la prossima modifica va nel gate» (−0,05 R su 230 segnali, ±0,14; ops 0532); 16 ott confermata (−0,03 su 566, ±0,09) ed esecuzione per la prima volta oltre il margine (+0,06 ±0,05; ops 0619) | — |

### 1.9 Serie I — controllo del learning (nate il 25-29 set)

| Sigla | Nata | Cosa propone | Tema | Stato | Esito misurato (fonte) | Motivo del rinvio o dello scarto |
|---|---|---|---|---|---|---|
| I1 | 25 set | I pesi del learning mettevano in panchina una strategia dopo 2 perdite: ridurre la size invece di rifiutare | dimensione e rischio | fatta (26 set) | Nel log del 26 set 0 rifiuti per peso (ops 0268). 12 trade toccati a +0,094 R contro −0,121, ±0,846: «non si vede» (ops 0620) | — |
| I2 | 25 set | Il freno globale (size dimezzata quando il paper rende meno del promesso) non ha data di uscita; aggiunto un freno «per gruppo» (CUSUM) | dimensione e rischio | freno per gruppo provato e tolto (acceso 26 set, spento 27 set); «spegnere il freno globale» scartata (1 ott); il difetto vero passa a K6 | Il freno per gruppo sarebbe scattato dopo il globale in 6 gruppi su 7 (ops 0288). Freno globale: toccati −0,111 R contro −0,173, ±0,254, ma +32,49 USDT risparmiati (ops 0620, 0596) | «spegnere il freno non cambia nessun R» (diario 2321) |
| I3 | 25 set | Il «keep» del trailing (quanta parte del guadagno proteggere) scelto dal gate per ogni coppia; dal 27 set anche una proposta per strategia dai verdetti del paper | uscite, stop e trailing | fatta (25-27 set) | 195 validate su 239 con il keep scelto dal gate (ops 0593). Trailing: 100 uscite premature contro 98 protette (ops 0612); con keep 0,75 7 premature e 0 protette, R −0,35 su 21 (analisi 12 ott, sezione 2.5). Il metro per strategia («se i prematuri non calano, la proposta va tolta», arch. 628) non è mai stato letto | — |
| I4 | 25 set | Dai referti sulle uscite un'ipotesi «scala più stretta» per strategia | uscite, stop e trailing | fatta (25 set) | Ipotesi `scala_stretta`: 3 nate, 0 varianti (ops 0586) | — |
| I4bis | 25 set | Usare la data in cui l'ipotesi scatta, non il primo trade, per la corsia urgente | learning e AI | fatta (1 ott, `scattata_ts`) | — | era stata rinviata perché `da_ts` decide anche la pre-registrazione (diario 2393 e seguenti) |
| I4ter | 26 set | Ipotesi sulle condizioni d'ingresso (ADX, volume, volatilità, RSI) dalle perdite «mai andate a favore» | ingressi | fatta (26 set), spenta il 2 ott con le varianti dai referti | `ingresso_atr_pct` 1 nata, `ingresso_vol_ratio` 1 nata, 0 varianti (ops 0586). Lettura prevista ~10 ott non fatta | — |
| I5 | 25 set | Validate senza la loro «promessa» (PF, win rate) nel registro: per loro deriva e veto di regime non agiscono | gate | aperta, si chiude da sola | Senza `last_pf`: 137 su 212 (27 set, ops 0300) → 124 su 202 (30 set, ops 0358). Senza win rate: 129 su 208 (1 ott, ops 0403) → 37 (12 ott, ops 0596) → 42 (16 ott, ops 0620) | riempirle prima riaccenderebbe il veto di regime, un freno (bl. 327-331) |
| I6 | 25 set (rinata 2 ott) | Troppe posizioni nello stesso verso insieme: un tetto sul numero per verso | dimensione e rischio | prima versione (rimettere il tetto di 5) scartata il 1 ott; rinata il 2 ott come misura; tetto **aperto** | 10 long aperti in 20 s il 2 ott (ops 0442-0443). R per posizioni nello stesso verso: 1-2 −0,083, 3-5 −0,126, 6+ −0,162 su 46 (ops 0596); 6+ −0,193 su 70 (ops 0620). Nel motore il tetto per direzione alza il PnL e abbassa il drawdown (ops 0387) | prima versione: toglierebbe trade in ordine d'arrivo, non i peggiori; 0 rifiuti per rischio su 71 (ops 0370) |
| I7 | 29 set | Contare anche le uscite con incasso parziale nei verdetti del trailing | uscite, stop e trailing | scartata (30 set) | Contandole i «protetti» scendono dal 58,6% al 55,1% (49 su 89), più lontani dalla soglia del 60% (diario 2230) | non cambierebbe nessuna scelta |
| I8 | 29 set | Usare i verdetti dopo gli stop (il prezzo torna al primo target = «rumore») per allargare lo stop | uscite, stop e trailing | scartata (30 set) | 23 «rumore» su 79 stop = 29%, dentro quanto darebbe il caso, 26-55% (simulazione, stima; diario 2233) | nessuna base per una regola |
| I9 | 29 set | Isteresi sulla proposta di keep 0,75 (si accende e si spegne attorno al 60%) | uscite, stop e trailing | scartata (1 ott) | 5 trade con keep 0,75 in tutto, −0,14 R (ops 0358); il gate sceglie il keep alto anche su prezzo casuale (stima) | diario 2321 |

### 1.10 Serie J — controllo orario, dashboard, misure (nate il 25 set-29 set)

| Sigla | Nata | Cosa propone | Tema | Stato | Esito misurato (fonte) | Motivo del rinvio o dello scarto |
|---|---|---|---|---|---|---|
| J1 | 25 set | Somme incrementali invece di rileggere tutti i trade ogni ora | dashboard, ops e macchina | scartata (1 ott, senza lavoro) | ~190 trade al 1 ott: costo nullo; lo sorveglia l'anomalia `CONTROLLO_LENTO` | diario 2353 |
| J2 | 25 set | Mostrare in dashboard le voci che aspettano il sì del proprietario | dashboard, ops e macchina | parcheggiata il 25 set, poi fatta il 1 ott (`bot/learning/backlog_doc.py`) | — | in `docs/backlog.md` risulta ancora «in lavorazione» (bl. 154) |
| J3 | 25 set | Un timer sulla VPS per il controllo quando il bot è fermo | dashboard, ops e macchina | scartata (1 ott) | — | un controllo vecchio è già l'avviso che il bot è fermo |
| J4 | 25 set | Verificare dal vivo la dashboard nuova | dashboard, ops e macchina | fatta (1 ott) | il proprietario ha trovato il 28 set i due totali diversi (+1,26 e +3,25), spiegati | — |
| J5 | 25 set | Rendere persistenti i contatori in memoria | dashboard, ops e macchina | scartata (1 ott) | — | costerebbe una scrittura per rifiuto; i rifiuti utili sono già salvati (J6) |
| J6 | 26 set | «Ombra dei rifiutati»: simulare come sarebbero andati i segnali che il bot non ha aperto | esecuzione e paper | fatta, solo misura (26 set; corretta 27 set e 1 ott) | 12 ott: «posizione aperta» −0,10 R su 217 come gli aperti (−0,10); «cooldown» +0,15 su 74 → lo strumento stampa «si può RITARARE», con margine ±0,29 e rifiutati senza costi, che valgono ~0,1-0,2 R di vantaggio apparente (ops 0599). Lettura ufficiale prevista il 26 ott | regola: si ritara solo con ≥ 30 casi e rifiutati meglio degli aperti, e anche allora è una proposta per il gate (arch. 683) |
| J7 | 26 set | Dividere i risultati per direzione e contesto di BTC (long con BTC su/giù, short con BTC su/giù) | regime e mercato | fatta, solo misura (26 set) | Ha dato i numeri della porta G8 (ops 0538); al 12 ott short contro BTC +0,030 R, long contro BTC −0,152 (ops 0596) | — |
| J8 | 26 set | Misurare se la confidenza del regime e l'indice Fear & Greed predicono l'esito | regime e mercato | fatta, solo misura | Terzili della confidenza: vinti 54%, 60%, 50%; PnL medio −0,60%, +0,12%, −0,58% (ops 0596). Lo strumento stampa «cresce» perché la fascia alta (−0,58%) supera di poco la bassa (−0,60%). Fear & Greed: 478 trade su 480 nella fascia di mezzo (ops 0596) | «la confidenza del regime non predice» (`docs/analisi_trade_16set_12ott.md`, sezione 2.6) |
| J9 | 26 set | Storia delle ipotesi dei referti e delle loro varianti, per tipo | learning e AI | fatta, solo misura | All'11 ott 13 ipotesi nate, 4 varianti, 0 passate; tasso delle figlie 0% contro 0,3% delle candidate (ops 0586) | lettura prevista ~10 ott non fatta come lettura a sé |
| J10 | 26 set | Giro completo del gate «ridotto»: strategie note solo dove hanno una coppia viva più una fetta a rotazione | dashboard, ops e macchina | fatta (26 set) | Metro scritto: completo ≤ 1h30. Misurato: 2h58 (1 ott, ops 0391), 3h22-3h28 (5-6 ott, ops 0501, 0520), 4h18 un giro urgente l'11 ott (ops 0586). Il primo giro con tutte le strategie era 3h48 (ops 0282-0284) | metro mancato; il passo scritto «se resta sopra le 2 ore, misurare dove sta il tempo» (arch. 694) non risulta fatto |
| J11 | 27 set | Conferma della finestra settimanale solo se la coppia passa più della metà delle sue valutazioni | gate | fatta (27 set) | Numero che l'ha decisa: valutate una volta sola passavano 23 validate su 194 (ops 0290). Metro: quota sopra il 50% in tre settimane; mai riletta (unico risultato `autopsia-validate` è ops 0290). Lettura prevista il 18 ott non fatta | — |
| J12 | 27 set | Verificare se il paper entra dove entra il motore | esecuzione e paper | fatta (chiusa il 30 set, obiettivo 80% raggiunto) | 54% il 26-27 set (ops 0304) → 81%, 64 su 79 (ops 0373); 81%, 58 su 72 sulle 8 coppie l'11 ott (ops 0594); 102 su 133 a 0 minuti il 12 ott (ops 0608) | — |
| J13 | 27 set | La variabile «sessione oraria» leggeva l'ora dell'orologio e non quella della candela: correggerla e azzerare le coppie che la usavano | strategie e segnali | fatta (27 set, opzione «azzerare» scelta dal proprietario) | 47 validate su 212 usavano la sessione (ops 0314); 347 coppie azzerate in tutto, 1 ripassata all'11 ott (ops 0586). Prima della correzione 20 trade non riproducibili, −33,57 USDT, circa metà della perdita del paper al 4 ott (ops 0483, diario 2834; il diario annota «Non verificato: che le due spec usino `session`», riga 2846). Lettura prevista il 18 ott non fatta | regola scritta: se ne ripassano meno di un quarto, la sessione «vinceva per il difetto» (arch. 725) |
| J14 | 28 set | Ridurre le letture Firestore (quota gratuita di 50.000 esaurita il 28 set) | dashboard, ops e macchina | fatta (28 set) | Da 39.000 letture al giorno (26 set, console Firebase; arch. 731) a 6.832 (ops 0449) e 8.674 (ops 0527) nelle 24 ore, sotto le 15.000 del metro | — |
| J15 | 29 set | Rinominare la riga «cambiamenti 24h» che in realtà confronta con un'ora prima | dashboard, ops e macchina | fatta (1 ott, git `edc3aaab`) | — | — |

### 1.11 Serie K — revisione delle voci in sospeso (nate il 30 set-1 ott)

| Sigla | Nata | Cosa propone | Tema | Stato | Esito misurato (fonte) | Motivo del rinvio o dello scarto |
|---|---|---|---|---|---|---|
| K1 | 30 set | Scrivere prima dei numeri le regole delle letture del 3, 7 e 14 ottobre | ricerca e protocollo; gate | fatta (30 set) | Regole nel diario del 30 set (riga 2262-2264). Hanno prodotto i verdetti del 7 e del 16 ott (ops 0532, 0619). Restano tre punti non corretti (arch. 92-96) | — |
| K2 | 30 set | Salvare la t di ogni validata e dividere il fuori campione per t (H1-misura) | gate | fatta (30 set-1 ott) | Passata del voto: 213 coppie in 647 s; t dell'ultimo esame ≥ 2 in 18 su 183 (ops 0383). Esito della regola H1: «chiusa» il 12 e il 16 ott (ops 0600, 0619) | — |
| K3 | 30 set | Gruppo di controllo: ~50 candidate bocciate a giro e la foto delle conferme, da rigiocare dopo | gate | raccolta fatta (30 set); rigioco **mai fatto** | Nessun risultato ops del rigioco trovato; lettura prevista il 15 ott (`docs/letture.md`) non fatta | doveva rispondere a «servono 3 conferme?» (F2) |
| K4 | 30 set | Il paper ha la firma del caso: condizione da superare prima dei soldi veri | esecuzione e paper | aperta (condizione, non lavoro) | Paper contro prezzo casuale con le stesse uscite: stop 44% contro 46%, massimo toccato 0,80 R contro 0,81, vinti 55% contro 54%, R −0,110 contro −0,067 (ops 0596) | — |
| K5 | 30 set | Il «quarto di size» di declassate ed esplorative agisce poco con stop stretti | dimensione e rischio | aperta | Rischio effettivo medio: declassate 0,11%, attive 0,23% del capitale (ops 0620): agisce a metà | prima dei soldi veri |
| K6 | 30 set | Il freno globale ha un'uscita irraggiungibile: chiede un massimo toccato mediano sopra 1,05 R (I2-bis) | dimensione e rischio | aperta | Paper 0,87 R (ops 0366), motore che guadagna 1,03 R (ops 0371), prezzo casuale 0,81 R (stima): la condizione non dice niente. La revisione sceglieva di toglierla (`docs/revisione_sospese_30set.md` riga 89-92) | prima dei soldi veri |
| K7 | 30 set | Correggere i numeri sbagliati che arrivavano all'AI (scarto 0,000, riga del gate ferma al 21 set) | learning e AI | fatta (1 ott) | 21 quasi-passaggi su 32 erano il segnaposto (ops 0341); la riga «su 1320 valutazioni ne passano 0» era ferma al 21 set (oggi 24.503 e 48, ops 0363) | — |
| K8 | 30 set | Conti in R invece che in USDT; costi e scivolamento degli stop | esecuzione e paper | parte report fatta (1 ott, git `edc3aaab`); scivolamento degli stop **aperto** | Costi 0,08 R a trade (ops 0401), 0,095 (ops 0596), 0,089 (ops 0620). Stop chiusi al prezzo esatto in motore e paper (arch. 196-197) | prima dei soldi veri |
| K9 | 1 ott | La leva torna a 2x dopo una sola vincita: un minimo di trade prima che il peso alzi la leva | dimensione e rischio | aperta | Leva sopra 1x: −0,152 R su 154 contro −0,103, ±0,175; pesi alti: −0,179 su 150 contro −0,022, ±0,341 (ops 0620). Il segno va contro, dentro il margine | tocca la size: dopo le letture |
| K10 | 1 ott | Il supervisore automatico ha abbassato la soglia del win rate del gate da 0,45 a 0,3966 e non l'ha più rimessa | gate | conteggio fatto (1 ott); rimetterla **aperta** | 1 ott: 7 validate esistono solo grazie alla soglia bassa, +0,244 R su 11 trade (ops 0403). 12 e 16 ott: 0 coppie «allentate» (ops 0596, 0620) | modifica del gate: dopo le letture |
| K11 | 1 ott | La storia delle esplorative tagliata a 200 voci cancellava le «validate» | dati | fatta (1 ott) | «Esplorative poi validate» era sceso da 1 a 0 senza cambiamenti veri (ops 0363 → 0391) | — |

### 1.12 Serie P — protocollo di ricerca (nate il 5-18 ott)

| Sigla | Nata | Cosa propone | Tema | Stato | Esito misurato (fonte) | Motivo del rinvio o dello scarto |
|---|---|---|---|---|---|---|
| P0 | 5 ott | Un protocollo di ricerca per moneta, con un periodo chiuso («vault») che si apre una volta sola | ricerca e protocollo | fatta e chiusa (12 ott) | 630 varianti su 20 monete e sul gruppo di 80 → 45 candidati di Fase 2 → 7 in validazione → 3 al vault → 0 passati, contro 0,02 attesi per caso (`research/confronto/risultati.md`, diario 3569). Motivo d'origine: cinque misure dicevano che il gate non trova un vantaggio (bl. 107) | — |
| P1 | 8 ott | Versione 4.5 del protocollo: correzioni emerse dalle prime campagne | ricerca e protocollo | fatta (approvata il 9 ott alle 12:06 UTC) | Prova a placebo: «netta» per caso 0,41%, p sotto 0,10 in validazione 3,26% (bl. 201) | — |
| P2 | 10 ott | Sette cose trovate preparando la campagna di gruppo (testi da allineare, guardiano, file dei candidati, memoria a 15 minuti) | ricerca e protocollo | aperta | Stima della revisione: 1,1 GB per processo a 15 minuti (bl. 196) | non servivano alla campagna di gruppo |
| P3 | 10 ott | Due scelte prese dal coordinamento per il proprietario sulla campagna di gruppo (taglio comune, trasferimento) | ricerca e protocollo | chiusa (11 ott) | Con il 70/30 per moneta il 34,5% dei giorni-moneta di validazione cadeva nella costruzione di un'altra moneta (git `ad3439a8`) | il gruppo non ha avuto candidati |
| P4 | 11 ott | Aprire il vault per i 3 candidati (BTC, BNB, ADA) | ricerca e protocollo | fatta (11 ott, «APRI IL VAULT» alle 17:29 UTC) | Tutti bocciati: BTCUSDT-V10 PF 1,067 contro 1,10 su 325 trade; BNB 0,55; ADA 0,79 (git `5df4bba5`, diario 3540) | — |
| P5 | 11 ott | Dopo il vault: trasferire sulle altre monete (Passo 6) o fare subito il giudizio d'insieme (Passo 7) | ricerca e protocollo | chiusa (12 ott, il proprietario salta il Passo 6) | — | — |
| P6 | 12 ott | Cosa fare del bot e della ricerca dopo la ricerca 4.5 | ricerca e protocollo; gate | in parte fatta (13 ott «procedi con tutto»): ricerca automatica del gate ferma (`ops/gate_fermo`), ingressi a ordine limite nel paper, seconda edizione del protocollo; il resto aperto | Paper −108,25 USDT su 459 trade secondo bl. 96 (ops 0584); ops 0584 stampa 458 trade e −109,19. Gate: 27.000 prove a giro, passa lo 0,29%, le passate fanno −0,06 R (ops 0601, 0604). Prova degli ordini limite: esecuzione 98%, costo da 0,062 a 0,039 R (−0,0225 contro i −0,04 richiesti), trade saltati 2,4% ma i migliori (+0,68 R) → «conviene poco» (`research/esperimenti/ordini_limite/risultati.md`). Paniere a barre giornaliere: nessuna strategia valida, due candidate cadute in Fase 4 (diario 3825). Misura degli ordini limite nel paper (3-4 settimane) non ancora letta | le 12 proposte di metodo di `research/lezioni/metodo.md` (punto d) restano non decise |
| P7 | 16 ott | Insegnare al bot a eseguire le strategie del catalogo del protocollo (incroci, uscite a tempo, limit con k × ATR, stop minimo 0,3%...) | esecuzione e paper | aperta | Oggi il bot non sa eseguire nessuna variante del catalogo (`research/config/bot_3.md`, punto 3); la prova di parità C del collaudo non è mai partita | farla subito o solo se un candidato supera il vault (bl. 89-91) |
| P8 | 17 ott | Robustezza: per le soglie a zero (funding 0,00%) uno spostamento di un passo fisso, perché il ±20% di zero è zero | ricerca e protocollo | **fatta nel protocollo 4** ma ancora elencata in attesa | Il protocollo 4 lo prevede (`research/PROTOCOLLO_4.md` riga 693 e 956; `research/protocollo_4_note.md` sezione 2, riga 4) | il backlog non è stato aggiornato |
| P9 | 17 ott | Scelta delle monete: volume dell'anno diviso i giorni dell'anno; una serie finisce all'ultima candela con scambi | dati; ricerca e protocollo | **fatta nel protocollo 4** ma ancora elencata in attesa | MATICUSDT 169 ore a prezzo fermo e volume zero dopo l'ultimo scambio; APT senza volume 2023 nella tabella (bl. 64-73). Regole in `research/PROTOCOLLO_4.md` righe 174-176 e 452 | il backlog non è stato aggiornato |
| P10 | 17 ott | Il prossimo protocollo con le 8 proposte delle lezioni di BTC51 | ricerca e protocollo | fatta (protocollo 4 approvato il 17 ott alle 20:12 UTC) | V-020 aveva superato la validazione con +0,167 R su 80 trade (circa 1,2 errori standard) ed era caduto nel vault (−0,007 R su 180) e su 8 monete di controllo su 9 (bl. 53-56). LINK6: nessun candidato, 33 varianti su 40, R medio −0,030 contro −0,032 delle entrate casuali (`research/campagne/LINK6/lezioni.md`) | — |
| P11 | 18 ott | Dopo LINK6: continuare la ricerca, e come | ricerca e protocollo | decisa dal proprietario (continuare), proposta di come ripartire **aperta** | Il metodo vede i vantaggi inseriti: 88 su 88 da 0,35 R (`research/collaudo_4/esiti.md`) | prima la storia del progetto, poi la proposta (bl. 36-39) |

### 1.13 Serie R e T — gate rigiocato nel passato, curva del vantaggio, take profit (nate il 1-4 ott)

| Sigla | Nata | Cosa propone | Tema | Stato | Esito misurato (fonte) | Motivo del rinvio o dello scarto |
|---|---|---|---|---|---|---|
| R1 | 1 ott | Rifare il gate a 26 date passate e confrontare dopo le promosse con le bocciate | gate | provata e tolta (fermata il 4 ott, opzione c del proprietario) | 8 date su 26, 6 promosse, 45 trade a −0,22 R contro −0,14 R delle bocciate: «non decide» (ops 0502); 1 promossa su 9.050 giudizi (diario 2851). Tempo: stimato 13-17 ore, poi ~45,8 ore rimaste stimate dal tempo misurato a unità, 129 s (ops 0433, diario 2650) | troppo lenta; la scelta del gate si leggeva già nel fuori campione |
| R1b | 4 ott | Scegliere fra più candidate per data, strategie già passate, o fermare R1 | gate | chiusa (4 ott, opzione c) | Per arrivare a 80 trade servirebbero ~40 promosse, centinaia di migliaia di giudizi (stima, git `0dc9e382`) | — |
| R2 | 3 ott | Taratura di R1: le stesse candidate giudicate dal gate di produzione con i dati di oggi | gate | fatta (4 ott) | 0 passate su 3.600 coppie: «lo 0 di R1 è vero» (ops 0485) | — |
| T1 | 2 ott | Take profit adattati al singolo trade, misurati sul movimento tipico della moneta nell'orizzonte del trade | uscite, stop e trailing | aperta, **congelata** dalla regola di T2 | 111 coppie su 209 con il primo incasso a 2 R mentre il massimo a favore mediano è 0,85 R; l'89% dei trade non tocca nessun take profit (ops 0394, 0417). Colonna di sola misura 0,8/1,6/2,4: −0,20/−0,24 R contro −0,86 della 2/4/6 nel modello semplificato (ops 0495, 0529); il 12 ott −0,265 contro −0,849 (ops 0597) | senza vantaggio all'ingresso cambia la forma, non il segno (bl. 376) |
| T2 | 2 ott | Misurare se e per quanto i segnali hanno un vantaggio sul caso (curva del vantaggio a 1, 4, 12, 24 ore) | strategie e segnali | fatta, solo misura (2 ott) | «Nessun vantaggio misurabile» su 201 trade (ops 0437); il 12 ott su 448 trade +0,008 / +0,066 / +0,119 / +0,028 mosse tipiche, tutte dentro il margine (ops 0597) | — |

### 1.14 Sotto-voci con un nome proprio (revisione del 30 set)

| Nome | Cosa | Esito (fonte) |
|---|---|---|
| FR-leva | Togliere prima le coppie che il gate abbandona | scartata: il −0,23 R su 45 trade veniva dal periodo del difetto della sessione; declassate +0,065 su 27 contro attive −0,039 su 45 (ops 0291, 0360; `docs/revisione_sospese_30set.md` riga 67-70) |
| D6-FILTRO | Filtro delle monete fatto dall'AI | spento il 30 set dal proprietario («filtro spegnilo tu»): giudicava dal nome, ha escluso QUSDT con 393 giorni di storia (diario 2308-2309) |
| D6-OMBRA | Ombra AI: il modello dice se avrebbe aperto ogni trade | spenta il 30 set («ombra spegnilo tu»): veto sull'85% dei trade, non passa dal gate, ~1.200 letture Firebase al giorno (diario 2310-2312). Dopo: i trade che avrebbe vetato −0,100 R su 85 contro +0,226 su 27 dove era d'accordo, ±0,360 (ops 0620) |
| D6-L1..L4 | Leve per la spesa AI (meno chiamate, modello più economico) | mai fatte: superate dallo spegnimento del 2 ott |
| D6-IPOTESI | Le idee AI servono? Contare le coppie per origine | fatta il 1 ott (riga ORIGINI); esito in D6 |
| E4-adx | Togliere `min_adx` | scartata: ADX ultima su 18 variabili (ops 0368) |
| H1-soglia-holdout | Chiedere una t minima all'ultimo esame | mai proposta: la regola H1 l'ha chiusa (ops 0600, 0619) |
| C4-misura | Misurare l'effetto degli annunci USA | parcheggiata: ~0,001 R nel caso migliore (stima) |

---

## 2. Provato e non ha funzionato

Qui «non ha funzionato» vuol dire: è stato costruito o misurato, e il numero dice che non migliora i risultati (o
non si distingue dal caso).

**Il gate stesso.**
* La scelta del gate non regge fuori campione: −0,05 R su 230 segnali (7 ott, ops 0532), −0,03 R su 566 (16 ott, ops
  0619). La promessa del gate è un profit factor 2,03, il vissuto 0,71 (ops 0612).
* Sui prezzi rimescolati il gate promuove il doppio che sui veri: 16 contro 8 su 7.200 (G7, ops 0506). Per la regola
  scritta prima l'esito è «non si sa» (sotto 10 passate sui prezzi veri): un indizio, non una prova.
* Una candidata nuova a caso non passa quasi mai: 0 su 3.600 (R2, ops 0485); a 15 minuti 25 su 20.667 (ops 0470).
* Con 27.000 prove a giro, a t = 2 ci si aspettano ~614 passaggi per caso; per lasciarne passare al massimo una
  servirebbe t = 3,96 e nessuna candidata ci arriva (ops 0601, `docs/analisi_trade_16set_12ott.md` sezione 2.6).
* Il voto t non separa le buone dalle fortunate: −0,21 ±0,24 (ops 0600), −0,09 ±0,21 (ops 0619) (G3/K2).
* Il gate rigiocato nel passato: promosse −0,22 R contro bocciate −0,14 su 45 trade, non decide (R1, ops 0502).
* Meno candidate casuali (G4): 0,21-0,26% contro 0,3%, nessun miglioramento (diario 2333).
* Giro completo ridotto (J10): obiettivo 1h30, misurato 2h58-3h28 (ops 0391, 0501, 0520); un giro «solo urgenti» 4h18 (ops 0586).

**Imparare dal paper.**
* Varianti nate dai referti (B8 parte 1, I4, I4ter, J9): 13 ipotesi, 4 varianti, 0 passate (ops 0586); 0 promosse
  (ops 0391, 0423). Spente il 2 ott.
* Figlie «nell'intorno» (B8 parte 2): nel paper −0,281 R su 13 trade contro −0,103 delle casuali (ops 0596).
* Selettore (F1, F1ter): 0 finestre su 3 su 92.257 trade (ops 0368) e su 150.015 (ops 0604); correlazione con
  l'esito +0,098 su 409 trade (ops 0596).
* Lettura AI dei referti (B4): nessuna condizione utile su 92.257 trade (ops 0368).
* Freno per gruppo (I2): sarebbe scattato dopo il globale in 6 gruppi su 7 (ops 0288). Spento il 27 set.
* Freno di serie (H4): win rate dopo 4 perdite non diverso (t −0,58, ops 0232; t −0,34, ops 0387). Spento il 24 set.
* Stop giornaliero (H3): sul portafoglio del gate −11.615 e drawdown da 11,7% a 20,3% (ops 0405).
* Funzioni che modulano size e leva (pesi alti, leva, tilt di trend e sentiment): tutte con il segno contrario al
  voluto, dentro il margine. Tilt −0,187 R su 220 contro −0,056, ±0,166; pesi alti −0,179 contro −0,022, ±0,341;
  leva −0,152 contro −0,103, ±0,175 (ops 0620).
* Declassate a un quarto (A4): due letture «non si decide» (ops 0445, 0620); in denaro hanno risparmiato +39,40 USDT
  (ops 0596), in R non si distinguono.

**Uscite.**
* Take profit dal grafico (A5): il livello è a 3,3-4 R e lo raggiunge il 2-8% dei trade (ops 0210, 0366, 0597).
* Verdetti dopo gli stop (I8): 29% «rumore», dentro il caso 26-55% (stima, diario 2233).
* Contare gli incassi parziali nel keep (I7): allontana la proposta (55,1% invece di 58,6%).
* Isteresi del keep 0,75 (I9): 5 trade a −0,14 R (ops 0358).
* Il trailing non taglia i vincitori più di quanto li protegga: 100 contro 98 (ops 0612). Non è un difetto: è ciò
  che fa un prezzo senza direzione.

**AI.**
* Idee AI e autopsia (B3, D6): 0 validate su 103 strategie AI al 2 ott (ops 0423), 4 su 117 all'11 ott (ops 0586);
  6 trade a −0,232 R (ops 0596). Spente il 2 ott.
* Filtro monete AI e ombra AI (D6-FILTRO, D6-OMBRA): nessun effetto misurabile sui trade; spenti il 30 set.

**Direzione e regime.**
* «Le short perdono sempre» (E1): il segno si è girato da solo (ops 0465, 0596). Un veto sulle short sarebbe stato
  sbagliato.
* Confidenza del regime (J8): vinti 54%, 60%, 50% nei tre terzi (ops 0596): non predice.
* La sessione oraria come variabile (J13): dopo la correzione 1 coppia ripassata su 347 azzerate (ops 0586), segno
  che vinceva per il difetto (lettura formale mai fatta).

**La ricerca con il protocollo.**
* Ricerca 4.5 (P0): 630 varianti, 0 oltre il vault contro 0,02 attese (`research/confronto/risultati.md`).
* Vault dei 3 candidati (P4): BTC PF 1,067 contro 1,10; BNB 0,55; ADA 0,79 (diario 3540).
* Campagna di gruppo: 30 varianti su 30, nessun candidato (git `98add7fb`, voce P4).
* Paniere a barre giornaliere (P6): 18 varianti, nessuna valida (diario 3825).
* BTC51 (P10): V-020 caduto nel vault, −0,007 R su 180 trade (`research/vault/BTC51_risultati.md`).
* LINK6 (P11): 33 varianti, R medio −0,030 contro −0,032 delle entrate casuali.
* Ordini limite (P6): costo −0,0225 R contro i −0,04 richiesti; le entrate casuali risparmiano uguale: «i costi
  scendono, un vantaggio non nasce» (diario 3611-3625).

---

## 3. Provato e ha funzionato (o è rimasto)

Attenzione: nessuna di queste voci ha reso il paper profittevole. «Ha funzionato» vuol dire che ha raggiunto il suo
metro (una misura pulita, un difetto tolto, un costo tagliato).

**Misure che hanno dato una risposta chiara.**
* Le regole scritte prima dei numeri (K1, H5): verdetti netti il 7 e il 16 ott (ops 0532, 0619): «la prossima
  modifica va nel gate».
* La curva del vantaggio (T2): «nessun vantaggio misurabile» su 201 e 448 trade (ops 0437, 0597).
* Il prezzo rimescolato (G7) e la taratura (R2): strumenti semplici che hanno detto molto in meno di un'ora (ops
  0485, 0506).
* Il voto t (K2): ha chiuso H1 con un numero invece di lasciarla aperta (ops 0600, 0619).
* Paper contro prezzo casuale (K4): ha detto che le misure d'uscita sono la forma delle regole, non una diagnosi
  (ops 0596).
* L'ombra dei rifiutati (J6): i segnali scartati per «posizione aperta» rendono come gli aperti (−0,10 contro −0,10
  su 217, ops 0599): il bot non butta via segnali buoni.

**Difetti tolti.**
* Sessione oraria (J13): dopo la correzione 7 trade su 8 riprodotti dal motore, nessuno «la regola non scatta»
  (ops 0483). Prima, 20 trade non riproducibili valevano circa metà della perdita del paper al 4 ott (che venissero
  dalla sessione il diario lo scrive «non verificato», riga 2846).
* Ingressi allineati al motore (J12): da 54% (ops 0304) a 81% (ops 0373, 0594); 102 su 133 a 0 minuti (ops 0608).
* Proposte AI non più scartate (E2, B2bis): da 1 su 20 a 20 su 20 (git `3d8f20a2`).
* Letture Firestore (J14): da 39.000 (arch. 731) a 6.800-8.700 al giorno (ops 0449, 0527).
* Chiamate AI troncate (D7), dati sintetici di default (D2), workflow GitHub senza dati (E3), reset del paper
  (D5), storia delle esplorative (K11), dati sbagliati all'AI (K7), scritte che portavano fuori strada (J15, panchina
  in parità).

**Cose rimaste accese con un contributo misurato (anche solo in denaro).**
* Tetto di rischio per direzione (G1): sul motore PnL da +48.444 a +56.445 e drawdown da 11,74% a 10,75% (ops 0387).
* Freno globale: in denaro +32,49 USDT risparmiati (ops 0596); in R non si distingue.
* Declassate a un quarto (A4): +39,40 USDT risparmiati (ops 0596).
* Paper esplorativo (F1bis): 4 coppie esplorative poi validate (ops 0620), quindi per la sua regola non va spento;
  in R non si distingue (−0,081 contro −0,116, ±0,327).
* Copertura dell'universo: 35% il 30 set (ops 0363), 38,5% l'11 ott (ops 0586), dopo B2 (via le strategie a mano) e
  C1 (passata a 1 ora).
* Spegnimento delle parti AI (D6): spesa da ~2,8 $ al giorno a 0 (ops 0510, 0525) senza perdere validate.
* Raccolta dei dati mancanti (D8): attiva, prova di parità superata (`tests/test_dati_parita.py`).
* Ordini limite nel paper (P6): accesi dal 13 ott come banco di misura; costo atteso più basso (0,062 → 0,039 R sulla
  storia), misura nel paper non ancora letta.
* Il metodo del protocollo: vede i vantaggi inseriti (88 su 88 da 0,35 R, `research/collaudo_4/esiti.md`) e ha fermato
  V-020 prima del paper.

---

## 4. Mai provato, ancora aperto

| Voce | Cosa | Perché è rimasta aperta |
|---|---|---|
| G8 | Porta nel gate per direzione e contesto BTC | aspettava la lettura del 14 ott; confermata, ma il gate è fermo (bl. 272) |
| C5 | Costi veri di Binance (0,10% e funding per scadenza) | sì del 2 ott «dopo le letture»; poi gate fermo e paper sugli ordini limite (bl. 274) |
| G6 (seconda metà) | Recenza anche nei criteri di validazione | cambierebbe chi entra; mai deciso |
| B8 (pre-registrazione) | Giudicare le varianti solo sui dati prima del paper | memoria dei worker (ops 0225) |
| E4 (gemelle già validate) | Decidere se tenerle, una per moneta, o nessuna | «vanno decise, non nascoste», mai decise |
| I6 (tetto per verso) | Tetto sul numero di posizioni nello stesso verso | misura in corso; «dopo le letture» |
| K9 | Minimo di trade prima che il peso alzi la leva | tocca la size: «dopo le letture» |
| K10 | Rimettere la soglia del win rate a 0,45 | modifica del gate: «dopo le letture»; al 16 ott 0 coppie «allentate» fra quelle col win rate salvato, 42 senza (ops 0620) |
| I5 | Riempire la promessa mancante delle validate | riaccenderebbe il veto di regime; si chiude da sola |
| T1 (a-f) | Scale dei take profit per famiglia, sulla media per le strategie di ritorno, quote 30/30/40, trailing «chandelier» | congelata finché la curva del vantaggio non mostra un vantaggio |
| G3 | t minima nel gate | sulla carta «metà novembre»; per la regola già chiusa |
| D1 | Registro su più documenti | rifacimento rischioso; gate fermo |
| C4, K5, K6, K8 (scivolamento) | Annunci USA, quarto di size, uscita del freno, scivolamento degli stop | «prima dei soldi veri» |
| K4 | Il paper deve distinguersi dal caso | è la condizione da superare, non un lavoro |
| B5, B6, B7 | Dati esterni (notizie, open interest, storico nostro) | parcheggiate dal proprietario il 23 set |
| H3, H4 | Stop giornaliero, freno di serie | parcheggiate dal proprietario |
| P2 | Sette correzioni ai testi e agli strumenti della ricerca | non servivano alla campagna di gruppo; non verificato se assorbite nei protocolli 3 e 4 |
| P6 (d) | Le 12 proposte di metodo in `research/lezioni/metodo.md` (stop a distanza fissa, baseline ristretta al filtro, ordine dei ritocchi, test del ritardo, stabilità su due anni, R senza i 3 migliori in validazione, slippage per anno, tetto dello stop, previsione numerica, prova di causalità, test paralleli, candidato «debole») | «elencate, non decise» (riga 369); non verificato voce per voce quali siano entrate nei protocolli 2-4 |
| P7 | Il bot che esegue il catalogo del protocollo | decidere se subito o solo dopo un vault superato |
| P11 (b) | Un cambio strutturale della ricerca: idee fuori dal catalogo a una moneta, o la stessa regola su più monete insieme | proposta del 18 ott; decide il proprietario |
| K3 (rigioco) | Rigiocare il gruppo di controllo | raccolta accesa, rigioco mai lanciato |
| Letture mai fatte | J9/I4ter (~10 ott), K3 (15 ott), J11, J13, C1 (18 ott), F1bis (a 100 trade), I3 per strategia | dopo l'11 ott i report del mattino sono fermi per ordine del proprietario (diario 3461) e dal 13 ott la ricerca del gate è ferma |
| Piccoli trovati e non fatti | `rebuild_clean.sh` azzera le strategie su Firebase senza copia; la lettura dei numeri del `.env` con `int()` all'import può far fallire l'avvio (arch. 160-163); scarti silenziosi non simulati e nessuna pulizia di `data/gate_storia` (D8); «misurare dove sta il tempo» del giro (J10); il motore sulle coppie NON scelte negli stessi giorni (H5, arch. 604-605); il freno per gruppo dopo che il globale si spegne (I2); un tetto `max_atr_pct` a due lati (I4ter, arch. 641) | nessun numero li ha chiesti |

**Proposte strutturali per il gate, mai applicate al gate di produzione.** L'analisi dei trade del 12 ottobre
(`docs/analisi_trade_16set_12ott.md`, sezione 4, citata da P6) elenca sei cambiamenti che i dati chiedono:
(1) ogni candidata confrontata con entrate casuali con le stesse uscite; (2) una correzione per i ~27.000 tentativi a
giro (soglia di t legata al numero di prove, o Benjamini-Hochberg); (3) un fuori campione vero, usato una volta sola;
(4) costi misurati per moneta (lo scarto di prezzo è il 44% dei costi, ops 0607); (5) la stessa definizione di regime
nel gate e dal vivo (discordano nel 22-37% dei casi su ETH e SOL nei grandi movimenti, ops 0609); (6) niente figlie dai
quasi-passaggi. Le prime tre sono ciò che il protocollo di ricerca fa già; il gate di produzione non le ha mai avute.

---

## 5. Le decisioni del proprietario registrate nel backlog

Date e parole come scritte nel backlog (o nel diario che il backlog cita).

| Data | Voce | Decisione | Parole (quando registrate) |
|---|---|---|---|
| 21 set | E4 | fare tutte e tre le correzioni senza azzerare il registro | «fai 1, 2 e anche 3, ma non buttiamo via nulla» (arch. 891-892) |
| 23 set | D4, B5, B6, B7 | dati esterni rimandati a una sessione dedicata; LunarCrush tolta | (git `ee6bf270`, voce D4) |
| 24 set | D3 | sulla VPS il modello `claude-opus-4-8`, più economico | (git `3d8f20a2`) |
| 25 set | H3 | stop giornaliero parcheggiato | «non voglio limitare la quantità, voglio trade migliori» (arch. 569) |
| 25 set | F1bis | sì al paper esplorativo | il proprietario «ha detto che in paper si può rischiare di più per validare ipotesi» (arch. 540) |
| 25 set | I3 | keep scelto dal gate per coppia | «ogni dato raccolto deve arrivare al cervello e produrre una decisione» (arch. 626) |
| 25 set | B8 | intorno a 40 coppie a notte | sì del proprietario (arch. 424) |
| 26 set | I1, A4 | ridurre la size invece di rifiutare; nessun tetto sul numero di trade | «riduci la size, non rifiutare» (arch. 623) |
| 27 set | J13 | opzione (c): azzerare le coppie con la sessione oraria | (arch. 716) |
| 27 set | J11, I3 per strategia, J12 (tre azioni) | sì | (arch. 628, 700; git `8f6c139f`, voce J12) |
| 29 set | D7 | più spazio al filtro monete | «dai più spazio al filtro monete» (arch. 817) |
| 29 set | D6 | contatore della spesa AI | «aggiungi al report la spesa giornaliera di AI e per quali ragioni» (arch. 778) |
| 30 set | K1, K3, K2 | regole scritte prima, gruppo di controllo, voto t | «parti da A e C insieme, poi B» (diario 2264) |
| 30 set | A5, C2, C3, D4, I7, I8 | tolte | «aggiorna il backlog rimuovendo le scartate» (arch. 71-73) |
| 30 set | regola H1, filtro AI, ombra AI, F2, J12 | regola H1 decisa prima dei numeri; filtro e ombra spenti; F2 e J12 chiuse | «H1: ultimo esame, soglia 1,5, minimo 80: sì, filtro spegnilo tu, ombra spegnilo tu, F2 e J12 chiudile» (diario 2300-2301) |
| 1 ott | tutto il file | backlog solo con le voci aperte | «un backlog solo con quelle da fare oppure in attesa» (arch. 3); «pulisci il registro» (diario 2321) |
| 1 ott | K10, K11 | conteggio della soglia e storia delle esplorative | «procedi k10-k11 e la scritta fuorviante» (diario 2427) |
| 1 ott | I4bis | fatta | «fai i4bis» (diario 2448) |
| 1 ott | J6 | stesso periodo per rifiutati e aperti | «correggi il report» (diario 2386) |
| 1 ott | R1 | rigiocare il gate, al posto di un giro al giorno | «vai con R1»; «procedi con R1 al posto di un giro del gate al giorno» (diario 2463, 2575) |
| 1 ott | K9 | (domanda che l'ha fatta nascere) | «il sistema può solo fare modifiche per guadagnare di più?» (arch. 209) |
| 2 ott | T2 | misurare il vantaggio del segnale | «fai la misura del punto 1… la mia idea alla fine è operare più come un quant» (diario 2594) |
| 2 ott | C5, R1 | C5 dopo il 14 ott; R1 sulle 71 monete operate | «sì C5, e limita R1 alle 71 monete» (diario 2693) |
| 2 ott | D6, B8 | idee AI, autopsia e varianti dai referti spente | «se pensi che non diano valore» (diario 2731) |
| 3 ott | R2 | sì | (diario 2743) |
| 4 ott | G7 | sì | «sì G7, procedi» (diario 2776) |
| 4 ott | R1, R1b | opzione (c), fermare R1 | «fermala dopo la prova di domani» (diario 2869) |
| 4 ott | T1 | (domanda) primo incasso a 0,8 R? risposta: non prima del 14 ott, solo una colonna di misura | (bl. 376, diario 2886) |
| 6 ott | P0 | Passo 0 del protocollo | «sì alla 4.3, sì ai branch, vai col Passo 0» (diario 2922) |
| 8 ott | P1 punto 1 | la variante che batte il caso ma perde dopo i costi entra nei ritocchi | «sì» alle 10:14 UTC (bl. 204) |
| 8 ott | G8 | (domanda che l'ha fatta nascere) | «con un mercato in discesa apriamo più long che short?» (bl. 259) |
| 8 ott | P1 punto 4 | ogni sessione di campagna con Opus 5.5 e ultracode | (bl. 206-207) |
| 9 ott | P1 | versione 4.5 approvata alle 12:06 UTC; tre scelte approvate | (bl. 201) |
| 10 ott | P0 | sì alla campagna di gruppo prima del vault; no a rifare BTCUSDT | (bl. 106) |
| 10 ott | P3 | testo della campagna di gruppo approvato in anticipo | «il testo è approvato appena hai finito, parti con l'esecuzione» (git `ad3439a8`) |
| 11 ott | P4 | aprire il vault | «APRI IL VAULT» alle 17:29 UTC (git `5df4bba5`) |
| 12 ott | P5 | saltare il Passo 6, fare il Passo 7 | (bl. 101-102) |
| 13 ott | P6 | ricerca automatica del gate ferma, ordini limite nel paper, seconda edizione in bozza | «procedi con tutto» (bl. 101); prova degli ordini limite «Procedi» alle 09:13 (diario 3613) |
| 13 ott | P6 | seconda edizione approvata alle 21:34 | (bl. 101) |
| 14 ott | P6 | STOP del Passo 0: parametri congelati, regola del 10% | «procedi» alle 07:00 (bl. 101) |
| 16 ott | protocollo 3 | approvato alle 19:26 UTC | (`CLAUDE.md`) |
| 17 ott | P10 | scrivere la bozza del protocollo 4; poi approvarla alle 20:12 UTC | «ok sì, scrivi la bozza del prossimo protocollo»; «sì, approvato» (bl. 58-60) |
| 17 ott | delega | il coordinamento va avanti da solo con i passi, il vault no | 21:10 UTC (`CLAUDE.md`; `research/protocollo_4_note.md` sezione 0) |
| 18 ott | P11 | continuare finché non si trovano strategie valide, anche riscrivendo il gate; prima la storia | «la domanda non è se vuoi continuare e dobbiamo continuare fino a quando non trovi delle strategie valide... se serve riscriviamo totalmente il gate non mi interessa (prima però voglio che tu storicizzi tutti i dati raccolti, quello che abbiamo imparato, cosa abbiamo cambiato, insomma tutto dall'inizio di questo progetto ad oggi)» (~08:40 UTC, bl. 36-39) |

Due regole del proprietario che toccano tutte le voci: **niente sigle nelle risposte** (4 ott, diario 2874) e
**report del mattino fermi fino a nuovo ordine** (11 ott: «ferma del tutto i report della mattina fino a nuovo
ordine», diario 3461). La seconda ha fermato anche le letture programmate delle voci in misura.

---

## 6. Errori di metodo emersi dalle voci

Ogni punto ha la voce da cui viene e il numero che lo mostra.

**6.1 Il paper usato (o quasi) come insieme di addestramento.**
* La regola c'è dall'inizio: «Il paper FALSIFICA, non ottimizza» (oggi `bot/config.py:439`; arch. 465-467 la cita alla riga 383 di allora).
  L'esempio che l'ha fatta scrivere: BIRBUSDT, profit factor 1,51 promesso, 0,16 vissuto (arch. 29-30).
* Eppure molte funzioni imparavano dal paper: scala dei take profit dal vissuto, keep dal paper, varianti dai
  referti, pesi, leva. Le varianti dai referti si giudicavano anche sulle perdite che le avevano fatte nascere,
  perché il taglio di pre-registrazione è spento dal 24 set (B8, arch. 424). Le scale dal paper «imparano dalle uscite
  di oggi, che tagliano l'mfe» (T1, bl. 372-373). Nessuna di queste funzioni ha mostrato un contributo (sezione 2).
* Con 442 trade su 159 strategie (3 a strategia) qualunque regola imparata è rumore (analisi 12 ott, sezione 4).

**6.2 Campioni piccoli letti come segnali.**
* E1: 7 short e 0 vinte il 19 set («probabilità 1,3%», arch. 845); un mese dopo le short andavano meglio dei long
  (ops 0596).
* F1bis «contribuisce» su 10 trade il 4 ott (ops 0465), sparito su 35 (ops 0620).
* K10: 7 coppie e 11 trade (ops 0403).
* Le ipotesi dei referti scattano su 3-6 trade; su 143 referti il rumore produce +0,21 R apparenti (stima, revisione
  30 set).

**6.3 Misurare una cosa credendo di misurarne un'altra.**
* H5: il 25 set «è il mercato, non l'esecuzione» (ops 0232); il 30 set si è visto che il confronto misurava la
  selezione (−1.357 contro +8.465 sugli stessi giorni con insiemi di coppie diversi, arch. 51-57).
* G7: il «diciotto volte» fra 1 ora (2,2%) e 15 minuti (0,12%) era composizione: 259 prove su 328 a 1 ora erano
  strategie già note (ops 0468, diario 2774-2780).
* K4 e A5: le classi «stop d'ingresso / d'uscita» e «88% senza primo target» sono la forma delle regole d'uscita, non
  una diagnosi; un prezzo casuale dà gli stessi numeri (arch. 169-174).
* J8: lo strumento stampa «cresce» con −0,58% contro −0,60% (ops 0596): un verdetto senza margine.

**6.4 Confronti fra periodi o gruppi diversi.**
* J6: per quattro mattine il report ha scritto «il freno si può RITARARE» confrontando i rifiutati (dal 26 set) con
  tutti gli aperti dal 16 set, compresi i giorni del difetto della sessione (ops 0329, 0350, 0370, 0398; arch. 671-678).
* J6, 12 ott: «cooldown» +0,15 contro −0,10 «si può RITARARE» (ops 0599): i rifiutati sono a prezzo puro, gli aperti
  netti dei costi (~0,1-0,2 R di vantaggio apparente), e il margine ±0,29 non entra nella regola.
* J12: l'analisi completa del 27 sera (46% abbinati, ops 0320) mescolava trade decisi con la regola vecchia della
  sessione e quella nuova.
* Lettura del 16 ott (H5): circa 80 dei 481 trade del paper sono entrati con l'ordine limite, che il motore non
  simula (diario 3854). Il primo verdetto «è esecuzione» mescola due modi d'ingresso.

**6.5 Errori di unità e difetti degli strumenti che cambiavano il verdetto.**
* J6, 27 set: lo stop era una frazione e veniva diviso ancora per 100: R medio degli aperti −6,80 invece di −0,17
  (ops 0289). Senza la correzione la regola avrebbe dato un falso via libera ad allentare i freni (arch. 687).
* J13: la sessione oraria leggeva l'ora del processo: le validazioni di ogni strategia con quella variabile non
  avevano senso e cambiavano da un giro all'altro (arch. 706-708). 47 validate su 212 (ops 0314).
* J12: 15 trade «senza motore» erano la cache ferma a ieri (ops 0308).
* G7: 144 unità in errore per un modulo caricato due volte (ops 0485, 0502).
* H2/K7: lo «scarto 0,000» scritto d'ufficio ordinava le coppie in un modo nell'autopsia e al contrario nelle
  esplorative; l'AI lo leggeva come «esattamente al limite» (git `3d8f20a2`, voce H2).
* T2: un ingresso casuale scelto prima del segnale «conosce il futuro»: su prezzi a caso dava «peggio del caso» 100
  volte su 100 (diario 2615-2617). Corretto prima dei numeri.

**6.6 Prove multiple e conferme poco indipendenti.**
* 27.000 prove a giro con soglie assolute: ~614 passaggi attesi per caso a t = 2 (ops 0601).
* Le tre conferme settimanali condividono 38 giorni su 45 di holdout (H2, git `3d8f20a2`).
* Una coppia valutata più volte a settimana prima o poi passa: una conferma bastava con un passaggio (J11; 23 su 194
  passavano una valutazione singola, ops 0290).
* Il 70-77% delle coppie a 1-2 conferme non ripassa: «firma del massimo di un rumore selezionato» (H1, git `3d8f20a2`).
* Tre letture (3, 7, 14 ott) alzano da ~2,5% a ~7% la probabilità che almeno una suoni per caso (stima, K1).

**6.7 Soglie del gate cambiate da una macchina senza memoria.**
* K10: il supervisore automatico ha portato la soglia del win rate da 0,45 a 0,3966 fra il 19 ago e l'8 set e non l'ha
  più rimessa (arch. 219-223). In più un «backlog.md» precedente diceva che il supervisore regolava
  `DECISION_THRESHOLD`: era sbagliato (arch. 226).
* K9: la leva torna piena dopo 1 vincita su 1 (arch. 210-212): «fortuna amplificata».

**6.8 Regole che non possono distinguere.**
* K6: l'uscita del freno chiede 1,05 R di massimo toccato mediano; il motore che guadagna è a 1,03 R e un prezzo
  casuale a 0,81 R (arch. 183-186).
* I2: il freno per gruppo suonava dopo il globale in 6 gruppi su 7 (ops 0288).
* I9: una soglia che oscilla attorno al 60% cambia le scelte delle coppie non ancora validate (29 set: 59,7%, ops 0345).
* H2: «PF ≥ 1,05 e ritorno > 0» resta quasi testa o croce per una strategia senza vantaggio, a qualunque numero di
  trade (stima, git `3d8f20a2`).
* T2: su prezzi a caso la regola dice «nessun vantaggio» solo 75-81 volte su 100 (stima, diario 2618), e non dice
  quanto piccolo potrebbe essere un vantaggio vero (±0,5% a 4 ore).

**6.9 Metri scritti e poi non applicati, o letture mai fatte.**
* B8: l'intorno a 40 aveva il metro «se il giro sfora le 2 ore si torna a 10» (arch. 424); il giro completo ha fatto 2h58-3h28
  (ops 0391, 0501, 0520; un giro urgente 4h18, ops 0586) e nel codice il tetto è ancora 40 (`scripts/discover_strategies.py:1540`). Non
  verificato se il `.env` della VPS lo cambiasse.
* J10: «se resta sopra le 2 ore, misurare dove sta il tempo» (arch. 694): non trovato.
* Letture programmate e mai fatte: J9/I4ter, K3, J11, J13, C1, F1bis a 100 trade, I3 per strategia (sezione 4).
* A4: la domanda «quanto vive una strategia validata?» non ha mai avuto il suo numero.

**6.10 Il backlog non aggiornato.**
* G3 dice «a metà novembre» (bl. 380-383) ma la regola H1 l'ha già chiusa il 12 e il 16 ott (ops 0600, 0619).
* P8 e P9 sono «Aspettano il tuo sì» ma il protocollo 4 le ha già messe in pratica (`research/PROTOCOLLO_4.md` righe 174,
  452, 693).
* J2 è «in lavorazione» (bl. 154), ma è fatta dal 1 ott (diario 2538-2550). G7, R1, R2, T2 sono nel gruppo «In
  lavorazione» ma sono fatte o fermate.
* Il gruppo 2 dice «dopo le letture del 7-14 ott»: le letture ci sono state (ops 0532, 0619), ma nessuna voce è stata
  ripresa perché nel frattempo il gate si è fermato.
* P6 cita −108,25 USDT su 459 trade per ops 0584; ops 0584 stampa 458 trade e −109,19 (vedi elenco delle incertezze).

**6.11 Numeri scritti senza base e poi corretti (dal backlog stesso).**
* H5, 30 set: «troppo grande per essere solo quello», scritto senza base e corretto (arch. 56).
* I5, 30 set: «peggiorata» invece che «in calo» (arch. 58-61).
* K5: la scritta «size ridotta» nel controllo non era vera con stop stretti; «le declassate pesano otto volte meno»
  era sbagliata (`docs/revisione_sospese_30set.md` riga 91).
* R1: stima di 13-17 ore, poi ~45,8 ore rimaste stimate dal tempo misurato a unità (ops 0433): il piano aveva 200 monete invece di 120-150.
* D6: il costo era «stima dai log, non dalla fattura» finché non è arrivato il contatore (arch. 780).

**6.12 La lezione più grande, detta dalle voci stesse.**
Quasi tutte le voci del backlog (serie A, H, I, J, K, T) lavorano su uscite, size, freni e misure del paper. Le
misure del 2-16 ottobre dicono che non sono leve: il lordo prima dei costi è ~0 (−0,015 R su 442 trade, ops 0596), i
costi sono ~0,09 R a trade (ops 0620), e la scelta del gate non regge fuori campione (ops 0532, 0619). «Le uscite si
possono rendere più coerenti; non possono creare un vantaggio che all'ingresso non c'è»
(`docs/analisi_trade_16set_12ott.md`, sezione 2.3). Il collo di bottiglia è l'informazione all'ingresso più i costi.

---

## Appendice A. Prima e ultima comparsa di ogni sigla in `docs/backlog.md`

Formato: sigla prima → ultima (commit, data). Le voci che arrivano a `672663b8` (18 ott) sono ancora nel file.
Ricavato leggendo ogni versione del file con `git show <hash>:docs/backlog.md`.

A1, A2, A3, B1, B2, B3, B4, D2, D3, E2, E3: `f0ac205f` 20 set → `3d8f20a2` 30 set · B2bis `32c50254` 20 set →
`3d8f20a2` · A4 `57ff082c` 21 set → `e75f9915` 1 ott · A5 `9003e811` 24 set → `ee6bf270` 30 set · B5 `f0ac205f`
20 set → `672663b8` · B6, B7, C4 `b393642a` 20 set → `672663b8` · B8 `0bc2d6d7` 21 set → `672663b8` · C1, E1
`f0ac205f` → `e75f9915` · C2, C3, D4 `f0ac205f` → `ee6bf270` · C5 `bbbdb2fa` 2 ott → `672663b8` · D1 `f0ac205f`
→ `672663b8` · D5 `b2e9e9d4` 28 set → `e75f9915` · D6 `ca878b11` 29 set → `672663b8` · D7 `6ae4c6a7` 29 set →
`e75f9915` · D8 `5e7522bc` 1 ott → `672663b8` · E4 `ba32eaa8` 21 set → `672663b8` · F1 `3368b238` 23 set →
`3d8f20a2` · F1bis, F1ter, I4bis `ae309d1c` 25 set → `e75f9915` · F2 `e26682a5` 23 set → `8f6c139f` 30 set ·
G1, G2, G4, G5 `3c8a2527` 24 set → `3d8f20a2` · G3 `3c8a2527` → `672663b8` · G6 `eb0b992d` 24 set → `672663b8` ·
G7 `f8c3fd92` 4 ott → `672663b8` · G8 `298be7b4` 8 ott → `672663b8` · H1, H2 `eb0b992d` → `3d8f20a2` · H3, H4
`eb0b992d` → `672663b8` · H5 `eb0b992d` → `e75f9915` · I1, I3, I4 `767d5529` 25 set → `e75f9915` · I2 `767d5529`
→ `3d8f20a2` · I4ter `3b851fe7` 26 set → `e75f9915` · I5, I6 `767d5529` → `672663b8` · I7, I8 `6ae4c6a7` 29 set →
`ee6bf270` · I9 `6ae4c6a7` → `3d8f20a2` · J1, J3, J4, J5 `425d8086` 25 set → `cff0caea` 1 ott · J2 `425d8086` →
`672663b8` · J6, J7, J8, J9 `0fa6c6d2` 26 set → `e75f9915` · J10 `579109fa` 26 set → `e75f9915` · J11 `aa6b89e5`
27 set → `e75f9915` · J12 `169945f7` 27 set → `8f6c139f` · J13 `6a846de4` 27 set → `e75f9915` · J14 `76ffb8d0`
28 set → `e75f9915` · J15 `6ae4c6a7` → `e75f9915` · K1, K2, K3, K7 `cadaa136` 30 set → `e75f9915` · K4, K5, K6,
K8 `cadaa136` → `672663b8` · K9, K10 `5d0bad5f` 1 ott → `672663b8` · K11 `d80054b6` 1 ott → `e75f9915` · P0
`58af4a2d` 5 ott → `672663b8` · P1 `8c97e1b1` 8 ott → `672663b8` · P2 `1f1682b5` 10 ott → `672663b8` · P3
`1f1682b5` → `ad3439a8` 11 ott · P4 `98add7fb` 11 ott (una sola versione) · P5 `5df4bba5` 11 ott (una sola) · P6
`76c104e0` 12 ott → `672663b8` · P7 `6efc005f` 16 ott → `672663b8` · P8 `e4576261` 17 ott → `672663b8` · P9
`22c756d5` 17 ott → `672663b8` · P10 `09795c2d` 17 ott → `672663b8` · P11 `f85a233a` 18 ott → `672663b8` · R1
`8d241733` 1 ott → `672663b8` · R1b `0dc9e382` 4 ott (una sola) · R2 `e3df041d` 3 ott → `672663b8` · T1 `376fbcd6`
2 ott → `672663b8` · T2 `e62534e7` 2 ott → `672663b8`.

Nota: le voci uscite da `docs/backlog.md` il 1 ott alle 09:52 (`e75f9915`) sono passate in `docs/backlog_archivio.md`
con il commit successivo `8d241733`; quelle uscite prima (`3d8f20a2`, `ee6bf270`, `8f6c139f`, `cff0caea`) esistono
solo nella storia di git e nel diario.
