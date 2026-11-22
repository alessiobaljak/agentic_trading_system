"""Prova 167 (CENTOCINQUESIMA.md), passo 1: elenco degli eventi con il solo Snapshot e i NOMI dei file dell'archivio (nessun prezzo).
Scarica proposte e spazi (cache in research/data/centocinquesima/, non in git), applica i filtri delle regole e della sezione
«Chiusura della verifica», scrive l'elenco in risultati_centocinquesima/. Non carica nessun prezzo e non calcola nessun rendimento.

Uso: python3 -m research.programma7.centocinquesima_dati
"""
from __future__ import annotations

import json
import re
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

QUI = Path(__file__).parent
RIS = QUI / "risultati_centocinquesima"
CACHE = QUI.parent / "data" / "centocinquesima"
NOMI = QUI.parent / "notizie" / "nomi_2026-11.json"
SNAP = "https://hub.snapshot.org/graphql"
S3 = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
PAROLE_Q = ["buyback", "buy back", "buy-back", "repurchase", "burn", "fee switch", "fee share", "revenue share", "revenue sharing"]
RE_PAROLE = re.compile(r"\b(buyback|buy back|buy-back|repurchase|burn|fee switch|fee share|revenue share|revenue sharing)\b", re.I)
RE_ESCLUSE = re.compile(r"\b(pause|stop|end|halt|cancel|reduce|suspend|remove|terminate|deprecate)\b", re.I)
RE_SI = re.compile(r"^(yes|for|approve|accept|in favor)", re.I)
STABLE = {"USDT", "USDC", "DAI", "BUSD", "FDUSD", "TUSD", "USDE", "FRAX", "LUSD"}
SEMPRE_FUORI = STABLE | {"BTC", "ETH", "BNB", "SOL", "MATIC", "POL", "AVAX", "ARB", "OP", "FTM"}
T_DA = int(datetime(2021, 1, 1, tzinfo=timezone.utc).timestamp())
T_A = int(datetime(2026, 11, 1, tzinfo=timezone.utc).timestamp())   # fine <= 31 ottobre 2026 23:59:59
MESI_TENUTA = {"A": 5, "B": 10}


def _post(q: str) -> dict:
    for tent in range(5):
        try:
            r = urllib.request.Request(SNAP, data=json.dumps({"query": q}).encode(), headers={"content-type": "application/json", "user-agent": "ricerca-client/1.0"})
            with urllib.request.urlopen(r, timeout=90) as f:
                j = json.loads(f.read())
            if "errors" in j:
                raise RuntimeError(str(j["errors"])[:200])
            return j["data"]
        except Exception:  # noqa: BLE001
            time.sleep(3 * (tent + 1))
    raise RuntimeError("Snapshot non risponde")


def proposte() -> list[dict]:
    f = CACHE / "proposte.json"
    if f.exists():
        return json.loads(f.read_text())
    tutte: dict[str, dict] = {}
    for p in PAROLE_Q:
        s = 0
        while True:
            q = ('{proposals(first:1000,skip:%d,where:{title_contains:"%s",state:"closed"},orderBy:"created",orderDirection:asc)'
                 '{id title start end state choices scores scores_total space{id}}}') % (s, p)
            righe = _post(q)["proposals"]
            for r in righe:
                tutte[r["id"]] = r
            if len(righe) < 1000:
                break
            s += 1000
    out = list(tutte.values())
    CACHE.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(out))
    return out


def spazi(ids: list[str]) -> dict[str, dict]:
    f = CACHE / "spazi.json"
    if f.exists():
        return json.loads(f.read_text())
    out: dict[str, dict] = {}
    for i in range(0, len(ids), 50):
        blocco = json.dumps(ids[i:i + 50])
        q = '{spaces(first:100,where:{id_in:%s}){id name symbol network verified flagged}}' % blocco
        for r in _post(q)["spaces"]:
            out[r["id"]] = r
        time.sleep(0.3)
    f.write_text(json.dumps(out))
    return out


def elenco_cartelle(prefisso: str) -> list[str]:
    nomi, marker = [], ""
    while True:
        url = f"{S3}?delimiter=/&prefix={prefisso}" + (f"&marker={marker}" if marker else "")
        for tent in range(6):
            try:
                with urllib.request.urlopen(url, timeout=90) as f:
                    root = ET.fromstring(f.read())
                break
            except Exception:  # noqa: BLE001
                if tent == 5:
                    raise
                time.sleep(2 * (tent + 1))
        ns = {"s": "http://s3.amazonaws.com/doc/2006-03-01/"}
        pref = [e.text for e in root.findall("s:CommonPrefixes/s:Prefix", ns)]
        chiavi = [e.text for e in root.findall("s:Contents/s:Key", ns)]
        nomi += pref + chiavi
        if root.findtext("s:IsTruncated", namespaces=ns) != "true":
            return nomi
        marker = (pref + chiavi)[-1] if (pref + chiavi) else ""


def perpetui() -> dict[str, str]:
    """base -> simbolo del perpetuo in USDT (con piu' storia se ce ne sono due con la stessa base). Solo nomi di cartelle."""
    f = CACHE / "perp_elenco.json"
    if f.exists():
        return json.loads(f.read_text())
    simboli = [x.rstrip("/").split("/")[-1] for x in elenco_cartelle("data/futures/um/monthly/klines/")]
    simboli = [s for s in simboli if s.endswith("USDT") and "_" not in s and s.isascii()]
    primo = {s: mesi_di(s)[0] for s in simboli}
    base: dict[str, str] = {}
    for s in simboli:
        b = re.sub(r"^(1000000|100000|10000|1000|1M)", "", s[:-4])
        if b not in base or primo[s] < primo[base[b]]:
            base[b] = s
    f.write_text(json.dumps(base))
    return base


def mesi_di(sim: str) -> list[str]:
    f = CACHE / f"mesi_{sim}.json"
    if f.exists():
        return json.loads(f.read_text())
    ks = elenco_cartelle(f"data/futures/um/monthly/klines/{sim}/1d/")
    m = sorted(re.search(r"-(\d{4}-\d{2})\.zip$", k).group(1) for k in ks if k.endswith(".zip"))
    CACHE.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(m))
    return m


def costruisci() -> dict:
    nomi = json.loads(NOMI.read_text())["elenco"]
    per_sigla = {v["sigla"].upper(): v["nome"] for v in nomi.values()}
    prop = proposte()
    sp = spazi(sorted({p["space"]["id"] for p in prop}))
    base = perpetui()
    rapp = {"proposte_grezze": len(prop), "spazi_grezzi": len(sp)}
    # spazi: entrano / escono, con il motivo
    spazi_log = []
    ok_sp: dict[str, str] = {}
    for sid, s in sorted(sp.items()):
        sim = (s.get("symbol") or "").upper()
        nome = (s.get("name") or "")
        nm = per_sigla.get(sim)
        motivo = None
        if sim not in base:
            motivo = "sigla senza perpetuo nell'archivio"
        elif not s.get("verified"):
            motivo = "non verificato"
        elif s.get("flagged"):
            motivo = "segnalato"
        else:
            c_sigla = sim.lower() in nome.lower()
            c_nome = bool(nm) and nm.lower() in nome.lower()
            if sim in SEMPRE_FUORI and not c_nome:
                motivo = "sigla sempre fuori (stablecoin o grande moneta) e nome della moneta assente"
            elif not (c_sigla or c_nome):
                motivo = "il nome dello spazio non contiene sigla ne' nome della moneta"
        if motivo is None:
            ok_sp[sid] = base[sim]
        spazi_log.append({"spazio": sid, "nome": nome, "sigla": sim, "verificato": bool(s.get("verified")), "segnalato": bool(s.get("flagged")),
                          "perpetuo": base.get(sim), "esito": "ENTRA" if motivo is None else "ESCE", "motivo": motivo or ""})
    # solo gli spazi con perpetuo e con almeno una proposta del filtro: il log completo e' lungo, si tiene
    # filtri sulle proposte
    cont = {"parole_intere": 0, "fine_nel_periodo": 0, "spazio_ufficiale": 0, "parole_escluse": 0, "approvata": 0, "perpetuo_nel_mese": 0}
    ev = []
    scarti = []
    for p in prop:
        t = p["title"] or ""
        if not RE_PAROLE.search(t):
            continue
        cont["parole_intere"] += 1
        if not (T_DA <= p["end"] < T_A):
            continue
        cont["fine_nel_periodo"] += 1
        sid = p["space"]["id"]
        if sid not in ok_sp:
            continue
        cont["spazio_ufficiale"] += 1
        if RE_ESCLUSE.search(t):
            scarti.append((p["id"], sid, t, "parola esclusa")); continue
        cont["parole_escluse"] += 1
        sc = p["scores"] or []
        if not sc or not (p["scores_total"] or 0) > 0 or not p["choices"]:
            scarti.append((p["id"], sid, t, "senza voti")); continue
        w = max(range(len(sc)), key=lambda i: sc[i])
        if not RE_SI.match(p["choices"][w].strip()):
            scarti.append((p["id"], sid, t, f"scelta vincente non e' un si: {p['choices'][w][:40]}")); continue
        cont["approvata"] += 1
        fine = datetime.fromtimestamp(p["end"], tz=timezone.utc)
        entrata = datetime(fine.year, fine.month, fine.day, tzinfo=timezone.utc) + timedelta(days=1)
        sim = ok_sp[sid]
        mesi = mesi_di(sim)
        mese = entrata.strftime("%Y-%m")
        # presente nel mese dell'entrata: il primo mese dell'archivio <= mese <= ultimo mese
        if not mesi or not (mesi[0] <= mese <= mesi[-1]):
            scarti.append((p["id"], sid, t, f"perpetuo {sim} non presente nel mese {mese} (archivio {mesi[:1]}..{mesi[-1:]})")); continue
        cont["perpetuo_nel_mese"] += 1
        ev.append({"id": p["id"], "spazio": sid, "perpetuo": sim, "titolo": t, "fine": fine.strftime("%Y-%m-%d %H:%M"),
                   "entrata": entrata.strftime("%Y-%m-%d"), "mese_primo_perp": mesi[0],
                   "scelta": p["choices"][w][:40]})
    ev.sort(key=lambda e: (e["fine"], e["id"]))
    # 30 giorni dalla fine del voto dell'ultimo evento TENUTO della stessa moneta; uno scartato non riavvia
    tenuti, ultimo = [], {}
    for e in ev:
        fine = datetime.strptime(e["fine"], "%Y-%m-%d %H:%M")
        u = ultimo.get(e["perpetuo"])
        if u is not None and (fine - u) < timedelta(days=30):
            scarti.append((e["id"], e["spazio"], e["titolo"], "entro 30 giorni dall'ultimo evento tenuto della stessa moneta")); continue
        ultimo[e["perpetuo"]] = fine
        tenuti.append(e)
    # limite 10 aperti insieme (tenuta massima 10 giorni)
    max_aperti = 0
    for e in tenuti:
        d = datetime.strptime(e["entrata"], "%Y-%m-%d")
        n = sum(1 for x in tenuti if datetime.strptime(x["entrata"], "%Y-%m-%d") <= d < datetime.strptime(x["entrata"], "%Y-%m-%d") + timedelta(days=10))
        max_aperti = max(max_aperti, n)
    cont["dopo_30_giorni"] = len(tenuti)
    cont["max_aperti_insieme_B"] = max_aperti
    RIS.mkdir(exist_ok=True)
    (RIS / "spazi.json").write_text(json.dumps(spazi_log, ensure_ascii=False, indent=1))
    (RIS / "eventi.json").write_text(json.dumps(tenuti, ensure_ascii=False, indent=1))
    (RIS / "scarti.json").write_text(json.dumps(scarti, ensure_ascii=False, indent=1))
    rapp["conti"] = cont
    rapp["eventi"] = len(tenuti)
    return {"rapporto": rapp, "eventi": tenuti, "spazi": spazi_log, "scarti": scarti}


def main() -> None:
    r = costruisci()
    print(json.dumps(r["rapporto"], ensure_ascii=False))


if __name__ == "__main__":
    main()
