# Programma 7 — quarantesima prova: il momento in giornata, le prime 23 ore decidono l'ultima (G25)

Scritto il 25 ottobre 2026, alle 08:41 UTC, **prima di qualunque calcolo**. Idea 72 della coda di `research/REGISTRO.md`. Il trading
di ogni giorno (programma 7) non va lasciato indietro: questa è una regola in giornata, un'operazione al giorno per moneta, chiusa
prima della mezzanotte. Il controllo di fattibilità ha contato solo le candele: 14 monete grandi hanno le candele orarie dal 2020.

## 1. Perché, e il dubbio

Nelle azioni è documentato il «momento in giornata»: il rendimento della prima parte della giornata prevede quello dell'ultima mezz'ora
(Gao, Han, Li e Zhou, *Journal of Financial Economics* 2018), perché chi copre le posizioni e chi ribilancia lo fa alla fine della
giornata nella direzione del movimento. Le crypto non chiudono, ma la mezzanotte UTC è il momento dei conti giornalieri: i regolamenti,
le candele giornaliere, i ribilanci dei fondi e dei prodotti a leva. Studi sul Bitcoin trovano versioni dello stesso effetto; non ne
ricordo i numeri e qui non li uso: la regola si fissa prima, da sola. **Il dubbio scritto prima**: un'ora sola di tenuta muove in media
poco, e i costi di un giro (circa 0,12% sul Bitcoin, di più sulle altre) possono mangiare tutto; il fatto è noto e potrebbe essere già
sparito. Probabilità bassa. Si riporta anche il lordo, per capire se la prevedibilità c'è e sono i costi a toglierla.

## 2. La regola (valori fissati qui)

* **Monete**: le 14 con le candele orarie dal 2020 nel nostro archivio: BTC, ETH, BCH, LTC, XRP, LINK, TRX, ADA, BNB, DOGE, DOT, AVAX,
  UNI, SOL (perpetui `USDT`).
* **Ogni giorno d** dal 4 gennaio 2021 al 4 ottobre 2026: il **segnale** è il rendimento dall'apertura delle 00:00 UTC alla chiusura
  della candela delle 22:00 (le prime 23 ore). **Operazione**: nella direzione del segno, entrata all'apertura delle 23:00, uscita
  all'apertura delle 00:00 del giorno dopo; costi della moneta (`seconda.costi_moneta`: commissione a mercato più scarto) in entrata e
  in uscita; niente funding (nessun regolamento fra le 23:00 e le 24:00). Segnale zero o candele mancanti: nessuna operazione.
* **Portafoglio**: ogni giorno le operazioni delle monete con lo stesso peso (1/14 del capitale ciascuna, al massimo il 100%).
* **Controllo**: lo stesso conto con il segno del segnale preso a caso (2.000 estrazioni, seme 2026).
* Una prova nel conto (G25): **172**.

## 3. L'esame

Media per operazione sopra zero con p ≤ 0,01 (bootstrap sui giorni), positiva nelle due metà (2021-2023, 2024-2026); il portafoglio
giornaliero con `terza.esame` sulle settimane, Sharpe corretto rivisto e t, la regola del proprietario. Descrittivo: il lordo prima dei
costi, per moneta e per anno, e la quota di estrazioni a caso che fa almeno come il segno vero.
