"""
Sonda a basso livello sul WebSocket: isola la causa di "connesso ma nessun dato".

Non usa PriceStream: apre le connessioni con un client minimale, così separa i
problemi di AMBIENTE/RETE da quelli del nostro codice.

I tre test che discriminano:
  1. PING/PONG — sono frame di CONTROLLO. Se tornano, la connessione e' pienamente
     funzionante e il silenzio e' una scelta del server (restrizione geografica /
     account). Se NON tornano, e' la rete che non inoltra i frame.
  2. SERVER DI CONTROLLO (echo pubblico) — se anche lui e' muto, il problema riguarda
     TUTTO il traffico WebSocket in uscita, non Binance.
  3. BINANCE SPOT vs FUTURES — host diversi: distingue un filtro su un host specifico.

Uso (sul VPS):
    .venv/bin/python -m scripts.diagnose_ws
    .venv/bin/python -m scripts.diagnose_ws --symbol ETHUSDT --seconds 8
"""
from __future__ import annotations

import argparse
import asyncio
import os
import socket
import sys

from bot.config import settings

FUTURES = ("wss://stream.binancefuture.com" if settings.BINANCE_TESTNET
           else "wss://fstream.binance.com")
SPOT = "wss://stream.binance.com:9443"
ECHO = "wss://echo.websocket.events"

PROXY_VARS = ("HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy",
              "ALL_PROXY", "all_proxy", "WS_PROXY", "ws_proxy", "NO_PROXY", "no_proxy")


def _dns(host: str) -> str:
    try:
        infos = socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)
    except Exception as exc:  # noqa: BLE001
        return f"risoluzione fallita: {exc}"
    v4 = sorted({i[4][0] for i in infos if i[0] == socket.AF_INET})
    v6 = sorted({i[4][0] for i in infos if i[0] == socket.AF_INET6})
    return f"IPv4={v4 or '-'} IPv6={v6 or '-'}"


def environment() -> None:
    print("=== AMBIENTE ===")
    print(f"python      : {sys.version.split()[0]}")
    try:
        import websockets
        print(f"websockets  : {getattr(websockets, '__version__', '?')}")
    except Exception as exc:  # noqa: BLE001
        print(f"websockets  : NON importabile ({exc})")
    print(f"testnet     : {settings.BINANCE_TESTNET}")
    found = {k: os.environ[k] for k in PROXY_VARS if os.environ.get(k)}
    print(f"proxy env   : {found or 'nessuna'}")
    for host in ("fapi.binance.com", FUTURES.split("//")[1].split(":")[0],
                 "stream.binance.com"):
        print(f"dns {host:24s}: {_dns(host)}")
    print()


async def probe(label: str, url: str, seconds: float) -> dict:
    """Apre l'URL, prova il ping/pong e conta i frame di dati entro `seconds`."""
    import websockets

    out = {"label": label, "connected": False, "frames": 0, "first": None,
           "ping": None, "peer": None, "error": None}
    try:
        async with websockets.connect(url, ping_interval=None, close_timeout=5) as ws:
            out["connected"] = True
            try:
                out["peer"] = str(getattr(ws, "remote_address", None))
            except Exception:  # noqa: BLE001
                pass
            # 1) PING/PONG: il test che separa "rete rotta" da "server muto"
            try:
                pong = await ws.ping()
                await asyncio.wait_for(pong, timeout=5.0)
                out["ping"] = True
            except Exception as exc:  # noqa: BLE001
                out["ping"] = False
                out["error"] = f"ping fallito: {type(exc).__name__}: {exc}"
            # 2) frame di dati
            loop = asyncio.get_running_loop()
            deadline = loop.time() + seconds
            while loop.time() < deadline:
                try:
                    raw = await asyncio.wait_for(ws.recv(),
                                                 timeout=max(0.1, deadline - loop.time()))
                except asyncio.TimeoutError:
                    break
                except Exception as exc:  # noqa: BLE001
                    out["error"] = f"recv: {type(exc).__name__}: {exc}"
                    break
                out["frames"] += 1
                if out["first"] is None:
                    out["first"] = raw if isinstance(raw, str) else raw.decode("utf-8", "replace")
    except Exception as exc:  # noqa: BLE001
        out["error"] = f"{type(exc).__name__}: {exc}"
    return out


def render(r: dict) -> None:
    if not r["connected"]:
        print(f"[{r['label']}] ❌ non connesso — {r['error']}")
        return
    ping = {True: "pong OK", False: "pong ASSENTE", None: "non testato"}[r["ping"]]
    print(f"[{r['label']}] connesso · {ping} · {r['frames']} frame di dati"
          f"{' ✅' if r['frames'] else ' (muto)'}")
    if r["peer"]:
        print(f"    peer : {r['peer']}")
    if r["first"]:
        print(f"    primo: {r['first'][:180]}")
    if r["error"] and r["frames"]:
        print(f"    nota : {r['error']}")
    elif r["error"]:
        print(f"    err  : {r['error']}")


async def run(symbol: str, seconds: float) -> int:
    s = symbol.lower()
    print(f"=== SONDE ({seconds:.0f}s ciascuna) ===")
    results = []
    for label, url in [
        ("futures combined", f"{FUTURES}/stream?streams={s}@aggTrade"),
        ("futures raw     ", f"{FUTURES}/ws/{s}@aggTrade"),
        ("spot raw        ", f"{SPOT}/ws/{s.lower()}@aggTrade"),
        ("echo (controllo)", ECHO),
    ]:
        r = await probe(label, url, seconds)
        render(r)
        results.append(r)
        print()

    by = {r["label"].strip(): r for r in results}
    binance = [r for r in results if "futures" in r["label"] or "spot" in r["label"]]
    echo = by.get("echo (controllo)")
    got_data = [r for r in binance if r["frames"] > 0]
    pinged = [r for r in binance if r["ping"] is True]

    print("=== DIAGNOSI ===")
    if got_data:
        print("Almeno una variante Binance riceve dati: "
              + ", ".join(r["label"].strip() for r in got_data))
        print("-> allineare il bot a quella variante.")
        return 0

    connected = [r for r in binance if r["connected"]]
    if not connected:
        print("Nessuna variante Binance si connette nemmeno: qui l'handshake viene")
        print("RIFIUTATO (vedi errori sopra), non e' il caso 'connesso ma muto'.")
        print("-> rete/firewall bloccano il WebSocket; il bot usa le candele REST.")
        return 1

    if echo is not None and echo["connected"] and echo["frames"] == 0 and echo["ping"] is not True:
        print("Nemmeno il server di CONTROLLO risponde: il problema riguarda TUTTO il")
        print("traffico WebSocket in uscita da questa macchina (firewall/appliance che")
        print("completa l'handshake e poi non inoltra i frame). Non e' Binance.")
        print("-> parlarne col provider, oppure restare sulle candele REST.")
        return 1

    if pinged:
        print("I PING tornano (pong OK) ma NESSUN dato arriva: la connessione e' sana,")
        print("quindi e' il SERVER che scientemente non invia nulla — tipico delle")
        print("restrizioni geografiche/di provider di Binance sugli stream.")
        print("-> la via praticabile e' un IP non filtrato (altra region) oppure")
        print("   restare sulle candele REST, che dallo stesso IP funzionano.")
        return 1

    print("Handshake ok ma né dati né pong: i frame non attraversano la rete.")
    print("Sospetti: middlebox/firewall che intercetta il 443, MTU blackhole.")
    print("-> il bot continua a funzionare con le candele 1m via REST.")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default="BTCUSDT")
    ap.add_argument("--seconds", type=float, default=6.0)
    args = ap.parse_args()
    environment()
    return asyncio.run(run(args.symbol.upper(), args.seconds))


if __name__ == "__main__":
    raise SystemExit(main())
