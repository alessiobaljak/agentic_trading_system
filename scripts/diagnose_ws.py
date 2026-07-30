"""
Sonda a basso livello sul WebSocket Binance: isola la causa di "connesso ma muto".

Non usa PriceStream: apre le connessioni con un client minimale, così separa i
problemi di AMBIENTE (versione libreria, proxy, endpoint) da quelli del nostro codice.

Prova piu' varianti di URL e per ognuna dice quanti frame arrivano:
  * /stream?streams=<s>   -> combined stream (quello che usa il bot)
  * /ws/<s>               -> raw stream singolo
  * markPrice@1s          -> tipo di stream diverso (esclude problemi su aggTrade)

Uso (sul VPS):
    .venv/bin/python -m scripts.diagnose_ws
    .venv/bin/python -m scripts.diagnose_ws --symbol ETHUSDT --seconds 8
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys

from bot.config import settings

BASE = ("wss://stream.binancefuture.com" if settings.BINANCE_TESTNET
        else "wss://fstream.binance.com")

PROXY_VARS = ("HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy",
              "ALL_PROXY", "all_proxy", "WS_PROXY", "ws_proxy", "NO_PROXY", "no_proxy")


def environment() -> None:
    print("=== AMBIENTE ===")
    print(f"python      : {sys.version.split()[0]}")
    try:
        import websockets
        ver = getattr(websockets, "__version__", "?")
        print(f"websockets  : {ver}")
        # da websockets 15 il client legge da solo le variabili proxy: se una e'
        # impostata, l'handshake puo' riuscire verso il proxy senza che i frame passino
        if ver and ver.split(".")[0].isdigit() and int(ver.split(".")[0]) >= 15:
            print("              (>=15: supporto proxy ATTIVO per default)")
    except Exception as exc:  # noqa: BLE001
        print(f"websockets  : NON importabile ({exc})")
    print(f"testnet     : {settings.BINANCE_TESTNET}")
    print(f"base        : {BASE}")
    found = {k: os.environ[k] for k in PROXY_VARS if os.environ.get(k)}
    print(f"proxy env   : {found or 'nessuna'}")
    print()


async def probe(url: str, seconds: float, use_proxy_none: bool = False) -> tuple[int, str | None]:
    """Apre l'URL e conta i frame ricevuti entro `seconds`. Ritorna (n_frame, primo_frame)."""
    import websockets

    kwargs = {"ping_interval": 20, "close_timeout": 5}
    if use_proxy_none:
        kwargs["proxy"] = None        # ignora le variabili d'ambiente (websockets >= 15)
    n, first = 0, None
    try:
        async with websockets.connect(url, **kwargs) as ws:
            deadline = asyncio.get_running_loop().time() + seconds
            while asyncio.get_running_loop().time() < deadline:
                try:
                    remaining = deadline - asyncio.get_running_loop().time()
                    raw = await asyncio.wait_for(ws.recv(), timeout=max(0.1, remaining))
                except asyncio.TimeoutError:
                    break
                n += 1
                if first is None:
                    first = raw if isinstance(raw, str) else raw.decode("utf-8", "replace")
    except TypeError as exc:
        # la versione installata non conosce il parametro proxy: implica che NON legge
        # le variabili d'ambiente proxy (supporto aggiunto in websockets 15) -> quella
        # ipotesi si puo' escludere.
        return -1, (f"variante non applicabile: questa versione di websockets non "
                    f"supporta proxy=None, quindi NON usa le variabili proxy "
                    f"d'ambiente ({exc})")
    except Exception as exc:  # noqa: BLE001
        return -1, f"{type(exc).__name__}: {exc}"
    return n, first


async def run(symbol: str, seconds: float) -> int:
    s = symbol.lower()
    variants = [
        (f"combined  /stream?streams={s}@aggTrade", f"{BASE}/stream?streams={s}@aggTrade", False),
        (f"raw       /ws/{s}@aggTrade", f"{BASE}/ws/{s}@aggTrade", False),
        (f"markPrice /ws/{s}@markPrice@1s", f"{BASE}/ws/{s}@markPrice@1s", False),
        (f"combined SENZA proxy env", f"{BASE}/stream?streams={s}@aggTrade", True),
    ]
    print(f"=== SONDE ({seconds:.0f}s ciascuna, {symbol}) ===")
    results = []
    for label, url, no_proxy in variants:
        n, first = await probe(url, seconds, use_proxy_none=no_proxy)
        if n < 0:
            print(f"[{label}] ERRORE: {first}")
        elif n == 0:
            print(f"[{label}] connesso ma 0 frame")
        else:
            print(f"[{label}] {n} frame ✅")
            print(f"    primo: {(first or '')[:200]}")
        results.append((label, n))
        print()

    ok = [lbl for lbl, n in results if n > 0]
    print("=== ESITO ===")
    if not ok:
        print("Nessuna variante riceve frame: il problema e' di AMBIENTE/RETE, non del")
        print("formato URL. Sospetti: proxy trasparente che completa l'handshake senza")
        print("inoltrare i dati, oppure filtro in uscita sul traffico WebSocket.")
        print("Il bot continua a funzionare con le candele 1m via REST.")
        return 1
    print(f"Varianti funzionanti: {', '.join(ok)}")
    print("-> il bot va allineato alla variante che funziona.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default="BTCUSDT")
    ap.add_argument("--seconds", type=float, default=6.0)
    args = ap.parse_args()
    environment()
    return asyncio.run(run(args.symbol.upper(), args.seconds))


if __name__ == "__main__":
    raise SystemExit(main())
