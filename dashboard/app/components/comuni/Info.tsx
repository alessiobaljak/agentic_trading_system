'use client';

import type { ReactNode, SyntheticEvent } from 'react';

/**
 * La piccola «i» che apre una spiegazione al tocco (seconda tornata, 10 nov 2026: «troppo testo»): il testo resta chiuso finché non
 * serve. Un `<details>` (funziona al tocco e con la tastiera); il testo si apre in un riquadro in basso sullo schermo, così non esce
 * mai dai bordi del telefono. Se ne apre una alla volta; un tocco sul riquadro lo chiude.
 */
export function Info({ children, etichetta = 'spiegazione' }: { children: ReactNode; etichetta?: string }) {
  const apri = (e: SyntheticEvent<HTMLDetailsElement>) => {
    const questa = e.currentTarget;
    if (!questa.open) return;
    document.querySelectorAll<HTMLDetailsElement>('details.cr-info[open]').forEach((d) => {
      if (d !== questa) d.open = false;
    });
  };
  return (
    <details className="cr-info" onToggle={apri}>
      <summary aria-label={etichetta} title={etichetta}>i</summary>
      <div className="cr-info-testo" role="note"
        onClick={(e) => { (e.currentTarget.parentElement as HTMLDetailsElement).open = false; }}>
        {children}
      </div>
    </details>
  );
}
