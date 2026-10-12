"""Conta o testa una variante sui dati di costruzione.

Uso:
  python research/campagne/MATICUSDT/codice/prova.py conta V01
  python research/campagne/MATICUSDT/codice/prova.py test V01

``conta``: una sola chiamata a ``conta_trade`` (sezione 8) sulle regole della variante; il numero
va nella registrazione. ``test``: la valutazione completa (Fase 2), scritta in
``campagne/MATICUSDT/esiti/<ID>.json``; il risultato nel log lo aggiunge ``chiudi.py``.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import quadro  # noqa: E402
import varianti  # noqa: E402

ESITI = Path(__file__).resolve().parents[1] / "esiti"
ESITI.mkdir(exist_ok=True)

modo, vid = sys.argv[1], sys.argv[2]
fabbrica = getattr(varianti, vid)
tf = varianti.TIMEFRAME[vid]
if modo == "conta":
    file = ESITI / f"{vid}_conta.json"
    if file.exists():
        raise SystemExit(f"{vid}: gia' contata una volta ({file.name}): non si riconta")
    c = quadro.conta(fabbrica, tf)
    file.write_text(json.dumps({"variante": vid, "timeframe": tf, **c}))
    print(json.dumps(c))
elif modo == "test":
    r = quadro.valuta(fabbrica, tf)
    testo = json.dumps(quadro.per_log(r), ensure_ascii=False)
    (ESITI / f"{vid}.json").write_text(testo)
    print(testo)
else:
    raise SystemExit("modo: conta o test")
