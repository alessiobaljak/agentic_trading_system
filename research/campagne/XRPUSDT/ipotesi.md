# XRPUSDT — Ipotesi (Fase 1)

Scritto il 2026-10-09, prima di qualunque conteggio dei trade e di qualunque test. Ogni idea ha la
sua fonte pubblicata prima del 2024-01-01; nessuna viene da risultati del gate, del registro, del
paper o di altre monete. Le varianti di ogni idea sono tutte scritte qui, con il motivo, prima del
primo test di quell'idea (regola 6). I numeri dei trade (`conta_trade`) stanno nel log.

Cosa ho visto dei dati prima di scrivere: solo i fatti della Fase 0 (`fase0_dati.md`: buchi,
volume, funding medio per anno) e la mediana dell'ATR(14) per timeframe sulla costruzione (per il
costo di un giro in R, `codice/costo_giro.py`). Ho visto anche l'esito del controllo positivo (voce
XRPUSDT-N006): con il ritardo di una barra, la regola «entra dopo una barra a 1 ora salita di almeno
lo 0,3%» batte la (b) con `t` 4,7 ma ha R medio negativo. Lo dichiaro perché è un'informazione sui
prezzi di costruzione: l'elenco delle idee qui sotto era già fissato prima (le idee nascono dalle
fonti), e nessuna variante usa quella regola.

## Regole comuni a tutte le varianti

* **Ingresso**: il segnale si calcola alla chiusura della barra i (solo barre chiuse), si entra
  all'apertura della barra i + 1 (motore, sezione 7).
* **Stop**: distanza = minimo fra k × ATR(14) del timeframe della variante e il 6% della chiusura
  della barra del segnale. Il 6% è il tetto dello stop del bot (`stop_massimo_bot`,
  `config/parametri.yaml`): così ogni variante è eseguibile dal bot così com'è. Sui timeframe
  lenti (4h e oltre, ATR mediano 2,8-7,7%) il tetto è spesso quello che decide.
* **Uscita a tempo**: con la posizione aperta alla barra j, alla chiusura della barra
  j + tenuta − 1 si chiude all'apertura della barra dopo. Tutte le tenute sono sotto le 96 barre
  dell'orizzonte del bot.
* **Dimensione e leva**: quelle del bot (rischio 1%, leva massima 2, isolated) via il motore.
* **Mesi illiquidi**: nessuno (Fase 0), il filtro esiste ma non toglie barre.
* **Costo di un giro** (0,14% del nozionale) in R, con lo stop tipico (mediana dell'ATR(14) sulla
  costruzione): 15m 0,145 R a 1,5 ATR; 30m 0,10 R; 1h 0,069 R; 2h 0,048 R; 4h 0,033 R (stop 4,2%);
  8h 0,022 R (stop già oltre il 6% a 1,5 ATR: col tetto 0,023 R); 1d stop sempre al tetto del 6%:
  0,023 R. Le previsioni qui sotto sono al netto di questo costo.

## Spiegazioni concorrenti comuni

Per ogni idea le spiegazioni concorrenti sono almeno dieci: le sette comuni qui sotto (G1-G7),
ognuna con la previsione e la smentita SPECIFICHE dell'idea scritte nella sua tabella, più quelle
proprie dell'idea (S1, S2, ...).

* **G1 Caso**: l'effetto è rumore. Prevede: nessuna differenza netta dalla (b); R medio per anno
  di segno variabile. Smentita: `t` contro la (b) sopra la soglia e R per anno dello stesso segno.
* **G2 Volatilità**: la condizione d'ingresso seleziona barre di volatilità diversa, e con stop e
  uscita in ATR il risultato in R cambia per questo, non per la direzione. Prevede: anche la (b)
  ristretta alle stesse condizioni di volatilità farebbe lo stesso; la quota di uscite a stop e a
  tempo diversa dalla (b). Smentita: il vantaggio resta guardando la direzione dei trade
  (rendimento medio in direzione) e non solo l'R.
* **G3 Trend di fondo**: la direzione è giusta perché il mercato nel periodo saliva (2020-2021) o
  scendeva (2022). Prevede: battere la (a) ma non la (b) (la (b) entra a caso nella stessa
  direzione); R per anno che segue il buy and hold. Smentita: batte la (b) in anni con buy and
  hold di segno opposto.
* **G4 Artefatto dei dati**: buchi, barre tolte, la prima settimana di gennaio 2020, candele
  anomale. Prevede: risultato concentrato in pochi trade vicino ai buchi. Smentita: risultato
  uguale senza i 3 trade migliori e senza trade a cavallo dei buchi.
* **G5 Costi**: il vantaggio lordo c'è ma è più piccolo del costo di un giro. Prevede: R medio
  lordo positivo e netto negativo. Smentita: R netto positivo anche a costi doppi.
* **G6 È solo il mercato**: XRP segue BTC; la regola cattura i movimenti comuni. Prevede: il
  rendimento di BTC nella stessa finestra dei trade, nella stessa direzione, ha lo stesso segno e
  una grandezza simile. Smentita: rendimento di BTC nella finestra dei trade vicino a zero o
  opposto.
* **G7 Lo fa l'uscita, non l'ingresso**: stop e uscita a tempo producono il risultato con
  qualunque ingresso. Prevede: la (a) e la (b) hanno R medio simile al candidato. Smentita:
  batte nettamente la (a) e la (b), che hanno la stessa uscita.

---

## I-01 — Momentum a una settimana

1. **Fonte**: Yukun Liu e Aleh Tsyvinski, «Risks and Returns of Cryptocurrency», NBER Working
   Paper 24877, agosto 2018 (poi Review of Financial Studies, 2021). Base generale: Tobias
   Moskowitz, Yao Hua Ooi e Lasse Heje Pedersen, «Time Series Momentum», Journal of Financial
   Economics 104(2), maggio 2012.
2. **Affermazione verificabile**: dopo una settimana con rendimento positivo, XRP rende nella
   settimana dopo più di una settimana presa a caso nella stessa direzione; dopo una settimana
   negativa, la settimana dopo rende meno (lo short guadagna più del caso). Falsa se l'R medio
   delle entrate dopo settimane positive (negative) non supera la (b) long (short).
3. **Sotto-domande**: vale dopo settimane di grande movimento o anche piccolo? (qui: ogni segno,
   senza soglia). Chi opera: investitori che arrivano in ritardo dopo i rialzi (attenzione,
   notizie che si diffondono lentamente) e vendite forzate dopo i ribassi. Quando: la fonte
   parla di effetti da 1 a 4 settimane dopo; qui tenuta 7 giorni. Dipende dalla volatilità?
   Da verificare per anno.
4-5. **Spiegazioni concorrenti** (previsione → smentita):

   | | Spiegazione | Cosa prevede qui | Cosa la smentisce |
   |---|---|---|---|
   | G1 | Caso | `t` (b) sotto 2, R per anno di segno misto | `t` (b) sopra soglia, stesso segno negli anni |
   | G2 | Volatilità | i 7 giorni dopo settimane positive hanno ATR diverso: R cambia per lo stop al 6% | stessa quota di uscite a stop della (b) e vantaggio nel rendimento in direzione |
   | G3 | Trend di fondo | long buono solo nel 2020-21, short solo nel 2022 | batte la (b) anche nell'anno di segno opposto |
   | G4 | Artefatto dei dati | pochi trade a cavallo dei buchi di luglio 2021 e febbraio-aprile 2022 fanno il risultato | senza i 3 migliori resta sopra la (b) |
   | G5 | Costi | a 1d il costo è 0,023 R: non spiega quasi nulla | — |
   | G6 | Solo il mercato | rendimento di BTC nella finestra dei trade dello stesso segno e simile | BTC nella finestra vicino a zero |
   | G7 | Lo fa l'uscita | (a) e (b) simili al candidato | batte nettamente (a) e (b) |
   | S1 | Pochi episodi enormi (dicembre 2020, aprile 2021) | R medio dominato da 2-3 trade | R senza i 3 migliori ancora sopra la (b) |
   | S2 | Ritorno verso la media a 1 settimana (l'opposto) | long dopo settimane positive sotto la (b) | — è la previsione opposta, il test la distingue |
   | S3 | Effetto del giorno della settimana (gli ingressi cadono in giorni ricorrenti) | risultato diverso per giorno d'ingresso | risultato simile in ogni giorno |

6. **Ipotesi completa**: XRPUSDT, momentum di una settimana, timeframe **1d** (il meccanismo è di
   settimane; candele giornaliere bastano e danno un ingresso al giorno possibile), una direzione
   per variante.
   * **XRPUSDT-V01 (long)**: alla chiusura del giorno i, se close[i] / close[i−7] − 1 > 0 →
     long. Stop: min(2 × ATR14, 6%) sotto la chiusura. Nessun target. Tenuta 7 barre (una
     settimana, l'orizzonte breve della fonte). Riscaldamento: 14 barre.
     Previsione: R medio fra −0,10 e +0,15; non batte nettamente la (b) (potenza bassa con ~100
     trade); criterio di successo: batte nettamente (a) e (b) con R medio positivo (sezione 8).
   * **XRPUSDT-V02 (short)**: stesso, con close[i] / close[i−7] − 1 < 0 → short, stop sopra.
     Previsione: R medio fra −0,15 e +0,10; non batte nettamente la (b).
   Motivo delle due varianti: la fonte parla di momentum in tutte e due le direzioni; il
   protocollo vuole una direzione per variante.

---

## I-02 — Rimbalzo dopo un movimento orario estremo con volume alto

1. **Fonte**: John Y. Campbell, Sanford J. Grossman e Jiang Wang, «Trading Volume and Serial
   Correlation in Stock Returns», Quarterly Journal of Economics 108(4), novembre 1993.
2. **Affermazione verificabile**: un movimento di prezzo grande accompagnato da volume alto è
   spesso domanda di liquidità (chi deve vendere o comprare subito) e tende a rientrare; quindi
   dopo un'ora con caduta estrema e volume alto il prezzo nelle ore dopo sale più del caso
   (long), e dopo un'ora con salita estrema e volume alto scende più del caso (short). Falsa se
   l'R medio non supera la (b).
3. **Sotto-domande**: vale per movimenti oltre 2,5 deviazioni standard della settimana, con
   volume oltre il doppio della media settimanale. Chi opera: liquidazioni a cascata e stop
   (vendite forzate), market maker che assorbono e rivendono. Quando: entro poche ore (qui 12).
   Dipende dalla sessione? dalla presenza di notizie (un movimento da notizia non rientra)?
4-5. **Spiegazioni concorrenti**:

   | | Spiegazione | Cosa prevede qui | Cosa la smentisce |
   |---|---|---|---|
   | G1 | Caso | `t` (b) sotto soglia | `t` (b) sopra soglia, stesso segno negli anni |
   | G2 | Volatilità | dopo l'ora estrema l'ATR è alto, lo stop a 1,5 ATR è largo: l'R cambia per questo | rendimento in direzione positivo, non solo R |
   | G3 | Trend di fondo | i rimbalzi long vanno bene solo nel 2020-21 | anche nel 2022 |
   | G4 | Artefatto dei dati | barre anomale (candele con ombra di un tick enorme) | senza i 3 migliori resta |
   | G5 | Costi | a 1h il costo è circa 0,07 R | R netto positivo a costi doppi |
   | G6 | Solo il mercato | l'ora estrema è di tutto il mercato e rimbalza tutto il mercato | BTC nelle stesse 12 ore non rimbalza |
   | G7 | Lo fa l'uscita | (a) e (b) simili | batte nettamente (a) e (b) |
   | S1 | Notizia vera (es. la causa legale di dicembre 2020): continuazione, non rientro | R negativo concentrato nei giorni di notizie | — |
   | S2 | Continuazione a 1 ora (l'opposto) | R sotto la (b) | — il test distingue |
   | S3 | Rimbalzo meccanico dopo le liquidazioni del mark price | il rientro c'è solo quando il funding è estremo | rientro anche con funding normale |

6. **Ipotesi completa**: XRPUSDT, rientro dopo domanda di liquidità, timeframe **1h** (le
   cascate di liquidazioni e i rientri durano ore, non giorni). Definizioni alla chiusura della
   barra i: r = close[i]/close[i−1] − 1; σ = deviazione standard dei rendimenti orari delle
   168 barre fino a i−1 compresa; volume relativo = volume[i] / media del volume delle 168
   barre fino a i−1. Riscaldamento 170 barre.
   * **XRPUSDT-V03 (long)**: r < −2,5 σ e volume relativo > 2 → long. Stop min(1,5 ATR14, 6%)
     sotto; nessun target; tenuta 12 barre. Previsione: R medio fra −0,10 e +0,15; batte la (b)
     solo se il rientro è forte. Criterio: sezione 8.
   * **XRPUSDT-V04 (short)**: r > +2,5 σ e volume relativo > 2 → short. Stop sopra; tenuta 12.
     Previsione: R medio fra −0,15 e +0,10.

---

## I-03 — Continuazione dopo un giorno di «sovrareazione»

1. **Fonte**: Guglielmo Maria Caporale e Alex Plastun, «Price overreactions in the
   cryptocurrency market», Journal of Economic Studies 46(5), 2019. Dalla sintesi del lavoro: dopo
   i giorni di sovrareazione (rendimento oltre la media più un multiplo della deviazione
   standard) il prezzo il giorno dopo tende a muoversi nella stessa direzione (momentum), e su
   alcune monete una strategia che lo sfrutta guadagna.
2. **Affermazione verificabile**: dopo un giorno con rendimento oltre media + 1,5 σ (dei 30 giorni
   prima), il giorno dopo XRP sale più del caso (long); dopo un giorno sotto media − 1,5 σ, scende
   più del caso (short). Falsa se l'R medio non supera la (b).
3. **Sotto-domande**: soglia (1,5 σ, scelta a priori fra l'1 e il 2 della fonte), finestra di 30
   giorni. Chi opera: chi rincorre i movimenti grandi (attenzione, notizie lente). Quando: il
   giorno dopo (tenuta 1). Dipende dalla volatilità del mese?
4-5. **Spiegazioni concorrenti**:

   | | Spiegazione | Cosa prevede qui | Cosa la smentisce |
   |---|---|---|---|
   | G1 | Caso | `t` (b) sotto soglia | `t` sopra soglia e segno uguale negli anni |
   | G2 | Volatilità | dopo i giorni estremi l'ATR è alto, lo stop al 6% scatta spesso | stessa quota di stop della (b) |
   | G3 | Trend di fondo | i long dopo giorni forti vanno bene solo nel 2021 | anche nel 2022 |
   | G4 | Artefatto dei dati | primi giorni di gennaio 2020 (serie dal 6) | — riscaldamento di 31 giorni li esclude |
   | G5 | Costi | 0,023 R a giorno: poco | — |
   | G6 | Solo il mercato | il giorno dopo si muove tutto il mercato | BTC piatto il giorno dopo |
   | G7 | Lo fa l'uscita | (a) e (b) simili | batte nettamente (a) e (b) |
   | S1 | Rientro (l'opposto, come I-02 su scala giornaliera) | R sotto la (b) | — |
   | S2 | Pochi giorni enormi (aprile 2021) | R dominato da 2-3 trade | senza i 3 migliori resta |
   | S3 | Il segnale coincide con il momentum di I-01 | stessi giorni d'ingresso di V01/V02 | — si guarda la sovrapposizione |

6. **Ipotesi completa**: XRPUSDT, continuazione dopo sovrareazione, timeframe **1d** (la fonte è
   giornaliera). r = close[i]/close[i−1] − 1; media e σ dei 30 rendimenti giornalieri fino a i−1.
   Riscaldamento 31 barre.
   * **XRPUSDT-V05 (long)**: r > media + 1,5 σ → long; stop min(1,5 ATR14, 6%) sotto; nessun
     target; tenuta 1 barra. Previsione: R medio fra −0,10 e +0,15.
   * **XRPUSDT-V06 (short)**: r < media − 1,5 σ → short; stop sopra; tenuta 1. Previsione: R
     medio fra −0,15 e +0,10.
   * **Ripiego dichiarato prima di contare** (regola 6, «allentare le soglie di uno scarto»): se
     V05 o V06 resta sotto i 70 trade, la stessa variante con 1,0 σ al posto di 1,5 σ
     (XRPUSDT-V05b, XRPUSDT-V06b). Il 1,0 è il valore più basso della fonte.

---

## I-04 — Funding estremo: leva affollata da una parte

1. **Fonte**: Maik Schmeling, Andreas Schrimpf e Karamfil Todorov, «Crypto carry», BIS Working
   Papers n. 1087, aprile 2023. Il carry delle crypto (premio dei futures e funding dei perpetui)
   riflette la domanda di leva degli investitori; quando è alto prevede rischio di crolli e
   liquidazioni.
2. **Affermazione verificabile**: dopo un settlement con funding molto positivo (almeno 0,05% per
   8 ore, cinque volte il tasso base dello 0,01%) XRP nei 3 giorni dopo scende più del caso
   (short); dopo un funding negativo (al massimo −0,02%) sale più del caso (long: gli short
   affollati vengono costretti a ricomprare). Falsa se l'R medio non supera la (b).
3. **Sotto-domande**: soglie scelte a priori come multipli del tasso base (lo 0,05% è circa il 55%
   l'anno). Nota: dalla Fase 0 so che il funding medio del 2021 è stato 0,044%: la soglia di
   0,05% scatterà soprattutto nel 2021; lo dichiaro. Chi opera: chi ha leva lunga paga il funding
   e viene liquidato nei ribassi. Quando: giorni (tenuta 9 barre da 8 ore = 3 giorni).
4-5. **Spiegazioni concorrenti**:

   | | Spiegazione | Cosa prevede qui | Cosa la smentisce |
   |---|---|---|---|
   | G1 | Caso | `t` (b) sotto soglia | sopra soglia |
   | G2 | Volatilità | funding alto in periodi di volatilità alta: stop al 6% scatta spesso | stessa quota di stop della (b) |
   | G3 | Trend di fondo | funding alto nel rialzo del 2021: lo short perde per il trend | batte la (b) short, che entra a caso nello stesso periodo |
   | G4 | Artefatto dei dati | settlement nei buchi | — |
   | G5 | Costi | lo short incassa il funding: guadagno in R che non è previsione del prezzo | vantaggio anche togliendo il funding incassato |
   | G6 | Solo il mercato | il funding alto è di tutto il mercato e il crollo di tutto il mercato | BTC piatto nelle stesse finestre |
   | G7 | Lo fa l'uscita | (a) e (b) simili | batte nettamente (a) e (b) |
   | S1 | Il funding alto segue un rialzo (momentum che continua): lo short perde | R short negativo | — |
   | S2 | Pochi episodi (2-3 crolli) | R dominato da pochi trade | senza i 3 migliori resta |
   | S3 | Funding negativo = notizia cattiva (causa legale di dicembre 2020): il long perde | R long negativo nel dicembre 2020 | — |

6. **Ipotesi completa**: XRPUSDT, contrarian sul funding estremo, timeframe **8h** (il periodo
   del funding). Funding della barra i = tasso dell'ultimo settlement con istante entro la chiusura
   della barra i (noto a quel momento). Riscaldamento: 14 barre (ATR) e almeno un settlement.
   * **XRPUSDT-V07 (short)**: funding ≥ 0,0005 → short; stop min(2 ATR14, 6%) sopra; nessun
     target; tenuta 9 barre. Previsione: R medio fra −0,15 e +0,15; il funding incassato aggiunge
     circa +0,01-0,03 R.
   * **XRPUSDT-V08 (long)**: funding ≤ −0,0002 → long; stop sotto; tenuta 9. Previsione: R medio
     fra −0,15 e +0,15.
   * **Ripiego dichiarato prima di contare**: se V07 resta sotto 70 trade, soglia 0,0003
     (XRPUSDT-V07b); se V08 resta sotto 70, soglia −0,0001 (XRPUSDT-V08b).

---

## I-05 — Effetto del lunedì

1. **Fonte**: Guglielmo Maria Caporale e Alex Plastun, «The day of the week effect in the
   cryptocurrency market», Finance Research Letters 31, dicembre 2019: per Bitcoin i rendimenti
   del lunedì sono significativamente più alti degli altri giorni.
2. **Affermazione verificabile**: il rendimento di XRP dalla mezzanotte UTC del lunedì alla
   mezzanotte del martedì è più alto di quello di un giorno preso a caso (long). Falsa se l'R
   medio non supera la (b).
3. **Sotto-domande**: perché il lunedì? riapertura dei mercati tradizionali e dei flussi
   istituzionali dopo il fine settimana a volume basso. Chi opera: chi riprende a comprare il
   lunedì. Quando: tutto il giorno UTC.
4-5. **Spiegazioni concorrenti**:

   | | Spiegazione | Cosa prevede qui | Cosa la smentisce |
   |---|---|---|---|
   | G1 | Caso (uno dei 7 giorni è il migliore per forza: problema dei confronti multipli nella fonte) | `t` (b) sotto soglia | sopra soglia |
   | G2 | Volatilità | lunedì più volatile: R diverso per lo stop | — |
   | G3 | Trend di fondo | buono solo nel 2020-21 | anche nel 2022 |
   | G4 | Artefatto dei dati | — | — |
   | G5 | Costi | 0,023 R | — |
   | G6 | Solo il mercato | è il lunedì di tutto il mercato (BTC) | BTC del lunedì piatto |
   | G7 | Lo fa l'uscita | (a) e (b) simili | batte nettamente (a) e (b) |
   | S1 | Fuso orario: il «lunedì» degli Stati Uniti è dalle 13 UTC | effetto solo nella seconda metà | — |
   | S2 | Pochi lunedì enormi | R dominato da 2-3 trade | senza i 3 migliori resta |
   | S3 | Ritorno dopo il fine settimana (il fine settimana scende, il lunedì recupera) | effetto solo dopo fine settimana negativi | anche dopo fine settimana positivi |

6. **Ipotesi completa**: XRPUSDT, timeframe **1d**, long.
   * **XRPUSDT-V09 (long)**: alla chiusura della candela della domenica (UTC) → long all'apertura
     del lunedì; stop min(1,5 ATR14, 6%) sotto; nessun target; tenuta 1. Riscaldamento 14.
     Previsione: R medio fra −0,10 e +0,10; non batte nettamente la (b).

---

## I-06 — BTC guida, XRP segue con ritardo

1. **Fonte**: Andrew W. Lo e A. Craig MacKinlay, «When Are Contrarian Profits Due to Stock Market
   Overreaction?», Review of Financial Studies 3(2), 1990: i titoli grandi guidano quelli piccoli
   (correlazione incrociata ritardata). Per le crypto: Imtiaz Mohammad Sifat, Azhar Mohamad e
   Mohamed Shariff Bin Mohamed Shariff, «Lead-Lag relationship between Bitcoin and Ethereum:
   Evidence from hourly and daily data», Research in International Business and Finance 50,
   dicembre 2019.
2. **Affermazione verificabile**: quando BTC si muove molto in un'ora e XRP nella stessa ora si è
   mosso meno della metà, nelle 4 ore dopo XRP recupera nella direzione di BTC più del caso. Falsa
   se l'R medio non supera la (b).
3. **Sotto-domande**: soglia del movimento di BTC (1% in un'ora, scelto a priori: circa due volte
   e mezzo il movimento orario tipico di BTC); quanto deve essere in ritardo XRP (meno della metà
   del movimento di BTC). Chi opera: arbitraggisti e algoritmi che riallineano i prezzi, investitori
   che guardano prima BTC. Quando: entro poche ore.
4-5. **Spiegazioni concorrenti**:

   | | Spiegazione | Cosa prevede qui | Cosa la smentisce |
   |---|---|---|---|
   | G1 | Caso | `t` (b) sotto soglia | sopra |
   | G2 | Volatilità | ore di BTC estremo = volatilità alta | rendimento in direzione positivo |
   | G3 | Trend di fondo | buono solo dove il trend va nella direzione del trade | anche contro |
   | G4 | Artefatto dei dati | barre di BTC e XRP non allineate | — si usano gli stessi `ts` |
   | G5 | Costi | 0,07 R a giro: il recupero di mezzo punto percentuale non basta | R netto positivo |
   | G6 | Solo il mercato | è proprio il mercato: il trade guadagna se BTC continua | il guadagno c'è anche quando BTC si ferma |
   | G7 | Lo fa l'uscita | (a) e (b) simili | batte nettamente (a) e (b) |
   | S1 | XRP in ritardo perché ha una notizia sua (resta indietro per un motivo) | R negativo | — |
   | S2 | BTC rientra (il suo movimento era domanda di liquidità, come I-02) | XRP non recupera | — |
   | S3 | Effetto del funding di BTC | — | — |

6. **Ipotesi completa**: XRPUSDT, timeframe **1h**. rb = rendimento orario di BTC alla barra i,
   rx = rendimento orario di XRP alla barra i (stessi `ts`). Riscaldamento 14.
   * **XRPUSDT-V10 (long)**: rb > +1% e rx < 0,5 × rb → long; stop min(1,5 ATR14, 6%) sotto;
     nessun target; tenuta 4 barre. Previsione: R medio fra −0,10 e +0,10.
   * **XRPUSDT-V11 (short)**: rb < −1% e rx > 0,5 × rb → short; stop sopra; tenuta 4.
     Previsione: R medio fra −0,10 e +0,10.

---

## I-07 — Uscita dal canale (rottura del massimo di 20 barre)

1. **Fonte**: Robert Hudson e Andrew Urquhart, «Technical trading and cryptocurrencies», Annals of
   Operations Research 297, 2021 (online dal 2019): le regole di rottura del canale di prezzo
   (trading range break-out) hanno potere predittivo su Bitcoin e altre crypto. Regole d'origine:
   William Brock, Josef Lakonishok e Blake LeBaron, «Simple Technical Trading Rules and the
   Stochastic Properties of Stock Returns», Journal of Finance 47(5), dicembre 1992.
2. **Affermazione verificabile**: quando XRP chiude sopra il massimo delle 20 barre da 4 ore
   precedenti, nelle barre dopo sale più del caso (long); sotto il minimo, scende più del caso
   (short). Falsa se l'R medio non supera la (b).
3. **Sotto-domande**: 20 barre = poco più di 3 giorni. Chi opera: stop degli short sopra i
   massimi, chi segue i trend. Quando: giorni.
4-5. **Spiegazioni concorrenti**:

   | | Spiegazione | Cosa prevede qui | Cosa la smentisce |
   |---|---|---|---|
   | G1 | Caso | `t` (b) sotto soglia | sopra |
   | G2 | Volatilità | rotture in momenti di volatilità in crescita | — |
   | G3 | Trend di fondo | long buono nel 2020-21, short nel 2022 | batte la (b) in entrambi |
   | G4 | Artefatto dei dati | — | — |
   | G5 | Costi | 0,03 R a giro | — |
   | G6 | Solo il mercato | rotture insieme a BTC | — |
   | G7 | Lo fa l'uscita (canale di uscita a 10 barre lascia correre i guadagni) | la (a) con la stessa uscita fa uguale | batte nettamente la (a) |
   | S1 | Falsi segnali in laterale | R negativo nei mesi laterali | — |
   | S2 | Pochi trend enormi | R dominato da 2-3 trade | senza i 3 migliori resta |
   | S3 | Rientro dopo la rottura (stop sopra il massimo presi e poi rientro) | R sotto la (b) | — |

6. **Ipotesi completa**: XRPUSDT, timeframe **4h** (rotture su più giorni; a 4h abbastanza trade).
   Riscaldamento 21 barre.
   * **XRPUSDT-V12 (long)**: close[i] > massimo degli high delle barre i−20…i−1 → long; stop
     min(2 ATR14, 6%) sotto; nessun target; uscita per segnale se close < minimo dei low delle
     10 barre precedenti; tenuta massima 30 barre (5 giorni). Previsione: R medio fra −0,10 e
     +0,20.
   * **XRPUSDT-V13 (short)**: close[i] < minimo dei low delle barre i−20…i−1 → short; uscita se
     close > massimo degli high delle 10 barre precedenti; tenuta 30. Previsione: fra −0,15 e
     +0,15.

---

## I-08 — RSI a 2 periodi: rientro dentro il trend

1. **Fonte**: Larry Connors e Cesar Alvarez, «Short Term Trading Strategies That Work»,
   TradingMarkets Publishing, 2008: sopra la media mobile a 200 periodi, comprare dopo un RSI(2)
   molto basso e uscire quando il prezzo torna sopra la media a 5 periodi.
2. **Affermazione verificabile**: dentro un trend rialzista (close sopra la media a 200), dopo un
   RSI(2) sotto 10 XRP rimbalza più del caso (long); dentro un trend ribassista, dopo un RSI(2)
   sopra 90 scende più del caso (short). Falsa se l'R medio non supera la (b).
3. **Sotto-domande**: la fonte è su azioni e indici giornalieri; qui 4 ore (crypto aperte sempre;
   la media a 200 barre da 4 ore è circa 33 giorni). Chi opera: chi vende in panico sui ribassi
   brevi, e chi compra «sullo sconto» nel trend.
4-5. **Spiegazioni concorrenti**:

   | | Spiegazione | Cosa prevede qui | Cosa la smentisce |
   |---|---|---|---|
   | G1 | Caso | `t` (b) sotto soglia | sopra |
   | G2 | Volatilità | dopo cadute brevi volatilità alta | — |
   | G3 | Trend di fondo (il filtro a 200 è il trend) | batte la (a) ma non la (b) | batte la (b), che entra a caso nella stessa direzione |
   | G4 | Artefatto dei dati | — | — |
   | G5 | Costi | 0,02-0,03 R a giro | — |
   | G6 | Solo il mercato | rimbalzo di tutto il mercato | — |
   | G7 | Lo fa l'uscita (uscita sopra la media a 5: tante piccole vincite, rare perdite grandi) | la (a) con la stessa uscita fa uguale | batte nettamente la (a) |
   | S1 | Il ribasso breve continua (momentum a 4h) | R sotto la (b) | — |
   | S2 | Pochi trade enormi | — | senza i 3 migliori resta |
   | S3 | La media a 200 a 4h è troppo corta per un «trend» | effetto uguale senza filtro | — si vede dalla (a)? no: la (a) toglie anche il filtro |

6. **Ipotesi completa**: XRPUSDT, timeframe **4h**. RSI di Wilder a 2 periodi; medie semplici a
   200 e a 5 barre. Riscaldamento 200 barre.
   * **XRPUSDT-V14 (long)**: close > media200 e RSI2 < 10 → long; stop min(2,5 ATR14, 6%) sotto
     (largo, perché il rientro richiede spazio); nessun target; uscita per segnale se close >
     media5; tenuta massima 30 barre. Previsione: R medio fra −0,10 e +0,15.
   * **XRPUSDT-V15 (short)**: close < media200 e RSI2 > 90 → short; stop sopra; uscita se close <
     media5; tenuta 30. Previsione: fra −0,15 e +0,10.

---

## I-09 — Compressione della volatilità e rottura delle bande

1. **Fonte**: John Bollinger, «Bollinger on Bollinger Bands», McGraw-Hill, 2001: la larghezza
   delle bande al minimo di molti mesi («the Squeeze») annuncia un aumento di volatilità; la
   direzione si legge dalla rottura della banda.
2. **Affermazione verificabile**: quando la larghezza delle bande (20 barre, 2 deviazioni) di XRP
   a 1 ora ha toccato il minimo delle ultime 480 barre (20 giorni) in una delle 10 barre prima, una
   chiusura sopra la banda superiore è seguita da salita più del caso (long), una sotto la banda
   inferiore da discesa più del caso (short).
3. **Sotto-domande**: finestra del minimo (480 barre, scelta a priori: l'equivalente orario di
   «molti mesi» su candele giornaliere non è ovvio; 20 giorni è un compromesso per avere trade).
   Chi opera: stop accumulati durante la quiete, chi aspetta la rottura. Quando: ore, un giorno.
4-5. **Spiegazioni concorrenti**:

   | | Spiegazione | Cosa prevede qui | Cosa la smentisce |
   |---|---|---|---|
   | G1 | Caso | `t` (b) sotto soglia | sopra |
   | G2 | Volatilità (il segnale sceglie per costruzione volatilità bassa: stop stretti in ATR) | R grande per lo stop stretto, non per la direzione | rendimento in direzione positivo |
   | G3 | Trend di fondo | segue il buy and hold dell'anno | — |
   | G4 | Artefatto dei dati | minimi di larghezza nei giorni dei buchi | — |
   | G5 | Costi | stop stretti = costo in R più alto (0,07-0,1 R) | R netto positivo |
   | G6 | Solo il mercato | rotture insieme a BTC | — |
   | G7 | Lo fa l'uscita | (a) e (b) simili | batte nettamente (a) e (b) |
   | S1 | Falsa rottura (rientro nelle bande) | R sotto la (b) | — |
   | S2 | Pochi trade | R dominato da pochi | senza i 3 migliori |
   | S3 | Le rotture di notte (UTC) sono rumore | — | — |

6. **Ipotesi completa**: XRPUSDT, timeframe **1h**. Media e deviazione standard delle 20 chiusure;
   larghezza = 4 σ / media. Riscaldamento 500 barre.
   * **XRPUSDT-V16 (long)**: compressione nelle 10 barre i−10…i−1 e close[i] > banda superiore[i]
     → long; stop min(2 ATR14, 6%) sotto; nessun target; tenuta 24 barre. Previsione: R medio
     fra −0,15 e +0,15.
   * **XRPUSDT-V17 (short)**: compressione e close[i] < banda inferiore[i] → short; stop sopra;
     tenuta 24. Previsione: fra −0,15 e +0,15.
   * **Ripiego aggiunto il 2026-10-09 dopo i soli conteggi** (V16: 28 trade, V17: 26; nessun test
     di questa idea fatto, nessun risultato visto; regola 6, «allentare le soglie di uno scarto»):
     compressione = larghezza al minimo delle ultime **240** barre (10 giorni) in una delle **24**
     barre prima (un giorno), il resto uguale: **XRPUSDT-V16b (long)** e **XRPUSDT-V17b (short)**.
     Se restano sotto 70, l'idea è scartata.

---

## I-10 — Squilibrio fra acquisti e vendite aggressive

1. **Fonte**: Tarun Chordia e Avanidhar Subrahmanyam, «Order imbalance and individual stock
   returns: Theory and evidence», Journal of Financial Economics 72(3), giugno 2004: lo squilibrio
   degli ordini (acquisti meno vendite iniziati dal compratore) prevede positivamente i rendimenti
   successivi, perché chi deve comprare o vendere molto spezza gli ordini nel tempo.
2. **Affermazione verificabile**: quando nelle ultime 4 ore gli acquisti aggressivi (volume
   «taker buy» delle candele) superano le vendite aggressive di oltre il 10% del volume, nelle 4
   ore dopo XRP sale più del caso (long); quando le vendite superano gli acquisti di oltre il 10%,
   scende più del caso (short).
3. **Sotto-domande**: soglia del 10% (squilibrio = 2 × acquisti aggressivi / volume − 1) scelta a
   priori senza conoscere la distribuzione; finestra 4 ore. Chi opera: grandi ordini spezzati,
   liquidazioni a catena. Quando: ore.
4-5. **Spiegazioni concorrenti**:

   | | Spiegazione | Cosa prevede qui | Cosa la smentisce |
   |---|---|---|---|
   | G1 | Caso | `t` (b) sotto soglia | sopra |
   | G2 | Volatilità | squilibri grandi in ore volatili | — |
   | G3 | Trend di fondo | segue il buy and hold | batte la (b) |
   | G4 | Artefatto dei dati (la colonna taker buy non esiste o è vuota in alcuni file) | pochi segnali in certi mesi | — si controlla la colonna |
   | G5 | Costi | 0,07 R | — |
   | G6 | Solo il mercato | lo squilibrio è di tutto il mercato | — |
   | G7 | Lo fa l'uscita | (a) e (b) simili | batte nettamente |
   | S1 | Lo squilibrio è già nel prezzo (rendimento delle 4 ore): è momentum di prezzo, non di flusso | stesso risultato di una regola sul solo rendimento | — |
   | S2 | Rientro dopo acquisti aggressivi (liquidità, come I-02) | R sotto la (b) | — |
   | S3 | Liquidazioni: lo squilibrio è forzato e rientra | — | — |

6. **Ipotesi completa**: XRPUSDT, timeframe **1h**. Squilibrio delle 4 barre i−3…i = 2 × (somma
   taker buy volume) / (somma volume) − 1, dalla colonna 9 dei file klines (volume in moneta base
   comprato da chi prende il prezzo). Riscaldamento 14.
   * **XRPUSDT-V18 (long)**: squilibrio > +0,10 → long; stop min(1,5 ATR14, 6%) sotto; nessun
     target; tenuta 4 barre. Previsione: R medio fra −0,10 e +0,10.
   * **XRPUSDT-V19 (short)**: squilibrio < −0,10 → short; stop sopra; tenuta 4. Previsione:
     fra −0,10 e +0,10.
   * **Ripiego dichiarato prima di contare**: se una delle due resta sotto 70 trade, soglia
     0,06 (XRPUSDT-V18b, XRPUSDT-V19b).

---

## I-11 — Premio del perpetuo sul mark price

1. **Fonte**: Songrun He, Asaf Manela, Omri Ross e Victor von Wachter, «Fundamentals of Perpetual
   Futures», arXiv 2212.06888, dicembre 2022: il prezzo dei perpetui si discosta in modo rilevante
   dal prezzo a pronti e gli scostamenti rientrano (arbitraggio limitato).
2. **Affermazione verificabile**: quando il last a 1 ora chiude sopra il mark price di oltre lo
   0,15% (il perpetuo è caro rispetto all'indice), nelle 4 ore dopo XRP scende più del caso
   (short); quando chiude sotto di oltre lo 0,15%, sale più del caso (long).
3. **Sotto-domande**: il mark price di Binance è costruito dall'indice a pronti più un premio medio:
   la differenza last − mark misura il premio di breve. Soglia 0,15% scelta a priori (più del
   costo di un giro). Chi opera: chi compra perpetui con leva in fretta (domanda che spinge il
   premio), gli arbitraggisti che lo riportano. Quando: ore.
4-5. **Spiegazioni concorrenti**:

   | | Spiegazione | Cosa prevede qui | Cosa la smentisce |
   |---|---|---|---|
   | G1 | Caso | `t` (b) sotto soglia | sopra |
   | G2 | Volatilità | premi grandi in ore volatili | — |
   | G3 | Trend di fondo | — | — |
   | G4 | Artefatto dei dati (mark e last chiudono in istanti diversi) | differenze dovute al tempo, non al premio | — |
   | G5 | Costi | il rientro del premio (0,15%) è circa il costo di un giro | — |
   | G6 | Solo il mercato | — | — |
   | G7 | Lo fa l'uscita | (a) e (b) simili | batte nettamente |
   | S1 | Il premio alto segnala domanda vera che continua (momentum) | R sotto la (b) | — |
   | S2 | Il rientro avviene col mark che sale, non col last che scende | R vicino a zero | — |
   | S3 | Pochi episodi | — | — |

6. **Ipotesi completa**: XRPUSDT, timeframe **1h**. premio = close del last / close del mark − 1
   alla barra i. Riscaldamento 14.
   * **XRPUSDT-V20 (short)**: premio > +0,0015 → short; stop min(1,5 ATR14, 6%) sopra; nessun
     target; tenuta 4. Previsione: R medio fra −0,10 e +0,10.
   * **XRPUSDT-V21 (long)**: premio < −0,0015 → long; stop sotto; tenuta 4. Previsione: fra −0,10
     e +0,10.
   * **Ripiego dichiarato prima di contare**: se una resta sotto 70 trade, soglia 0,0010
     (XRPUSDT-V20b, XRPUSDT-V21b).

---

## I-12 — Numeri tondi: ordini di stop oltre la soglia

1. **Fonte**: Carol L. Osler, «Currency Orders and Exchange Rate Dynamics: An Explanation for the
   Predictive Success of Technical Analysis», Journal of Finance 58(5), ottobre 2003: gli ordini di
   presa di profitto si concentrano sui numeri tondi (il prezzo si ferma lì), gli ordini di stop
   subito oltre (una volta attraversato il numero tondo il prezzo accelera).
2. **Affermazione verificabile**: quando la chiusura a 1 ora di XRP attraversa verso l'alto un
   numero tondo, nelle ore dopo sale più del caso (long); quando lo attraversa verso il basso,
   scende più del caso (short).
3. **Sotto-domande**: numero tondo = prezzo con due cifre significative (passo = 10 elevato a
   (parte intera di log10 del prezzo) − 1: a 0,25 il passo è 0,01, a 1,5 è 0,1). Chi opera: stop
   dei trader al dettaglio messi sui numeri tondi. Quando: poche ore.
4-5. **Spiegazioni concorrenti**:

   | | Spiegazione | Cosa prevede qui | Cosa la smentisce |
   |---|---|---|---|
   | G1 | Caso | `t` (b) sotto soglia | sopra |
   | G2 | Volatilità | attraversamenti più frequenti nelle ore volatili | — |
   | G3 | Trend di fondo | attraversamenti verso l'alto più frequenti nel rialzo | batte la (b) |
   | G4 | Artefatto dei dati | — | — |
   | G5 | Costi | 0,07 R | — |
   | G6 | Solo il mercato | — | — |
   | G7 | Lo fa l'uscita | (a) e (b) simili | batte nettamente |
   | S1 | Rientro sui numeri tondi (gli ordini di presa di profitto fermano il prezzo) | R sotto la (b) | — |
   | S2 | I numeri tondi di XRP non sono quelli che guardano i trader (passo troppo fitto o rado) | nessuna differenza | — |
   | S3 | È momentum a 1 ora (un attraversamento è un movimento) | stesso risultato di una regola sul rendimento | — |

6. **Ipotesi completa**: XRPUSDT, timeframe **1h**. Passo alla barra i calcolato su close[i−1].
   Riscaldamento 14.
   * **XRPUSDT-V22 (long)**: esiste un multiplo del passo m con close[i−1] < m ≤ close[i] → long;
     stop min(1,5 ATR14, 6%) sotto; nessun target; tenuta 6 barre. Previsione: R medio fra −0,10
     e +0,10.
   * **XRPUSDT-V23 (short)**: close[i−1] > m ≥ close[i] → short; stop sopra; tenuta 6. Previsione:
     fra −0,10 e +0,10.

---

## I-13 — Momentum dentro la giornata: la prima mezz'ora guida l'ultima

1. **Fonte**: Lei Gao, Yufeng Han, Sophia Zhengzi Li e Guofu Zhou, «Market Intraday Momentum»,
   Journal of Financial Economics 129(2), agosto 2018: il rendimento della prima mezz'ora prevede
   quello dell'ultima mezz'ora. Per le crypto: Zhuzhu Wen, Elie Bouri, Yahua Xu e Yang Zhao,
   «Intraday return predictability in the cryptocurrency markets: Momentum, reversal, or both»,
   North American Journal of Economics and Finance 62, novembre 2022.
2. **Affermazione verificabile**: con la giornata UTC, se la prima mezz'ora (00:00-00:30) di XRP
   chiude in rialzo, l'ultima mezz'ora (23:30-24:00) rende più del caso (long); se chiude in
   ribasso, l'ultima rende meno (short).
3. **Sotto-domande**: il «giorno» delle crypto non ha apertura né chiusura vera: la mezzanotte UTC
   è il confine delle candele giornaliere e dei settlement del funding. Chi opera: ribilanciamenti
   di fine giornata, chi informato entra presto e chi chiude tardi. Quando: l'ultima mezz'ora.
4-5. **Spiegazioni concorrenti**:

   | | Spiegazione | Cosa prevede qui | Cosa la smentisce |
   |---|---|---|---|
   | G1 | Caso | `t` (b) sotto soglia | sopra |
   | G2 | Volatilità | — | — |
   | G3 | Trend di fondo | — | — |
   | G4 | Artefatto dei dati | — | — |
   | G5 | Costi (0,10 R a 1,5 ATR a 30m) | lordo positivo e netto negativo | netto positivo |
   | G6 | Solo il mercato | — | — |
   | G7 | Lo fa l'uscita | (a) e (b) simili | batte nettamente |
   | S1 | Settlement del funding a mezzanotte: chi chiude prima del settlement muove l'ultima mezz'ora | effetto legato al segno del funding, non alla prima mezz'ora | — |
   | S2 | La mezzanotte UTC non ha significato per XRP: nessun effetto | `t` vicino a zero | — |
   | S3 | Rientro invece che momentum (la fonte crypto dice «o entrambi») | R sotto la (b) | — |

6. **Ipotesi completa**: XRPUSDT, timeframe **30m**. Segnale alla chiusura della barra delle
   23:00-23:30 UTC, ingresso all'apertura delle 23:30, uscita all'apertura di mezzanotte (tenuta 1).
   Rendimento della prima mezz'ora = close/open − 1 della barra delle 00:00 dello stesso giorno.
   Riscaldamento 14.
   * **XRPUSDT-V24 (long)**: prima mezz'ora > 0 → long; stop min(1,5 ATR14, 6%) sotto; tenuta 1.
     Previsione: R medio fra −0,20 e +0,05 (il costo pesa 0,10 R).
   * **XRPUSDT-V25 (short)**: prima mezz'ora < 0 → short; stop sopra; tenuta 1. Previsione:
     fra −0,20 e +0,05.

---

## I-14 — Momentum relativo: XRP contro BTC

Aggiunta il 2026-10-09 mentre giravano V02-V25, prima di vederne gli esiti (avevo visto solo V01
e V02, momentum assoluto a una settimana, nessuno dei due vicino a battere il caso).

1. **Fonte**: Yukun Liu, Aleh Tsyvinski e Xi Wu, «Common Risk Factors in Cryptocurrency», NBER
   Working Paper 25882, maggio 2019 (poi Journal of Finance 77(2), 2022): fra le crypto c'è un
   fattore momentum trasversale: le monete che hanno reso più delle altre continuano a farlo.
2. **Affermazione verificabile**: quando XRP ha reso più di BTC negli ultimi 7 giorni, nella
   settimana dopo rende più del caso (long); quando ha reso meno, rende meno del caso (short).
   Diversa da I-01: qui conta la forza RELATIVA a BTC, non il segno del rendimento di XRP.
3. **Sotto-domande**: una sola altra moneta (BTC) come termine di confronto, perché la campagna
   non ha dati di altre monete; il mercato comune si toglie per differenza. Chi opera: investitori
   che spostano capitale verso le monete «che vanno», attenzione dei media. Quando: settimane.
4-5. **Spiegazioni concorrenti**:

   | | Spiegazione | Cosa prevede qui | Cosa la smentisce |
   |---|---|---|---|
   | G1 | Caso | `t` (b) sotto soglia | sopra soglia, stesso segno negli anni |
   | G2 | Volatilità | XRP batte BTC nei periodi in cui XRP è più volatile: R cambia per lo stop | stessa quota di stop della (b) |
   | G3 | Trend di fondo | long buono nel 2021, short nel 2022 | batte la (b) in entrambi |
   | G4 | Artefatto dei dati | BTC parte il 2020-01-01, XRP il 06: primi 7 giorni | riscaldamento di 14 barre li esclude |
   | G5 | Costi | 0,023 R | — |
   | G6 | Solo il mercato | il segnale coincide con quello di I-01 (XRP sale quando sale tutto) | segnali diversi da I-01 in molti giorni |
   | G7 | Lo fa l'uscita | (a) e (b) simili | batte nettamente (a) e (b) |
   | S1 | Rientro del rapporto XRP/BTC (l'opposto) | R sotto la (b) | — |
   | S2 | Pochi episodi (XRP che raddoppia in pochi giorni) | R dominato da 2-3 trade | senza i 3 migliori resta |
   | S3 | Notizie proprie di XRP (causa legale): il distacco da BTC continua per motivi non ripetibili | il risultato viene da dicembre 2020 | resta togliendo dicembre 2020 |

6. **Ipotesi completa**: XRPUSDT, timeframe **1d**. rel = (close XRP[i]/close XRP[i−7] − 1) −
   (close BTC[i]/close BTC[i−7] − 1), con le chiusure di BTC sugli stessi giorni. Riscaldamento 14.
   * **XRPUSDT-V26 (long)**: rel > 0 → long; stop min(2 ATR14, 6%) sotto; nessun target; tenuta 7.
     Previsione: R medio fra −0,10 e +0,15; non batte nettamente la (b).
   * **XRPUSDT-V27 (short)**: rel < 0 → short; stop sopra; tenuta 7. Previsione: fra −0,15 e +0,10.

---

## I-15 — Rottura dell'intervallo di apertura della giornata UTC

1. **Fonte**: Toby Crabel, «Day Trading with Short Term Price Patterns and Opening Range
   Breakout», Traders Press, 1990: la rottura dell'intervallo dei primi minuti od ore di una
   sessione indica la direzione del resto della giornata.
2. **Affermazione verificabile**: con la giornata UTC, quando una chiusura oraria fra le 02:00 e le
   23:00 supera per la prima volta nel giorno il massimo delle prime due ore (00:00-02:00), XRP fino
   a fine giornata sale più del caso (long); quando scende per la prima volta sotto il minimo delle
   prime due ore, scende più del caso (short).
3. **Sotto-domande**: le crypto non hanno apertura vera; la mezzanotte UTC è il confine delle
   candele giornaliere, che molti guardano. Due ore scelte a priori (la fonte usa intervalli brevi
   all'apertura; due ore su 24 sono l'equivalente di circa 30 minuti di una sessione azionaria).
   Chi opera: chi segue la rottura, stop sopra e sotto l'intervallo. Quando: entro la giornata.
4-5. **Spiegazioni concorrenti**:

   | | Spiegazione | Cosa prevede qui | Cosa la smentisce |
   |---|---|---|---|
   | G1 | Caso | `t` (b) sotto soglia | sopra |
   | G2 | Volatilità | rotture nei giorni volatili | rendimento in direzione positivo |
   | G3 | Trend di fondo | rotture verso l'alto buone solo nel 2020-21 | anche nel 2022 |
   | G4 | Artefatto dei dati | giorni con buchi (intervallo d'apertura incompleto) | — si esige che le barre 00:00 e 01:00 esistano |
   | G5 | Costi | 0,07 R a giro | R netto positivo |
   | G6 | Solo il mercato | rotture insieme a BTC | — |
   | G7 | Lo fa l'uscita | (a) e (b) simili | batte nettamente |
   | S1 | Falsa rottura e rientro nell'intervallo | R sotto la (b) | — |
   | S2 | Momentum a 1 ora (la rottura è un movimento) | stesso risultato di una regola sul rendimento | — |
   | S3 | La mezzanotte UTC non ha significato per XRP | `t` vicino a zero | — |

6. **Ipotesi completa**: XRPUSDT, timeframe **1h**. Massimo e minimo dell'intervallo = massimo
   degli high e minimo dei low delle barre delle 00:00 e 01:00 dello stesso giorno (servono
   entrambe). Segnale alle chiusure delle barre dalle 02:00 alle 22:00 (l'ingresso deve cadere entro
   le 23:00), solo la prima rottura del giorno in quella direzione. Uscita per segnale alla
   chiusura della barra delle 23:00 (si esce all'apertura di mezzanotte). Riscaldamento 14.
   * **XRPUSDT-V28 (long)**: prima chiusura del giorno sopra il massimo dell'intervallo → long;
     stop min(1,5 ATR14, 6%) sotto; nessun target; uscita a fine giornata; tenuta massima 22.
     Previsione: R medio fra −0,10 e +0,10.
   * **XRPUSDT-V29 (short)**: prima chiusura del giorno sotto il minimo dell'intervallo → short;
     stop sopra; uscita a fine giornata; tenuta 22. Previsione: fra −0,10 e +0,10.

---

## Riepilogo

15 idee (I-14 e I-15 aggiunte dopo), 29 varianti (più i ripieghi dichiarati, che sostituiscono una variante solo se quella
resta sotto i 70 trade). Famiglie di meccanismi: momentum di prezzo (I-01, I-03, I-07),
rientro dopo domanda di liquidità (I-02, I-08), leva e funding (I-04), calendario (I-05, I-13),
legame con BTC (I-06), volatilità (I-09), flusso degli ordini (I-10), premio del perpetuo
(I-11), ordini sui numeri tondi (I-12), forza relativa (I-14), rottura dell'intervallo d'apertura
(I-15). Se tutte le varianti superano i 70 trade resta 1 unità del budget: per un'altra idea con
fonte se la trovo, poi per i ritocchi nell'ordine della regola 6.
