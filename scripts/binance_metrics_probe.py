"""
QUANTO STORICO DI OPEN INTEREST ABBIAMO DAVVERO, E QUANTO PESA.

Backlog B6. Il bot legge open interest e long/short DAL VIVO, ma l'endpoint REST
ne tiene 30 giorni: per questo il GATE 1, che valida su 4,6 anni, non li ha mai
visti. Gli stessi numeri esistono come file scaricabili dal 2020.

PRIMA DI COSTRUIRE QUALSIASI COSA, tre numeri che oggi non abbiamo:

  1. quante delle coppie validate hanno davvero dati dal 2022-01-01
     (sospetto forte che molte no: sono coin quotate nel 2024-2025);
  2. quanto pesa lo storico sul disco della VPS;
  3. i file si leggono davvero, con le trappole note dentro il codice?

Questo script risponde e BASTA. Non scrive su Firebase, non tocca il registro,
non aggiunge feature al gate: decidere se costruirci sopra viene DOPO aver
guardato questi numeri, non prima. Il paper sta correndo verso i 40 trade e
cambiare l'esperimento mentre misura lo butterebbe via.

Il grosso del lavoro non scarica niente: il listing S3 riporta gia' la
dimensione di ogni file, quindi bastano ~4 richieste per coppia invece di
millesettecento. Solo il campione (`--campione`) scarica davvero, per provare
il lettore su file veri.

Uso:
    .venv/bin/python -m scripts.binance_metrics_probe
    .venv/bin/python -m scripts.binance_metrics_probe --symbols BTCUSDT,VETUSDT
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
from datetime import date, datetime, timedelta, timezone

import requests

from backtesting.metrics_loader import (
    apri_zip, buchi, elenco_giorni, leggi_csv, scarica_giorno,
)

MIB = 1024 * 1024


def coppie_validate() -> list[str]:
    """Le coin del registro validato. Su questa macchina Firebase non c'e': in
    quel caso lo si dice e si usa `--symbols`, invece di inventare un elenco."""
    from bot.core.firebase_client import decode_pairs, get_firebase

    fb = get_firebase()
    pairs = decode_pairs((fb.get_doc("strategy_registry", "validated") or {}).get("pairs"))
    simboli = set()
    for chiave, rec in pairs.items():
        sym = (rec or {}).get("symbol") if isinstance(rec, dict) else None
        simboli.add(sym or chiave.split("|", 1)[0])
    return sorted(s for s in simboli if s)


def _riga(sym: str, mappa: dict[date, int], dal: date, al: date) -> dict:
    presenti = set(mappa)
    dentro = {g: b for g, b in mappa.items() if dal <= g <= al}
    return {
        "symbol": sym,
        "primo": min(presenti) if presenti else None,
        "ultimo": max(presenti) if presenti else None,
        "giorni_finestra": len(dentro),
        "byte_finestra": sum(dentro.values()),
        "byte_totali": sum(mappa.values()),
        "buchi": buchi(presenti, max(dal, min(presenti)), al) if presenti else [],
    }


def main() -> int:
    # IERI, non oggi: il file di un giorno viene pubblicato il giorno dopo.
    # Chiudere la finestra a oggi faceva comparire 24 coppie su 25 «con giorni
    # mancanti» — un allarme inventato dalla data di fine, non dai dati.
    ieri = datetime.now(timezone.utc).date() - timedelta(days=1)
    ap = argparse.ArgumentParser()
    ap.add_argument("--dal", default="2022-01-01",
                    help="inizio della finestra usata dal gate")
    ap.add_argument("--al", default=ieri.isoformat(),
                    help="fine della finestra; default IERI, perche' il file di "
                         "oggi non e' ancora pubblicato")
    ap.add_argument("--symbols", default="",
                    help="elenco separato da virgole; vuoto = registro validato")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--campione", type=int, default=2,
                    help="giorni da scaricare DAVVERO per coppia, per provare il "
                         "lettore (0 = nessun download)")
    args = ap.parse_args()

    dal, al = date.fromisoformat(args.dal), date.fromisoformat(args.al)

    if args.symbols:
        simboli = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    else:
        try:
            simboli = coppie_validate()
        except Exception as exc:  # noqa: BLE001
            print(f"[metrics] registro non leggibile ({type(exc).__name__}: "
                  f"{str(exc)[:80]}).\n           Rilancia con --symbols "
                  f"SYM1,SYM2 oppure dalla VPS.")
            return 1
    if not simboli:
        print("[metrics] nessuna coppia da misurare.")
        return 1

    print("=" * 72)
    print(f"STORICO «metrics» DI BINANCE VISION · {len(simboli)} coppie · "
          f"finestra {dal} → {al}")
    print("=" * 72)
    print("[metrics] leggo il listing S3 (nessun download: le dimensioni sono "
          "gia' li')…\n")

    sess = requests.Session()
    righe: list[dict] = []
    errori: list[tuple[str, str]] = []
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(elenco_giorni, s, 30, sess): s for s in simboli}
        for f in cf.as_completed(futs):
            sym = futs[f]
            try:
                righe.append(_riga(sym, f.result(), dal, al))
            except Exception as exc:  # noqa: BLE001
                errori.append((sym, f"{type(exc).__name__}: {str(exc)[:60]}"))

    righe.sort(key=lambda r: (r["primo"] or date.max))
    attesi = (al - dal).days + 1

    print(f"{'coppia':<16}{'primo dato':<13}{'ultimo':<13}{'gg dal ' + str(dal):>14}"
          f"{'copertura':>11}{'MiB':>8}")
    print("-" * 72)
    for r in righe:
        if not r["primo"]:
            print(f"{r['symbol']:<16}{'— nessun dato —':<37}")
            continue
        cop = r["giorni_finestra"] / attesi
        print(f"{r['symbol']:<16}{str(r['primo']):<13}{str(r['ultimo']):<13}"
              f"{r['giorni_finestra']:>14}{cop*100:>10.0f}%"
              f"{r['byte_finestra']/MIB:>8.1f}")

    dal_2022 = [r for r in righe if r["primo"] and r["primo"] <= dal]
    con_dati = [r for r in righe if r["primo"]]
    tot_mib = sum(r["byte_finestra"] for r in righe) / MIB
    con_buchi = [r for r in righe if r["buchi"]]

    print("-" * 72)
    print(f"\n[metrics] coppie con dati dall'inizio della finestra ({dal}): "
          f"{len(dal_2022)} su {len(simboli)}")
    print(f"[metrics] coppie con dati (anche piu' recenti): {len(con_dati)}")
    print(f"[metrics] PESO SUL DISCO, compresso, tutta la finestra: "
          f"{tot_mib:.1f} MiB")
    if con_dati:
        gg = sum(r["giorni_finestra"] for r in con_dati)
        print(f"[metrics] {gg} file giornalieri in tutto "
              f"(~{tot_mib*1024/max(gg,1):.0f} KiB l'uno)")
    if con_buchi:
        print(f"[metrics] coppie con giorni MANCANTI dentro il loro storico: "
              f"{len(con_buchi)}")
        for r in sorted(con_buchi, key=lambda r: -len(r["buchi"]))[:5]:
            esempi = ", ".join(str(g) for g in r["buchi"][:3])
            print(f"     {r['symbol']:<14} {len(r['buchi'])} buchi (es. {esempi})")
    if errori:
        print(f"[metrics] listing NON riuscito per {len(errori)} coppie:")
        for sym, e in errori[:5]:
            print(f"     {sym}: {e}")

    # ------------------------------------------------------------------ #
    # Il campione: i file si leggono davvero?                            #
    # ------------------------------------------------------------------ #
    if args.campione and con_dati:
        print(f"\n[metrics] provo il lettore su {args.campione} giorni per "
              f"coppia (download vero, con checksum)…")
        righe_lette = compressi = scompattati = 0
        falliti: list[str] = []
        for r in con_dati:
            for g in (r["ultimo"], r["primo"])[: args.campione]:
                try:
                    dati = scarica_giorno(r["symbol"], g, sessione=sess)
                    if dati is None:
                        continue
                    testo = apri_zip(dati)
                    parsate = leggi_csv(testo)
                    compressi += len(dati)
                    scompattati += len(testo.encode())
                    righe_lette += len(parsate)
                    ordinate = all(parsate[i]["ts"] <= parsate[i + 1]["ts"]
                                   for i in range(len(parsate) - 1))
                    if not ordinate:
                        falliti.append(f"{r['symbol']} {g}: righe non ordinate")
                except Exception as exc:  # noqa: BLE001
                    falliti.append(f"{r['symbol']} {g}: {type(exc).__name__}: "
                                   f"{str(exc)[:50]}")
        print(f"[metrics] righe lette: {righe_lette} · compresso "
              f"{compressi/MIB:.2f} MiB → csv {scompattati/MIB:.2f} MiB "
              f"(×{scompattati/max(compressi,1):.1f})")
        if righe_lette:
            print(f"[metrics] proiezione dello SCOMPATTATO su tutta la finestra: "
                  f"~{tot_mib*scompattati/max(compressi,1):.0f} MiB")
        if falliti:
            print(f"[metrics] LETTURA FALLITA su {len(falliti)} file:")
            for m in falliti[:5]:
                print(f"     {m}")
        else:
            print("[metrics] nessun file illeggibile nel campione.")

    print("\n" + "=" * 72)
    print("Questo comando MISURA e basta: non scrive niente e non cambia il gate.")
    print("Serve a decidere se vale la pena costruirci una feature — decisione")
    print("che resta aperta finche' il paper non chiude i 40 trade.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
