"""Scrive campagne/GRUPPO/fase0_dati.md dai file di lavoro della Fase 0 (fase0_dati.json, scarico_*.json) e dalle impronte.

Uso: python3 -u fase0_md.py
Solo impaginazione: i numeri vengono da fase0_dati.py (research/src/dati.py) e dallo scarico.
"""
import hashlib
import json

from comune import CARTELLA_GRUPPO

LAVORO = CARTELLA_GRUPPO / "lavoro"


def elenco(xs, massimo=12):
    if not xs:
        return "—"
    testo = ", ".join(xs[:massimo])
    return testo + (f" (+{len(xs) - massimo})" if len(xs) > massimo else "")


def main():
    f0 = json.loads((LAVORO / "fase0_dati.json").read_text())
    scarichi = sorted(LAVORO.glob("scarico_*.json"))
    righe = ["# Campagna di gruppo — Fase 0, i dati", "",
             "Scritto da `codice/fase0_md.py` dai risultati di `codice/fase0_dati.py` e `codice/scarico.py` (tutti i "
             "numeri vengono da `research/src/dati.py`). Periodi: nota del log GRUPPO-006 (taglio comune "
             "2023-01-16). Regole: regole.md, sezione 2.", ""]
    righe += ["## Impronte dei file scaricati", "",
              "Le impronte SHA-256 di ogni file stanno in `impronte/` (`{simbolo: {file: impronta}}`); qui l'impronta "
              "di ogni file di impronte. Le impronte di BTCUSDT stanno in file a parte (`BTCUSDT_klines_<tf>.json`), "
              "perché i file `klines_<tf>.json` delle 80 monete si scrivono una sola volta quando quel timeframe si "
              "scarica per le monete, e non vanno riscritti.", ""]
    for p in sorted((CARTELLA_GRUPPO / "impronte").glob("*.json")):
        dati_imp = json.loads(p.read_text())
        n = sum(len(v) for v in dati_imp.values())
        righe.append(f"* `impronte/{p.name}`: {len(dati_imp)} simboli, {n} file, SHA-256 "
                     f"`{hashlib.sha256(p.read_bytes()).hexdigest()}`")
    righe += ["", "## Scarichi", ""]
    for p in scarichi:
        s = json.loads(p.read_text())
        righe.append(f"* `{p.name}` (modo {' '.join(s['modo'])}): {s['file']} mesi chiesti, errori {len(s['errori'])}, "
                     f"file accettati senza CHECKSUM remoto {len(s['checksum_mancanti'])}.")
    btc = f0["btc"]
    righe += ["", "## BTCUSDT (riferimento di mercato e dato dei segnali), dal 2020-01-01 al 2023-12-31", "",
              "| Timeframe | Barre | Attese | Mancanti | Salti fra barre consecutive |", "|---|---|---|---|---|"]
    for tf, v in btc.items():
        righe.append(f"| {tf} | {v['barre']} | {v['attese']} | {v['mancanti']} | {v['buchi']} |")
    monete = f0["monete"]
    righe += ["", "## Riassunto", "",
              f"* Monete: {len(monete)}. Storia (primo giorno in comune fra last e mark 1d prima del 2022-01-01): "
              f"superata da {sum(1 for v in monete.values() if v['storia_ok'])} su {len(monete)}.",
              f"* Monete con almeno un mese sotto la liquidità minima: "
              f"{sum(1 for v in monete.values() if v['mesi_sotto_liquidita'])}; mesi sotto la soglia in tutto: "
              f"{sum(len(v['mesi_sotto_liquidita']) for v in monete.values())}.",
              "* Salto giornaliero massimo (rapporto fra due chiusure consecutive, indizio di un cambio di contratto): "
              "in tabella; nessun cambio di contratto si cerca altrove (sezione 2, punto 9).", ""]
    righe += ["## Tabella per moneta", "",
              "Mesi: presenti/attesi dal primo mese della scheda al 2023-12. Giorni mancanti: nelle serie 1d dal primo "
              "giorno presente al 2023-12-31. Tolte: barre dall'allineamento di last e mark (`carica_serie_allineate`), "
              "per timeframe, «solo last / solo mark». Volume: media giornaliera in milioni di USDT per anno (colonna "
              "quote_volume dei file 1d del last).", "",
              "| Moneta | Primo mese | Mesi last / mark / funding | Giorni mancanti last / mark | Tolte (tf: last/mark) "
              "| Funding: regolamenti, intervalli | Volume per anno | Mesi sotto la liquidità | Salto massimo | Storia |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    for s, v in monete.items():
        mesi = " · ".join(f"{v[k]['presenti']}/{v[k]['attesi']}" for k in ("mesi_last_1d", "mesi_mark_1d", "mesi_funding"))
        manc = f"{v['last_1d'].get('giorni_mancanti', '—')} / {v['mark_1d'].get('giorni_mancanti', '—')}"
        tolte = "; ".join(f"{tf}: {a['tolte_last']}/{a['tolte_mark']}" for tf, a in v["allineamento"].items())
        fund = f"{v['funding']['regolamenti']}, " + ", ".join(f"{d}: {int(o)}h" for d, o in v["funding"]["intervalli_ore"])
        vol = ", ".join(f"{a}: {x}" for a, x in v["volume_medio_per_anno_musdt"].items())
        salto = f"{v['salto_giornaliero_massimo']['rapporto']} ({v['salto_giornaliero_massimo']['giorno']})"
        righe.append(f"| {s} | {v['primo_mese']} | {mesi} | {manc} | {tolte} | {fund} | {vol} | "
                     f"{elenco(v['mesi_sotto_liquidita'])} | {salto} | {'sì' if v['storia_ok'] else 'NO'} |")
    righe += ["", "## Buchi (intervalli di giorni mancanti, mesi mancanti)", ""]
    for s, v in monete.items():
        parti = []
        for nome in ("last_1d", "mark_1d"):
            inter = v[nome].get("intervalli_mancanti") or []
            if inter:
                parti.append(f"{nome}: {elenco(inter, 20)}")
        for nome in ("mesi_last_1d", "mesi_mark_1d", "mesi_funding"):
            if v[nome]["mancanti"]:
                parti.append(f"{nome} mancanti: {elenco(v[nome]['mancanti'], 20)}")
        for tf, a in v["allineamento"].items():
            if a["intervalli_tolte_last"] or a["intervalli_tolte_mark"]:
                parti.append(f"tolte {tf}: solo last {elenco(a['intervalli_tolte_last'], 10)}; solo mark "
                             f"{elenco(a['intervalli_tolte_mark'], 10)}")
        if parti:
            righe.append(f"* **{s}**: " + "; ".join(parti))
    (CARTELLA_GRUPPO / "fase0_dati.md").write_text("\n".join(righe) + "\n")
    print("scritto fase0_dati.md")


if __name__ == "__main__":
    main()
