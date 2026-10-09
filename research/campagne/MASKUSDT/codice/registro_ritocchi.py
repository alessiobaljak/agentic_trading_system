"""Ritocchi (regola 6): stessa idea, timeframe, direzione e meccanismo della variante di partenza."""
import numpy as np

import varianti_idee as v
from registro_idee import F, M


class R1(v.I03S):
    rr = 2.0
    barre_max = 12


class R2(R1):
    """R1 con il filtro del funding: nessun ingresso se l'ultimo funding regolato e' negativo."""

    def prepara_condizione(self, st):
        super().prepara_condizione(st)
        fund = st["per"].funding
        ts_f = np.array([t for t, _ in fund], dtype=np.int64)
        tassi = np.array([r for _, r in fund], dtype=float)
        f = np.full(len(st["c"]), np.nan)
        for i, cand in enumerate(st["candele"]):
            j = int(np.searchsorted(ts_f, cand.close_ts, side="right")) - 1
            if j >= 0:
                f[i] = tassi[j]
        st["f"] = f

    def pronta(self, st, i):
        return super().pronta(st, i) and not np.isnan(st["f"][i])

    def condizione(self, st, i):
        return super().condizione(st, i) and st["f"][i] >= 0


class R3(R1):
    barre_max = 24


class R4(R1):
    k_stop = 1.5


class R5(R2):
    k_stop = 1.5


def _r(idea, famiglia, di, cambia, par, prev, lo, hi):
    return {"idea": idea, "famiglia": famiglia, "ritocco_di": di, "fonte": F[idea], "meccanismo": M[idea],
            "parametri": par, "cosa_cambia": cambia,
            "previsione": f"R medio dopo i costi fra {lo} e {hi}; {prev}", "previsione_r": [lo, hi]}


VARIANTI = {
    "MASKUSDT-028": (R1, _r("I-03", "MASKUSDT-006", "MASKUSDT-006",
                            "target da 1 a 2 volte lo stop, uscita a tempo da 6 a 12 barre (Fase 3, nota MASKUSDT-N006)",
                            {"deviazioni": 3, "finestra_dev": 168, "stop_atr": 2, "target_rapporto": 2, "uscita_barre": 12},
                            "t contro la (b) fra 0,5 e 2, probabilmente non netto", -0.05, 0.20)),
    "MASKUSDT-029": (R2, _r("I-03", "MASKUSDT-006", "MASKUSDT-028",
                            "filtro nato dai fallimenti: nessun ingresso con l'ultimo funding regolato negativo (nota MASKUSDT-N007)",
                            {"deviazioni": 3, "finestra_dev": 168, "stop_atr": 2, "target_rapporto": 2, "uscita_barre": 12,
                             "funding_minimo_ingresso": 0},
                            "t contro la (b) fra 1,5 e 3, puo' essere netto", 0.05, 0.35)),
    "MASKUSDT-030": (R3, _r("I-03", "MASKUSDT-006", "MASKUSDT-028",
                            "uscita a tempo da 12 a 24 barre (nota MASKUSDT-N007)",
                            {"deviazioni": 3, "finestra_dev": 168, "stop_atr": 2, "target_rapporto": 2, "uscita_barre": 24},
                            "t contro la (b) fra 1 e 2,5", 0.0, 0.25)),
    "MASKUSDT-031": (R4, _r("I-03", "MASKUSDT-006", "MASKUSDT-028",
                            "stop da 2 a 1,5 ATR (target a 2 volte lo stop): stop sotto il tetto del 6% del bot nella maggior parte dei trade",
                            {"deviazioni": 3, "finestra_dev": 168, "stop_atr": 1.5, "target_rapporto": 2, "uscita_barre": 12},
                            "t contro la (b) fra 0,5 e 2", -0.05, 0.20)),
    "MASKUSDT-032": (R5, _r("I-03", "MASKUSDT-006", "MASKUSDT-028",
                            "filtro del funding (nota MASKUSDT-N007) e stop da 2 a 1,5 ATR (tetto del 6% del bot)",
                            {"deviazioni": 3, "finestra_dev": 168, "stop_atr": 1.5, "target_rapporto": 2, "uscita_barre": 12,
                             "funding_minimo_ingresso": 0},
                            "t contro la (b) fra 1 e 2,5", 0.0, 0.25)),
}
