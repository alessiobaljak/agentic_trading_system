/**
 * I COLORI DEI GRAFICI, e il motivo per cui sono questi.
 *
 * Le fasce del gate (1 passaggio, 2 passaggi, validata) NON sono categorie: sono
 * gradini di una scala. Più conferme = più evidenza. Quindi la codifica giusta è una
 * RAMPA ORDINALE — un solo colore, che schiarisce man mano che si avanza — e non
 * quattro tinte diverse, che direbbero "cose distinte" invece di "stessa cosa, più
 * avanti".
 *
 * L'ultimo gradino fa eccezione ed è verde: «validata» non è "un passaggio in più", è
 * lo stato di arrivo. È un colore di STATO, e come tale non porta mai il significato da
 * solo — c'è sempre l'etichetta accanto.
 *
 * VALIDATI, NON SCELTI A OCCHIO. Con lo strumento del design system, sulla superficie
 * scura di questa dashboard (#111a2c):
 *
 *   rampa ordinale #256abf → #86b6ef
 *     luminosità monotona · gradini ≥ 0.06 · estremo chiaro 3.22:1 sulla superficie
 *     · una sola tinta (3° di scarto)  ->  tutti i controlli passati
 *
 *   separazione fra le tre serie (caso peggiore, tutte le coppie)
 *     vista normale ΔE 24.2 · protanopia 23.7 · tritanopia 9.8
 *     -> sopra il pavimento richiesto (15 normale, 8 daltonismo)
 *
 * La versione precedente di questi pannelli usava #2a4a73/#3f7fd0/#4f9cf9/#3fb950 e
 * NON passava: due dei blu erano a ΔE 9.5, indistinguibili anche con vista piena.
 */

/** Rampa ordinale del gate: più chiaro = più conferme accumulate. */
export const GATE_RAMP = {
  uno: '#256abf',      // 1 passaggio
  due: '#86b6ef',      // 2 passaggi
} as const;

/** Colori di STATO (fissi, mai tematizzati). Vanno sempre con un'etichetta. */
export const STATO = {
  buono: '#0ca30c',
  attenzione: '#fab219',
  serio: '#ec835a',
  critico: '#d03b3b',
} as const;

/** Griglia e assi: una tacca sopra la superficie, mai tratteggiati. */
export const CHROME = {
  griglia: '#1c2740',
  asse: '#5f6d84',
  superficie: '#111a2c',
} as const;

export function formatta(n: number | undefined | null): string {
  return Number(n ?? 0).toLocaleString('it-IT');
}

export function quando(ts?: number | null): string {
  if (!ts) return '—';
  return new Date(ts * 1000).toLocaleString('it-IT', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/* ------------------------------------------------------------------------- */
/* Formattazione dei numeri del controllo (25 set 2026).                      */
/* La virgola decimale e' quella italiana, come gia' fa `formatta`; qui si    */
/* aggiungono i decimali fissi, il segno esplicito e le durate, perche' i     */
/* pannelli del controllo mostrano decine di numeri e devono essere uguali    */
/* fra loro (e uguali alle letture scritte dal bot, che usa la stessa regola).*/
/* ------------------------------------------------------------------------- */

/** «1.234,50» con decimali fissi; «—» se il dato manca (null = non misurato). */
export function numero(n: number | null | undefined, dec = 2): string {
  if (n == null || !Number.isFinite(Number(n))) return '—';
  return Number(n).toLocaleString('it-IT', {
    minimumFractionDigits: dec,
    maximumFractionDigits: dec,
  });
}

/** Come `numero`, ma col «+» davanti ai positivi: per PnL e rendimenti. */
export function segno(n: number | null | undefined, dec = 2): string {
  if (n == null || !Number.isFinite(Number(n))) return '—';
  const s = numero(n, dec);
  return Number(n) > 0 ? `+${s}` : s;
}

/** Percentuale gia' in percento (campi `_pct`): «4,7%». */
export function pct(n: number | null | undefined, dec = 1): string {
  if (n == null || !Number.isFinite(Number(n))) return '—';
  return `${numero(n, dec)}%`;
}

/** Frazione 0-1 mostrata in percento: 0,42 → «42%». */
export function quota(n: number | null | undefined, dec = 0): string {
  if (n == null || !Number.isFinite(Number(n))) return '—';
  return `${numero(Number(n) * 100, dec)}%`;
}

/**
 * Durata leggibile da secondi: «22 s», «5 min», «1 h 30», «2 g 3 h».
 * Stessa regola di `_eta` in `bot/learning/controllo.py`, cosi' la dashboard e
 * le letture scritte dal bot dicono la stessa cosa.
 */
export function durata(s: number | null | undefined): string {
  if (s == null || !Number.isFinite(Number(s))) return '—';
  const sec = Math.max(0, Math.floor(Number(s)));
  if (sec < 60) return `${sec} s`;
  if (sec < 3600) return `${Math.floor(sec / 60)} min`;
  if (sec < 86400) {
    const h = Math.floor(sec / 3600);
    const m = Math.floor((sec % 3600) / 60);
    return m > 0 ? `${h} h ${String(m).padStart(2, '0')}` : `${h} h`;
  }
  const g = Math.floor(sec / 86400);
  const h = Math.floor((sec % 86400) / 3600);
  return `${g} g ${h} h`;
}
