# Indice della memoria dell'auditor (massimo 40 righe)
Aggiornato: 2026-11-27. Leggere all'inizio di ogni invocazione questo file e `KNOWN_PITFALLS.md`; il resto solo se serve.
## Stato degli audit per strategia
| Strategia | Ultimo audit | Verdetto | Note |
|---|---|---|---|
| Prova 28: K2, F5 + M7 + K2 (riesame) | 2026-11-11 | PASS tecnico | Alti: Sharpe corretto 0,75/0,47 con N = conto, 0,89/0,69 con N = gruppi; regole: «non candidate» |
| Prova 113: N3G, monete gratis (riesame) | 2026-11-11 | PASS tecnico del «no» | corretta p 0,0268 (serve 0,01); Alto: eventi della 32 da rifare (19 persi); tocca anche N3 nel paper |
| G1 (demo, candidata ai soldi veri; configurazione 280 USDT) | 2026-11-12 | PASS tecnico | Alti: esame 0,80 solo con il limite della ricerca (A 0,81, a mercato 0,77); GTC al mark; soglia cambiata dopo; moneta fino al 44% |
| Prova 96: G22, deriva del Bitcoin dopo la Fed (riesame) | 2026-11-12 | PASS tecnico del «no» | p 0,0205 rifatta identica; nessun errore la porta a 0,01; Medi: controllo a caso esagera, limite macro di 2 ore |
| Prova 55: C3, punteggio unico F5 + K2 + M7 (riesame) | 2026-11-12 | FAIL del calcolo, «no» confermato | settimana oltre il periodo; «peggio di F5» falso sulle stesse settimane (1,87 contro 1,61); corretto oggi 0,75 |
| Mazzo dello Sharpe corretto (`asticella.py`, `78235da`) | 2026-11-12 | FAIL del mazzo | numeri rifatti identici; 27 varianti senza serie tolte, 81-82 senza filtro, conferme dentro; corretti G1 0,733, miscela 0,797/0,802 |
| Prova 157: CB, funding coperto su BTC ed ETH | 2026-11-15 | FAIL del calcolo | margine senza perdite chiuse: 9 e 5 liquidazioni; con margine possibile 7,3%/7,4% (non 10,5%), dal 2022 circa 4%; rifatta come 161 |
| Prova 161: CM, funding coperto con il margine vero (la 157 rifatta) | 2026-11-15 | PASS tecnico | Alti: settimane legate (t corretto 2,4-3,2, Sharpe l'anno ~0,9-1,0); bot senza pronti e trasferimenti; dal 2022 ~3%, ultimi 12 mesi ~1,3% |
| F5 nel conto vero (prova 24; 280, 300 e 1.000 USDT) | 2026-11-27 | FAIL a 280-300; PASS tecnico a 1.000 | filtri veri a 280: 1,40-1,57, 2026 fra −5% e +1%, discesa −32/−33%; sotto il minimo non chiude (TUT −13,8%); per Alessio: N dell'esame (24: 0,96; 56: 0,90; oggi 0,51), taglia (codice a 300), chiusure «solo riduzione», costo dei limiti, stop −35% |
| G11, G1N, eventi (paper); vecchie `bot/strategies/` (ferme dal 13 ott) | mai | — | solo elenco con lo stato al prossimo avvio completo |

## Cosa contiene ogni file
- `KNOWN_PITFALLS.md`: errori del repo, con file e schema da cercare (sempre). `AUDIT_LOG.md`: una riga per audit.
- `reports/AAAA-MM-GG-<strategia>.md`: rapporto completo. Da leggere solo DOPO aver formato il verdetto, per i problemi tornati.
- `repro/` (esiti in `*_esito*.json`): `prova28_*.py` (settimanali del programma 6: taglio, entrata oraria, conto unico, filtri);
  `g1_2026-11-12.py`, `g1_parte2_*` (G1 e conti giornalieri di `nucleo`: cache `CACHE_G1N`, parte `base` prima); `prova113_*` (eventi
  orari, ore in cartella temporanea); `prova96_*` (p in otto modi); `prova55_*` (punteggio a parti); `mazzo_2026-11-12.py` (prima
  `cache <cartella>`, poi `numeri`, `copertura`, `allinea`, `eventi`, `sensi`, `regola_scritta`, `fino57`, `varianti_g1`);
  `prova157_2026-11-15.py` (coperture: `scarica <cartella>`, `dati`, `rifai`, `margine`, `filtri`, `extra`, `esempio`); `prova161_2026-11-15.py`
  (simulatore ora per ora dalle regole; `rifai` prima, poi `indipendente`, `margine`, `sensi`, `misure`, `robustezza_t`, `filtri`, `corretti`,
  `tasso_base`, `limiti_bot`); `f5_conto_vero_2026-11-27.py` (F5 sul conto vero: `--codice`, `--pannello`; `base` e `ore` prima).

## Decisioni aperte per Alessio
- (7 nov) Minimo di anni e di operazioni; perdita giornaliera del 5% da simulare o no. (11 nov) Riesame che rende candidata una
  «costruzione» esclusa; famiglia del funding nelle miscele; minimo di eventi; esame in avanti delle monete gratis scritto prima.
- (12 nov) G1 sul conto vero: soglia (0,95 scritta, 0,80 di oggi), costo dei limiti, tetto per moneta, capitale minimo.
- (12 nov) Prova 96: limite macro di 2 ore; soglia a eventi. Prova 55: «qualche punto sotto»; riserva del 23 ott. Mazzo: prove dopo
  la scoperta (G1 fino alla 57: 0,946; tutte 0,733-0,769), prove senza serie, conferme, serie corte.
- (15 nov) Coperture 157/161: ~3% l'anno dal 2022 vale il rischio di borsa?; t corretto per settimane legate; pronti 0,10%+0,05%,
  mantenimento 0,5%, capitale minimo ~400 USDT; gamba a pronti e trasferimenti nel bot; 161 idea nuova o 157 rifatta.

## Note di metodo
- Mai il `main` delle prove (voce 11); l'auditor non committa (11 nov). Copia troncata: commit con `gh api` (voce 17); mai
  `grep -r research/` né `ls research/data` (negato). Script: `python3 -I audits/repro/<script>.py` dalla radice.
- La sessione principale lavora in parallelo (giro del mattino): file cambiati fuori da `audits/` durante l'audit non sono dell'auditor.
