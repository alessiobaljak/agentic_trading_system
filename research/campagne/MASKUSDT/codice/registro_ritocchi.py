"""Ritocchi (regola 6): stessa idea, timeframe, direzione e meccanismo della variante di partenza."""
import varianti_idee as v
from registro_idee import F, M


class R1(v.I03S):
    rr = 2.0
    barre_max = 12


def _r(idea, famiglia, di, cambia, par, prev, lo, hi):
    return {"idea": idea, "famiglia": famiglia, "ritocco_di": di, "fonte": F[idea], "meccanismo": M[idea],
            "parametri": par, "cosa_cambia": cambia,
            "previsione": f"R medio dopo i costi fra {lo} e {hi}; {prev}", "previsione_r": [lo, hi]}


VARIANTI = {
    "MASKUSDT-028": (R1, _r("I-03", "MASKUSDT-006", "MASKUSDT-006",
                            "target da 1 a 2 volte lo stop, uscita a tempo da 6 a 12 barre (Fase 3, nota MASKUSDT-N006)",
                            {"deviazioni": 3, "finestra_dev": 168, "stop_atr": 2, "target_rapporto": 2, "uscita_barre": 12},
                            "t contro la (b) fra 0,5 e 2, probabilmente non netto", -0.05, 0.20)),
}
