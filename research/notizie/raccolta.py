"""La raccolta delle notizie crypto (REGOLE.md): a ogni giro legge le pagine pubbliche degli ultimi articoli di 21 siti, salva gli articoli
nuovi in `archivio/AAAA-MM-GG.jsonl.gz` e scrive il giro in `archivio/giri.csv`. Il primo giorno di ogni mese rifa' l'elenco dei nomi
delle monete (`nomi_AAAA-MM.json`) dalle prime 1.000 di CoinGecko.

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
    "cryptonews": "https://cryptonews.com/news/feed/",
    "dailyhodl": "https://dailyhodl.com/feed/",
    "cryptobriefing": "https://cryptobriefing.com/feed/",
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


def visti_di_recente(oggi: datetime, giorni: int = 10) -> set:
    s = set()
    for k in range(giorni):
        f = ARCHIVIO / f"{(oggi - timedelta(days=k)).strftime('%Y-%m-%d')}.jsonl.gz"
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


def citate(testo: str, elenco: dict) -> list:
    """Le monete citate in un testo (REGOLE.md, sezione 2)."""
    out = []
    for s, x in elenco.items():
        sigla, nome = x["sigla"], x["nome"]
        trovata = bool(re.search(r"\$" + re.escape(sigla) + r"\b", testo, re.I))
        if not trovata and len(sigla) >= 3 and sigla not in PAROLE:
            trovata = bool(re.search(r"(?<![A-Za-z0-9])" + re.escape(sigla) + r"(?![A-Za-z0-9])", testo))
        if not trovata and len(nome) >= 5 and nome not in PAROLE and nome.upper() not in PAROLE:
            trovata = bool(re.search(r"\b" + re.escape(nome) + r"\b", testo))
        if not trovata and s in SEMPRE:
            trovata = any(re.search(r"\b" + n + r"\b", testo) for n in SEMPRE[s])
        if trovata:
            out.append(s)
    return out


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
        giro.append((fonte, len(articoli), n_nuovi, "piena" if articoli and n_nuovi == len(articoli) else ""))
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
    log(f"[notizie] {ora.strftime('%Y-%m-%d %H:%M')} UTC: {len(nuovi)} articoli nuovi da {risposte} fonti su {len(FONTI)}; "
        f"piene: {', '.join(x[0] for x in giro if x[3]) or 'nessuna'}")
    return {"nuovi": len(nuovi), "fonti_che_rispondono": risposte}


if __name__ == "__main__":
    esegui()
