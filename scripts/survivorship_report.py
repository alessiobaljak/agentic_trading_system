"""
BIAS DI SOPRAVVIVENZA — quante coin il GATE non ha mai visto morire.

IL PROBLEMA
L'universo del gate nasce da `exchangeInfo`, che restituisce SOLO i contratti
attivi oggi. Una coin quotata nel 2023 e delistata nel 2025 non compare con un
flag "delistata": sparisce e basta. Quindi il gate valida 4.6 anni di storia
guardando esclusivamente i SOPRAVVISSUTI.

PERCHE' CONTA
E' come valutare una scuola intervistando solo i diplomati. Una strategia
"compra il ribasso" testata sui soli sopravvissuti sembra ottima — ogni ribasso
e' rimbalzato, perche' le coin che NON sono rimbalzate sono state rimosse dal
campione. Sulle micro-cap, dove il delisting e' frequente, la stima dell'edge
puo' essere gonfiata in modo sistematico.

Non vogliamo TRADARE le coin morte: vogliamo che il gate le abbia viste morire,
cosi' le sue statistiche includono anche gli esiti peggiori.

LA FONTE
data.binance.vision (repository pubblico di dati storici Binance) conserva gli
archivi anche dei simboli delistati. Il listing S3 delle directory enumera tutti
i simboli che hanno MAI avuto dati; sottraendo quelli attivi si ottengono i
delistati. Le date si ricavano dai nomi dei file mensili.

Uso:
    python -m scripts.survivorship_report
    python -m scripts.survivorship_report --since 2022-01-01 --dates 40
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

import requests

S3 = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
PREFIX = "data/futures/um/monthly/klines/"
NS = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}


def _list_prefixes(prefix: str, timeout: int = 30) -> list[str]:
    """Directory sotto `prefix` (paginate). Sono i simboli con dati storici."""
    out: list[str] = []
    marker = ""
    while True:
        params = {"delimiter": "/", "prefix": prefix}
        if marker:
            params["marker"] = marker
        r = requests.get(S3, params=params, timeout=timeout)
        r.raise_for_status()
        root = ET.fromstring(r.text)
        names = [p.text for p in root.findall(".//s3:CommonPrefixes/s3:Prefix", NS) if p.text]
        out.extend(n[len(prefix):].strip("/") for n in names)
        if (root.findtext("s3:IsTruncated", "false", NS) or "false").lower() != "true":
            break
        marker = names[-1] if names else ""
        if not marker:
            break
    return sorted(set(out))


def _last_month(symbol: str, interval: str, timeout: int = 20) -> tuple[str, str] | None:
    """(primo, ultimo) mese con dati. L'ULTIMO e' la firma del delisting: un
    simbolo vivo produce dati fino al mese corrente, uno rimosso si ferma."""
    try:
        r = requests.get(S3, params={"prefix": f"{PREFIX}{symbol}/{interval}/"},
                         timeout=timeout)
        r.raise_for_status()
    except Exception:  # noqa: BLE001
        return None
    months = sorted(set(re.findall(r"-(\d{4}-\d{2})\.zip", r.text)))
    return (months[0], months[-1]) if months else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--interval", default="15m", help="timeframe usato dal gate")
    ap.add_argument("--since", default="2022-01",
                    help="inizio della finestra di validazione (YYYY-MM)")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--limit", type=int, default=0, help="0 = tutti i simboli")
    args = ap.parse_args()

    print("[surv] elenco dei simboli con dati STORICI su data.binance.vision…")
    try:
        symbols = [s for s in _list_prefixes(PREFIX) if s.endswith("USDT")]
    except Exception as exc:  # noqa: BLE001
        print(f"[surv] listing non riuscito: {exc}")
        return 1
    if args.limit:
        symbols = symbols[: args.limit]
    print(f"[surv] perpetual *USDT mai esistiti: {len(symbols)}")
    print(f"[surv] dato ogni simboli la finestra dei dati (una richiesta ciascuno, "
          f"{args.workers} in parallelo)…\n")

    # il mese corrente e quello prima: un simbolo vivo ha dati almeno fino a li'
    now = datetime.now(timezone.utc)
    cur = f"{now.year:04d}-{now.month:02d}"
    prev_m, prev_y = (now.month - 1, now.year) if now.month > 1 else (12, now.year - 1)
    prev = f"{prev_y:04d}-{prev_m:02d}"

    rows: list[tuple[str, str, str]] = []
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(_last_month, s, args.interval): s for s in symbols}
        for i, f in enumerate(cf.as_completed(futs), 1):
            sym = futs[f]
            rng = f.result()
            if rng:
                rows.append((sym, rng[0], rng[1]))
            if i % 100 == 0:
                print(f"    …{i}/{len(symbols)}")

    live = [r for r in rows if r[2] >= prev]
    dead = [r for r in rows if r[2] < prev]
    # quelli morti che erano VIVI dentro la finestra: sono i veri assenti dal gate
    dead_in_window = [r for r in dead if r[2] >= args.since]
    universe_in_window = [r for r in rows if r[2] >= args.since]

    print(f"\n[surv] datati: {len(rows)}/{len(symbols)}")
    print(f"[surv] ancora VIVI (dati fino a {prev} o {cur}): {len(live)}")
    print(f"[surv] DELISTATI (dati interrotti prima): {len(dead)}")
    print(f"[surv] di cui delistati DOPO {args.since} (dentro la finestra "
          f"del gate): {len(dead_in_window)}")

    denom = max(len(universe_in_window), 1)
    share = len(dead_in_window) / denom
    print(f"\n[surv] QUOTA INVISIBILE AL GATE: {len(dead_in_window)} su {denom} "
          f"simboli attivi nella finestra = {share*100:.1f}%")

    if dead_in_window:
        print("\n[surv] esempi di coin nate e morte dentro la finestra:")
        for sym, a, b in sorted(dead_in_window, key=lambda r: r[2], reverse=True)[:15]:
            print(f"    {sym:20s} {a} → {b}")

    print()
    if share >= 0.20:
        print("[surv] VERDETTO: bias RILEVANTE. La stima dell'edge del registro e'")
        print("       gonfiata — vale la pena caricare gli archivi dei delistati nel")
        print("       backtest (seconda pipeline dati da data.binance.vision).")
    elif share >= 0.08:
        print("[surv] VERDETTO: bias MODERATO. Da documentare come limite noto e da")
        print("       pesare sulle micro-cap piu' giovani.")
    else:
        print("[surv] VERDETTO: bias MARGINALE. Documentarlo e proseguire: costruire")
        print("       la pipeline dei delistati non ripagherebbe il lavoro.")
    print("\n[surv] NB: non vogliamo TRADARE le coin morte — vogliamo che il gate le")
    print("       abbia viste morire, cosi' le sue statistiche includono i peggiori esiti.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
