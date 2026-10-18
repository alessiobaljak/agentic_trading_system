# M-002 — Ogni mese i segnali che hanno battuto il caso nei 12 mesi prima, sulle 100 monete

Scheda scritta il 18 ottobre 2026 **prima di qualunque calcolo** (REGOLE.md, sezioni 8 e 9). Si prova **solo in avanti**
(periodo A, dal 2026-10-01): il passato è già usato da M-001, di cui è parente.

## Perché

M-001c sul passato ha guadagnato +1,32% a trade, ma due terzi venivano dall'essere long nei mesi in cui il mercato saliva
(`idee/M-001/diagnosi.json`: ingressi a caso nello stesso mese +0,91%). M-002 sceglie invece le celle per il loro
**vantaggio sul caso** (il netto meno quello che avrebbe reso la stessa direzione tenuta per lo stesso tempo a un'ora
qualunque dello stesso mese e della stessa moneta): le celle che sanno quando entrare, non quelle che seguono il mercato.

## La procedura (`strumenti/meta2.py`)

Come M-001c (candidate: tutte le celle a una moneta delle esplorazioni nei due versi; ogni inizio mese, solo i trade già
chiusi nei 12 mesi prima; 10 celle, al massimo 2 per famiglia, mai i due versi della stessa cella; costi con lo scarto
doppio), con il punteggio sul t del vantaggio sul caso (almeno 30 trade, netto medio > 0, vantaggio medio > 0, t ≥ 2).
Monete: le 100 di `universo_top100.json`.

## La prova

REGOLE.md, sezione 9 (registrata in `avanti.md`).
