# Prova a placebo dell'esame di gruppo — risultati (11 ottobre 2026)

Regole scritte e committate prima del lancio: `regole.md`, commit **39d095877452dfd85eac2e6201c4fe5a3816d75f**
(10 ottobre, 17:10 UTC, branch `research/coordinamento`). Il codice della prova (`placebo_gruppo.py`, `esegui.py`,
`riassunto.py`) e `regole.md` non sono cambiati dopo quel commit (`git diff 39d09587 HEAD` su quei file: vuoto).
Esiti grezzi: `esiti_k0.jsonl` … `esiti_k3.jsonl` (192 righe, una per placebo e periodo; ogni riga porta
`commit_file_della_prova` 39d09587 e le cinque impronte). Lancio dal 10 ottobre alle 17:11 UTC all'11 ottobre alle
07:52 UTC, in 9 pezzi da circa 100 minuti su 4 processori; un riavvio della macchina del coordinamento (11 ottobre,
02:38 UTC) ha fermato il sesto pezzo senza perdere righe (tutte leggibili; ripreso dalle mancanti). Misure calcolate
con `riassunto.py` (uscita completa in fondo, codice d'uscita 0).

**Le cinque impronte** (punto 7 delle regole) sono quelle delle righe e quelle dei file del branch principale l'11
ottobre alle 07:55 UTC (`sha256sum`), invariate dal commit 2a88046a (dopo, sul principale, è cambiato solo
`research/src/guardiano.py`, che non è fra le cinque):

```
1f3fe8c8218cd32711b153b05872ac1042e417b2d7fe3b142a2a1972794c81cb  research/src/gruppo.py
ca027d2687d9129a533077eb980c0517bd09c476331659d61eaf15dda45c9e5a  research/src/statistica.py
5a3998c5f0a1535d255b5bf6fc3a367a5805a7ff9766024d74df096816e89c42  research/src/motore.py
4b9ed237125ede9fc6d5103cdf93f6a382309649e34d5b07686f58be59ab8a6d  research/src/dati.py
7f530082d7d5119d9e12e99a0bbe44548f9671c9b28aa70f77f97d6c2b4edfa7  research/config/parametri.yaml
```

## Esito, con la regola scritta prima

**L'esame di gruppo regge sui prezzi veri.** Tutte e quattro le condizioni (`regole.md`, punto 5; GRUPPO, sezione
11, punto 3) valgono, e nessuna è al limite.

| Misura | Valore | Limite | Regge |
|---|---|---|---|
| M1: placebo «nette» (z > 2,00) in costruzione | **0 su 85** (0,00%) | ⌊0,03 · 85⌋ = 2 | sì |
| M2: placebo con p sotto 0,10 (z > 1,2816) in validazione | **2 su 93** (2,15%) | ⌊0,13 · 93⌋ = 12 | sì |
| M3 costruzione: 1 − Φ((2,00 − μ)/σ), μ 0,055, σ 0,672 | **0,19%** | 3% | sì |
| M3 validazione: 1 − Φ((1,2816 − μ)/σ), μ 0,068, σ 0,643 | **2,95%** | 13% | sì |

Copertura: 192 righe su 192 (24 combinazioni × 4 sfasamenti × 2 periodi), 0 errori. Campione: 85 placebo valutabili
in costruzione e 93 in validazione (minimo 80 per periodo: nessuno sfasamento in più). Non valutabili: 11 in
costruzione e 2 in validazione con meno di 3 blocchi interi (o candidato senza rumore stimabile), 1 in validazione
perché gli ingressi casuali non entrano su GTCUSDT. Nessuna placebo sotto i minimi di trade (trade sommati: mediana
8.573 in costruzione, minimo 1.551; mediana 5.260 in validazione, minimo 931). Intervalli al 95% ricampionando le 24
combinazioni: coda M3 0,03-0,59% in costruzione e 1,04-5,49% in validazione, quota M2 0-5,38%: le soglie stanno fuori.

**Ricalcolo indipendente** del coordinamento dagli esiti grezzi (z = Φ⁻¹(T(t)) con la t di Student del confronto con
la (b), stesse esclusioni): 85 / 0 / μ 0,055 / σ 0,672 / 0,19% in costruzione, 93 / 2 / μ 0,068 / σ 0,643 / 2,95% in
validazione. Coincide.

## Cosa vuol dire

* **L'esame di gruppo non promuove il rumore**, nemmeno con i trade a grappoli fra monete: nessuna placebo «netta» in
  costruzione, 2 su 93 sotto p 0,10 in validazione (2,15% contro il 10% che darebbe il caso puro).
* **È più severo di quanto dichiara, ancora più dell'esame per moneta.** Gli z hanno deviazione standard 0,67 in
  costruzione e 0,64 in validazione invece di 1 (il 9 ottobre, per moneta, 0,815), con il centro giusto (μ 0,06-0,07).
  Il prezzo è la **potenza**: un vantaggio vero ma piccolo passa più difficilmente di quanto dice la sezione 15 di
  `regole.md`. Le regole d'esame non si cambiano guardando questi numeri.
* **Regge anche senza il pavimento delle strategie sfasate** (solo informativo): M2 3 su 93, M3 4,58% in validazione;
  in costruzione 0 nette, M3 0,25%. Dove il pavimento delle sfasate decide (19 placebo in costruzione, 33 in
  validazione), la deviazione standard di (R medio − B)/pavimento è 0,578 e 0,833: sotto 1,10, quindi **nessuna
  correzione da proporre** al pavimento (regole, punto 5). Togliendo dal pavimento la sfasata più vicina agli ingressi
  della regola non cambia lettura nessuna placebo (0 su 85, 0 su 93).
* **Effetto grappolo misurato sui prezzi veri: mediana 12,5 in costruzione e 12,2 in validazione** (errore² · N /
  varianza degli R): i trade sommati valgono circa un dodicesimo di altrettanti trade indipendenti. Conferma la stima
  del 10 ottobre (circa un decimo, simulazione del coordinamento in `regole.md`, sezione 15). La moneta più presente
  pesa al massimo il 4,32% dei trade (limite 10%).
* **Da tenere per il vault (informativo):** in validazione 14 placebo su 93 (15,05%) hanno R medio sopra il 90°
  percentile delle proprie sfasate, contro il 10% atteso (con 93 placebo il caso dà circa 9 ± 3: 14 è sopra di circa
  1,6 deviazioni). Le sfasate abbassano molto il 26% stimato per gli ingressi casuali indipendenti (`regole.md`,
  sezione 9), ma la condizione del percentile può passare per caso un po' più del 10%: il tasso del caso del vault si
  calcola comunque come scrive la sezione 9, punto 4.

## Limiti

Regole d'ingresso e uscite fisse da manuale, non le idee della campagna; solo regole su una moneta alla volta; nessuna
verifica della Fase 4. In 70 righe su 192 (incrocio delle medie, rottura e MACD, le uscite senza chiusura a tempo) la
durata massima dei trade è a meno di 60 barre dal margine di 30 giorni: lo spostamento in cerchio potrebbe far
guardare a un trade i prezzi vicini al segnale vero, ma le regole da manuale non hanno vantaggio e nessuna lettura
cambia togliendo la sfasata più vicina. La prova misura i falsi positivi dell'esame di gruppo, non la sua potenza su
un vantaggio vero.

## Cosa succede adesso (scritto nelle regole, punto 6)

L'esame regge: il coordinamento scrive il via libera quando la sessione di gruppo lo chiede (GRUPPO, sezione 7, punto
2), con le cinque impronte qui sopra. Se una delle cinque impronte cambia durante la campagna, la prova si rifà intera
prima del via libera. I numeri restano su questo branch fino alla consegna del gruppo (GRUPPO, sezione 11, punto 5).

## Uscita completa di `riassunto.py`

```
file di k [0, 1, 2, 3]; righe 192, illeggibili 0; commit principale ['18b3f39a', '2a88046a', '626a2970', 'ad227319', 'ad3439a8', 'b0119758'], prova ['12b3b52f', '39d09587', '8ff80d4d', '95f876d2']
sfasamenti usati [0, 1, 2, 3]; copertura: 192 su 192 (24 combinazioni x 4 sfasamenti x 2 periodi); righe con errore 0, errori senza una riga buona 0
campione: valutabili in costruzione 85, in validazione 93 (minimo 80 per periodo); scarti in costruzione {}; validazione sotto il minimo di trade 0
non valutabili: {'costruzione: meno di 3 blocchi interi o candidato senza rumore stimabile': 11, 'validazione: gli ingressi casuali non entrano su: GTCUSDT': 1, 'validazione: meno di 3 blocchi interi o candidato senza rumore stimabile': 2}
costruzione: n 85; M1 0 con z > 2 (limite 2, quota 0.00%); μ 0.055, σ 0.672; M3 P(z > 2) 0.19% (soglia 3.00%)
validazione: n 93; M2 2 con z > 1,282 (limite 12, quota 2.15%); μ 0.068, σ 0.643; M3 P(z > 1,282) 2.95% (soglia 13.00%)
condizioni: M1 regge, M2 regge, M3_costruzione regge, M3_validazione regge
ESITO: l'esame di gruppo regge sui prezzi veri
--- solo informative ---
letture diverse fra z e «netta»/«p < 0,10» del confronto, costruzione: 0
letture diverse fra z e «netta»/«p < 0,10» del confronto, validazione: 0
senza il pavimento delle sfasate, costruzione: n 85; M1 0 con z > 2 (limite 2, quota 0.00%); μ 0.059, σ 0.691; M3 P(z > 2) 0.25% (soglia 3.00%)
senza il pavimento delle sfasate, validazione: n 93; M2 3 con z > 1,282 (limite 12, quota 3.23%); μ 0.060, σ 0.724; M3 P(z > 1,282) 4.58% (soglia 13.00%)
dove decide il pavimento delle sfasate, costruzione: 19 placebo, sd((R - B)/pavimento) 0.578
dove decide il pavimento delle sfasate, validazione: 33 placebo, sd((R - B)/pavimento) 0.833
validazione, R medio sopra il 90° percentile delle proprie sfasate: 14 su 93 (15.05%, atteso circa 10%)
costruzione: effetto grappolo mediana 12.48 (25-75%: 9.35-16.94); quota della moneta piu' presente mediana 3.15%, massimo 4.32%
validazione: effetto grappolo mediana 12.19 (25-75%: 9.56-16.07); quota della moneta piu' presente mediana 1.94%, massimo 2.50%
intervalli al 95% ricampionando le combinazioni, costruzione: quota 0.00%-0.00%; μ -0.060-0.178; σ 0.562-0.765; coda M3 0.03%-0.59%
intervalli al 95% ricampionando le combinazioni, validazione: quota 0.00%-5.38%; μ -0.061-0.202; σ 0.536-0.738; coda M3 1.04%-5.49%
per timeframe:
  1h costruzione: n 43; M1 0 con z > 2 (limite 1, quota 0.00%); μ -0.082, σ 0.701; M3 P(z > 2) 0.15% (soglia 3.00%)
  1h validazione: n 47; M2 1 con z > 1,282 (limite 6, quota 2.13%); μ 0.135, σ 0.550; M3 P(z > 1,282) 1.85% (soglia 13.00%)
  4h costruzione: n 42; M1 0 con z > 2 (limite 1, quota 0.00%); μ 0.196, σ 0.618; M3 P(z > 2) 0.18% (soglia 3.00%)
  4h validazione: n 46; M2 1 con z > 1,282 (limite 5, quota 2.17%); μ -0.000, σ 0.726; M3 P(z > 1,282) 3.87% (soglia 13.00%)
per direzione:
  long costruzione: n 46; M1 0 con z > 2 (limite 1, quota 0.00%); μ 0.042, σ 0.705; M3 P(z > 2) 0.27% (soglia 3.00%)
  long validazione: n 47; M2 1 con z > 1,282 (limite 6, quota 2.13%); μ 0.119, σ 0.693; M3 P(z > 1,282) 4.67% (soglia 13.00%)
  short costruzione: n 39; M1 0 con z > 2 (limite 1, quota 0.00%); μ 0.071, σ 0.640; M3 P(z > 2) 0.13% (soglia 3.00%)
  short validazione: n 46; M2 1 con z > 1,282 (limite 5, quota 2.17%); μ 0.016, σ 0.590; M3 P(z > 1,282) 1.60% (soglia 13.00%)
per regola:
  bollinger costruzione: n 16; M1 0 con z > 2 (limite 0, quota 0.00%); μ 0.030, σ 0.694; M3 P(z > 2) 0.23% (soglia 3.00%)
  bollinger validazione: n 16; M2 0 con z > 1,282 (limite 2, quota 0.00%); μ -0.213, σ 0.785; M3 P(z > 1,282) 2.84% (soglia 13.00%)
  incrocio_medie costruzione: n 14; M1 0 con z > 2 (limite 0, quota 0.00%); μ 0.123, σ 0.841; M3 P(z > 2) 1.28% (soglia 3.00%)
  incrocio_medie validazione: n 16; M2 1 con z > 1,282 (limite 2, quota 6.25%); μ 0.201, σ 0.700; M3 P(z > 1,282) 6.12% (soglia 13.00%)
  macd costruzione: n 12; M1 0 con z > 2 (limite 0, quota 0.00%); μ -0.038, σ 0.430; M3 P(z > 2) 0.00% (soglia 3.00%)
  macd validazione: n 15; M2 0 con z > 1,282 (limite 1, quota 0.00%); μ 0.110, σ 0.600; M3 P(z > 1,282) 2.55% (soglia 13.00%)
  momento_10 costruzione: n 16; M1 0 con z > 2 (limite 0, quota 0.00%); μ 0.006, σ 0.484; M3 P(z > 2) 0.00% (soglia 3.00%)
  momento_10 validazione: n 16; M2 0 con z > 1,282 (limite 2, quota 0.00%); μ 0.154, σ 0.476; M3 P(z > 1,282) 0.90% (soglia 13.00%)
  rottura_20 costruzione: n 11; M1 0 con z > 2 (limite 0, quota 0.00%); μ -0.072, σ 0.692; M3 P(z > 2) 0.14% (soglia 3.00%)
  rottura_20 validazione: n 14; M2 0 con z > 1,282 (limite 1, quota 0.00%); μ -0.083, σ 0.452; M3 P(z > 1,282) 0.13% (soglia 13.00%)
  rsi costruzione: n 16; M1 0 con z > 2 (limite 0, quota 0.00%); μ 0.227, σ 0.830; M3 P(z > 2) 1.63% (soglia 3.00%)
  rsi validazione: n 16; M2 1 con z > 1,282 (limite 2, quota 6.25%); μ 0.223, σ 0.728; M3 P(z > 1,282) 7.29% (soglia 13.00%)
limiti: finestra unione diversa da quella del pavimento in 0 placebo []; durata massima dei trade a meno di 60 barre dal margine in 70 ['GRUPPO|1h|rottura_20|short|costruzione|0', 'GRUPPO|1h|macd|long|costruzione|0', 'GRUPPO|1h|macd|short|costruzione|0', 'GRUPPO|4h|incrocio_medie|long|costruzione|0', 'GRUPPO|4h|incrocio_medie|short|costruzione|0', 'GRUPPO|4h|rottura_20|long|costruzione|0', 'GRUPPO|4h|macd|long|costruzione|0', 'GRUPPO|1h|incrocio_medie|long|costruzione|1', 'GRUPPO|1h|rottura_20|long|costruzione|1', 'GRUPPO|1h|rottura_20|short|costruzione|1', 'GRUPPO|1h|macd|short|costruzione|1', 'GRUPPO|4h|incrocio_medie|long|costruzione|1', 'GRUPPO|4h|rottura_20|long|costruzione|1', 'GRUPPO|4h|macd|short|costruzione|1', 'GRUPPO|1h|incrocio_medie|short|costruzione|2', 'GRUPPO|1h|rottura_20|long|costruzione|2', 'GRUPPO|1h|macd|long|costruzione|2', 'GRUPPO|1h|macd|short|costruzione|2', 'GRUPPO|4h|incrocio_medie|long|costruzione|2', 'GRUPPO|4h|incrocio_medie|short|costruzione|2', 'GRUPPO|4h|rottura_20|long|costruzione|2', 'GRUPPO|4h|macd|long|costruzione|2', 'GRUPPO|4h|macd|short|costruzione|2', 'GRUPPO|1h|incrocio_medie|long|costruzione|3', 'GRUPPO|1h|incrocio_medie|short|costruzione|3', 'GRUPPO|1h|rottura_20|long|costruzione|3', 'GRUPPO|1h|macd|long|costruzione|3', 'GRUPPO|4h|incrocio_medie|long|costruzione|3', 'GRUPPO|4h|incrocio_medie|short|costruzione|3', 'GRUPPO|4h|rottura_20|long|costruzione|3', 'GRUPPO|4h|rottura_20|short|costruzione|3', 'GRUPPO|4h|macd|long|costruzione|3', 'GRUPPO|4h|macd|short|costruzione|3', 'GRUPPO|1h|rottura_20|long|validazione|0', 'GRUPPO|1h|rottura_20|short|validazione|0', 'GRUPPO|1h|macd|long|validazione|0', 'GRUPPO|4h|incrocio_medie|long|validazione|0', 'GRUPPO|4h|incrocio_medie|short|validazione|0', 'GRUPPO|4h|rottura_20|long|validazione|0', 'GRUPPO|4h|rottura_20|short|validazione|0', 'GRUPPO|4h|macd|long|validazione|0', 'GRUPPO|4h|macd|short|validazione|0', 'GRUPPO|1h|incrocio_medie|long|validazione|1', 'GRUPPO|1h|rottura_20|short|validazione|1', 'GRUPPO|1h|macd|long|validazione|1', 'GRUPPO|4h|incrocio_medie|long|validazione|1', 'GRUPPO|4h|incrocio_medie|short|validazione|1', 'GRUPPO|4h|rottura_20|long|validazione|1', 'GRUPPO|4h|rottura_20|short|validazione|1', 'GRUPPO|4h|macd|long|validazione|1', 'GRUPPO|4h|macd|short|validazione|1', 'GRUPPO|1h|incrocio_medie|short|validazione|2', 'GRUPPO|1h|rottura_20|long|validazione|2', 'GRUPPO|1h|rottura_20|short|validazione|2', 'GRUPPO|1h|macd|long|validazione|2', 'GRUPPO|4h|incrocio_medie|long|validazione|2', 'GRUPPO|4h|incrocio_medie|short|validazione|2', 'GRUPPO|4h|rottura_20|short|validazione|2', 'GRUPPO|4h|macd|long|validazione|2', 'GRUPPO|4h|macd|short|validazione|2', 'GRUPPO|1h|incrocio_medie|long|validazione|3', 'GRUPPO|1h|rottura_20|long|validazione|3', 'GRUPPO|1h|rottura_20|short|validazione|3', 'GRUPPO|1h|macd|long|validazione|3', 'GRUPPO|1h|macd|short|validazione|3', 'GRUPPO|4h|incrocio_medie|long|validazione|3', 'GRUPPO|4h|incrocio_medie|short|validazione|3', 'GRUPPO|4h|rottura_20|long|validazione|3', 'GRUPPO|4h|macd|long|validazione|3', 'GRUPPO|4h|macd|short|validazione|3']
  senza la sfasata piu' vicina agli ingressi della regola, costruzione: 0 su 85 cambiano lettura; distanza 0 in 2; distanza mediana 13.0 barre; scarto mediano -0.13 sd
  senza la sfasata piu' vicina agli ingressi della regola, validazione: 0 su 93 cambiano lettura; distanza 0 in 6; distanza mediana 3.0 barre; scarto mediano 0.42 sd
```
