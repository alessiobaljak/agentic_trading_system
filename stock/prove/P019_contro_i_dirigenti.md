# Prova 19 — tenere lo SPY e vendere allo scoperto i titoli appena comprati dai dirigenti (periodo chiuso)

Regole scritte il 25 ottobre 2026 **prima di qualsiasi calcolo** (idea I20 di `REGISTRO.md`; il proprietario: «se loro comprano noi
andiamo short»), committate prima di lanciare il programma.

## Perché, e perché decide solo il periodo chiuso

La prova 18 ha trovato che nelle aziende dell'S&P 500, nel mese dopo l'acquisto di un dirigente, il titolo fa peggio dello SPY: −0,59% in
media su 1457 acquisti, t −3,0. **La regola nasce da quel risultato**, trovato dopo 47 prove: sul 2016-2024 non può essere validata.
**L'esito lo decide solo il periodo chiuso** (gennaio 2025 → settembre 2026), aperto una volta per questa famiglia. I dati della SEC
arrivano ai depositi del primo trimestre 2026: gli ingressi del periodo chiuso vanno dal 2 gennaio 2025 al 31 marzo 2026. Il 2016-2024
si calcola solo da leggere.

## La regola

* **Sempre lo SPY:** il 98% del conto, comprato alla prima seduta.
* **Gli eventi:** come la prova 18 (moduli 4 della SEC, acquisti sul mercato di dirigenti e consiglieri, almeno 100'000 dollari per
  azienda e giorno di deposito, dopo la pulizia dei prezzi; aziende nell'S&P 500 quel giorno; cambi di simbolo).
* **Vendita allo scoperto:** a mercato all'apertura del primo giorno di borsa dopo il deposito, il **5%** del conto, azioni intere; al
  massimo 20 titoli insieme (prima gli acquisti di valore più alto). **Ricopertura** a mercato all'apertura del 21° giorno di borsa dopo
  l'ingresso. Leva massima 2 (lo SPY più gli scoperti).
* **Costi:** come la prova 18, più il **prestito dei titoli venduti allo scoperto: 1% l'anno** (per le azioni dell'S&P 500 di solito è
  molto meno; fissato qui per prudenza), e il 6% l'anno sui contanti sotto zero. Costi doppi.
* **Dividendi:** chi è allo scoperto li paga (il simulatore lo fa).

## L'esame, solo sul periodo chiuso

(1) Sharpe annuo con i costi più alto del comprare e tenere lo SPY sugli stessi giorni; (2) con i costi doppi la strategia guadagna più
del tenere lo SPY; (3) almeno 4 trimestri su 7 in guadagno. Da leggere accanto: il rendimento medio per evento rispetto allo SPY (deve
essere negativo perché lo scoperto guadagni) e il suo t. Nel conto: **1 prova più 1 apertura = 2** (49).
