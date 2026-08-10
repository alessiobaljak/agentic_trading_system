"""Client LLM condiviso — l'unico punto da cui il sistema parla con un modello.

TRE REGOLE, valide per ogni chiamante di questo modulo.

1. FAIL-OPEN. Nessuna chiave, rete giu', risposta malformata, timeout: si torna
   `None` e il chiamante prosegue col comportamento deterministico di sempre.
   L'AI puo' solo AGGIUNGERE valore, mai togliere disponibilita': un bot che si
   ferma perche' un'API non risponde e' peggio di un bot senza AI.

2. MAI NEL PERCORSO DI ESECUZIONE. Qui non si decidono trade. Il modello genera
   IPOTESI e LETTURE; a validarle resta il GATE 1, che e' deterministico,
   riproducibile e non ha opinioni. Mettere un modello sul singolo trade
   romperebbe la parita' gate<->paper, che e' l'unica cosa che oggi funziona.

3. L'OUTPUT E' UN SOSPETTO, NON UN FATTO. Ogni struttura che torna di qui va
   validata dal chiamante contro un vocabolario chiuso prima di essere usata.
"""
from __future__ import annotations

import json
import time
from typing import Any, Optional

from bot.config import settings

# budget di sicurezza: una risposta che non arriva non deve bloccare un ciclo
_TIMEOUT_S = float(settings.AI_TIMEOUT_SECONDS)


def available() -> bool:
    """True se il livello AI e' utilizzabile. I chiamanti lo usano per saltare
    del tutto la preparazione dell'input quando non c'e' chiave configurata."""
    return bool(settings.AI_ENABLED and settings.ANTHROPIC_API_KEY)


def ask_json(system: str, user: str, max_tokens: int = 2000,
             label: str = "ai") -> Optional[Any]:
    """Interroga il modello e ritorna il JSON della risposta, o None.

    Il modello puo' incorniciare il JSON con del testo: si estrae il primo
    oggetto/array bilanciato invece di pretendere una risposta pulita.
    """
    if not available():
        return None
    t0 = time.time()
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY,
                                     timeout=_TIMEOUT_S)
        resp = client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(getattr(b, "text", "") for b in resp.content).strip()
        data = _extract_json(text)
        if data is None:
            print(f"[{label}] risposta senza JSON valido -> ignorata")
            return None
        usage = getattr(resp, "usage", None)
        tok = f" · {usage.input_tokens}+{usage.output_tokens} token" if usage else ""
        print(f"[{label}] ok in {time.time() - t0:.1f}s{tok}")
        return data
    except Exception as exc:  # noqa: BLE001
        print(f"[{label}] non disponibile ({type(exc).__name__}: {exc}) -> proseguo senza AI")
        return None


def _extract_json(text: str) -> Optional[Any]:
    """Primo oggetto o array JSON bilanciato nel testo.

    Non si puo' usare find('{') + rfind('}'): se il modello scrive prosa dopo il
    JSON, o due blocchi, quegli indici catturano spazzatura. Qui si conta la
    profondita' delle parentesi ignorando quelle dentro le stringhe.
    """
    # si parte dal delimitatore che compare PRIMA: provando sempre '{' per primo,
    # un array di oggetti tornerebbe come il suo primo elemento invece che intero.
    candidates = [(text.find(o), o, c) for o, c in (("{", "}"), ("[", "]"))]
    for start, opener, closer in sorted(p for p in candidates if p[0] >= 0):
        depth = 0
        in_str = False
        escape = False
        for i in range(start, len(text)):
            ch = text[i]
            if in_str:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_str = False
                continue
            if ch == '"':
                in_str = True
            elif ch == opener:
                depth += 1
            elif ch == closer:
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i + 1])
                    except json.JSONDecodeError:
                        break
    return None
