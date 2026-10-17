'use client';

import { useMemo } from 'react';
import { gravitaColore, lista, useControllo, type Anomalia, type Gravita } from '../lib/controllo';

/**
 * Le anomalie del controllo orario (25 set 2026), dalla piu' grave.
 *
 * Il bot le calcola da regole (`docs/controllo_schema.md` §1.6): ogni riga ha
 * un codice, la famiglia («sistema» = e' rotto?, «paper» = perde?), la
 * gravita', un testo e — quando ha senso — il valore misurato e la soglia.
 * Sul telefono si legge SOLO il testo: valore e soglia stanno nel `title`
 * (e in una colonna che compare da tablet in su), perche' una riga come
 * «rischio aperto 7,2% > 6%» in 360 px va a capo tre volte e non si legge.
 *
 * Le `info` non colorano il semaforo, e qui stanno in fondo, grigie.
 */
const ORDINE: Record<Gravita, number> = { rosso: 0, giallo: 1, info: 2 };

function testoValore(v: unknown): string {
  if (v == null) return '';
  if (typeof v === 'number') return v.toLocaleString('it-IT', { maximumFractionDigits: 2 });
  return String(v);
}

export default function ControlloAnomalie() {
  const { doc, caricamento, stato } = useControllo();

  const righe = useMemo(() => {
    const tutte = lista<Anomalia>(doc?.salute?.anomalie);
    return [...tutte].sort(
      (a, b) => (ORDINE[a.gravita ?? 'info'] ?? 9) - (ORDINE[b.gravita ?? 'info'] ?? 9),
    );
  }, [doc]);

  if (stato === 'assente' || (caricamento && !doc)) return null;

  const gravi = righe.filter((a) => a.gravita === 'rosso').length;
  const avvisi = righe.filter((a) => a.gravita === 'giallo').length;

  return (
    <div className="panel">
      <h2>
        Anomalie
        <span className="muted" style={{ fontWeight: 500, fontSize: 12, marginLeft: 8 }}>
          {righe.length === 0
            ? 'nessuna'
            : [gravi ? `${gravi} gravi` : '', avvisi ? `${avvisi} avvisi` : '']
                .filter(Boolean)
                .join(' · ') || `${righe.length} note`}
        </span>
      </h2>
      {righe.length === 0 ? (
        <p style={{ color: 'var(--green)', margin: 0, fontSize: 13 }}>
          Nessuna anomalia nell&apos;ultimo controllo: bot vivo, gate in orario, rischio nei tetti.
        </p>
      ) : (
        <ul className="anomalie">
          {righe.map((a, i) => {
            const val = testoValore(a.valore);
            const sog = testoValore(a.soglia);
            const dettaglio = [val ? `valore ${val}` : '', sog ? `soglia ${sog}` : '']
              .filter(Boolean)
              .join(' · ');
            return (
              <li
                key={`${a.codice ?? 'x'}-${i}`}
                className="anomalia"
                title={[a.codice, a.famiglia, dettaglio].filter(Boolean).join(' · ') || undefined}
              >
                <span className="dot" style={{ background: gravitaColore(a.gravita), flexShrink: 0 }} />
                <span className="anomalia-testo">{a.testo || a.codice || '—'}</span>
                {dettaglio && <span className="anomalia-dettaglio solo-largo muted">{dettaglio}</span>}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
