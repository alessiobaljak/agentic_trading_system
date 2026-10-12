# Lezioni comuni sulle monete (Passo 7, 12 ottobre 2026)

Unione delle 21 `research/campagne/<SIMBOLO>/lezioni_moneta.md` (20 monete e GRUPPO, protocollo 4.5), con qualche
numero dalle `consegna.md` dove la lezione lo richiama e dal `vault/risultati.md`. Ogni affermazione porta la moneta e il
file da cui viene; «t» è il t contro la (b) (entrate casuali con la stessa uscita e direzione; soglia circa 2), R è dopo
i costi, tutto sui dati di costruzione salvo dove è scritto validazione o vault. Le campagne distinguono «osservato» da
«indizio»: qui si tiene la stessa distinzione. Gli archivi della prova di processo (7 ottobre) sono descritti in fondo,
non uniti.

## Il quadro in una tabella

| Moneta | Varianti | Candidati in Fase 2 | Arrivati in validazione | Al vault | Fonte |
|---|---|---|---|---|---|
| BTCUSDT | 37 (V01-V37) | V10, V11, V32, V33, V35 | V10 | **V10: non passa** (profit factor 1,067, R +0,031, 325 trade) | consegna.md, vault/risultati.md |
| ETHUSDT | 30 (più 4 scarti) | 026 | nessuno (cade in Fase 4) | — | consegna.md |
| SOLUSDT | 30 | 4 (famiglia di 015) | nessuno (cadono a costi doppi) | — | consegna.md |
| XRPUSDT | 30 | V21r3 | V21r3: 5 trade, «non si sa» | — | consegna.md |
| DOGEUSDT | 30 | 042 | nessuno (Fase 4) | — | consegna.md |
| BNBUSDT | 30 | 043, 044, 045 | 045: passa al limite (32 trade, p 0,031) | **045: non passa** (R −0,087, pf 0,55) | consegna.md, vault |
| LTCUSDT | 30 | 0 | — | — | consegna.md |
| MATICUSDT | 30 | 025 | nessuno (Fase 4) | — | consegna.md |
| BCHUSDT | 30 | 0 | — | — | consegna.md |
| LINKUSDT | 30 | 0 | — | — | consegna.md |
| AVAXUSDT | 30 | 5 | nessuno (Fase 4) | — | consegna.md |
| ADAUSDT | 30 | 025, 034, 035, 037, 039, 040 (famiglie 024 e 009) | 037: passa (82 trade, R +0,624, +0,014 senza i 3 migliori) | **037: non passa** (R −0,164, pf 0,79) | consegna.md, vault |
| TRBUSDT | 30 | 0 | — | — | consegna.md |
| FILUSDT | 30 | 016, 024, 025, 032-039 | 025: fallito (R −0,117 su 87 trade) | — | consegna.md |
| 1000SHIBUSDT | 30 | 2 (ritocchi) | nessuno (costi doppi) | — | consegna.md |
| DYDXUSDT | 30 | 008 | 008: fallito (R −0,178, pf 0,43, 83 trade) | — | consegna.md |
| MASKUSDT | 30 | 029 | 029: fallito (R +0,01 su 41 trade) | — | consegna.md |
| FTMUSDT | 30 | 0 | — | — | consegna.md |
| GALAUSDT | 30 | 032 | nessuno (costi doppi) | — | consegna.md |
| ETCUSDT | 30 | 3 (famiglia I-12) | nessuno (costi doppi e ritardo) | — | consegna.md |
| GRUPPO (80 monete) | 30 | 0 | — | — | consegna.md |

Sette candidati hanno girato in validazione (BTC V10, XRP V21r3, BNB 045, ADA 037, FIL 025, DYDX 008,
MASK 029): nessuno ha tenuto l'R medio della costruzione. Tre sono arrivati al vault: zero passaggi,
contro circa 0,02 attesi per caso (`vault/risultati.md`). Il giudizio d'insieme è del Passo 7, punto 1.

## 1. Lezioni comuni a molte monete

### 1.1 Le idee di tendenza guadagnano quanto un ingresso a caso nella stessa direzione: è l'anno, non la regola

Su tutte le monete con il 2020-2021 in costruzione, momentum settimanale, rottura del canale, media
mobile a 50 e simili hanno R medi alti che la (b) nella stessa direzione fa uguali, e che spariscono
senza i 3 trade migliori.

* BTCUSDT: rottura del canale a 4h V03 +0,438 R contro +0,27 della (b), t 0,65; media di 50 V29 +0,355
  R, t −0,06 (`BTCUSDT/lezioni_moneta.md`).
* ETHUSDT: Donchian long 003 +0,343 R contro +0,297 della (b), t 0,17, −0,089 senza i 3 migliori
  (`ETHUSDT/lezioni_moneta.md`).
* SOLUSDT: tre idee di trend con R +0,19/+0,34 contro +0,07/+0,26 del caso, t 0,3-0,8, +0,03/+0,04
  senza i 3 migliori (`SOLUSDT/lezioni_moneta.md`).
* BNBUSDT: Donchian long +0,814 R, ma 3 trade del 2021 fanno tutto, −0,10 senza di loro; media a 50
  long +0,477, t +0,01 (`BNBUSDT/lezioni_moneta.md`).
* MATICUSDT: momento settimanale long R 0,43, −0,05 senza i 3 migliori, t 0,73 (`MATICUSDT/lezioni_moneta.md`).
* 1000SHIBUSDT: quattro idee long con uscite lunghe (R 0,22-0,55) tutte negative senza i 3 migliori;
  la (b) di I-03 c vale 0,31 (`1000SHIBUSDT/lezioni_moneta.md`).
* ETCUSDT: momento a 7 giorni long +0,42 R e short +0,27, t 0,38 e 1,75; volume alto long +0,46, t
  0,50 (`ETCUSDT/lezioni_moneta.md`).
* XRPUSDT: canale long +0,42 R, −0,01 senza i 3 migliori (`XRPUSDT/lezioni_moneta.md`).
* LTCUSDT: canale long +0,171 R tutto nel 2020, −0,11 senza i 3 migliori (`LTCUSDT/lezioni_moneta.md`).
* BCHUSDT: canale long −0,23 senza i 3 migliori; le short vicine guadagnano solo nel 2022
  (`BCHUSDT/lezioni_moneta.md`).
* FILUSDT: lo short settimanale +0,25 R solo perché la (b) short guadagna uguale nel ribasso di fondo
  (`FILUSDT/lezioni_moneta.md`). FTMUSDT, AVAXUSDT, ADAUSDT, GALAUSDT: stessa lettura, con i trade
  solo nell'anno del trend (`FTMUSDT`, `AVAXUSDT`, `ADAUSDT`, `GALAUSDT/lezioni_moneta.md`).
* GRUPPO: rottura long su 80 monete 0,110 R ma −0,033 senza i 30 migliori; 2022 negativo in quasi tutte
  le long con R positivo; al 99,5-100° percentile contro ingressi indipendenti, non contro le sfasate
  (`GRUPPO/lezioni_moneta.md`, `GRUPPO/consegna.md`).

Lezione: un R medio alto in costruzione non dice nulla senza la (b) nella stessa direzione e senza l'R
per anno; ETCUSDT lo scrive: «i confronti con la (b) sono stati indispensabili per non scambiarlo per
un segnale».

### 1.2 Sotto l'ora i costi decidono tutto

Il costo di un giro a 15-30 minuti e a 1 ora è dell'ordine dell'effetto cercato, e la (b) parte in
perdita: ETHUSDT 0,067 R a 30 minuti; SOLUSDT circa 0,05; 1000SHIBUSDT 0,065; AVAXUSDT 0,06; ETCUSDT
0,08; DOGEUSDT e TRBUSDT circa 0,1 (la (b) a −0,06/−0,07 e fino a −0,3 R); BNBUSDT 0,14; GALAUSDT 0,03-0,10
a 1 ora con la (b) fra −0,05 e −0,08; MASKUSDT la (b) a 1 ora intorno a −0,05 e a 30 minuti −0,08;
DYDXUSDT la (b) perde 0,02-0,05 R; ADAUSDT il costo fisso di 0,14% «decide tutto» a 15-30 minuti;
GRUPPO 0,072 R a 1 ora contro 0,034 a 4 ore e 0,012 a 1 giorno (tutti in `lezioni_moneta.md`).
LTCUSDT: il funding da solo costa 0,08 R a trade ai long settimanali.

### 1.3 Il segnale più ripetuto: short sull'ultima mezz'ora del giorno UTC dopo una giornata in calo, ma vale meno dei costi

È l'unica idea che è venuta «netta» o vicina su molte monete, sempre con un guadagno lordo più
piccolo del costo di un giro.

* BTCUSDT V19: lordo +0,045 R contro costi 0,12 R; cinque ritocchi fino a t 3,58, nessuno regge costi
  doppi e ritardo (`BTCUSDT/lezioni_moneta.md`).
* ETHUSDT-012: t 2,32, effetto circa 0,035 R, metà del costo (`ETHUSDT/lezioni_moneta.md`).
* SOLUSDT-015: lordo +0,038 R, costi 0,05, netto −0,013; con i filtri positivo in costruzione e negativo
  a costi doppi (`SOLUSDT/lezioni_moneta.md`).
* ETCUSDT I-12: t 3,15, circa 10 punti base lordi (29 nei giorni sotto −5%) contro 20 di costi; tre
  ritocchi candidati, tutti caduti (`ETCUSDT/lezioni_moneta.md`).
* 1000SHIBUSDT I-08 b: t 1,92, dopo 5 ritocchi 2,08-2,15, lordo 0,1-0,15% di prezzo, meno di due giri
  (`1000SHIBUSDT/lezioni_moneta.md`).
* ADAUSDT-009: t 2,20 ma R −0,044 (`ADAUSDT/lezioni_moneta.md`).
* AVAXUSDT: +0,065 R lordi in entrambe le direzioni, pari ai costi (`AVAXUSDT/lezioni_moneta.md`).
* FILUSDT: la versione a 4 ore (fascia 20-24 UTC) batte la (b) fino a t 3,40 e regge i costi doppi, ma
  crolla col ritardo per costruzione (`FILUSDT/lezioni_moneta.md`).
* Assente o come il caso su BNBUSDT, MATICUSDT, XRPUSDT, TRBUSDT, DYDXUSDT, GALAUSDT, LINKUSDT,
  MASKUSDT (rispettivi `lezioni_moneta.md`).

ETCUSDT osserva che è un effetto di tutto il mercato (su BTC l'ultima mezz'ora è la più negativa delle
48 nei giorni in calo, −14,8 punti base) e che «con costi più bassi (ordini limit, monete più liquide)
potrebbe essere un'altra storia: qui non si può dire». Vedi anche la contraddizione 3.3.

### 1.4 Dopo un movimento estremo di un'ora il prezzo continua, non torna indietro (osservato quasi ovunque, non sfruttabile)

Lo short dopo un salto orario, e spesso il long dopo un crollo orario, perdono più del caso.

* SOLUSDT 009: short dopo +3σ R −0,127, t −1,30 (`SOLUSDT/lezioni_moneta.md`).
* MATICUSDT I-09: t −1,62 e −2,70, «nelle 6 ore dopo un salto prevale la continuazione» (`MATICUSDT`).
* 1000SHIBUSDT I-02 b: R −0,19, t −2,33, negativo in tutti gli anni (`1000SHIBUSDT`).
* LINKUSDT: l'inversione perde con t −2,6 e −3,1 in tutti gli anni (`LINKUSDT`).
* ETCUSDT I-03: short −0,18 R, t −1,9 (`ETCUSDT`).
* GALAUSDT 024 (pompa e scarico): t −2,75 (`GALAUSDT`).
* BNBUSDT I-12: long dopo una caduta oraria di 2 ATR R −0,178, t −2,13 (`BNBUSDT`).
* LTCUSDT I-04: short dopo i balzi con volume t −1,46 (`LTCUSDT`).
* ETHUSDT 024/025: le barre orarie enormi non rimbalzano, R −0,37 e −0,51, t −2,09 e −2,89 (`ETHUSDT`).
* XRPUSDT: il rientro dopo un'ora estrema è sotto il caso in tutte e due le direzioni (`XRPUSDT`).
* FILUSDT 005/006 e 009/010: nessun rimbalzo, nel 2022 i crolli con volume continuano (`FILUSDT`).
* TRBUSDT: short dopo un'ora esplosiva R −0,16 contro −0,10 della (b) (`TRBUSDT`).
* AVAXUSDT V-28: short dopo +3σ orario perde più del caso (`AVAXUSDT`).
* BTCUSDT V05/V06 (4h): peggio del caso o nessun rimbalzo (`BTCUSDT`).

Ma la continuazione, provata come idea, non paga i costi: LINKUSDT fino a fine giornata t +0,62 e
+0,31; GALAUSDT 011/015/017 t 1,3-1,9 (anche il controllo positivo col ritardo batte il caso, t 3,7:
«indizio da non contare due volte»); ETHUSDT-034 +0,015 R, t 1,17; AVAXUSDT V-14 a 4 ore t 2,68 ma
cade al ritardo (1,33 contro 1,34). MATICUSDT, BCHUSDT e FTMUSDT dicono di non averla provata come
idea perché sarebbe nata dai risultati, senza fonte. Vedi anche le contraddizioni 3.1 e 3.2.

### 1.5 Il funding alto non anticipa un calo: accompagna i rialzi

Lo short dopo un funding estremo positivo perde o fa come il caso, su tutte le monete che hanno
abbastanza episodi.

* SOLUSDT 016: R −0,198 su 79 trade, t −2,70, quasi tutto nel 2021 (`SOLUSDT`).
* DOGEUSDT: R −0,163, t −2,67, 106 trade tutti nel 2021 (`DOGEUSDT`).
* MATICUSDT: R −0,28, t −2,27 (`MATICUSDT`). BCHUSDT 017: t −2,05, negativo in tutti e tre gli anni
  (`BCHUSDT`). LINKUSDT t −1,64 (`LINKUSDT`). BNBUSDT −0,103 (`BNBUSDT`). XRPUSDT −0,13 (`XRPUSDT`).
  FILUSDT −0,15 (`FILUSDT`). ADAUSDT −0,085 (`ADAUSDT`). LTCUSDT perde nel 2021 (`LTCUSDT`).
  1000SHIBUSDT 0,00 (`1000SHIBUSDT`). AVAXUSDT nessuno vicino (`AVAXUSDT`).
* BTCUSDT V14: +0,069 R, t 1,47, non netto, nessun segnale nel 2022 (`BTCUSDT`): l'unica non negativa.
* GRUPPO I-05: nessun segnale (`GRUPPO`). DYDXUSDT, TRBUSDT, ETCUSDT, FTMUSDT: sotto i 70 trade
  (funding estremo troppo raro: DYDXUSDT oltre ±0,03% troppo di rado in 596 giorni; FTMUSDT 58 segnali).

Il funding negativo è un'altra storia: vedi la contraddizione 3.4.

### 1.6 Il lunedì non ha nulla, e dove ha qualcosa è in perdita

Nulla su BNBUSDT (R −0,004, t −0,38), MATICUSDT (t −0,59), BCHUSDT (t −0,16), LTCUSDT, SOLUSDT,
ETHUSDT, 1000SHIBUSDT (R 0,00), DYDXUSDT (t 0,92, −0,004 senza i 3 migliori), TRBUSDT (t 0,44),
FTMUSDT, GALAUSDT, ETCUSDT, AVAXUSDT. Debole e instabile su BTCUSDT (+0,063 R, t 1,13, quasi tutto dal
2020) e XRPUSDT (+0,10 R, t 1,11, negativo nel 2022). Peggio del caso su FILUSDT (−0,21 R, t −1,9) e nel
GRUPPO (t −1,37). (Tutti dai rispettivi `lezioni_moneta.md`.)

### 1.7 I numeri tondi non dicono nulla, con moltissimi trade

ETHUSDT: circa 1.600 trade per direzione, R identico al caso, t 0,09 e −0,24 («il risultato più
pulito»). BTCUSDT V20: 1.452 trade, peggio del caso (t −2,69). LTCUSDT: 900 attraversamenti, nessuna
continuazione dopo i costi. BNBUSDT 1.482 e 1.396 trade, niente. Niente su SOLUSDT, XRPUSDT, DOGEUSDT,
BCHUSDT (costi alti in R), ADAUSDT, TRBUSDT, 1000SHIBUSDT, DYDXUSDT, GALAUSDT, ETCUSDT. (Rispettivi
`lezioni_moneta.md`.)

### 1.8 Il ritorno alla media di poche ore (RSI a 2 periodi e simili) non paga, e dove paga vive nella prima ora

Nulla su BTCUSDT, SOLUSDT, XRPUSDT, MATICUSDT, BCHUSDT, AVAXUSDT, DYDXUSDT, ETCUSDT; scarti per trade su
ADAUSDT; GALAUSDT lo short perde; LTCUSDT vince il 65% dei trade ma piccoli rispetto allo stop al 6%,
R +0,004/+0,016; FILUSDT short +0,045, t 0,94. L'unica che è arrivata al vault, BNBUSDT-045 (RSI a 2 a
1 ora, solo fine settimana), aveva il rimbalzo «nella prima ora» (senza il filtro, col ritardo di
un'ora t −0,04) e nel vault fa −0,087 R, come la media delle entrate casuali (`BNBUSDT/lezioni_moneta.md`,
`vault/risultati.md`). BNBUSDT lo chiama «un vantaggio di esecuzione più che di previsione».

### 1.9 La rottura di volatilità dall'apertura del giorno (Williams) è la famiglia più spesso «vicina», ed è quella più esposta alla trappola dello stop

* BTCUSDT V10: l'unico candidato della ricerca arrivato al vault; regge lo stop fisso (t 3,10) ma si
  assottiglia a ogni periodo: +0,149 R in costruzione, +0,048 in validazione, +0,031 nel vault, positivo
  solo nel 2024 (`BTCUSDT/lezioni_moneta.md`, `vault/risultati.md`). Lo short V11 sembrava candidato
  solo per lo stop (t 3,01 → 1,01 con stop fisso).
* ETHUSDT 032/033: la famiglia più vicina (t 1,52 e 1,66), non netta (`ETHUSDT`).
* LINKUSDT: +0,044 long e +0,074 short, t 0,86 e 1,62 (`LINKUSDT`). BCHUSDT short 1,53, solo nel 2022
  (`BCHUSDT`). GALAUSDT 017 vicina (`GALAUSDT`). TRBUSDT a 15 minuti short t 1,37, il più alto della
  campagna (`TRBUSDT`). DOGEUSDT vicino a zero (`DOGEUSDT`). AVAXUSDT ed ETCUSDT nulla.
* Dove lo stop era l'apertura del giorno o il minimo dell'intervallo, il vantaggio era la posizione
  dello stop: LTCUSDT I-07 con 5 ritocchi, t a 0 con lo stop fisso; FILUSDT-025 t 1,38 contro stop
  normali e −0,117 R in validazione; ADAUSDT I-13 a 15 minuti (t 2,49 e 3,28), poi 037 nel vault −0,164 R
  con 113 uscite allo stop su 167 (`LTCUSDT`, `FILUSDT`, `ADAUSDT/lezioni_moneta.md`, `vault/risultati.md`).

### 1.10 Le idee lente non arrivano a 70 trade su una moneta sola, e il gruppo non le ha salvate

Funding estremo, canali, compressione delle bande di Bollinger, volume anomalo, massimo dell'anno,
cambio del mese: sotto i 70 trade in costruzione su SOLUSDT (sette idee elencate con 36-62 trade
stimati), DOGEUSDT (8 scarti su 14 a 1d/4h), BNBUSDT, LTCUSDT, MATICUSDT (I-10: 2 trade), BCHUSDT,
LINKUSDT, ADAUSDT (8-54 trade), TRBUSDT, FILUSDT (canale: 4 scarti in 815 giorni), DYDXUSDT, MASKUSDT,
FTMUSDT (8 scarti su 15 idee), ETCUSDT, XRPUSDT (bande). ETCUSDT suggeriva la campagna di gruppo come il
posto per provarle; il GRUPPO le ha provate su 80 monete (momento, rotture, funding, volume a 1 giorno)
e non ha trovato nulla: 6 scarti sotto i 700 trade e nessuna variante netta (`GRUPPO/consegna.md`).

### 1.11 «BTC guida, la moneta segue»: un effetto piccolo e di regime, sempre sotto i costi

* FILUSDT-016 (long a 1h su FIL in ritardo): t 2,35, regge tutto tranne i costi doppi (R −0,004); lordo
  circa 0,14 R, «solo il doppio del costo di un giro»: «l'indizio più pulito della campagna» (`FILUSDT`).
* DYDXUSDT-008: candidato (t 2,22), ma lo scettico mostra che conta solo l'ora forte di BTC, non il
  ritardo di DYDX; in validazione −0,178 R: ha funzionato nel 2021 e a inizio 2023, non nel 2022
  (`DYDXUSDT`).
* ADAUSDT I-06: t 1,86, R −0,007, «il ritardo esiste un po', non paga i costi» (`ADAUSDT`).
* GALAUSDT 011: t 1,3-1,9, due ritocchi non la portano oltre (`GALAUSDT`).
* GRUPPO I-07 su 80 monete: +0,04/+0,09 R lordi contro 0,05-0,07 di costi, t massimo 2,06 contro
  soglia 2,16 dopo 5 ritocchi (`GRUPPO`).
* Nulla su SOLUSDT (018, 019), XRPUSDT, ETCUSDT, AVAXUSDT, 1000SHIBUSDT, MASKUSDT, FTMUSDT, MATICUSDT (I-14).
* Il residuo rispetto a BTC si richiude quando è negativo: ADAUSDT 022 long t 1,92 (e lo short dopo un
  residuo positivo perde, t −1,80); GRUPPO I-19 a 4 ore «l'effetto più grande e più stabile», R da
  +0,017 a +0,089, t massimo 1,89, concentrato nei giorni di vendite generali e negativo nel 2022; GRUPPO
  I-26 a 3 settimane: le monete rimaste indietro recuperano (lo short perde, t −1,33). FILUSDT: i
  movimenti di FIL non accompagnati da BTC non continuano (+0,30 R nei giorni di rottura anche di BTC,
  −0,11 nei giorni della sola FIL). LINKUSDT: il rimbalzo giornaliero vive nei giorni di discesa comune a
  tutto il mercato.

### 1.12 Il premio del perpetuo sul mark: qualcosa solo dove la liquidità è scarsa

XRPUSDT: l'unica idea vicina della campagna, ma 84 trade su 97 nel 2020 a volume basso e in validazione
5 segnali in 14 mesi (R −0,57): «un effetto, se c'è, dei periodi di liquidità scarsa». GALAUSDT 032: short
quando il last è sopra il mark più del solito, l'unico netto in costruzione, circa 0,06 R sopra il caso ma
R +0,013 e −0,043 a costi doppi. LTCUSDT I-12 short +0,011 R. Nulla su DYDXUSDT e MASKUSDT. (Rispettivi
`lezioni_moneta.md`.)

### 1.13 Tutto si indebolisce fuori dalla costruzione

Dei sette candidati validati, nessuno ha tenuto l'R di costruzione: BTCUSDT V10 +0,149 → +0,048 → +0,031
(vault); BNBUSDT-045 +0,138 → +0,047 → −0,087; ADAUSDT-037 (validazione +0,624 fatta da 3 trade) → −0,164;
FILUSDT-025 +0,084 → −0,117; DYDXUSDT-008 +0,060 → −0,178; MASKUSDT-029 netto in costruzione → +0,01 su 41
trade; XRPUSDT-V21r3 → 5 trade. (`consegna.md` delle monete, `vault/risultati.md`.) Dove il protocollo
aveva lasciato passare un candidato, erano i pochi trade (BNB: 32; ADA: 3 giornate) o lo stop
(FIL) a spiegarlo, e le campagne lo avevano scritto nelle riserve.

## 2. Lezioni specifiche di una moneta

* **BTCUSDT.** Le idee di ritorno alla media di breve (V05-V07, V27) perdono contro il caso: a 4 ore nel
  2020-2022 BTC non rimbalza dopo gli eccessi. Funding estremo e squilibrio degli ordini aggressivi
  (V14-V16) danno R positivi ma non netti, «da non buttare se un giorno si potranno contare più monete
  insieme» (`BTCUSDT/lezioni_moneta.md`).
* **ETHUSDT.** Nei ribassi forti ETH tende a resistere: short quando ETH scende meno di BTC t −1,93,
  short dopo un giorno anomalo negativo t −1,86, e anche il long dopo un giorno anomalo positivo t −1,52
  (a un giorno, dopo i giorni estremi il prezzo non prosegue). Il rifiuto del massimo del giorno prima
  (026) porta un'informazione stabile in ogni parametro e timeframe, ma vale circa zero dopo i costi e si
  concentra nella prima ora (`ETHUSDT/lezioni_moneta.md`).
* **SOLUSDT.** La rottura al ribasso di una barra stretta (NR7/NR4) lavora solo sotto la SMA200 (R −0,19
  sopra, +0,18 sotto), mai netta contro la (a). Il funding molto alto è stato seguito da altri rialzi
  (`SOLUSDT/lezioni_moneta.md`).
* **XRPUSDT.** Nessuna delle 15 idee batte il caso così com'è scritta (t massimo 1,77); XRP «rimasto
  indietro» su BTC non recupera abbastanza da pagare i costi (`XRPUSDT/lezioni_moneta.md`).
* **DOGEUSDT.** Le rotture verso il basso a 1 ora fanno meglio di quelle verso l'alto in tre idee
  (strettoia short t 1,33 contro long −0,39; giorno stretto 1,17 contro −0,98; numeri tondi 0,61 contro
  −1,71): un indizio, che il 2021 di DOGE può spiegare da solo. Il candidato 042 era un picco: netto in 6
  casi su 14 della robustezza, costi doppi t 2,013 contro soglia 2,040 (`DOGEUSDT/lezioni_moneta.md`).
* **BNBUSDT.** Dopo i crolli il prezzo continua più che rimbalzare (caduta oraria di 2 ATR t −2,13;
  crollo di 24 ore short R −0,21); fa eccezione il calo di poche ore dentro un rialzo (RSI a 2), che
  rimbalza nella prima ora (`BNBUSDT/lezioni_moneta.md`).
* **LTCUSDT.** I balzi con volume alto continuano (short t −1,46); il momentum a una settimana non si
  distingue dal trend dell'anno; l'intervallo d'apertura UTC con 5 ritocchi vince solo per la posizione
  dello stop (`LTCUSDT/lezioni_moneta.md`).
* **MATICUSDT.** ATR giornaliero mediano 10%: ogni idea da 4 ore in su ha lo stop fisso al 6%. Lo
  squilibrio di vendite aggressive anticipa un debole ribasso (short t 2,08; 025 con BTC non in rialzo R
  0,149), ma col ritardo di un'ora t 0,53: «troppo fragile per un bot che entra con latenza»
  (`MATICUSDT/lezioni_moneta.md`).
* **BCHUSDT.** Due osservazioni non provate come idee: dopo un funding nel decile alto il prezzo NON
  scende (R −0,111, negativo in tutti gli anni); dopo acquisti aggressivi insoliti il prezzo nelle 4 ore
  dopo scende (R −0,143, t −1,99). «Compatibili con il caso (2 valori di |t| vicini a 2 su 30)»
  (`BCHUSDT/lezioni_moneta.md`).
* **LINKUSDT.** Il momentum a breve non funziona a nessuna scala (giornaliero t −2,30/−1,98: domina
  l'inversione). Il long dopo un giorno negativo (V24) è il più vicino: t 2,23 contro la (b) ma 1,71
  contro la (a); su BTC la stessa regola fa t 0,86 (`LINKUSDT/lezioni_moneta.md`).
* **AVAXUSDT.** Continuazione dopo una barra di 4 ore oltre 2σ (V-14): R 0,20 su 113 trade, t 2,68,
  positivo in tutti e tre gli anni, robusto, netto a costi doppi, rendimento medio +0,33%/+1,09%/+0,52%
  nelle barre 1-3 contro +0,07% di una barra qualsiasi; scartato dalla regola del ritardo (t 1,33 contro
  1,34 richiesto), non per un errore trovato. L'effetto non è simmetrico: i crolli di 4 ore rimbalzano un
  po' (short −0,18, t −1,74) (`AVAXUSDT/lezioni_moneta.md`).
* **ADAUSDT.** Il residuo negativo rispetto a BTC si richiude (022 t 1,92), quello positivo continua (023
  t −1,80); i volumi alti senza grande movimento precedono rialzi (019 R 0,27 su 78 trade, t 1,40). Il
  candidato 037 in validazione «vive di 3 giornate» (`ADAUSDT/lezioni_moneta.md`).
* **TRBUSDT.** ATR mediano 1,1% a 15m, 2,3% a 1h, 4,9% a 4h, 13,4% a 1d; ombre fino all'83%; R per trade
  del 2020 molto negativo in quasi tutte le varianti; le baseline a 15m-1h fino a −0,3 R. Nessuna idea
  sopra t 1,37 (`TRBUSDT/lezioni_moneta.md`).
* **FILUSDT.** Il lunedì di FIL è stato peggiore di un giorno qualunque (−0,21 R, t −1,9); dopo forti
  acquisti aggressivi il prezzo scende (−0,43 R), il contrario della fonte; la stagionalità della fascia
  oraria a 4h è nettamente negativa (t −2,36); l'incrocio con la media a 50 «viene dall'uscita», la (b)
  con la stessa uscita fa uguale (`FILUSDT/lezioni_moneta.md`).
* **1000SHIBUSDT.** La mania del 2021 domina ogni regola long lunga; a 1 ora i movimenti estremi
  continuano, a 4 ore dopo un crollo prevale il rimbalzo (short −0,22 R, t −2,25): «la direzione dopo un
  crollo cambia con l'orizzonte» (`1000SHIBUSDT/lezioni_moneta.md`).
* **DYDXUSDT.** Sul perpetuo i taker vendono più di quanto comprano (quota sotto 0,5 in 257 giorni contro
  54); il funding estremo è troppo raro per 70 trade; il candidato 008 è «un comportamento di regime»
  (`DYDXUSDT/lezioni_moneta.md`).
* **MASKUSDT.** L'impennata oraria oltre 3σ tende a rientrare nelle 6-12 ore seguenti (t 1,54) e il
  funding negativo all'ingresso sembra separare i casi che non rientrano; il candidato 029 in validazione
  fa +0,01 R su 41 trade: «l'effetto non regge fuori campione, o è molto più piccolo»
  (`MASKUSDT/lezioni_moneta.md`).
* **FTMUSDT.** Trade solo nel 2021 e nel 2022; il momento short a 2 settimane (036) netto contro la (b)
  ma non contro la (a), e i ritocchi peggiorano («probabile fortuna e ribasso del 2022»); stop in ATR
  giornalieri del 30% e oltre (`FTMUSDT/lezioni_moneta.md`).
* **GALAUSDT.** L'unico vantaggio netto è lo short quando il last è sopra il mark più del solito (032),
  che vale meno di un giro di costi; dopo un'ora forte il prezzo continua per qualche ora (tre varianti a
  t 1,3-1,9); volume medio da 828 milioni al giorno (2021) a 198 (2023) (`GALAUSDT/lezioni_moneta.md`).
* **ETCUSDT.** Fine giornata UTC nei giorni in calo t 3,15, circa 10 punti base lordi contro 20 di costi;
  tutto il resto nulla o sotto i trade minimi (`ETCUSDT/lezioni_moneta.md`).
* **GRUPPO (80 monete).** Il rientro del residuo a 4 ore (I-19) è l'effetto più grande e stabile ma
  vive nei giorni di vendite generali (fino a 112 uscite in un giorno, blocchi di 200-290 trade); il
  ritardo da BTC a 1 ora (I-07) arriva a t 2,06 contro 2,16. Con 80 monete che si muovono insieme la
  potenza per vantaggi di pochi centesimi di R è bassa (`GRUPPO/lezioni_moneta.md`, `GRUPPO/consegna.md`).

## 3. Lezioni in contraddizione fra campagne

Tutte osservate, nessuna provata: vanno lette come «dipende dalla moneta, dall'orizzonte o dal
periodo», non come fatti.

### 3.1 Dopo un crollo di 4 ore (o di 24 ore): rimbalzo o continuazione?

* Rimbalzo: 1000SHIBUSDT I-13 b (short dopo una barra da 4 ore sotto −2σ: R −0,22, t −2,25); AVAXUSDT V-15
  (short dopo un crollo di 4 ore oltre 2σ: R −0,18, t −1,74); BNBUSDT I-08 (short dopo un crollo di 24 ore
  oltre 1,5σ: R −0,213, t −1,95, «il ribasso NON continua»).
* Continuazione: FTMUSDT I-14 (inversione a 4 ore dopo un calo con volume alto: t −2,08, «i movimenti
  forti sembrano continuare»); FILUSDT 009/010 (nel 2022 i crolli con volume continuano); BTCUSDT V06
  (nessun rimbalzo a 4 ore dopo una barra anomala in ribasso).
  (Rispettivi `lezioni_moneta.md`.)

### 3.2 Dopo un'impennata oraria: continua (quasi ovunque, 1.4) o rientra?

MASKUSDT: l'impennata oraria oltre 3σ tende a rientrare nelle 6-12 ore seguenti in costruzione (short t
1,54, poi candidato 029 con uscita e filtro ritoccati), ma in validazione +0,01 R. ADAUSDT: il residuo
negativo rispetto a BTC si richiude (long t 1,92). Contro: SOLUSDT, MATICUSDT, 1000SHIBUSDT, LINKUSDT,
ETCUSDT, GALAUSDT, LTCUSDT, TRBUSDT, AVAXUSDT (1.4).

### 3.3 Fine giornata UTC: è l'ora, o è il momento infragiornaliero?

* È l'ora: SOLUSDT (la stessa regola alle 11:30 ha t −1,52: «l'effetto è dell'ora»); 1000SHIBUSDT (non
  c'è a mezzogiorno, t −1,09, né alle 17:30, t 1,38); ETCUSDT (su BTC è la mezz'ora più negativa delle 48).
* Non è l'ora: AVAXUSDT (il segno del giorno fino alle 23:30 predice la mezz'ora dopo «e continua anche
  dopo la mezzanotte; l'ora in sé non è speciale»). FILUSDT a 4 ore: il segnale lavora solo quando anche
  BTC si muove nella stessa direzione e nei giorni volatili.

### 3.4 Funding molto negativo, poi long: debole guadagno o perdita?

* Debole guadagno, mai netto: BTCUSDT V15 (+0,053 R, t 1,28; nell'archivio della prova: decile più basso
  R 0,08, positivo ogni anno, 96° percentile); BNBUSDT (+0,064, t 1,16); XRPUSDT (+0,15, t 0,92, quasi
  tutto dal 2021); MASKUSDT (t 1,38); BCHUSDT (0,22).
* Perdita o nulla: AVAXUSDT (nel 2022 il funding negativo accompagnava il ribasso, t −1,29); 1000SHIBUSDT
  (−0,13 R); LTCUSDT (quasi tutto nel ribasso del 2022); MATICUSDT (t −0,24); LINKUSDT (−0,41); ADAUSDT
  (−0,006); DYDXUSDT (−0,014).
  (Rispettivi `lezioni_moneta.md`.) Le monete grandi stanno da una parte, le piccole dall'altra: è
  un'osservazione, non una prova.

### 3.5 Squilibrio degli ordini aggressivi (taker): segno opposto da moneta a moneta

* Acquisti aggressivi, poi long: debole positivo su BTCUSDT V16 (+0,073 R, t 1,16) e BNBUSDT I-09 (+0,103,
  t 1,50, 2022 negativo); chiaramente negativo su BCHUSDT 019 (t −1,99, nelle 4 ore dopo −0,143) e FILUSDT
  021 (−0,43 R); nulla su ETHUSDT, SOLUSDT, XRPUSDT, ADAUSDT, 1000SHIBUSDT, AVAXUSDT, LINKUSDT; in perdita
  per i costi su ETCUSDT (−0,09/−0,07 R su quasi 900 trade).
* Vendite aggressive, poi short: MATICUSDT netto contro la (b) (t 2,08) ma fragile; DYDXUSDT t 1,14 con
  5 ritocchi sotto la soglia; nulla altrove.

### 3.6 Il momentum a un giorno: inversione debole o nulla?

Inversione debole: LINKUSDT (long dopo un giorno negativo t 2,23 contro la (b)); ETHUSDT (dopo i giorni
estremi il prezzo non prosegue, t −1,52/−1,86 per la continuazione); ADAUSDT I-04 long 1,46; MATICUSDT
I-03 long 1,51 (positivo in entrambi gli anni). Nulla: ETCUSDT I-04, BCHUSDT I-06, DOGEUSDT (scarto),
XRPUSDT, GRUPPO I-03 (t −0,38/−0,37 su 1.738 e 1.405 trade).

### 3.7 Volume alto a 1 giorno o 4 ore: solo trend, o un indizio?

Solo trend: MATICUSDT I-08 (t fino a 1,94, febbraio-maggio 2021 fa quasi tutto, la (a) fa già 0,45),
BNBUSDT (come il caso), ETCUSDT (t 0,50), BTCUSDT V30 (t −0,49), BCHUSDT (0,24). Indizio: ADAUSDT 019
(volume sopra il 90° percentile, R 0,27 su 78 trade, t 1,40), GALAUSDT 015 (t 1,3-1,9), LTCUSDT I-11
(+0,10 R, t 1,58, ma scelta dopo aver visto un'altra idea).

## 4. Cosa dicono le lezioni per il Passo 7, punto 2 (idee simili fra monete)

* Nessuna idea è passata nel vault su nessuna moneta: non esiste un'«idea di gruppo» nel senso del
  protocollo. Le convergenze qui sopra (1.3, 1.4, 1.11) sono indizi fra campagne che sono copie dello
  stesso modello (sezione 11, «stesso modello»), non prove.
* Le idee che falliscono ovunque, e che vale la pena non riprovare così come sono: lunedì (1.6), numeri
  tondi (1.7), short sul funding alto (1.5), ritorno alla media di poche ore (1.8), le idee di tendenza
  giudicate contro zero invece che contro la (b) (1.1), e qualunque idea sotto l'ora con un lordo sotto
  due giri di costi (1.2).
* Le idee più ripetute ma sempre sotto i costi (fine giornata UTC, continuazione oraria, ritardo da
  BTC, premio sul mark): tre campagne (ETCUSDT, FILUSDT, BTCUSDT) scrivono che con costi più bassi o con
  più monete insieme «potrebbe essere un'altra storia». È una domanda per il proprietario, non un
  risultato.

## 5. Cosa contengono gli archivi della prova di processo (non uniti)

`origin/research/archivio/campagna/BTCUSDT`, `ETHUSDT`, `SOLUSDT` (7 ottobre, archiviati al Passo 2)
hanno una `lezioni_moneta.md` ciascuno, sulle stesse monete ma con idee in parte diverse e con il minimo
di 100 trade della 4.3:

* BTCUSDT (archivio): il 2020 fa guadagnare qualunque long di qualche giorno (canale +0,99 R, intervallo
  di apertura +0,57); ritorno alla media a 4 ore «no, in nessuna forma»; funding negativo nel decile più
  basso → 24 ore positive (R 0,08, ogni anno, 96° percentile, mai netto, sparisce a 12 ore); stop in ATR
  giornaliero 10-12% del prezzo.
* ETHUSDT (archivio): 23 varianti, nessuna oltre 2 errori standard; «il 2020-21 regala e il 2022
  toglie»; a 1 ora «i costi sono il mercato» (profit factor dopo costi fra 0,66 e 0,95); il funding
  estremo è stato positivo nel 97% dei settlement 2020-21 e ha accompagnato il trend.
* SOLUSDT (archivio): 17 varianti; 2021 ×113 e 2022 ÷17, «qualunque strategia direzionale segue
  l'anno»; lo **short sui ritracciamenti in tendenza ribassista** (R 0,14, profit factor 1,30, positivo
  nei due anni, sopra tutte le 200 casuali, p 0,085) fallisce solo il «netta» a due campioni: «l'unica idea
  che varrebbe la pena riprovare con una regola scritta meglio prima». La campagna 4.5 di SOLUSDT ha poi
  trovato qualcosa di simile con NR7/NR4 short sotto la SMA200 (R +0,18, non netta contro la (a)).
  Beta di SOL su BTC a 1 ora 1,21-1,23; SOL si muove con BTC, nessun ritardo sfruttabile.
