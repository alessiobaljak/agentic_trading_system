"""Validazione (dopo la Fase 5): il candidato congelato gira UNA volta sul periodo di validazione.

Serie dall'inizio della costruzione alla fine del 2023 (indicatori caldi); contano solo i trade
entrati dopo la fine della costruzione; la (b) entra solo nelle barre di validazione. Asticella:
Benjamini-Hochberg al 10% su m candidati (qui m = 1), p-value da contro_baseline contro la (b) di
validazione. Esito provvisorio: lo conferma il coordinamento.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import quadro  # noqa: E402
import registro  # noqa: E402
from campagna import _scrivi_esito  # noqa: E402
from registro_ritocchi import R2  # noqa: E402
from research.src import statistica  # noqa: E402

CAND = "MASKUSDT-029"
VID = "MASKUSDT-029-VALIDAZIONE"


def main():
    if any(v.get("id") == VID for v in registro.voci()):
        raise SystemExit("validazione gia' fatta: non si rifa'")
    registro.aggiungi({
        "id": VID, "tipo": "registrazione", "tipo_test": "verifica", "verifica_di": CAND, "verifica": "validazione",
        "periodo": "validazione (2023-04-11 → 2023-12-31; serie dal 2021-08-01, trade entrati dopo la costruzione)",
        "trade_stimati": round(86 * 30 / 70),
        "nota_stima": "stima proporzionale: 86 trade di costruzione x 30/70 = 36,9; conta_trade non si usa sulla validazione",
        "previsione": "R medio fra -0,10 e +0,25; circa 30-40 trade; con 30-40 trade il p-value sotto 0,10 richiede un R medio di circa +0,2: piu' probabile che non passi",
        "criterio_successo": "almeno 30 trade di validazione e p-value contro la (b) di validazione <= 0,10 (Benjamini-Hochberg con m = 1)",
        "candidati_m": [CAND]})
    per = quadro.periodo_validazione("1h")
    e = quadro.valuta(R2(), per)
    _scrivi_esito(VID, e)
    m = e["metriche"]
    b = e.get("baseline_b", {})
    p = float(b.get("p_value", 1.0)) if b.get("valutabile") else 1.0
    sotto = m["trade"] < 30
    if sotto:
        p = 1.0
    passa = statistica.benjamini_hochberg([p], 0.10)[0]
    voce = {"id": VID, "tipo": "risultato", "metriche": {k: m[k] for k in [
        "profit_factor", "trade", "r_medio", "r_medio_per_anno", "trade_per_anno", "r_medio_senza_3_migliori",
        "drawdown_max", "rendimento_totale", "rendimento_per_anno", "win_rate", "esiti", "n_ridotti",
        "n_violazioni_liquidazione", "funding_totale", "stop_pct_mediana", "stop_oltre_6pct"]},
        "blocco": e.get("blocco"), "baseline_a": e.get("baseline_a"), "baseline_b": b,
        "percentile_caso": e.get("percentile_caso"), "buy_and_hold_per_anno": e.get("buy_and_hold_per_anno"),
        "sotto_trade_minimi_validazione": sotto, "p_value_asticella": p, "m": 1,
        "asticella_benjamini_hochberg_10": bool(passa), "esito_provvisorio": True}
    registro.aggiungi(voce)
    print(json.dumps(registro._pulisci({"trade": m["trade"], "r_medio": m["r_medio"], "pf": m["profit_factor"],
                                        "t_b": b.get("t"), "p": p, "passa": passa, "t_a": e.get("baseline_a", {}).get("t"),
                                        "media_b": b.get("media"), "r_senza3": m["r_medio_senza_3_migliori"]})))


if __name__ == "__main__":
    main()
