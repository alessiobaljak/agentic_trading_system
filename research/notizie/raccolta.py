"""La raccolta delle notizie crypto (REGOLE.md): a ogni giro legge le pagine pubbliche degli ultimi articoli di 21 siti, salva gli articoli
nuovi in `archivio/AAAA-MM-GG.jsonl.gz` e scrive il giro in `archivio/giri.csv`. Il primo giorno di ogni mese rifa' l'elenco dei nomi
delle monete (`nomi_AAAA-MM.json`) dalle prime 1.000 di CoinGecko. Dal 31 ottobre 2026 salva anche le monete di tendenza di
CoinGecko in `archivio/tendenze.csv` (idea 126 del registro); dal 2 novembre legge anche le posizioni dei trader migliori di
Hyperliquid (`research/trader_copiati/hyperliquid.py`, idea 132).

Uso: python3 -m research.notizie.raccolta
"""
from __future__ import annotations

import gzip
import hashlib
import html
import json
import re
import time
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

QUI = Path(__file__).parent
ARCHIVIO = QUI / "archivio"
UA = {"User-Agent": "ricerca/1.0"}
FONTI = {
    "cointelegraph": "https://cointelegraph.com/rss",
    "coindesk": "https://www.coindesk.com/arc/outboundfeeds/rss",
    "decrypt": "https://decrypt.co/feed",
    "theblock": "https://www.theblock.co/rss.xml",
    "cryptoslate": "https://cryptoslate.com/feed/",
    "newsbtc": "https://www.newsbtc.com/feed/",
    "bitcoinmagazine": "https://bitcoinmagazine.com/feed",
    "utoday": "https://u.today/rss.php",
    "ambcrypto": "https://ambcrypto.com/feed/",
    "coingape": "https://coingape.com/feed/",
    "cryptopotato": "https://cryptopotato.com/feed/",
    "beincrypto": "https://beincrypto.com/feed/",
    "beincrypto2": "https://beincrypto.com/feed/?paged=2",   # 6 nov 2026: 12 articoli, circa 5 ore; piena alle 04:20 e alle 16:20
    "cryptonews": "https://cryptonews.com/news/feed/",
    "dailyhodl": "https://dailyhodl.com/feed/",
    "cryptobriefing": "https://cryptobriefing.com/feed/",
    "cryptobriefing2": "https://cryptobriefing.com/feed/?paged=2",   # 4 nov 2026: la prima pagina (30) non bastava fra due giri
    "cryptobriefing3": "https://cryptobriefing.com/feed/?paged=3",   # 10 nov 2026: piene anche le prime due alle 16:18
    "cryptobriefing4": "https://cryptobriefing.com/feed/?paged=4",   # 17 nov 2026: piene tutte e tre alle 20:18 (98 articoli in 4 ore)
    "coinjournal": "https://coinjournal.net/feed/",
    "cryptonewsdotnet": "https://crypto.news/feed/",
    "bitcoinist": "https://bitcoinist.com/feed/",
    "zycrypto": "https://zycrypto.com/feed/",
    "coincodex": "https://coincodex.com/feed/",
    "thedefiant": "https://thedefiant.io/api/feed",
}
# sigle e nomi che sono anche parole comuni: non si contano senza il «$» (REGOLE.md, sezione 2)
PAROLE = {"ONE", "ALL", "GAS", "SUN", "NOT", "WIN", "HOT", "KEY", "BAND", "FLOW", "MOVE", "PEOPLE", "ACE", "MASK", "RARE", "BOND", "CAKE",
          "DOGS", "BEAM", "PORTAL", "SAFE", "OPEN", "TRUMP", "MEME", "HOOK", "LOOM", "DENT", "POND", "COTI", "AUCTION", "BANANA", "MAGIC",
          "CHESS", "ORDER", "BLUR", "PRIME", "SAGA", "SCR", "STORJ", "TOKEN", "TRUTH", "VANA", "WOO", "ZERO", "HIGH", "LOW", "AIR", "BIG",
          "CAT", "DOG", "NEW", "TOP", "NOW", "ART", "USD", "CEO", "SEC", "ETF", "NFT", "DAO", "API", "APP", "GDP", "CPI", "FED", "IPO",
          "ATH", "TVL", "DEX", "CEX", "AMA", "FUD", "WEB", "BUY", "SELL", "THE", "AND", "FOR", "ARE", "YOU", "HAS", "NET", "PAY", "RED",
          "Optimism", "Stacks", "Polygon", "Ronin", "Celo", "Gnosis", "Arweave", "Render", "Theta", "Fantom", "Sonic", "Bitget", "Kaspa",
          "Story", "Movement", "Plume", "Echelon", "Monad", "Berachain", "Gravity", "Pump", "Bonk", "Floki", "Popcat", "Pepe", "Maker",
          "Compound", "Curve", "Balancer", "Frax", "Liquity", "Synapse", "Across", "Wormhole", "Jupiter", "Raydium", "Orca", "Drift",
          "Kamino", "Marinade", "Ethena", "Pendle", "Lido", "Rocket", "Eigen", "Puffer", "Swell", "Ether", "Bitcoin", "Ethereum"}
# 27 novembre 2026 (audit del 26 novembre): sigle che nel conto automatico davano abbinamenti falsi (ARK Invest, la società di mining
# HIVE, la legge GENIUS, le azioni SATS di Strive, «APR» il tasso annuo); da oggi contano solo con il «$» (REGOLE.md, nota del 27
# novembre). Tenute a parte perché la prova in avanti (`prova_avanti.py`) riporta il conto con e senza di loro.
PAROLE_FINO_AL_26_NOVEMBRE = frozenset(PAROLE)
PAROLE_27_NOVEMBRE = frozenset({"ARK", "HIVE", "GENIUS", "SATS", "APR"})
PAROLE = set(PAROLE_FINO_AL_26_NOVEMBRE | PAROLE_27_NOVEMBRE)
# Bitcoin ed Ether si contano comunque con il nome (REGOLE.md): li aggiunge `nomi()`
SEMPRE = {"BTCUSDT": ("Bitcoin",), "ETHUSDT": ("Ethereum", "Ether")}


def _get(url: str, tentativi: int = 3) -> bytes | None:
    for k in range(tentativi):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return r.read()
        except Exception:  # noqa: BLE001
            time.sleep(2 * (k + 1))
    return None


def _testo(x: str | None) -> str:
    t = html.unescape(re.sub(r"<[^>]+>", " ", x or ""))
    return re.sub(r"\s+", " ", t).strip()


def _ora(x: str | None) -> str | None:
    if not x:
        return None
    try:
        d = parsedate_to_datetime(x)
    except Exception:  # noqa: BLE001
        try:
            d = datetime.fromisoformat(x.replace("Z", "+00:00"))
        except Exception:  # noqa: BLE001
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def leggi_fonte(nome: str, url: str) -> list:
    dati = _get(url)
    if not dati:
        return []
    try:
        radice = ET.fromstring(dati)
    except ET.ParseError:
        return []
    atom = "{http://www.w3.org/2005/Atom}"
    out = []
    for it in list(radice.iter("item")) + list(radice.iter(atom + "entry")):
        titolo = it.findtext("title") or it.findtext(atom + "title")
        link = it.findtext("link") or ""
        if not link:
            e = it.find(atom + "link")
            link = e.get("href", "") if e is not None else ""
        data = it.findtext("pubDate") or it.findtext(atom + "published") or it.findtext(atom + "updated")
        somm = it.findtext("description") or it.findtext(atom + "summary") or ""
        if titolo and link:
            out.append({"fonte": nome, "titolo": _testo(titolo), "sommario": _testo(somm)[:500], "link": link.strip(), "pubblicato": _ora(data)})
    return out


def ora_utc(x) -> datetime | None:
    """Un'ora dell'archivio («pubblicato» o «visto»: in UTC, scritte senza il fuso) letta sempre in UTC, qualunque sia il fuso della
    macchina. Dal 27 novembre 2026 (audit del 26 novembre): `fromisoformat` seguito da `astimezone` prendeva l'ora senza fuso come ora
    locale (con l'ora svizzera la finestra si spostava di 1 o 2 ore)."""
    if not x:
        return None
    try:
        d = datetime.fromisoformat(str(x).replace("Z", "+00:00"))
    except ValueError:
        return None
    return (d if d.tzinfo else d.replace(tzinfo=timezone.utc)).astimezone(timezone.utc)


def visti_di_recente(oggi: datetime, giorni: int | None = None) -> set:
    """Gli id degli articoli già salvati. Dal 27 novembre 2026 (audit del 26 novembre) di tutto l'archivio (`giorni=None`), non più dei
    soli ultimi 10 giorni: un articolo che restava in pagina (la pagina fissa di Cointelegraph «Here's what happened in crypto today») si
    salvava di nuovo ogni 10 giorni, mentre REGOLE.md (sezione 1) dice che chi l'ha già visto non lo salva una seconda volta."""
    if giorni is None:
        file = sorted(ARCHIVIO.glob("????-??-??.jsonl.gz"))
    else:
        file = [ARCHIVIO / f"{(oggi - timedelta(days=k)).strftime('%Y-%m-%d')}.jsonl.gz" for k in range(giorni)]
    s = set()
    for f in file:
        if f.exists():
            with gzip.open(f, "rt", encoding="utf-8") as g:
                s.update(json.loads(r)["id"] for r in g if r.strip())
    return s


def nomi(oggi: datetime) -> Path:
    """L'elenco dei nomi del mese (REGOLE.md, sezione 2): prime 1.000 monete di CoinGecko, abbinate ai perpetui del pannello."""
    f = QUI / f"nomi_{oggi.strftime('%Y-%m')}.json"
    if f.exists():
        return f
    from research.programma6 import annunci as an
    from research.programma6 import seconda as sc
    simboli = list(sc.pannello()["simboli"])
    monete = []
    for p in range(1, 5):
        d = _get(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page={p}")
        if d:
            monete += json.loads(d)
        time.sleep(3)
    elenco: dict = {}
    for m in monete:                                   # gia' in ordine di valore: vale la prima sigla vista
        sigla = (m.get("symbol") or "").upper()
        s = an.perpetuo(sigla, simboli) if sigla else ""
        if s and s not in elenco:
            elenco[s] = {"sigla": sigla, "nome": m.get("name") or ""}
    for s, nn in SEMPRE.items():
        elenco.setdefault(s, {"sigla": s[:-4], "nome": nn[0]})
    f.write_text(json.dumps({"fatto": oggi.strftime("%Y-%m-%d %H:%M"), "monete": len(monete), "elenco": elenco}, ensure_ascii=False, indent=0))
    return f


def citate(testo: str, elenco: dict, parole: set | None = None) -> list:
    """Le monete citate in un testo (REGOLE.md, sezione 2). `parole` (di norma `PAROLE`) serve solo alla prova in avanti, che rifà il
    conto anche senza le sigle aggiunte il 27 novembre 2026."""
    parole = PAROLE if parole is None else parole
    out = []
    for s, x in elenco.items():
        sigla, nome = x["sigla"], x["nome"]
        trovata = bool(re.search(r"\$" + re.escape(sigla) + r"\b", testo, re.I))
        if not trovata and len(sigla) >= 3 and sigla not in parole:
            trovata = bool(re.search(r"(?<![A-Za-z0-9])" + re.escape(sigla) + r"(?![A-Za-z0-9])", testo))
        if not trovata and len(nome) >= 5 and nome not in parole and nome.upper() not in parole:
            trovata = bool(re.search(r"\b" + re.escape(nome) + r"\b", testo))
        if not trovata and s in SEMPRE:
            trovata = any(re.search(r"\b" + n + r"\b", testo) for n in SEMPRE[s])
        if trovata:
            out.append(s)
    return out


def citatore(elenco: dict, parole: set | None = None):
    """La stessa regola di `citate` (REGOLE.md, sezione 2) con le espressioni preparate una volta per elenco: restituisce una funzione
    testo → monete citate. Serve alla prova in avanti, che legge migliaia di articoli (`citate` ne fa circa 20 al secondo, perché
    ricompila le espressioni a ogni articolo). Un test controlla che dia sempre lo stesso risultato di `citate`."""
    parole = PAROLE if parole is None else parole
    prove = []
    for s, x in elenco.items():
        sigla, nome = x["sigla"], x["nome"]
        pp = [re.compile(r"\$" + re.escape(sigla) + r"\b", re.I)]
        if len(sigla) >= 3 and sigla not in parole:
            pp.append(re.compile(r"(?<![A-Za-z0-9])" + re.escape(sigla) + r"(?![A-Za-z0-9])"))
        if len(nome) >= 5 and nome not in parole and nome.upper() not in parole:
            pp.append(re.compile(r"\b" + re.escape(nome) + r"\b"))
        if s in SEMPRE:
            pp += [re.compile(r"\b" + n + r"\b") for n in SEMPRE[s]]
        prove.append((s, pp))

    def cerca(testo: str) -> list:
        return [s for s, pp in prove if any(p.search(testo) for p in pp)]
    return cerca


TENDENZE = "https://api.coingecko.com/api/v3/search/trending"


def tendenze(ora: datetime) -> int:
    """Idea 126 del registro: la lista delle monete di tendenza di CoinGecko (le più cercate), salvata a ogni giro in
    `archivio/tendenze.csv` (ora, posizione, id, sigla, nome, posizione per capitalizzazione). Restituisce le righe scritte."""
    b = _get(TENDENZE)
    if not b:
        return 0
    try:
        voci = json.loads(b).get("coins") or []
    except Exception:  # noqa: BLE001
        return 0
    f = ARCHIVIO / "tendenze.csv"
    if not f.exists():
        f.write_text("ora,posizione,id,sigla,nome,rango_capitalizzazione\n")
    righe = []
    for k, v in enumerate(voci, 1):
        x = v.get("item") or {}
        nome = str(x.get("name") or "").replace(",", " ").replace("\n", " ")
        righe.append(f"{ora.strftime('%Y-%m-%d %H:%M')},{k},{x.get('id') or ''},{str(x.get('symbol') or '').upper()},{nome},"
                     f"{x.get('market_cap_rank') if x.get('market_cap_rank') is not None else ''}\n")
    with f.open("a") as g:
        g.writelines(righe)
    return len(righe)


def sito(fonte: str) -> str:
    """Il sito di una fonte: le pagine in più dello stesso sito hanno il nome con un numero in fondo (cryptobriefing2, beincrypto2)."""
    return re.sub(r"\d+$", "", fonte)


def note_piena(giro: list) -> list:
    """La nota «piena» di ogni riga del giro [(fonte, articoli, nuovi), ...], nell'ordine di `FONTI`. Dal 27 novembre 2026 (audit del
    26 novembre) si calcola per sito e non per pagina: un sito è pieno solo se gli articoli nuovi riempiono tutto quello che le sue
    pagine hanno dato, e la nota va solo sulla riga della sua ultima pagina. Prima una prima pagina tutta nuova con la seconda che
    ritrovava articoli già visti dava un falso allarme (26 novembre, Crypto Briefing)."""
    tot: dict = {}
    nuovi: dict = {}
    ultima: dict = {}
    for k, (fonte, n, n_nuovi) in enumerate(giro):
        s = sito(fonte)
        tot[s] = tot.get(s, 0) + n
        nuovi[s] = nuovi.get(s, 0) + n_nuovi
        ultima[s] = k
    pieni = {s for s in tot if tot[s] and nuovi[s] == tot[s]}
    return ["piena" if sito(fonte) in pieni and ultima[sito(fonte)] == k else "" for k, (fonte, _, _) in enumerate(giro)]


def esegui(log=print) -> dict:
    ora = datetime.now(timezone.utc)
    ARCHIVIO.mkdir(parents=True, exist_ok=True)
    nomi(ora)
    with ThreadPoolExecutor(max_workers=8) as ex:
        risultati = dict(zip(FONTI, ex.map(lambda x: leggi_fonte(*x), FONTI.items())))
    visti = visti_di_recente(ora)
    nuovi, giro = [], []
    for fonte, articoli in risultati.items():
        n_nuovi = 0
        for a in articoli:
            a["id"] = hashlib.sha1(a["link"].encode()).hexdigest()[:16]
            if a["id"] in visti:
                continue
            visti.add(a["id"])
            a["visto"] = ora.strftime("%Y-%m-%d %H:%M:%S")
            nuovi.append(a)
            n_nuovi += 1
        giro.append((fonte, len(articoli), n_nuovi))
    giro = [(fonte, n, k, nota) for (fonte, n, k), nota in zip(giro, note_piena(giro))]
    f = ARCHIVIO / f"{ora.strftime('%Y-%m-%d')}.jsonl.gz"
    with gzip.open(f, "at", encoding="utf-8") as g:
        for a in nuovi:
            g.write(json.dumps(a, ensure_ascii=False) + "\n")
    giri = ARCHIVIO / "giri.csv"
    if not giri.exists():
        giri.write_text("ora,fonte,articoli,nuovi,nota\n")
    with giri.open("a") as g:
        for fonte, n, k, nota in giro:
            g.write(f"{ora.strftime('%Y-%m-%d %H:%M')},{fonte},{n},{k},{nota}\n")
    risposte = sum(1 for _, n, _, _ in giro if n)
    try:
        n_tendenze = tendenze(ora)
    except Exception:  # noqa: BLE001
        n_tendenze = 0
    try:                                          # idea 132: i trader migliori di Hyperliquid (trader_copiati/HYPERLIQUID.md)
        from research.trader_copiati import hyperliquid as th
        th.esegui(ora, log)
    except Exception as ex:  # noqa: BLE001
        log(f"[trader] Hyperliquid non letto ({ex})")
    try:                                          # idea 151: la mappa delle liquidazioni di Hyperliquid (trader_copiati/LIQUIDAZIONI.md)
        from research.trader_copiati import liquidazioni as tl
        tl.esegui(ora, log)
    except Exception as ex:  # noqa: BLE001
        log(f"[liquidazioni] Hyperliquid non letto ({ex})")
    log(f"[notizie] {ora.strftime('%Y-%m-%d %H:%M')} UTC: {len(nuovi)} articoli nuovi da {risposte} fonti su {len(FONTI)}; "
        f"piene: {', '.join(sito(x[0]) for x in giro if x[3]) or 'nessuna'}; monete di tendenza su CoinGecko: {n_tendenze}")
    return {"nuovi": len(nuovi), "fonti_che_rispondono": risposte, "tendenze": n_tendenze}


if __name__ == "__main__":
    esegui()
