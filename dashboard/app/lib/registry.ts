/**
 * Il registro delle coppie, decodificato.
 *
 * Il registro sta in UN solo documento Firestore, e il limite e' 1 MiB. Il 19
 * settembre era all'86% e cresceva di ~37 KiB al giorno: oltre il limite Firestore
 * rifiuta la scrittura e il giro dell'ottimizzatore perde le conferme appena
 * guadagnate, cioe' settimane di attesa. Da li' il formato compatto, scritto da
 * `bot/core/firebase_client.py::encode_registry`:
 *
 *   - nomi di campo di una lettera (le chiavi JSON si ripetono 2.600 volte);
 *   - `symbol` e `strategy` tolti, perche' sono gia' dentro la chiave `COIN|strat`;
 *   - tempi arrotondati al secondo.
 *
 * Questa funzione e' l'UNICO punto in cui la dashboard sa che il formato compatto
 * esiste: i componenti continuano a leggere `pass_count`, `symbol`, `last_pf` come
 * prima. Accetta anche i formati vecchi, perche' il registro vivo resta in quello
 * finche' il primo giro col codice nuovo non lo riscrive — e nel mezzo la
 * dashboard deve continuare a mostrare i numeri, non una pagina vuota.
 */

const LUNGHI: Record<string, string> = {
  p: 'pass_count',
  d: 'last_pass_data_end',
  f: 'fail_count',
  v: 'last_seen_at',
  m: 'last_params',
  r: 'scale_r_mults',
  x: 'drift_seen_at',
  w: 'window_start',
  q: 'passed_in_window',
  g: 'generated',
  l: 'last_passed_at',
};

const FORMATO_COMPATTO = 2;

type Rec = Record<string, unknown>;

function espandi(compatte: Record<string, Rec>): Record<string, Rec> {
  const fuori: Record<string, Rec> = {};
  for (const [chiave, rec] of Object.entries(compatte ?? {})) {
    if (rec === null || typeof rec !== 'object') continue;
    const lungo: Rec = {};
    for (const [campo, valore] of Object.entries(rec)) {
      lungo[LUNGHI[campo] ?? campo] = valore;
    }
    const taglio = chiave.indexOf('|');
    if (taglio > 0) {
      if (lungo.symbol === undefined) lungo.symbol = chiave.slice(0, taglio);
      if (lungo.strategy === undefined) lungo.strategy = chiave.slice(taglio + 1);
    }
    fuori[chiave] = lungo;
  }
  return fuori;
}

/** `reg.pairs` in qualunque formato -> mappa `chiave -> record` coi nomi lunghi. */
export function decodePairs<T = Rec>(raw: unknown): Record<string, T> {
  let v: unknown = raw;
  if (typeof v === 'string') {
    try {
      v = JSON.parse(v);
    } catch {
      return {};
    }
  }
  if (v === null || typeof v !== 'object') return {};
  const obj = v as Record<string, unknown>;
  if (obj.v === FORMATO_COMPATTO && obj.k && typeof obj.k === 'object') {
    return espandi(obj.k as Record<string, Rec>) as unknown as Record<string, T>;
  }
  return obj as unknown as Record<string, T>;
}
