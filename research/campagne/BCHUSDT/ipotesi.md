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

---

## I-05 — Attraversamento dei livelli tondi (1h)

**Fonte.** C. L. Osler, «Currency Orders and Exchange Rate Dynamics: An Explanation for the
Predictive Success of Technical Analysis», *Journal of Finance* 58(5), ottobre 2003: gli ordini
stop si accumulano appena oltre i numeri tondi; quando il prezzo li attraversa, gli stop
eseguiti spingono il prezzo nella stessa direzione (trend rapidi dopo l'attraversamento).

**Affermazione verificabile.** Dopo una chiusura oraria che attraversa verso l'alto (il basso)
un multiplo di 10 USDT (di 100 sopra 1.000 USDT), il prezzo delle 12 ore successive va in
quella direzione più di un ingresso orario qualunque con la stessa uscita.

**Sotto-domande.** Più forte sui multipli di 50 e 100 che su quelli di 10? Chi muove il
prezzo: stop dei venditori allo scoperto sopra il numero tondo (compre forzate), stop dei long
sotto (vendite forzate). Tempo: ore.

**Spiegazioni concorrenti:**
1. *Caso* → `t` < 2.
2. *Trend di fondo* → più attraversamenti verso l'alto negli anni di rialzo: la (b) ha la stessa direzione, il confronto lo neutralizza anno per anno.
3. *È solo il mercato* → annoto.
4. *Ordini take-profit sui tondi (inversione)* → Osler trova anche inversioni AL numero tondo: chi attraversa può rientrare; R sotto la (b).
5. *Il passo è arbitrario* → con il prezzo fra 100 e 1.600 USDT il passo 10 è circa 1-3% (molti attraversamenti) e il passo 100 sopra 1.000 è circa 7-10%: l'effetto sarebbe diverso per livello; non lo separo in questa variante.
6. *Volatilità* → più attraversamenti nelle ore volatili; neutralizzata dalla (b).
7. *Costi* → stop a 1 ATR orario sotto il livello, ~1,5% → costi ~0,09 R: il vantaggio deve essere grande; costi doppi.
8. *Pochi trade estremi* → senza i 3 migliori.
9. *Artefatto: attraversamenti a ripetizione* → il prezzo che oscilla attorno a un tondo dà molti segnali in poche ore; la tenuta di 12 barre e una posizione alla volta li riducono.
10. *Il numero tondo non è visibile a tutti* → su un perpetuo in USDT i livelli psicologici sono quelli del prezzo in dollari, coerente: nessuna previsione diversa.

**Ipotesi completa.** BCHUSDT, ordini sui numeri tondi, candele 1h (l'effetto è di ore), due varianti.

| Variante | Direzione | Regole |
|---|---|---|
| BCHUSDT-009 | long | passo = 10^(cifre intere del close precedente − 2) (10 fra 100 e 999, 100 fra 1.000 e 9.999); la chiusura precedente ≤ un multiplo del passo < la chiusura attuale: long all'apertura dopo; stop al livello attraversato − 1 × ATR(24 ore); nessun target; uscita dopo 12 barre tenute |
| BCHUSDT-010 | short | specchio: attraversamento verso il basso; stop al livello + 1 ATR |

Costo ≈ 0,05-0,10 R.

---

## I-06 — Inerzia dopo le giornate di sovra-reazione (1d)

**Fonte.** G. M. Caporale, A. Plastun, «Price overreactions in the cryptocurrency market»,
*Journal of Economic Studies* 46(5), 2019 (CESifo Working Paper 6861, gennaio 2018): dopo una
giornata di sovra-reazione il movimento del giorno dopo è più ampio; una strategia di inerzia
(nella direzione della sovra-reazione) sembrava redditizia ma non distinguibile dal caso.

**Affermazione verificabile.** Dopo un giorno con rendimento apertura-chiusura oltre la media
più una deviazione standard dei rendimenti assoluti dei 30 giorni precedenti (verso l'alto o il
basso), il giorno dopo va nella stessa direzione più di un giorno qualunque.

**Sotto-domande.** Più forte dopo i ribassi (liquidazioni a catena) o dopo i rialzi? Chi muove
il prezzo: notizie che si incorporano in più giorni, rincorsa di chi arriva tardi. Tempo: un giorno.

**Spiegazioni concorrenti:**
1. *Caso* → la fonte stessa dice «non distinguibile dal caso»: prior basso.
2. *Inversione (sovra-reazione vera)* → il giorno dopo rientra: R sotto la (b).
3. *Trend di fondo* → anno per anno con la (b).
4. *È solo il mercato* → annoto.
5. *Volatilità a grappoli* → dopo un giorno estremo la volatilità resta alta; senza direzione non dà R positivo con la (b) che usa lo stesso stop.
6. *Pochi trade estremi* → senza i 3 migliori.
7. *Costi* → stop 2 ATR giornalieri (~10%), costi ~0,015 R: irrilevanti.
8. *Artefatto del confine del giorno UTC* → il rendimento apertura-chiusura dipende dall'ora del confine; annoto.
9. *Funding* → piccolo su un giorno.
10. *Soglia mobile* → nei periodi calmi anche un movimento modesto passa la soglia; nessuna previsione diversa, ma rende il segnale meno «estremo».

**Ipotesi completa.** BCHUSDT, inerzia dopo la sovra-reazione, candele 1d (come la fonte), due varianti.

| Variante | Direzione | Regole |
|---|---|---|
| BCHUSDT-011 | long | close/open − 1 del giorno > media + 1 deviazione standard dei |close/open − 1| dei 30 giorni prima: long all'apertura dopo; stop 2 × ATR(14) sotto il close; uscita all'apertura successiva (1 giorno) |
| BCHUSDT-012 | short | specchio: close/open − 1 < −(media + 1 deviazione standard) |

---

## I-07 — Il lunedì (1d)

**Fonte.** G. M. Caporale, A. Plastun, «The day of the week effect in the cryptocurrency
market», *Finance Research Letters* 31, 2019 (online novembre 2018; CESifo WP 6716, ottobre
2017): i rendimenti di BTC il lunedì sono più alti degli altri giorni; le altre monete studiate
(LTC, XRP, DASH) non mostrano l'anomalia.

**Affermazione verificabile.** Il rendimento di BCHUSDT dal lunedì 00:00 al martedì 00:00 UTC
è più alto di quello di un giorno qualunque con la stessa uscita.

**Sotto-domande.** È un effetto di BTC trasmesso a BCH? Chi muove il prezzo: riapertura dei
mercati tradizionali e flussi istituzionali dopo il fine settimana. Tempo: un giorno.

**Spiegazioni concorrenti:**
1. *Caso* → con ~146 lunedì in costruzione, un effetto di 0,5% al giorno è sotto il rumore (~5% di deviazione giornaliera): prior molto basso.
2. *La fonte trova l'effetto solo per BTC* → su BCH nessun effetto.
3. *È solo il mercato* → se c'è, è quello di BTC; annoto.
4. *Trend di fondo* → la (b) long ha lo stesso trend.
5. *Pochi lunedì estremi* → senza i 3 migliori.
6. *Volatilità del lunedì* → più movimento ma senza direzione.
7. *Costi* → ~0,015 R.
8. *Il confine UTC* → il «lunedì» dei mercati tradizionali comincia più tardi (Asia/Europa/USA); annoto.
9. *Funding* → piccolo.
10. *Artefatto di selezione nella fonte* → l'effetto è stato trovato su un periodo e una moneta; previsione: non si ripete fuori campione.

**Ipotesi completa.** BCHUSDT, calendario, candele 1d, una sola variante (la fonte indica il long).

| Variante | Direzione | Regole |
|---|---|---|
| BCHUSDT-013 | long | alla chiusura della domenica: long all'apertura del lunedì; stop 2 × ATR(14) sotto il close; uscita all'apertura del martedì |

---

## I-08 — Il premio del volume alto (1d)

**Fonte.** S. Gervais, R. Kaniel, D. H. Mingelgrin, «The High-Volume Return Premium», *Journal
of Finance* 56(3), giugno 2001: dopo un volume insolitamente alto (fra il 10% più alto dei 50
giorni), il titolo rende di più nel mese successivo; spiegazione: la visibilità attira nuovi
compratori.

**Affermazione verificabile.** Dopo un giorno con volume in USDT sopra il 90° percentile dei 49
giorni precedenti, i 10 giorni successivi rendono più di un periodo qualunque di 10 giorni con
la stessa uscita.

**Sotto-domande.** Dipende dal segno del rendimento del giorno di volume? Chi muove il prezzo:
nuovi compratori attirati dall'attenzione; nelle crypto il volume alto spesso coincide con i
crolli. Tempo: 1-4 settimane (10 giorni per avere abbastanza trade).

**Spiegazioni concorrenti:**
1. *Caso* → `t` < 2.
2. *Volume alto = capitolazione* → nelle crypto i giorni di volume massimo sono spesso crolli; dopo, rimbalzo (vantaggio long) o continuazione (svantaggio); previsione ambigua.
3. *Trend di fondo* → anno per anno con la (b).
4. *È solo il mercato* → il volume alto di BCH coincide con quello del mercato; annoto.
5. *Volatilità* → dopo il volume alto la volatilità resta alta; lo stop in ATR si allarga; neutralizzato dalla (b).
6. *Pochi trade estremi* → senza i 3 migliori.
7. *Costi* → stop 3 ATR (~15%) → costi ~0,01 R.
8. *Il meccanismo è delle azioni poco seguite* → BCH è già molto visibile: nessun effetto.
9. *Artefatto di volume* → volumi gonfiati da eventi tecnici (es. maggio 2021) concentrati in pochi giorni; senza i 3 migliori.
10. *Funding* → il long paga funding nel 2020-21; piccolo.

**Ipotesi completa.** BCHUSDT, attenzione e volume, candele 1d, una variante (il meccanismo della fonte è solo rialzista).

| Variante | Direzione | Regole |
|---|---|---|
| BCHUSDT-014 | long | volume in USDT del giorno > 90° percentile dei 49 giorni precedenti: long all'apertura dopo; stop 3 × ATR(14) sotto il close; uscita dopo 10 giorni tenuti |

---

## I-09 — Inversione dei movimenti grandi con volume alto (4h)

**Fonte.** J. Y. Campbell, S. J. Grossman, J. Wang, «Trading Volume and Serial Correlation in
Stock Returns», *Quarterly Journal of Economics* 108(4), novembre 1993: i movimenti di prezzo
accompagnati da volume alto tendono a invertirsi (chi chiede liquidità per motivi non
informativi paga uno sconto a chi la fornisce, e il prezzo poi rientra).

**Affermazione verificabile.** Dopo una barra di 4 ore con rendimento oltre 2 deviazioni
standard (delle 100 barre precedenti) e volume oltre il doppio della media delle 100 barre
precedenti, le 24 ore successive vanno in direzione opposta più di un ingresso qualunque con la
stessa uscita.

**Sotto-domande.** Più forte dopo i ribassi (liquidazioni forzate) che dopo i rialzi? Chi muove
il prezzo: venditori forzati e chi assorbe. Tempo: ore, un giorno.

**Spiegazioni concorrenti:**
1. *Caso* → `t` < 2.
2. *Continuazione per informazione* → il volume alto porta notizie vere: il movimento continua; R sotto la (b).
3. *Cascate di liquidazioni* → nelle crypto il calo con volume può continuare per ore prima di invertire: l'ingresso alla barra dopo è presto; previsione: R negativo nelle prime barre.
4. *Trend di fondo* → anno per anno con la (b).
5. *È solo il mercato* → annoto.
6. *Volatilità* → neutralizzata dalla (b).
7. *Pochi trade estremi* → un paio di rimbalzi (marzo 2020); senza i 3 migliori.
8. *Costi* → stop 2,5 ATR(4h) ~4,5% → costi ~0,03 R.
9. *Pochi segnali* → la doppia condizione può dare pochi trade: lo dice la conta.
10. *Artefatto dei dati* → barre dopo il buco del 2022-10-02: il rendimento della prima barra dopo il buco è su 28 ore; al massimo un segnale.

**Ipotesi completa.** BCHUSDT, inversione con volume, candele 4h, due varianti.

| Variante | Direzione | Regole |
|---|---|---|
| BCHUSDT-015 | long | rendimento della barra / deviazione standard dei rendimenti delle 100 barre prima < −2 e volume in USDT > 2 × media delle 100 barre prima: long all'apertura dopo; stop 2,5 × ATR(14) sotto il close; uscita dopo 6 barre tenute |
| BCHUSDT-016 | short | specchio: rendimento standardizzato > +2 con volume > 2 volte la media |

---

## I-10 — Funding estremo: la parte affollata paga (8h)

**Fonte.** S. He, A. Manela, O. Ross, V. von Wachter, «Fundamentals of Perpetual Futures»,
arXiv 2212.06888, prima versione dicembre 2022: il funding misura lo scarto fra perpetuo e
spot, cioè lo squilibrio della domanda di leva; gli scarti sono grandi e si chiudono.
Riformulazione mia (da dichiarare): un funding molto alto indica long a leva affollati, che
chiudono o vengono liquidati e spingono il prezzo in basso; specchio per il funding molto basso.

**Affermazione verificabile.** Dopo un settlement con tasso di funding sopra il 90° percentile
dei 90 settlement precedenti (30 giorni), le 24 ore successive rendono meno di un ingresso
qualunque (short); dopo un tasso sotto il 10° percentile rendono di più (long).

**Sotto-domande.** Vale solo sopra soglie assolute (es. oltre 0,05%)? Chi muove il prezzo: chi
è a leva dalla parte affollata, chi fa arbitraggio (vende perpetuo, compra spot). Tempo: ore, giorni.

**Spiegazioni concorrenti:**
1. *Caso* → `t` < 2.
2. *Momento* → il funding alto segue i rialzi e i rialzi continuano: R dello short sotto la (b).
3. *L'arbitraggio chiude lo scarto sul perpetuo, non sul prezzo* → lo scarto si chiude con il perpetuo che scende verso lo spot di poco (0,05%): troppo poco per un R visibile; nessun vantaggio.
4. *Trend di fondo* → funding alto nel 2020-21 (rialzo): lo short perde con il trend; la (b) short ha lo stesso trend.
5. *È solo il mercato* → il funding di BCH segue quello di tutto il mercato; annoto.
6. *Il percentile mobile non è «estremo»* → nei periodi calmi il decile alto è un funding normale; previsione: effetto diluito.
7. *Costi e funding* → lo short incassa il funding alto: l'R migliora per il funding incassato, non per il prezzo; lo separo guardando il funding totale.
8. *Volatilità* → neutralizzata dalla (b).
9. *Pochi trade estremi* → senza i 3 migliori.
10. *Artefatto dell'istante* → il tasso del settlement si conosce al settlement (apertura della barra); il segnale usa il settlement all'apertura della barra appena chiusa: nessun anticipo.

**Ipotesi completa.** BCHUSDT, posizionamento a leva, candele 8h (allineate ai settlement di 8
ore: 00, 08, 16 UTC), due varianti.

| Variante | Direzione | Regole |
|---|---|---|
| BCHUSDT-017 | short | tasso del settlement all'apertura della barra > 90° percentile dei 90 settlement precedenti: short all'apertura dopo; stop 2 × ATR(14 barre) sopra il close; uscita dopo 3 barre tenute (24 ore) |
| BCHUSDT-018 | long | tasso < 10° percentile dei 90 precedenti: long; stop 2 ATR sotto; uscita dopo 3 barre |

---

## I-11 — Flusso degli ordini aggressivi (1h)

**Fonte.** M. D. D. Evans, R. K. Lyons, «Order Flow and Exchange Rate Dynamics», *Journal of
Political Economy* 110(1), febbraio 2002: il flusso netto degli ordini aggressivi porta
informazione e ha un effetto persistente sul prezzo.

**Affermazione verificabile.** Quando la quota degli acquisti aggressivi (volume in USDT dei
compratori taker / volume totale) delle ultime 4 ore supera di 2 deviazioni standard la sua
media dei 30 giorni precedenti, le 4 ore successive salgono più di un ingresso orario
qualunque (specchio per le vendite aggressive).

**Sotto-domande.** Il flusso predice o accompagna soltanto il prezzo? Chi muove il prezzo:
operatori informati che eseguono a pezzi. Tempo: ore.

**Spiegazioni concorrenti:**
1. *Caso* → `t` < 2.
2. *Effetto contemporaneo, non predittivo* → il flusso muove il prezzo nella stessa ora e poi basta: nessun vantaggio dopo.
3. *Inversione* → il prezzo spinto dal flusso rientra (pressione temporanea): R sotto la (b).
4. *Trend di fondo* → anno per anno.
5. *È solo il mercato* → annoto.
6. *Costi* → stop 2 ATR orari ~2,5% → costi ~0,06 R; con tenuta di 4 ore il movimento atteso è piccolo: serve un vantaggio grande.
7. *Volatilità* → neutralizzata dalla (b).
8. *Artefatto della colonna* → la colonna taker_buy dei file Binance è ciò che dichiara di essere (acquisti dal lato taker); nessuna verifica indipendente.
9. *Pochi trade estremi* → senza i 3 migliori.
10. *Robot di mercato* → negli anni la quota cambia per la struttura del mercato; la standardizzazione mobile lo assorbe in parte.

**Ipotesi completa.** BCHUSDT, flusso degli ordini, candele 1h, due varianti.

| Variante | Direzione | Regole |
|---|---|---|
| BCHUSDT-019 | long | quota acquisti aggressivi delle ultime 4 barre, standardizzata con media e deviazione standard delle 720 barre precedenti, > +2: long all'apertura dopo; stop 2 × ATR(24) sotto il close; uscita dopo 4 barre tenute |
| BCHUSDT-020 | short | specchio: standardizzata < −2 |

---

## I-12 — Compressione delle bande di Bollinger e rottura (4h)

**Fonte.** J. Bollinger, *Bollinger on Bollinger Bands*, McGraw-Hill, 2001: una larghezza delle
bande al minimo di mesi («squeeze») precede un'espansione di volatilità; la direzione si prende
dalla rottura della banda.

**Affermazione verificabile.** Se la larghezza delle bande (20 barre, 2 deviazioni) ha toccato
nelle ultime 10 barre il minimo delle ultime 125 barre (~21 giorni), una chiusura sopra la banda
superiore (sotto l'inferiore) è seguita da un movimento nella stessa direzione maggiore di un
ingresso qualunque con la stessa uscita.

**Sotto-domande.** Chi muove il prezzo: ordini accumulati durante la calma che si eseguono alla
rottura; venditori di volatilità che coprono. Tempo: giorni.

**Spiegazioni concorrenti:**
1. *Caso* → `t` < 2.
2. *Falsa rottura* → la prima rottura dopo la calma rientra («head fake», citato dallo stesso Bollinger): R sotto la (b).
3. *Trend di fondo* → anno per anno.
4. *È solo il mercato* → annoto.
5. *Volatilità* → dopo la compressione la volatilità sale per costruzione (ritorno alla media), senza direzione; la (b) usa lo stesso stop ma entra anche fuori dalla compressione: la (b) e la (a) misurano cose diverse.
6. *Pochi trade estremi* → senza i 3 migliori.
7. *Costi* → stop 2 ATR(4h) ~3,5% → costi ~0,04 R.
8. *Pochi segnali* → la doppia condizione può dare pochi trade: lo dice la conta.
9. *Uscita* → l'uscita sulla media a 20 da sola fa il risultato; la (a) lo misura.
10. *Somiglianza con I-02* → è anche una rottura, ma condizionata alla calma: se vince solo come rottura, I-02 lo avrebbe mostrato.

**Ipotesi completa.** BCHUSDT, compressione di volatilità, candele 4h, due varianti.

| Variante | Direzione | Regole |
|---|---|---|
| BCHUSDT-021 | long | minimo della larghezza (4 × deviazione standard / media, 20 barre) delle ultime 10 barre ≤ minimo delle ultime 125 barre, e close > media + 2 deviazioni: long all'apertura dopo; stop 2 × ATR(14) sotto il close; uscita all'apertura dopo la prima chiusura sotto la media a 20 |
| BCHUSDT-022 | short | specchio: close < media − 2 deviazioni; uscita alla prima chiusura sopra la media |

---

## I-13 — Il prezzo sopra la media mobile (1d)

**Fonte.** A. Detzel, H. Liu, J. Strauss, G. Zhou, Y. Zhu, «Bitcoin: Predictability and
Profitability via Technical Analysis», working paper, gennaio 2018 (pubblicato come «Learning
and predictability via technical analysis: Evidence from bitcoin and stocks with hard-to-value
fundamentals», *Financial Management* 50(1), 2021): il rapporto fra prezzo e media mobile (5-100
giorni) predice i rendimenti giornalieri di BTC; con fondamentali difficili da valutare gli
investitori imparano dai prezzi.

**Affermazione verificabile.** Dopo che il close giornaliero passa sopra la media a 20 giorni
(sotto), i giorni fino al ritorno sotto (sopra) la media rendono più di un ingresso qualunque con
la stessa uscita.

**Sotto-domande.** Chi muove il prezzo: investitori che imparano lentamente dai prezzi. Tempo:
settimane.

**Spiegazioni concorrenti:**
1. *Caso* → `t` < 2.
2. *Falsi incroci* → in laterale gli incroci si ripetono e perdono i costi: R sotto la (b).
3. *Trend di fondo* → anno per anno.
4. *È solo il mercato* → lo studio è su BTC; per BCH è trasmissione; annoto.
5. *Somiglianza con I-01 e I-02* → è un'altra misura di trend; se vince, va confrontata con le altre due famiglie di trend (Fase 5).
6. *Pochi trade estremi* → le regole di trend vivono di poche corse lunghe; senza i 3 migliori.
7. *Costi* → stop 3 ATR (~15%) → ~0,01 R.
8. *Uscita* → l'uscita sulla media da sola fa il risultato; la (a) lo misura.
9. *Volatilità* → neutralizzata dalla (b).
10. *Funding* → il long paga nel 2020-21.

**Ipotesi completa.** BCHUSDT, apprendimento dai prezzi, candele 1d, due varianti (la fonte usa
long o liquidità; lo short è lo specchio e lo provo come variante separata).

| Variante | Direzione | Regole |
|---|---|---|
| BCHUSDT-023 | long | close > media a 20 giorni e close precedente ≤ media precedente: long all'apertura dopo; stop di sicurezza 3 × ATR(14) sotto il close; uscita all'apertura dopo la prima chiusura sotto la media |
| BCHUSDT-024 | short | specchio |
