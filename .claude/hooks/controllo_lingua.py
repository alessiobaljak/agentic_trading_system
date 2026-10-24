#!/usr/bin/env python3
"""Controllo della lingua (24 ott 2026, richiesta del proprietario: «risolvi una volta per tutte»).

Gira come hook di Stop: prima che una risposta parta, legge l'ultimo testo dell'assistente nella trascrizione e, se sembra
scritto in inglese, blocca e chiede di riscriverlo in italiano. Il conto e' semplice: parole-spia inglesi contro parole-spia
italiane. Se la chiusura e' gia' stata bloccata una volta (stop_hook_active) non blocca di nuovo, per non girare in tondo.
Qualunque errore: esce zitto senza bloccare.
"""
import json
import re
import sys

INGLESI = {"the", "and", "with", "that", "this", "is", "are", "was", "were", "for", "not", "of", "to", "it", "you", "we",
           "i'm", "i'll", "i've", "it's", "here", "there", "from", "have", "has", "been", "will", "would", "should", "test",
           "tests", "round", "result", "results", "running", "done", "when", "which", "while", "still", "only", "also", "each",
           "every", "about", "after", "before", "because", "between", "against", "both", "than", "them", "they", "their", "then",
           "what", "where", "how", "why", "an", "at", "by", "or", "as", "so", "up", "out", "its", "into", "over", "under", "more",
           "most", "some", "any", "all", "one", "two", "three", "day", "days", "week", "weeks", "coins", "coin", "trade", "trades"}
ITALIANE = {"il", "lo", "la", "le", "gli", "di", "del", "della", "dei", "delle", "che", "non", "per", "con", "una", "un", "uno",
            "sono", "è", "ho", "hai", "ha", "abbiamo", "nel", "nella", "sul", "sulla", "anche", "questo", "questa", "questi",
            "prova", "prove", "come", "ma", "se", "più", "già", "ancora", "quando", "dove", "perché", "cosa", "ogni", "giorno",
            "giorni", "settimana", "monete", "moneta", "risultato", "risultati", "operazione", "operazioni", "regola", "regole",
            "al", "alla", "allo", "ai", "agli", "dal", "dalla", "fra", "tra", "tutto", "tutti", "tutte", "stessa", "stesso",
            "adesso", "ora", "poi", "dopo", "prima", "senza", "mai", "sempre", "quindi", "cioè", "ecco", "fatto", "fatta"}


def ultimo_testo(percorso: str) -> str:
    """L'ultimo blocco di testo dell'assistente nella trascrizione (la risposta che sta per partire)."""
    ultimo = ""
    with open(percorso, encoding="utf-8") as f:
        for riga in f:
            try:
                r = json.loads(riga)
            except ValueError:
                continue
            if r.get("type") != "assistant":
                continue
            c = r.get("message", {}).get("content")
            if not isinstance(c, list):
                continue
            for b in c:
                if isinstance(b, dict) and b.get("type") == "text" and b.get("text", "").strip():
                    ultimo = b["text"]
    return ultimo


def sembra_inglese(testo: str) -> tuple:
    # via il codice e i percorsi, che sono in inglese per forza
    t = re.sub(r"`[^`]*`", " ", testo)
    t = re.sub(r"https?://\S+|\S+/\S+", " ", t)
    parole = re.findall(r"[a-zàèéìòù']+", t.lower())
    if len(parole) < 12:
        return False, 0, 0
    en = sum(p in INGLESI for p in parole)
    it = sum(p in ITALIANE for p in parole)
    return en >= 6 and en > 1.5 * it, en, it


def main() -> int:
    try:
        dati = json.load(sys.stdin)
        if dati.get("stop_hook_active"):
            return 0
        testo = ultimo_testo(dati.get("transcript_path", ""))
        inglese, en, it = sembra_inglese(testo)
        if inglese:
            print(json.dumps({"decision": "block",
                              "reason": f"L'ultima risposta sembra in inglese ({en} parole inglesi contro {it} italiane). Il "
                                        "proprietario vuole SOLO l'italiano: riscrivi per intero lo stesso messaggio in italiano "
                                        "semplice, senza sigle, e manda quello."}))
    except Exception:  # noqa: BLE001
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
