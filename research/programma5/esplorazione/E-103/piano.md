# E-103 — Sessioni, fine settimana e prezzo medio, sul periodo recente C2 (fase 2)

Piano scritto e committato il 18 ottobre 2026 **prima del calcolo** (REGOLE.md, sezioni 6bis e 7). Periodo C2; 24 monete
della fase 2; barre di un'ora; programma `strumenti/esplora_calendario.py`.

## Perché

Dal 2024 il mercato delle cripto ha un ritmo nuovo: i fondi quotati in borsa negli Stati Uniti comprano e vendono solo
nelle ore di borsa americane e mai nel fine settimana. Chi muove il prezzo nel fine settimana o di notte è un'altra
platea, con meno liquidità: i movimenti fatti fuori dagli orari dei grandi possono tornare indietro quando i grandi
rientrano, e quelli fatti nelle ore dei grandi possono continuare. Queste famiglie non c'erano in E-001 (che aveva solo
l'ora del giorno e il giorno della settimana, da soli).

## Le famiglie (σ, z, ingresso e uscita come E-001; «segue» = verso del movimento)

| Famiglia | Decisione e segnale | h | Valori |
|---|---|---|---|
| W1 fine settimana | lunedì 00:00 UTC: z del rendimento da venerdì 24:00 a domenica 24:00 (48 ore), \|z\| ≥ k | 24, 72 | k 1, 1,5, 2 |
| W2 sessioni | alla fine di una sessione (Asia 00-08, Europa 08-14, America 14-21, sera 21-24 UTC), z del rendimento della sessione, \|z\| ≥ k; si tiene per tutta la sessione dopo | 6, 7, 3, 8 | k 1, 2 |
| W3 giornata | alle 20:00 UTC, z del rendimento dalle 00:00 (20 ore), \|z\| ≥ k; si tiene fino alle 24:00. Alle 15:00, z della prima ora americana (14-15), \|z\| ≥ k; si tiene fino alle 21:00 | 4 / 6 | k 1, 2 |
| W4 prezzo medio | alla chiusura dell'ora, scarto fra il prezzo e il prezzo medio delle 24 ore pesato sul volume (chiusure orarie), diviso σ·√24, \|·\| ≥ k | 4, 24 | k 1,5, 2,5 |
| W5 fine mese | long dalle 00:00 dell'ultimo giorno del mese per 96 ore; per confronto, long dalle 00:00 del giorno 15 per 96 ore | 96 | — |

Celle: W1 12, W2 16, W3 8, W4 8, W5 2 = **46** (92 con i due versi).

## Criteri di promozione

Gli stessi di E-101 (lordo, caso, segno in ogni semestre, 70% di almeno 10 monete, |t| ≥ 3, almeno 100 trade); al massimo
3 idee J.
