"""Il giudice delle balene (GIUDICE_BALENE.md, idea 152): prepara il foglio del lunedì con i numeri di ogni conto.

Per ogni conto del gruppo (i conti di `hyperliquid/scelti_*.json` e quelli della mappa delle liquidazioni) e per le 4 settimane finite
il lunedì: guadagno per moneta letto dai nostri giri, parte del mercato (paniere uguale di Bitcoin, Ether e Solana) e parte propria,
costanza (giorni e settimane con parte propria positiva, peso del giorno migliore), dimensione delle scommesse (peso delle posizioni,
leva media e massima: esposizione lorda sul valore del conto) e perdita dal picco; il foglio dice da dove viene il gruppo (conti scelti o
mappa delle liquidazioni) e, se la mappa ha meno di 10 giorni di dati, che il gruppo è fatto solo dei conti scelti.
Propone una voce (costante, mercato, caso) con le soglie della sezione «Cosa giudica»: il giudizio vero lo scrive la sessione nel file
`giudice_balene/giudizi/AAAA-MM-GG.json` e lo committa prima della settimana dopo. Nessun dato di Binance: i prezzi sono valore/quantità
delle nostre letture e i prezzi medi della raccolta delle liquidazioni.

Uso: python3 -m research.trader_copiati.giudice_balene [AAAA-MM-GG del lunedì]   (scrive giudice_balene/AAAA-MM-GG.md e .json)
"""
from __future__ import annotations

import gzip
import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

QUI = Path(__file__).resolve().parent
ARCHIVIO = QUI / "hyperliquid"
USCITA = QUI / "giudice_balene"
PANIERE = ("BTC", "ETH", "SOL")
SALTO_MAX = timedelta(hours=8)          # due giri più lontani di così non fanno un intervallo (giro saltato)
CONTO_MIN, MONETE_MIN, GIRI_MIN, GIORNI_MIN = 100_000, 5, 10, 10


def _ora(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)


def giri(inizio: datetime, fine: datetime, fonti: dict | None = None) -> tuple[dict, dict]:
    """(posizioni, prezzi): posizioni[ora][indirizzo] = (valore del conto, {moneta: (quantità, valore)}); prezzi[ora][moneta].
    Con ``fonti`` (un dizionario) scrive anche da dove viene ogni conto (``fonti["conti"][indirizzo]``: «scelti» per le righe di
    `posizioni_*.jsonl.gz`, «mappa» per quelle di `liquidazioni_*.jsonl.gz`) e le ore dei giri della mappa (``fonti["giri_mappa"]``)."""
    pos: dict = defaultdict(dict)
    prezzi: dict = defaultdict(dict)
    mesi = sorted({(inizio + timedelta(days=d)).strftime("%Y-%m") for d in range((fine - inizio).days + 1)})
    conti_sett: dict = {}
    da_dove: dict = defaultdict(set)
    giri_mappa: set = set()
    for m in mesi:
        f = ARCHIVIO / f"posizioni_{m}.jsonl.gz"
        if f.exists():
            for r in gzip.open(f, "rt", encoding="utf-8"):
                if not r.strip():
                    continue
                x = json.loads(r)
                t = _ora(x["ora"])
                if not (inizio <= t <= fine):
                    continue
                pp = {}
                for p in x.get("posizioni") or []:
                    q, v = float(p["quantita"]), float(p["valore"])
                    if q:
                        pp[p["moneta"]] = (q, v)
                        prezzi[t].setdefault(p["moneta"], abs(v / q))
                pos[t][x["indirizzo"]] = (float(x.get("conto") or 0), pp)
                da_dove[x["indirizzo"]].add("scelti")
        f = ARCHIVIO / f"liquidazioni_{m}.jsonl.gz"
        if f.exists():
            for r in gzip.open(f, "rt", encoding="utf-8"):
                if not r.strip():
                    continue
                x = json.loads(r)
                t = _ora(x["ora"])
                if not (inizio <= t <= fine):
                    continue
                nome = x["conti_della_settimana"]
                if nome not in conti_sett:
                    g = ARCHIVIO / nome
                    conti_sett[nome] = [c["indirizzo"] for c in json.loads(g.read_text())["conti"]] if g.exists() else []
                indirizzi = conti_sett[nome]
                for moneta, p in (x.get("prezzi") or {}).items():
                    prezzi[t][moneta] = float(p)
                per_conto: dict = defaultdict(dict)
                for i, moneta, q, v, *_ in x.get("posizioni") or []:
                    if q:
                        per_conto[i][moneta] = (float(q), float(v))
                valori = x.get("conti") or []
                giri_mappa.add(t)
                for i, ind in enumerate(indirizzi):
                    if i < len(valori) and valori[i] is not None and ind not in pos[t]:
                        pos[t][ind] = (float(valori[i]), per_conto.get(i, {}))
                        da_dove[ind].add("mappa")
    if fonti is not None:
        fonti["conti"] = dict(da_dove)
        fonti["giri_mappa"] = sorted(giri_mappa)
    return pos, prezzi


def numeri(lunedi: datetime, info: dict | None = None) -> list:
    """I numeri per conto. Con ``info`` (un dizionario) scrive anche i giorni (UTC) con giri della mappa delle liquidazioni nella
    finestra (``info["giorni_mappa"]``) e l'ora del primo di quei giri (``info["primo_giro_mappa"]``)."""
    inizio = lunedi - timedelta(days=28)
    fonti: dict = {}
    pos, prezzi = giri(inizio, lunedi, fonti)
    if info is not None:
        gm = [t for t in fonti.get("giri_mappa", []) if t < lunedi]
        info["giorni_mappa"] = len({t.date() for t in gm})
        info["primo_giro_mappa"] = gm[0] if gm else None
    ore = sorted(pos)
    per_conto: dict = defaultdict(list)
    for t in ore:
        for ind, v in pos[t].items():
            per_conto[ind].append((t, *v))
    out = []
    for ind, serie in per_conto.items():
        if len(serie) < 2:
            continue
        tot = mercato = 0.0
        propria_moneta: dict = defaultdict(float)
        propria_giorno: dict = defaultdict(float)
        propria_sett: dict = defaultdict(float)
        toccate, giri_aperti, saltati = set(), 0, 0
        pesi, leve, monete_n, nette = [], [], [], []
        for (t0, c0, p0), (t1, _, _) in zip(serie, serie[1:]):
            if t1 - t0 > SALTO_MAX or not p0:
                continue
            giri_aperti += 1
            pr0, pr1 = prezzi.get(t0, {}), prezzi.get(t1, {})
            rb = [pr1[m] / pr0[m] - 1 for m in PANIERE if m in pr0 and m in pr1 and pr0[m]]
            rp = sum(rb) / len(rb) if rb else None
            netta = sum(q * pr0[m] for m, (q, _) in p0.items() if m in pr0)
            nette.append(netta)
            monete_n.append(len(p0))
            if c0 > 0:
                pesi += [abs(v) / c0 for _, v in p0.values()]
                leve.append(sum(abs(v) for _, v in p0.values()) / c0)     # regola 5: esposizione lorda sul valore del conto
            for m, (q, v) in p0.items():
                toccate.add(m)
                if m not in pr0 or m not in pr1 or not pr0[m] or rp is None:
                    saltati += 1
                    continue
                r = pr1[m] / pr0[m] - 1
                g, gp = q * pr0[m] * r, q * pr0[m] * (r - rp)
                tot += g
                propria_moneta[m] += gp
                propria_giorno[t0.date()] += gp
                propria_sett[(t0 - timedelta(days=t0.weekday())).date()] += gp
            if rp is not None:
                mercato += netta * rp
        valori = [c for _, c, _ in serie if c > 0]
        if not valori:
            continue
        picco, discesa = valori[0], 0.0
        for v in valori:
            picco = max(picco, v)
            discesa = min(discesa, v / picco - 1)
        propria = tot - mercato
        giorni = len(propria_giorno)
        migliore = max(propria_giorno.values(), default=0.0)
        d = {"indirizzo": ind, "conto_medio": sum(valori) / len(valori), "giri_aperti": giri_aperti, "giorni": giorni,
             "intervalli_saltati": saltati, "totale": tot, "mercato": mercato, "propria": propria,
             "quota_propria": propria / tot if tot > 0 else None,
             "giorni_propria_positiva": sum(1 for x in propria_giorno.values() if x > 0),
             "settimane": len(propria_sett), "settimane_propria_positiva": sum(1 for x in propria_sett.values() if x > 0),
             "giorno_migliore_su_propria": migliore / propria if propria > 0 else None,
             "monete_toccate": len(toccate), "monete_propria_positiva": sum(1 for x in propria_moneta.values() if x > 0),
             "peso_medio_posizione": sum(pesi) / len(pesi) if pesi else None, "peso_massimo_posizione": max(pesi) if pesi else None,
             "leva_media": sum(leve) / len(leve) if leve else None, "leva_massima": max(leve) if leve else None,
             "monete_aperte_medie": sum(monete_n) / len(monete_n) if monete_n else 0,
             "netta_media_su_conto": (sum(nette) / len(nette)) / (sum(valori) / len(valori)) if nette else 0,
             "discesa_massima": discesa,
             "fonte": " e ".join(sorted(fonti["conti"].get(ind, set()), key=["scelti", "mappa"].index)) or "—"}
        d["fuori"] = (d["conto_medio"] < CONTO_MIN or d["monete_toccate"] < MONETE_MIN or giri_aperti < GIRI_MIN or giorni < GIORNI_MIN)
        d["voce_proposta"] = None if d["fuori"] else proposta(d)
        out.append(d)
    return sorted(out, key=lambda d: -(d["propria"] / d["conto_medio"] if d["conto_medio"] else 0))


def proposta(d: dict) -> str:
    """Le soglie della regola 6 (una guida: il giudizio vero lo scrive la sessione)."""
    gg = d["giorni_propria_positiva"] / d["giorni"] if d["giorni"] else 0
    ss = d["settimane_propria_positiva"] / d["settimane"] if d["settimane"] else 0
    if (d["propria"] > 0 and gg >= 4 / 7 and ss >= 0.75 and (d["giorno_migliore_su_propria"] or 1) < 0.5
            and (d["quota_propria"] or 0) >= 0.4 and d["monete_propria_positiva"] >= 3):
        return "costante"
    if d["totale"] > 0 and d["mercato"] >= 0.8 * d["totale"]:
        return "mercato"
    return "caso"


def main(lunedi: datetime | None = None) -> Path:
    if lunedi is None:
        oggi = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        lunedi = oggi - timedelta(days=oggi.weekday())
    info: dict = {}
    dd = numeri(lunedi, info)
    dentro = [d for d in dd if not d["fuori"]]
    USCITA.mkdir(exist_ok=True)
    js = USCITA / f"{lunedi:%Y-%m-%d}.json"
    js.write_text(json.dumps(dd, indent=0, default=str))
    conta = {v: sum(1 for d in dentro if d["voce_proposta"] == v) for v in ("costante", "mercato", "caso")}
    pc = lambda x: "—" if x is None else f"{x * 100:+.1f}%"
    da_scelti = sum(1 for d in dentro if "scelti" in d["fonte"])
    gruppo = (f"**Il gruppo**: giudicabili {da_scelti} dai conti scelti (`scelti_*.json`, con le balene) e {len(dentro) - da_scelti} "
              f"dalla sola mappa delle liquidazioni.")
    if info.get("giorni_mappa", 0) < GIORNI_MIN:          # nota del 27 novembre 2026 (audit del 26 novembre, raccolta-6)
        primo = info.get("primo_giro_mappa")
        gruppo += (f" **Il gruppo è fatto solo dei conti scelti**: la mappa delle liquidazioni ha {info.get('giorni_mappa', 0)} giorni di "
                   f"dati nella finestra{f' (dal {primo:%Y-%m-%d %H:%M} UTC)' if primo else ''}, meno dei {GIORNI_MIN} richiesti, e i suoi "
                   f"conti non si giudicano ancora (regola 1 e finestra della sezione «Cosa giudica»).")
    righe = [f"# Il giudice delle balene — lunedì {lunedi:%Y-%m-%d}", "",
             f"Finestra: dal {lunedi - timedelta(days=28):%Y-%m-%d} al {lunedi:%Y-%m-%d}. Conti letti {len(dd)}, giudicabili {len(dentro)} "
             f"(fuori: sotto 100.000 dollari, meno di 5 monete, meno di 10 giri o 10 giorni). Voci proposte dalle soglie: "
             f"costante {conta['costante']}, mercato {conta['mercato']}, caso {conta['caso']}. Regole: `GIUDICE_BALENE.md`; numeri interi in "
             f"`{js.name}`. Il giudizio vero va in `giudizi/{lunedi:%Y-%m-%d}.json`, committato prima della settimana dopo, nel formato "
             f"della nota del 27 novembre di `GIUDICE_BALENE.md` (`lunedi`, `scritto_il` in UTC, e in `giudizi` un elemento per conto "
             f"giudicabile con `indirizzo` intero, `voce` e `motivo`): lo legge la misura delle regole 10-11.", "",
             gruppo, "",
             "Dimensione delle scommesse (regola 5): **leva** = esposizione lorda (somma dei valori delle posizioni aperte) diviso il valore "
             "del conto, giro per giro, media e massimo; **peso** = valore di una posizione sul valore del conto, medio e massimo. Per i conti "
             "della mappa le posizioni sotto i 10.000 dollari non sono salvate (`LIQUIDAZIONI.md`, punto 2): leva e pesi vi sono un poco "
             "più bassi del vero.", "",
             "| conto | fonte | valore medio | totale | mercato | propria | giorni propria + | settimane + | giorno migliore | "
             "monete + / toccate | monete aperte | peso medio / massimo | leva media / massima | netta | discesa | voce proposta |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    due = lambda x: "—" if x is None else f"{x:.2f}"
    pp = lambda x: "—" if x is None else f"{x * 100:.0f}%"
    for d in dentro:
        c = d["conto_medio"]
        righe.append(f"| {d['indirizzo'][:10]}… | {d['fonte']} | {c / 1e6:.2f} M | {pc(d['totale'] / c)} | {pc(d['mercato'] / c)} | "
                     f"{pc(d['propria'] / c)} | {d['giorni_propria_positiva']}/{d['giorni']} | "
                     f"{d['settimane_propria_positiva']}/{d['settimane']} | {pc(d['giorno_migliore_su_propria'])} | "
                     f"{d['monete_propria_positiva']}/{d['monete_toccate']} | {d['monete_aperte_medie']:.1f} | "
                     f"{pp(d['peso_medio_posizione'])} / {pp(d['peso_massimo_posizione'])} | "
                     f"{due(d['leva_media'])} / {due(d['leva_massima'])} | "
                     f"{d['netta_media_su_conto']:+.2f} | {d['discesa_massima'] * 100:.1f}% | {d['voce_proposta']} |")
    md = USCITA / f"{lunedi:%Y-%m-%d}.md"
    md.write_text("\n".join(righe) + "\n", encoding="utf-8")
    print(f"{md.name}: {len(dd)} conti, {len(dentro)} giudicabili, proposte {conta}")
    return md


if __name__ == "__main__":
    main(datetime.strptime(sys.argv[1], "%Y-%m-%d").replace(tzinfo=timezone.utc) if len(sys.argv) > 1 else None)
