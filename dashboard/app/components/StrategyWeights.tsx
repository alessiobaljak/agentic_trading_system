'use client';

import { useEffect, useMemo, useState } from 'react';
import { doc, onSnapshot } from 'firebase/firestore';
import { getDb } from '../lib/firebase';
import type { StrategyWeightsDoc, StrategyWeight } from '../lib/types';

/**
 * Pesi adattivi (0..1) per strategia × regime, come barre. Reads strategy_weights/
 * current. Colore per "salute": verde in forma, ambra sotto osservazione, rosso
 * penalizzata; tag "in prova" per i gruppi in rientro (sample_size 0).
 */
function healthColor(w: number): string {
  if (w >= 0.9) return 'var(--green)';
  if (w >= 0.7) return 'var(--amber)';
  return 'var(--red)';
}

export default function StrategyWeights() {
  const [doc_, setDoc] = useState<StrategyWeightsDoc | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const db = getDb();
    const unsub = onSnapshot(
      doc(db, 'strategy_weights', 'current'),
      (snap) => {
        setDoc(snap.exists() ? (snap.data() as StrategyWeightsDoc) : null);
        setLoaded(true);
      },
      () => setLoaded(true),
    );
    return () => unsub();
  }, []);

  const rows = useMemo(() => {
    const weights: StrategyWeight[] = doc_?.weights ?? [];
    return [...weights].sort((a, b) => (a.weight ?? 0) - (b.weight ?? 0)); // peggiori in cima
  }, [doc_]);

  return (
    <div className="panel">
      <h2>Peso appreso · strategia × regime</h2>
      <p className="subtitle">Quanto il learning si fida di ogni combo (0..1). In cima le più penalizzate.</p>
      {!loaded ? (
        <p className="muted">Loading…</p>
      ) : rows.length === 0 ? (
        <p className="muted">Nessun peso pubblicato ancora.</p>
      ) : (
        <div style={{ maxHeight: 380, overflowY: 'auto' }}>
          {rows.map((w) => {
            const wt = w.weight ?? 0;
            const col = healthColor(wt);
            const inProva = (w.sample_size ?? 0) === 0 && wt < 1;
            return (
              <div className="wrow" key={`${w.strategy}|${w.regime}`}>
                <span className="wlab" title={`${w.strategy} · ${w.regime}`}>
                  {w.strategy} <span className="wreg">· {w.regime}</span>
                  {inProva && (
                    <span className="wtag" style={{ background: 'rgba(227,169,43,0.15)', color: 'var(--amber)' }}>
                      in prova
                    </span>
                  )}
                </span>
                <span className="bucket-track">
                  <span className="bucket-fill" style={{ width: `${Math.max(0, Math.min(1, wt)) * 100}%`, background: col }} />
                </span>
                <span className="wval">
                  <span className="mono" style={{ color: col, fontWeight: 700 }}>{wt.toFixed(2)}</span>
                  {w.win_rate != null && (
                    <> · wr {Math.round(w.win_rate * 100)}%</>
                  )}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
