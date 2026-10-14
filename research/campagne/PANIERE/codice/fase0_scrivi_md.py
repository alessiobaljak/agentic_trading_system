"""Scrive fase0_dati.md dalle uscite di fase0_dati.py, fase0_periodi.py e scarico.py (nessun calcolo nuovo)."""

import json
from pathlib import Path

CARTELLA = Path(__file__).resolve().parents[1]
LAVORO = CARTELLA / "lavoro"


def milioni(x):
    return f"{x / 1e6:,.0f}".replace(",", ".")


def main():
    d = json.loads((LAVORO / "fase0_dati.json").read_text(encoding="utf-8"))
    s = json.loads((LAVORO / "scarico_esito.json").read_text(encoding="utf-8"))
    p = json.loads((LAVORO / "fase0_periodi.json").read_text(encoding="utf-8"))
    monete = [m for m in d if m != "BTCUSDT"]
    righe = []
    a = righe.append
    a("# Fase 0 — i dati del paniere")
    a("")
    a("Scritto da `codice/fase0_scrivi_md.py` con i numeri di `codice/fase0_dati.py` (`lavoro/fase0_dati.json`), "
      "`codice/scarico.py` (`lavoro/scarico_esito.json`) e `codice/fase0_periodi.py` (`lavoro/fase0_periodi.json`). "
      "Solo funzioni di `research/src/dati.py`; solo candele giornaliere di last e mark e funding, dal primo mese della "
      "scheda al 2023-12-31 (BTCUSDT dal 2020-01).")
    a("")
    a("## Scarico e impronte")
    a("")
    a(f"* File scaricati e presenti: {s['ok']} su {s['compiti']} mesi chiesti; mesi assenti alla fonte (404): "
      f"{len(s['buchi'])}; errori dopo 3 tentativi: {len(s['errori'])}; file accettati senza CHECKSUM remoto: "
      f"{len(s.get('checksum_mancanti', []))}.")
    a(f"* Confronto con `impronte_1d.json` (`dati.verifica_impronte`), sulle serie 1d e funding: simboli con "
      f"differenze o file mancanti: {s['simboli_con_differenze'] or 'nessuno'}; file su disco non registrati: "
      f"{s['simboli_con_file_in_piu'] or 'nessuno'}. Le impronte valgono quelle di `impronte_1d.json` (regole.md, "
      "sezione 2): non si riscrivono.")
    for simbolo, v in s["registrati_non_scaricati"].items():
        a(f"* Registrati in `impronte_1d.json` e NON scaricati: {simbolo}, {v['n']} file a 8 ore (da `{v['primo']}` a "
          f"`{v['ultimo']}`): le regole del paniere (sezione 2) vietano ogni timeframe diverso da 1d. Domanda "
          "all'utente nel log (PANIERE-006).")
    a(f"* Mesi assenti alla fonte: {', '.join(s['buchi'])}. Sono tutti mesi di funding: il motore non addebita "
      "funding in quei mesi (regole del gruppo, sezione 2, punto 9).")
    a("")
    a("## Periodi (lavoro/fase0_periodi.json, voce PANIERE-005 del log)")
    a("")
    a(f"Costruzione fino al {p['fine_costruzione']} compreso, validazione dal {p['inizio_validazione']} al "
      f"{p['fine_validazione']} ({p['giorni_validazione']} giorni). Giorni-moneta {p['giorni_moneta']}, obiettivo "
      f"{p['giorni_moneta_obiettivo']}, di costruzione {p['giorni_moneta_costruzione']}.")
    a("")
    a("## Storia, buchi, allineamento")
    a("")
    storia_ko = [m for m in d if not d[m]["storia_ok"]]
    a(f"* Controllo della storia (regole del gruppo, sezione 2, punto 9: prima barra in entrambe le serie prima del "
      f"2022-01-01): {'80 su 80 superano' if not storia_ko else 'NON superano: ' + ', '.join(storia_ko)}.")
    tardive = [(m, d[m]["inizio_scheda"], d[m]["prima_barra_allineata"]) for m in monete
               if d[m]["prima_barra_allineata"] != d[m]["inizio_scheda"]]
    a(f"* Monete con la prima barra vera dopo il primo giorno della scheda: {len(tardive)} su 80 (la prima candela "
      "giornaliera può essere parziale, `lezioni/metodo.md`):")
    for m, i, b in tardive:
        a(f"  * {m}: scheda {i}, prima barra allineata {b}")
    tot_tl = sum(d[m]["n_tolte_last"] for m in d)
    tot_tm = sum(d[m]["n_tolte_mark"] for m in d)
    a(f"* Barre tolte dall'allineamento (presenti nel last e non nel mark): {tot_tl} in tutto; presenti nel mark e "
      f"non nel last: {tot_tm}. Dettaglio per moneta nella tabella e, con le date, in `lavoro/fase0_dati.json`.")
    giorni_tolti = {}
    for m in d:
        for g in d[m]["tolte_last"]:
            giorni_tolti.setdefault(g, []).append(m)
    comuni = sorted(((g, len(v)) for g, v in giorni_tolti.items() if len(v) >= 5), key=lambda x: x[0])
    a(f"* Giorni tolti su 5 monete o più (lo stesso giorno senza mark su molte monete): "
      f"{', '.join(f'{g} ({n})' for g, n in comuni) or 'nessuno'}.")
    a("")
    a("## Tabella per moneta")
    a("")
    a("Colonne: mesi attesi; mesi mancanti di last, mark e funding; barre allineate; barre tolte (solo last / solo "
      "mark; fra parentesi quelle in validazione); giorni mancanti nel last fra la prima e l'ultima barra; intervalli "
      "del funding (ore, da quando); volume medio giornaliero in milioni di USDT per anno; mesi sotto i 20 milioni "
      "(costruzione / validazione); slippage per lato della scheda.")
    a("")
    a("| Moneta | Mesi | Manc. last/mark/funding | Barre | Tolte last/mark (val.) | Giorni manc. last | Funding | "
      "Volume per anno (M USDT) | Mesi sotto soglia c/v | Slippage |")
    a("|---|---|---|---|---|---|---|---|---|---|")
    for m in d:
        x = d[m]
        manc = "/".join(str(len(x[f"mesi_{k}"]["mancanti"])) for k in ("last", "mark", "funding"))
        fund = "; ".join(f"{o:g}h dal {g}" for g, o in x["funding_intervalli"])
        vol = ", ".join(f"{anno}: {milioni(v)}" for anno, v in x["volume_medio_usdt_per_anno"].items())
        slip = f"{x['slippage_per_lato'] * 100:.2f}%" if "slippage_per_lato" in x else "—"
        a(f"| {m} | {x['mesi_last']['attesi']} | {manc} | {x['barre_allineate']} | {x['n_tolte_last']}/"
          f"{x['n_tolte_mark']} ({x['tolte_last_in_validazione']}) | {len(x['giorni_mancanti_last'])} | {fund} | "
          f"{vol} | {x['mesi_sotto_liquidita_costruzione']}/{x['mesi_sotto_liquidita_validazione']} | {slip} |")
    a("")
    a("## Mesi sotto la liquidità minima (20 milioni di USDT al giorno, `dati.mesi_sotto_liquidita`)")
    a("")
    a("Su questi mesi le varianti non aprono posizioni (il filtro lo applica `gruppo.py`); le stesse barre sono "
      "vietate alla (b) e alle sfasate.")
    a("")
    tot_c = sum(d[m]["mesi_sotto_liquidita_costruzione"] for m in monete)
    tot_v = sum(d[m]["mesi_sotto_liquidita_validazione"] for m in monete)
    tot = sum(d[m]["mesi_totali"] for m in monete)
    a(f"Sulle 80 monete: {tot_c} mesi-moneta sotto soglia fino a gennaio 2023 e {tot_v} nel 2023, su {tot} "
      "mesi-moneta.")
    a("")
    for m in monete:
        if d[m]["mesi_sotto_liquidita"]:
            a(f"* {m}: {', '.join(d[m]['mesi_sotto_liquidita'])}")
    (CARTELLA / "fase0_dati.md").write_text("\n".join(righe) + "\n", encoding="utf-8")
    print("tardive", len(tardive), "storia ko", storia_ko, "tolte", tot_tl, tot_tm, "sotto c/v", tot_c, tot_v, tot)
    print("comuni", comuni)
    print("fatto")


if __name__ == "__main__":
    main()
