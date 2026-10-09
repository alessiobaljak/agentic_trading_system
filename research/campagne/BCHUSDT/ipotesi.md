# BCHUSDT — Ipotesi (Fase 1)

Ogni idea è scritta qui prima del primo test delle sue varianti. Il codice di ogni variante
è in `codice/varianti.py` (classe indicata), committato prima del test. I costi di un giro
(commissione 0,05% + slippage 0,02% per lato) sono circa 0,14% del nozionale: in R valgono
0,14% diviso la distanza dello stop. Ricordo (Fase 0) che nel 2020 e nel 2022 lo slippage
vero era probabilmente più alto (fascia 0,05%): una previsione al limite va letta peggio.

Spiegazioni concorrenti comuni a tutte le idee, che riscrivo per ognuna con la sua
previsione: effetto casuale; volatilità; trend di fondo; artefatto dei dati; effetto costi;
«è solo il mercato» (BCHUSDT segue BTC); più quelle specifiche del meccanismo.

---

## I-01 — Momento della serie a una settimana (1d)

**Fonte.** T. J. Moskowitz, Y. H. Ooi, L. H. Pedersen, «Time Series Momentum», *Journal of
Financial Economics* 104(2), maggio 2012. Per le crypto: Y. Liu, A. Tsyvinski, «Risks and
Returns of Cryptocurrency», NBER Working Paper 24877, agosto 2018: il rendimento di una
settimana predice quello delle settimane successive.

**Affermazione verificabile.** Su BCHUSDT, se il rendimento degli ultimi 7 giorni è positivo
(negativo), il rendimento dei 7 giorni successivi è in media più alto (più basso) di quello
di un ingresso qualunque con la stessa uscita. Falsificata se l'R medio dei trade condizionati
non supera nettamente quello degli ingressi casuali con la stessa uscita.

**Sotto-domande.** Vale di più dopo movimenti grandi o piccoli? In regimi di alta volatilità
(sotto-reazione alle notizie, poi rincorsa)? Chi muove il prezzo: chi rincorre (trend
follower, investitori che entrano dopo i rialzi) e chi liquida tardi. Tempo: l'effetto
documentato è su 1-4 settimane, quindi tenuta di 7 giorni.

**Spiegazioni concorrenti** (previsione → cosa la smentirebbe):
1. *Caso.* R medio vicino a quello della (b), `t` < 2 → smentita da `t` contro la (b) netto e stabile negli anni.
2. *Trend di fondo.* Nel 2020-21 tutto sale, nel 2022 tutto scende: il long guadagna solo negli anni di rialzo, lo short solo nel 2022, come la (b) della stessa direzione → smentita se la variante batte la (b) anno per anno.
3. *È solo il mercato (BTC).* Il segnale è il momento di BTC trasmesso a BCH: l'effetto sparisce se si guarda BCH al netto di BTC → smentita se la variante batte la (b) anche negli anni in cui BCH e BTC divergono (non lo misuro qui direttamente; lo guardo in Fase 3 se serve).
4. *Volatilità.* Dopo settimane forti la volatilità è alta: lo stop in ATR si allarga e l'R cambia scala, non il vantaggio → la (a) e la (b) usano lo stesso stop, quindi il confronto lo neutralizza; smentita se il vantaggio resta con la (b).
5. *Pochi eventi estremi.* Il risultato viene da 2-3 corse (es. maggio 2021) → smentita se l'R medio senza i 3 migliori resta sopra la (b).
6. *Artefatto dei dati.* Il giorno mancante (2022-10-02) o il riscaldamento falsano un trade → al massimo un trade toccato; smentita guardando quel trade.
7. *Costi.* Con stop a ~12% i costi sono ~0,01 R: non possono creare né distruggere il vantaggio; smentita se costi doppi cambiano l'esito.
8. *Inversione di breve.* A una settimana le crypto potrebbero invertire invece di continuare (sovra-reazione): previsione opposta, R medio sotto la (b) → la vedo nel segno del `t`.
9. *Sovrapposizione degli ingressi.* Con tenuta 7 giorni e segnale quasi sempre acceso, la variante entra quasi ogni 7 giorni come la (a): differenza piccola per costruzione → se il segnale è acceso >80% dei giorni la variante non si distingue; lo vedo dal numero di trade rispetto alla (a).
10. *Effetto funding.* Il long in regime di funding positivo (2020-21) paga funding, lo short lo incassa: l'R netto cambia per il funding, non per il prezzo → smentita se il funding totale è piccolo rispetto alla differenza.

**Ipotesi completa.** BCHUSDT, momento della serie, candele 1d (il meccanismo è su settimane;
1d è la candela più fine che ha senso per un rendimento a 7 giorni), due varianti.

| Variante | Direzione | Regole |
|---|---|---|
| BCHUSDT-001 | long | alla chiusura del giorno, se close/close di 7 giorni prima − 1 > 0: long all'apertura dopo; stop 2,5 × ATR(14 giorni) sotto il close; nessun target; uscita all'apertura dopo 7 giorni tenuti |
| BCHUSDT-002 | short | specchio: rendimento a 7 giorni < 0, short, stop 2,5 ATR sopra, uscita dopo 7 giorni |

Motivo dei parametri: 7 giorni = orizzonte di Liu e Tsyvinski; 2,5 ATR è uno stop largo che
lascia lavorare una tenuta di una settimana (il momento si misura sul rendimento a scadenza,
non su uno stop stretto). Lo stop supera spesso il 6% del bot: dichiarato.
Costo di un giro ≈ 0,14% / ~12% ≈ 0,01 R.

---

## I-02 — Rottura del canale dei massimi e minimi (4h)

**Fonte.** W. Brock, J. Lakonishok, B. LeBaron, «Simple Technical Trading Rules and the
Stochastic Properties of Stock Returns», *Journal of Finance* 47(5), dicembre 1992 (regola
della rottura del range); C. Faith, *Way of the Turtle*, McGraw-Hill, 2007 (ingresso sulla
rottura del massimo di N periodi, stop a 2 volte l'ATR, uscita sulla rottura del minimo di N/2
periodi).

**Affermazione verificabile.** Dopo una chiusura sopra il massimo delle 20 barre precedenti
(sotto il minimo), il prezzo continua nella direzione della rottura più di quanto faccia dopo un
ingresso qualunque con la stessa uscita.

**Sotto-domande.** Vale di più con volatilità compressa prima della rottura? Chi muove il
prezzo: ordini stop accumulati oltre i massimi/minimi recenti e trend follower che entrano
sulla rottura; chi vende allo scoperto sotto un massimo viene costretto a ricoprire. Tempo:
ore o pochi giorni; l'uscita a 10 barre lascia correre.

**Spiegazioni concorrenti:**
1. *Caso* → `t` contro la (b) sotto 2; smentita da `t` netto.
2. *Trend di fondo* → il long vince nel 2020-21, lo short nel 2022 come la (b); smentita se batte la (b) anno per anno.
3. *È solo il mercato* → le rotture di BCH coincidono con quelle di BTC; resterebbe comunque un vantaggio su BCH, ma non specifico; lo annoto.
4. *Falsa rottura (inversione)* → in un mercato laterale le rotture rientrano: R medio sotto la (b) (previsione opposta) → segno del `t`.
5. *Volatilità* → dopo la rottura la volatilità sale e con uno stop a 2 ATR lo stop scatta spesso; neutralizzata dalla (b) con lo stesso stop.
6. *Pochi trade estremi* → poche corse lunghe fanno tutto (tipico delle regole di trend); smentita se l'R senza i 3 migliori resta sopra la (b).
7. *Costi* → stop ~3,6% → costi ~0,04 R; con slippage vero più alto nel 2020/2022 ~0,06 R: un vantaggio sotto 0,05 R è dentro i costi; smentita se regge a costi doppi.
8. *Artefatto dei dati* → barre tolte del 2022-10-02 creano una falsa rottura dopo il buco; al massimo un trade.
9. *Uscita, non ingresso* → l'uscita sul minimo di 10 barre da sola fa il risultato (la (a) con la stessa uscita lo mostrerebbe): smentita se batte nettamente la (a).
10. *Funding* → il long paga funding nel 2020-21; piccolo su tenute di giorni; smentita se il funding totale è piccolo rispetto alla differenza.

**Ipotesi completa.** BCHUSDT, rottura del canale, candele 4h (le rotture che gli operatori
vedono sono quelle di giorni; su 1d le rotture di 20 giorni darebbero troppo pochi trade, su
4h 20 barre sono 3,3 giorni), due varianti.

| Variante | Direzione | Regole |
|---|---|---|
| BCHUSDT-003 | long | close > massimo dei massimi delle 20 barre precedenti: long all'apertura dopo; stop 2 × ATR(20) sotto il close; nessun target; uscita all'apertura dopo la prima chiusura sotto il minimo dei minimi delle 10 barre precedenti |
| BCHUSDT-004 | short | specchio |

Costo di un giro ≈ 0,04 R.

---

## I-03 — RSI a 2 periodi nel verso della media lunga (4h)

**Fonte.** L. Connors, C. Alvarez, *Short Term Trading Strategies That Work*, TradingMarkets
Publishing, 2008: comprare quando l'RSI a 2 periodi scende sotto 10 con il prezzo sopra la
media a 200 periodi, uscire alla chiusura sopra la media a 5 periodi (e lo specchio per lo short).

**Affermazione verificabile.** Dentro un trend (prezzo sopra la media a 200 barre), un ribasso
brusco di 1-3 barre (RSI(2) < 10) viene recuperato in media più di quanto renda un ingresso
qualunque con la stessa uscita; specchio per i rialzi bruschi sotto la media.

**Sotto-domande.** Vale di più quando il calo è accompagnato da volumi alti (venditori
forzati)? Chi muove il prezzo: chi ha bisogno di liquidità vende in fretta, chi fornisce
liquidità compra a sconto e rivende al rientro. Tempo: poche barre.

**Spiegazioni concorrenti:**
1. *Caso* → `t` < 2; smentita da `t` netto.
2. *Trend di fondo* → comprare i cali sopra la media funziona solo negli anni di rialzo; smentita se batte la (b) anno per anno (la (b) entra a caso sopra e sotto la media? no: la (b) entra a caso fra le barre valide, quindi anche il filtro della media è un pezzo dell'ipotesi; lo distinguo con la (a), che non ha né RSI né media).
3. *È solo il mercato* → i cali di BCH sono i cali di BTC; annoto.
4. *Continuazione* → nelle crypto i cali bruschi continuano (cascate di liquidazioni): R medio sotto la (b) → segno del `t`.
5. *Volatilità* → dopo il calo la volatilità è alta e l'R cambia scala; neutralizzata dalla (b).
6. *Pochi trade estremi* → un paio di rimbalzi enormi (es. marzo 2020, se passa il filtro); smentita senza i 3 migliori.
7. *Costi* → stop ~5%, costi ~0,03 R; le tenute brevi rendono poco: un vantaggio < 0,05 R è fragile; costi doppi.
8. *Uscita* → l'uscita sopra la media a 5 da sola esce presto sui guadagni e tardi sulle perdite; la (a) con la stessa uscita lo misura.
9. *Artefatto del timeframe* → la regola è stata pensata su candele giornaliere di azioni: su 4h crypto 24 ore su 24 i «cali brevi» sono rumore; previsione: nessun vantaggio.
10. *Funding* → piccolo su tenute brevi.

**Ipotesi completa.** BCHUSDT, inversione di breve dentro il trend, candele 4h (su 1d la
regola entra poche volte l'anno; 4h tiene le stesse proporzioni: 200 barre ≈ 33 giorni, 5 barre
≈ 20 ore), due varianti.

| Variante | Direzione | Regole |
|---|---|---|
| BCHUSDT-005 | long | RSI(2) < 10 e close > media semplice a 200 barre: long all'apertura dopo; stop di sicurezza 3 × ATR(14) sotto il close; nessun target; uscita all'apertura dopo la prima chiusura sopra la media semplice a 5 barre |
| BCHUSDT-006 | short | RSI(2) > 90 e close < media a 200: short; stop 3 ATR sopra; uscita dopo la prima chiusura sotto la media a 5 |

Lo stop non è nella fonte (che non ne usa): è uno stop di sicurezza largo, richiesto dal motore
e dal bot. Costo ≈ 0,03 R.

---

## I-04 — Rottura di volatilità dall'apertura del giorno (1h)

**Fonte.** L. Williams, *Long-Term Secrets to Short-Term Trading*, Wiley, 1999: comprare
quando il prezzo supera l'apertura del giorno di una frazione del range del giorno prima
(«volatility breakout»), uscire alla prima apertura successiva.

**Affermazione verificabile.** Quando nel giorno UTC il prezzo chiude un'ora sopra apertura +
0,5 × range del giorno prima (sotto apertura − 0,5 × range), il resto della giornata continua in
quella direzione più di un ingresso orario qualunque con la stessa uscita.

**Sotto-domande.** Vale di più nelle giornate che seguono un range stretto? Chi muove il
prezzo: un'espansione di range segnala l'arrivo di ordini direzionali grandi (informazione o
flussi), che si eseguono durante la giornata. Tempo: ore, fino alla fine del giorno.

**Spiegazioni concorrenti:**
1. *Caso* → `t` < 2.
2. *Trend di fondo* → il long vince solo negli anni di rialzo; anno per anno con la (b).
3. *È solo il mercato* → le giornate di espansione sono quelle di BTC; annoto.
4. *Inversione intraday* → nelle crypto le rotture intraday rientrano entro sera: R sotto la (b).
5. *Volatilità* → nelle giornate di espansione lo stop (all'apertura del giorno) è lontano e l'R ha un'altra scala; la (b) usa lo stesso stop calcolato allo stesso modo nelle barre valide.
6. *Pochi trade estremi* → poche giornate di crollo/rialzo enormi; senza i 3 migliori.
7. *Costi* → stop medio stimato ~3% → 0,05 R; vantaggio piccolo mangiato dai costi; costi doppi.
8. *Confine del giorno UTC* → il «giorno» UTC è arbitrario per un mercato 24/7: se l'effetto esiste dovrebbe dipendere poco da dove cade il confine (non lo verifico come variante: lo annoto come limite).
9. *Orario* → le rotture cadono in ore precise (apertura USA) e l'effetto è dell'orario, non della rottura; la (b) entra in ore qualunque: se vince solo per l'orario resterebbe un vantaggio, ma di un'altra idea.
10. *Artefatto dei dati* → giorni incompleti (2022-10-02 senza mark) escludono il range del giorno dopo: la regola salta quei giorni (nessun segnale), non crea trade falsi.

**Ipotesi completa.** BCHUSDT, rottura di volatilità intraday, candele 1h (il meccanismo è
dentro la giornata: serve una candela più corta del giorno; 1h tiene i costi sotto controllo
rispetto a 15m), due varianti.

| Variante | Direzione | Regole |
|---|---|---|
| BCHUSDT-007 | long | giorno UTC con prima barra alle 00:00 e giorno precedente completo (24 barre); alla prima chiusura oraria del giorno sopra apertura del giorno + 0,5 × (massimo − minimo del giorno prima): long all'apertura dopo; stop all'apertura del giorno; nessun target; uscita all'apertura del giorno dopo (00:00); nessun segnale alla barra delle 23:00 |
| BCHUSDT-008 | short | specchio: prima chiusura sotto apertura − 0,5 × range; stop all'apertura del giorno |

k = 0,5 è il valore più usato nella fonte. Costo ≈ 0,05 R.
