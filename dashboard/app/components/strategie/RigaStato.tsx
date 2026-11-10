'use client';

import { allarmiAccesi, durataFa, nomeMoneta, oraItaliana, STRATEGIE, type DatiStrategie } from '../../lib/strategie';

/**
 * La riga in cima alla prima schermata: il bot è vivo? (l'ultimo battito del ciclo, /bot_status/heartbeat, scritto a ogni giro da
 * bot/main.py) e gli allarmi del demo, ben visibili: /demo_binance/allarme (conto non vuoto da fermo), /demo_binance/allarmi/<tipo>
 * (uno per tipo), il demo fermo (/demo_binance/fermo); con loro quelli del conto vero, se un giorno ce ne saranno.
 */

/** La soglia di sempre per «vivo» (era in TopVitals: 900 s, la soglia scritta dal bot nel controllo orario). */
const SOGLIA_VIVO_S = 900;

function IconaAllarme() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"
      strokeLinejoin="round" aria-hidden="true">
      <path d="M12 3 2 21h20L12 3z" />
      <path d="M12 10v5M12 18v.01" />
    </svg>
  );
}

export default function RigaStato({ dati, adesso }: { dati: DatiStrategie; adesso: number }) {
  const { battito, battitoArrivato, demo, contoVero, rami } = dati;
  const eta = battito != null ? adesso - battito : null;
  const vivo = eta != null && eta < SOGLIA_VIVO_S;
  const allarmi = allarmiAccesi(demo, contoVero);
  const aggiornamenti = STRATEGIE.map((s) => rami[s.ramo]?.stato?.aggiornato ?? 0).filter((x) => x > 0);
  const ultimo = aggiornamenti.length ? Math.max(...aggiornamenti) : null;

  return (
    <section className="cr-stato" aria-label="stato del bot e allarmi">
      <div className="cr-stato-riga">
        {!battitoArrivato ? (
          <span className="cr-pill attesa"><span className="dot" />Lettura…</span>
        ) : vivo ? (
          <span className="cr-pill ok"><span className="dot" />Bot vivo</span>
        ) : (
          <span className="cr-pill ko"><span className="dot" />Bot fermo?</span>
        )}
        <span>
          ultimo segnale <b>{battito != null ? durataFa(adesso, battito) : 'mai visto'}</b>
          {battito != null && !vivo ? ' (oltre 15 minuti: la macchina o il bot potrebbero essere giù)' : ''}
        </span>
        {ultimo != null && (
          <span>strategie aggiornate <b>{durataFa(adesso, ultimo)}</b></span>
        )}
      </div>

      {demo.fermo && (
        <div className="cr-allarme" role="alert">
          <IconaAllarme />
          <span>
            <b>Demo fermo</b> dal {oraItaliana(demo.fermo.ora)}: {demo.fermo.motivo}
            {demo.fermo.chiuse != null ? ` (${demo.fermo.chiuse} posizioni chiuse)` : ''}. Per farlo ripartire: «Riparti» nella scheda
            del demo, qui sotto.
          </span>
        </div>
      )}
      {allarmi.map((a, i) => (
        <div className="cr-allarme" role="alert" key={`${a.dove}-${a.tipo}-${i}`}>
          <IconaAllarme />
          <span>
            <b>Allarme del {a.dove}</b> ({a.tipo.replace(/_/g, ' ')}, {oraItaliana(a.ora)}): {a.testo}
            {a.monete.length ? ` (${a.monete.map(nomeMoneta).join(', ')})` : ''}
          </span>
        </div>
      ))}
      {!demo.fermo && allarmi.length === 0 && (
        <div className="cr-nessun-allarme">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round"
            strokeLinejoin="round" aria-hidden="true"><path d="M5 12l5 5 9-10" /></svg>
          Nessun allarme sul demo.
        </div>
      )}
    </section>
  );
}
