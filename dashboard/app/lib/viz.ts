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
