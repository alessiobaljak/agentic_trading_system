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
