'use client';

import type { ReactNode } from 'react';
import { durata } from '../lib/viz';

/**
 * Una sezione a fisarmonica della scheda Controllo (25 set 2026).
 *
 * E' un `<details>` nativo: si apre e si chiude senza JavaScript, funziona
 * anche se React non e' ancora montato, e sul telefono un titolo cliccabile
 * vale piu' di dieci pannelli srotolati. Nel titolo c'e' l'indicazione di
 * QUANDO la sezione e' stata calcolata («aggiornato 12 min fa»), perche' il
 * controllo e' orario e chi legge deve sapere se sta guardando un numero di
 * adesso o di un'ora fa. Se la sezione e' fallita nel bot (`errore` della
 * testata) lo si dice qui, nel titolo, e il contenuto resta nascosto.
 */
export default function ControlloSezione({
  titolo,
  computedAt,
  aggiornatoS,
  errore,
  aperta = false,
  riassunto,
  children,
}: {
  titolo: string;
  /** `computed_at` della sezione (secondi epoch): da qui l'eta'. */
  computedAt?: number | null;
  /** In alternativa, l'eta' gia' calcolata in secondi. */
  aggiornatoS?: number | null;
  /** `errore` della testata: la sezione non e' stata calcolata dal bot. */
  errore?: string | null;
  aperta?: boolean;
  /** Una riga a destra del titolo, visibile anche a sezione chiusa. */
  riassunto?: ReactNode;
  children?: ReactNode;
}) {
  const eta =
    aggiornatoS != null
      ? aggiornatoS
      : computedAt != null && Number.isFinite(Number(computedAt))
        ? Math.max(0, Math.floor(Date.now() / 1000 - Number(computedAt)))
        : null;

  return (
    <details className="sezione panel" open={aperta || undefined}>
      <summary className="sezione-testa">
        <span className="sezione-titolo">{titolo}</span>
        {riassunto != null && <span className="sezione-riassunto">{riassunto}</span>}
        <span className="sezione-eta muted" title={errore ? errore : undefined}>
          {errore ? 'non calcolata dal bot' : eta != null ? `aggiornato ${durata(eta)} fa` : '—'}
        </span>
      </summary>
      <div className="sezione-corpo">
        {errore ? (
          <p className="muted" style={{ margin: 0, fontSize: 12.5 }}>
            Il bot non ha potuto calcolare questa sezione: <code>{errore}</code>. Il resto del
            controllo e&apos; uscito lo stesso.
          </p>
        ) : (
          children
        )}
      </div>
    </details>
  );
}
