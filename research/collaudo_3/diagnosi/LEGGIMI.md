# Diagnosi del primo giro della prova A (16 ottobre 2026)

Non sono prove ufficiali del collaudo: servono a trovare la causa per cui la prova A non e' passata. Girano
sulle stesse 100 varianti finte della prova ufficiale (`../esiti/giro1/prova_a.jsonl`). Si lanciano dalla radice del
repository, per esempio `python3 research/collaudo_3/diagnosi/diag_a.py senza_costi`.

| Script | Cosa cambia rispetto alla prova ufficiale | p-value sotto 0,10 (su 100) | sotto 0,023 |
|---|---|---|---|
| (prova ufficiale) | — | 21 | 7 |
| `diag_a.py senza_tendenza` | serie senza la tendenza di fondo | 21 | — |
| `diag_a.py senza_costi` | commissioni e slippage a zero | 15 | — |
| `diag_a.py entrambi` | senza tendenza e senza costi | 17 | — |
| `diag_strato.py 5` | entrate casuali con la stessa larghezza di stop del candidato (5 fasce) | 17 | 4 |
| `diag_segni.py` | serie con la direzione di ogni candela girata a caso (la volatilita' resta al suo posto) | 22 | 6 |
| `diag_segni.py strato` | tutte e due le cose | **12** | 4 |

`diagnosi_a.py` scompone l'R di ogni variante e delle sue entrate casuali (lordo, costi, funding, larghezza
dello stop, durata); `avanti.py` misura i rendimenti dopo i segnali sulle serie rimescolate (nessuna
differenza sistematica: niente informazione dal passato al futuro).
