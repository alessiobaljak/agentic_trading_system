# Skill di terze parti per la ricerca (aggiunte il 25 ottobre 2026)

Servono al revisore separato del metodo (`research/REGISTRO.md`, sezione 1): si usano DOPO che una prova è stata
calcolata con le regole scritte prima, mai per scegliere i parametri. Codice letto riga per riga prima di copiarlo:
solo libreria standard di Python, niente rete, niente chiavi. Licenze MIT nei singoli `LICENSE`.

| Skill | Origine | A cosa serve qui |
|---|---|---|
| `backtest-expert` | tradermonty/claude-trading-skills | metodo per mettere alla prova un'idea; `scripts/evaluate_backtest.py` dà un punteggio su campione, attesa, rischio, robustezza, realismo (88 test) |
| `residual-edge-analyzer` | tradermonty/claude-trading-skills | scompone i rendimenti giornalieri di una strategia in esposizione al mercato (o ad altri fattori dichiarati) e residuo, con errori standard robusti; ingresso CSV in `references/input-contract.md` (26 test) |
| `backtest-review` | shakeebshaan/claude-code-quant-skills | lista di controllo: sguardo al futuro, sopravvivenza, troppi parametri, costi, regimi, esecuzione |
| `strategy-critique` | shakeebshaan/claude-code-quant-skills | critica avversaria: chi sta dall'altra parte, cosa la uccide, rischi nascosti |
| `risk-report` | shakeebshaan/claude-code-quant-skills | riassunto del rischio di una serie di rendimenti (Sharpe, Sortino, discesa, code, stabilità) |
| `data-scrub` | shakeebshaan/claude-code-quant-skills | controllo di una tabella di candele prima di usarla (buchi, doppioni, barre ferme, universo nel tempo) |

Le parti delle stesse raccolte legate ad azioni, a Finviz o alla loro pipeline di file YAML non si copiano.
`blave-quant` (manda ordini veri agli exchange) non si installa mai.
