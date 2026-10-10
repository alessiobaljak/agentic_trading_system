"""Diagnosi del coordinamento: il controllo positivo degli strumenti con le uscite della prova a placebo di gruppo."""
import json, sys, time
sys.path.insert(0, "/home/user/agentic_trading_system")
from research.src import gruppo

S = "/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad"
MOD = "/home/user/coordinamento/research/taratura/placebo_gruppo/placebo_gruppo.py"

def main():
    car = gruppo.CaricatoreDisco(radice=f"{S}/placebo_gruppo_lavoro/radice")
    out = {}
    for tf, regola in (("4h", "rsi"), ("4h", "incrocio_medie"), ("1h", "rsi")):
        t0 = time.time()
        r = gruppo.controllo_positivo(MOD, {"regola": regola, "direzione": "long"}, tf, "long", id=f"cp-{tf}-{regola}",
                                      processi=2, cartella_campagna=f"{S}/cp/lavoro_{tf}_{regola}", caricatore=car)
        s = r["esami"]["senza_ritardo"]
        out[f"{tf}-{regola}"] = {"passa": r["passa"], "condizioni": r["condizioni"], "t_senza": r["t_senza_ritardo"],
                                 "t_con": r["t_con_ritardo"], "trade": s.get("n_trade") or s.get("metriche", {}).get("n_trade"),
                                 "t_a": s["baseline_a"].get("t"), "t_b": s["baseline_b"].get("t"),
                                 "soglia_b": s["baseline_b"].get("soglia"), "effetto_grappolo": s.get("effetto_grappolo"),
                                 "secondi": round(time.time() - t0)}
        print(json.dumps(out[f"{tf}-{regola}"]), flush=True)
    json.dump(out, open(f"{S}/cp/esito.json", "w"), indent=1)

if __name__ == "__main__":
    main()
