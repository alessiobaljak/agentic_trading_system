"""Tabella di tutte le varianti del log (registrazioni, scarti e risultati di costruzione).

Uso: python research/campagne/ETHUSDT/codice/tabella.py [md]
Con ``md`` stampa una tabella markdown (per lezioni_moneta.md e consegna.md).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import registro  # noqa: E402


def f(x, n=3):
    if isinstance(x, (int, float)) and not isinstance(x, bool):
        return f"{x:+.{n}f}".replace(".", ",")
    return str(x)


def main() -> None:
    md = len(sys.argv) > 1 and sys.argv[1] == "md"
    voci = registro.voci()
    ris = {v["id"]: v for v in voci if v["tipo"] == "risultato" and v.get("metriche")}
    righe = []
    for v in voci:
        if v["tipo"] == "scarto":
            righe.append([v["id"], v.get("variante_ipotesi"), v["timeframe"], v["direzione"], str(v["trade_stimati"]),
                          "scarto", "", "", "", "", "", ""])
        elif v["tipo"] == "registrazione" and v.get("tipo_test") == "variante":
            r = ris.get(v["id"])
            if r is None:
                righe.append([v["id"], v.get("variante_ipotesi"), v["timeframe"], v["direzione"], str(v["trade_stimati"]),
                              "in attesa", "", "", "", "", "", ""])
                continue
            m, a, b = r["metriche"], r["baseline_a"], r["baseline_b"]
            righe.append([v["id"], v.get("variante_ipotesi"), v["timeframe"], v["direzione"], str(m["trade"]),
                          f(m["r_medio"]), f(m["r_medio_senza_3_migliori"]), f(a["t"], 2), f(b["media"]), f(b["t"], 2),
                          "si'" if r.get("candidato") else "no", "si'" if r.get("previsione_corretta") else "no"])
    testa = ["id", "variante", "tf", "direzione", "trade", "R medio", "R senza 3 migliori", "t contro (a)",
             "R medio (b)", "t contro (b)", "candidato", "previsione giusta"]
    if md:
        print("| " + " | ".join(testa) + " |")
        print("|" + "---|" * len(testa))
        for r in righe:
            print("| " + " | ".join(r) + " |")
    else:
        for r in righe:
            print("  ".join(r))


if __name__ == "__main__":
    main()
