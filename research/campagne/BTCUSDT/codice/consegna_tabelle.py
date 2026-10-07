"""Costruisce le tabelle della consegna dal log (log.jsonl) e dai risultati salvati.

Stampa in Markdown: (1) varianti testate con metriche di costruzione e confronto con le
baseline; (2) scarti per stima dei trade; (3) verifiche eseguite; (4) riepilogo del budget.
Non calcola nulla di nuovo: riporta.
"""
from __future__ import annotations
import json
from pathlib import Path

QUI = Path(__file__).resolve().parent
LOG = QUI.parent / "log.jsonl"
voci = [json.loads(r) for r in LOG.read_text(encoding="utf-8").splitlines() if r.strip()]

reg = {v["id"]: v for v in voci if v.get("tipo") == "registrazione" and v.get("tipo_test") == "variante"}
ris = {v["id"]: v for v in voci if v.get("tipo") == "risultato" and v.get("id") in reg}
scarti = [v for v in voci if v.get("tipo") == "scarto"]
verifiche = [(v, next((r for r in voci if r.get("tipo") == "risultato" and r.get("id") == v["id"]), None)) for v in voci if v.get("tipo") == "registrazione" and v.get("tipo_test") == "verifica"]

def f(x, nd=2):
    return "—" if x is None else (f"{x:.{nd}f}".replace(".", ","))

print("### Varianti testate (periodo di costruzione, 2020-01-01 → 2022-10-19)\n")
print("| n | Variante | Idea | TF | Dir. | Trade | PF | R medio | R mediano | R medio per anno (2020/2021/2022) | Percentile sul caso | Netta vs caso | Netta vs incondizionata | Previsione PF | PF nell'intervallo | Esito |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for id_, r in sorted(reg.items(), key=lambda kv: kv[1]["variante_n"]):
    m = ris[id_]["metriche"] if id_ in ris else {}
    b = ris[id_].get("baseline_b_casuale") or {} if id_ in ris else {}
    a = ris[id_].get("baseline_a_incondizionata") or {} if id_ in ris else {}
    anni = m.get("r_medio_per_anno", {})
    anni_s = "/".join(f(anni.get(y), 2) for y in ("2020", "2021", "2022"))
    netta_b = (b.get("confronto_con_sim_mediana") or {}).get("netta")
    netta_a = (a.get("confronto") or {}).get("netta")
    segno_a = (a.get("confronto") or {}).get("segno")
    esito = "non va avanti" if not ris[id_].get("criterio_successo_superato") else "CANDIDATO"
    if m.get("n_trade", 0) < 100:
        esito = "sotto 100 trade: non si sa"
    pv = r.get("previsione_pf", [None, None])
    print(f"| {r['variante_n']} | {id_} | {r['idea']} | {r['timeframe']} | {r['direzione']} | {m.get('n_trade','—')} | {f(m.get('profit_factor'))} | {f(m.get('r_medio'),3)} | {f(m.get('r_mediano'),3)} | {anni_s} | {f(b.get('percentile_del_candidato'),0)} | {'sì' if netta_b else 'no'} | {('sì' if netta_a and segno_a == 1 else 'no') if a else '—'} | {f(pv[0])}–{f(pv[1])} | {'sì' if ris[id_].get('previsione_corretta') else 'no'} | {esito} |")

print("\n### Scarti per stima dei trade (nessun budget consumato)\n")
print("| Variante | Idea | TF | Dir. | Segnali grezzi | Trade stimati | Occupazione (barre) |")
print("|---|---|---|---|---|---|---|")
for v in scarti:
    st = v.get("stima_trade", {})
    print(f"| {v['id']} | {v['idea']} | {v['timeframe']} | {v['direzione']} | {st.get('segnali_grezzi')} | {st.get('trade_stimati')} | {st.get('occupazione_barre')} |")

print("\n### Verifiche eseguite (costruzione)\n")
print("| Verifica di | Verifica | TF | Trade | PF | R medio | R mediano | R medio per anno | Senza i 5 migliori | Percentile sul caso | Netta |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
for v, r in verifiche:
    if r is None:
        continue
    m = r["metriche"]; b = r.get("baseline_b_casuale") or {}
    anni = m.get("r_medio_per_anno", {})
    print(f"| {v['verifica_di']} | {v['verifica']} | {v['timeframe']} | {m['n_trade']} | {f(m['profit_factor'])} | {f(m['r_medio'],3)} | {f(m['r_mediano'],3)} | {'/'.join(f(anni.get(y),2) for y in ('2020','2021','2022'))} | {f(r.get('r_medio_senza_5_migliori'),3)} | {f(b.get('percentile_del_candidato'),0)} | {'sì' if b.get('netta') else 'no'} |")

print(f"\nBudget: {len(reg)} varianti registrate su 30; {len(scarti)} scarti per stima; {len([1 for v, r in verifiche if r])} verifiche.")
