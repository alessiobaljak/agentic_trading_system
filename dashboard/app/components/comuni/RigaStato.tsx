'use client';

import type { ReactNode } from 'react';
import { durataFa } from '../../lib/conti';

/**
 * La riga di stato in cima a una scheda (mattone comune a crypto e azioni): chi scrive i dati è vivo? (l'ultimo battito, in secondi)
 * e gli avvisi da vedere subito, in riquadri rossi con l'icona e il titolo (mai solo il colore). Senza avvisi una riga corta.
 */
export interface AvvisoStato {
  chiave: string;
  titolo: string;
  dettaglio: ReactNode;
}

function IconaAllarme() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"
      strokeLinejoin="round" aria-hidden="true">
      <path d="M12 3 2 21h20L12 3z" />
      <path d="M12 10v5M12 18v.01" />
    </svg>
  );
}

export default function RigaStatoBase({
  battito, arrivato, adesso, sogliaS = 900, nomeVivo = 'Bot vivo', nomeFermo = 'Bot fermo?', aggiornato,
  aggiornatoNome = 'strategie aggiornate', avvisi, nessunAvviso,
}: {
  /** l'ultimo battito, in secondi (null: mai visto) */
  battito: number | null;
  /** vero quando la lettura del battito è arrivata (anche vuota) */
  arrivato: boolean;
  adesso: number;
  /** oltre quanti secondi senza battito si dice «fermo?» */
  sogliaS?: number;
  nomeVivo?: string;
  nomeFermo?: string;
  /** l'ultimo aggiornamento dei dati, in secondi */
  aggiornato?: number | null;
  aggiornatoNome?: string;
  avvisi: AvvisoStato[];
  /** la riga da mostrare quando non ci sono avvisi (niente se manca) */
  nessunAvviso?: string;
}) {
  const eta = battito != null ? adesso - battito : null;
  const vivo = eta != null && eta < sogliaS;
  return (
    <section className="cr-stato" aria-label="stato e allarmi">
      <div className="cr-stato-riga">
        {!arrivato ? (
          <span className="cr-pill attesa"><span className="dot" />Lettura…</span>
        ) : vivo ? (
          <span className="cr-pill ok"><span className="dot" />{nomeVivo}</span>
        ) : (
          <span className="cr-pill ko"><span className="dot" />{nomeFermo}</span>
        )}
        <span>
          ultimo segnale <b>{battito != null ? durataFa(adesso, battito) : 'mai visto'}</b>
          {battito != null && !vivo ? ` (oltre ${Math.round(sogliaS / 60)} minuti: la macchina o il programma potrebbero essere giù)` : ''}
        </span>
        {aggiornato != null && aggiornato > 0 && (
          <span>{aggiornatoNome} <b>{durataFa(adesso, aggiornato)}</b></span>
        )}
      </div>

      {avvisi.map((a) => (
        <div className="cr-allarme" role="alert" key={a.chiave}>
          <IconaAllarme />
          <span><b>{a.titolo}</b> {a.dettaglio}</span>
        </div>
      ))}
      {avvisi.length === 0 && nessunAvviso && (
        <div className="cr-nessun-allarme">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round"
            strokeLinejoin="round" aria-hidden="true"><path d="M5 12l5 5 9-10" /></svg>
          {nessunAvviso}
        </div>
      )}
    </section>
  );
}
