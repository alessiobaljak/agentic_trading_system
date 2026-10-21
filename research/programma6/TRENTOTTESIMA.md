# Programma 6 — trentottesima prova: solo lo short delle rotture verso il basso dove i long pagano (T7), conferma sulle monete 101-200

Scritto il 21 ottobre 2026, **prima del calcolo**. Vale `TRENTAQUATTRESIMA.md` dove qui non si dice altro.

## 1. Perché

In tre prove sulle 100 monete più scambiate il lato short delle rotture verso il basso guadagna e il long perde: T1 short
+0,19% a operazione, T2 (con il funding alto) +0,32%, T6 (entrata a limite) +0,36%; i long −0,57%, −0,31%, −0,28%. **Visto
dopo il calcolo**, quindi sulle 100 non vale come prova. L'ipotesi, scritta ora: **una rottura verso il basso in una moneta
dove i long pagano molto di funding continua**, perché i long affollati devono uscire. La si prova su monete dove questa
regola non è mai stata guardata: le **101-200** per volume.

## 2. La regola

* Monete: ogni settimana le **101-200** per volume (terza prova con `da=100, a=200`), dati corretti; 503 monete, tutte con le
  candele a 1 ora.
* Solo **short**: chiusura a 4 ore sotto il minimo delle 20 candele prima, con il funding dei 7 giorni nel **40% più alto**
  fra le monete 101-200 di quel giorno.
* Entrata all'apertura della candela dopo (a mercato); uscite come T2 (stop 2 ATR, uscita mobile 3 ATR, al massimo 42
  candele); costi 0,05% più **0,10%** di scarto all'entrata e all'uscita (le monete 101-200); funding incassato.
* Dal 4 gennaio 2021 al 10 ottobre 2026.

## 3. L'esame (conferma: una regola sola su dati non usati)

Per operazione: media netta sopra zero con **p ≤ 0,01** a una coda (bootstrap sulle settimane d'entrata), positiva nelle due
metà e senza le 5 migliori. Si riporta anche il portafoglio (5% a operazione, al massimo 20 aperte). Una prova di conferma,
nel registro.
