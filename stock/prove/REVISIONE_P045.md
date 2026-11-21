# Prova 45 — la revisione separata (21 novembre 2026, prima del periodo chiuso)

**Chi ha fatto cosa.** Regole, programma e risultato: la sessione «trading stock» (commit `336197bc` regole 10:44:48 UTC, `8cd4c980`
programma e test 10:46:28, `fa2ca7f2` risultati scritti dal lavoro di GitHub 10:49:08). Questa revisione: un agente che non ha scritto
né le regole né il codice, in sola lettura sul repository (unico file scritto: questo). **Nessun dato dopo il 31 dicembre 2024**: gli
script del revisore si fermano con un errore se una serie va oltre; le serie `*_chiuso` (9) sono escluse per nome senza aprirle; DIX.csv
e le copie vecchie sono tagliate al 31 dicembre 2024 subito dopo la lettura. Dati: barre al minuto e al giorno dello SPY di Alpaca
(`~/stock_dati/SPY/`), calendario di borsa ricostruito con la libreria `exchange_calendars` (borsa di New York, installata con pip),
DIX.csv di SqueezeMetrics scaricato oggi, 12 copie vecchie di DIX.csv da repository pubblici di GitHub, S&P 500, VIX e SPY da Yahoo
fino al 2024. Il metodo dei controlli (in particolare il 6, i giorni agitati) è stato scritto prima di guardare i rendimenti
(`PIANO.md` fra gli script, elenco in fondo).

## Esito: **FAIL** per il criterio «entrare nella miscela»; confermata la bocciatura da sola

* **Da sola: bocciata**, confermato: Sharpe con i costi 0,51 contro 0,84-0,87 del tenere lo SPY, Sharpe corretto 0,000 (anche senza
  le serie del periodo chiuso: 29 gruppi), 14 trimestri su 32 in guadagno. Passa solo la condizione dei costi doppi (0,39).
* **Il calcolo è giusto e si riproduce esattamente** con codice e calendario indipendenti: 255 operazioni, +7,58 punti base lordi a
  operazione (t 1,91), serie identica a quella committata (differenza massima 1·10⁻¹⁶). Nessuno sguardo nel futuro: la riga di
  SqueezeMetrics con la data t è calcolata dopo la chiusura di t e decide il giorno dopo. L'esame della miscela rifatto passa
  (correlazione 0,04, miscela nuova 1,124 contro 1,082, t della parte 1,53, 94-95% dei campionamenti con 10 semi diversi).
* **Ma il passaggio sta in un mese: marzo 2020.** 18 operazioni su 255 (il 7%) fanno il **50%** del guadagno lordo; le 4 migliori
  (tutte di marzo 2020) ne fanno metà. **Senza marzo 2020 l'esame non passa**: t della parte **0,86** (soglia 1,3), Sharpe 0,29,
  campionamenti 80%. Senza tutto il 2020 non passa (t 1,06). Con la regola della revisione della prova 37 (un passaggio che cade
  togliendo un solo episodio non conta) questo rovescia l'esito.
* **Differenza dalla prova 37 (da leggere, non cambia l'esito):** qui fuori da marzo 2020 il segnale non è zero. La direzione è giusta
  nel 57% delle operazioni (146 su 255, probabilità per caso 1,2%), ancora nel 57% senza marzo 2020 (134 su 237, 2,6%); togliendo in
  modo simmetrico le migliori e le peggiori l'esame passa; nei giorni con la copertura sopra zero il vantaggio è zero (+0,05 punti
  base, 2.004 operazioni). La copertura delle opzioni aggiunge qualcosa oltre «giornata agitata» (controllo 6), ma con poca forza. È
  un FAIL più debole di quello della prova 37: il segnale ha senso, ma i soldi che fanno passare l'esame vengono da una crisi sola.

## I problemi

**Alto 1 — il passaggio dipende da marzo 2020.** Somma dei rendimenti lordi delle 255 operazioni: +1.934 punti base; marzo 2020
(18 operazioni) +974 (50%). Le 4 migliori (13, 17, 16 e 2 marzo 2020) ne fanno metà, le 10 migliori il 99% (7 di marzo 2020); fra le
5 peggiori 4 sono di febbraio-marzo 2020 (`c5_concentrazione.py`). L'esame della miscela rifatto (`crit.py`):

| Senza | Operazioni | Lordo (t) | Sharpe netto | t della parte (1,3) | Miscela nuova / miscela | Campionamenti (80%) | Esame |
|---|---|---|---|---|---|---|---|
| niente (le regole) | 255 | +7,58 (1,91) | 0,51 | 1,53 | 1,124 / 1,082 | 94% | passa |
| marzo 2020 | 237 | +4,05 (1,37) | 0,29 | **0,86** | 1,178 / 1,160 | 80% | **no** |
| il 2020 | 224 | +4,42 (1,60) | 0,37 | **1,06** | 1,120 / 1,098 | 83% | **no** |
| il 2022 | 151 | +9,09 (1,52) | 0,45 | 1,26 | 1,453 / 1,426 | 87% | no |
| dicembre 2018 e marzo 2020 | 224 | +4,16 (1,40) | 0,30 | 0,90 | 1,229 / 1,210 | 82% | no |
| le 3 migliori | 252 | — | — | 0,78 | 1,104 / 1,091 | 73% | no |
| le 3 migliori e le 3 peggiori | 249 | +6,65 (2,12) | — | 1,64 | 1,173 / 1,133 | 93% | passa |
| le 10 migliori e le 10 peggiori | 235 | +6,72 (2,80) | — | 2,16 | 1,207 / 1,166 | 98% | passa |

Se il vantaggio fosse uguale in tutti i giorni, togliendo 18 operazioni su 255 il t della parte scenderebbe da 1,53 a circa 1,48; scende
a 0,86. Senza il 2022 la caduta è quasi tutta dovuta ai giorni in meno (lo Sharpe resta 0,45), senza marzo 2020 no (lo Sharpe va da
0,51 a 0,29). A favore (`c5b_robusti.py`, `c5c_normalizzato.py`): prova dei segni p 0,012 (senza marzo 2020 p 0,026), Wilcoxon p 0,018
(0,043), media tagliata al 20% +5,27 punti base (t di Yuen 1,99; senza marzo 2020 +4,08, t 1,64); diviso per il VIX della vigilia il
lordo è +4,44 punti base «a VIX 20» (t 2,06), senza marzo 2020 +3,37 (t 1,61), positivo nel 2016, 2018, 2019, 2020 e 2022, negativo nel
2021 (16 operazioni) e 2023 (23). Il sospetto «il risultato può venire da un solo periodo» era scritto prima nelle regole: è confermato
per il guadagno, non per la direzione.

**Medio 1 — la soglia sta sul filo.** Lo zero è scritto prima ed è la scelta naturale; ma spostandolo di un quarto di miliardo di
dollari l'esito cambia: sotto −0,25 miliardi passa (204 operazioni, t della parte 1,35), sotto −0,5 no (t 1,00), sotto −1 no (1,02),
sotto +0,25 no (312 operazioni, t 1,04), sotto +0,5 no (0,93). Le 57 operazioni con la copertura fra 0 e +0,25 miliardi perdono in
media 6,7 punti base, le 51 fra −0,25 e 0 ne guadagnano 6,1 (`c5b_robusti.py`). Vuol dire che un ricalcolo anche piccolo del dato
(Medio 2) potrebbe spostare il risultato.

**Medio 2 — il dato si può controllare solo dal novembre 2021.** Undici copie pubbliche di DIX.csv, salvate fra il novembre 2021 e
oggi (ultime date: 22 e 24 nov 2021, 11 nov 2022, 3 ott 2023, 19 gen 2024, 12 apr 2024 e cinque che vanno oltre il 2024), sono
**identiche** a quella di oggi in tutti i giorni in comune (100%, nessun segno diverso, 256 giorni sotto zero nel 2016-2024 in tutte
quelle complete). Una dodicesima copia è diversa, ma è stata modificata da chi l'ha salvata (non ha nessun valore sotto zero; lo stesso
repository ha anche la copia intatta) (`c2_copie_vecchie.py`). Copie più vecchie non sono raggiungibili da qui (l'archivio web ha una
copia del 29 novembre 2020, ma la connessione cade). Tre fatti pesano: (1) la serie parte dal 2011 ma il metodo è del 2017 (secondo una
fonte terza): almeno il 2016-2017 è stato **calcolato dopo**; (2) la nota di SqueezeMetrics del 19 aprile 2020 racconta che durante il
crollo hanno rifatto la loro copertura («GEX 2.0», buttando via l'ipotesi «tutte le call vendute, tutte le put comprate»): non si sa se
la colonna gratuita `gex` di marzo 2020, che fa metà del risultato, sia stata toccata; (3) la loro pagina dei documenti dice che
«correzioni a monte possono rivedere i file storici». Sugli anni con il dato controllato (2022-2024, 128 operazioni) il lordo è +4,50
punti base (t 1,21), Sharpe 0,48, l'esame non passa (t 0,82); sul 2016-2021 +10,69 (t 1,52), Sharpe 0,53, non passa (t 1,30 arrotondato
per difetto, sotto la soglia). La parte più forte è quella che non si può controllare.

**Medio 3 — la «chiusura ufficiale» di Alpaca non lo è in marzo 2020.** Nei 255 giorni della regola la chiusura al giorno di Alpaca
differisce da quella di Yahoo (che cade sempre dentro la barra dell'asta delle 16:00 di Alpaca, a meno di un centesimo) di più di 1
punto base in 77 giorni e di più di 10 in 13 (3 nel 2018, 10 in marzo 2020; il massimo, il 12 marzo 2020, quasi 300 punti base: il
giornaliero di Alpaca cade negli scambi dopo la chiusura, come trovato nella revisione della prova 37). Fuori da marzo 2020 l'errore è
rumore (+0,01 punti base in media), in marzo 2020 è di +11,3 punti base a operazione **contro** la strategia. Con la chiusura di Yahoo:
lordo +8,40 (t 2,03), Sharpe 0,55, t della parte 1,66, l'esame passa (95%); senza marzo 2020 il lordo resta +4,06 (t 1,36)
(`c4_costi.py`, `c4b_asta.py`, `c7_miscela.py`). Non rovescia niente, ma la regola dice «chiusura ufficiale» e il programma non la usa;
e la miscela della prova 25 usa ancora le chiusure sbagliate di marzo 2020 (Medio 2 della revisione della prova 37, non corretto:
`P025_miscela.csv` non cambia dall'11 novembre).

**Medio 4 — quando il file è disponibile non è scritto da nessuna parte.** Sul contenuto non c'è sguardo nel futuro: la colonna `price`
della riga t è la chiusura dell'S&P 500 dello stesso giorno (2.407 giorni su 2.414 entro 1 punto base, mediana 0,000; contro il giorno
prima la mediana è 48 punti base), quindi la riga t usa dati fino alla chiusura di t e decide t+1 (`c1_date_dix.py`). L'ora di
pubblicazione non è documentata (la pagina dei documenti dice solo che la data è quella della seduta e che non garantisce che ogni campo
fosse pronto alla chiusura; la nota del 2020 dice che il loro dato a pagamento si aggiorna «ogni mattina»). Per il passato non conta; per
il demo bisognerebbe verificare ogni giorno che il file sia aggiornato prima delle 15:30 (è un file gratuito di una società privata,
senza garanzia di servizio).

**Medio 5 — il conto delle prove e la scelta di questa variante.** È la quarta serie della famiglia «ultima mezz'ora» (prova 1 su SPY
e QQQ, prova 23 sulle 10 azioni, ora la 45): il raggruppamento dell'asticella la mette nello stesso gruppo (correlazione 0,64 con la
prova 1 su SPY). Chi ha scritto le regole conosceva il risultato della prova 1, e la variante scelta contiene tutto il vantaggio lordo
che la prova 1 aveva: in tutti i 2.259 giorni +0,90 punti base a operazione (circa 2.030 in somma), nei 255 sotto zero 1.934, negli
altri 2.004 zero. La copertura come filtro viene dall'articolo, non dai dati, e le alternative «agitate» non passano (controllo 6). Ma
dalla prova 32 l'esame della miscela (solo la soglia del t a 1,3 si supera per caso il 9,7% delle volte) è stato fatto da circa 14
prove: due passaggi (37 e 45), quanti se ne aspetterebbero per caso. Sharpe corretto 0,000 con o senza le serie del periodo chiuso
(`c8_conto.py`).

**Basso 1** — vendita allo scoperto il 16 marzo 2020 (+201 punti base) con la regola del rialzo attiva (lo SPY era sceso più del 10%):
un ordine a mercato non può vendere sul prezzo di acquisto migliore; si vende al prezzo di vendita, un centesimo, probabilmente eseguito.
Il 18 marzo 2020 (−167) è al limite del 10%. **Basso 2** — la tassa SEC sulle vendite (al massimo 0,28 punti base a operazione, il
3,7% del lordo) non è contata: la coprono i costi doppi (Sharpe 0,39). **Basso 3** — il t della parte è su tutto il periodo (1,53);
sui giorni della miscela è 1,42; tutti e due sopra 1,3, le regole non dicono quale (come nella prova 37). **Basso 4** — il conto
dell'asticella comprende ancora le 9 serie `*_chiuso` (Basso 2 della prova 37): senza, 29 gruppi invece di 33 e lo Sharpe corretto resta
0,000. **Basso 5** — il programma esclude anche i giorni senza le barre delle 15:58 e 15:59 (ereditato dalla prova 1, dove servivano
per l'uscita), che le regole della 45 non chiedono: tocca 0 giorni (solo il 12 agosto 2019, già escluso). **Basso 6** — con un conto da
10.000 dollari lo Sharpe scende a 0,38 (commissione minima). **Basso 7** — l'idea I8 (uscita all'asta) ha di fatto la sua risposta:
in tutti i giorni con l'uscita all'asta il lordo è +0,90 punti base a operazione (t 1,39), sotto i costi (circa 1,5 punti base); nel
registro è ancora aperta.

## 1. Sguardo nel futuro e tempi

* **La copertura:** il valore che decide il giorno b è quello della riga con la data del giorno di borsa prima (`copertura_del_giorno_prima`,
  rifatto nel mio codice con un calendario diverso: stessi 256 giorni sotto zero, per anno 22, 2, 38, 19, 31, 16, 104, 23, 1). La riga
  t è calcolata con la chiusura di t (vedi Medio 4): nessuna informazione del giorno b. **OK.**
* **Segnale, ingresso, uscita:** segnale = chiusura della barra che inizia 31 minuti prima della chiusura (15:29, o 12:29 nei 18 giorni
  corti) / chiusura dell'ultima barra della seduta di ieri; ingresso = apertura della barra dopo (15:30); uscita = chiusura al giorno
  di Alpaca. È quello che dicono le regole; il mio ricalcolo con lo stesso schema dà la stessa serie. Ingresso un minuto dopo: Sharpe
  0,50 (t 1,49) invece di 0,51 (`c4_costi.py`). **OK.**
* Ordine dei commit: regole, poi programma e test, poi risultati scritti dal lavoro di GitHub. Il file DIX.csv della sessione principale
  nella cartella temporanea è delle 10:42, prima delle regole: coerente con «visti prima solo i conteggi» (non verificabile oltre).

## 2. Il dato di SqueezeMetrics

Vedi Medio 1, 2 e 4. In più: la colonna `gex` è una stima con un'ipotesi fissa su chi tiene le opzioni (le regole lo scrivono fra i
sospetti); SqueezeMetrics stessa, nella nota dell'aprile 2020, dice che l'ipotesi originale non regge e che con il metodo nuovo la
copertura «non può mai diventare molto negativa». Fonti: `squeezemetrics.com/monitor/docs` (letta oggi), la nota
`notes.squeezemetrics.com/2020-04-19.pdf` (letta oggi), la pagina `squeezemetrics.com/monitor/dix`.

## 3. Ricalcolo indipendente (`c0_calendario.py`, `c1_date_dix.py`, `c3_ricalcolo.py`)

* Calendario: `exchange_calendars` dà 2.264 giorni nel 2016-2024 con 18 chiusure anticipate; le barre di Alpaca ci stanno esattamente
  (nessun giorno mancante o in più; l'ultima barra della seduta è la chiusura meno un minuto in tutti i giorni tranne il 12 agosto 2019,
  il giorno escluso dal controllo dei minuti). Nessun doppione nelle barre.
* Risultato: 2.262 segnali validi (3 con r = 0); **sotto zero 255 operazioni, +7,58 punti base (t 1,91), 57% in guadagno**; sopra o
  uguale 2.004, +0,05 (t 0,10), 49%; tutti 2.259, +0,90 (t 1,39). Operazioni per anno uguali. Guadagno senza costi / con i costi /
  doppi +20,2% / +15,8% / +11,6%; Sharpe 0,64 / 0,51 / 0,39; netto medio +5,95 punti base sul conto; anni uguali al risultato. Serie
  committata riprodotta (differenza massima 9,9·10⁻¹⁷). **Nessuna differenza da spiegare.** I 4 test del programma passano.

## 4. I costi (`c4_costi.py`)

* Ingresso: metà dello scarto misurato (0,185 punti base) più 0,5 di slittamento: ragionevole per 100.000 dollari sullo SPY anche nei
  giorni agitati (lo scarto dello SPY resta di solito un centesimo). Uscita all'asta: nessuno scarto, 0,5 di slittamento come margine:
  prudente. Commissioni IB «fisso» su tutte e due le parti. In tutto i costi tolgono lo 0,42% l'anno su un lordo del 2,11%.
* La chiusura di Alpaca come prezzo dell'asta: vedi Medio 3. Ultimo minuto della seduta al posto dell'asta (con scarto e slittamento):
  Sharpe 0,54. Tasse sulle vendite e regola del rialzo: Basso 1 e 2. Prestito dei titoli: non serve (la posizione si chiude in giornata).
* Taglia del conto: 1.000.000 di dollari 0,51, 10.000 dollari 0,38.

**Esito:** le ipotesi sono ragionevoli, anzi un po' pessimiste (l'errore di Alpaca va contro la strategia). Il margine non è il problema.

## 5. Concentrazione (`c5_concentrazione.py`, `c5b_robusti.py`, `c5c_normalizzato.py`)

Anno per anno (operazioni, lordo medio, t, Sharpe netto dell'anno): 2016 21, +7,9, 1,09, 0,86; 2017 2, +10,2, —, 1,09; 2018 38, +8,1,
0,97, 0,79; 2019 19, +5,4, 1,04, 0,75; 2020 31, +30,4, 1,18, 1,11; 2021 16, −11,3, −1,14, −1,26; 2022 104, +5,4, 1,23, 0,90; 2023 23,
+0,7, 0,12, −0,12; 2024 1, −1,6. Il resto è nell'Alto 1.

## 6. La copertura sotto zero è solo «giornata agitata»? (`c6_agitati.py`, criterio scritto prima in `PIANO.md`)

N = 255. (a) i 255 giorni con il VIX della vigilia più alto (soglia 26,8); (b) i 255 con la volatilità di 20 giorni più alta fino al
giorno prima (chiusure di Alpaca).

| Giorni | Operazioni | Lordo (t) | In guadagno |
|---|---|---|---|
| copertura sotto zero (la regola) | 255 | +7,58 (1,91) | 57% |
| (a) VIX alto | 255 (122 in comune) | +5,19 (1,19) | 53% |
| (a) VIX alto e copertura sopra zero | 133 | +0,82 (0,18) | 50% |
| (a) copertura sotto zero e VIX non alto | 133 | +5,41 (1,90) | 58% |
| (b) volatilità alta | 255 (92 in comune) | +6,12 (1,49) | 56% |
| (b) volatilità alta e copertura sopra zero | 163 | +3,59 (1,06) | 56% |
| (b) copertura sotto zero e volatilità non alta | 163 | +5,88 (1,97) | 58% |
| né agitati né sotto zero (a) / (b) | 1.871 / 1.841 | −0,00 / −0,26 | 49% / 48% |

Con i giorni agitati al posto della copertura l'esame della miscela non passa: (a) t della parte 0,85, Sharpe 0,28; (b) t 1,13, Sharpe
0,38. Regressione del lordo su «sotto zero» e sul VIX insieme: +3,4 punti base per «sotto zero» (t 0,90), +3,5 ogni 10 punti di VIX (t
1,02): i dati non separano bene le due cose. **Esito:** la copertura non è solo un modo di dire «giornata agitata» (i giorni agitati con
la copertura positiva non hanno vantaggio, quelli calmi con la copertura negativa sì), come dice l'articolo; ma la prova è debole.

## 7. L'esame per la miscela, rifatto (`crit.py`, `c7_miscela.py`)

* La miscela usata è giusta: `P025_miscela.csv` è la media giornaliera delle sei parti `P007`, `P015`, `P016` su SPY e QQQ (differenza
  1·10⁻¹⁶); `P045_miscela.csv` è tre quarti la miscela e un quarto la parte (1,3·10⁻¹⁶), dal 1° novembre 2016 (2.054 giorni).
* Rifatto con codice mio: Sharpe della parte 0,50 (costi doppi 0,38), correlazione 0,04 (nei soli 236 giorni con un'operazione 0,09),
  miscela nuova 1,124 contro 1,082, tenere lo SPY 0,87 (Yahoo, con i dividendi; il risultato dice 0,89 con Alpaca), t della parte 1,53
  (1,42 sui giorni comuni), campionamenti a blocchi di 20 giorni, 2000 ripetizioni: **94-95% con 10 semi** (compreso il 32 del
  programma). Il campionamento è fatto come dicono le regole (stessi giorni per le due serie, blocchi che si sovrappongono).
* Come nella prova 37, il campionamento non vede la concentrazione: misura la fortuna nell'ordine dei giorni, non la ripetibilità di
  un episodio. Senza marzo 2020 scende all'80%.

## 8. Conto delle prove e asticella (`c8_conto.py`)

Vedi Medio 5 e Basso 4. La prova conta 2 nel registro, come scritto nelle regole; la famiglia «ultima mezz'ora» arriva così a 5 serie
nel conto (prova 1: 2; prova 23: 1 delle 5; prova 45: 2). Lo Sharpe giornaliero della parte (0,032) è un quinto della soglia «per caso»
con 29 gruppi (0,158, cioè 2,50 l'anno).

## 9. Altro nel codice e nelle regole

Nessun errore che cambi i numeri. Le piccole cose sono nei Bassi 3, 4 e 5. Il programma legge tutto DIX.csv dalla rete (comprese le
righe del 2025-2026) ma usa solo i giorni del calendario 2016-2024: nessun dato del periodo chiuso entra nel calcolo; sarebbe più pulito
tagliarlo subito dopo la lettura.

## Domande aperte

1. **Una parte che guadagna soprattutto nelle crisi.** Qui, a differenza della prova 37, la direzione è giusta più spesso del caso
   anche fuori da marzo 2020; ma l'esame passa solo grazie a quel mese. Accettare una parte «da crisi» è un'altra domanda, con regole
   scritte prima e un secondo episodio indipendente. Decide la sessione principale.
2. **Il periodo chiuso non sarebbe una prova cieca.** Il crollo dell'aprile 2025 è noto a tutti e quasi certamente ha giorni con la
   copertura negativa: il risultato lì dipenderebbe di nuovo da pochi giorni. Con questo FAIL le regole dicono di non aprirlo.
3. **Una copia di DIX.csv di prima dell'aprile 2020** (l'archivio web ne ha una del 29 novembre 2020, non raggiungibile da qui; meglio
   ancora una del 2018-2019) chiuderebbe il Medio 2 per marzo 2020.
4. Il Medio 3 (chiusure di Alpaca di marzo 2020 nella miscela della prova 25) e il Basso 4 (serie `*_chiuso` nell'asticella) toccano
   tutte le prove della miscela: segnalati già nella revisione della prova 37, ancora aperti.
5. L'idea I8 nel registro andrebbe chiusa con il numero del Basso 7.

## Gli script del revisore

Tutti in `/tmp/claude-0/-home-user-agentic-trading-system/55688ced-bd2e-59dc-8673-d3e30f31b49e/scratchpad/revisione_p045/` (fuori
dal repository: la cartella si può svuotare), da lanciare con `python3 <percorso completo>` dalla cartella stessa: `PIANO.md` (metodo
scritto prima), `comune.py` (blocco delle date, calendario `exchange_calendars`, lettura dei dati), `yahoo.py`, `c0_calendario.py`,
`c1_date_dix.py`, `c2_copie_vecchie.py`, `c3_ricalcolo.py` (ricalcolo indipendente; scrive `ops.csv` e `serie_rev.csv`), `c4_costi.py`,
`c4b_asta.py`, `c5_concentrazione.py`, `c5b_robusti.py`, `c5c_normalizzato.py`, `c6_agitati.py`, `crit.py` (esame della miscela),
`c7_miscela.py`, `c8_conto.py`, `c9_da_sola.py`. I file scaricati (DIX.csv di oggi, le 12 copie vecchie, Yahoo) sono nelle
sottocartelle `dl_dix/` e `dl_yahoo/`; non entrano nel repository.
