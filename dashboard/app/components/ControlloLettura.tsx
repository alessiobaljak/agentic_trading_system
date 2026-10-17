'use client';

import type { CSSProperties } from 'react';
import type { Testata } from '../lib/controllo';

/**
 * La «lettura» di una sezione del controllo, in una riga (25 set 2026).
 *
 * Ogni sezione del documento porta una frase scritta dal bot da regole (mai
 * da un modello), lunga al massimo 140 caratteri, in cui ogni numero esiste
 * anche come campo: «55 trade in 10 giorni, 42% vinti, −46,65 USDT (−4,7%)».
 * E' la riga che il proprietario legge dal telefono prima di ogni altra cosa,
 * quindi sta da sola, grande abbastanza, e porta nel `title` le fonti e il
 * dettaglio (piu' lungo) per chi vuole sapere da dove viene.
 *
 * Se la sezione e' fallita (`errore`), la riga lo dice al posto della lettura:
 * un errore nascosto sarebbe un numero mancante che sembra uno zero.
 */
export default function ControlloLettura({
  sezione,
  vuoto = 'lettura non disponibile',
  style,
}: {
  sezione?: Testata | null;
  /** Cosa scrivere se la sezione (o la lettura) manca del tutto. */
  vuoto?: string;
  style?: CSSProperties;
}) {
  if (!sezione) {
    return (
      <p className="lettura muted" style={style}>
        {vuoto}
      </p>
    );
  }
  if (sezione.errore) {
    return (
      <p className="lettura" style={{ color: 'var(--amber)', ...style }} title={sezione.errore}>
        sezione non calcolata dal bot: {sezione.errore}
      </p>
    );
  }
  const fonti = (sezione.fonti ?? []).filter(Boolean);
  const titolo = [sezione.dettaglio, fonti.length ? `fonti: ${fonti.join(', ')}` : '']
    .filter(Boolean)
    .join('\n');
  return (
    <p className="lettura" style={style} title={titolo || undefined}>
      {sezione.lettura || vuoto}
    </p>
  );
}
