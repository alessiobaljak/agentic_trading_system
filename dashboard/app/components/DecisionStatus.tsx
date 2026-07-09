'use client';

import { useEffect, useState } from 'react';
import { onValue, ref } from 'firebase/database';
import { getRtdb } from '../lib/firebase';

/**
 * Esito dell'ultima decisione dell'orchestratore (/decision_status).
 * Spiega PERCHÉ il bot è flat o ha aperto, senza dover leggere i log della VPS.
 */
type DecisionStatus = {
  ts?: number;
  regime?: string;
  assets_evaluated?: number;
  signals_found?: number;
  best_symbol?: string | null;
  best_strategy?: string | null;
  best_confidence?: number | null;
  best_adjusted?: number | null;
  threshold?: number;
  outcome?: string; // "flat" | "decided" | "opened"
  reason?: string;
};

function timeAgo(ts?: number): string {
  if (!ts) return '—';
  const s = Math.floor(Date.now() / 1000 - ts);
  if (s < 60) return `${s}s fa`;
  const m = Math.floor(s / 60);
  if (m < 60) return `${m}m fa`;
  return `${Math.floor(m / 60)}h fa`;
}

export default function DecisionStatus() {
  const [st, setSt] = useState<DecisionStatus | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const db = getRtdb();
    const unsub = onValue(ref(db, 'decision_status'), (snap) => {
      setSt(snap.exists() ? (snap.val() as DecisionStatus) : null);
      setLoaded(true);
    });
    return () => unsub();
  }, []);

  const opened = st?.outcome === 'opened';
  const color = opened ? '#3fb950' : '#8b96a5';

  return (
    <div className="panel">
      <h2>Ultima decisione</h2>
      <p className="subtitle">Perché il bot ha aperto o è rimasto flat · ad ogni candela chiusa</p>
      {!loaded ? (
        <p className="muted">Loading…</p>
      ) : !st ? (
        <p className="muted">Nessuna decisione pubblicata ancora (in attesa del primo ciclo).</p>
      ) : (
        <div style={{ fontSize: 13, lineHeight: 1.7 }}>
          <div>
            <span style={{ color, fontWeight: 700 }}>
              {opened ? '🟢 APERTA' : '⚪ FLAT'}
            </span>{' '}
            <span className="muted">· {timeAgo(st.ts)} · regime {st.regime ?? '—'}</span>
          </div>
          <div style={{ marginTop: 6 }}>{st.reason ?? '—'}</div>
          <div className="muted" style={{ marginTop: 6 }}>
            Asset valutati: {st.assets_evaluated ?? 0} · segnali trovati: {st.signals_found ?? 0}
            {st.best_symbol
              ? ` · miglior segnale: ${st.best_symbol} ${st.best_strategy ?? ''} ` +
                `(conf. ${st.best_adjusted ?? '—'} / soglia ${st.threshold ?? 30})`
              : ''}
          </div>
        </div>
      )}
    </div>
  );
}
