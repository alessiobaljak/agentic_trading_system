"""Fase 1, punto 7: conta i trade di UNA variante e scrive subito la voce nel log.

Uso: python research/campagne/ETHUSDT/codice/registra.py <nome in ipotesi.md>

``conta_trade`` si chiama una volta sola, sulle regole esatte di ``idee.VARIANTI``.
Con almeno 70 trade la voce e' una ``registrazione`` (tipo_test variante, prima del
test); sotto, uno ``scarto`` (nessun budget consumato). Il numero va sempre nel log:
nessun conteggio resta fuori. Una variante gia' contata non si riconta.
"""

import inspect
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune  # noqa: E402
import idee  # noqa: E402
import registro  # noqa: E402
import schede  # noqa: E402

BUDGET = 30  # budget_varianti_per_moneta di parametri.yaml


def parametri_completi(V, kw):
    firma = inspect.signature(V.__init__)
    tutti = {k: v.default for k, v in firma.parameters.items()
             if k not in ("self", "serie") and v.default is not inspect.Parameter.empty}
    tutti.update(kw)
    return tutti


def prossimo_id(voci):
    numeri = [int(v["id"].split("-")[1]) for v in voci
              if v["tipo"] in ("registrazione", "scarto") and v["id"].split("-")[1].isdigit()]
    return f"{comune.SIMBOLO}-{(max(numeri) + 1 if numeri else 1):03d}"


def main() -> None:
    nome = sys.argv[1]
    V, kw, tf = idee.VARIANTI[nome]
    scheda = schede.SCHEDE[nome]
    voci = registro.voci()
    if any(v.get("variante_ipotesi") == nome and v["tipo"] in ("registrazione", "scarto") for v in voci):
        raise SystemExit(f"{nome} e' gia' stata contata: non si riconta")
    if registro.prossimo_variante_n() > BUDGET:
        raise SystemExit(f"budget di {BUDGET} varianti esaurito: {nome} non si conta e non si testa")
    conteggio = comune.conta(V, kw, tf)
    ident = prossimo_id(voci)
    voce = {
        "id": ident,
        "variante_ipotesi": nome,
        "idea": scheda["idea"],
        "famiglia": scheda.get("famiglia", ident),
        "ritocco_di": scheda.get("ritocco_di"),
        "fonte": scheda["fonte"],
        "meccanismo": scheda["meccanismo"],
        "timeframe": tf,
        "direzione": kw["direzione"],
        "regole": scheda["regole"],
        "parametri": parametri_completi(V, kw),
        "codice": f"campagne/ETHUSDT/codice/idee.py, {V.__name__}",
        "periodo": "costruzione",
        "previsione": scheda["previsione"]["testo"],
        "previsione_numeri": scheda["previsione"],
        "criterio_successo": schede.CRITERIO,
        "trade_stimati": conteggio["trade"],
        "conteggio": conteggio,
    }
    if "nota" in scheda:
        voce["nota_idea"] = scheda["nota"]
    if "cosa_cambia" in scheda:
        voce["cosa_cambia"] = scheda["cosa_cambia"]
        voce["perche"] = scheda["perche"]
    if conteggio["trade"] >= comune.TRADE_MINIMI_COSTRUZIONE:
        voce.update({"tipo": "registrazione", "tipo_test": "variante", "variante_n": registro.prossimo_variante_n()})
    else:
        voce.update({"tipo": "scarto", "motivo": f"sotto i trade minimi di costruzione ({comune.TRADE_MINIMI_COSTRUZIONE}): "
                                                   f"{conteggio['trade']} trade con conta_trade; non si testa, nessun budget"})
    registro.aggiungi(voce)
    print(ident, nome, voce["tipo"], "trade stimati", conteggio["trade"], "variante_n", voce.get("variante_n"))


if __name__ == "__main__":
    main()
