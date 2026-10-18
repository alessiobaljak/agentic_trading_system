# Ipotesi della campagna LINK6 (protocollo 4, Fase 1)

Scritte prima di qualunque test. Ogni idea ha: fonte (pubblicata prima del 2024-01-01), affermazione verificabile,
sotto-domande, almeno 10 spiegazioni concorrenti con la previsione di ciascuna e cosa la smentirebbe, le varianti
scritte per intero con il motivo di ogni scelta, e la stima dei trade (8.4) sul periodo di costruzione.

Regola 7: nessuna di queste idee e' scelta perche' so che abbia funzionato dal 2024 in poi; sono le famiglie
classiche della letteratura e del catalogo. La costruzione di LINKUSDT e' gia' stata esplorata da un protocollo
precedente (sezione 15): non ne conosco le varianti; se qualcuna coincide, conta come idea gia' provata su questi dati.

Le stime dei trade le ha calcolate `codice/stima.py` (solo conteggi) il 18 ottobre 2026; le bozze provate per la stima
sono in `codice/bozze_stima_1.json` e `codice/bozze_stima_2.json`.

Le previsioni sono a priori e prudenti: per la sezione 8.3 la maggior parte delle varianti non deve superare la Fase 2.

---

## I-01 — Rottura di un canale in tendenza (momentum di serie temporale)

**Fonte.** T. J. Moskowitz, Y. H. Ooi, L. H. Pedersen, «Time Series Momentum», *Journal of Financial Economics*,
2012. Y. Liu, A. Tsyvinski, «Risks and Returns of Cryptocurrency», *Review of Financial Studies*, 2021 (prima come
documento di lavoro NBER, 2018): nelle criptovalute il rendimento recente predice quello dei giorni successivi. Regola
della rottura del canale: C. Faith, *Way of the Turtle*, McGraw-Hill, 2007 (rottura del massimo di 55 periodi).

**Affermazione verificabile.** Su LINKUSDT, quando la chiusura supera il massimo delle 55 candele orarie precedenti
mentre il prezzo e' sopra la sua EMA a 200 ore, il prezzo nelle ore e nei giorni dopo tende a proseguire nella stessa
direzione abbastanza da pagare i costi: un trailing stop a 3 ATR cattura in media almeno 0,2 R per trade dopo i costi,
piu' di entrate casuali con le stesse uscite. Simmetrico per lo short sotto la EMA a 200. Si smentisce se l'R medio
non supera le entrate casuali (p-value sopra 0,023) o resta sotto 0,2 R.

**Sotto-domande.** In quali condizioni: tendenze di giorni, volatilita' in aumento dopo la rottura. Chi opera: chi
segue la tendenza, chi ha stop sopra i massimi recenti (short che chiudono), chi entra tardi per notizie. Perche'
muoverebbe il prezzo: ordini di stop e di rottura concentrati sopra i massimi, aggiustamento lento all'informazione.
Quando e in quanto tempo: da poche ore a qualche giorno; il trailing lascia correre.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentirebbe |
|---|---|---|---|
| 1 | Caso | R medio vicino a quello delle entrate casuali, p-value uniforme | p-value molto piccolo e stabile nei blocchi |
| 2 | Tendenza di fondo 2020-2021 (rialzo) | il long guadagna solo nel 2020-2021, lo short perde li' e guadagna solo nel 2022 | guadagno anche nei blocchi di direzione opposta |
| 3 | Volatilita': le rotture capitano quando la volatilita' sale, e il trailing guadagna piu' R con movimenti ampi | anche entrate casuali in periodi agitati guadagnano | il segnale batte entrate casuali con la stessa larghezza dello stop |
| 4 | Costi: troppi trade brevi fermati subito | R lordo positivo ma netto negativo; peggiora molto a costi doppi | R positivo anche a costi doppi |
| 5 | Pochi trade enormi (maggio 2021, marzo 2020) | togliendo il 5% migliore il vantaggio sparisce | verifica 4 superata |
| 6 | Falsa rottura (caccia agli stop): il prezzo supera il massimo e torna indietro | molte uscite per stop subito dopo l'ingresso, R medio negativo | prosecuzione media dopo la rottura |
| 7 | Filtro EMA200 che fa da solo il lavoro (essere long in tendenza) | entrate casuali con lo stesso filtro andrebbero bene quanto il segnale; qui le casuali non hanno il filtro, quindi il p-value puo' sembrare migliore per merito del filtro | — (limite noto: si guarda il blocco per blocco) |
| 8 | Artefatto dei dati: candele anomale (marzo 2020) | risultati concentrati in pochi giorni anomali | risultato stabile togliendo quei giorni (verifica 4 e blocchi) |
| 9 | Salti di prezzo che fanno uscire oltre lo stop | perdite medie peggiori di −1 R | perdite medie vicine a −1 R |
| 10 | Effetto del mercato crypto intero (BTC trascina LINK) e non di LINK | vale anche sulle monete di controllo (verifica 12) | — (in questo caso e' un vantaggio generale, cio' che il protocollo cerca) |
| 11 | Momento della giornata: le rotture capitano all'apertura degli Stati Uniti | concentrazione oraria degli ingressi | ingressi distribuiti nelle ore |

**Varianti.**

> **V-001** · 1h · long · filtro F1: chiusura sopra EMA(200) · ingresso E3: rottura di Donchian a 55 · conferma
> nessuna · tipo M · stop S1: 2 × ATR(14) · uscita U3: trailing a 3 × ATR(14).
>
> **V-002** · stessa, short: filtro F1 chiusura sotto EMA(200), rottura del minimo di 55 candele, stop e trailing
> simmetrici.

Motivi: 1h perche' a 4h la rottura a 20 dava solo 65-66 trade (bozze B-01, B-02), sotto i minimi; a 1h il canale a 55
ore (circa 2,3 giorni) da' abbastanza segnali. EMA(200) a 1h (circa 8 giorni) come direzione di fondo. Stop a 2 ATR per
non uscire per il rumore della candela di rottura; trailing a 3 ATR, l'uscita classica dei sistemi di tendenza, che
lascia correre i guadagni; nessun target, che taglierebbe le code su cui vive l'idea. Nessuna conferma: una condizione
in meno. Stima: V-001 228 trade, V-002 182 trade.

**Previsione.** R medio fra −0,1 e +0,2 R; p-value sopra 0,05 per entrambe. Il long piu' probabilmente positivo nel
2020-2021, lo short nel 2022.

---

## I-02 — Funding estremo: posizioni con leva affollate da un lato

**Fonte.** S. He, A. Manela, O. Ross, V. von Wachter, «Fundamentals of Perpetual Futures», documento di lavoro (arXiv),
dicembre 2022: il funding misura lo scarto fra il prezzo del perpetuo e quello a pronti, cioe' la domanda di leva da un
lato del mercato. L'uso contrarian (un funding molto alto annuncia un ribasso, uno negativo un rialzo) e' una mia
inferenza da quel meccanismo, non un risultato dell'articolo.

**Affermazione verificabile.** Su LINKUSDT, alla prima candela oraria dopo un regolamento con funding sopra +0,05%
per 8 ore, il prezzo nelle 24 ore successive scende abbastanza da dare almeno 0,2 R per trade dopo i costi a uno short
con stop a 2 ATR, target a 2 R e uscita dopo 24 candele, piu' di entrate casuali con le stesse uscite. Simmetrico:
dopo un funding negativo (sotto 0,00%) il prezzo sale. Si smentisce se l'R medio non supera le casuali o resta sotto
0,2 R.

**Sotto-domande.** In quali condizioni: rialzi rapidi con molta leva in acquisto (funding alto) o ribassi con molti
short (funding negativo). Chi opera: speculatori con leva da un lato, arbitraggisti che vendono il perpetuo e comprano
a pronti incassando il funding. Perche' il prezzo dovrebbe muoversi contro la folla: chiusure forzate e liquidazioni
quando il movimento si ferma; l'arbitraggio riporta il perpetuo verso il pronti. Quando: nelle ore successive al
regolamento, entro un giorno.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentirebbe |
|---|---|---|---|
| 1 | Caso | nessuna differenza dalle casuali | p-value piccolo |
| 2 | Il funding alto segnala forza, non eccesso (momentum): il prezzo continua a salire | lo short perde, piu' delle casuali | lo short batte le casuali |
| 3 | Tendenza di fondo: il funding alto capita nel rialzo 2020-2021, quindi lo short perde per la tendenza | perdite concentrate nel 2021 | guadagni anche nel 2021 |
| 4 | Il segnale e' solo il riflesso di un movimento gia' avvenuto (ritorno verso la media di breve) | stesso effetto con un ingresso su qualunque forte rialzo | — (indistinguibile qui; informativo) |
| 5 | Costi del funding: lo short incassa il funding alto, che da solo sembra un vantaggio | R positivo piccolo, quasi tutto dal funding | vantaggio molto piu' grande del funding incassato (circa 0,05% a regolamento) |
| 6 | Volatilita' alta dopo funding estremo: le uscite a 2 R scattano piu' spesso in entrambe le direzioni | casuali in periodi agitati simili | il segnale batte le casuali con la stessa larghezza dello stop |
| 7 | Pochi episodi di crollo (maggio 2021) | vantaggio sparisce senza il 5% migliore | verifica 4 superata |
| 8 | Segnali raggruppati: tanti regolamenti consecutivi sopra soglia nello stesso episodio, non prove indipendenti | trade concentrati in poche settimane | trade distribuiti nel tempo |
| 9 | Artefatto: il tasso dei file e' quello regolato, noto solo dopo il regolamento; nessun anticipo se il motore lo usa dopo | — (il motore usa la prima candela dopo il regolamento: nessun anticipo) | test di troncamento fallito |
| 10 | Effetto generale del mercato con leva, non solo di LINK | vale sulle monete di controllo | non vale altrove |
| 11 | Funding negativo raro e in mercati gia' crollati: il long rimbalza per il ritorno di breve, non per il funding | effetto uguale a un rimbalzo dopo forte ribasso | — (informativo) |

**Varianti.**

> **V-003** · 1h · short · nessun filtro · ingresso E11: funding sopra +0,05% (soglia alta del catalogo) · conferma
> nessuna · tipo M · stop S1: 2 × ATR(14) · uscite U1: target 2 R, U2: dopo 24 candele.
>
> **V-004** · 1h · long · nessun filtro · ingresso E11: funding sotto 0,00% · conferma nessuna · tipo M · stop S1:
> 2 × ATR(14) · uscite U1: target 2 R, U2: dopo 24 candele.

Motivi: 1h perche' il segnale nasce a un istante preciso (il regolamento) e l'effetto atteso dura ore, non giorni;
24 candele = un giorno, tre regolamenti. Soglia +0,05% (cinque volte il tasso normale dello 0,01%) per prendere solo
gli eccessi veri; con +0,03% i trade sarebbero di piu' (285, bozza B-05) ma il segnale meno estremo. Per il long la
soglia −0,01% dava 100 trade (bozza B-06), sotto i minimi: si usa 0,00%. Stop a 2 ATR perche' dopo un funding estremo
la volatilita' e' alta. Target a 2 R. Stima: V-003 202 trade, V-004 174 trade.

**Previsione.** V-003: R medio fra −0,15 e +0,15 R, p-value sopra 0,05 (la spiegazione 2 mi sembra forte quanto
l'ipotesi). V-004: R medio fra −0,1 e +0,2 R, p-value sopra 0,05.

---

## I-03 — Rottura del range asiatico all'apertura europea

**Fonte.** T. Eross, F. McGroarty, A. Urquhart, S. Wolfe, «The intraday dynamics of bitcoin», *Research in
International Business and Finance*, 2019: volumi e volatilita' di bitcoin hanno un andamento giornaliero, con picchi
nelle ore europee e statunitensi. L. Gao, Y. Han, S. Z. Li, G. Zhou, «Market intraday momentum», *Journal of Financial
Economics*, 2018: il rendimento della prima parte della giornata predice quello dell'ultima. La regola del range
asiatico e' un'applicazione pratica di queste due osservazioni (esempio V-012 della sezione 7.9 del protocollo).

**Affermazione verificabile.** Su LINKUSDT, la prima chiusura oraria fra le 08:00 e le 16:00 UTC oltre il massimo
(o il minimo) delle candele fra le 00:00 e le 08:00 dello stesso giorno annuncia un movimento nella stessa direzione
che, con stop al minimo (massimo) delle ultime 5 candele, target a 2 R e uscita alle 21:00 UTC, da' almeno 0,2 R per
trade dopo i costi, piu' delle casuali. Si smentisce come le altre.

**Sotto-domande.** Condizioni: notti asiatiche tranquille seguite da volumi europei; giorni feriali piu' dei fine
settimana. Chi opera: operatori europei e statunitensi che arrivano con informazioni nuove; stop accumulati sopra e
sotto il range notturno. Perche' il prezzo proseguirebbe: la rottura scatta ordini di stop e di ingresso. Quando:
nelle ore di Europa e Stati Uniti, entro la sera UTC.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentirebbe |
|---|---|---|---|
| 1 | Caso | come le casuali | p-value piccolo |
| 2 | Il mercato crypto e' aperto 24 ore: la notte asiatica non e' "chiusa", il range non e' speciale | rotture non migliori di entrate casuali nelle stesse ore | vantaggio sulle casuali |
| 3 | Le casuali entrano in tutte le ore, il segnale solo in quelle europee: la differenza e' l'ora, non la rottura | vantaggio presente ma uguale per qualunque ingresso nelle ore europee | — (limite: le casuali non sono condizionate all'ora) |
| 4 | Falsa rottura e ritorno nel range | molti stop, R medio negativo | prosecuzione media |
| 5 | Tendenza di fondo | long buono nel 2020-2021, short nel 2022 | buono nei blocchi opposti |
| 6 | Costi: stop stretti (minimo di 5 candele orarie) gonfiano i costi in R | R lordo positivo e netto negativo; costi doppi molto peggio | positivo a costi doppi |
| 7 | Volatilita' giornaliera: nei giorni agitati il range si rompe e il target si tocca, in entrambi i sensi | casuali con stessa larghezza dello stop simili | il segnale le batte |
| 8 | Effetto giorno della settimana (fine settimana diversi) | risultati diversi fra feriali e festivi | uguali |
| 9 | Pochi giorni estremi | verifica 4 fallisce | superata |
| 10 | Artefatto orario: candele di manutenzione (volume zero il 2 marzo 2021) | trascurabile | — |
| 11 | Uscita alle 21:00 troppo presto: il vantaggio, se c'e', e' nelle ore dopo | R medio piccolo, uscite a tempo con R positivo | — (informativo) |

**Varianti.**

> **V-005** · 1h · long · nessun filtro · ingresso E10: rottura del massimo del range asiatico · conferma nessuna ·
> tipo M · stop S2: minimo delle ultime 5 candele · uscite U1: target 2 R, U2s: uscita alle 21:00 UTC.
>
> **V-006** · stessa, short: rottura del minimo del range asiatico, stop al massimo delle ultime 5 candele.

Motivi: 1h, il timeframe piu' lungo ammesso per E10, per avere meno rumore e meno costi in R che a 15m o 30m. Stop S2
a 5 candele: sotto la struttura delle ultime ore, piu' stretto di un ATR di molte ore. Target 2 R e uscita a fine
giornata: l'ipotesi riguarda la giornata, non i giorni dopo. Nessun filtro di tendenza: si prova la rottura da sola
(l'esempio V-012 del protocollo ha anche filtro e conferma; qui si parte dalla forma piu' semplice). Stima: V-005 412
trade, V-006 344 trade.

**Previsione.** R medio fra −0,15 e +0,1 R per entrambe, p-value sopra 0,05. Mi aspetto la spiegazione 2.

---

## I-04 — Candela con volume anomalo: prosecuzione nella direzione della candela

**Fonte.** S. Gervais, R. Kaniel, D. H. Mingelgrin, «The High-Volume Return Premium», *Journal of Finance*, 2001: le
azioni con un volume insolitamente alto in un giorno o in una settimana tendono a salire nel mese dopo (l'attenzione
attira compratori). L'adattamento a candele di 2 ore e a entrambe le direzioni, con la direzione della candela, e' mio:
un volume anomalo in una candela rialzista indica domanda nuova e informata che non si esaurisce subito; in una candela
ribassista, vendite informate o forzate.

**Affermazione verificabile.** Su LINKUSDT a 2 ore, una candela con volume almeno doppio della media delle 20
precedenti e chiusura sopra l'apertura e' seguita da un rialzo che, con stop a 1,5 ATR, target a 2 R e uscita dopo 6
candele (12 ore), da' almeno 0,2 R dopo i costi, piu' delle casuali. Simmetrico per lo short.

**Sotto-domande.** Condizioni: notizie, liste su nuove piattaforme, liquidazioni a catena. Chi opera: chi ha
informazioni, chi viene liquidato, chi segue il movimento. Perche' il prezzo proseguirebbe: l'informazione si diffonde
in ore; oppure si invertirebbe se il volume e' una liquidazione esaurita. Quando: nelle 12 ore successive.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentirebbe |
|---|---|---|---|
| 1 | Caso | come le casuali | p-value piccolo |
| 2 | Esaurimento: il volume anomalo segna la fine del movimento (capitolazione o euforia) | R medio negativo, inversione | prosecuzione |
| 3 | Volatilita': il volume alto viene con candele grandi, ATR alto, stop larghi | casuali con stessa larghezza simili | il segnale le batte |
| 4 | Tendenza di fondo | long nel 2020-2021, short nel 2022 | buono nei blocchi opposti |
| 5 | Liquidazioni a catena (marzo 2020, maggio 2021) | risultato in pochi giorni | verifica 4 superata |
| 6 | Effetto del mercato intero (tutte le crypto con volume alto insieme) | vale sulle monete di controllo | non vale |
| 7 | Volume relativo alto solo per una candela di volume basso prima (fine settimana) | segnali concentrati il lunedi' | distribuiti |
| 8 | Costi | R lordo positivo, netto negativo | positivo a costi doppi |
| 9 | Ingresso in ritardo: il movimento avviene dentro la candela del segnale e dopo non resta niente | R medio vicino a zero meno i costi | R positivo dopo i costi |
| 10 | Salti di prezzo all'apertura successiva | uscite oltre lo stop | perdite medie vicine a −1 R |
| 11 | Effetto dell'ora del giorno (volume alto all'apertura USA) | concentrazione oraria | distribuzione oraria ampia |

**Varianti.**

> **V-007** · 2h · long · nessun filtro · ingresso E12: volume relativo sopra 2,0 e chiusura sopra l'apertura ·
> conferma nessuna · tipo M · stop S1: 1,5 × ATR(14) · uscite U1: target 2 R, U2: dopo 6 candele.
>
> **V-008** · stessa, short: volume relativo sopra 2,0 e chiusura sotto l'apertura.

Motivi: a 4h il long dava 145 trade (bozza B-10), sotto i minimi; 2h e' il timeframe successivo verso il basso, ancora
abbastanza lungo perche' "volume anomalo" voglia dire un evento e non un minuto agitato. Soglia 2,0 (la piu' alta) per
prendere solo volumi veramente anomali. Uscita dopo 6 candele (12 ore): l'ipotesi parla di ore. Stop 1,5 ATR, target
2 R. Stima: V-007 312 trade, V-008 339 trade.

**Previsione.** R medio fra −0,15 e +0,1 R, p-value sopra 0,05 per entrambe.

---

## I-05 — Ritorno dentro le bande di Bollinger in un mercato laterale

**Fonte.** J. Bollinger, *Bollinger on Bollinger Bands*, McGraw-Hill, 2001: in un mercato senza tendenza le chiusure
fuori dalle bande tendono a rientrare. J. W. Wilder, *New Concepts in Technical Trading Systems*, Trend Research,
1978: l'ADX sotto 20 indica un mercato senza tendenza.

**Affermazione verificabile.** Su LINKUSDT a 30 minuti, con ADX(14) sotto 20, quando una candela chiude di nuovo
dentro le bande (k = 2,0) dopo una chiusura sotto la banda inferiore, il prezzo risale verso la media abbastanza da dare,
con stop a 1,5 ATR, target a 1,5 R e uscita dopo 12 candele (6 ore), almeno 0,2 R dopo i costi, piu' delle casuali.
Simmetrico per lo short dalla banda superiore.

**Sotto-domande.** Condizioni: mercato laterale (ADX basso), volatilita' bassa o media. Chi opera: chi fornisce
liquidita' e compra gli eccessi, chi vende e poi ricompra. Perche' il prezzo tornerebbe: in assenza di informazione
nuova gli eccessi di breve sono rumore che si riassorbe. Quando: in poche ore.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentirebbe |
|---|---|---|---|
| 1 | Caso | come le casuali | p-value piccolo |
| 2 | L'ADX e' in ritardo: quando dice "laterale" la tendenza puo' gia' essere partita, e il rientro e' una pausa | molte uscite per stop | target frequenti |
| 3 | Costi a 30 minuti: il movimento atteso e' dello stesso ordine dei costi | R lordo positivo, netto negativo; costi doppi molto peggio | positivo a costi doppi |
| 4 | Tendenza di fondo | long nel 2020-2021, short nel 2022 | buono nei blocchi opposti |
| 5 | Volatilita': stop stretti in mercati calmi, molto rumore | casuali con stessa larghezza simili | il segnale le batte |
| 6 | Il rientro avviene gia' nella candela del segnale: dopo non resta niente | R medio vicino a zero meno i costi | positivo |
| 7 | Effetto dell'ora (notte asiatica piu' laterale) | concentrazione oraria | distribuiti |
| 8 | Pochi trade estremi | verifica 4 fallisce | superata |
| 9 | Raggruppamento: piu' segnali nello stesso episodio | trade concentrati | distribuiti |
| 10 | Generale fra le monete grandi (microstruttura comune) | vale sulle monete di controllo | non vale |
| 11 | Target a 1,5 R troppo lontano per un ritorno alla media | molte uscite a tempo con R piccolo | target frequenti |

**Varianti.**

> **V-009** · 30m · long · filtro F2: ADX(14) sotto 20 · ingresso E5: ritorno da Bollinger (20, 2,0) dalla banda
> inferiore · conferma nessuna · tipo M · stop S1: 1,5 × ATR(14) · uscite U1: target 1,5 R, U2: dopo 12 candele.
>
> **V-010** · stessa, short: ritorno dalla banda superiore.

Motivi: a 1h con il filtro ADX il long dava 143 trade (bozza B-13), sotto i minimi; senza il filtro i trade erano
quasi 700 (bozza B-20), ma l'ipotesi riguarda proprio il mercato laterale: si scende a 30m tenendo il filtro. k = 2,0
(piu' segnali di 2,5). Target vicino (1,5 R) e uscita dopo 6 ore: il ritorno alla media e' un effetto breve. Stima:
V-009 315 trade, V-010 327 trade.

**Previsione.** R medio fra −0,2 e +0,05 R per entrambe (a 30 minuti i costi pesano), p-value sopra 0,05.

---

## I-06 — Rottura dopo la compressione della volatilita'

**Fonte.** J. Bollinger, *Bollinger on Bollinger Bands*, McGraw-Hill, 2001 (lo «squeeze»: a periodi di volatilita'
bassa seguono periodi di volatilita' alta, e la prima rottura delle bande ne indica spesso la direzione). R. F. Engle,
«Autoregressive Conditional Heteroscedasticity with Estimates of the Variance of United Kingdom Inflation»,
*Econometrica*, 1982: la volatilita' si raggruppa nel tempo.

**Affermazione verificabile.** Su LINKUSDT a 1 ora, con l'ATR percentile sotto il 30° (volatilita' bassa rispetto
alle 500 ore precedenti), una chiusura sopra la banda di Bollinger superiore (k = 2,0) annuncia un movimento al
rialzo che, con stop a 2 ATR e trailing a 2 ATR, da' almeno 0,2 R dopo i costi, piu' delle casuali. Simmetrico per lo
short sotto la banda inferiore.

**Sotto-domande.** Condizioni: settimane calme seguite da notizie o da rotture tecniche. Chi opera: chi vende
volatilita' e viene sorpreso, chi aspetta la rottura. Perche' il prezzo proseguirebbe: il passaggio dalla calma
all'agitazione porta flussi nuovi in una direzione. Quando: ore o giorni dopo la rottura.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentirebbe |
|---|---|---|---|
| 1 | Caso | come le casuali | p-value piccolo |
| 2 | La volatilita' torna alta ma senza direzione: la rottura non dice da che parte | stop e trailing in pari | vantaggio direzionale sulle casuali |
| 3 | Stop stretti in volatilita' bassa: il trade e' solo piu' grande in R, per costi minori, e le casuali lo correggono con la stessa larghezza | vantaggio sparisce con le casuali | resta |
| 4 | Falsa rottura | molti stop | prosecuzione |
| 5 | Tendenza di fondo | long nel 2020-2021, short nel 2022 | buono nei blocchi opposti |
| 6 | Pochi movimenti enormi dopo la calma (marzo 2020, maggio 2021) | verifica 4 fallisce | superata |
| 7 | Costi | R lordo positivo, netto negativo | positivo a costi doppi |
| 8 | Raggruppamento di segnali | trade concentrati | distribuiti |
| 9 | Effetto del fine settimana (volatilita' bassa il sabato) | segnali concentrati nei fine settimana | distribuiti |
| 10 | Generale fra le monete grandi | vale sulle monete di controllo | non vale |
| 11 | Il trailing a 2 ATR esce troppo presto per catturare la tendenza | molte uscite piccole positive | — (informativo) |

**Varianti.**

> **V-011** · 1h · long · filtro F3: ATR percentile sotto il 30° · ingresso E4: chiusura sopra la banda superiore
> (20, 2,0) · conferma nessuna · tipo M · stop S1: 2 × ATR(14) · uscita U3: trailing a 2 × ATR(14).
>
> **V-012** · stessa, short: chiusura sotto la banda inferiore.

Motivi: 1h perche' la finestra di 500 candele dell'ATR percentile copre circa tre settimane, l'orizzonte di una
"compressione"; a 4h coprirebbe quasi tre mesi. k = 2,0 per piu' segnali. Stop a 2 ATR: con l'ATR basso uno stop a
1 ATR sarebbe vicino al limite dello 0,3%. Trailing a 2 ATR (il piu' stretto) perche' i movimenti dopo la compressione
possono rientrare. Stima: V-011 212 trade, V-012 160 trade.

**Previsione.** R medio fra −0,15 e +0,15 R per entrambe, p-value sopra 0,05.

---

# Secondo lotto (scritto il 18 ottobre 2026, dopo i risultati del lotto 1)

Dichiarazione (Fase 3, punto 3, e regola 5). Queste idee sono scritte dopo i risultati di V-001 ... V-012. Nessuna
differisce da una variante gia' provata per un solo elemento: I-07 differisce da V-009 e V-010 per timeframe, filtro,
valore di k e tipo di ingresso; I-08 da V-001 e V-002 per filtro e ingresso; I-09 da V-001 e V-002 per timeframe,
ingresso e uscite. Che cosa ho preso dal lotto 1: solo la conferma che a 30 minuti i costi pesano circa il doppio in R
che a 1 ora (0,085 contro 0,04 R, `codice/fase3_analisi.py`), fatto gia' scritto nella sezione 15 del protocollo;
nessuna scelta di ora, giorno o soglia viene dai risultati.

## I-07 — Fornire liquidita' dopo un eccesso: ingresso con ordine limit

**Fonte.** S. Nagel, «Evaporating Liquidity», *Review of Financial Studies*, 2012: i rendimenti dell'inversione di
breve periodo sono in gran parte il compenso di chi fornisce liquidita' a chi ha fretta di vendere o comprare, e sono
piu' alti quando la volatilita' e' alta. Bande di Bollinger: J. Bollinger, 2001 (come I-05).

**Affermazione verificabile.** Su LINKUSDT a 1 ora, dopo una chiusura fuori dalla banda di Bollinger a 2,5 deviazioni
e il ritorno dentro alla candela successiva, un ordine limit di acquisto 0,5 ATR sotto la chiusura (valido 3 candele)
compra da chi vende in fretta a un prezzo migliore; con stop a 1,5 ATR, target a 1,5 R e uscita dopo 12 candele il
risultato e' di almeno 0,2 R dopo i costi, piu' delle casuali con lo stesso ordine limit. Simmetrico per lo short.

**Sotto-domande.** Condizioni: volatilita' alta, liquidazioni, venditori forzati. Chi opera: chi deve chiudere
posizioni (margine, liquidazioni), chi fornisce liquidita'. Perche' il prezzo tornerebbe: la pressione di chi ha fretta
e' temporanea. Quando: entro qualche ora.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentirebbe |
|---|---|---|---|
| 1 | Caso | come le casuali | p-value piccolo |
| 2 | Selezione avversa del limit: l'ordine si esegue soprattutto quando il prezzo continua a scendere (informazione vera) | trade eseguiti peggiori di quelli non eseguiti; R negativo | R positivo |
| 3 | Il vantaggio e' solo il prezzo d'ingresso migliore, non il segnale | casuali con lo stesso limit simili | il segnale batte le casuali limit |
| 4 | Tendenza di fondo | long nel 2020-2021, short nel 2022 | buono nei blocchi opposti |
| 5 | Pochi crolli e rimbalzi enormi (marzo 2020) | verifica 4 fallisce | superata |
| 6 | Riempimento ottimistico del backtest | crolla con il riempimento severo (verifica 8) | regge |
| 7 | Volatilita': stop larghi, costi bassi in R | casuali con stessa larghezza simili | il segnale le batte |
| 8 | Raggruppamento in pochi episodi | trade concentrati | distribuiti |
| 9 | Effetto generale fra le monete grandi | vale sulle monete di controllo | non vale |
| 10 | Il ritorno avviene gia' dentro la candela del segnale | ordini spesso non eseguiti; R medio vicino a zero | — |
| 11 | Costi | R lordo positivo, netto negativo | positivo a costi doppi |

**Varianti.**

> **V-013** · 1h · long · nessun filtro · ingresso E5: ritorno da Bollinger (20, 2,5) dalla banda inferiore ·
> conferma nessuna · tipo L: limit a 0,5 × ATR(14) sotto la chiusura, validita' 3 candele · stop S1: 1,5 × ATR(14) ·
> uscite U1: target 1,5 R, U2: dopo 12 candele.
>
> **V-014** · stessa, short: ritorno dalla banda superiore, limit 0,5 × ATR sopra la chiusura.

Motivi: k = 2,5 per prendere solo eccessi veri (l'idea parla di chi ha fretta); 1h perche' un'ora e' un orizzonte
in cui la fretta di chi vende si vede ma i costi pesano la meta' che a 30 minuti; ordine limit a 0,5 ATR (il piu'
lontano) perche' l'idea e' comprare la fretta degli altri a sconto; validita' 3 candele per lasciare al prezzo il tempo
di arrivarci. Nessun filtro: Nagel trova l'effetto in tutti i regimi, piu' forte con volatilita' alta. Stima: V-013
217 trade (310 ordini, 217 eseguiti), V-014 226 trade (331 ordini, 226 eseguiti).

**Previsione.** R medio fra −0,15 e +0,15 R, p-value sopra 0,05 per entrambe.

---

## I-08 — RSI che passa 50 in un mercato con tendenza forte

**Fonte.** J. W. Wilder, *New Concepts in Technical Trading Systems*, Trend Research, 1978 (RSI e ADX). Momentum di
serie temporale nelle criptovalute: Liu e Tsyvinski, 2021 (come I-01).

**Affermazione verificabile.** Su LINKUSDT a 1 ora, con ADX(14) sopra 25, quando l'RSI(14) passa sopra 50 il prezzo
riprende la tendenza abbastanza da dare, con stop a 2 ATR e trailing a 3 ATR, almeno 0,2 R dopo i costi, piu' delle
casuali. Simmetrico per lo short sotto 50. Differisce da I-01: non si compra la rottura del massimo ma la ripresa del
momento dopo una pausa, solo quando la tendenza e' forte.

**Sotto-domande.** Condizioni: tendenze forti di ore o giorni. Chi opera: chi segue la tendenza e rientra dopo le
pause. Perche' il prezzo proseguirebbe: l'ADX alto dice che la tendenza c'e'; l'RSI che passa 50 dice che la pausa e'
finita. Quando: ore o giorni.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentirebbe |
|---|---|---|---|
| 1 | Caso | come le casuali | p-value piccolo |
| 2 | L'ADX alto non ha direzione: con ADX alto in ribasso il long che passa 50 compra un rimbalzo | long perde nel 2022 | long buono anche nel 2022 |
| 3 | L'RSI a 50 attraversa spesso: segnali di rumore | molti stop, R negativo | R positivo |
| 4 | Tendenza di fondo | long nel 2020-2021, short nel 2022 | buono nei blocchi opposti |
| 5 | Pochi trade enormi | verifica 4 fallisce | superata |
| 6 | Costi | R lordo positivo, netto negativo | positivo a costi doppi |
| 7 | Volatilita': ADX alto viene con ATR alto e stop larghi | casuali con stessa larghezza simili | il segnale le batte |
| 8 | Ritardo: ADX e RSI arrivano tardi, la tendenza e' gia' finita | R negativo, trailing presto | R positivo |
| 9 | Raggruppamento | trade concentrati in poche tendenze | distribuiti |
| 10 | Generale fra le monete grandi | vale sulle monete di controllo | non vale |
| 11 | Stesso vantaggio (o assenza) di I-01: e' la stessa famiglia di tendenza | risultati simili a V-001 e V-002 | risultati diversi |

**Varianti.**

> **V-015** · 1h · long · filtro F2: ADX(14) sopra 25 · ingresso E7: RSI(14) passa sopra 50 · conferma nessuna ·
> tipo M · stop S1: 2 × ATR(14) · uscita U3: trailing a 3 × ATR(14).
>
> **V-016** · stessa, short: RSI(14) passa sotto 50.

Motivi: 1h perche' a 4h e 2h i trade erano troppo pochi (bozze B-32 ... B-35: 58-163); RSI a 14, il valore di Wilder;
ADX a 25 (tendenza); stop e trailing come I-01, le uscite classiche di tendenza, cosi' le due idee si confrontano a
parita' di uscite. Stima: V-015 316 trade, V-016 271 trade.

**Previsione.** R medio fra −0,15 e +0,1 R, p-value sopra 0,05 per entrambe (spiegazione 11: mi aspetto risultati
simili a I-01).

---

## I-09 — Incrocio del MACD nella direzione della tendenza di fondo

**Fonte.** G. Appel, *Technical Analysis: Power Tools for Active Investors*, FT Prentice Hall, 2005 (il MACD e il suo
uso nella direzione della tendenza). Momentum di serie temporale: Moskowitz, Ooi e Pedersen, 2012.

**Affermazione verificabile.** Su LINKUSDT a 2 ore, con la chiusura sopra la EMA a 200 candele (circa 17 giorni), un
incrocio al rialzo della linea del MACD sul suo segnale annuncia la ripresa della tendenza; con stop a 2 ATR, trailing
a 3 ATR e uscita al segnale opposto (incrocio al ribasso) il risultato e' di almeno 0,2 R dopo i costi, piu' delle
casuali. Simmetrico per lo short sotto la EMA a 200.

**Sotto-domande.** Condizioni: tendenze di settimane con correzioni di giorni. Chi opera: chi segue la tendenza.
Perche' il prezzo proseguirebbe: la correzione finisce e la tendenza riparte. Quando: giorni.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentirebbe |
|---|---|---|---|
| 1 | Caso | come le casuali | p-value piccolo |
| 2 | Il MACD incrocia spesso in mercati laterali: rumore | molte uscite al segnale opposto in piccola perdita | R positivo |
| 3 | Tendenza di fondo | long nel 2020-2021, short nel 2022 | buono nei blocchi opposti |
| 4 | Pochi trade enormi | verifica 4 fallisce | superata |
| 5 | Costi | R lordo positivo, netto negativo | positivo a costi doppi |
| 6 | Ritardo: il MACD incrocia quando il movimento e' gia' fatto | R vicino a zero | R positivo |
| 7 | Volatilita' | casuali con stessa larghezza simili | il segnale le batte |
| 8 | Il filtro EMA200 da solo fa il lavoro | casuali senza filtro peggiori, ma blocco per blocco nessun vantaggio | vantaggio stabile nei blocchi |
| 9 | Raggruppamento | trade concentrati | distribuiti |
| 10 | Generale fra le monete grandi | vale sulle monete di controllo | non vale |
| 11 | Stessa famiglia di I-01 e I-08 | risultati simili | diversi |

**Varianti.**

> **V-017** · 2h · long · filtro F1: chiusura sopra EMA(200) · ingresso E9: MACD (12, 26, 9) incrocia verso l'alto
> il segnale · conferma nessuna · tipo M · stop S1: 2 × ATR(14) · uscite U3: trailing a 3 × ATR(14), U4: segnale
> opposto.
>
> **V-018** · stessa, short: chiusura sotto EMA(200), incrocio verso il basso.

Motivi: 2h perche' a 4h i trade erano troppo pochi (bozze B-40, B-41: 114 e 90); EMA(200) come direzione di fondo;
uscita al segnale opposto perche' e' l'uso classico del MACD, piu' il trailing per proteggere i guadagni. Stima:
V-017 232 trade, V-018 191 trade.

**Previsione.** R medio fra −0,15 e +0,1 R, p-value sopra 0,05 per entrambe.

---

# Varianti nate dalla Fase 3

## V-019 — V-004 con l'uscita a tempo dopo 48 candele (nata dalla Fase 3)

Scritta il 18 ottobre 2026, dopo il risultato di V-004. Differisce da V-004 per un solo elemento (l'uscita a tempo:
48 candele invece di 24): e' una variante nata dalla Fase 3 (punto 3), qualunque sia la sua ipotesi. Prima della sua
Fase 2 si chiede al coordinamento il controllo sulle monete di controllo, sul periodo di costruzione, fra V-019 e
V-004 (Fase 3, punto 4); se non passa, V-019 e' uno scarto e consuma comunque il tentativo.

**Da dove viene.** Dai trade di V-004 (`codice/fase3_analisi.py`): le 67 uscite a tempo, dopo 24 ore, avevano in media
+0,449 R; se il rialzo dopo un funding negativo continua oltre le 24 ore, tenere la posizione il doppio dovrebbe
catturarne di piu'. Ipotesi (la stessa di I-02, con un orizzonte piu' lungo): la chiusura delle posizioni short con leva
dopo un funding negativo richiede piu' di un giorno.

**Spiegazioni concorrenti, in piu' di quelle di I-02.**

| # | Spiegazione | Previsione | Cosa la smentirebbe |
|---|---|---|---|
| 1 | Le uscite a tempo positive di V-004 sono un caso, scelto guardando i trade | sulle monete di controllo la modifica non migliora (controllo non passato) | controllo passato |
| 2 | Piu' tempo in posizione vuol dire piu' esposizione alla tendenza di fondo, non al segnale | il miglioramento c'e' anche per le entrate casuali | il p-value migliora rispetto a V-004 |
| 3 | Con 48 candele piu' trade arrivano allo stop | R medio uguale o peggiore di V-004 | migliore |

**Variante.**

> **V-019** · 1h · long · nessun filtro · ingresso E11: funding sotto 0,00% · conferma nessuna · tipo M · stop S1:
> 2 × ATR(14) · uscite U1: target 2 R, U2: dopo 48 candele.

Stima: 157 trade.

**Previsione.** Controllo sulle monete di controllo: piu' probabilmente non passa (spiegazione 1). Se passa: R medio fra
0,0 e +0,2 R, p-value sopra 0,023 (non supera la Fase 2).

---

# Quarto lotto (scritto il 18 ottobre 2026, dopo i lotti 1 e 2, mentre V-019 aspetta il coordinamento)

Dichiarazione (Fase 3, punto 3). I-10 differisce da ogni variante provata per ingresso, stop e uscite; I-11 da V-009,
V-010, V-013 e V-014 (le altre idee di ritorno alla media) per timeframe o tipo d'ingresso, segnale, filtro, stop e
uscite. Nessuna scelta viene dai risultati dei lotti precedenti. I-11 e' la terza idea di ritorno alla media dopo
I-05 e I-07, entrambe fallite: lo scrivo qui perche' la Fase 5 lo chiede (idee diverse o ritagli della stessa?). Il
segnale e' diverso (l'RSI, non le bande) e non ha ne' filtro ne' ordine limit.

## I-10 — Il prezzo che incrocia la sua media mobile

**Fonte.** W. Brock, J. Lakonishok, B. LeBaron, «Simple Technical Trading Rules and the Stochastic Properties of Stock
Returns», *Journal of Finance*, 1992: sull'indice Dow Jones dal 1897 al 1986 i segnali di acquisto dati dal prezzo
che supera la sua media mobile (50, 150 e 200 giorni) erano seguiti da rendimenti piu' alti di quelli di vendita, oltre
quanto spiegano i modelli casuali di riferimento.

**Affermazione verificabile.** Su LINKUSDT a 4 ore, quando la chiusura incrocia verso l'alto la SMA a 50 candele (circa
8 giorni), stare long fino all'incrocio opposto, con uno stop a 3 ATR, da' almeno 0,2 R dopo i costi per trade, piu'
delle casuali. Simmetrico per lo short.

**Sotto-domande.** Condizioni: tendenze di settimane. Chi opera: chi segue la tendenza; chi guarda le medie come
livelli. Perche' il prezzo proseguirebbe: aggiustamento lento all'informazione, comportamento gregario. Quando: giorni
o settimane.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentirebbe |
|---|---|---|---|
| 1 | Caso | come le casuali | p-value piccolo |
| 2 | Effetto pubblicato nel 1992 su azioni: sparito dopo la pubblicazione e assente nelle crypto | nessun vantaggio | vantaggio |
| 3 | Mercato laterale: molti incroci consecutivi in perdita (frusta) | tanti trade brevi negativi, R medio negativo | R positivo |
| 4 | Tendenza di fondo | long nel 2020-2021, short nel 2022 | buono nei blocchi opposti |
| 5 | Pochi trade enormi (le grandi tendenze) | verifica 4 fallisce | superata |
| 6 | Costi | R lordo positivo, netto negativo | positivo a costi doppi |
| 7 | Stop a 3 ATR troppo largo: R piccoli per trade | R medio vicino a zero | — |
| 8 | Volatilita' | casuali con stessa larghezza simili | il segnale le batte |
| 9 | Stessa famiglia di I-01, I-08, I-09 (tendenza), gia' fallite | risultati simili | diversi |
| 10 | Generale fra le monete grandi | vale sulle monete di controllo | non vale |
| 11 | L'uscita al segnale opposto arriva tardi e restituisce i guadagni | uscite al segnale opposto in media negative | positive |

**Varianti.**

> **V-020** · 4h · long · nessun filtro · ingresso E2: chiusura incrocia verso l'alto la SMA(50) · conferma nessuna ·
> tipo M · stop S1: 3 × ATR(14) · uscita U4: segnale opposto (chiusura incrocia verso il basso la SMA(50)).
>
> **V-021** · stessa, short.

Motivi: 4h e SMA a 50 candele (circa 8 giorni) perche' la regola e' di medio periodo e a 4h i costi pesano poco; la
SMA come nell'articolo; uscita al segnale opposto come nella regola originale (si sta dalla parte della media); stop a
3 ATR, il piu' largo, perche' la regola non ha uno stop e serve solo come protezione dai crolli. Nessun filtro. Stima:
V-020 199 trade, V-021 199 trade.

**Previsione.** R medio fra −0,15 e +0,1 R, p-value sopra 0,05 per entrambe (spiegazioni 2 e 9).

---

## I-11 — RSI agli estremi: ritorno di breve periodo

**Fonte.** N. Jegadeesh, «Evidence of Predictable Behavior of Security Returns», *Journal of Finance*, 1990:
inversione dei rendimenti di breve periodo. J. W. Wilder, 1978: livelli 30 e 70 dell'RSI.

**Affermazione verificabile.** Su LINKUSDT a 1 ora, quando l'RSI(14) risale sopra 30 dopo esserci stato sotto, il
prezzo nelle 24 ore successive sale abbastanza da dare, con stop a 2 ATR, target a 2 R e uscita dopo 24 candele,
almeno 0,2 R dopo i costi, piu' delle casuali. Simmetrico per lo short quando l'RSI scende sotto 70.

**Sotto-domande.** Condizioni: ribassi rapidi senza notizie. Chi opera: venditori in fretta e chi compra gli eccessi.
Perche' il prezzo tornerebbe: pressione temporanea. Quando: ore.

**Spiegazioni concorrenti.**

| # | Spiegazione | Previsione | Cosa la smentirebbe |
|---|---|---|---|
| 1 | Caso | come le casuali | p-value piccolo |
| 2 | Nelle crypto a 1 ora domina la prosecuzione, non l'inversione | R negativo | positivo |
| 3 | Tendenza di fondo: in ribasso il long che compra l'ipervenduto perde | long perde nel 2022 | long buono nel 2022 |
| 4 | Costi | R lordo positivo, netto negativo | positivo a costi doppi |
| 5 | Volatilita' | casuali con stessa larghezza simili | il segnale le batte |
| 6 | Pochi rimbalzi enormi | verifica 4 fallisce | superata |
| 7 | Raggruppamento: segnali ripetuti nello stesso ribasso | trade concentrati | distribuiti |
| 8 | Stessa famiglia di I-05 e I-07, gia' fallite | risultati simili (negativi) | positivi |
| 9 | Il ritorno avviene gia' nella candela del segnale (l'RSI che risale) | R vicino a zero meno i costi | positivo |
| 10 | Generale fra le monete grandi | vale sulle monete di controllo | non vale |
| 11 | Target a 2 R troppo lontano per un rimbalzo | molte uscite a tempo con R piccolo | target frequenti |

**Varianti.**

> **V-022** · 1h · long · nessun filtro · ingresso E6: RSI(14) incrocia verso l'alto 30 · conferma nessuna · tipo M ·
> stop S1: 2 × ATR(14) · uscite U1: target 2 R, U2: dopo 24 candele.
>
> **V-023** · stessa, short: RSI(14) incrocia verso il basso 70.

Motivi: RSI a 14 e livelli 30/70, i valori di Wilder (con RSI a 7 i trade sarebbero il doppio, bozze B-26 e B-27, ma
con piu' rumore); 1h e uscita dopo un giorno, l'orizzonte dell'inversione di breve; stop a 2 ATR e target a 2 R come
I-02, per uscite gia' scritte prima. Stima: V-022 273 trade, V-023 301 trade.

**Previsione.** R medio fra −0,2 e +0,05 R, p-value sopra 0,05 per entrambe (spiegazioni 2 e 8).
